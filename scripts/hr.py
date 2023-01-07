from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from fitbit import authenticate, hr

token = authenticate()
df = hr(token, datetime.now())

plt.plot(df.hr)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
plt.show()
