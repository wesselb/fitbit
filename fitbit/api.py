import datetime
import pprint

import pandas as pd
import requests

from .rate import rate_limiter

__all__ = ["hr", "hrv", "spo2", "br"]


def hr(token, day):
    """Get your heart rate time series at day `date`.

    Args:
        token (str): Authentication token.
        day (:class:`datetime.datetime`): Day in your local time zero.

    Returns:
        :class:`pandas.DataFrame`: Data frame containing your heart rate time series.
    """
    res = _fetch(token, "activities/heart/date/{date}/1d/1sec.json", day)

    def parse_time(x, ref):
        h, m, s = map(int, x.split(":"))
        dt = datetime.datetime(ref.year, ref.month, ref.day, h, m, s)
        return dt

    series = res["activities-heart-intraday"]["dataset"]
    series = [(parse_time(x["time"], day), x["value"]) for x in series]
    series = pd.DataFrame(series, columns=["date", "hr"]).set_index("date")

    return series


def hrv(token, day):
    """Get your heart rate variability time series at day `date`.

    Args:
        token (str): Authentication token.
        day (:class:`datetime.datetime`): Day in your local time zero.

    Returns:
        :class:`pandas.DataFrame`: Data frame containing your heart rate variability
            time series.
    """
    res = _fetch(token, "hrv/date/{date}/all.json", day)

    def parse_time(x):
        return datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.000")

    series = res["hrv"][0]["minutes"]
    series = [(parse_time(x["minute"]), x["value"]["rmssd"]) for x in series]
    series = pd.DataFrame(series, columns=["date", "hrv"]).set_index("date")

    return series


def spo2(token, day):
    """Get your SpO2 time series at day `date`.

    Args:
        token (str): Authentication token.
        day (:class:`datetime.datetime`): Day in your local time zero.

    Returns:
        :class:`pandas.DataFrame`: Data frame containing your SpO2 time series.
    """
    res = _fetch(token, "spo2/date/{date}/all.json", day)

    def parse_time(x):
        return datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S")

    series = res["minutes"]
    series = [(parse_time(x["minute"]), x["value"]) for x in series]
    series = pd.DataFrame(series, columns=["date", "spo2"]).set_index("date")

    return series


def br(token, day):
    """Get your breathing rate time series at day `date`.

    Args:
        token (str): Authentication token.
        day (:class:`datetime.datetime`): Day in your local time zero.

    Returns:
        :class:`pandas.DataFrame`: Data frame containing your breathing rate time
            series.
    """
    res = _fetch(token, "br/date/{date}/all.json", day)
    series = pd.DataFrame(
        [
            (
                datetime.datetime(day.year, day.month, day.day),
                res["br"][0]["value"]["fullSleepSummary"]["breathingRate"],
                res["br"][0]["value"]["deepSleepSummary"]["breathingRate"],
                res["br"][0]["value"]["remSleepSummary"]["breathingRate"],
                res["br"][0]["value"]["lightSleepSummary"]["breathingRate"],
            )
        ],
        columns=[
            "date",
            "br_full",
            "br_deep",
            "br_rem",
            "br_light",
        ],
    ).set_index("date")
    return series


def _fetch(token, url, day):
    with rate_limiter:
        date = f"{day.year}-{day.month:02d}-{day.day:02d}"
        res = requests.get(
            "https://api.fitbit.com/1/user/-/" + url.format(date=date),
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )
    try:
        res.raise_for_status()
    except requests.HTTPError as e:
        print("Full response:")
        pprint.pprint(res.json())
        raise e

    return res.json()
