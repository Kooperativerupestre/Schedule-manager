from datetime import datetime

def validate_datetime(dt: datetime) -> datetime:
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("Datetime must be timezone-aware.")
    return dt
