from datetime import datetime


def parse_dates(dates_raw: list[str | datetime]) -> list[datetime | None]:
    parsed_dates: list[datetime | None] = []
    for d in dates_raw:
        if isinstance(d, datetime):
            parsed_dates.append(d)
        elif isinstance(d, str):
            dt: datetime | None = None
            # Try ISO formats first
            try:
                dt = datetime.fromisoformat(d.replace('Z', '+00:00'))
            except Exception:
                # Try common EXIF datetime format
                try:
                    dt = datetime.strptime(d, "%Y:MM:DD %H:%M:%S")
                except Exception:
                    # Try a fallback with dashes
                    try:
                        dt = datetime.strptime(d, "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        dt = None
            parsed_dates.append(dt)
        else:
            parsed_dates.append(None)
    return parsed_dates