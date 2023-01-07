import pandas as pd

hr = pd.read_parquet("output/hr/hr.parquet")
hrv = pd.read_parquet("output/hrv/hrv.parquet")
spo2 = pd.read_parquet("output/spo2/spo2.parquet")
br = pd.read_parquet("output/br/br.parquet")

print(hr)
print(hrv)
print(spo2)
print(br)
