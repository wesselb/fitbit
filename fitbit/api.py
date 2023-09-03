import datetime
import pprint
import warnings

import pandas as pd
import requests

from .rate import rate_limiter

__all__ = [
    # AZM endpoint appears to be broken currently.
    # "zone",
    "cal",
    "dist",
    "elev",
    "floors",
    "steps",
    "hr",
    "hrv",
    "spo2",
    "br",
    "sleep_summary",
    "sleep_series",
]


def zone(token, day):
    """Get your active zone minutes time series at day `day`.

    Args:
        token (str): Authentication token.
        day (:class:`datetime.datetime`): Day in your local time zero.

    Returns:
        :class:`pandas.DataFrame`: Active zone minutes time series.
    """
    warnings.warn(
        "The API endpoint for intraday active zone minutes appears to be broken. "
        "For example, see the following thread: "
        "https://community.fitbit.com/t5/Web-API-Development"
        "/active-zone-minutes-endpoint-throwing-error/td-p/5438823",
        stacklevel=1,
    )
    return _intraday_activity("active-zone-minutes", "1min", "zone", token, day)


def cal(token, day):
    """Get your calories time series at day `day`.

    Args:
        token (str): Authentication token.
        day (:class:`datetime.datetime`): Day in your local time zero.

    Returns:
        :class:`pandas.DataFrame`: Calories time series.
    """
    return _intraday_activity("calories", "1min", "cal", token, day)


def dist(token, day):
    """Get your distance time series at day `day`.

    Args:
        token (str): Authentication token.
        day (:class:`datetime.datetime`): Day in your local time zero.

    Returns:
        :class:`pandas.DataFrame`: Distance time series.
    """
    return _intraday_activity("distance", "1min", "dist", token, day)


def elev(token, day):
    """Get your elevation time series at day `day`.

    Args:
        token (str): Authentication token.
        day (:class:`datetime.datetime`): Day in your local time zero.

    Returns:
        :class:`pandas.DataFrame`: Elevation time series.
    """
    return _intraday_activity("elevation", "1min", "elev", token, day)


def floors(token, day):
    """Get your floors times series at day `day`.

    Args:
        token (str): Authentication token.
        day (:class:`datetime.datetime`): Day in your local time zero.

    Returns:
        :class:`pandas.DataFrame`: Floors time series.
    """
    return _intraday_activity("elevation", "1min", "elev", token, day)


def steps(token, day):
    """Get your steps times series at day `day`.

    Args:
        token (str): Authentication token.
        day (:class:`datetime.datetime`): Day in your local time zero.

    Returns:
        :class:`pandas.DataFrame`: Steps time series.
    """
    return _intraday_activity("steps", "1min", "steps", token, day)


def hr(token, day):
    """Get your heart rate time series at day `day`.

    Args:
        token (str): Authentication token.
        day (:class:`datetime.datetime`): Day in your local time zero.

    Returns:
        :class:`pandas.DataFrame`: Heart rate time series.
    """
    return _intraday_activity("heart", "1sec", "hr", token, day)


def _intraday_activity(name, resolution, column_name, token, day):
    """Get intraday activity time series at day `day`.

    Args:
        name (str): Name of the activity.
        column_name (str): Name of the column in the resulting data frame.
        token (str): Authentication token.
        day (:class:`datetime.datetime`): Day in your local time zero.

    Returns:
        :class:`pandas.DataFrame`: Intraday activity time series.
    """
    res = _fetch(token, f"activities/{name}/date/{{date}}/1d/{resolution}.json", day)

    def parse_time(x, ref):
        h, m, s = map(int, x.split(":"))
        dt = datetime.datetime(ref.year, ref.month, ref.day, h, m, s)
        return dt

    series = res[f"activities-{name}-intraday"]["dataset"]
    series = [(parse_time(x["time"], day), x["value"]) for x in series]
    series = pd.DataFrame(series, columns=["date", column_name]).set_index("date")

    return series


