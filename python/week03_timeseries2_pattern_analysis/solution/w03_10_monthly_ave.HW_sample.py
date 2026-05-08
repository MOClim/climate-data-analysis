"""
Example: Calculate Monthly Climate Averages

This program demonstrates how to:
1. Read daily climate observations from a CSV file
2. Convert date columns into datetime format
3. Set datetime as the DataFrame index
4. Resample daily observations into monthly averages
5. Compare daily and monthly temperature variability

Dataset source:
Utah Climate Center AgWeather Network
https://climate.usu.edu/mchd/

Location:
UCRN Cedar City
"""

import pandas as pd
import matplotlib.pyplot as plt
import sys

import pandas as pd
import numpy as np
from pathlib import Path


# File paths for the dataset.
# Daily climate observations for 2025

file_dly_path = Path('../../data/cedar-city-zion-np-kolob.daily_2025.csv')


# Read the CSV files
data_dly = pd.read_csv(file_dly_path, header=0, comment="#")


# Convert to datetime
data_dly['date_time'] = pd.to_datetime(data_dly['Category'])


# Set 'Date' as the index of the DataFrame
data_dly.set_index('date_time', inplace=True)

# Remove original text/date column
data_dly.drop(columns=['Category'], inplace=True)

# Normalize the timestamps to remove time part
# Removes the time component from timestamps

data_dly.index = data_dly.index.normalize()


print(data_dly.head())
print(data_dly.shape)


# Calculate monthly averages
# Daily observations are aggregated into monthly
# mean values using the pandas resample() function.
#
# 'ME' represents month-end frequency.
#
# numeric_only=True ensures that only numeric
# variables are included in the averaging process.

data_mnt = data_dly.resample('ME').mean(numeric_only=True)

print(data_mnt.head())
print(data_mnt.shape)


# ---------------------------------------------------
# Optional: Shift timestamps to first day of month
# ---------------------------------------------------
# Uncomment the line below if monthly timestamps
# should represent the beginning of each month.

data_mnt.index = (
     data_mnt.index
     - pd.DateOffset(months=1)
     + pd.Timedelta(days=15)
 )


# --- Create the plot ---

plt.figure(figsize=(8, 5))


# Plot the data
# Define x-axis and y-axis data from data_mnt
var='Air Temp Avg'
x_data =  data_mnt.index
y_data =  data_mnt[var]

plt.plot(x_data, y_data, marker='.', linestyle='-', color="black", label='Monthly',zorder=3)
plt.plot(data_dly.index, data_dly[var], marker='.', linestyle='-', color="blue", label='Daily',zorder=1)

# Adding title and labels
fig_title = 'Monthly Climate Data for 2025 at Ceder City'

plt.title(fig_title)
plt.xlabel('Year')
plt.ylabel('Air Temperature (°C)')
plt.grid(True)

# Adjust layout to prevent overlap
plt.tight_layout()

# Save the plot as a JPEG file
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)

# Display the plot
plt.show()

