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
import sys

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
    # Move up two directory levels to reach the repository root
    repo_dir = script_dir.parents[2]
else:
    # Move up two directory levels to reach the repository root
    repo_dir = script_dir.parents[1]

filein = repo_dir / "data" / "air.2m.mon.mean.nc"

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
#trend_start = "1981-01-01"
trend_start = "1949-01-01"
trend_end = "2020-12-31"

# Annual anomaly
air_anom = calc_seasonal_anom(air, clim_period=[clim_start, clim_end])

year = air_anom.year


# ---------------------------------------------------------
# Plot three regions: anomaly vs. detrended anomaly
# ---------------------------------------------------------
fig, axes = plt.subplots(
    3, 2,
    figsize=(12, 8),
    sharex=True,
    sharey="row"
)

regions = [
    ("North America", 75, 15, 190, 310),
    ("Tropical Pacific", 20, -20, 120, 280),
    ("Arctic", 90, 60, 0, 360),
]

for i, (name, lat1, lat2, lon1, lon2) in enumerate(regions):

    # Regional anomaly
    reg_anom = regional_weighted_mean(air_anom, lat1, lat2, lon1, lon2)

    # Detrended annual anomaly
    reg_anom_detrended, trend_line, slope_decade  = linear_detrend(
        reg_anom, trend_period=[trend_start,trend_end], return_trend=True)

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
        reg_anom_detrended,
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
    row_min = min(float(reg_anom.min()), float(reg_anom_detrended.min()))
    row_max = max(float(reg_anom.max()), float(reg_anom_detrended.max()))
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
