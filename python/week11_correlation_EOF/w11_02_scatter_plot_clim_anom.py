# Scatter Plot of Two Climate Variables
#
# w11_02_scatter_plot_clim_anom.py
#
# Compare annual mean anomalies of global SST and global 2-m air temperature.
# The monthly climatology is removed first, and then monthly anomalies are
# averaged into annual anomalies.

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import sys

from pathlib import Path

# ---------------------------------------------------------
# Functions
# ---------------------------------------------------------
def regional_weighted_mean(data, lat1, lat2, lon1, lon2):
    """
    Compute cosine-latitude-weighted regional mean over the specified lat-lon bounds.

    Parameters
    ----------
    data : xarray.DataArray
        Input data with dimensions (time, lat, lon) or (year, lat, lon).
    lat1, lat2 : float
        Latitude bounds.
    lon1, lon2 : float
        Longitude bounds, either in -180 to 180 or 0 to 360.

    Returns
    -------
    dat_region_mean : xarray.DataArray
        Regional mean time series.
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

    return dat_region_mean

def calc_seasonal_anom(dat, window=12, end_month=12, clim_period=None):
    """
    Calculate seasonal mean anomaly using a trailing running mean, extract the final month (e.g., Mar for NDJFM),
    convert to year-lat-lon DataArray, apply minimum coverage mask, and optionally remove trend.

    Parameters:
    -----------
    dat : xr.DataArray
        Input data with dimensions (time, lat, lon) and datetime64 'time'.
    window : int
        Running mean window size (default is 12).
    end_month : int
        Target month used to extract seasonal means (final month of the trailing average).
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

def linear_fit_xy(x, y):
    """
    Calculate a linear regression line for a scatter plot.

    Parameters
    ----------
    x, y : xarray.DataArray or numpy.ndarray
        Input x and y data. Both must be 1-D time series.

    Returns
    -------
    slope : float
        Linear regression slope.
    intercept : float
        Linear regression intercept.
    xfit : numpy.ndarray
        x values for plotting the fitted line.
    yfit : numpy.ndarray
        y values for plotting the fitted line.
    """

    x_values = np.asarray(x)
    y_values = np.asarray(y)

    # Remove missing values before fitting
    valid = np.isfinite(x_values) & np.isfinite(y_values)
    x_values = x_values[valid]
    y_values = y_values[valid]

    slope, intercept = np.polyfit(x_values, y_values, 1)

    xfit = np.linspace(x_values.min(), x_values.max(), 100)
    yfit = slope * xfit + intercept

    return slope, intercept, xfit, yfit

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

# -------------------------------------------------------
# Read datasets
# -------------------------------------------------------

indir = Path("../../data")
indir2 = Path("../../data_raw")

air_file = indir / "air.2m.mon.mean.nc"
sst_file = indir2 / "HadISST_sst.nc"

ds_air = xr.open_dataset(air_file)
ds_sst = xr.open_dataset(sst_file)

air = ds_air["air"]
sst = ds_sst["sst"]

# Convert Kelvin to Celsius
air = air - 273.15
air.attrs["units"] = "degC"

# Replace missing values with NaN while keeping xarray coordinates
sst = sst.where((sst != -1000) & (sst != -1.0e30))

if "latitude" in sst.coords:
   sst = sst.rename({"latitude": "lat"})

if "longitude" in sst.coords:
   sst = sst.rename({"longitude": "lon"})


# -------------------------------------------------------
# Monthly anomalies
# -------------------------------------------------------

air_mon_anom = monthly_clm_anom(air)
sst_mon_anom = monthly_clm_anom(sst)

# -------------------------------------------------------
# Annual mean of monthly anomalies
# -------------------------------------------------------

air_anom = calc_seasonal_anom(air).sel(year=slice(1948,2025))
sst_anom = calc_seasonal_anom(sst).sel(year=slice(1948,2025))

# -------------------------------------------------------
# Global monthly means
# -------------------------------------------------------
# This reduces the gridded fields to 1-D global time series.

air_anom_glob = regional_weighted_mean(
    air_anom,
    90, -90,
    0, 360
)

sst_anom_glob = regional_weighted_mean(
    sst_anom,
    90, -90,
    -180, 180
)


# -------------------------------------------------------
# Remove linear trends
# -------------------------------------------------------

air_detrended = linear_detrend(air_anom_glob)
sst_detrended = linear_detrend(sst_anom_glob)

# -------------------------------------------------------
# Linear regression
# -------------------------------------------------------

slope, intercept, xfit, yfit = linear_fit_xy(
    sst_detrended,
    air_detrended
)


# -------------------------------------------------------
# Pearson correlation coefficient
# np.corrcoef() returns a 2×2 correlation matrix.
# [0, 1] extracts the correlation between SST and air temperature.
# -------------------------------------------------------

r = np.corrcoef(
    sst_detrended,
    air_detrended
)[0, 1]

# -------------------------------------------------------
# Create figure
# -------------------------------------------------------

fig, axes = plt.subplots(
    1, 2,
    figsize=(10, 5),
    constrained_layout=True
)


# ---------------------------------
# Time series
# ---------------------------------

axes[0].plot(
    air_detrended.year,
    air_detrended,
    label="Detrended Air Temperature Anomaly",
    linewidth=2,
)

axes[0].plot(
    sst_detrended.year,
    sst_detrended,
    label="Detrended SST Anomaly",
    linewidth=2,
)

axes[0].axhline(0, color="black", linewidth=0.8)
axes[0].set_xlabel("Year")
axes[0].set_ylabel("Temperature Anomaly (°C)")
axes[0].set_title("Detrended Annual Mean Global Anomalies")
axes[0].grid(True)
axes[0].legend()


# ---------------------------------
# Scatter plot
# ---------------------------------

axes[1].scatter(
    sst_detrended,
    air_detrended,
    s=40,
    label="Detrended Annual Anomalies"
)

axes[1].plot(
    xfit,
    yfit,
    color="red",
    linewidth=2,
    label=f"Linear Fit (Slope = {slope:.2f}, r = {r:.2f})"
)

axes[1].axhline(0, color="black", linewidth=0.8)
axes[1].axvline(0, color="black", linewidth=0.8)
axes[1].set_xlabel("Global Mean SST Anomaly (°C)")
axes[1].set_ylabel("Global Mean Air Temperature Anomaly (°C)")
axes[1].set_title("SST vs Air Temperature Anomaly")
axes[1].grid(True)
axes[1].legend()


# -------------------------------------------------------
# Save figure
# -------------------------------------------------------

output_path = Path(__file__).with_suffix(".jpg")
plt.savefig(output_path, dpi=300, bbox_inches="tight")

plt.show()
