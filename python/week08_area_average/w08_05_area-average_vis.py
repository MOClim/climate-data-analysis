# ---------------------------------------------------------
# North America Area-Averaged Temperature Anomaly
# ---------------------------------------------------------
# This program reads NOAA NCEP/NCAR Reanalysis monthly
# 2-m air temperature data and calculates an area-weighted
# average temperature anomaly over North America.
#
# Students can:
#   - Change the analysis region
#   - Calculate climatology and anomalies
#   - Compare different geographic regions
#   - Investigate long-term climate variability
#
# Data source:
# NOAA Physical Sciences Laboratory (PSL)
# NCEP/NCAR Reanalysis Project
# https://psl.noaa.gov/data/gridded/data.ncep.reanalysis.html
#
# Dataset:
# air.2m.mon.mean.nc
#
# Reference:
# Kalnay et al. (1996), The NCEP/NCAR 40-Year Reanalysis
# Project, Bulletin of the American Meteorological Society.
# ---------------------------------------------------------

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys
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

def calculate_annual_anomaly(regional_mean):
    """
    Calculate monthly anomalies and annual mean anomalies.
    """

    # Monthly climatology
    clim = regional_mean.groupby("time.month").mean("time")

    # Monthly anomaly
    anom = regional_mean.groupby("time.month") - clim

    # Annual mean anomaly
    anom_ann = anom.resample(time="YS").mean()

    return anom_ann

# -----------------------------
# User settings
# -----------------------------
indir = filename = Path('../../data/')
filein = indir / "air.2m.mon.mean.nc"


# -----------------------------
# Load data
# -----------------------------
ds = xr.open_dataset(filein)
print(ds)

# Common variable name in NCEP/NCAR air.2m file

# The latest year may contain only a few months of data.
# Exclude the final two records to ensure that only complete
# months are used in the annual-average calculation.

air = ds["air"][:-2]
print(air)

# -----------------------------
# Convert K to degC 
# -----------------------------
air = air - 273.15
air.attrs["units"] = "degC"

# ---------------------------------------------------------
# Area-weighted mean
# ---------------------------------------------------------
# Grid cells become smaller toward the poles.
# Cosine(latitude) weighting accounts for the
# changing area represented by each grid cell.
# ---------------------------------------------------------
# Approximate North America box
lat_str, lat_end = 75, 15
lon_str, lon_end = 190, 300   # 0–360 longitude: 190E=170W, 300E=60W

air_na_mean = regional_weighted_mean(air, lat_str, lat_end, lon_str, lon_end)

# Annual mean anomaly
air_na_ann = calculate_annual_anomaly(air_na_mean)

# -----------------------------
# Plot
# -----------------------------
plt.figure(figsize=(10, 4))
plt.plot(air_na_ann.time.dt.year, air_na_ann, color="black", linewidth=1.5)
plt.axhline(0, color='gray', linestyle="-")


plt.xlabel("Year")
plt.ylabel("2-m air temperature anomaly (°C)")
plt.title("North America area-averaged 2-m air temperature anomaly")
plt.grid(alpha=0.3)
plt.tight_layout()

# Major ticks
plt.xticks(np.arange(1950, 2025, 10))
plt.yticks(np.arange(-1, 1, 0.2))

# Minor ticks
plt.gca().xaxis.set_minor_locator(MultipleLocator(1))
plt.gca().yaxis.set_minor_locator(MultipleLocator(0.2))

# Grid
plt.grid(which='major', linestyle='-', linewidth=0.7, alpha=0.7)
plt.grid(which='minor', linestyle='--', linewidth=0.4, alpha=0.5)


# Save the plot as a JPEG file
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)

# Show the plot
plt.show()

