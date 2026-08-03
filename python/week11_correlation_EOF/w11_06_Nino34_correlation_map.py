# -------------------------------------------------------------
# Global SST Correlation Map with the Niño 3.4 Index
# -------------------------------------------------------------
# 
# Create a global correlation map between annual Niño 3.4 SST anomalies
# and annual SST anomalies at each grid point.
#
# The program calculates annual SST anomalies, computes the Niño 3.4
# index, evaluates the Pearson correlation coefficient at every grid
# point, and visualizes the global teleconnection pattern.
#
# -------------------------------------------------------------

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pathlib import Path
from cartopy.util import add_cyclic_point
import sys

import warnings
warnings.filterwarnings(
    "ignore",
    message="invalid value encountered in create_collection",
    category=RuntimeWarning
)

def regional_weighted_mean(data, lat1, lat2, lon1, lon2):
    """Compute a cosine-latitude-weighted regional mean."""

    if "latitude" in data.coords:
        data = data.rename({"latitude": "lat"})
    if "longitude" in data.coords:
        data = data.rename({"longitude": "lon"})

    if (lon1 < 0 or lon2 < 0) and bool((data.lon > 180).any()):
        data = data.assign_coords(
            lon=((data.lon + 180) % 360 - 180)
        ).sortby("lon")
    elif lon1 >= 0 and lon2 >= 0 and bool((data.lon < 0).any()):
        data = data.assign_coords(lon=(data.lon % 360)).sortby("lon")

    if data.lat[0] < data.lat[-1]:
        lat_slice = slice(min(lat1, lat2), max(lat1, lat2))
    else:
        lat_slice = slice(max(lat1, lat2), min(lat1, lat2))

    region = data.sel(
        lat=lat_slice,
        lon=slice(min(lon1, lon2), max(lon1, lon2))
    )

    weights = np.cos(np.deg2rad(region.lat))
    dat_reg_ave = region.weighted(weights).mean(
        dim=["lat", "lon"],
        skipna=True
    )

    return dat_reg_ave

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

# -------------------------------------------------------
# User settings
# -------------------------------------------------------

indir = Path("../../data_raw")
sst_file = indir / "HadISST_sst.nc"

start_year = 1948
end_year = 2025


# Set to False to retain the long-term trend
use_detrended_data = True

# -------------------------------------------------------
# Read SST
# -------------------------------------------------------

ds_sst = xr.open_dataset(sst_file)
sst = ds_sst["sst"]

sst = sst.where((sst != -1000) & (sst != -1.0e30))

if "latitude" in sst.coords:
    sst = sst.rename({"latitude": "lat"})
if "longitude" in sst.coords:
    sst = sst.rename({"longitude": "lon"})

if bool((sst.lon > 180).any()):
    sst = sst.assign_coords(
        lon=((sst.lon + 180) % 360 - 180)
    ).sortby("lon")


# -------------------------------------------------------
# Annual mean anomalies
# -------------------------------------------------------

# pick up DJF SST anomaly
sst_djf_anom = calc_seasonal_anom(sst,window=3,end_month=2)
print(sst_djf_anom.coords)
sst_djf_anom = sst_djf_anom.sel(year=slice(start_year, end_year))
print(sst_djf_anom.coords)

# -------------------------------------------------------
# Niño 3.4 index
# -------------------------------------------------------

# Niño 3.4: 5°N-5°S, 170°W-120°W
nino_lat1, nino_lat2 = 5, -5
nino_lon1, nino_lon2 = -170, -120

nino34 = regional_weighted_mean(
    sst_djf_anom,
    nino_lat1,
    nino_lat2,
    nino_lon1,
    nino_lon2
)


# -------------------------------------------------------
# Optional detrending
# -------------------------------------------------------

if use_detrended_data:
    sst_for_corr = linear_detrend(sst_djf_anom)
    nino34_for_corr = linear_detrend(nino34)
    analysis_label = "Detrended"
else:
    sst_for_corr = sst_djf_anom
    nino34_for_corr = nino34
    analysis_label = "Annual Anomaly"


# -------------------------------------------------------
# Match common years
# -------------------------------------------------------

common_years = np.intersect1d(
    sst_for_corr.year,
    nino34_for_corr.year
)

sst_for_corr = sst_for_corr.sel(year=common_years)
nino34_for_corr = nino34_for_corr.sel(year=common_years)


# -------------------------------------------------------
# Grid-point correlation
# -------------------------------------------------------

corr_map = xr.corr(
    sst_for_corr,
    nino34_for_corr,
    dim="year"
)

# Add a cyclic longitude point to remove the seam at 180°
corr_cyclic, lon_cyclic = add_cyclic_point(
    corr_map.values,
    coord=corr_map.lon.values
)

# -------------------------------------------------------
# Create figure
# -------------------------------------------------------

fig = plt.figure(figsize=(11, 8), constrained_layout=True)
grid = fig.add_gridspec(2, 1, height_ratios=[1, 2])

# -------------------------------------------------------
# Niño 3.4 time series (positive = red, negative = blue)
# -------------------------------------------------------

years = nino34_for_corr.year.values
values = nino34_for_corr.values

colors = np.where(values >= 0, "red", "blue")

# Niño 3.4 time series
ax0 = fig.add_subplot(grid[0, 0])

ax0.bar(
    years,
    values,
    color=colors,
    width=0.6,
)

ax0.axhline(
    0,
    color="black",
    linewidth=1.0,
)

ax0.set_xlabel("Year")
ax0.set_ylabel("SST Anomaly (°C)")
ax0.set_title(f"Niño 3.4 {analysis_label} index")
ax0.grid(
    axis="y",
    alpha=0.3,
)


# Correlation map
projection = ccrs.Robinson(central_longitude=180)
ax1 = fig.add_subplot(grid[1, 0], projection=projection)

levels = np.arange(-0.9, 0.91, 0.1)

cf = ax1.contourf(
    lon_cyclic,
    corr_map.lat,
    corr_cyclic,
    levels=levels,
    cmap="RdBu_r",
    extend="both",
    transform=ccrs.PlateCarree()
)

ax1.add_feature(cfeature.LAND, facecolor="lightgray", zorder=2)
ax1.coastlines(linewidth=0.8, zorder=3)
ax1.add_feature(cfeature.BORDERS, linewidth=0.4, zorder=3)
# Draw latitude and longitude lines
ax1.gridlines(draw_labels=True, linewidth=1, color='gray', alpha=0.5, linestyle='--')
ax1.set_global()

# Draw Niño 3.4 box
box_lon = [nino_lon1, nino_lon2, nino_lon2, nino_lon1, nino_lon1]
box_lat = [nino_lat1, nino_lat1, nino_lat2, nino_lat2, nino_lat1]

ax1.plot(
    box_lon,
    box_lat,
    color="black",
    linewidth=1.5,
    transform=ccrs.PlateCarree()
)

ax1.set_title(
    f"Correlation of Global SST with Niño 3.4 {analysis_label}"
)

cbar = fig.colorbar(
    cf,
    ax=ax1,
    orientation="horizontal",
    pad=0.06,
    shrink=0.85
)
cbar.set_label("Pearson Correlation Coefficient (r)")

output_path = Path(__file__).with_suffix(".jpg")
plt.savefig(output_path, dpi=300, bbox_inches="tight")
plt.show()
