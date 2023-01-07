from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from fitbit import authenticate, spo2

token = authenticate()
df = spo2(token, datetime.now())

plt.plot(df.spo2)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
plt.show()
