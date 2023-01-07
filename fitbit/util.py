import datetime

__all__ = ["timestamp"]


def timestamp() -> float:
    """Get a timestamp of now in fractional seconds.

    Returns:
        float: Timestamp.
    """
    return datetime.datetime.utcnow().timestamp()
