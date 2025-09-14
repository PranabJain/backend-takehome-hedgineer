import datetime as dt
from typing import Union

def safe_fromisoformat(d: Union[str, dt.date, dt.datetime]) -> dt.date:
    """Parse date safely from string/date/datetime."""
    if isinstance(d, dt.datetime):
        d = d.date()
    if isinstance(d, dt.date):
        return d  # already a date object
    if isinstance(d, str):
        return dt.date.fromisoformat(d)
    raise ValueError(f"Unsupported type for date parsing: {type(d)}")
