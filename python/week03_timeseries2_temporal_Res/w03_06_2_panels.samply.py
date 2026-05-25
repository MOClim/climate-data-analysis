import pandas as pd
import matplotlib.pyplot as plt
import sys

import pandas as pd
import numpy as np
from pathlib import Path

# Source URL for the dataset
# This data is downloaded from the Utah Climate Center
# URL: https://climate.usu.edu/mchd/
# The dataset contains daily precipitation water in April 2024.
# Location: UAGRIMET Preston 

# --- Read Data ---

# File paths for the dataset.
data_dir Path('../../data_raw')

# Add data name for the path. 
file_path = data_dir / 'beaver-big-flat-nfs-ucrn.csv'

# Read the CSV file, assuming data starts from the first row (so no skiprow command)
data = pd.read_csv(file_path)
print(data.head())

# Convert to datetime
data['Category'] = pd.to_datetime(data['Category'])
print(data.head())

# Set 'Date' as the index of the DataFrame
data.set_index('Category', inplace=True)
print(data.head())


# --- Create the plot ---

plt.figure(figsize=(8, 5))

# Create first subplot
plt.subplot(2, 1, 1)  # 1 row, 2 columns, first subplot
plt.plot(data.index, data['Precipitation'], color='blue')


fig_title = 'Daily Precipitation for March 2026 at Beaver'
plt.title(fig_title)
plt.xlabel('Date')
plt.ylabel('Precipitation (mm)')
# Set the x-axis limits to cover the full date range
xmin = data.index.min()-pd.Timedelta(days=1)
xmax = data.index.max()+ pd.Timedelta(days=1)
plt.xlim([xmin, xmax])
plt.grid(True)

# Create second subplot
plt.subplot(2, 1, 2)  # 1 row, 2 columns, first subplot
plt.bar(data.index, data['Precipitation'], color='blue')
plt.title(fig_title)
plt.xlabel('Date')
plt.ylabel('Precipitation (in)')
# Set the x-axis limits to cover the full date range
xmin = data.index.min()-pd.Timedelta(days=1)
xmax = data.index.max()+ pd.Timedelta(days=1)
plt.xlim([xmin, xmax])
plt.grid(True)

# Adjust layout to prevent overlap
plt.tight_layout()

# Save the plot as a JPEG file
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)

# Display the plot
plt.show()

