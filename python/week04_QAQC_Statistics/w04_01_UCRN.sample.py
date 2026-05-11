import pandas as pd
import matplotlib.pyplot as plt
import sys
import copy

import pandas as pd
import numpy as np
from pathlib import Path

def plot_data(data, var, title, ylabel):
    """
    Plot time series data on a specified axis.
    """

    plt.plot(
        data.index,
        data[var],
        marker='.',
        linestyle='-',
        linewidth=2,
        label=var
    )

    plt.title(title)
    plt.ylabel(ylabel)

    plt.xlim(data.index.min(), data.index.max())
    plt.grid(True)
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
plt = plot_data(data_min,'PRT1','Temperature (Original data) (C)','Temp')

# Adjust layout to prevent overlap
plt.tight_layout()

# Save the plot as a JPEG file
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)

# Display the plot
plt.show()

