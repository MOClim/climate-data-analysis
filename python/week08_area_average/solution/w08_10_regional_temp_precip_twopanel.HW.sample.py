# ---------------------------------------------------------
# Global Mean Temperature and Precipitation Time Series
# ---------------------------------------------------------
# Exercise:
# 1. Read global monthly 2-m air temperature data.
# 2. Read global monthly precipitation rate data.
# 3. Convert units:
#      air   : K to °C
#      prate : kg m-2 s-1 to mm/day
# 4. Calculate regional area-weighted mean time series.
# 5. Plot temperature and precipitation in two panels.
# ---------------------------------------------------------

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.ticker import MultipleLocator

def regional_weighted_mean(data, lat1, lat2, lon1, lon2):
    """
    Compute cosine-latitude-weighted regional mean over the specified lat-lon bounds.

    Parameters
    ----------
    data : xarray.DataArray
        Input data with dimensions (time, lat, lon).
    lat1, lat2 : float
        Latitude bounds.
    lon1, lon2 : float
        Longitude bounds (either in -180 to 180 or 0 to 360).

    Returns
    -------
    dat_region_mean : xarray.DataArray
        Regional mean time series (time).
    """
    # --- Longitude adjustment ---
    target_lon_range = 'neg180_180' if lon1 < 0 or lon2 < 0 else '0_360'
    if target_lon_range == 'neg180_180' and (data.lon > 180).any():
        data = data.assign_coords(lon=((data.lon + 180) % 360 - 180)).sortby('lon')
    elif target_lon_range == '0_360' and (data.lon < 0).any():
        data = data.assign_coords(lon=(data.lon % 360)).sortby('lon')

    # --- Select region ---
    dat_region = data.sel(lat=slice(lat1, lat2), lon=slice(lon1, lon2))

    # --- Apply cosine-latitude weighting ---
    weights = np.cos(np.deg2rad(dat_region['lat']))
    dat_region_mean = dat_region.weighted(weights).mean(dim=['lat', 'lon'], skipna=True)

    # --- Assign name ---
    dat_region_mean.name = f"regional_mean_{lat1}_{lat2}_{lon1}_{lon2}"

    return dat_region_mean


def global_weighted_mean(data):
    """Calculate cosine-latitude-weighted global mean."""

    weights = np.cos(np.deg2rad(data.lat))

    global_mean = data.weighted(weights).mean(
        dim=("lat", "lon"),
        skipna=True
    )

    return global_mean

def annual_anomaly(monthly_mean):
    """Calculate annual mean anomaly from monthly data."""

    clim = monthly_mean.groupby("time.month").mean("time")
    anom = monthly_mean.groupby("time.month") - clim

    anom_ann = anom.resample(time="YS").mean()
    count_ann = anom.resample(time="YS").count()

    anom_ann = anom_ann.where(count_ann == 12, drop=True)

    return anom_ann

# ---------------------------------------------------------
# Read data
# ---------------------------------------------------------
script_dir = Path(__file__).resolve().parent

# Check whether the script is inside the "solution" directory
if script_dir.name == "solution":
    # Move up two directory levels to reach the repository root
    repo_dir = script_dir.parents[2]
else:
    # Move up two directory levels to reach the repository root
    repo_dir = script_dir.parents[1]

air_file = repo_dir/ "data" / "air.2m.mon.mean.nc"
pr_file  = repo_dir / "data_raw" / "prate.mon.mean.nc"

ds_air = xr.open_dataset(air_file)
ds_pr = xr.open_dataset(pr_file)

air = ds_air["air"]
prate = ds_pr["prate"]


# ---------------------------------------------------------
# Unit conversion
# ---------------------------------------------------------

# Temperature: K to °C
air = air - 273.15
air.attrs["units"] = "°C"

# Precipitation rate: kg m-2 s-1 to mm/day
prate = prate * 86400
prate.attrs["units"] = "mm/day"


# ---------------------------------------------------------
# Calculate regional area-weighted means
# ---------------------------------------------------------
# Approximate North America box
lat_str, lat_end = 75, 15
lon_str, lon_end = 190, 300   # 0–360 longitude: 190E=170W, 300E=60W

air_NA = regional_weighted_mean(air, lat_str, lat_end, lon_str, lon_end)
pr_NA = regional_weighted_mean(prate, lat_str, lat_end, lon_str, lon_end)


# ---------------------------------------------------------
# Calculate annual anomalies
# ---------------------------------------------------------

air_anom_ann = annual_anomaly(air_NA)
pr_anom_ann = annual_anomaly(pr_NA)

# ---------------------------------------------------------
# Plot two panels
# ---------------------------------------------------------

fig, axes = plt.subplots(
    2, 1,
    figsize=(10, 6),
    sharex=True
)

# Panel 1: Temperature
axes[0].plot(
    air_anom_ann.time.dt.year,
    air_anom_ann,
    linewidth=1.5,
    color="black"
)

axes[0].axhline(0, color="gray", linewidth=0.8)
axes[0].set_ylabel("Temperature anomaly (°C)")
axes[0].set_title("(a) North America Mean 2-m Air Temperature Anomaly", loc="left")
axes[0].yaxis.set_minor_locator(MultipleLocator(0.1))
axes[0].grid(which="major", linestyle="-", alpha=0.6)
axes[0].grid(which="minor", linestyle="--", alpha=0.3)


# Panel 2: Precipitation
axes[1].plot(
    pr_anom_ann.time.dt.year,
    pr_anom_ann,
    linewidth=1.5,
    color="black"
)

axes[1].axhline(0, color="gray", linewidth=0.8)
axes[1].set_ylabel("Precipitation anomaly (mm/day)")
axes[1].set_xlabel("Year")
axes[1].set_title("(b) North America Mean Precipitation Rate Anomaly", loc="left")
axes[1].yaxis.set_minor_locator(MultipleLocator(0.01))
axes[1].grid(which="major", linestyle="-", alpha=0.6)
axes[1].grid(which="minor", linestyle="--", alpha=0.3)


# X-axis setting
axes[1].set_xlim(1948, 2025)
axes[1].set_xticks(np.arange(1950, 2030, 10))

plt.suptitle("Global Mean Temperature and Precipitation Anomalies")
plt.tight_layout()

output_path = Path(__file__).with_suffix(".jpg")
plt.savefig(output_path, dpi=300)

plt.show()

ds_air.close()
ds_pr.close()
