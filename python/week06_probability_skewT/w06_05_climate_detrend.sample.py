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
# Student Exercise:
# - Change start_year and end_year to analyze
#   different climate periods.
# - Compare how the land-ocean correlation changes
#   between different time ranges.
# - Test periods such as:
#     1950-2025
#     1980-2025
#     2000-2025
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
   """
   Calculate a linear trend and remove it from the data.

   Parameters
   ----------
   years : array-like
      Year values.
   data : pandas Series
      Temperature anomaly data.

   Returns
   -------
   dtrd_data : pandas Series
      Detrended anomaly data.
   trend : array
      Linear trend line.
   slope : float
      Linear trend slope per year.
   """

   # Calculate linear regression
   result = linregress(years, data)

   # Extract slope and intercept
   slope = result.slope
   intercept = result.intercept

   # Calculate the linear trend line
   trend = slope * years + intercept

   # Remove the linear trend from the original data
   dtrd_data = data - trend

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

# Step 1: Select the analysis period
# Students can change these two values to test how the
# land-ocean correlation changes for different time periods.
# For example, try 1950-2025, 1980-2025, or 2000-2025.

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


