# --- QC 1: Data Range Test ---
#
# QA/QC Procedure
# ---------------
# 1. Inspect the original data using plots and summary statistics.
# 2. Define physically realistic minimum and maximum thresholds.
# 3. Apply the QC1 range test to detect unrealistic values.
# 4. Replace values outside the accepted range with NaN.
# 5. Compare original and QC-modified datasets.
# 6. Evaluate the effect of QC1 using visualization.
#
# Exercise Steps
# --------------
# Step 1: Modify the QC1 threshold values:
#
#         min_temp = -40.
#         max_temp =  50.
#
# Step 2: Run the code and generate the QC1 plots.
#
# Step 3: Evaluate whether unrealistic values were properly removed
#         without excluding valid environmental variability.

import copy
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

def QC1_range(data, variables, vmin, vmax):

    data = data.copy()

    for var in variables:

        mask = (data[var] < vmin) | (data[var] > vmax)

        data.loc[mask, var] = np.nan

    return data

def plot_data(ax, data, var, title, unit):
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
    ax.set_ylabel(f"{title} ({unit})")
    ax.set_xlim(data.index.min(), data.index.max())
    ax.grid(True)
    ax.legend()

    return ax


# --- Read Data ---

# File paths for the dataset.
# Daily climate observations for 2016

# Define the relative path to the data directory
#data_dir = Path("../../data/")

# Get the directory where this script is located
script_dir = Path(__file__).resolve().parent

# Check whether the script is inside the "solution" directory
if script_dir.name == "solution":
    # Move up two directory levels to reach the repository root
    repo_dir = script_dir.parents[2]
else:
    # Move up two directory levels to reach the repository root
    repo_dir = script_dir.parents[1]
# Define the path to the UCRN data directory
data_dir = repo_dir / "data" 

file_min_path = data_dir/"Cedar_Min.2016.csv"


# Read the CSV file, assuming the header at the 1st line
data_min = pd.read_csv(file_min_path, header=0, comment="#")
print(data_min.head())

# Convert to datetime
data_min['timestamp'] = pd.to_datetime(data_min['timestamp'], format='%m/%d/%y %H:%M')

# Set 'Date' as the index of the DataFrame
data_min.set_index('timestamp', inplace=True)

# Convert the specified columns to float
select_vars = ['PRT1', 'PRT2', 'PRT3']
data_min[select_vars] = data_min[select_vars].astype(float)

# Replace 'NAN' strings with np.nan
data_min=data_min.replace('NAN', np.nan)

# Create a deep copy of the original dataset
data_qc = data_min.copy()


# Step 1: Change appropriate temperature ranges
min_temp = -40.
max_temp = 50.

# --- QC 1 ---
# Call the function to detect extremes (outside the defined data range) 
# and convert them to missing values.
data_qc = QC1_range(data_min, select_vars, min_temp, max_temp)

# --- Create Plots ---
# plt.figure() creates only the figure container and requires
# subplot axes to be added manually using plt.subplot().

# plt.subplots() creates both the figure object (fig)
# and subplot axes (ax) simultaneously, providing a cleaner
# and more flexible plotting workflow.

fig, ax = plt.subplots(2, 1, figsize=(8, 8))

# Original data
plot_data(ax[0], data_min, 'PRT1', 'Temperature (Original Data)', 'C')

# QC data
plot_data(ax[1], data_qc, 'PRT1', 'Temperature (QC1 Data Range)', 'C')

plt.tight_layout()


# Save the plot as a JPEG file
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)

# Display the plot
plt.show()

