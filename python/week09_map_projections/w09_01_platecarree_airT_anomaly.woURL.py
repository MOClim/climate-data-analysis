# ---------------------------------------------------------
# Map Projections for Effective Global Analysis
# ---------------------------------------------------------
# This program visualizes global air temperature anomalies
# using NOAA NCEP/NCAR Reanalysis data and Cartopy.
#
# Different projections preserve different properties:
#   PlateCarree : Simple latitude–longitude grid
#   Robinson    : Better visual balance for global maps
#   Lambert     : Useful for mid-latitude regional analysis
#   Projection list:
#   https://scitools.org.uk/cartopy/docs/v0.15/crs/projections.html
#
# IMPORTANT:
# This exercise is setup to read a downloaded NetCDF data instead of 
# an online OPeNDAP URL. 
#
#
# Some Cartopy tutorials use cartopy.crs directly.
# In this course, we import cartopy.crs as "ccrs"
# as a short alias for convenience.
#
# Example:
# cartopy.crs.Robinson() == ccrs.Robinson()
# ---------------------------------------------------------

import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pathlib import Path
import sys
import numpy as np
from cartopy.util import add_cyclic_point

import warnings
warnings.filterwarnings(
    "ignore",
    message="invalid value encountered in create_collection",
    category=RuntimeWarning
)


# -----------------------------
# Load data
# -----------------------------

# Example NOAA PSL OPeNDAP URLs
air_url = "https://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis.derived/surface/air.mon.mean.nc"
prate_url = "https://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis.derived/surface/prate.sfc.mon.mean.nc"
sst_url = "https://psl.noaa.gov/thredds/dodsC/Datasets/COBE2/sst.mon.mean.nc"

# Step 1: Inspect the dataset structure and available time range.
# Run this section first and check the printed output.
# Once you understand the data format, comment out sys.exit()
# so the script can proceed to the remaining steps.

indir = Path('../../data')
filename = indir / 'air.2m.mon.mean.nc'

ds = xr.open_dataset(filename)
print(ds)
#print(ds['air'].values)
#print(ds.time[-1].values)
#sys.exit()

# Select near-surface air temperature
# Convert from K to degC if needed
air_c = ds['air'] - 273.15

# Example: January climatology
jan_clim = air_c.sel(time=slice("1991-01-01", "2020-12-31")).where(
    air_c["time.month"] == 1, drop=True
).mean("time")

# Example: January 2026 anomaly
jan_2026 = air_c.sel(time="2026-01-01")
anom = jan_2026 - jan_clim

print("Anomaly Minimum = ",anom.min().values)
print("Anomaly Maximum = ",anom.max().values)

# Add cyclic point to close the 0/360 longitude seam
anom_cyclic, lon_cyclic = add_cyclic_point(anom.values, coord=anom.lon)
print('')
print("Data type:", type(anom_cyclic))
print("Shape:", anom_cyclic.shape)
print("Dimensions:", anom_cyclic.ndim)


# Reconstruct xarray DataArray
anom_cyclic_xr = xr.DataArray(anom_cyclic,
    coords={"lat": anom.lat,"lon": lon_cyclic},
    dims=("lat", "lon"), name="prate_anomaly",
    attrs=anom.attrs)

print(' ')
print('Original anomaly (anom) coordinates: ')
print(anom.coords)
print(' ')
print('New anomaly (anom_cyclic_xr) coordinates after add_cyclic: ')
print(anom_cyclic_xr.coords)
print("Data type:", type(anom_cyclic_xr))
#sys.exit()

# Plot
fig = plt.figure(figsize=(10, 5))

# projection: map coordinate system (output)
# transform : data coordinate system (input)

ax = plt.axes(projection=ccrs.PlateCarree())

#levels = np.arange(-20, 22, 2)
#print(levels)

anom.plot(
    ax=ax,
    transform=ccrs.PlateCarree(),
    cmap="RdBu_r",
    levels=21,
    cbar_kwargs={"label": "2-m Air Temperature Anomaly (°C)"}
)

ax.coastlines()
ax.add_feature(cfeature.BORDERS, linewidth=0.5)
ax.set_global()
ax.set_title("January 2026 Air Temperature Anomaly")

output_path = Path(__file__).with_suffix(".jpg")
plt.savefig(output_path, dpi=300)

plt.show()
