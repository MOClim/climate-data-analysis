# ==========================================================
# Automatically Create the Year Range for the Plot Title
# ==========================================================
#
# start_year
#   Extract the earliest year from the time-series data.
#
# end_year
#   Extract the latest year from the time-series data.
#
# This allows the plot title to update automatically
# when a different dataset or time range is used.
# ==========================================================

import pandas as pd
import matplotlib.pyplot as plt
import sys, os
import glob

import pandas as pd
import numpy as np
from pathlib import Path

# --- Read Data ---

# Specify the directory path
# List all CSV files in the directory
data_dir = Path('../../data/UCRN')

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

# Get data by specifying column name
# https://climate.usu.edu/mchd/dashboard/overview/UCRN.php
varname = 'airt'

# Read each file into a DataFrame and store in a list
dataframes = []
for file_path in filenames:
    df = pd.read_csv(file_path, index_col='date_time', parse_dates=True, header=0, skiprows=26, usecols=['date_time',varname])
    dataframes.append(df[varname])

# Convert daily data to monthly data
monthly_dats = []
for dataframe in dataframes:
    # resample monthly frequency and calculate the mean
    monthly_df = dataframe.resample('ME').mean()  

    # Append the resulting DataFrame to the list
    monthly_dats.append(monthly_df)


# Assuming 'monthly_dats' is a list of 16 DataFrames, each with a time series
# Combine the DataFrames along the columns
combined_data = pd.concat(monthly_dats, axis=1)
combined_data.columns = {location_info[i] for i in range(len(monthly_dats))}

# Calculate the maximum and minimum values across the 20 time series
max_values = combined_data.max(axis=1)
min_values = combined_data.min(axis=1)

# Calculate the mean across the 20 time series for each time point
mean_series = combined_data.mean(axis=1)


# --- Create the plot ---

plt.figure(figsize=(10, 6))

# Plot the average of all station data
plt.plot(mean_series.index, mean_series, label='Average', color='black',linewidth=2,zorder=3)

# Plot each station data
for dat, file_path, loc in zip(monthly_dats, filenames, location_info):
    plt.plot(dat.index, dat, label=loc, linewidth=1,zorder=2)

# Plot the spread of all station data
plt.fill_between(combined_data.index, min_values, max_values, color='skyblue', alpha=0.4, label='Spread (Max - Min)',zorder=1)

# Adding a main title to the figure
# Extract the first and last year from the dataset
start_year = combined_data.index.year.min()
end_year = combined_data.index.year.max()

# Create the title automatically
main_title = f'Monthly Data for {start_year}-{end_year} in Utah (Max/Min Spread)'


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

