from datetime import datetime, timedelta


def calc_time_difference():
    midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    now = datetime.now()
    time_difference = midnight - now
    if time_difference.days < 0:
        midnight = midnight + timedelta(days=1)
        time_difference = midnight - now
    total_seconds = int(time_difference.total_seconds())
    hours = total_seconds // 3600
    remaining_seconds = total_seconds % 3600
    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60
    return f"{hours}h {minutes}m {seconds}s"
