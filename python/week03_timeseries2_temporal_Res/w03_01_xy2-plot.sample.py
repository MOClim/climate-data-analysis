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

data_dir = Path('ENTER_FULL_PATH')
data_dir2 = Path('ENTER_FULL_PATH')

ocean_file_path = data_dir / 'ENTER_OCEAN_FILE.csv'
land_file_path = data_dir2 / 'ENTER_LAND_FILE.csv'

# --- Read the CSV files ---
land_data = pd.read_csv(land_file_path, comment="#")
ocean_data = pd.read_csv(ocean_file_path, comment="#")


# --- Step 2: Choose plot colors ---

# Example colors: 'red', 'blue', 'green', 'black', 'orange'
land_color = 'ENTER_LAND_COLOR'
ocean_color = 'ENTER_OCEAN_COLOR'


# --- Initialize a new figure ---
# This creates a blank plotting canvas.
# figsize=(10, 5) sets the width and height of the figure in inches.
# You must call this BEFORE plotting so all graphs appear on this figure.

plt.figure(figsize=(10, 5))


# --- Plot the land data ---
plt.plot(land_data['Year'], land_data['Anomaly'], marker='o', linestyle='-', color=land_color, label='Land',zorder=1)


# --- Step 3: Plot the ocean data ---

# Use the land plot above as a model.
# Change land_data to ocean_data, ocean_color, and label='Ocean'.


# --- Step 4: Add a figure title ---

fig_title = 'YOUR_FIGURE_TITLE'

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

