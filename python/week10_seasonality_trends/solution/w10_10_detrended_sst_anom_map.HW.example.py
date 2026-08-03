# ---------------------------------------------------------
# Annual SST Anomaly vs. Detrended Anomaly
# ---------------------------------------------------------
# Purpose:
#   Compare tropical Pacific SST anomalies before and after
#   removing the long-term linear trend.
#
#   The top row shows annual mean SST anomaly maps and
#   detrended anomaly maps for a selected year. The bottom
#   row shows the corresponding Tropical Pacific mean time
#   series.
#
# Directions:
#   Complete the missing sections to:
#     1. Calculate detrended annual anomalies.
#     2. Calculate the Tropical Pacific regional mean.
#     3. Plot annual anomaly and detrended anomaly maps.
#     4. Plot the regional annual and detrended anomaly time series and
#        fitted linear trend.
#
#   The program removes the 1991–2020 monthly climatology,
#   calculates annual mean anomalies, estimates the linear
#   trend, and removes the fitted trend from the annual
#   anomaly field.
# ---------------------------------------------------------

from pathlib import Path

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.util import add_cyclic_point
from matplotlib.ticker import MultipleLocator
import sys

import warnings
warnings.filterwarnings(
    "ignore",
    message="invalid value encountered in create_collection",
    category=RuntimeWarning
)


# ---------------------------------------------------------
# Functions
# ---------------------------------------------------------

def regional_weighted_mean(data, lat1, lat2, lon1, lon2):
    """
    Calculate cosine-latitude-weighted regional mean.

    Parameters
    ----------
    data : xarray.DataArray
        Input data with dimensions time, lat, lon.
    lat1, lat2 : float
        Latitude range.
    lon1, lon2 : float
        Longitude range.

    Returns
    -------
    regional_mean : xarray.DataArray
        Area-averaged regional time series.
    """

    # Rename coordinates if necessary
    if "latitude" in data.coords:
      data = data.rename({"latitude": "lat"})

    if "longitude" in data.coords:
      data = data.rename({"longitude": "lon"})

    # Convert longitude system if needed
    if lon1 < 0 or lon2 < 0:
        if (data.lon > 180).any():
            data = data.assign_coords(
                lon=((data.lon + 180) % 360 - 180)
            ).sortby("lon")
    else:
       if (data.lon < 0).any():
            data = data.assign_coords(
                lon=(data.lon % 360)
            ).sortby("lon")

    # Select latitude range correctly
    if data.lat[0] > data.lat[-1]:
        dat_region = data.sel(
            lat=slice(lat1, lat2),
            lon=slice(lon1, lon2)
        )
    else:
        dat_region = data.sel(
            lat=slice(lat2, lat1),
            lon=slice(lon1, lon2)
        )

    # Cosine-latitude weighting
    weights = np.cos(np.deg2rad(dat_region.lat))

    regional_mean = dat_region.weighted(weights).mean(
        dim=("lat", "lon"),
        skipna=True
    )

    return regional_mean

def calc_seasonal_anom(dat, window=12, end_month=12, clim_period=None):
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
# Read data
# ---------------------------------------------------------
script_dir = Path(__file__).resolve().parent

# Check whether the script is inside the "solution" directory
if script_dir.name == "solution":
    repo_dir = script_dir.parents[2]
else:
    repo_dir = script_dir.parents[1]

ds_file = repo_dir / "data_raw/HadISST_sst.nc"

ds = xr.open_dataset(ds_file)

print(ds)
print("Last available time:", ds.time[-1].values)

# Select SST [degC]
sst = ds["sst"]

# Mask land and missing values
sst = sst.where(sst > -100)

# Rename coordinates to match the course examples
sst = sst.rename({
    "latitude": "lat",
    "longitude": "lon"
})
sst.attrs["units"] = "degC"

print(sst.min().values)
print(sst.max().values)

if "latitude" in sst.coords:
    sst = sst.rename({"latitude": "lat"})

if "longitude" in sst.coords:
    sst = sst.rename({"longitude": "lon"})

# ---------------------------------------------------------
# Analysis settings
# ---------------------------------------------------------
clim_start = "1991-01-01"
clim_end = "2020-12-31"
trend_start = "1949-01-01"
trend_end = "2020-12-31"
target_year = 1969

# ---------------------------------------------------------
# Calculate annual anomalies and detrended anomalies
# ---------------------------------------------------------
# Annual mean anomalies relative to monthly climatology
anom = calc_seasonal_anom(sst, window=12, end_month=12, clim_period=[clim_start, clim_end])

