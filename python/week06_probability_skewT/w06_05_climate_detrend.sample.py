# ==========================================================
# Climate Data Trend Analysis and Detrending
#
# This script demonstrates how to:
# 1. Read climate temperature anomaly datasets
# 2. Calculate linear trends using regression
# 3. Remove long-term trends from the data
# 4. Compare detrended land and ocean variability
# 5. Calculate correlation after detrending
#
# Detrending is commonly used in climate analysis
# to isolate short-term variability by removing
# long-term warming trends.
# ==========================================================

import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress
from pathlib import Path
import sys

# ----------------------------------------------------------
# Function to calculate a linear trend and detrended data
# ----------------------------------------------------------

def cal_regression(years, data):

   # Use the original data as temporary detrended data
   # (replace this later with actual detrending)
   dtrd_data = data

   # Example slope value for a linear trend
   slope = 0.02

   # Example intercept value for a linear trend
   intercept = -38.

   # Calculate the linear trend line
   # using slope and intercept
   trend = slope * years + intercept

   return dtrd_data, trend, slope


# ----------------------------------------------------------
# Example dataset:
# Annual temperature anomaly values
# ----------------------------------------------------------


# File paths for both datasets. Add data name for each path.
data_dir = Path('../../data/')
data2_dir = Path('../../data_raw/')
ocean_file_path = data_dir / 'NOAA.1850-2025.OCN.csv'
land_file_path = data2_dir / 'NOAA.1850-2025.LND.csv'

# Read the CSV files, assuming data starts from the 5th row
tland_data = pd.read_csv(land_file_path, comment="#",index_col='Year')
tocean_data = pd.read_csv(ocean_file_path, comment="#",index_col='Year')

# Select the analysis period
start_year = 1950
end_year = 2025
ocean_data = tocean_data['Anomaly'].loc[start_year:end_year]
land_data = tland_data['Anomaly'].loc[start_year:end_year]

years = land_data.index.values

# *** Update cal_regression subroutine to obtain accurate trends, slop, and detrended data
dtrd_land_data, trend_land, slope_land = cal_regression(years,land_data)
dtrd_ocn_data, trend_ocn, slope_ocn = cal_regression(years,ocean_data)

# Create the plot
plt.figure(figsize=(10, 5))

# Choose colors for land and ocean data
land_color = 'sienna'
ocean_color = 'deepskyblue'

plt.subplot(1, 2, 1)
figtitle = 'Annual-Mean Temperature Anomaly'
funcline = True
plt.plot(years, land_data, marker='o', linestyle='-', color=land_color, label='Land',zorder=1)
plt.plot(years, ocean_data, marker='o', linestyle='-', color=ocean_color, label='Ocean',zorder=1)
lineinfo = f'Land trend (slope={slope_land:0.3f})'
plt.plot(years, trend_land, label=lineinfo, color='red')
lineinfo = f'Ocean trend (slope={slope_ocn:0.3f})'
plt.plot(years, trend_ocn, label=lineinfo, color='black')

# Adding title and labels
plt.title(figtitle)
plt.ylabel('Temperature Anomaly (°C)')
plt.xlabel('Year')
plt.grid(True)
plt.legend()


plt.subplot(1, 2, 2)
figtitle = 'Detrended'
funcline = True
plt.plot(years, dtrd_land_data, linestyle='-', color=land_color, label='Land',zorder=1)
plt.plot(years, dtrd_ocn_data,  linestyle='-', color=ocean_color, label='Ocean',zorder=1)

# Calculate the correlation
correlation = dtrd_land_data.corr(dtrd_ocn_data)
plt.title(f'cor={correlation:0.2f}', loc='right')

# Adding title and labels
plt.title(figtitle)
plt.ylabel('Temperature Anomaly (°C)')
plt.xlabel('Year')
plt.grid(True)
plt.legend()

# Add the main title to the figure
fig_title = 'Land vs. Ocean: Correlation of Temperature Anomalies'
plt.suptitle(fig_title, fontsize=16)

# Adjust the spacing between the plots
plt.subplots_adjust(hspace=0.5)  # Increase this value to add more space vertically

# Save the plot as a JPEG file
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)

# Display the plot
plt.show()