def hrv(token, day):
    """Get your heart rate variability time series at day `day`.

    Args:
        token (str): Authentication token.
        day (:class:`datetime.datetime`): Day in your local time zero.

    Returns:
        :class:`pandas.DataFrame`: Heart rate variability time series.
    """
    res = _fetch(token, "hrv/date/{date}/all.json", day)

    def parse_time(x):
        return datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.000")

    series = res["hrv"][0]["minutes"]
    series = [(parse_time(x["minute"]), x["value"]["rmssd"]) for x in series]
    series = pd.DataFrame(series, columns=["date", "hrv"]).set_index("date")

    return series


def spo2(token, day):
    """Get your SpO2 time series at day `day`.

    Args:
        token (str): Authentication token.
        day (:class:`datetime.datetime`): Day in your local time zero.

    Returns:
        :class:`pandas.DataFrame`: SpO2 time series.
    """
    res = _fetch(token, "spo2/date/{date}/all.json", day)

    def parse_time(x):
        return datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S")

    series = res["minutes"]
    series = [(parse_time(x["minute"]), x["value"]) for x in series]
    series = pd.DataFrame(series, columns=["date", "spo2"]).set_index("date")

    return series


def br(token, day):
    """Get your breathing rate information at day `day`.

    Args:
        token (str): Authentication token.
        day (:class:`datetime.datetime`): Day in your local time zero.

    Returns:
        :class:`pandas.DataFrame`: Breathing rate information.
    """
    res = _fetch(token, "br/date/{date}/all.json", day)
    return pd.DataFrame(
        [
            {
                "date": datetime.datetime(day.year, day.month, day.day),
                "br_full": res["br"][0]["value"]["fullSleepSummary"]["breathingRate"],
                "br_deep": res["br"][0]["value"]["deepSleepSummary"]["breathingRate"],
                "br_rem": res["br"][0]["value"]["remSleepSummary"]["breathingRate"],
                "br_light": res["br"][0]["value"]["lightSleepSummary"]["breathingRate"],
            }
        ]
    ).set_index("date")


def sleep(token, day):
    """Get your sleep information at day `day`.

    Args:
        token (str): Authentication token.
        day (:class:`datetime.datetime`): Day in your local time zero.

    Returns:
        :class:`pandas.DataFrame`: Summary of your sleep.
        :class:`pandas.DataFrame`: Sleep time series.
    """
    res = _fetch(token, "sleep/date/{date}.json", day, version=1.2)

    def parse_time(x):
        return datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.000")

    # Find the main sleep.
    i = [d["isMainSleep"] for d in res["sleep"]].index(True)

    summary = pd.DataFrame(
        [
            {
                "date": datetime.datetime(day.year, day.month, day.day),
                "sleep_start": parse_time(res["sleep"][i]["startTime"]),
                "sleep_end": parse_time(res["sleep"][i]["endTime"]),
                "sleep_deep_mins": res["summary"]["stages"]["deep"],
                "sleep_rem_mins": res["summary"]["stages"]["rem"],
                "sleep_light_mins": res["summary"]["stages"]["light"],
                "sleep_wake_mins": res["summary"]["stages"]["wake"],
            }
        ]
    ).set_index("date")
    series = pd.DataFrame(
        [
            {
                "date": parse_time(entry["dateTime"]),
                "sleep_stage_level": entry["level"],
                "sleep_stage_dur_mins": entry["seconds"] / 60,
            }
            for entry in res["sleep"][i]["levels"]["data"]
        ]
    ).set_index("date")
    return summary, series


def sleep_summary(token, day):
    """Get a summary of your sleep information at day `day`.

    Args:
        token (str): Authentication token.
        day (:class:`datetime.datetime`): Day in your local time zero.

    Returns:
        :class:`pandas.DataFrame`: Summary of your sleep.
    """
    return sleep(token, day)[0]


def sleep_series(token, day):
    """Get your sleep time series at day `day`.

    Args:
        token (str): Authentication token.
        day (:class:`datetime.datetime`): Day in your local time zero.

    Returns:
        :class:`pandas.DataFrame`: Sleep time series.
    """
    return sleep(token, day)[1]


def _fetch(token, url, day, version=1):
    with rate_limiter:
        date = f"{day.year}-{day.month:02d}-{day.day:02d}"
        res = requests.get(
            f"https://api.fitbit.com/{version}/user/-/" + url.format(date=date),
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
