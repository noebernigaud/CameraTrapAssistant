import matplotlib
import datetime
import io
import sys
import os
from reportlab.platypus import Image
import numpy as np

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))
from utils.meteo_api.getMeteoData import MeteoData

matplotlib.use('agg')   
import matplotlib.pyplot as plt

def generateObservationsByTimeAndDaysGraph(
    species_set: list[str],
    predictedclass: list[str],
    date_objs: list[datetime.datetime],
    species_colors: dict[str, str],
    chunk_dates_list: list[datetime.date],
    meteo_data: MeteoData  # MeteoData with .days list having date, weather_code, sunrise, sunset
):
    hours = list(range(24))
    chunk_dates_list = sorted(chunk_dates_list, reverse=True)
    num_dates = len(chunk_dates_list)
    fig_height = min(2 + (num_dates * 0.12), 8)
    plt.figure(figsize=(9, fig_height))
    # Plot points for this chunk only
    for species in species_set:
        indices = [i for i, s in enumerate(predictedclass) if s == species and date_objs[i].date() in chunk_dates_list]
        if not indices:
            continue
        y = [date_objs[i].date() for i in indices]
        x = [date_objs[i].hour + date_objs[i].minute/60.0 for i in indices]
        plt.scatter(x, y, label=species, color=species_colors[species])
    plt.xlabel("Hour of Day")
    plt.ylabel("Date")
    plt.title(f"Detections by Species (dates {chunk_dates_list[-1]} to {chunk_dates_list[0]})")
    plt.xlim(0, 24)
    plt.xticks(hours, [f"{h:02d}:00" for h in hours], rotation=45)
    plt.yticks(chunk_dates_list, [d.strftime("%m-%d") for d in chunk_dates_list])
    plt.ylim(chunk_dates_list[0] + (chunk_dates_list[-1] - chunk_dates_list[0]).__class__(1),
                chunk_dates_list[-1] - (chunk_dates_list[-1] - chunk_dates_list[0]).__class__(1))
    # --- Meteo overlay aligned with y-axis dates ---
    # Build a date -> meteo day map if provided
    def _weather_color(code: int) -> str:
        # Simplified mapping based on WMO weather codes
        if code == 0:
            return '#f9d71c'  # clear
        if code in (1, 2, 3):
            return '#9ecae1'  # clouds
        if code in (45, 48):
            return '#c7c7c7'  # fog
        if 51 <= code <= 57:
            return '#74add1'  # drizzle
        if 61 <= code <= 67:
            return '#2c7fb8'  # rain
        if 71 <= code <= 77:
            return '#74c476'  # snow
        if 80 <= code <= 82:
            return '#2c7fb8'  # rain showers
        if 85 <= code <= 86:
            return '#74c476'  # snow showers
        if code in (95, 96, 99):
            return '#dd1c77'  # thunder
        return '#999999'

    sunrise_label_done = False
    sunset_label_done = False
    weather_label_done = False

    if meteo_data and getattr(meteo_data, 'days', None):
        # Create a mapping from date -> day
        try:
            day_map = {}
            for d in meteo_data.days:
                # d.date is expected to be a pandas Timestamp; convert to date
                try:
                    dt = d.date.date() if hasattr(d.date, 'date') else d.date
                except Exception:
                    dt = d.date
                day_map[dt] = d

            for y_date in chunk_dates_list:
                day = day_map.get(y_date)
                if not day:
                    continue
                # sunrise/sunset are epoch seconds; convert to hour-of-day
                try:
                    sr = datetime.datetime.fromtimestamp(int(day.sunrise))
                    ss = datetime.datetime.fromtimestamp(int(day.sunset))
                    x_sr = sr.hour + sr.minute/60.0
                    x_ss = ss.hour + ss.minute/60.0
                    plt.scatter(
                        [x_sr], [y_date], marker='^', color='orange', s=20, alpha=0.3, linewidths=0,
                        label=None if sunrise_label_done else 'Sunrise'
                    )
                    sunrise_label_done = True
                    plt.scatter(
                        [x_ss], [y_date], marker='v', color='red', s=20, alpha=0.3, linewidths=0,
                        label=None if sunset_label_done else 'Sunset'
                    )
                    sunset_label_done = True
                except Exception:
                    pass

                # Weather code marker at the far right
                try:
                    wx_color = _weather_color(int(day.weather_code))
                    x_wx = 23.8
                    plt.scatter(
                        [x_wx], [y_date], marker='s', s=40, color=wx_color, edgecolors='k', linewidths=0.2,
                        label=None if weather_label_done else 'Weather code'
                    )
                    weather_label_done = True
                except Exception:
                    pass
        except Exception:
            pass

    plt.grid(True, which='both', axis='both', color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
    plt.legend(fontsize=8)
    plt.tight_layout()
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='PNG', dpi=150)
    plt.close()
    img_buffer.seek(0)
    img_width = 500
    img_height = int(fig_height * 72)
    return Image(img_buffer, width=img_width, height=img_height)

