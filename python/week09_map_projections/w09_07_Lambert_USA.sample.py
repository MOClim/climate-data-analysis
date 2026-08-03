# ---------------------------------------------------------
# Lambert Projection Map over the United States
# ---------------------------------------------------------
# This program plots January 2026 2-m air temperature
# anomalies using NOAA NCEP/NCAR Reanalysis data.
#
# The anomaly is calculated relative to the 1991–2020
# January climatology. The Lambert Conformal projection is
# used because it is well suited for mid-latitude regional
# maps, including the contiguous United States.
#
# Students can modify:
#   1. the map center in LambertConformal()
#   2. the color range using clevs below
#   3. the map domain in ax.set_extent()
# ---------------------------------------------------------

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pathlib import Path
import sys

import warnings
warnings.filterwarnings(
    "ignore",
    message="invalid value encountered in create_collection",
    category=RuntimeWarning
)


# -----------------------------
# Load data
# -----------------------------

# NOAA PSL OPeNDAP URL
#air_url = (
#    "https://psl.noaa.gov/thredds/dodsC/"
#    "Datasets/ncep.reanalysis.derived/surface/air.mon.mean.nc"
#)
#ds = xr.open_dataset(air_url)

# NOAA PSL local NetCDF file
script_dir = Path(__file__).resolve().parent

# Check whether the script is inside the "solution" directory
if script_dir.name == "solution":
    # Move up two directory levels to reach the repository root
    repo_dir = script_dir.parents[2]
else:
    # Move up two directory levels to reach the repository root
    repo_dir = script_dir.parents[1]

air_file = repo_dir / "data/air.2m.mon.mean.nc"
ds = xr.open_dataset(air_file)

print(ds)
print(ds.time[-1].values)

# ---------------------------------------------------------
# Calculate January 2026 air temperature anomaly
# ---------------------------------------------------------
# Select 2-m air temperature and convert from Kelvin to Celsius

air = ds["air"].load()

# Convert K to °C
air_c = air - 273.15

# January climatology (1991–2020)
ref = air_c.sel(time=slice("1991-01-01", "2020-12-31"))
jan_clim = ref.groupby("time.month").mean("time").sel(month=1)

# January 2026 anomaly
jan_2026 = air_c.sel(time="2026-01-01").squeeze()
anom = jan_2026 - jan_clim

print("Anomaly Minimum = ",anom.min().values)
print("Anomaly Maximum = ",anom.max().values)


# Create figure
fig = plt.figure(figsize=(10, 6))

#
# Use Lambert Conformal projection
# Step 1: Define the map projection.
# The central longitude and latitude place the projection center
# near the middle of the contiguous United States.
# central_longitude=xx,
# central_latitude=xx
#
ax = plt.axes(
    projection=ccrs.LambertConformal(
        central_longitude=,
        central_latitude=
    )
)

# ---------------------------------------------------------
# Set the color range for the anomaly map
# ---------------------------------------------------------
# Step 2: Change these values to adjust the color range.
# For example:
#   np.arange(-10, 10.1, 1)  -> -10 to +10 °C, every 1 °C
#   np.arange(-15, 15.1, 1)  -> -15 to +15 °C, every 1 °C
clevs = np.arange(, , )

anom.plot(
    ax=ax,
    transform=ccrs.PlateCarree(),
    cmap="RdBu_r",
    levels=clevs,
    cbar_kwargs={"label": "2-m Air Temperature Anomaly (°C)"}
)

#
# Focus on the contiguous United States
# Step 3: Set the map domain.
# [west longitude, east longitude, south latitude, north latitude]
# This range focuses on the contiguous United States.
#
ax.set_extent(
    [, , , ], 
    crs=ccrs.PlateCarree())

ax.coastlines()
ax.add_feature(cfeature.BORDERS, linewidth=0.5)
ax.add_feature(cfeature.STATES, linewidth=0.3)

ax.set_title("January 2026 Air Temperature Anomaly (Lambert Projection)")

output_path = Path(__file__).with_suffix(".jpg")
plt.savefig(output_path, dpi=300)
plt.show()
