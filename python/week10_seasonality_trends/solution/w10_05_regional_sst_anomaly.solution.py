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
#           monthly_climatology_anomaly() function.
#
#   Step 3: Calculate annual mean anomalies by averaging the
#           monthly anomalies for each year. Use
#           resample(time="YE").mean() and keep only complete
#           years with 12 monthly values.
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


def monthly_climatology_anomaly(monthly_mean, clim_start="1991-01-01", clim_end="2020-12-31"):
    """
    Calculate monthly anomalies relative to monthly climatology.

    This removes the climatological seasonal cycle.
    """

    clim = monthly_mean.sel(time=slice(clim_start, clim_end)).groupby(
        "time.month"
    ).mean("time")

#    clim = monthly_climatology(monthly_mean, clim_start, clim_end)
    anom = monthly_mean.groupby("time.month") - clim

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
script_dir = Path(__file__).resolve().parent

# Check whether the script is inside the "solution" directory
if script_dir.name == "solution":
    # Move up two directory levels to reach the repository root
    repo_dir = script_dir.parents[2]
else:
    # Move up two directory levels to reach the repository root
    repo_dir = script_dir.parents[1]

sst_file = repo_dir / "data_raw" / "HadISST_sst.nc"

ds_sst = xr.open_dataset(sst_file)

sst = ds_sst["sst"]

# ---------------------------------------------------------
# Calculate regional area-weighted means
# ---------------------------------------------------------
# Approximate North America box
lat_str, lat_end = 60, 0
lon_str, lon_end = -80, 0   # -180-180 longitude

sst_NA = regional_weighted_mean(sst, lat_str, lat_end, lon_str, lon_end)


# ---------------------------------------------------------
# Calculate monthly and annual mean anomalies
# ---------------------------------------------------------
clim_start = "1991-01-01"
clim_end = "2020-12-31"

# Step 2: Calculate monthly SST anomalies relative to the
# 1991–2020 monthly climatology by calling
# monthly_climatology_anomaly().

sst_NA_anom_monthly = monthly_climatology_anomaly(sst_NA, clim_start, clim_end)

# Step 3: Calculate annual mean anomalies from the monthly
# anomalies.
#
# Hint:
#   • Average monthly anomalies within each year using
#     resample(time="YE").mean().
#   • Keep only complete years containing 12 monthly values.

sst_NA_anom_annual = sst_NA_anom_monthly.resample(time='YE').mean()

# ---------------------------------------------------------
# Plot one panel
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
    sst_NA_anom_monthly.time,
    sst_NA_anom_monthly,
    linewidth=0.7,
    color="gray",
    alpha=0.7,
    label="Monthly anomaly"
)
axes.plot(
    sst_NA_anom_annual.time,
    sst_NA_anom_annual,
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

