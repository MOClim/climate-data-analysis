"""
Annual Histogram and Probability

Description:
This exercise uses daily COOP station data to examine the annual distribution of
climate variables. Students will calculate annual mean temperature and annual
accumulated precipitation, then compare histograms shown as frequency counts and
probabilities.

Directions:
1. Read the daily station CSV file.
2. Convert the date column to datetime format and set it as the DataFrame index.
3. Select the analysis period.
4. Convert trace precipitation ('T') to 0.0 mm and make precipitation numeric.
5. Resample daily data to annual values:
   - temperature: annual mean
   - precipitation: annual accumulation
6. Convert each annual pandas Series to a 1-D NumPy array and remove missing values.
7. Plot annual histograms as both frequency and probability.
8. Save the figure as a JPEG file.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

def pd_to_numpy(data):
    """Convert a pandas Series/DataFrame to a 1-D NumPy array without NaN values."""
    values_1d = data.values.flatten()
    return values_1d[~np.isnan(values_1d)]

def plot_histogram(data, nbins, xmin, xmax, color, title, x_label, show_probability):

    # Plot a histogram as frequency counts or probability for each bin.

    # Calculate histogram manually to get density values
    counts, bins = np.histogram(data, bins=nbins, range=(xmin, xmax))

    # Calculate centers of bins
    bin_centers = (bins[:-1] + bins[1:]) / 2

    bin_widths = np.diff(bins)

    if show_probability:
        y_values = counts / counts.sum()
        y_label = "Probability"
        value_format = "{:.2f}"
    else:
        y_values = counts
        y_label = "Frequency (years)"
        value_format = "{:.0f}"

    plt.bar(bin_centers, y_values, width=bin_widths, color=color, edgecolor="black")
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid(True)

    for x_value, y_value in zip(bin_centers, y_values):
        plt.text(x_value, y_value, value_format.format(y_value), ha="center", va="bottom")


# -----------------------------
# Main script
# -----------------------------

# Set data path
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
data_dir = repo_dir / "data_raw/map-server-report-1791475073/GHCN/USC00425186"

filename = data_dir / 'dly-report.csv'

# Set analysis period
start_year = "1893"
end_year = "2010"

# Read the CSV file
# The first 19 rows contain station metadata, so they are skipped.
#df = pd.read_csv(filename, header=0, skiprows=19, na_values="nan")
df = pd.read_csv(filename, header=0, skiprows=19, na_values="NaN")

# Convert the date column to datetime format and use it as the index
df["day"] = pd.to_datetime(df["day"])
df = df.set_index("day")

# Select the analysis period
df = df.loc[start_year:end_year]

# Treat trace precipitation as 0.0 mm
# 'T' means trace precipitation: observed, but too small to measure accurately.
df["Precipitation"] = df["Precipitation"].replace("T", 0.0)

# Convert precipitation to numeric values; invalid values become NaN
df["Precipitation"] = pd.to_numeric(df["Precipitation"], errors="coerce")
print(df["Max Temperature"])
#sys.exit()

# Select daily variables
daily_temp = df["Min Temperature"]
daily_prc = df["Precipitation"]

# Calculate annual climate statistics
annual_avg_temp = daily_temp.resample("YE").mean()
annual_sum_prc = daily_prc.resample("YE").sum()

# Convert annual pandas Series to 1-D NumPy arrays without missing values
annual_temp = pd_to_numpy(annual_avg_temp)
annual_prc = pd_to_numpy(annual_sum_prc)

# Create and plot the histograms
plt.figure(figsize=(12, 6))

# Annual temperature histogram settings
temp_min = -6
temp_max =  8
temp_bins = 13

plt.subplot(2, 2, 1)
plot_histogram(
    annual_temp,
    temp_bins,
    temp_min,
    temp_max,
    "orange",
    "Annual Temperature",
    "Temperature (°C)",
    show_probability=False,
)

plt.subplot(2, 2, 3)
plot_histogram(
    annual_temp,
    temp_bins,
    temp_min,
    temp_max,
    "orange",
    "Annual Temperature",
    "Temperature (°C)",
    show_probability=True,
)

# Annual precipitation histogram settings
prc_min = 0.0
prc_max = 900.0
prc_bins = 9

plt.subplot(2, 2, 2)
plot_histogram(
    annual_prc,
    prc_bins,
    prc_min,
    prc_max,
    "blue",
    "Annual Precipitation",
    "Precipitation (mm)",
    show_probability=False,
)

plt.subplot(2, 2, 4)
plot_histogram(
    annual_prc,
    prc_bins,
    prc_min,
    prc_max,
    "blue",
    "Annual Precipitation",
    "Precipitation (mm)",
    show_probability=True,
)

# Add the main title and adjust spacing
plt.suptitle(f"USU Annual Climate Distribution ({start_year}–{end_year})", fontsize=16)
plt.subplots_adjust(hspace=0.5)

# Save the plot as a JPEG file with the same base name as this script
output_path = Path(__file__).with_suffix(".jpg")
plt.savefig(output_path, dpi=300, bbox_inches="tight")

plt.show()
