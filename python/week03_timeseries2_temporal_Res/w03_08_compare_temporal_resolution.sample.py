"""
Example: Zoom into a narrow time range

A shorter time window (4 days) is used to better
 visualize the differences among daily, hourly,
 and minute observations.

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


# --- Read Data ---

# File paths for the dataset.
data_dir = Path('../../data_raw')

file_dly_path = data_dir / 'cedar-city-zion-np-kolob.daily.csv'
file_hly_path = data_dir / 'cedar-city-zion-np-kolob.hourly.csv'
file_min_path = data_dir / 'cedar-city-zion-np-kolob.min.csv'


# Read the CSV file, assuming data starts from the 5th row
data_dly = pd.read_csv(file_dly_path, header=0, comment="#")
data_hly = pd.read_csv(file_hly_path, header=0, comment="#")
data_min = pd.read_csv(file_min_path, header=0, comment="#")

# Convert to Panda's friendly datetime
data_dly['date_time'] = pd.to_datetime(data_dly['Category'])
data_hly['date_time'] = pd.to_datetime(data_hly['Category'])
data_min['date_time'] = pd.to_datetime(data_min['Category'])

# Set 'Date' as the index of the DataFrame
data_dly.set_index('date_time', inplace=True)
data_hly.set_index('date_time', inplace=True)
data_min.set_index('date_time', inplace=True)

# Normalize the timestamps to remove time part
data_dly.index = data_dly.index.normalize()

# --- Create the plot ---

plt.figure(figsize=(8, 5))

fig_title = 'Climate Data for April 2026 at Cedar City'

# Plot data
var='Air Temp Avg'
plt.plot(data_dly.index, data_dly[var], marker='o', linestyle='-', color="black", label='Daily',zorder=3)
plt.plot(data_hly.index, data_hly[var], marker='+', linestyle='-', color="blue", label='Hourly',zorder=2)
plt.plot(data_min.index, data_min[var], marker='.', linestyle='-', color="green", label='Minite',zorder=1)

# Adding title and labels
plt.title(fig_title)
plt.xlabel('Year')
plt.ylabel('Air Temperature (°C)')
plt.grid(True)

# Set the x-axis limits to cover for 4 days
# Zooming into a narrow time range makes these
# differences in temporal sampling much easier
# to compare visually.

xmin = data_dly.index.max()-pd.Timedelta(days=3)
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

