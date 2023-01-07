import datetime

import pandas as pd
import requests

from .rate import rate_limiter

__all__ = ["heart_rate"]


def heart_rate(token, day):
    """Get your heart rate time series at day `date`.

    Args:
        token (str): Authentication token.
        day (:class:`datetime.datetime`): Day in your local time zero.

    Returns:
        :class:`pandas.DataFrame`: Data frame containing your heart rate time series.
    """
    day = datetime.datetime.now() - datetime.timedelta(days=1)
    with rate_limiter:
        res = requests.get(
            (
                f"https://api.fitbit.com/1/user/-/activities/heart"
                f"/date/{day.year}-{day.month:02d}-{day.day:02d}"
                f"/1d/1sec.json"
            ),
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )
    res.raise_for_status()
    hr = res.json()

    def parse_time(x, ref):
        h, m, s = map(int, x.split(":"))
        dt = datetime.datetime(ref.year, ref.month, ref.day, h, m, s)
        return dt

    series = hr["activities-heart-intraday"]["dataset"]
    series = [(parse_time(x["time"], day), x["value"]) for x in series]
    series = pd.DataFrame(series, columns=["date", "heart_rate"]).set_index("date")

    return series
