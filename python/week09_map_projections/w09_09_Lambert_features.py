# ---------------------------------------------------------
# Lambert Projection with Map Features
# ---------------------------------------------------------
# This program plots January 2026 2-m air temperature
# anomalies over the contiguous United States.
#
# The purpose of this exercise is to improve regional
# climate-map readability by adding common Cartopy map
# features such as coastlines, borders, states, lakes,
# rivers, land/ocean shading, and gridlines.
#
# Students can modify:
#   1. map features added with ax.add_feature()
#   2. gridline settings
#   3. color range using clevs
# ---------------------------------------------------------

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pathlib import Path

import warnings
warnings.filterwarnings(
    "ignore",
    message="invalid value encountered in create_collection",
    category=RuntimeWarning
)

# ---------------------------------------------------------
# Read local NetCDF file
# ---------------------------------------------------------
script_dir = Path(__file__).resolve().parent

# Check whether the script is inside the "solution" directory
if script_dir.name == "solution":
    repo_dir = script_dir.parents[2]
else:
    repo_dir = script_dir.parents[1]

air_file = repo_dir / "data/air.2m.mon.mean.nc"
ds = xr.open_dataset(air_file)

print(ds)
print(ds.time[-1].values)

# ---------------------------------------------------------
# Calculate January 2026 air temperature anomaly
# ---------------------------------------------------------
air = ds["air"].load()

# Convert K to degC
air_c = air - 273.15

# January climatology: 1991-2020
ref = air_c.sel(time=slice("1991-01-01", "2020-12-31"))
jan_clim = ref.groupby("time.month").mean("time").sel(month=1)

# January 2026 anomaly
jan_2026 = air_c.sel(time="2026-01-01").squeeze()
anom = jan_2026 - jan_clim

print(anom.min().values)
print(anom.max().values)

# ---------------------------------------------------------
# Create figure and map projection
# ---------------------------------------------------------
fig = plt.figure(figsize=(10, 6))

ax = plt.axes(
    projection=ccrs.LambertConformal(
        central_longitude=-96,
        central_latitude=39
    )
)

# Focus on the contiguous United States
ax.set_extent(
    [-125, -66.5, 24, 50],
    crs=ccrs.PlateCarree()
)

# ---------------------------------------------------------
# Add background map features
# ---------------------------------------------------------
# These features provide geographic context for interpreting
# regional climate anomalies.

ax.add_feature(cfeature.LAND, facecolor="lightgray", zorder=0)
ax.add_feature(cfeature.OCEAN, facecolor="white", zorder=0)
ax.add_feature(cfeature.LAKES, facecolor="white", edgecolor="gray", linewidth=0.4)
ax.add_feature(cfeature.RIVERS, edgecolor="gray", linewidth=0.4)

# Political and coastline boundaries
ax.coastlines(linewidth=0.7)
ax.add_feature(cfeature.BORDERS, linewidth=0.5)
ax.add_feature(cfeature.STATES, linewidth=0.3)

# ---------------------------------------------------------
# Plot air temperature anomaly
# ---------------------------------------------------------
# Use a diverging color map because anomalies have both
# negative and positive values relative to climatology.

clevs = np.arange(-10, 10.1, 1)

p = anom.plot(
    ax=ax,
    transform=ccrs.PlateCarree(),
    cmap="RdBu_r",
    levels=clevs,
    extend="both",
    cbar_kwargs={"label": "2-m Air Temperature Anomaly (degC)"}
)

# ---------------------------------------------------------
# Add latitude-longitude gridlines
# ---------------------------------------------------------
# Gridlines help users connect the regional map to geographic
# coordinates. Labels are kept only on the left and bottom to
# avoid crowding the figure.

gl = ax.gridlines(
    crs=ccrs.PlateCarree(),
    draw_labels=True,
    linewidth=0.4,
    color="gray",
    alpha=0.6,
    linestyle="--"
)

gl.top_labels = False
gl.right_labels = False
gl.xlabel_style = {"size": 8}
gl.ylabel_style = {"size": 8}

ax.set_title(
    "January 2026 Air Temperature Anomaly\n"
    "Lambert Conformal Projection with Map Features"
)

output_path = Path(__file__).with_suffix(".jpg")
plt.savefig(output_path, dpi=300, bbox_inches="tight")
plt.show()
