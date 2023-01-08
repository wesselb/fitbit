import datetime
from pathlib import Path

import pandas as pd
from fitbit import authenticate, br, hr, hrv, spo2

# Ensure that the output directories exist.
out_dir = Path("output")
(out_dir / "hr").mkdir(parents=True, exist_ok=True)
(out_dir / "hrv").mkdir(parents=True, exist_ok=True)
(out_dir / "br").mkdir(parents=True, exist_ok=True)
(out_dir / "spo2").mkdir(parents=True, exist_ok=True)

# Start at yesterday, because today's data might not yet be complete.
current = datetime.datetime.now() - datetime.timedelta(days=1)


def fetch_and_dump(path, api_call, day):
    """Fetch data and dump it to a CSV. Will only fetch data if it was not already
    fetched.

    Args:
        path (str): Directory to dump the CSV into.
        api_call (function): API function to call.
        day (:class:`datetime.datetime`): Day to fetch data for.

    Returns:
        bool: `True` if any data was available, otherwise `False`.
    """
    out = path / day.strftime("%Y-%m-%d.csv")
    if not out.exists():
        try:
            df = api_call(authenticate(), day)
            df.to_csv(str(out))
        except Exception as e:
            print(f'Failed "{out}" with the following exception:', type(e), str(e))
            return False
    else:
        df = pd.read_csv(out)
    return len(df) > 0


# How many days without any data before stopping scraping?
allowance = 10

while True:
    print("Current day:", current.strftime("%Y-%m-%d"))
    any_available = False
    any_available |= fetch_and_dump(out_dir / "hr", hr, current)
    any_available |= fetch_and_dump(out_dir / "hrv", hrv, current)
    any_available |= fetch_and_dump(out_dir / "br", br, current)
    any_available |= fetch_and_dump(out_dir / "spo2", spo2, current)
    if not any_available:
        allowance -= 1
        if allowance == 0:
            break
    current -= datetime.timedelta(days=1)
