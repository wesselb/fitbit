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
        # Sleep to ensure that we don't exceed the rate limit.
        while self.last + 1 / self.frequency > now:
            to_sleep = self.last + 1 / self.frequency - now
            print(f"Waiting {to_sleep:.1f} seconds to not exceed API rate limit.")
            # Add 10 milliseconds to ensure that we _really_ slept enough.
            time.sleep(to_sleep + 0.01)
            now = timestamp()

        # We're good now.
        self.last = now
        config["session", "last_api_request_timestamp_utc"] = now

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


rate_limiter = RateLimiter()
""":class:`RateLimiter`: Rate limiter."""
