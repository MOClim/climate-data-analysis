###############################################################################
# Exercise: Monthly Precipitation Histogram Analysis
#
# Additional Precipitation Processing
#
# Precipitation datasets may contain:
#
#   T = trace precipitation
#
# which indicates precipitation was observed but the amount was too small
# to measure accurately.
#
# Because 'T' is a text value, pandas reads the precipitation column
# as an object/string type instead of numeric data.
#
# The following code:
#   1. Replaces trace precipitation ('T') with 0.0 mm
#   2. Converts the precipitation column into numeric values
#
###############################################################################

import netCDF4 as nc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import math
from pathlib import Path

### Read Main ###

# Path of the downloaded CSV file
data_dir = Path('../../data_raw/map-server-report-1779136575/COOP/425186')

filename = data_dir / 'dly-report.csv'


# Read the CSV file
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

# Stop the program here for debugging.
# Comment out this line to continue the remaining analysis.
# Example:
#   # sys.exit()
sys.exit()

# Treat trace precipitation as 0.0 mm
df['pcpn'] = df['pcpn'].replace('T', 0.0)

# Convert precipitation to numeric
df['pcpn'] = pd.to_numeric(df['pcpn'], errors='coerce')

# Compute monthly mean precipitation
df_mon = df['pcpn'].resample('ME').mean()

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
plt.hist(all_data, bins=100, color='blue', edgecolor='black')

start_year = df_mon.index[0].year
end_year = df_mon.index[-1].year
total_months = len(df_mon)
total_years = int(math.ceil(total_months / 12))

plt.title(
    f'Histogram of Precipitation at USU '
    f'({start_year}-{end_year}, '
    f'{total_years} years, '
    f'{total_months} months)'
)

plt.xlabel('Precipitation (mm)')
plt.ylabel('Frequency (months)')
plt.grid(True)

# Adjust spacing automatically
plt.tight_layout()

# Save the plot as a JPEG file
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)


plt.show()

