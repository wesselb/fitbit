import datetime
from pathlib import Path

from fitbit import authenticate, hr, hrv, br, spo2

# Ensure that the output directories exist.
out_dir = Path("output")
(out_dir / "hr").mkdir(parents=True, exist_ok=True)
(out_dir / "hrv").mkdir(parents=True, exist_ok=True)
(out_dir / "br").mkdir(parents=True, exist_ok=True)
(out_dir / "spo2").mkdir(parents=True, exist_ok=True)

# Start at yesterday, because today's data might not yet be complete.
current = datetime.datetime.now() - datetime.timedelta(days=1)


def fetch_and_dump(path, api_call, day):
    out = path / day.strftime("%Y-%m-%d.csv")
    if not out.exists():
        try:
            df = api_call(authenticate(), day)
            df.to_csv(str(out))
            return True
        except Exception as e:
            print(f'Failed "{out}" with the following exception:', type(e), str(e))
            return False
    else:
        return True


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
    else:
        current -= datetime.timedelta(days=1)
