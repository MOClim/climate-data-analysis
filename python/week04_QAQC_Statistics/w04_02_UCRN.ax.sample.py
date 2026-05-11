"""
Exercise: Minutes Time Series Plot using fig, ax

This exercise demonstrates how to create a time-series figure
using the matplotlib object-oriented plotting approach.

Students will:
    - read minute climate observations from a CSV file,
    - convert timestamps into datetime format,
    - create a time-series plot using fig and ax,
    - modify plot colors,
    - save the figure as a JPG image.

Compared to plt.figure() and plt.subplot(),
fig, ax = plt.subplots() creates both the figure object
and plotting axes simultaneously, providing a cleaner
and more flexible plotting workflow.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_data(ax, data, var, title, ylabel):
    """
    Plot time series data on a specified axis.
    """

    ax.plot(
        data.index,
        data[var],
        marker='.',
        linestyle='-',
        linewidth=2,
        label=var
    )

    ax.set_title(title)
    ax.set_ylabel(ylabel)

    ax.set_xlim(data.index.min(), data.index.max())

    ax.grid(True)
    ax.legend()

    return ax


# --- Read Data ---

# File path for the dataset
# Minute climate observations for 2016
file_min_path = Path('../../data/Cedar_Min.2016.csv')


# Read the CSV file
# Lines beginning with '#' are ignored.
data_min = pd.read_csv(file_min_path, header=0, comment="#")

print(data_min.head())


# Convert timestamp column into datetime format
data_min['timestamp'] = pd.to_datetime(data_min['timestamp'],format='%m/%d/%y %H:%M')

print(data_min['timestamp'].head())


# Set datetime as the DataFrame index
data_min.set_index('timestamp', inplace=True)


# Convert selected variables to float
columns_to_convert = ['PRT1', 'PRT2', 'PRT3']

data_min[columns_to_convert] = (data_min[columns_to_convert]
    .replace('NAN', np.nan).astype(float))


# --- Create the Plot ---

# fig:
#     Figure container
#
# ax:
#     Plotting axis object
#
# plt.subplots() creates both objects simultaneously.

fig, ax = plt.subplots(figsize=(10, 5))

# Plot temperature observations
plot_data(ax,data_min,'PRT1','Temperature (Original Data) (C)','Temp')

# Add a main title to the figure
main_title = 'Minutes Data at Cedar City in 2016'
fig.suptitle(main_title, fontsize=16)

# Adjust layout to prevent overlap
fig.tight_layout()

# Save the figure as a JPG file
output_path = Path(__file__).with_suffix('.jpg')
fig.savefig(output_path, dpi=300)

# Display the figure
plt.show()

