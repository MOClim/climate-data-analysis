"""
Correlation Analysis for Different Time Ranges

Description:
This example demonstrates how to compare global land and ocean
temperature anomalies using correlation analysis. The script reads
two climate datasets, selects a user-defined time range, calculates
the correlation coefficient, and visualizes both time series.

Learning Goals:
- Read climate datasets using Pandas
- Select and analyze a specific time period
- Calculate correlations between climate variables

Directions:
1. Set the start year and end year for the analysis.
2. Extract the selected time range from both datasets.
"""

import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress
from pathlib import Path
import sys

# File paths for both datasets. Add data name for each path.
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
data_dir = repo_dir / "data" 
data_dir2 = repo_dir / "data_raw"  

ocean_file_path = data_dir / 'NOAA.1850-2025.OCN.csv'
land_file_path = data_dir2 / 'NOAA.1850-2025.LND.csv'

# Read the CSV files
# comment='#' ignores metadata lines beginning with '#'
# index_col='Year' sets the Year column as the DataFrame index
tland_data = pd.read_csv(land_file_path, comment='#',index_col='Year')
tocean_data = pd.read_csv(ocean_file_path, comment='#',index_col='Year')

# Step 1: 
# Select the analysis period
# Choose the start and end years for correlation analysis
start_year = 1950
end_year = 2025

# Extract the temperature anomaly data for the selected period
land_data = tland_data['Anomaly'].loc[start_year:end_year]
ocean_data = tocean_data['Anomaly'].loc[start_year:end_year]

# Calculate the correlation coefficient between land and ocean temperatures
correlation = land_data.corr(ocean_data)
print(f'Correlation: {correlation}')

# Create the plot
plt.figure(figsize=(10, 5))

# Add the appropriate figure title here
fig_title = 'Temperature Anomalies: Land vs Ocean'

# Choose colors for land and ocean data
land_color = 'sienna'
ocean_color = 'deepskyblue'

# Plot land data
plt.plot(land_data.index, land_data, marker='o', linestyle='-', color=land_color, label='Land',zorder=1)

# Plot ocean data
plt.plot(ocean_data.index, ocean_data, marker='o', linestyle='-', color=ocean_color, label='Ocean',zorder=2)

# Adding title and labels
plt.title('Temperature Anomalies: Land vs Ocean')
plt.title(f'correlation={correlation:0.2f}', loc='right')
plt.xlabel('Year')
plt.ylabel('Temperature Anomaly (°C)')
plt.grid(True)

# Add a legend
plt.legend()

# Save the plot as a JPEG file
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)

# Display the plot
plt.show()


