from datetime import datetime
import pytz
import numpy as np
import math



def iso_extract_date(timestamp: str) -> str:
    '''
    Extract date from iso date string

    e.g. from "2025-06-01T08:49:54.0" extract "2025-06-01"
    '''
    dt = datetime.fromisoformat(timestamp)
    return dt.date().isoformat()


def iso_to_datetime(iso_string: str) -> datetime:
    '''
    Convert iso date string (e.g. "2025-06-01T08:49:54.0") into datetime
    '''
    return datetime.fromisoformat(iso_string).replace(tzinfo=pytz.UTC)


def get_julian_datetime(date: datetime) -> float:
    """
    Convert a datetime object into julian float.
    Args:
        date: datetime-object of date in question

    Returns: float - Julian calculated datetime.
    Raises: 
        TypeError : Incorrect parameter type
        ValueError: Date out of range of equation
    """

    # Ensure correct format
    if not isinstance(date, datetime.datetime):
        raise TypeError('Invalid type for parameter "date" - expecting datetime')
    elif date.year < 1801 or date.year > 2099:
        raise ValueError('Datetime must be between year 1801 and 2099')

    # Perform the calculation
    julian_datetime = 367 * date.year - int((7 * (date.year + int((date.month + 9) / 12.0))) / 4.0) + int(
        (275 * date.month) / 9.0) + date.day + 1721013.5 + (
                          date.hour + date.minute / 60.0 + date.second / math.pow(60,
                                                                                  2)) / 24.0 - 0.5 * math.copysign(
        1, 100 * date.year + date.month - 190002.5) + 0.5

    return julian_datetime