#
# Step 1: Calculate detrended annual anomalies
#
# Remove the linear trend from the annual mean anomaly.
# Also save the fitted trend line and trend slope.
#
# Hint:
# linear_detrend() returns three variables:
#   1. Detrended anomaly
#   2. Fitted trend line
#   3. Linear trend (degC per decade)

anom_detrended, trend_line, slope_decade = linear_detrend(
    anom, trend_period=[trend_start,trend_end], return_trend=True)

#
# Step 2: Calculate Tropical Pacific mean time series
#
# Define the Tropical Pacific region and calculate
# regional mean annual anomalies, detrended anomalies,
# and the fitted trend.
#
# Latitude : 20°N to 20°S
# Longitude: 120°E to 220°E

lat1, lat2 = 20, -20
lon1, lon2 = 120, 220

reg_anom = regional_weighted_mean(anom, lat1, lat2, lon1, lon2)
reg_detrended = regional_weighted_mean(anom_detrended, lat1, lat2, lon1, lon2)
reg_trend = regional_weighted_mean(trend_line, lat1, lat2, lon1, lon2)

# Regional trend value for the legend
# linear_detrend() returns three values:
#   detrended anomaly, trend line, and slope per decade.
# Use "_" for returned values that are not needed here.

_, _, reg_slope_decade = linear_detrend(
    reg_anom, trend_period=[trend_start,trend_end], return_trend=True)


# ---------------------------------------------------------
# Select target year for map and time-series marker
# ---------------------------------------------------------
target_time = f"{target_year}-01-01"

anom_target = anom.sel(year=target_year)
detrended_target = anom_detrended.sel(year=target_year)

reg_anom_target = reg_anom.sel(year=target_year)
reg_detrended_target = reg_detrended.sel(year=target_year)

print("Annual anomaly range:", float(anom_target.min()), float(anom_target.max()))
print(
    "Detrended annual anomaly range:",
    float(detrended_target.min()),
    float(detrended_target.max())
)


# ---------------------------------------------------------
# Add cyclic points to close the 0/360 longitude seam
# ---------------------------------------------------------
anom_cyclic, lon_cyclic = add_cyclic_point(
    anom_target.values,
    coord=anom_target.lon
)

detrended_cyclic, lon_cyclic = add_cyclic_point(
    detrended_target.values,
    coord=detrended_target.lon
)


# ---------------------------------------------------------
# Plot maps and tropical Pacific mean time series
# ---------------------------------------------------------
proj = ccrs.Robinson(central_longitude=180)

fig, axes = plt.subplots(
    2, 2,
    figsize=(12, 8),
    constrained_layout=True
)

# Remove the default top-row axes
axes[0, 0].remove()
axes[0, 1].remove()

# Create Cartopy axes in the same positions
axes[0, 0] = fig.add_subplot(2, 2, 1, projection=proj)
axes[0, 1] = fig.add_subplot(2, 2, 2, projection=proj)


# Use the same contour levels for both maps because both fields
# have the same unit. This makes the comparison direct.
levels = np.arange(-1, 1.1, 0.1)
cmap = "RdBu_r"

# ---------------------------------------------------------
# Panel 1: original annual anomaly map
# ---------------------------------------------------------

# Step 3: Plot the annual anomaly map
#
# Complete the contourf() function.
# Hint:
#   Use the cyclic longitude, latitude, annual anomaly,
#   contour levels, colormap, and PlateCarree transform.

cf1 = axes[0, 0].contourf(
    lon_cyclic,
    anom_target.lat,
    anom_cyclic,
    levels=levels,
    cmap=cmap,
    extend="both",
    transform=ccrs.PlateCarree()
)

axes[0, 0].set_title(
    f"(a) Annual Mean SST Anomaly\n"
    f"{target_year} relative to {clim_start[:4]}-{clim_end[:4]} climatology",
    loc="left"
)

# ---------------------------------------------------------
# Panel 2: detrended annual anomaly map
# ---------------------------------------------------------

# Step 3: Plot the detrended annual anomaly map
#
# Complete the contourf() function.
# Hint:
#   Use the cyclic longitude, latitude, annual anomaly,
#   contour levels, colormap, and PlateCarree transform.

cf2 = axes[0, 1].contourf(
    lon_cyclic,
    detrended_target.lat,
    detrended_cyclic,
    levels=levels,
    cmap=cmap,
    extend="both",
    transform=ccrs.PlateCarree()
)

axes[0, 1].set_title(
    f"(b) Detrended Annual Mean SST Anomaly\n"
    f"{target_year} with {trend_start[:4]}-{trend_end[:4]} trend removed",
    loc="left"
)

