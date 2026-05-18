###############################################################################
# Exercise: Monthly Temperature Histogram Analysis
#
# Objective:
#   Download daily meteorological observations from the Utah Climate Center,
#   compute monthly mean temperature, and visualize the temperature
#   distribution using a histogram.
#
# Dataset Source:
#   Utah Climate Center / Southwest Climate Observations (SWCO)
#   https://climate.usu.edu/swco/
#
# Download Instructions:
#   1. Open the SWCO website.
#   2. Use the interactive station map.
#   3. Select the USU weather station (COOP 425186).
#   4. Download daily observations:
#        - Temperature
#        - Precipitation
#   5. Select metric units.
#   6. Download the ZIP archive from the website.
#   7. Unzip the downloaded file.
#   8. Move the extracted directory:
#
#        map-server-report-xxxxxxxxx/
#
#      into:
#
#        ../../data_raw/
#
#   9. Confirm the CSV file exists at:
#
#        ../../data_raw/map-server-report-xxxxxxxxx/COOP/425186/dly-report.csv
#
# Code Processing Steps:
#   1. Read the CSV dataset using pandas.
#   2. Skip metadata rows at the top of the file.
#   3. Convert the 'day' column into a DatetimeIndex.
#   4. Resample daily temperature into monthly means.
#   5. Remove missing values (NaN).
#   6. Generate a histogram of monthly mean temperature.
#   7. Automatically calculate:
#        - analysis start year
#        - analysis end year
#        - total months
#        - total years
#   8. Save the figure as a JPEG image.
#
# CSV Configuration:
#   header=0
#   skiprows=19
#   na_values='nan'
###############################################################################

import netCDF4 as nc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import math
from pathlib import Path

### Read Main ###

# Step 1:
# EDIT HERE:
# Add the path to the downloaded CSV file
filename = Path('../../data_raw/map-server-report-1779136575/COOP/425186/dly-report.csv')

# Step 2:
# EDIT HERE:
# Check the CSV file and define:
#   header    -> row number containing variable names
#   skiprows  -> number of metadata rows to skip
#   na_values -> missing value text in the dataset
df = pd.read_csv(
    filename,
    header=0,
    skiprows=19,
    na_values='nan'
)

# Display column names and first few rows
print(df.columns)
print(df.head())

# Example: if your date column is named "day"
df['day'] = pd.to_datetime(df['day'])
df = df.set_index('day')

# Select data period
df = df.loc['1893':'2010']

# Compute monthly mean temperature
df_mon = df['tmid'].resample('ME').mean()

# convert index from Timestamp to monthly period
df_mon.index = df_mon.index.to_period('M')

print(df_mon)

# Combine all monthly data into a single series (.floatten())
single_series = df_mon.values.flatten()

# Remove NaN values 
all_data = single_series[~np.isnan(single_series)]

# ---- Plotting ----
# Step 3: Create and plot the histogram
plt.figure(figsize=(10, 6))
plt.hist(all_data, bins=100, color='orange', edgecolor='black')

start_year = df_mon.index[0].year
end_year = df_mon.index[-1].year
total_months = len(df_mon)
total_years = int(math.ceil(total_months / 12))

plt.title(
    f'Histogram of Temperature at USU '
    f'({start_year}-{end_year}, '
    f'{total_years} years, '
    f'{total_months} months)'
)

plt.xlabel('Temperature (°C)')
plt.ylabel('Frequency (months)')
plt.grid(True)

# Adjust spacing automatically
plt.tight_layout()

# Save the plot as a JPEG file
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)


plt.show()

