"""
Example: Plot Daily, Hourly, and Minute Climate Data

This program demonstrates how to:
1. Read climate datasets with different temporal resolutions
2. Convert date columns into datetime format
3. Set datetime as the index
4. Plot multiple time-series datasets together

Dataset source:
Utah Climate Center
https://climate.usu.edu/mchd/
"""

import pandas as pd
import matplotlib.pyplot as plt
import sys

import pandas as pd
import numpy as np
from pathlib import Path


# Step 1. Define file paths
# Replace the file names below with your own full paths.
data_dir = Path('ENTER_FULL_PATH')

file_dly_path = data_dir / 'ENTER_DAILY_FILE.csv'
file_hly_path = data_dir / 'ENTER_HOURLY_FILE.csv'
file_min_path = data_dir / 'ENTERL_MINITUES_FILE.csv'


# Read the CSV files
# The comment="#" option ignores metadata lines
# beginning with # in the climate files.

data_dly = pd.read_csv(file_dly_path, header=0, command="#")
data_hly = pd.read_csv(file_hly_path, header=0, command="#")
data_min = pd.read_csv(file_min_path, header=0, command="#")


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

# --- Create the plot ---

plt.figure(figsize=(8, 5))

fig_title = 'Climate Data for April 2026 at Cedar City'

# Plot data
var='Air Temp Avg'
plt.plot(data_dly.index, data_dly[var], marker='o', linestyle='-', color="black", label='Daily',zorder=3)

# Step 2: Plot hourly and minute air temperature

plt.plot()
plt.plot()


# Adding title and labels

plt.title(fig_title)
plt.xlabel('Year')
plt.ylabel('Air Temperature (°C)')
plt.grid(True)


# Set x-axis range

xmin = data.index.min()
xmax = data.index.max()+ pd.Timedelta(days=0.5)
plt.xlim([xmin, xmax])

# Adjust layout to prevent overlap
plt.tight_layout()

# Save the plot as a JPEG file
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)

# Display the plot
plt.show()

