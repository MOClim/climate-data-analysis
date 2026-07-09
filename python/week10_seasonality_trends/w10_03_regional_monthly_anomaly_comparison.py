# ---------------------------------------------------------
# Regional Monthly Anomaly Comparison
# ---------------------------------------------------------
# This program compares two ways to calculate monthly anomalies
# for regional 2-m air temperature and precipitation.
#
# The program:
# 1. Reads monthly 2-m air temperature data.
# 2. Reads monthly precipitation rate data.
# 3. Converts units:
#      air   : K to degC
#      prate : kg m-2 s-1 to mm/day
# 4. Calculates regional area-weighted mean time series.
# 5. Calculates anomalies relative to the long-term mean.
# 6. Calculates anomalies relative to monthly climatology.
# 7. Plots both anomaly definitions for comparison.
#
# Concept:
#   Long-term mean anomaly = monthly value - long-term mean
#       -> the seasonal cycle remains.
#
#   Monthly climatology anomaly = monthly value - climatological
#                                 value for the same calendar month
#       -> the seasonal cycle is removed.
#
# Example:
#   January 2026 monthly climatology anomaly
#     = January 2026 value - mean January value during 1991-2020.
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


def long_term_mean_anomaly(monthly_mean, clim_start="1991-01-01", clim_end="2020-12-31"):
    """
    Calculate anomaly relative to one long-term mean.

    This removes only the long-term average value. The regular seasonal cycle
    remains in the anomaly time series.
    """

    clim_mean = monthly_mean.sel(time=slice(clim_start, clim_end)).mean("time")
    anom_mean = monthly_mean - clim_mean

    return anom_mean

def monthly_climatology_anomaly(monthly_mean, clim_start="1991-01-01", clim_end="2020-12-31"):
    """
    Calculate monthly anomalies relative to monthly climatology.

    This removes the climatological seasonal cycle.
    """

    clim = monthly_mean.sel(time=slice(clim_start,clim_end)
       ).groupby("time.month").mean("time")
    anom = monthly_mean.groupby("time.month") - clim

    return anom


# ---------------------------------------------------------
# Read data
# ---------------------------------------------------------
indir = Path("../../data")
indir2 = Path("../../data_raw")

air_file = indir / "air.2m.mon.mean.nc"
pr_file = indir2 / "prate.mon.mean.nc"

ds_air = xr.open_dataset(air_file)
ds_pr = xr.open_dataset(pr_file)

air = ds_air["air"]
prate = ds_pr["prate"]


# ---------------------------------------------------------
# Unit conversion
# ---------------------------------------------------------
# Temperature: K to degC
air = air - 273.15
air.attrs["units"] = "degC"

# Precipitation rate: kg m-2 s-1 to mm/day
prate = prate * 86400
prate.attrs["units"] = "mm/day"


# ---------------------------------------------------------
# Calculate regional area-weighted means
# ---------------------------------------------------------
# Approximate North America box
lat_str, lat_end = 75, 15
lon_str, lon_end = 190, 300   # 0-360 longitude: 190E=170W, 300E=60W

air_NA = regional_weighted_mean(air, lat_str, lat_end, lon_str, lon_end)
pr_NA = regional_weighted_mean(prate, lat_str, lat_end, lon_str, lon_end)


# ---------------------------------------------------------
# Calculate anomalies
# ---------------------------------------------------------
clim_start = "1991-01-01"
clim_end = "2020-12-31"

# Anomaly relative to one long-term mean
air_anom_mean = long_term_mean_anomaly(air_NA, clim_start, clim_end)
pr_anom_mean = long_term_mean_anomaly(pr_NA, clim_start, clim_end)

# Anomaly relative to monthly climatology
air_anom_monthly = monthly_climatology_anomaly(air_NA, clim_start, clim_end)
pr_anom_monthly = monthly_climatology_anomaly(pr_NA, clim_start, clim_end)


# ---------------------------------------------------------
# Plot four panels
# ---------------------------------------------------------
fig, axes = plt.subplots(
    2, 2,
    figsize=(13, 7),
    sharex=True
)

