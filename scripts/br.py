from datetime import datetime

from fitbit import authenticate, br

token = authenticate()
df = br(token, datetime.now())

print(df)
