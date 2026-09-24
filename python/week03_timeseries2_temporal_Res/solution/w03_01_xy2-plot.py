# ============================================================
# Student Tasks
# 1. Add the land CSV filename.
# 2. Add the ocean CSV filename.
# 3. Choose two plot colors.
# 4. Add the ocean plot command.
# 5. Add a figure title.
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import sys
from pathlib import Path

# --- Read Data ---

# --- Step 1: Enter CSV file names ---
# Replace the text inside the quotes with the FULL file path and filename.
# This includes both the folder location and the file name.
# Example (same folder): Path('filename.csv')
# Example (different folder): Path('../data/filename.csv')
# Example (absolute path): Path('/Users/yourname/data/filename.csv')

#data_dir = Path('../../data')
#data_dir2 = Path('../../data_raw')

# For scripts saved in the "solution/" directory:
# Use paths relative to the script location rather than the
# current working directory to ensure consistent file access.

# Get the directory where this script is located
script_dir = Path(__file__).resolve().parent

# Locate the repository root for student and instructor versions
# (the instructor version is inside an additional "solution" folder).
if script_dir.name == "solution":
    repo_dir = script_dir.parents[2]
else:
    repo_dir = script_dir.parents[1]

data_dir = repo_dir / 'data'
data_dir2 = repo_dir /'data_raw'

ocean_file_path = data_dir / 'NOAA.1850-2025.OCN.csv'
land_file_path = data_dir2 / 'NOAA.1850-2025.LND.csv'

# --- Read the CSV files ---
land_data = pd.read_csv(land_file_path, comment="#")
ocean_data = pd.read_csv(ocean_file_path, comment="#")


# --- Step 2: Choose plot colors ---

# Example colors: 'red', 'blue', 'green', 'black', 'orange'
land_color = 'orange'
ocean_color = 'blue'


# --- Initialize a new figure ---
# This creates a blank plotting canvas.
# figsize=(10, 5) sets the width and height of the figure in inches.
# You must call this BEFORE plotting so all graphs appear on this figure.

plt.figure(figsize=(10, 5))


# --- Plot the land data ---
plt.plot(land_data['Year'], land_data['Departure from Average'], marker='o', linestyle='-', color=land_color, label='Land',zorder=1)


# --- Step 3: Plot the ocean data ---

# Use the land plot above as a model.
# Change land_data to ocean_data, ocean_color, and label='Ocean'.
plt.plot(ocean_data['Year'], ocean_data['Anomaly'], marker='o', linestyle='-', color=ocean_color, label='Ocean',zorder=1)


# --- Step 4: Add a figure title ---

fig_title = 'Global Ocean and Land Temperature Anomalies'

# Adding title and labels
plt.title(fig_title)
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

