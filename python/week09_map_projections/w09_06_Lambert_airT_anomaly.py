# ---------------------------------------------------------
# Lambert Projection for Regional Climate Analysis
# ---------------------------------------------------------
# This program visualizes regional air temperature anomalies
# using NOAA NCEP/NCAR Reanalysis data and Cartopy.
#
# Lambert Conformal projection is commonly used for
# mid-latitude regional analysis because it preserves shape
# reasonably well over limited areas.
#
# In this example, the map is centered over North America.
# ---------------------------------------------------------

import xarray as xr
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

# NOAA PSL OPeNDAP URL
#air_url = (
#    "https://psl.noaa.gov/thredds/dodsC/"
#    "Datasets/ncep.reanalysis.derived/surface/air.mon.mean.nc"
#)
#ds = xr.open_dataset(air_url)

# NOAA PSL local NetCDF file
indir = Path("../../data")
air_file = indir / "air.2m.mon.mean.nc"
ds = xr.open_dataset(air_file)

print(ds)
print(ds.time[-1].values)

# Select air temperature
air = ds["air"].load()

# Convert K to °C
air_c = air - 273.15

# January climatology (1991–2020)
ref = air_c.sel(time=slice("1991-01-01", "2020-12-31"))
jan_clim = ref.groupby("time.month").mean("time").sel(month=1)

# January 2026 anomaly
jan_2026 = air_c.sel(time="2026-01-01").squeeze()
anom = jan_2026 - jan_clim

print(anom.min().values)
print(anom.max().values)

# Create figure
fig = plt.figure(figsize=(10, 6))

#
# Use Lambert Conformal projection
#
ax = plt.axes(
    projection=ccrs.LambertConformal(
        central_longitude=-100,
        central_latitude=45
    )
)

anom.plot(
    ax=ax,
    transform=ccrs.PlateCarree(),
    cmap="RdBu_r",
    levels=21,
    cbar_kwargs={"label": "2-m Air Temperature Anomaly (°C)"}
)

# Focus on North America
ax.set_extent(
    [-150, -50, 15, 75],
    crs=ccrs.PlateCarree()
)

ax.coastlines()
ax.add_feature(cfeature.BORDERS, linewidth=0.5)
ax.add_feature(cfeature.STATES, linewidth=0.3)

ax.set_title("January 2026 Air Temperature Anomaly (Lambert Projection)")

output_path = Path(__file__).with_suffix(".jpg")
plt.savefig(output_path, dpi=300)
plt.show()
