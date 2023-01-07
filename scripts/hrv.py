from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from fitbit import authenticate, hrv

token = authenticate()
df = hrv(token, datetime.now())

plt.plot(df.hrv)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
plt.show()
