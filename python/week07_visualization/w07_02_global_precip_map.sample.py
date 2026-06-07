"""
Global precipitation map using NOAA PSL UDel monthly climatology data.

Student direction:
- Change month_idx to select a different month.
- Change color_name to compare different colormaps.
- For precipitation, use a sequential colormap because precipitation is non-negative.
  Good examples: 'viridis', 'viridis_r', 'Blues', 'GnBu', 'YlGnBu'.
- Avoid diverging colormaps such as 'bwr' or 'seismic' unless the data have
  meaningful positive and negative values around a central value, such as anomaly data.

Data source:
https://psl.noaa.gov/data/gridded/data.UDel_AirT_Precip.html

Matplotlib colormap reference:
https://matplotlib.org/stable/users/explain/colors/colormaps.html
"""

import warnings
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import xarray as xr
import sys
from pathlib import Path

import warnings

warnings.filterwarnings(
    "ignore",
    message="invalid value encountered in create_collection",
    category=RuntimeWarning
)

month_idx = 0
month_name = ["January","February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]

# Path to your NetCDF file
indir = Path('../../data/')
filename = indir / 'precip.mon.v401.ltm.1981-2010.nc'
 
# Open the NetCDF dataset
ds = xr.open_dataset(filename, use_cftime=True)

# Extract temperature data for the specified month
dat = ds['precip'].isel(time=month_idx)
ds.close()

print("Shape of DataArray:",dat.shape)
print("Shape of DataArray.squeeze():",dat.squeeze().shape)

# ----- Plot the global data on a Map ----

# Create a figure and axis with Cartopy projection
fig = plt.figure(figsize=(12, 8))

# Choose the map projection type
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

# Step 1: Choose an appropriate colormap.
# Precipitation is non-negative, so a sequential colormap is usually best.
# Try changing this value and compare the maps.
# Examples: 'viridis', 'viridis_r', 'Blues', 'GnBu', 'YlGnBu'
# Full list: https://matplotlib.org/stable/users/explain/colors/colormaps.html
#color_name = 'bwr'
color_name = 'rainbow'
cmap = plt.get_cmap(color_name)

# Plotting using the defined axes
dmax = 8 
dmin = 0 
img = ax.pcolormesh(dat['lon'], dat['lat'], dat.squeeze(), cmap=cmap, transform=ccrs.PlateCarree(), shading='auto', vmin=dmin, vmax=dmax)

# Add coastlines
ax.coastlines()

# Add gridlines
ax.gridlines()

# Add a colorbar
cbar = fig.colorbar(img, ax=ax, orientation='vertical', shrink=0.7)
cbar.set_label('Precipitation (cm)')

# Add title with long_name attribute
long_name = dat.long_name if 'long_name' in dat.attrs else 'Temperature'
plt.title(f'{long_name} (GISST) for {month_name[month_idx]}')

# Save the plot as a JPEG file
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)

# Show the plot
plt.show()


