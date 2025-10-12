import datetime

def getDatesRange(date_objs: list[datetime.datetime]):
    if date_objs:
        start_date =  min(date_objs)
        end_date = max(date_objs)
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        total_days = (end_date.date() - start_date.date()).days + 1
    else:
        start_date_str = end_date_str = total_days = "N/A"
    return start_date_str, end_date_str, total_days