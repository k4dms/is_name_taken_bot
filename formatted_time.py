from datetime import datetime


def get_time_now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def get_time_delta_seconds(time_new, time_old):
    time_new = format_time(time_new)
    time_old = format_time(time_old)
    time_delta = (time_new - time_old).total_seconds()
    return time_delta


def format_time(time):
    return datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
