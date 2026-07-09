# ---------------------------------------------------------
# Annual Temperature Anomaly vs. Detrended Anomaly
# ---------------------------------------------------------
# Purpose:
#   Compare annual mean 2-m air temperature anomalies before
#   and after removing the long-term linear trend.
#
#   The top row shows the spatial pattern for one selected
#   year. The bottom row shows the corresponding global mean
#   time series, so the connection between the detrending
#   procedure and the mapped anomaly fields is clear.
#
#   The program removes the 1991-2020 monthly climatology,
#   calculates annual mean anomalies, estimates the linear
#   trend at each grid point, and removes the fitted trend
#   from the annual anomaly field.
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


def global_weighted_mean(data):
    """Calculate cosine-latitude-weighted global mean."""

    weights = np.cos(np.deg2rad(data.lat))
    global_mean = data.weighted(weights).mean(
        dim=("lat", "lon"),
        skipna=True
    )

    return global_mean


# ---------------------------------------------------------
# Read data
# ---------------------------------------------------------
indir = Path("../../data")
air_file = indir / "air.2m.mon.mean.nc"

ds = xr.open_dataset(air_file)

print(ds)
print("Last available time:", ds.time[-1].values)

# Select 2-m air temperature and convert K to degC
air = ds["air"] - 273.15
air.attrs["units"] = "degC"


# ---------------------------------------------------------
# Analysis settings
# ---------------------------------------------------------
clim_start = "1991-01-01"
clim_end = "2020-12-31"
trend_start = "1949-01-01"
trend_end = "2020-12-31"
target_year = 2016


# ---------------------------------------------------------
# Calculate annual anomalies and detrended anomalies
# ---------------------------------------------------------
# Annual mean anomalies relative to monthly climatology
anom_ann = annual_anomaly(air, clim_start, clim_end)
anom_ann.attrs["units"] = "degC"

# Detrended annual mean anomalies
anom_ann_detrended, trend_line, slope_decade = linear_detrend(
    anom_ann,
    trend_start,
    trend_end
)
anom_ann_detrended.attrs["units"] = "degC"

# Global mean time series for the bottom row
# These time series show how the linear trend is removed from
# the global annual mean anomaly.
global_anom = global_weighted_mean(anom_ann)
global_detrended = global_weighted_mean(anom_ann_detrended)
global_trend = global_weighted_mean(trend_line)

# Global trend value for the legend
_, _, global_slope_decade = linear_detrend(
    global_anom,
    trend_start,
    trend_end
)


# ---------------------------------------------------------
# Select target year for map and time-series marker
# ---------------------------------------------------------
target_time = f"{target_year}-01-01"

anom_target = anom_ann.sel(time=target_time)
detrended_target = anom_ann_detrended.sel(time=target_time)

global_anom_target = global_anom.sel(time=target_time)
global_detrended_target = global_detrended.sel(time=target_time)

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
# Plot maps and global mean time series
# ---------------------------------------------------------
proj = ccrs.Robinson(central_longitude=180)
data_crs = ccrs.PlateCarree()

# Use GridSpec so the map row, colorbar, and time-series row
# have separate spaces. This avoids overlap between the maps,
# colorbar, and lower panels.
fig = plt.figure(figsize=(10, 7), constrained_layout=True)
gs = fig.add_gridspec(
    3, 2,
    height_ratios=[1.0, 0.08, 1.0],
    hspace=0.10,
    wspace=0.12
)

# Top row: map panels
ax_map1 = fig.add_subplot(gs[0, 0], projection=proj)
ax_map2 = fig.add_subplot(gs[0, 1], projection=proj)

# Middle row: shared colorbar for the map panels
cax = fig.add_subplot(gs[1, :])

# Bottom row: global mean time-series panels
ax_ts1 = fig.add_subplot(gs[2, 0])
ax_ts2 = fig.add_subplot(gs[2, 1])

# Use the same contour levels for both maps because both fields
# have the same unit. This makes the comparison direct.
levels = np.arange(-5, 5.5, 0.5)
cmap = "RdBu_r"

# ---------------------------------------------------------
# Panel 1: original annual anomaly map
# ---------------------------------------------------------
cf1 = ax_map1.contourf(
    lon_cyclic,
    anom_target.lat,
    anom_cyclic,
    levels=levels,
    cmap=cmap,
    extend="both",
    transform=data_crs
)

ax_map1.set_title(
    f"(a) Annual Mean Air Temperature Anomaly\n"
    f"{target_year} relative to {clim_start[:4]}-{clim_end[:4]} climatology",
    loc="left"
)