# Common map features
for ax in [axes[0, 0], axes[0, 1]]:
    ax.set_global()
    ax.coastlines(linewidth=0.7)
    ax.add_feature(cfeature.BORDERS, linewidth=0.4)
    ax.gridlines(linewidth=0.3, color="gray", alpha=0.5, linestyle="--")

# ---------------------------------------------------------
# Panel 3: regional annual anomaly and linear trend
# ---------------------------------------------------------
year = reg_anom.year
trend_start_year = int(trend_start[:4])
trend_end_year = int(trend_end[:4])

# Step 4: Plot the annual mean anomaly time series
#
# Complete the plot() function.
# Hint:
#   Use the regional annual anomaly and its time coordinate.

axes[1, 0].plot(
    year,
    reg_anom,
    linewidth=1.5,
    color="black",
    label="Tropical Pacific annual anomaly"
)
axes[1, 0].plot(
    year,
    reg_trend,
    linewidth=2.0,
    color="red",
    label=f"Trend = {float(reg_slope_decade):.2f} degC/decade"
)

axes[1, 0].scatter(
    target_year,
    reg_anom_target,
    color="blue",
    zorder=5,
    label=f"Selected year: {target_year}"
)
axes[1, 0].axvline(target_year, color="blue", linestyle="--", linewidth=1.0)
axes[1, 0].axvspan(
    trend_start_year,
    trend_end_year,
    color="gray",
    alpha=0.10,
    zorder=0
)
axes[1, 0].axhline(0, color="gray", linewidth=0.8)
axes[1, 0].set_title(
    "(c) Tropical Pacific SST Anomaly and Linear Trend",
    loc="left"
)
axes[1, 0].set_ylabel("Temperature anomaly (degC)")
axes[1, 0].legend(loc="upper left", fontsize=8, frameon=False)

# ---------------------------------------------------------
# Panel 4: Tropical Pacific detrended annual anomaly
# ---------------------------------------------------------

# Step 4: Plot the detrended annual mean anomaly time series
#
# Complete the plot() function.
# Hint:
#   Use the regional annual anomaly and its time coordinate.

axes[1, 1].plot(
    year,
    reg_detrended,
    linewidth=1.5,
    color="black",
    label="Tropical Pacific detrended annual anomaly"
)

axes[1, 1].scatter(
    target_year,
    reg_detrended_target,
    color="blue",
    zorder=5,
    label=f"Selected year: {target_year}"
)
axes[1, 1].axvline(target_year, color="blue", linestyle="--", linewidth=1.0)
axes[1, 1].axvspan(
    trend_start_year,
    trend_end_year,
    color="gray",
    alpha=0.10,
    zorder=0
)
axes[1, 1].axhline(0, color="gray", linewidth=0.8)
axes[1, 1].set_title(
    "(d) Tropical Pacific Mean Detrended Annual Anomaly",
    loc="left"
)
axes[1, 1].set_ylabel("SST anomaly (degC)")
axes[1, 1].legend(loc="upper left", fontsize=8, frameon=False)


# Use the same y-axis range for the two time-series panels
row_min = min(float(reg_anom.min()), float(reg_detrended.min()))
row_max = max(float(reg_anom.max()), float(reg_detrended.max()))
row_abs = max(abs(row_min), abs(row_max))
row_lim = np.ceil(row_abs * 10) / 10

# Common time-series axis settings
for ax in [axes[1, 0], axes[1, 1]]:
    ax.set_xlim(1948, 2025)
    ax.set_xticks(np.arange(1950, 2030, 10))
    ax.set_xlabel("Year")
    ax.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax.grid(which="major", linestyle="-", alpha=0.6)
    ax.grid(which="minor", linestyle="--", alpha=0.3)
    ax.set_ylim(-row_lim, row_lim)

# One shared colorbar for the two map panels
cbar1 = fig.colorbar(
    cf1,
    ax=axes[0, 0],
    orientation="horizontal"
)
cbar1.set_label("SST anomaly (degC)")

cbar2 = fig.colorbar(
    cf2,
    ax=axes[0, 1],
    orientation="horizontal"
)
cbar2.set_label("SST anomaly (degC)")



fig.suptitle(
    "Tropical Pacific Annual Mean SST: Anomaly vs. Detrended Anomaly",
    fontsize=14
)

output_path = Path(__file__).with_suffix(".jpg")
plt.savefig(output_path, dpi=300, bbox_inches="tight")

plt.show()
ds.close()
