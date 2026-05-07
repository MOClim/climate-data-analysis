import pandas as pd
import matplotlib.pyplot as plt
import sys

import pandas as pd
import numpy as np
from pathlib import Path

# --- Read Data ---

# File paths for both datasets. Add data name for each path.
land_file_path = Path('../../data_raw/NOAA.1850-2025.LND.csv')
ocean_file_path = Path('../../data/NOAA.1850-2025.OCN.csv')

# Read the CSV files, assuming data starts from the 5th row
land_data = pd.read_csv(land_file_path, comment="#")
ocean_data = pd.read_csv(ocean_file_path, comment="#")


# --- Create the plot ---

plt.figure(figsize=(10, 5))

fig_title = "Area Plot of Ocean Temperature Anomalies"

# Fill positive anomalies with red
plt.fill_between(ocean_data['Year'], ocean_data['Anomaly'], where=(ocean_data['Anomaly'] > 0), color='red', alpha=0.5, label='Positive Anomaly')

# Fill negative anomalies with blue
plt.fill_between(ocean_data['Year'], ocean_data['Anomaly'], where=(ocean_data['Anomaly'] <= 0), color='blue', alpha=0.5, label='Negative Anomaly')

plt.plot(ocean_data['Year'], ocean_data['Anomaly'], color="Black", alpha=0.6, linewidth=1)
plt.title(fig_title)
plt.xlabel('Year')
plt.ylabel('Temperature')
plt.grid(True)

# Save the plot as a JPEG file
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)

# Display the plot
plt.show()

