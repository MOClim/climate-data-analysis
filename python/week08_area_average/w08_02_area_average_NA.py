# ---------------------------------------------------------
# North America Area-Averaged Temperature Anomaly
# ---------------------------------------------------------
# This program reads monthly NOAA NCEP/NCAR Reanalysis
# 2-m air temperature data and calculates annual temperature
# anomalies over North America.
#
# The program:
#   - Calculates monthly temperature anomalies
#   - Calculates annual means using two methods:
#       1. A 12-month trailing running mean
#       2. Calendar-year resampling
#   - Computes a cosine-latitude-weighted regional mean
#   - Compares the resulting annual anomaly time series
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

def calc_resample_mean(dat, freq):
    """
    Calculate calendar-year mean using resampling.

    Parameters
    ----------
    dat : xarray.DataArray
        Monthly data with a datetime64 time coordinate. The expected
        dimensions are time, latitude, and longitude.

    Returns
    -------
    dat_out : xarray.DataArray
        Annual mean with dimensions year, latitude,
        and longitude. The year coordinate contains year-end
        datetime values.
    """

    # Rename coordinates if necessary
    if "latitude" in dat.coords:
      dat = dat.rename({"latitude": "lat"})

    if "longitude" in dat.coords:
      dat = dat.rename({"longitude": "lon"})

    # Calculate calendar-year mean anomalies
    dat_rm = dat.resample(time=freq).mean()

    # Rename the temporal dimension
    dat_rm = dat_rm.rename({"time": "year"})

    return dat_rm

def calc_seasonal_mean(dat, window=5, end_month=1):
    """
    Calculate seasonal mean using a trailing running mean, extract the final month (e.g., Mar for NDJFM),
    convert to year-lat-lon DataArray.

    Parameters:
    -----------
    dat : xr.DataArray
        Input data with dimensions (time, lat, lon) and datetime64 'time'.
    window : int
        Running mean window size (default is 5).
    end_month : int
        Target month used to extract seasonal means (final month of the trailing average).

    Returns:
    --------
    dat_out : xr.DataArray
        Seasonal mean with dimensions (year, lat, lon).
    """

    # Rename coordinates if necessary
    if "latitude" in dat.coords:
      dat = dat.rename({"latitude": "lat"})

    if "longitude" in dat.coords:
      dat = dat.rename({"longitude": "lon"})

    # Apply trailing running mean
    dat_rm = dat.rolling(time=window, center=False, min_periods=window).mean()

    # Filter for entries where month == end_month
    dat_tmp = dat_rm.sel(time=dat_rm["time"].dt.month == end_month)

    # Extract year from the end_month timestamps
    years = dat_tmp["time"].dt.year

    # Create clean DataArray with dimensions ['year', 'lat', 'lon']
    dat_out = xr.DataArray(
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

    return dat_out



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
# Calculate annual-mean temperature 
# ---------------------------------------------------------

# Method 1: 12-month trailing running mean
#
# This method is flexible because the averaging window and
# ending month can be changed. It can therefore calculate
# calendar-year, seasonal, or water-year means.
air_ann = calc_seasonal_mean(air, window=12, end_month=12)

# Method 2: Calendar-year resampling
#
# This method provides a concise way to aggregate monthly
# data into calendar-year means. Other annual periods can
# also be calculated by changing the resampling frequency.
air_ann_rsm = calc_resample_mean(air,"YE")

print("Annual means calculated using the running-mean method:")
print(air_ann.sizes)
print()
print("Annual means calculated using the resampling method:")
print(air_ann_rsm.sizes)

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

air_na_ann = regional_weighted_mean(air_ann, lat_str, lat_end, lon_str, lon_end)
print(air_na_ann.coords)
air_na_ann_rsm = regional_weighted_mean(air_ann_rsm, lat_str, lat_end, lon_str, lon_end)

# -----------------------------
# Plot
# -----------------------------
fig, axes = plt.subplots(
    nrows=2,
    ncols=1,
    figsize=(10, 7),
)

# Panel 1: 12-month trailing running mean
axes[0].plot(
    air_na_ann.year,
    air_na_ann,
    color="black",
    linewidth=1.5,
)

#axes[0].axhline(
#    y=0,
#    color="gray",
#    linestyle="--",
#    linewidth=1.0,
#)

axes[0].set_title(
    "Annual mean from a 12-month trailing running mean"
)
axes[0].set_ylabel("Air Temperature (°C)")
axes[0].grid(alpha=0.3)

# Panel 2: Calendar-year resampling
axes[1].plot(
    air_na_ann_rsm.year,
    air_na_ann_rsm,
    color="black",
    linewidth=1.5,
)

axes[1].set_title(
    "Annual mean from calendar-year resampling"
)
axes[1].set_xlabel("Year")
axes[1].set_ylabel("Air Temperature (°C)")
axes[1].grid(alpha=0.3)

fig.suptitle(
    "North America area-averaged 2-m air temperature",
    fontsize=14,
)

plt.tight_layout()

# Save the plot as a JPEG file
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)

# Show the plot
plt.show()

