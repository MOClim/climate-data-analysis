###############################################################################
# Homework 5: Monthly vs Annual Histogram Analysis
#
# Objectives:
#   1. Resample daily station observations into monthly and annual datasets.
#   2. Calculate:
#        - monthly mean temperature
#        - annual mean temperature
#        - monthly accumulated precipitation
#        - annual accumulated precipitation
#   3. Convert each resampled dataset into a NumPy array and remove missing values.
#   4. Compare histogram distributions between monthly and annual data.
#   5. Edit the histogram bin numbers for monthly and annual datasets.
#
# Notes:
#   - Temperature is averaged over time using mean().
#   - Precipitation is accumulated over time using sum().
#   - Precipitation may include 'T', meaning trace precipitation. In this script,
#     trace precipitation is treated as 0.0 mm before numerical analysis.
###############################################################################

import netCDF4 as nc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import math
from pathlib import Path

### Read Main ###

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
data_dir = repo_dir / "data_raw"

# Path of the downloaded CSV file
filename = data_dir / 'map-server-report-1791475073/GHCN/USC00425186/dly-report.csv'


# Read the CSV file
df = pd.read_csv(
    filename,
    header=0,
    skiprows=19,
    na_values='nan'
)

# Convert the date column into pandas datetime format and set it as the index
df['day'] = pd.to_datetime(df['day'])
df = df.set_index('day')

# Select data period
df = df.loc['1893':'2010']
print(df)

# Treat trace precipitation as 0.0 mm
# 'T' means trace precipitation: observed, but too small to measure accurately.
df['Precipitation'] = df['Precipitation'].replace('T', 0.0)

# Convert precipitation to numeric values
df['Precipitation'] = pd.to_numeric(df['Precipitation'], errors='coerce')
df['Max Temperature'] = pd.to_numeric(df['Max Temperature'], errors='coerce')


# Step 1: EDIT HERE
# Resample and compute monthly and annual temperature and precipitation.
# Hint:
#   - Temperature should use mean().
#   - Precipitation should use sum().
#   - Monthly resampling uses 'ME'.
#   - Annual resampling uses 'YE'.
df_temp_mon = df['Max Temperature'].resample('ME').mean()
df_temp_anu = df['Max Temperature'].resample('YE').mean()
df_prc_mon = df['Precipitation'].resample('ME').sum()
df_prc_anu = df['Precipitation'].resample('YE').sum()
#sys.exit()


# Convert resampled data into NumPy arrays and remove NaN values
temp_mon = df_temp_mon.values.flatten()[~np.isnan(df_temp_mon.values.flatten())]
temp_anu = df_temp_anu.values.flatten()[~np.isnan(df_temp_anu.values.flatten())]
prc_mon = df_prc_mon.values.flatten()[~np.isnan(df_prc_mon.values.flatten())]
prc_anu = df_prc_anu.values.flatten()[~np.isnan(df_prc_anu.values.flatten())]


# Create and plot the histogram
plt.figure(figsize=(12, 6))

plt.subplot(2, 2, 1)
# Step 2: EDIT HERE
# Change the bin number for monthly temperature.
plt.hist(temp_mon, bins=20, color='orange', edgecolor='black')
plt.title('Monthly Temperature')
plt.xlabel('Temperature (C)')
plt.ylabel('Frequency (months)')
plt.grid(True)

plt.subplot(2, 2, 3)
# Step 3: EDIT HERE
# Change the bin number for annual temperature.
plt.hist(temp_anu, bins=20, color='orange', edgecolor='black')
plt.title('Annual-mean Temperature')
plt.xlabel('Temperature (C)')
plt.ylabel('Frequency (years)')
plt.grid(True)

plt.subplot(2, 2, 2)
# Step 4: EDIT HERE
# Change the bin number for monthly precipitation.
plt.hist(prc_mon, bins=20, color='blue', edgecolor='black')
plt.title('Monthly Precipitation')
plt.xlabel('Precipitation (mm)')
plt.ylabel('Frequency (months)')
plt.grid(True)

plt.subplot(2, 2, 4)
# Step 5: EDIT HERE
# Change the bin number for annual precipitation.
plt.hist(prc_anu, bins=20, color='blue', edgecolor='black')
plt.title('Annual Precipitation')
plt.xlabel('Precipitation (mm)')
plt.ylabel('Frequency (years)')
plt.grid(True)

start_year = df_temp_mon.index[0].year
end_year = df_temp_mon.index[-1].year
total_months = len(df_temp_mon)
total_years = int(math.ceil(total_months / 12))

title = (
    f'Histogram at USU '
    f'{start_year}-{end_year}, '
    f'{total_years} years, '
    f'{total_months} months'
)

# Add the main title to the figure
plt.suptitle(title, fontsize=16)

# Adjust the spacing between the plots
plt.subplots_adjust(hspace=0.5)

# Adjust spacing automatically
plt.tight_layout()

# Save the plot as a JPEG file
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)

plt.show()

