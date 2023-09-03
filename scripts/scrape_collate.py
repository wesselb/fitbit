from pathlib import Path

import fitbit.api as api
import pandas as pd

api_calls = api.__all__

out_dir = Path("output")

for call in api_calls:
    folder = out_dir / call
    dfs = [
        pd.read_csv(str(f), date_parser=["date"]).set_index("date")
        for f in sorted(folder.glob("*.csv"))
    ]
    df = pd.concat(dfs)
    df.to_parquet(str(folder / call) + ".parquet")
