import pandas as pd

hr = pd.read_parquet("output/hr/hr.parquet")
hrv = pd.read_parquet("output/hrv/hrv.parquet")
spo2 = pd.read_parquet("output/spo2/spo2.parquet")
br = pd.read_parquet("output/br/br.parquet")

hr.index = pd.to_datetime(hr.index)
hrv.index = pd.to_datetime(hrv.index)
spo2.index = pd.to_datetime(spo2.index)
br.index = pd.to_datetime(br.index)

print(hr)
print(hrv)
print(spo2)
print(br)
