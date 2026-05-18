import pandas as pd
import matplotlib.pyplot as plt
import sys, os
import glob

import pandas as pd
import numpy as np
from pathlib import Path

# Specify the directory path
# List all CSV files in the directory
filenames = list(Path('../../data/UCRN').glob('*.csv'))


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

# Calculate the mean across the 16 time series for each time point
mean_series = combined_data.mean(axis=1)

# Calculate the standard deviation across the 16 time series for each time point
std_series = combined_data.std(axis=1)

# Calculate +1 sigma and -1 sigma
plus_1_sigma = mean_series + std_series
minus_1_sigma = mean_series - std_series

# --- Create the plot ---

plt.figure(figsize=(10, 6))

# Plot the average of all station data
plt.plot(mean_series.index, mean_series, label='Average', color='black',linewidth=2,zorder=3)

# Plot each station data
for dat, file_path, loc in zip(monthly_dats, filenames, location_info):
    plt.plot(dat.index, dat, label=loc, linewidth=1,zorder=2)

# Plot the spread of all station data
plt.fill_between(combined_data.index, minus_1_sigma, plus_1_sigma, color='pink', alpha=0.6, label='Spread (±1σ)',zorder=1)

# Extract the first and last year from the dataset
start_year = combined_data.index.year.min()
end_year = combined_data.index.year.max()

# Create the title automatically
main_title = f'Monthly Mean Air Temperature and ±1σ Spread in Utah ({start_year}-{end_year})'

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