def generateObservationsByTimeAndSpeciesGraph(
    species_set: list[str],
    predictedclass: list[str],
    date_objs: list[datetime.datetime],
    species_colors: dict[str, str],
    jitter_strength: float = 0.1  # controls how much vertical spread you get
):
    hours = list(range(24))
    species_list = sorted(species_set)
    num_species = len(species_list)
    fig_height = min(1.5 + (num_species * 0.4), 8)

    plt.figure(figsize=(9, fig_height))

    for species in species_list:
        indices = [i for i, s in enumerate(predictedclass) if s == species]
        if not indices:
            continue

        x = [date_objs[i].hour + date_objs[i].minute / 60.0 for i in indices]

        # --- Apply jitter on y-axis ---
        base_y = species_list.index(species)
        y = [base_y + np.random.uniform(-jitter_strength, jitter_strength) for _ in indices]

        plt.scatter(
            x,
            y,
            label=species,
            color=species_colors.get(species, "gray"),
            alpha=0.8,
            s=20
        )

    plt.xlabel("Hour of Day")
    plt.ylabel("Species")
    plt.title("Detections by Species and Time of Day")
    plt.xlim(0, 24)
    plt.xticks(hours, [f"{h:02d}:00" for h in hours], rotation=45)
    plt.yticks(range(len(species_list)), species_list)
    plt.grid(True, which='both', axis='both', color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
    plt.legend(fontsize=8, bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='PNG', dpi=150)
    plt.close()
    img_buffer.seek(0)

    img_width = 500
    img_height = int(fig_height * 72)
    return Image(img_buffer, width=img_width, height=img_height)


def generateCircularObservationsGraph(
    species_set: list[str],
    predictedclass: list[str],
    date_objs: list[datetime.datetime],
    species_colors: dict[str, str],
    jitter_strength: float = 0.05
):
    species_list = sorted(species_set)
    num_species = len(species_list)
    if num_species == 0:
        raise ValueError("No species provided.")

    # --- Radius configuration ---
    inner_radius = 2.0
    outer_radius = 6.0
    fixed_interval = 0.75

    max_rings_that_fit = int((outer_radius - inner_radius) / fixed_interval) + 1

    if num_species <= max_rings_that_fit:
        ring_positions = [outer_radius - i * fixed_interval for i in range(num_species)]
    else:
        ring_positions = np.linspace(outer_radius, inner_radius, num_species)

    fig_size = 6
    plt.figure(figsize=(fig_size, fig_size))
    ax = plt.subplot(111, polar=True)
    ax.set_theta_direction(-1)       # Clockwise
    ax.set_theta_zero_location("N")  # 0h = top (north)

    # --- Plot each species ---
    for i, species in enumerate(species_list):
        indices = [j for j, s in enumerate(predictedclass) if s == species]
        if not indices:
            continue

        # Convert time → radians (24h = full circle)
        hours = np.array([date_objs[j].hour + date_objs[j].minute / 60.0 for j in indices])
        theta = (hours / 24.0) * 2 * np.pi

        # Dynamic radius with jitter
        base_r = ring_positions[i]
        r = base_r + np.random.uniform(-jitter_strength, jitter_strength, size=len(theta))

        # Light grey reference ring
        circle_theta = np.linspace(0, 2 * np.pi, 360)
        ax.plot(circle_theta, np.full_like(circle_theta, base_r),
                color='lightgray', lw=0.6, alpha=0.6)

        # Detections
        ax.scatter(
            theta,
            r,
            color=species_colors.get(species, "gray"),
            label=species,
            alpha=0.8,
            s=30
        )

    # --- Axis setup ---
    ax.set_rgrids(ring_positions, labels=species_list, angle=90, fontsize=8)
    ax.set_rticks([])
    ax.set_rlabel_position(0)

    # Hour labels every 2 hours
    hour_labels = [f"{h:02d}:00" for h in range(0, 24, 2)]
    ax.set_xticks(np.linspace(0, 2 * np.pi, 12, endpoint=False))
    ax.set_xticklabels(hour_labels)

    # Add padding beyond the outermost ring
    padding = fixed_interval / 2
    ax.set_ylim(0, ring_positions[0] + padding)

    ax.set_title("Detections by Time of Day", va='bottom')
    ax.legend(bbox_to_anchor=(1.15, 1.05), fontsize=8)
    plt.tight_layout()

    # --- Export as ReportLab Image ---
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='PNG', dpi=150, bbox_inches='tight')
    plt.close()
    img_buffer.seek(0)

    img_width = 500
    img_height = int(fig_size * 72)
    return Image(img_buffer, width=img_width, height=img_height)


def getDatesChunksForObservationsByTimeGraphs(date_objs: list[datetime.datetime]):
    MAX_DATES_PER_GRAPH = 50
    if date_objs:
        min_date = min(date_objs).date()
        max_date = max(date_objs).date()
        all_dates = [min_date]
        while all_dates[-1] < max_date:
            all_dates.append(all_dates[-1] + (max_date - min_date).__class__(1))
    else:
        all_dates = []
    # Split all_dates into chunks of MAX_DATES_PER_GRAPH
    def chunk_dates(dates, n):
        return [dates[i:i+n] for i in range(0, len(dates), n)]
    return chunk_dates(all_dates, MAX_DATES_PER_GRAPH) if all_dates else []