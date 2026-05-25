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
data_dir = Path('../../data')

# Daily climate observations for 2025
file_dly_path = data_dir / 'cedar-city-zion-np-kolob.daily_2025.csv'


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


# Step 1: Calculate monthly averages
# Replace ADD_TIME_FREQUENCY with the correct pandas
# monthly frequency code.
#
# Use 'ME' to calculate monthly averages and assign
# each monthly value to the end of the month.
#
# Daily observations are aggregated into monthly
# mean values using the pandas resample() function.

data_mnt = data_dly.resample('ADD_TIME_FREQUENCY').mean()

print(data_mnt.head())
print(data_mnt.shape)



# --- Create the plot ---

plt.figure(figsize=(8, 5))


# Plot the data
# Define x-axis and y-axis data from data_mnt
var='Air Temp Avg'

# Step 2: Add two plot commands
# Plot the monthly average data and the original daily data.
#
# First plot:
#   x-axis = data_mnt.index
#   y-axis = data_mnt[var]
#
# Second plot:
#   x-axis = data_dly.index
#   y-axis = data_dly[var]

plt.plot()
plt.plot()

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

