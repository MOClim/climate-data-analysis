"""
# TODO:
# Update the code below so that:
#
# 1. The 'airt' column is selected
# 2. The data are converted to monthly averages
# 3. The result is added to the monthly_dats list
#
# Hint:
# Use .resample('ME').mean()

# Append the monthly averaged data to the monthly_dats list.
  monthly_dats.append(______________________________)

# Update the code below.
  monthly_dats.append(data2['airt'].resample('ME').mean())
"""

import pandas as pd
import matplotlib.pyplot as plt
import sys, os
import glob

import pandas as pd
import numpy as np
from pathlib import Path

# --- Read Data ---

# Get the directory where this script is located
script_dir = Path(__file__).resolve().parent

# If the script is inside the "solution" folder,
# move up one additional directory level
if script_dir.name == "solution":
    repo_dir = script_dir.parents[2]
else:
    repo_dir = script_dir.parents[1]

# Create the path to the data directory
# using an absolute path based on the repository location
data_dir = repo_dir / "data" / "UCRN"

filenames = list(data_dir.glob('*.csv'))

# Extract the location information
location_info = [] 
for file_path in filenames:
    with open(file_path, 'r') as file:
        first_line = file.readline().strip()
        # Split to extract after the colon and before the dash
        station_full = first_line.split(': ')[1] if ': ' in first_line else first_line
        station_name = station_full.split(' -')[0]  # Splits at the dash and takes the first part
        location_info.append(station_name)

# ============================================
# TODO:
# Select the 'airt' column, calculate monthly
# averages, and append the result to monthly_dats.
#
# Hint:
# Use .resample('ME').mean()
# ============================================

monthly_dats = []
for file_path in filenames:
    data = pd.read_csv(file_path, header=0, skiprows=26)

   # Ensure 'date_time' column is in datetime format
    data['date_time'] = pd.to_datetime(data['date_time'])

    # Set 'date_time' column as the index
    data2 = data.set_index('date_time')

    # Append the resulting DataFrame to the list
    monthly_dats.append(data2['airt'].resample('ME').mean())

print(monthly_dats)


# --- Create the plot ---

plt.figure(figsize=(10, 6))
for dat, loc in zip(monthly_dats, location_info):
    plt.plot(dat.index, dat, label=loc)

# Adding a main title to the figure
main_title = 'Monthly Data for 2022-2025 in Utah'

plt.title(main_title)
plt.xlabel('Date')
plt.ylabel('Temperature (C)')
plt.grid(True)

# Place the legend outside the plot
plt.legend(loc='center left', bbox_to_anchor=(0.96, 0.5), fontsize='small')

# Adjust spacing automatically
plt.tight_layout()

# Save the plot as a JPEG file
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)

# Display the plot
plt.show()

