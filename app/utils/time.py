from datetime import datetime
from pytz import timezone


def get_current_time():
    """
    Returns the current time in IST.
    """
    return datetime.now().astimezone(timezone("Asia/Kolkata"))
