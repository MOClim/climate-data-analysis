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

def calc_seasonal_anom(dat, window=5, end_month=1):
    """
    Calculate seasonal mean anomaly using a trailing running mean, extract the final month (e.g., Mar for NDJFM),
    convert to year-lat-lon DataArray, apply minimum coverage mask, and optionally remove trend.

    Parameters:
    -----------
    dat : xr.DataArray
        Input data with dimensions (time, lat, lon) and datetime64 'time'.
    window : int
        Running mean window size (default is 5).
    end_month : int
        Target month used to extract seasonal means (final month of the trailing average).
    min_coverage : float
        Minimum fraction of year coverage required for masking (default 0.9).
    dtrend : bool
        If True, remove linear trend after applying coverage mask.

    Returns:
    --------
    dat_out : xr.DataArray
        Seasonal mean anomaly with dimensions (year, lat, lon).
    """

    # Compute monthly anomalies
    clm = dat.groupby("time.month").mean(dim="time")
    anm = dat.groupby("time.month") - clm

    # Apply trailing running mean
    dat_rm = anm.rolling(time=window, center=False, min_periods=window).mean()

    # Filter for entries where month == end_month
    dat_tmp = dat_rm.sel(time=dat_rm["time"].dt.month == end_month)

    # Extract year from the end_month timestamps
    years = dat_tmp["time"].dt.year

    # Create clean DataArray with dimensions ['year', 'lat', 'lon']
    datS = xr.DataArray(
        data=dat_tmp.values,
        dims=["year", "lat", "lon"],
        coords={
            "year": years.values,
            "lat": dat_tmp["lat"].values,
            "lon": dat_tmp["lon"].values,
        },
        name=dat.name if hasattr(dat, "name") else "SeasonalMean",
        attrs=dat.attrs.copy(),
    )

    return datS

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
# Calculate annual-mean anomalies using running mean
# ---------------------------------------------------------

air_an_anm = calc_seasonal_anom(air, window=12, end_month=12)


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

reg_an_anm = regional_weighted_mean(air_an_anm, lat_str, lat_end, lon_str, lon_end)
print(reg_an_anm.sizes)

# -----------------------------
# Plot
# -----------------------------
plt.figure(figsize=(10, 4))
plt.plot(reg_an_anm.year, reg_an_anm, color="black", linewidth=1.5)
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

