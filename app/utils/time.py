from datetime import datetime, timezone


def utc_now() -> datetime:
    """
    Returns current UTC time with timezone awareness.
    """
    return datetime.now(timezone.utc)


def to_isoformat(dt: datetime) -> str:
    """
    Converts datetime to ISO-8601 string.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()
