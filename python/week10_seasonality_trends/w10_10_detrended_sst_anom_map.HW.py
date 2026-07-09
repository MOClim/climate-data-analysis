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

import warnings
from pathlib import Path

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.util import add_cyclic_point
from matplotlib.ticker import MultipleLocator

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

def annual_anomaly(monthly_mean, clim_start="1991-01-01", clim_end="2020-12-31"):
    """Calculate annual mean anomalies relative to monthly climatology."""

    # Monthly climatology
    clim = monthly_mean.sel(time=slice(clim_start, clim_end)).groupby(
        "time.month"
    ).mean("time")

    # Monthly anomaly
    anom = monthly_mean.groupby("time.month") - clim

    # Annual mean anomaly
    anom_ann = anom.resample(time="YS").mean()
    count_ann = anom.resample(time="YS").count()

    # Keep only complete years
    anom_ann = anom_ann.where(count_ann == 12, drop=True)

    return anom_ann


def linear_detrend(da, trend_start="1949-01-01", trend_end="2020-12-31"):
    """
    Remove the full fitted linear trend from an annual anomaly field.

    This function works for both a 1-D regional time series and a
    3-D gridded field with dimensions (time, lat, lon).
    """

    # Select the period used for trend estimation
    da_fit = da.sel(time=slice(trend_start, trend_end))

    # Convert time to numeric year values
    year_fit = xr.DataArray(
        da_fit.time.dt.year.astype(float),
        dims="time",
        coords={"time": da_fit.time}
    )
    year_all = xr.DataArray(
        da.time.dt.year.astype(float),
        dims="time",
        coords={"time": da.time}
    )

    # Center the year coordinate using the trend-analysis period
    year_mean = float(year_fit.mean())
    x_fit = year_fit - year_mean
    x_all = year_all - year_mean

    # Fit linear trend at each grid point:
    # anomaly = slope * centered_year + intercept
    slope_per_year = (da_fit * x_fit).sum("time", skipna=True) / (
        x_fit ** 2
    ).sum("time", skipna=True)
    intercept = da_fit.mean("time", skipna=True)

    # Fitted linear trend line for all years
    trend_line = slope_per_year * x_all + intercept
    trend_line.name = "linear_trend"

    # Remove the full fitted trend line
    da_detrended = da - trend_line
    da_detrended.name = "detrended_anomaly"

    # Convert trend unit to degC per decade
    slope_decade = slope_per_year * 10.0
    slope_decade.name = "linear_trend_per_decade"

    return da_detrended, trend_line, slope_decade

# ---------------------------------------------------------
# Read data
# ---------------------------------------------------------
indir = Path("../../data_raw")
ds_file = indir / "HadISST_sst.nc"

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

print(sst.min().values)
print(sst.max().values)

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
anom_ann = annual_anomaly(sst, clim_start, clim_end)
anom_ann.attrs["units"] = "degC"

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

anom_ann_detrended, trend_line, slope_decade = 

anom_ann_detrended.attrs["units"] = "degC"

#
# Step 2: Calculate Tropical Pacific mean time series
#
# Define the Tropical Pacific region and calculate
# regional mean annual anomalies, detrended anomalies,
# and the fitted trend.
#
# Latitude : 20°N to 20°S
# Longitude: 120°E to 220°E

lat1, lat2 = , 
lon1, lon2 = , 

regional_anom = 
regional_detrended = 
regional_trend = 

# Regional trend value for the legend
# linear_detrend() returns three values:
#   detrended anomaly, trend line, and slope per decade.
# Use "_" for returned values that are not needed here.

_, _, regional_slope_decade = linear_detrend(
    regional_anom,
    trend_start,
    trend_end
)


# ---------------------------------------------------------
# Select target year for map and time-series marker
# ---------------------------------------------------------
target_time = f"{target_year}-01-01"

anom_target = anom_ann.sel(time=target_time)
detrended_target = anom_ann_detrended.sel(time=target_time)

regional_anom_target = regional_anom.sel(time=target_time)
regional_detrended_target = regional_detrended.sel(time=target_time)

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
    ,                   # longitude
    ,                   # latitude
    ,                   # annual anomaly
    levels=,            # contour levels
    cmap=,              # colormap
    extend="both",
    transform=          # PlateCarree projection
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
    ,                   # longitude
    ,                   # latitude
    ,                   # annual anomaly
    levels=,            # contour levels
    cmap=,              # colormap
    extend="both",
    transform=          # PlateCarree projection
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
year = regional_anom.time.dt.year
trend_start_year = int(trend_start[:4])
trend_end_year = int(trend_end[:4])

# Step 4: Plot the annual mean anomaly time series
#
# Complete the plot() function.
# Hint:
#   Use the regional annual anomaly and its time coordinate.

axes[1, 0].plot(
    ,                  # x-axis (time)
    ,                  # regional annual anomaly
    linewidth=,        # line width
    color="",          # line color
    label=""           # legend label
)

axes[1, 0].plot(
    year,
    regional_trend,
    linewidth=2.0,
    color="red",
    label=f"Trend = {float(regional_slope_decade):.2f} degC/decade"
)

axes[1, 0].scatter(
    target_year,
    regional_anom_target,
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
    ,                  # x-axis (time)
    ,                  # regional detrended annual anomaly
    linewidth=,        # line width
    color="",          # line color
    label=""           # legend label
)

axes[1, 1].scatter(
    target_year,
    regional_detrended_target,
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
row_min = min(float(regional_anom.min()), float(regional_detrended.min()))
row_max = max(float(regional_anom.max()), float(regional_detrended.max()))
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
