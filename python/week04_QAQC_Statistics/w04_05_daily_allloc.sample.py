# ==========================================================
# Reading the UCRN CSV File
# ==========================================================
#
# skiprows=26
#   Skip the first 26 lines in the file because they contain
#   metadata and station information, not tabular data.
#
# header=0
#   Use the first remaining row as the column header.
#
# Example header row:
# date_time, airt, precip, ...
# ==========================================================

import pandas as pd
import matplotlib.pyplot as plt
import sys, os
import glob

import pandas as pd
import numpy as np
from pathlib import Path

# --- Read Data ---

# Create a list of all CSV files inside the ../../data/UCRN directory
# Path('../../data/UCRN') specifies the folder location
# .glob('*.csv') searches for all files ending with .csv
# list(...) converts the search results into a Python list
data_dir = Path('../../data/UCRN')

filenames = list(data_dir.glob('*.csv'))

# Print the complete list of file paths
print(filenames)
print('')

# Loop through each file path in the list
# Print the full file path
for f in filenames:
    print(f)
print('')

# Loop through each file path again
# Print only the file name (without the directory path)
for f in filenames:
    print(f.name)
print('')


# Extract the location information
location_info = [] 
for file_path in filenames:
    with open(file_path, 'r') as file:
        first_line = file.readline().strip()
        # Split to extract after the colon and before the dash
        station_full = first_line.split(': ')[1] if ': ' in first_line else first_line
        station_name = station_full.split(' -')[0]  # Splits at the dash and takes the first part
        location_info.append(station_name)

# Read each file into a DataFrame and store in a list
daily_dats = []
for file_path in filenames:
    data = pd.read_csv(file_path, header=0, skiprows=26)

    # Ensure 'date_time' column is in datetime format
    data['date_time'] = pd.to_datetime(data['date_time'])
    # Set 'date_time' column as the index
    data2 = data.set_index('date_time')

    # Append the resulting DataFrame to the list
    daily_dats.append(data2['airt'])

print(daily_dats)
print(data.head())

# --- Create the plot ---

plt.figure(figsize=(10, 6))
for dat, loc in zip(daily_dats, location_info):
    plt.plot(dat.index, dat, label=loc)

# Adding a main title to the figure
main_title = 'Daily Data for 2022-2025 in Utah'

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

