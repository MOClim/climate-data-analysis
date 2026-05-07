import pandas as pd
import matplotlib.pyplot as plt
import sys

import pandas as pd
import numpy as np
from pathlib import Path

# --- Read Data ---

# File paths for both datasets. Add data name for each path.
file_path = Path('../data/co2_daily_mld.csv')

# Assuming columns are year, month, day, decimal year, and CO2 level
column_names = ['Year', 'Month', 'Day', 'Decimal_Year', 'CO2']

# Read the CSV files, assuming data starts from the 33rd row
data = pd.read_csv(file_path, header=None, skiprows=32, names=column_names)

# Create a 'Date' column by combining year, month, and day
data['Date'] = pd.to_datetime(data[['Year', 'Month', 'Day']])
print(data.head())


# --- Create the plot ---

plt.figure(figsize=(10, 5))

# Figure title
fig_title = 'Daily Mauna Loa CO2'

# Defalut marker and line size
plt.plot(data['Date'], data['CO2'], marker='.', linestyle='-',color='g')

plt.title(fig_title)
plt.xlabel('Date')
plt.ylabel('CO2 mole fraction (ppm)')

plt.grid(True)

# Save the plot as a JPEG file
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)

# Display the plot
plt.show()

