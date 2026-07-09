# ---------------------------------------------------------
# Regional Detrended SST Anomalies
# ---------------------------------------------------------
#   Calculate annual mean SST anomalies, remove the long-term
#   linear trend, and compare the original and detrended
#   annual mean anomaly time series.
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

    clim = monthly_mean.sel(time=slice(clim_start, clim_end)
       ).groupby("time.month").mean("time")
    anom = monthly_mean.groupby("time.month") - clim

    return anom

def linear_trend(da):
    """
    Calculate a linear trend using least-squares regression.

    Parameters
    ----------
    da : xarray.DataArray
        Annual mean anomaly time series.

    Returns
    -------
    trend : xarray.DataArray
        Linear trend line.
    slope_decade : float
        Linear trend (degC per decade).
    """

    x = np.arange(da.sizes["time"])
    y = da.values

    slope, intercept = np.polyfit(x, y, 1)

    trend = xr.DataArray(
        slope * x + intercept,
        coords={"time": da.time},
        dims=["time"]
    )

    slope_decade = slope * 10

    return trend, slope_decade

def linear_detrend(da, trend_start="1981-01-01", trend_end="2020-12-31"):
    """
    Remove the full fitted linear trend from an annual anomaly time series.

    The fitted line is

        anomaly = slope * centered_year + intercept

    and the detrended anomaly is calculated as

        detrended anomaly = anomaly - fitted trend line

    This is the standard detrending method. After detrending, the mean value
    during the trend-analysis period is close to zero, and the long-term
    linear trend is removed.

    Parameters
    ----------
    da : xarray.DataArray
        Annual anomaly time series with dimension time.
    trend_start, trend_end : str
        Period used to estimate the linear trend.

   Returns
    -------
    da_detrended : xarray.DataArray
        Anomaly with the full fitted linear trend removed.
    trend_line : xarray.DataArray
        Fitted linear trend line evaluated at all years.
    slope_decade : float
        Linear trend in degC per decade.
    """

    # Select the period used for trend estimation
    da_fit = da.sel(time=slice(trend_start, trend_end))

    # Convert time to numeric year values
    year_fit = da_fit.time.dt.year
    year_all = da.time.dt.year

    # Center the year coordinate using the trend-analysis period
    # This improves numerical stability and makes the intercept equal to
    # the fitted value near the middle of the trend period.
    year_mean = float(year_fit.mean())
    x_fit = year_fit - year_mean
    x_all = year_all - year_mean

    # Fit linear trend: anomaly = slope * centered_year + intercept
    slope, intercept = np.polyfit(x_fit.values, da_fit.values, deg=1)

    # Fitted linear trend line for all years
    trend_line = xr.DataArray(
        slope * x_all + intercept,
        dims="time",
        coords={"time": da.time},
        name="linear_trend"
    )

    # Remove the full fitted trend line: slope component + intercept
    da_detrended = da - trend_line
    da_detrended.name = "detrended_anomaly"

    # Convert trend unit to degC per decade
    slope_decade = slope * 10.0

    return da_detrended, trend_line, slope_decade

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
trend_start = "1949-01-01"
trend_end = "2020-12-31"

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


# Calculate a linear trend of annual-mean anomaly
# Ignore the second returned value
sst_NA_trend, __ = linear_trend(sst_NA_anom_annual)

# Detrended annual anomaly
sst_NA_detrended, trend_line, slope_decade = linear_detrend(
        sst_NA_anom_annual,
        trend_start,
        trend_end
    )

# ---------------------------------------------------------
# Plot two panels
# 1: monthly anomalies, annual mean anomalies, and the linear trend
# 2: detrended annual mean anomalies
# ---------------------------------------------------------

fig, axes = plt.subplots(
    1, 2,
    figsize=(11, 4),
    sharex=True
)

# ---------------------------------------------------------
# Panel 1: Temperature annual mean anomaly with the linear trend
# ---------------------------------------------------------
axes[0].plot(
    sst_NA_anom_annual.time,
    sst_NA_anom_annual,
    linewidth=2.0,
    color="black",
    label="Annual mean anomaly"
)
# Overlay a linear trend 
axes[0].plot(
    sst_NA_trend.time,
    sst_NA_trend,
    color="red",
    linewidth=2.5,
    label=f"Trend = {slope_decade:.2f} degC/decade"
)

axes[0].axhline(0, color="gray", linewidth=0.8)
axes[0].set_ylabel("SST anomaly (degC)")
axes[0].set_title(
    "North Atlantic SST Anomaly",
    loc="left"
)
axes[0].yaxis.set_minor_locator(MultipleLocator(0.5))
axes[0].legend(loc="upper left", frameon=False)
axes[0].grid(which="major", linestyle="-", alpha=0.6)
axes[0].grid(which="minor", linestyle="--", alpha=0.3)

# ---------------------------------------------------------
# Panel 2: Detrended annual anomaly
# ---------------------------------------------------------

axes[1].plot(
    sst_NA_detrended.time,
    sst_NA_detrended,
    linewidth=2.0,
    color="black",
    label="Detrended annual mean anomaly"
)

axes[1].axhline(0, color="gray", linewidth=0.8)
axes[1].set_ylabel("SST anomaly (degC)")
axes[1].set_title(
    "North Atlantic Dentrended SST Anomaly",
    loc="left"
)
axes[1].yaxis.set_minor_locator(MultipleLocator(0.5))
axes[1].legend(loc="upper left", frameon=False)
axes[1].grid(which="major", linestyle="-", alpha=0.6)
axes[1].grid(which="minor", linestyle="--", alpha=0.3)

# ---------------------------------------------------------
# Common axis settings
# ---------------------------------------------------------
for ax in axes:
    ax.set_xlim(np.datetime64("1948-01-01"), np.datetime64("2025-12-31"))
    ax.set_ylim(-1.5, 1.5)


plt.suptitle(
    "North Atlantic SST Anomaly and Linear Trend\n"
    "Relative to 1991–2020 Monthly Climatology",
    fontsize=14
)

plt.tight_layout()

output_path = Path(__file__).with_suffix(".jpg")
plt.savefig(output_path, dpi=300, bbox_inches="tight")

plt.show()

