"""
Calculate daily averages

Hourly and minute observations are resampled to
daily frequency using the mean value for each day.

This process converts high-frequency observations
into daily averages, allowing direct comparison
with the original daily dataset.

'D' represents daily resampling frequency in pandas.
"""

import pandas as pd
import matplotlib.pyplot as plt
import sys

import pandas as pd
import numpy as np
from pathlib import Path


# File paths for the dataset.

file_dly_path = Path('../../data_raw/cedar-city-zion-np-kolob.daily.csv')
file_hly_path = Path('../../data_raw/cedar-city-zion-np-kolob.hourly.csv')
file_min_path = Path('../../data_raw/cedar-city-zion-np-kolob.min.csv')


# Read the CSV files

data_dly = pd.read_csv(file_dly_path, header=0, comment="#")
data_hly = pd.read_csv(file_hly_path, header=0, comment="#")
data_min = pd.read_csv(file_min_path, header=0, comment="#")


# Convert date_time column to datetime format

data_dly['date_time'] = pd.to_datetime(data_dly['Category'])
data_hly['date_time'] = pd.to_datetime(data_hly['Category'])
data_min['date_time'] = pd.to_datetime(data_min['Category'])


# Set datetime as index

data_dly.set_index('date_time', inplace=True)
data_hly.set_index('date_time', inplace=True)
data_min.set_index('date_time', inplace=True)


# Normalize daily timestamps
# Removes the time component from daily data.

data_dly.index = data_dly.index.normalize()


# Resample hourly and minute data to daily averages
# Aggregate sub-daily observations into daily mean values

data_h_daily_avg = data_hly.resample('D').mean()
print(data_hly.head())
print(data_h_daily_avg.head())

data_m_daily_avg = data_min.resample('D').mean()
print(data_min.head())
print(data_m_daily_avg.head())


# --- Create the plot ---

plt.figure(figsize=(8, 5))


# Plot data
var='Air Temp Avg'
plt.plot(data_dly.index, data_dly[var], marker='.', linestyle='-', color="black", label='Daily (original)',zorder=3)
plt.plot(data_h_daily_avg.index, data_h_daily_avg[var], marker='+', linestyle='-', color="blue", label='Daily from Hourly',zorder=2)
plt.plot(data_m_daily_avg.index, data_m_daily_avg[var], marker='.', linestyle='-', color="green", label='Daily from Minite',zorder=1, linewidth=3)

# Adding title and labels

fig_title = 'Daily Climate Data for April 2026 at Cedar City'

plt.title(fig_title)
plt.xlabel('Year')
plt.ylabel('Air Temperature (°F)')
plt.grid(True)


# Set the x-axis limits to cover the full date range

xmin = data_dly.index.max()-pd.Timedelta(days=7)
xmax = data_dly.index.max()+pd.Timedelta(days=1)
plt.xlim([xmin, xmax])


# Add legend labels to distinguish between different datasets on the plot.
plt.legend()


# Adjust layout to prevent overlap
plt.tight_layout()

# Save the plot as a JPEG file
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)

# Display the plot
plt.show()

