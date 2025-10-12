from datetime import date, datetime
import logging
import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry
from dataclasses import dataclass
from typing import List
from datetime import timedelta

@dataclass
class MeteoDay:
    date: pd.Timestamp
    weather_code: int
    sunrise: int
    sunset: int
    temperature_2m_max: float
    temperature_2m_min: float

@dataclass
class MeteoData:
    days: List[MeteoDay]

def getMeteoData(latitude: float, longitude: float, start_date: date, end_date: date) -> MeteoData:
    try:
        """
        Retrieve weather data from Open-Meteo API for given coordinates and date range.
        Chooses the right source automatically:
        - Forecast API: supports ~last months to ~+2 weeks; preferred when possible
        - Archive API: supports 1940 up to ~7 days ago
        If the requested range cannot be served by a single source, fetch the past month
        from Forecast and older dates from Archive, then merge (favoring Forecast on overlaps).
        """
        logging.info(
            f"Retrieving meteo data for coordinates ({latitude:.2f}, {longitude:.2f}) from {start_date} to {end_date}..."
        )

        end_date = end_date + timedelta(days=1)

        # Normalize range
        req_start = min(start_date, end_date)
        req_end = max(start_date, end_date)

        # Setup API client with cache and retries
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        archive_url = "https://archive-api.open-meteo.com/v1/archive"
        forecast_url = "https://api.open-meteo.com/v1/forecast"

        today = date.today()
        # Define supported windows
        archive_min = date(1940, 1, 1)
        archive_max = today - timedelta(days=7)
        forecast_min = today - timedelta(days=30)
        forecast_max = today + timedelta(days=14)

        def in_range(s: date, e: date, rmin: date, rmax: date) -> bool:
            return s >= rmin and e <= rmax

        def clamp(s: date, e: date, rmin: date, rmax: date) -> tuple[date, date] | None:
            cs = max(s, rmin)
            ce = min(e, rmax)
            return (cs, ce) if cs <= ce else None

        def fetch_days(url: str, s: date, e: date) -> list[MeteoDay]:
            # Open-Meteo end_date is inclusive; we'll request end_date+1 in the date_range inclusive-left pattern below
            local_params = {
                "latitude": round(latitude, 2),
                "longitude": round(longitude, 2),
                "daily": [
                    "weather_code",
                    "sunrise",
                    "sunset",
                    "temperature_2m_max",
                    "temperature_2m_min",
                ],
                "timezone": "auto",
                "start_date": s.strftime("%Y-%m-%d"),
                "end_date": e.strftime("%Y-%m-%d"),
            }
            responses = openmeteo.weather_api(url, params=local_params)
            response = responses[0]
            # logging.debug(f"Using {url.split('//')[1].split('/')[0]} for {s} -> {e}")
            daily = response.Daily()
            daily_weather_code = daily.Variables(0).ValuesAsNumpy()
            daily_sunrise = daily.Variables(1).ValuesInt64AsNumpy()
            daily_sunset = daily.Variables(2).ValuesInt64AsNumpy()
            daily_temperature_2m_max = daily.Variables(3).ValuesAsNumpy()
            daily_temperature_2m_min = daily.Variables(4).ValuesAsNumpy()

            dates = pd.date_range(
                start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=daily.Interval()),
                inclusive="left",
            )

            res: list[MeteoDay] = []
            for i in range(len(dates)):
                res.append(
                    MeteoDay(
                        date=dates[i],
                        weather_code=int(daily_weather_code[i]),
                        sunrise=int(daily_sunrise[i]),
                        sunset=int(daily_sunset[i]),
                        temperature_2m_max=float(daily_temperature_2m_max[i]),
                        temperature_2m_min=float(daily_temperature_2m_min[i]),
                    )
                )
            return res

        # Decide best strategy
        days: list[MeteoDay] = []

        if in_range(req_start, req_end, forecast_min, forecast_max):
            # Entire range available via forecast (preferred)
            logging.info("Using forecast API for entire range.")
            days = fetch_days(forecast_url, req_start, req_end)
        elif in_range(req_start, req_end, archive_min, archive_max):
            # Entire range available via archive
            logging.info("Using archive API for entire range.")
            days = fetch_days(archive_url, req_start, req_end)
        else:
            # Split: past month on forecast, older on archive
            # Past month window within requested range
            logging.info("Splitting request between archive and forecast APIs.")
            past_month_start = max(req_start, req_end - timedelta(days=29))
            forecast_span = clamp(past_month_start, req_end, forecast_min, forecast_max)
            archive_span = clamp(req_start, (forecast_span[0] - timedelta(days=1)) if forecast_span else req_end, archive_min, archive_max)

            # Fetch available parts and merge
            parts: list[list[MeteoDay]] = []
            if archive_span:
                parts.append(fetch_days(archive_url, archive_span[0], archive_span[1]))
            if forecast_span:
                parts.append(fetch_days(forecast_url, forecast_span[0], forecast_span[1]))

            # Merge with de-dup preferring forecast (since it's appended last)
            merged: dict[date, MeteoDay] = {}
            for part in parts:
                for d in part:
                    key = d.date.date() if hasattr(d.date, 'date') else d.date
                    merged[key] = d
            # Convert back to list sorted by date
            days = [merged[k] for k in sorted(merged.keys())]

        return MeteoData(days=days)
    except Exception as e:
        logging.info(f"Could not retrieve meteo data, error occurred: {e}")
        return MeteoData(days=[])
    
def getMeteoInterpretationFromWMOCode(wmo_code: int) -> str:
    """
    Provides a human-readable interpretation of the WMO weather code.
    """
    wmo_descriptions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense intensity drizzle",
        56: "Light freezing drizzle",
        57: "Dense intensity freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy intensity rain",
        66: "Light freezing rain",
        67: "Heavy intensity freezing rain",
        71: "Slight snow fall",
        73: "Moderate snow fall",
        75: "Heavy intensity snow fall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    return wmo_descriptions.get(wmo_code, "Unknown weather condition")
