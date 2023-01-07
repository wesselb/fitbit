import pandas as pd
from pathlib import Path

out_dir = Path("output")

for folder, name in [
    (out_dir / "hr", "hr"),
    (out_dir / "hrv", "hrv"),
    (out_dir / "spo2", "spo2"),
    (out_dir / "br", "br"),
]:
    dfs = [
        pd.read_csv(str(f), date_parser=["date"]).set_index("date")
        for f in sorted(folder.glob("*.csv"))
    ]
    df = pd.concat(dfs)
    df.to_parquet(str(folder / name) + ".parquet")
