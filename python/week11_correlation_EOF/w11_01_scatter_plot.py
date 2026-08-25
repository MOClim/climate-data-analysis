# Scatter Plot of Two Climate Variables
#
# Compare annual global mean SST and annual global mean
# 2-m air temperature.

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

def linear_fit_xy(x, y):
    """
    Calculate a linear regression line for a scatter plot.

    Parameters
    ----------
    x, y : xarray.DataArray or numpy.ndarray
        Input x and y data.

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

    slope, intercept = np.polyfit(x_values, y_values, 1)

    xfit = np.linspace(x_values.min(), x_values.max(), 100)
    yfit = slope * xfit + intercept

    return slope, intercept, xfit, yfit

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

#### Replace missing values with NaN ####
sst = sst.where((sst != -1000) & (sst != -1.e+30))
sst.attrs["units"] = "degC"

# -------------------------------------------------------
# Calculate annual means
# -------------------------------------------------------

air_ann = calc_seasonal_mean(air,window=12,end_month=12)
sst_ann = calc_seasonal_mean(sst,window=12,end_month=12)



# -------------------------------------------------------
# Global annual means
# -------------------------------------------------------
lat_str, lat_end = 90, -90
lon_str, lon_end = 0, 360   # 0-360 longitude: 190E=170W, 300E=60W

air_global = regional_weighted_mean(air_ann, lat_str, lat_end, lon_str, lon_end)

lat_str, lat_end = 90, -90
lon_str, lon_end = -180, 180   # 0-360 longitude: 190E=170W, 300E=60W
sst_global = regional_weighted_mean(sst_ann, lat_str, lat_end, lon_str, lon_end)


common_years = np.intersect1d(
    air_global.year,
    sst_global.year
)

air_global = air_global.sel(year=common_years)
sst_global = sst_global.sel(year=common_years)

# -------------------------------------------------------
# Calculate annual anomalies
# Use the common-year period as the baseline
# -------------------------------------------------------

air_anom = air_global - air_global.mean("year")
sst_anom = sst_global - sst_global.mean("year")

# -------------------------------------------------------
# Linear regression
# -------------------------------------------------------

slope, intercept, xfit, yfit = linear_fit_xy(sst_anom, air_anom)

# -------------------------------------------------------
# Pearson correlation coefficient
# np.corrcoef() returns a 2×2 correlation matrix.
# [0, 1] extracts the correlation between SST and air temperature.
# -------------------------------------------------------

r = np.corrcoef(sst_anom,air_anom)[0, 1]

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
    air_anom.year,
    air_anom,
    label="Air Temperature Anomaly",
    linewidth=2,
)

axes[0].plot(
    sst_anom.year,
    sst_anom,
    label="SST Anomaly",
    linewidth=2,
)

axes[0].set_xlabel("Year")
axes[0].set_ylabel("Temperature Anomaly (°C)")
axes[0].set_title("Annual Global Mean Temperature Anomaly")
axes[0].grid(True)
axes[0].legend()


# ---------------------------------
# Scatter plot
# ---------------------------------


axes[1].scatter(
    sst_anom,
    air_anom,
    s=40,
)

axes[1].plot(
    xfit,
    yfit,
    color="red",
    linewidth=2,
    label=f"Linear Fit (Slope = {slope:.2f}, r = {r:.2f})"
)

axes[1].legend()
axes[1].set_xlabel("Global Mean SST Anomaly (°C)")
axes[1].set_ylabel("Global Mean Air Temperature Anomaly (°C)")
axes[1].set_title("SST vs Air Temperature Anomaly")
axes[1].grid(True)

output_path = Path(__file__).with_suffix(".jpg")
plt.savefig(output_path, dpi=300, bbox_inches="tight")


plt.show()

