import pandas as pd
import matplotlib.pyplot as plt
import sys

import pandas as pd
import numpy as np
from pathlib import Path

# Source URL for the dataset
# This data is downloaded from the Utah Climate Center
# URL: https://climate.usu.edu/mchd/
# The dataset contains daily precipitation water in March 2026.
# Location: UCRN Beaver

# --- Read Data ---


# Tips: easy copy and paste by Mac
# 1. click filename and command C on terminal
# 2. move cursol to the location where you want to add filename
# 3. command v

# File paths for the dataset. 
data_dir = Path('../../data_raw')

# Add data name for the path. 
file_path = data_dir / 'beaver-big-flat-nfs-ucrn.csv'

# Read the CSV file: Skip metadata lines beginning with '#'
data = pd.read_csv(file_path, header=0, comment="#")

# Convert to datetime
data['Category'] = pd.to_datetime(data['Category'])
# Set 'Category' as the index of the DataFrame.
data.set_index('Category', inplace=True)
print(data.head())


# --- Create the plot ---

plt.figure(figsize=(10, 5))

# Figure title
fig_title = 'Daily Precipitation for March 2026 at Beaver'

plt.plot(data.index, data['Precipitation'], color='blue')

plt.title(fig_title)
plt.xlabel('Date')
plt.ylabel('Precipitation (mm)')

plt.grid(True)

# Save the plot as a JPEG file
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)

# Display the plot
plt.show()


