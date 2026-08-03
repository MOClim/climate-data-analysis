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
import sys

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

def linear_detrend(
    dat,
    min_coverage=0.9,
    dtrend=True,
    trend_period=None,
    return_trend=False
):
    """
    Remove the long-term linear trend from annual data.

    Parameters
    ----------
    dat : xr.DataArray
        Annual data with a "year" dimension.
    min_coverage : float
        Minimum fraction of valid years required.
    dtrend : bool
        If True, remove the fitted linear trend.
    trend_period : list, optional
        Start and end dates used to estimate the trend.
    return_trend : bool
        If True, also return the trend line and slope per decade.

    Returns
    -------
    dat_out : xr.DataArray
        Masked annual data with the linear trend removed.
    trend_line : xr.DataArray, optional
        Fitted linear trend evaluated over the full record.
    slope_decade : xr.DataArray, optional
        Linear slope in units per decade.
    """

    if trend_period is None:
        dat_fit = dat
    else:
        start, end = trend_period
        start_year = int(str(start)[:4])
        end_year = int(str(end)[:4])
        dat_fit = dat.sel(year=slice(start_year, end_year))

    # Apply coverage mask
    valid_counts = dat_fit.count(dim="year")
    total_years = dat_fit["year"].size
    min_valid_years = int(total_years * min_coverage)

    sufficient_coverage = valid_counts >= min_valid_years
    dat_masked = dat.where(sufficient_coverage)
    dat_fit_masked = dat_fit.where(sufficient_coverage)

    # Fit the trend using only the selected trend period
    coeffs = dat_fit_masked.polyfit(dim="year", deg=1)

    # Evaluate the fitted line over the full data period
    trend_line = xr.polyval(
        dat_masked["year"],
        coeffs.polyfit_coefficients
    )

    # Extract slope and convert from units/year to units/decade
    slope_year = coeffs.polyfit_coefficients.sel(degree=1)
    slope_decade = slope_year * 10

    if dtrend:
        dat_out = dat_masked - trend_line
    else:
        dat_out = dat_masked

    if return_trend:
        return dat_out, trend_line, slope_decade
    else:
        return dat_out

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

if "latitude" in sst.coords:
   sst = sst.rename({"latitude": "lat"})

if "longitude" in sst.coords:
   sst = sst.rename({"longitude": "lon"})

# ---------------------------------------------------------
# Calculate monthly and annual mean anomalies
# ---------------------------------------------------------
clim_start = "1991-01-01"
clim_end = "2020-12-31"
trend_start = "1949-01-01"
trend_end = "2020-12-31"

# Step 2: Calculate monthly SST anomalies relative to the
# 1991–2020 monthly climatology by calling
# monthly_clm_anom().

sst_mon_anom = monthly_clm_anom(sst, clim_period=[clim_start, clim_end])

# Step 3: Calculate annual mean anomalies from the monthly
# anomalies.
#

sst_anom = calc_seasonal_anom(sst,window=12,end_month=12,clim_period=[clim_start,clim_end])


# ---------------------------------------------------------
# Calculate regional area-weighted means
# ---------------------------------------------------------
# Approximate North America box
lat_str, lat_end = 60, 0
lon_str, lon_end = -80, 0   # -180-180 longitude

sst_anom_NA = regional_weighted_mean(sst_anom, lat_str, lat_end, lon_str, lon_end)
sst_mon_anom_NA = regional_weighted_mean(sst_mon_anom, lat_str, lat_end, lon_str, lon_end)


# Calculate linear regression coefficients
coeffs = sst_anom_NA.polyfit(dim="year", deg=1)

# Extract the slope in °C per year
slope_year = coeffs.polyfit_coefficients.sel(degree=1)

# Convert to °C per decade
slope_decade = float(slope_year * 10)

# Calculate the fitted trend line
sst_anom_NA_trend = xr.polyval(
    sst_anom_NA["year"],
    coeffs.polyfit_coefficients
)

# Detrended annual anomaly
sst_anom_NA_detrended = linear_detrend(
        sst_anom_NA, trend_period=[trend_start,trend_end])

# Convert year coordinates to datetime for plotting
sst_time = np.array([np.datetime64(f"{y}-01-01") for y in sst_anom_NA.year.values])

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
    sst_time,
    sst_anom_NA,
    linewidth=2.0,
    color="black",
    label="Annual mean anomaly"
)
# Overlay a linear trend 
axes[0].plot(
    sst_time,
    sst_anom_NA_trend,
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
    sst_time,
    sst_anom_NA_detrended,
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

