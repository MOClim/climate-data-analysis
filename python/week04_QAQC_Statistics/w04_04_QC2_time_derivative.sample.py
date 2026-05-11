# ============================================================
# QA/QC Description
# ============================================================
#
# This exercise applies two quality control (QC) procedures
# to atmospheric temperature observations.
#
# QC1:
#     Detects values outside a physically realistic
#     temperature range and replaces them with NaN.
#
# QC2:
#     Detects unrealistically large temporal changes using
#     the squared time derivative and replaces them with NaN.
#
# Students should:
#     1. modify the QC2 criteria value,
#     2. run the script,
#     3. compare the original and QC datasets,
#     4. evaluate how different criteria values affect
#        spike detection and data removal.
#
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import sys
import copy

import pandas as pd
import numpy as np
from pathlib import Path

def QC1_range(data, variables, vmin, vmax):

    data = data.copy()

    for var in variables:

        mask = (data[var] < vmin) | (data[var] > vmax)

        data.loc[mask, var] = np.nan

    return data

def QC2_mark_extreme_time_variation(data, var, criteria):
    """
    QC2: Replace values with unrealistically large temporal changes with NaN.
    """

    data_qc = data.copy()

    temp_interp = data_qc[var].interpolate()

    data_qc["forward_diff"] = temp_interp.diff(periods=1) ** 2
    data_qc["backward_diff"] = temp_interp.diff(periods=-1) ** 2

    mask = (
        (data_qc["forward_diff"] > criteria * criteria)
        | (data_qc["backward_diff"] > criteria * criteria)
    )

    print("\nQC2: Extreme Time Variation")
    print(data_qc.loc[mask, ["forward_diff", "backward_diff", var]])

    data_qc.loc[mask, var] = np.nan

    return data_qc

def plot_data(ax, data, var, title, ylabel, funclog=False):
    """
    Plot time series data on a specified axis.
    """

    ax.plot(
        data.index,
        data[var],
        linestyle='-',
        linewidth=2,
        label=var
    )

    if funclog:
        ax.set_yscale('log')
        ax.set_ylim([5, data[var].max()])

    ax.set_title(title)
    ax.set_ylabel(ylabel)

    ax.set_xlim(data.index.min(), data.index.max())
    ax.grid(True)
    ax.legend()

    return ax


# --- Read Data ---

# File paths for the dataset.
# Daily climate observations for 2016
file_min_path = Path('../../data/Cedar_Min.2016.csv')

data_min = pd.read_csv(file_min_path, header=0, comment="#")

data_min["timestamp"] = pd.to_datetime(
    data_min["timestamp"],
    format="%m/%d/%y %H:%M"
)

data_min.set_index("timestamp", inplace=True)

select_vars = ["PRT1"]

data_min[select_vars] = (
    data_min[select_vars]
    .replace("NAN", np.nan)
    .astype(float)
)

print(data_min.head())
print(data_min[select_vars].describe())


# --- QC1: Data Range Test ---

min_temp = -40.
max_temp = 40.

data_qc1 = QC1_range(
    data_min,
    select_vars,
    min_temp,
    max_temp
)


# --- QC2: Time-Variation Test ---

# Step 1: Modify the criteria
# QC2 uses the squared time derivative:
#
#     (dT/dt)^2
#
# The criteria value is squared internally:
#
#     criteria2 = criteria * criteria
#
# Example:
#     criteria = 10  ->  (dT/dt)^2 = 100
#
# Smaller criteria values detect smaller spikes,
# while larger values detect only extreme variations.

criteria = 100

data_qc2 = QC2_mark_extreme_time_variation(
    data_qc1,
    "PRT1",
    criteria
)

# --- Create Plots ---

fig, ax = plt.subplots(4, 1, figsize=(6, 6))


# Plot 1 (original data)
funclog = False
plot_data(ax[0], data_min, 'PRT1', 'Temperature (Original) (C)', 'Temp', funclog)

# Plot 2 (QC1 data)
funclog = False
plot_data(ax[1], data_qc1, 'PRT1', 'Temperature (QC1 Data Range) (C)', 'Temp', funclog)

# Plot 3 (QC2 data)
funclog = False
plot_data(ax[2],data_qc2,'PRT1','Temperature (QC2 Time Deriv) (C)','Temp',funclog)

# Plot 4 (QC diff)
funclog = True
plot_data(ax[3], data_qc2,'forward_diff','Temperature Time Derivative Square (C)','Temp',funclog)


main_title = 'Minute QC data at Cedar City in 2016'
plt.suptitle(main_title, fontsize=12)
plt.tight_layout()

# Save the plot as a JPEG file
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)

# Display the plot
plt.show()

