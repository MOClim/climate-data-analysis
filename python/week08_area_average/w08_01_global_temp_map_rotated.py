# ---------------------------------------------------------
# Global Surface Air Temperature Map
# ---------------------------------------------------------
# This program reads a NOAA global temperature NetCDF file
# and visualizes monthly climatological temperature data
# on a world map using Cartopy.
#
# Students can:
#   - Change month_idx to display different months
#   - Experiment with different colormaps
#   - Modify dmin and dmax to adjust the color range
#
# Diverging colormaps such as 'bwr' or 'seismic'
# are useful for temperature data because they clearly
# separate colder and warmer regions.
#
# Example colormaps:
#   'bwr'
#   'seismic'
#   'coolwarm'
#   'RdBu_r'
#
# Matplotlib colormap reference:
# https://matplotlib.org/stable/users/explain/colors/colormaps.html
#
# Data source:
# GISS Surface temperature analysis (https://psl.noaa.gov/data/gridded/tables/temperature.html)
# ---------------------------------------------------------

import warnings
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import xarray as xr
import sys
from pathlib import Path

import matplotlib.ticker as mticker
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

month_name = ["January","February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]

month_idx = 0

# Path to your NetCDF file

filename = Path('../../data/air.2x2.250.mon.1991-2020.ltm.comb.nc')
 
# Open the NetCDF dataset
ds = xr.open_dataset(filename, use_cftime=True)

# Extract temperature data for the specified month
dat = ds['air'].isel(time=month_idx)
ds.close()

print("Shape of DataArray:",dat.shape)
print("Shape of DataArray.squeeze():",dat.squeeze().shape)


# ----- Plot the global data on a Map ----

# Create a figure and axis with Cartopy projection
fig = plt.figure(figsize=(12, 8))

# ---------------------------------------------------------
# Choose the map projection
#
# central_longitude controls the longitude at the center
# of the map.
#
# Examples:
#   0   = Atlantic-centered view
#   180 = Pacific-centered view
# ---------------------------------------------------------

#ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(central_longitude=180))


# Define the colormap 
color_name = 'bwr'
cmap = plt.get_cmap(color_name)

dmax = 3
dmin = -3
img = ax.pcolormesh(dat['lon'], dat['lat'], dat.squeeze(), cmap=cmap, transform=ccrs.PlateCarree(), shading='auto', vmin=dmin, vmax=dmax)

# Add coastlines
ax.coastlines()

# Add gridlines
#ax.gridlines()

gl = ax.gridlines(
    draw_labels=True,
    linewidth=0.5,
    color='gray',
    alpha=0.5,
    linestyle='--'
)

gl.top_labels = False
gl.right_labels = False

gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER

gl.xlocator = mticker.FixedLocator(np.arange(-180, 181, 60))
gl.ylocator = mticker.FixedLocator(np.arange(-90, 91, 30))


# Add a colorbar
cbar = fig.colorbar(img, ax=ax, orientation='vertical', shrink=0.7)
cbar.set_label('Temperature (°C)')

# Add title with long_name attribute
long_name = dat.long_name if 'long_name' in dat.attrs else 'Temperature'
plt.title(f'{long_name} (GISST) for {month_name[month_idx]}')

# Save the plot as a JPEG file
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)

# Show the plot
plt.show()


