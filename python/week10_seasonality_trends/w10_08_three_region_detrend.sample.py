# ---------------------------------------------------------
# Three-Region Temperature Anomaly vs. Detrended Anomaly
# ---------------------------------------------------------
# Purpose:
#   Compare annual mean temperature anomalies with detrended
#   anomalies for three climate regions.
#
# Direction:
#   After running the program, change the trend analysis
#   period (trend_start and trend_end) and compare how the
#   detrended time series and estimated linear trends change.
# ---------------------------------------------------------

from pathlib import Path

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


# ---------------------------------------------------------
# Functions
# ---------------------------------------------------------
def regional_weighted_mean(data, lat1, lat2, lon1, lon2):
    """Calculate cosine-latitude-weighted regional mean."""

    # Convert longitude coordinates if needed
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

    # Select latitude correctly for either increasing or decreasing latitude axis
    if data.lat[0] > data.lat[-1]:
        dat_region = data.sel(lat=slice(lat1, lat2), lon=slice(lon1, lon2))
    else:
        dat_region = data.sel(lat=slice(lat2, lat1), lon=slice(lon1, lon2))

    # Cosine-latitude weights for area-weighted mean
    weights = np.cos(np.deg2rad(dat_region.lat))

    reg_mean = dat_region.weighted(weights).mean(
        dim=("lat", "lon"),
        skipna=True
    )

    return reg_mean


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
    coeff = np.polyfit(x_fit.values, da_fit.values, deg=1)
    slope_per_year = coeff[0]
    intercept = coeff[1]

    # Fitted linear trend line for all years
    trend_line = xr.DataArray(
        slope_per_year * x_all + intercept,
        dims="time",
        coords={"time": da.time},
        name="linear_trend"
    )

    # Remove the full fitted trend line: slope component + intercept
    da_detrended = da - trend_line
    da_detrended.name = "detrended_anomaly"

    # Convert trend unit to degC per decade
    slope_decade = slope_per_year * 10.0

    return da_detrended, trend_line, slope_decade

# ---------------------------------------------------------
# Read data
# ---------------------------------------------------------
indir = Path("../../data")
filein = indir / "air.2m.mon.mean.nc"

ds = xr.open_dataset(filein)
air = ds["air"]

# Convert K to degC
air = air - 273.15
air.attrs["units"] = "degC"


# ---------------------------------------------------------
# Analysis settings
# ---------------------------------------------------------
clim_start = "1991-01-01"
clim_end = "2020-12-31"
trend_start = "1949-01-01"
trend_end = "2020-12-31"

regions = [
    ("North America", 75, 15, 190, 310),
    ("Tropical Pacific", 20, -20, 120, 280),
    ("Arctic", 90, 60, 0, 360),
]


# ---------------------------------------------------------
# Plot three regions: anomaly vs. detrended anomaly
# ---------------------------------------------------------
fig, axes = plt.subplots(
    3, 2,
    figsize=(12, 8),
    sharex=True,
    sharey="row"
)

for i, (name, lat1, lat2, lon1, lon2) in enumerate(regions):

    # Regional mean
    reg_mean = regional_weighted_mean(air, lat1, lat2, lon1, lon2)

    # Annual anomaly
    reg_anom = annual_anomaly(reg_mean, clim_start, clim_end)

    # Detrended annual anomaly
    reg_detrended, trend_line, slope_decade = linear_detrend(
        reg_anom,
        trend_start,
        trend_end
    )

    year = reg_anom.time.dt.year

    # -----------------------------
    # Left column: original anomaly with trend
    # -----------------------------
    axes[i, 0].plot(
        year,
        reg_anom,
        linewidth=1.3,
        color="black",
        label="Annual anomaly"
    )
    axes[i, 0].plot(
        year,
        trend_line,
        linewidth=1.8,
        color="red",
        label=f"Trend = {slope_decade:.2f} degC/decade"
    )

    axes[i, 0].axhline(0, color="gray", linewidth=0.8)
    axes[i, 0].set_title(f"({chr(97 + 2*i)}) {name}: Anomaly", loc="left")
    axes[i, 0].set_ylabel("Temperature anomaly (degC)")
    axes[i, 0].legend(loc="upper left", fontsize=8, frameon=False)

    # -----------------------------
    # Right column: detrended anomaly
    # -----------------------------
    axes[i, 1].plot(
        year,
        reg_detrended,
        linewidth=1.3,
        color="black"
    )

    axes[i, 1].axhline(0, color="gray", linewidth=0.8)
    axes[i, 1].set_title(
        f"({chr(98 + 2*i)}) {name}: Detrended Anomaly",
        loc="left"
    )

    # Mark the period used to estimate and remove the linear trend
    trend_start_year = int(trend_start[:4])
    trend_end_year = int(trend_end[:4])
    for j in range(2):
        axes[i, j].axvspan(
            trend_start_year, trend_end_year,
            color="gray",
            alpha=0.08,
            zorder=0
        )

    # Same y-axis range within each row
    row_min = min(float(reg_anom.min()), float(reg_detrended.min()))
    row_max = max(float(reg_anom.max()), float(reg_detrended.max()))
    row_abs = max(abs(row_min), abs(row_max))
    row_lim = np.ceil(row_abs * 2) / 2
    axes[i, 0].set_ylim(-row_lim, row_lim)
    axes[i, 1].set_ylim(-row_lim, row_lim)

    # Grid and minor ticks
    for j in range(2):
        axes[i, j].yaxis.set_minor_locator(MultipleLocator(0.5))
        axes[i, j].grid(True, which="major", linestyle="-", alpha=0.6)
        axes[i, j].grid(True, which="minor", linestyle="--", alpha=0.3)


# X-axis settings
for ax in axes[-1, :]:
    ax.set_xlabel("Year")

axes[-1, 0].set_xlim(1948, 2025)
axes[-1, 0].set_xticks(np.arange(1950, 2030, 10))

plt.suptitle(
    "Regional 2-m Air Temperature: Anomaly vs. Detrended Anomaly",
    fontsize=14
)
plt.tight_layout()

trend_label = f"{trend_start[:4]}_{trend_end[:4]}"

output_path = Path(__file__).with_name(
    f"{Path(__file__).stem}_{trend_label}.jpg"
)

plt.savefig(output_path, dpi=300, bbox_inches="tight")
plt.show()

ds.close()
