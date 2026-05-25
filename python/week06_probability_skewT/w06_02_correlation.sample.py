import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress
from pathlib import Path
import sys

# File paths for both datasets. Add data name for each path.
ocean_file_path = Path('../../data/NOAA.1850-2025.OCN.csv')
# Students should have downloaded land CO2 flux from NOAA website 
# (see details in week2 slide).
# https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/global/time-series
land_file_path = Path('../../data_raw/NOAA.1850-2025.LND.csv')

# Read the CSV files
tland_data = pd.read_csv(land_file_path, comment='#',index_col='Year')
tocean_data = pd.read_csv(ocean_file_path, comment='#',index_col='Year')

land_data = tland_data['Anomaly']
ocean_data = tocean_data['Anomaly']

# Calculate the correlation
correlation = land_data.corr(ocean_data)
print(f'Correlation: {correlation}')

# Create the plot
plt.figure(figsize=(10, 5))

# Add the appropriate figure title here
fig_title = 'Temperature Anomalies: Land vs Ocean'

# Choose colors for land and ocean data
land_color = 'sienna'
ocean_color = 'deepskyblue'

# Plot land data
plt.plot(land_data.index, land_data, marker='o', linestyle='-', color=land_color, label='Land',zorder=1)

# Plot ocean data
plt.plot(ocean_data.index, ocean_data, marker='o', linestyle='-', color=ocean_color, label='Ocean',zorder=2)

# Adding title and labels
plt.title('Temperature Anomalies: Land vs Ocean')
plt.title(f'correlation={correlation:0.2f}', loc='right')
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


