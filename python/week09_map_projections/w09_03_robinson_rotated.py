# ---------------------------------------------------------
# Pacific-Centered Robinson Projection
# ---------------------------------------------------------
# This program visualizes global air temperature anomalies
# using NOAA NCEP/NCAR Reanalysis data and Cartopy.
#
# The Robinson projection provides a visually balanced view
# of the global climate field.
#
# Here, the map is centered near the Pacific Ocean using
# central_longitude=180, which is useful for ocean and
# climate variability analysis.
#
# A cyclic point is added to avoid a blank seam at the
# 0/360-degree longitude boundary.
# ---------------------------------------------------------

import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.util import add_cyclic_point
from pathlib import Path
import sys
import cartopy
import shapely
import matplotlib

import warnings
warnings.filterwarnings(
    "ignore",
    message="invalid value encountered in create_collection",
    category=RuntimeWarning
)

# Example NOAA PSL OPeNDAP URLs
air_url = "https://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis.derived/surface/air.mon.mean.nc"
prate_url = "https://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis.derived/surface/prate.sfc.mon.mean.nc"
sst_url = "https://psl.noaa.gov/thredds/dodsC/Datasets/COBE2/sst.mon.mean.nc"

ds = xr.open_dataset(air_url)
print(ds)
print(ds.time[-1].values)

# Select near-surface air temperature
air = ds["air"]

# Convert from K to degC if needed
air_c = air - 273.15

# Example: January climatology
jan_clim = air_c.sel(time=slice("1991-01-01", "2020-12-31")).where(
    air_c["time.month"] == 1, drop=True
).mean("time")

# Example: January 2026 anomaly
jan_2026 = air_c.sel(time="2026-01-01")
anom = jan_2026 - jan_clim

print(anom.min().values)
print(anom.max().values)

# Add cyclic point to close the 0/360 longitude seam
anom_cyclic, lon_cyclic = add_cyclic_point(anom.values, coord=anom.lon)

# Plot
fig = plt.figure(figsize=(10, 5))

#
# Pacific centered Projection 
#
# Plot
fig = plt.figure(figsize=(10, 5))

ax = plt.axes(projection=ccrs.Robinson(central_longitude=180.))

levels = range(-20, 22, 2)

cf = ax.contourf(
    lon_cyclic,
    anom.lat,
    anom_cyclic,
    levels=levels,
    cmap="RdBu_r",
    extend="both",
    transform=ccrs.PlateCarree()
)

plt.colorbar(
    cf,
    ax=ax,
    orientation="vertical",
    shrink=0.8,
    label="2-m Air Temperature Anomaly (°C)"
)

ax.coastlines()
ax.add_feature(cfeature.BORDERS, linewidth=0.5)
ax.set_global()
ax.set_title("January 2026 Air Temperature Anomaly")

output_path = Path(__file__).with_suffix(".jpg")
plt.savefig(output_path, dpi=300, bbox_inches="tight")
plt.show()

