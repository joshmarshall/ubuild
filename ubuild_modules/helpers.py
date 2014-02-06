from datetime import datetime


def generate_datetime_version():
    return datetime.utcnow().strftime("%Y%m%d.%H%M%S")
