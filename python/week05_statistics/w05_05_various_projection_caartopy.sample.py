"""
Exercise: Compare Different Map Projections using Cartopy

This script reads sea surface temperature (SST) data from a netCDF file
and displays the data using several different map projections.

Data availability: https://www.metoffice.gov.uk/hadobs/hadisst/data/download.html

Learning Objectives:
- Read climate data from a netCDF file
- Visualize gridded SST data
- Create maps using Cartopy
- Compare different map projections
- Add coastlines, gridlines, and colorbars
- Save figures as image files
"""

import warnings
from pathlib import Path

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
from netCDF4 import Dataset
from cartopy import feature

import warnings
warnings.filterwarnings("ignore", message="invalid value encountered in create_collection")

# reading in netCDF file
filename = Path('../../data/HadISST_sst.nc')

# Open the netCDF dataset
f = Dataset(filename, mode='r')

# Read longitude, latitude, and SST data
lons = f.variables['longitude'][:]
lats = f.variables['latitude'][:]
sst = f.variables['sst'][0, :, :]

# Close the file
f.close()

#### Replace missing values with NaN ####

sst = np.where(sst == -1000, np.nan, sst)
sst = np.where(sst == -1.e+30, np.nan, sst)


## Mask the data: replace -1000 with NaN
#fld = np.where(dat == -1000, np.nan, dat)
#fld = np.where(fld == -1.e+30, np.nan, fld)


# define contour levels
levels = np.arange(0, 26, 1)

# set up figure and map projection
fig = plt.figure(figsize=(14., 7))

# Define map projections
projections = [
    ("PlateCarree", ccrs.PlateCarree()),
    ("Robinson", ccrs.Robinson()),
    ("Mollweide", ccrs.Mollweide()),
    ("LambertConformal", ccrs.LambertConformal()),
    ("Orthographic", ccrs.Orthographic()),
    ("InterruptedGoodeHomolosine", ccrs.InterruptedGoodeHomolosine()),
    ("RotatedPole",ccrs.RotatedPole(pole_latitude=37.5,pole_longitude=177.5)),
    ("Orthographic",ccrs.Orthographic())
]

for i, (title, projection) in enumerate(projections):

    # Create subplot
    ax = plt.subplot(2, 4, i + 1, projection=projection)

    # Add coastlines
    ax.coastlines(linewidth=0.5)

    # Add gridlines
    ax.gridlines(
        linewidth=0.5,
        linestyle=':'
    )

    # Add title
    ax.set_title(title, fontsize=12)

    # Plot SST data
    myplot = ax.contourf(
        lons,
        lats,
        sst,
        levels,
        transform=ccrs.PlateCarree(),
        cmap='viridis',
        extend='both'
    )

#### Add colorbar ####

#cbar = plt.colorbar(
#    myplot,
#    orientation='horizontal',
#    pad=0.05
#)


## Set global font size
#plt.rcParams.update({'font.size': 20})


# add colorbar
# Adjust spacing for 8 larger maps
plt.subplots_adjust(
    left=0.03,
    bottom=0.12,
    right=0.97,
    top=0.92,
    wspace=0.15,
    hspace=0.20
)

# Add one shared colorbar at the bottom
cbaxes = fig.add_axes([0.25, 0.09, 0.50, 0.025])

cbar = plt.colorbar(myplot, orientation='horizontal', cax=cbaxes)
cbar.set_label('Sea Surface Temperature (°C)', fontsize=14)
cbar.ax.tick_params(labelsize=10)


# Save the figure to a file
output_path = Path(__file__).with_suffix('.jpg')
fig.savefig(output_path, dpi=300)

# Show the figure
plt.show()