# ---------------------------------------------------------
# Panel 2: detrended annual anomaly map
# ---------------------------------------------------------
cf2 = ax_map2.contourf(
    lon_cyclic,
    detrended_target.lat,
    detrended_cyclic,
    levels=levels,
    cmap=cmap,
    extend="both",
    transform=data_crs
)

ax_map2.set_title(
    f"(b) Detrended Annual Mean Air Temperature Anomaly\n"
    f"{target_year} with {trend_start[:4]}-{trend_end[:4]} trend removed",
    loc="left"
)

# Common map features
for ax in [ax_map1, ax_map2]:
    ax.set_global()
    ax.coastlines(linewidth=0.7)
    ax.add_feature(cfeature.BORDERS, linewidth=0.4)
    ax.gridlines(linewidth=0.3, color="gray", alpha=0.5, linestyle="--")

# ---------------------------------------------------------
# Panel 3: global annual anomaly and linear trend
# ---------------------------------------------------------
year = global_anom.time.dt.year
trend_start_year = int(trend_start[:4])
trend_end_year = int(trend_end[:4])

ax_ts1.plot(
    year,
    global_anom,
    linewidth=1.5,
    color="black",
    label="Global annual anomaly"
)
ax_ts1.plot(
    year,
    global_trend,
    linewidth=2.0,
    color="red",
    label=f"Trend = {float(global_slope_decade):.2f} degC/decade"
)
ax_ts1.scatter(
    target_year,
    global_anom_target,
    color="blue",
    zorder=5,
    label=f"Selected year: {target_year}"
)
ax_ts1.axvline(target_year, color="blue", linestyle="--", linewidth=1.0)
ax_ts1.axvspan(
    trend_start_year,
    trend_end_year,
    color="gray",
    alpha=0.10,
    zorder=0
)
ax_ts1.axhline(0, color="gray", linewidth=0.8)
ax_ts1.set_title(
    "(c) Global Mean Annual Anomaly and Linear Trend",
    loc="left"
)
ax_ts1.set_ylabel("Temperature anomaly (degC)")
ax_ts1.legend(loc="upper left", fontsize=8, frameon=False)

# ---------------------------------------------------------
# Panel 4: global detrended annual anomaly
# ---------------------------------------------------------
ax_ts2.plot(
    year,
    global_detrended,
    linewidth=1.5,
    color="black",
    label="Global detrended annual anomaly"
)
ax_ts2.scatter(
    target_year,
    global_detrended_target,
    color="blue",
    zorder=5,
    label=f"Selected year: {target_year}"
)
ax_ts2.axvline(target_year, color="blue", linestyle="--", linewidth=1.0)
ax_ts2.axvspan(
    trend_start_year,
    trend_end_year,
    color="gray",
    alpha=0.10,
    zorder=0
)
ax_ts2.axhline(0, color="gray", linewidth=0.8)
ax_ts2.set_title(
    "(d) Global Mean Detrended Annual Anomaly",
    loc="left"
)
ax_ts2.set_ylabel("Temperature anomaly (degC)")
ax_ts2.legend(loc="upper left", fontsize=8, frameon=False)

# Common time-series axis settings
for ax in [ax_ts1, ax_ts2]:
    ax.set_xlim(1948, 2025)
    ax.set_xticks(np.arange(1950, 2030, 10))
    ax.set_xlabel("Year")
    ax.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax.grid(which="major", linestyle="-", alpha=0.6)
    ax.grid(which="minor", linestyle="--", alpha=0.3)

# Use the same y-axis range for the two time-series panels
row_min = min(float(global_anom.min()), float(global_detrended.min()))
row_max = max(float(global_anom.max()), float(global_detrended.max()))
row_abs = max(abs(row_min), abs(row_max))
row_lim = np.ceil(row_abs * 10) / 10
ax_ts1.set_ylim(-row_lim, row_lim)
ax_ts2.set_ylim(-row_lim, row_lim)

# One shared colorbar for the two map panels
cbar = fig.colorbar(
    cf2,
    cax=cax,
    orientation="horizontal"
)
cbar.set_label("2-m air temperature anomaly (degC)")

fig.suptitle(
    "Global Annual Mean 2-m Air Temperature: Anomaly vs. Detrended Anomaly",
    fontsize=14
)

output_path = Path(__file__).with_suffix(".jpg")
plt.savefig(output_path, dpi=300, bbox_inches="tight")

plt.show()
ds.close()
