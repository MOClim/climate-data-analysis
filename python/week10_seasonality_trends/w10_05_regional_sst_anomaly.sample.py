# ---------------------------------------------------------
# Regional Monthly and Annual Mean Anomalies
# ---------------------------------------------------------
# Purpose:
#   Compare monthly anomalies with annual mean anomalies for
#   regional SST.
#
# Directions:
#   Step 1: Read ../../data_raw/HadISST_sst.nc and extract
#           the SST variable ("sst").
#
#   Step 2: Calculate monthly SST anomalies relative to the
#           1991–2020 monthly climatology by calling the
#           monthly_clm_anom() function.
#
#   Step 3: Calculate annual mean anomalies by averaging the
#           monthly anomalies for each year by using
#           calc_seasonal_mean()
# ---------------------------------------------------------

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.ticker import MultipleLocator


# ---------------------------------------------------------
# Functions
# ---------------------------------------------------------
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
    # Rename coordinates if necessary
    if "latitude" in data.coords:
      data = data.rename({"latitude": "lat"})

    if "longitude" in data.coords:
      data = data.rename({"longitude": "lon"})

    # --- Longitude adjustment ---
    target_lon_range = "neg180_180" if lon1 < 0 or lon2 < 0 else "0_360"

    if target_lon_range == "neg180_180" and (data.lon > 180).any():
        data = data.assign_coords(
            lon=((data.lon + 180) % 360 - 180)
        ).sortby("lon")
    elif target_lon_range == "0_360" and (data.lon < 0).any():
        data = data.assign_coords(
            lon=(data.lon % 360)
        ).sortby("lon")

    # --- Select region ---
    dat_region = data.sel(lat=slice(lat1, lat2), lon=slice(lon1, lon2))

    # --- Apply cosine-latitude weighting ---
    weights = np.cos(np.deg2rad(dat_region["lat"]))
    dat_region_mean = dat_region.weighted(weights).mean(
        dim=["lat", "lon"],
        skipna=True
    )

    dat_region_mean.name = f"regional_mean_{lat1}_{lat2}_{lon1}_{lon2}"

    return dat_region_mean

def calc_seasonal_anom(dat, window=5, end_month=1, clim_period=None):
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

    # Monthly climatology
    if clim_period is None:
        clm = dat.groupby("time.month").mean("time")
    else:
        start, end = clim_period
        clm = (
            dat.sel(time=slice(start, end))
            .groupby("time.month")
            .mean("time")
        )

    # Monthly anomalies
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


def monthly_clm_anom(dat, clim_period=None):
    """
    Calculate monthly anomalies relative to monthly climatology.

    This removes the climatological seasonal cycle.
    """

    # Monthly climatology
    if clim_period is None:
        clm = dat.groupby("time.month").mean("time")
    else:
        start, end = clim_period
        clm = (
            dat.sel(time=slice(start, end))
            .groupby("time.month")
            .mean("time")
        )

    anom = dat.groupby("time.month") - clm

    return anom


# ---------------------------------------------------------
# Step 1: Read the HadISST dataset and extract the SST variable.
#
# File:
#   ../../data_raw/HadISST_sst.nc
#
# Hint:
#   1. Open the NetCDF file.
#   2. Extract the data variable named "sst".
#
#   ncdump -h ../../data_raw/HadISST_sst.nc
# ---------------------------------------------------------

sst =

print(sst.dims)

# Rename coordinates if necessary
if "latitude" in sst.coords:
   sst = sst.rename({"latitude": "lat"})

if "longitude" in sst.coords:
   sst = sst.rename({"longitude": "lon"})

# ---------------------------------------------------------
# Calculate monthly and annual mean anomalies
# ---------------------------------------------------------
clim_start = "1991-01-01"
clim_end = "2020-12-31"

# Step 2: Calculate monthly SST anomalies relative to the
# 1991–2020 monthly climatology by calling
# monthly_climatology_anomaly().

sst_mon_anom = monthly_clm_anom()

# Step 3: Calculate annual mean anomalies from the monthly
# anomalies.
#

sst_anom = calc_seasonal_anom()

# ---------------------------------------------------------
# Calculate regional area-weighted means
# ---------------------------------------------------------
# Approximate North America box
lat_str, lat_end = 60, 0
lon_str, lon_end = -80, 0   # -180-180 longitude

sst_anom_NA = regional_weighted_mean(sst_anom, lat_str, lat_end, lon_str, lon_end)
sst_mon_anom_NA = regional_weighted_mean(sst_mon_anom, lat_str, lat_end, lon_str, lon_end)

# Convert year coordinates to datetime for plotting
sst_time = np.array([np.datetime64(f"{y}-01-01") for y in sst_anom_NA.year.values])

# ---------------------------------------------------------
# Plot one panels
# ---------------------------------------------------------
fig, axes = plt.subplots(
    1, 1,
    figsize=(11, 7),
    sharex=True
)

# ---------------------------------------------------------
# Temperature monthly and annual mean anomaly
# ---------------------------------------------------------
axes.plot(
    sst_mon_anom_NA.time,
    sst_mon_anom_NA,
    linewidth=0.7,
    color="gray",
    alpha=0.7,
    label="Monthly anomaly"
)
axes.plot(
    sst_time,
    sst_anom_NA,
    linewidth=2.0,
    color="black",
    label="Annual mean anomaly"
)
axes.axhline(0, color="gray", linewidth=0.8)
axes.set_ylabel("SST anomaly (degC)")
axes.set_title(
    "North Atlantic SST Anomaly",
    loc="left"
)
axes.yaxis.set_minor_locator(MultipleLocator(0.5))
axes.legend(loc="upper left", frameon=False)
axes.grid(which="major", linestyle="-", alpha=0.6)
axes.grid(which="minor", linestyle="--", alpha=0.3)


# ---------------------------------------------------------
# Common axis settings
# ---------------------------------------------------------
axes.set_xlim(np.datetime64("1948-01-01"), np.datetime64("2025-12-31"))

axes.set_ylim(-3, 3)

plt.suptitle(
    "North Atlantic Monthly and Annual Mean Anomalies\n"
    "Relative to 1991-2020 Monthly Climatology",
    fontsize=14
)
plt.tight_layout()

output_path = Path(__file__).with_suffix(".jpg")
plt.savefig(output_path, dpi=300, bbox_inches="tight")

plt.show()

