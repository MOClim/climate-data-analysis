import pandas as pd
import matplotlib.pyplot as plt
import sys
import copy

import pandas as pd
import numpy as np
from pathlib import Path

# Source URL for the dataset
# This data is downloaded from the Utah Climate Center
# URL: https://climate.usu.edu/mchd/
# Location: UCRN Cedar City

def plot_data(data,kr,var,varname,unit):

  plt.plot(data.index, data[var]*kr, marker='.', linestyle='-', color="green", label=var,zorder=1, linewidth=2)

  # Adding title and labels
  plt.title(varname)
  plt.ylabel(varname+' ('+unit+')')
  plt.grid(True)

  # Set the x-axis limits to cover the full date range
  plt.xlim([data.index.min(), data.index.max()])

  # Add legend labels to distinguish between different datasets on the plot.
  plt.legend()

  return plt

# --- Read Data ---

# File paths for the dataset.
# Daily climate observations for 2016
file_min_path = Path('../../data/Cedar_Min.2016.csv')


# Read the CSV file, assuming the header at the 1st line
data_min = pd.read_csv(file_min_path, header=0, comment="#")
print(data_min.head())

# Convert to datetime
data_min['timestamp'] = pd.to_datetime(data_min['timestamp'], format='%m/%d/%y %H:%M')
print(data_min['timestamp'].head())

# Set 'Date' as the index of the DataFrame
data_min.set_index('timestamp', inplace=True)

# Convert the specified columns to float
columns_to_convert = ['PRT1', 'PRT2', 'PRT3']
data_min[columns_to_convert] = data_min[columns_to_convert].astype(float)

# Replace 'NAN' strings with np.nan
data_min=data_min.replace('NAN', np.nan)


# --- Create the plot ---

plt.figure(figsize=(10, 5))

# Adding a main title to the figure
main_title = 'Minutes Data at Cedar City in 2016'
plt.suptitle(main_title, fontsize=16)

# Plot data
kr = 1.
plt = plot_data(data_min,kr,'PRT1','Temperature (Original data)','C')

# Adjust layout to prevent overlap
plt.tight_layout()

# Save the plot as a JPEG file
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)

# Display the plot
plt.show()

