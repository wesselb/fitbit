import time

from .config import config
from .util import timestamp

__all__ = ["rate_limiter"]


class RateLimiter:
    """Rate limiter.

    Args:
        frequency (float): Frequency of allowed requests.
    """

    def __init__(self, frequency: float = 150 / 3600):
        self.frequency = frequency
        self.last = config["session", "last_api_request_timestamp_utc"]

    def __enter__(self):
        now = timestamp()
        while now < self.last + 1 / self.frequency:
            to_sleep = self.last + 1 / self.frequency - now
            print(f"Waiting {to_sleep:.1f} seconds to not exceed API rate limit.")
            time.sleep(to_sleep)
            now = timestamp()
        self.last = now
        config["session", "last_api_request_timestamp_utc"] = now

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


rate_limiter = RateLimiter()
""":class:`RateLimiter`: Rate limiter."""
