import datetime
import logging


def time_offset_to_timezone(time_offset: str) -> datetime.tzinfo:
    """
    Converts a time_offset string to a timezone object.
    time_offset can be "auto" (returns local zoneinfo), or "Europe/Paris", or "UTC±HH:MM".
    If 'auto', returns the local zoneinfo (with DST handled automatically).
    If a valid IANA timezone name (e.g. Europe/Paris), returns that zoneinfo.
    If UTC offset, returns a fixed offset timezone.
    """
    try:
        if time_offset == "auto":
            try:
                from zoneinfo import ZoneInfo
                import tzlocal
                local_tz_name = tzlocal.get_localzone_name()
                return ZoneInfo(local_tz_name)
            except Exception:
                return datetime.datetime.now().astimezone().tzinfo
        # If it's a valid IANA timezone name
        if not time_offset.startswith("UTC"):
            try:
                from zoneinfo import ZoneInfo
                return ZoneInfo(time_offset)
            except Exception:
                logging.error(f"Invalid timezone name: {time_offset}")
                return datetime.datetime.now().astimezone().tzinfo
        # If it's a UTC offset
        if not time_offset.startswith("UTC") or (len(time_offset) != 9):
            raise ValueError("Invalid time offset format. Use 'UTC±HH:MM', 'auto', or a timezone name.")
        sign = 1 if time_offset[3] == '+' else -1
        hours = int(time_offset[4:6])
        minutes = int(time_offset[7:9]) if len(time_offset) == 9 else 0
        offset = datetime.timedelta(hours=hours * sign, minutes=minutes * sign)
        return datetime.timezone(offset)
    except Exception as e:
        logging.error(f"Error parsing time offset '{time_offset}': {e}")
        return datetime.datetime.now().astimezone().tzinfo
    
def convert_to_timezone(dt: datetime.datetime, tz: datetime.tzinfo):
        if dt is None or dt == "NA":
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt.astimezone(tz)