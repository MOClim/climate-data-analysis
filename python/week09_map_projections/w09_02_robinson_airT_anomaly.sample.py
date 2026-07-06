# ---------------------------------------------------------
# Robinson Projection for Global Climate Analysis
# ---------------------------------------------------------
# This program visualizes global air temperature anomalies
# using NOAA NCEP/NCAR Reanalysis data and Cartopy.
#
# In this exercise, data are read directly from an online
# OPeNDAP URL instead of a downloaded NetCDF file.
#
# OPeNDAP allows Python to access remote climate datasets
# without manual download.
#
# Note:
# cartopy.crs is imported as "ccrs" for convenience.
# ---------------------------------------------------------

import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pathlib import Path
import sys

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

# Plot
fig = plt.figure(figsize=(10, 5))

#
# Step 1: Choose the Robinson projection from the
# Cartopy projection list and complete the code below.
# https://scitools.org.uk/cartopy/docs/v0.15/crs/projections.html 
#
ax = plt.axes(projection=)

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
