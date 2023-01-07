from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from fitbit import authenticate, heart_rate

token = authenticate()
df = heart_rate(token, datetime.now())

plt.plot(df.heart_rate)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
plt.show()