# ---------------------------------------------------------
# Panel 1: Temperature anomaly relative to long-term mean
# ---------------------------------------------------------
axes[0, 0].plot(
    air_anom_mean.time,
    air_anom_mean,
    linewidth=0.8,
    color="black"
)
axes[0, 0].axhline(0, color="gray", linewidth=0.8)
axes[0, 0].set_ylabel("Temperature anomaly (degC)")
axes[0, 0].set_title(
    "(a) Temperature anomaly relative to long-term mean\n"
    "Seasonal cycle remains",
    loc="left"
)
axes[0, 0].yaxis.set_minor_locator(MultipleLocator(2))
axes[0, 0].grid(which="major", linestyle="-", alpha=0.6)
axes[0, 0].grid(which="minor", linestyle="--", alpha=0.3)


# ---------------------------------------------------------
# Panel 2: Temperature anomaly relative to monthly climatology
# ---------------------------------------------------------
axes[0, 1].plot(
    air_anom_monthly.time,
    air_anom_monthly,
    linewidth=0.8,
    color="black"
)
axes[0, 1].axhline(0, color="gray", linewidth=0.8)
axes[0, 1].set_title(
    "(b) Temperature anomaly relative to monthly climatology\n"
    "Seasonal cycle removed",
    loc="left"
)
axes[0, 1].yaxis.set_minor_locator(MultipleLocator(0.5))
axes[0, 1].grid(which="major", linestyle="-", alpha=0.6)
axes[0, 1].grid(which="minor", linestyle="--", alpha=0.3)


# ---------------------------------------------------------
# Panel 3: Precipitation anomaly relative to long-term mean
# ---------------------------------------------------------
axes[1, 0].plot(
    pr_anom_mean.time,
    pr_anom_mean,
    linewidth=0.8,
    color="black"
)
axes[1, 0].axhline(0, color="gray", linewidth=0.8)
axes[1, 0].set_ylabel("Precipitation anomaly (mm/day)")
axes[1, 0].set_xlabel("Year")
axes[1, 0].set_title(
    "(c) Precipitation anomaly relative to long-term mean\n"
    "Seasonal cycle remains",
    loc="left"
)
axes[1, 0].yaxis.set_minor_locator(MultipleLocator(0.2))
axes[1, 0].grid(which="major", linestyle="-", alpha=0.6)
axes[1, 0].grid(which="minor", linestyle="--", alpha=0.3)


# ---------------------------------------------------------
# Panel 4: Precipitation anomaly relative to monthly climatology
# ---------------------------------------------------------
axes[1, 1].plot(
    pr_anom_monthly.time,
    pr_anom_monthly,
    linewidth=0.8,
    color="black"
)
axes[1, 1].axhline(0, color="gray", linewidth=0.8)
axes[1, 1].set_xlabel("Year")
axes[1, 1].set_title(
    "(d) Precipitation anomaly relative to monthly climatology\n"
    "Seasonal cycle removed",
    loc="left"
)
axes[1, 1].yaxis.set_minor_locator(MultipleLocator(0.1))
axes[1, 1].grid(which="major", linestyle="-", alpha=0.6)
axes[1, 1].grid(which="minor", linestyle="--", alpha=0.3)


# ---------------------------------------------------------
# Common axis settings
# ---------------------------------------------------------
for ax in axes.ravel():
    ax.set_xlim(np.datetime64("1948-01-01"), np.datetime64("2025-12-31"))

# Use separate y-axis ranges because the long-term mean anomaly includes
# the seasonal cycle and therefore has much larger amplitude.
axes[0, 0].set_ylim(-18, 18)
axes[0, 1].set_ylim(-3, 3)
axes[1, 0].set_ylim(-1.5, 1.5)
axes[1, 1].set_ylim(-0.7, 0.7)

plt.suptitle(
    "North America Monthly Anomaly Comparison\n"
    "Long-term Mean Removed vs. Monthly Climatology Removed",
    fontsize=14
)
plt.tight_layout()

output_path = Path(__file__).with_suffix(".jpg")
plt.savefig(output_path, dpi=300, bbox_inches="tight")

plt.show()

ds_air.close()
ds_pr.close()
