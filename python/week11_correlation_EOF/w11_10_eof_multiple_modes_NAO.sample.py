# ---------------------------------------------------------
# Leading EOF Modes of North Atlantic DJF SLP
# ---------------------------------------------------------
#
# This example demonstrates how Empirical Orthogonal
# Function (EOF) analysis can be used to identify the
# dominant patterns of winter (DJF) sea-level pressure
# variability over the North Atlantic.
#
# Complete the following tasks:
#
# 1. Calculate DJF SLP anomalies using
#    calc_seasonal_anom().
#
# 2. Compute the first three EOF modes using
#    compute_eof_analysis().
#
# 3. Calculate the correlation maps between the
#    principal components and the global DJF SLP
#    anomalies using correlation_with_pcs().
#
# ---------------------------------------------------------

from pathlib import Path

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from eofs.xarray import Eof
import sys

import warnings
warnings.filterwarnings(
    "ignore",
    message="invalid value encountered in create_collection",
    category=RuntimeWarning,
)

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

    # Remove seasonal means that are entirely missing
    valid_time = dat_tmp.notnull().any(dim=["lat", "lon"])

    dat_tmp = dat_tmp.where(valid_time,drop=True)

    # Extract year after removing incomplete seasons
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

def compute_eof_analysis(
    datA,
    latlonEOF=(30.0, 50.0, -125.0, -100.0),
    neval=3,
    normalize=False,
    min_coverage=0.9,
):

    lat_min, lat_max, lon_min, lon_max = latlonEOF

    # Ensure latitude increases from south to north
    if datA["lat"][0] > datA["lat"][-1]:
        datA = datA.isel(lat=slice(None, None, -1))

    # Subset the EOF domain
    datA_eof = datA.sel(
        lat=slice(lat_min, lat_max),
        lon=slice(lon_min, lon_max),
    )

    # Mask grid points with insufficient temporal coverage
    valid_count = datA_eof.notnull().sum(dim="year")
    required_count = int(
        np.ceil(datA_eof.sizes["year"] * min_coverage)
    )

    datY = datA_eof.where(
        valid_count >= required_count
    )

    # Optional gridpoint standardization
    if normalize:
        dat_std = datY.std(dim="year")
        datY = datY / dat_std

    datY = datY.transpose("year","lat","lon").rename({"year": "time"})

    # Latitude weights
    weights = np.sqrt(np.cos(np.deg2rad(datY.lat.values)))[:, np.newaxis]

    solver = Eof(datY,weights=weights)

    # Calculate multiple EOF modes
    eofs = solver.eofsAsCovariance(neofs=neval,pcscaling=1)
    pcs = solver.pcs(npcs=neval,pcscaling=1)

    variance_percent = (
        solver.varianceFraction(
            neigs=neval
        ) * 100
    )

    pcs = pcs.rename(
        {"time": "year"}
    )

    for mode, value in enumerate(
        variance_percent.values,
        start=1,
    ):
        print(
            f"EOF{mode} variance explained: "
            f"{value:.1f}%"
        )

    return pcs, eofs, variance_percent

def correlation_with_pcs(dat, pcs, min_coverage=0.9):
    """
    Calculate Pearson correlation maps between a climate field
    and all principal-component modes.

    Parameters
    ----------
    dat : xr.DataArray
        Climate field with dimensions (year, lat, lon).
    pcs : xr.DataArray
        Principal components with dimensions (year, mode).
    min_coverage : float
        Minimum fraction of valid years required at each grid point.

    Returns
    -------
    corr : xr.DataArray
        Correlation maps with dimensions (mode, lat, lon).
    """

    # Match the years shared by the field and PCs
    dat, pcs = xr.align(
        dat,
        pcs,
        join="inner",
    )

    # Require sufficient temporal coverage at each grid point
    valid_counts = dat.notnull().sum(dim="year")
    required_count = int(
        np.ceil(dat.sizes["year"] * min_coverage)
    )

    dat_masked = dat.where(
        valid_counts >= required_count
    )

    # xarray broadcasts the mode dimension automatically
    corr = xr.corr(
        dat_masked,
        pcs,
        dim="year",
    )

    # Arrange dimensions consistently
    corr = corr.transpose(
        "mode",
        "lat",
        "lon",
    )

    corr.name = "correlation"

    return corr

# ---------------------------------------------------------
# User settings
# ---------------------------------------------------------

start_year = 1948
end_year = 2025

# North Atlantic EOF domain
lat1, lat2 = 20.0, 80.0
lon1, lon2 = -90.0, 40.0
latlonEOF = (lat1, lat2, lon1, lon2)

# Number of EOF modes to calculate and plot
n_modes = 3

# Set False to retain the long-term linear trend.
use_detrended_data = True

# False: covariance-based EOF
# True: correlation-based EOF
normalize_eof = False

# ---------------------------------------------------------
# Read SLP
# ---------------------------------------------------------

indir = Path("../../data")
slp_file = indir / "slp.mon.mean.nc"

ds_slp = xr.open_dataset(slp_file)

slp = ds_slp["slp"]


# ---------------------------------------------------------
# Calculate monthly and annual mean anomalies
# ---------------------------------------------------------
#
# Task 1
# Calculate DJF SLP anomalies.

clim_start = "1991-01-01"
clim_end = "2020-12-31"

# Complete the function call.
# Calculate DJF mean anomalies from monthly anomalies.
slp_anom = calc_seasonal_anom(slp, window=, end_month=, clim_period=[clim_start, clim_end])

# Convert longitude to -180° to 180°
slp_anom = slp_anom.assign_coords(lon=((slp_anom.lon + 180) % 360 - 180)).sortby("lon")

# Global SLP anomalies
slp_global = slp_anom

# ---------------------------------------------------------
# Calculate regional area-weighted means
# ---------------------------------------------------------
# North Atlantic EOF domain
lat_str, lat_end = 80.0, 20.0
lon_str, lon_end = -90.0, 40.0

slp_anom_NA = regional_weighted_mean(slp_anom, lat_str, lat_end, lon_str, lon_end)

# Convert year coordinates to datetime for plotting
slp_time = np.array([np.datetime64(f"{y}-01-01") for y in slp_anom_NA.year.values])

# ---------------------------------------------------------
# Optional detrending
# ---------------------------------------------------------

if use_detrended_data:
    slp_analysis = linear_detrend(
        slp_anom,
        min_coverage=0.9,
    )
    slp_global_analysis = slp_global
    analysis_label = "Detrended"
else:
    slp_analysis = slp_anom
    slp_global_analysis = slp_global
    analysis_label = "DJF Anomaly"

# -------------------------------------------------------------
# EOF analysis over the North Atlantic: first three modes
# -------------------------------------------------------------
#
# Task 2
# Compute the first three EOF modes.
#
pcs, eofs, variance_percent = compute_eof_analysis(
    ,
    latlonEOF=latlonEOF,
    neval=,
    normalize=normalize_eof,
    min_coverage=0.9,
)

# Optional sign reversal for EOF1 and PC1
pcs = -pcs
eofs = -eofs

# Separate individual modes
pc1 = pcs.isel(mode=0)
pc2 = pcs.isel(mode=1)
pc3 = pcs.isel(mode=2)

eof1 = eofs.isel(mode=0)
eof2 = eofs.isel(mode=1)
eof3 = eofs.isel(mode=2)

var1 = variance_percent.isel(mode=0)
var2 = variance_percent.isel(mode=1)
var3 = variance_percent.isel(mode=2)

# -------------------------------------------------------------
# Calculate the correlation of the global DJF SLP onto standardized PC1
# -------------------------------------------------------------
#
# Task 3
# Calculate correlation maps between DJF SLP and each PC.
#
cor_map = correlation_with_pcs(
    ,
    ,
    min_coverage=0.9,
)


# ---------------------------------------------------------
# Display variance explained by each EOF mode
# ---------------------------------------------------------

print(
    f"Analysis period: "
    f"{int(slp_analysis.year.values[0])}-"
    f"{int(slp_analysis.year.values[-1])}"
)

for mode, value in enumerate(
    variance_percent,
    start=1,
):
    print(
        f"EOF{mode} variance explained: "
        f"{value:.2f}%"
    )


# ---------------------------------------------------------
# Create figure
# ---------------------------------------------------------

# Panel position and size controls


# PC time-series panels
pc_width_scale = 1.10
pc_height_scale = 0.90
pc_x_shift = 0.00
pc_y_shift = 0.0


fig = plt.figure(figsize=(11, 5))

# Top row: PC time series
# Bottom row: Correlation maps
grid = fig.add_gridspec(
    2,
    n_modes,
    height_ratios=[0.65, 1.35],
    hspace=0.02,      # was 0.15
    wspace=0.25,
)

projection = ccrs.PlateCarree(central_longitude=0)

levels = np.linspace(-0.8, 0.8, 9)


# ---------------------------------------------------------
# Plot EOF maps on the upper row
# ---------------------------------------------------------
#
# Each EOF map represents one dominant spatial mode of
# SLP variability.
#
# Positive and negative values indicate regions that
# vary together with the corresponding principal component.
#
# The percentage in each title indicates the fraction of
# total variance explained by that EOF mode.
#

map_axes = []
cf = None

map_width_scale = 1.10
map_height_scale = 1.15
map_y_shift = 0.0

for mode in range(n_modes):

    ax_map = fig.add_subplot(
        grid[1, mode],
        projection=projection,
    )

    # Store the map axis for the shared colorbar
    map_axes.append(ax_map)

    ax_map.set_extent([-100, 40, 15, 85],crs=ccrs.PlateCarree())

    cdat = cor_map.isel(mode=mode)

    cf = ax_map.contourf(
        cdat.lon,
        cdat.lat,
        cdat,
        levels=levels,
        cmap="RdBu_r",
        extend="both",
        transform=ccrs.PlateCarree(),
        zorder=1,
    )

    ax_map.add_feature(cfeature.LAND,
      facecolor="none",
      edgecolor="none",
      zorder=2)

    ax_map.coastlines(
        linewidth=0.8,
        zorder=3,
    )

    ax_map.add_feature(
        cfeature.BORDERS,
        linewidth=0.4,
        zorder=3,
    )

    ax_map.gridlines(
        linewidth=0.4,
        linestyle="--",
        alpha=0.6,
    )

    ax_map.set_title(
        f"Correlation of DJF SLP with PC{mode + 1}"
        f"({variance_percent.isel(mode=mode).item():.1f}% Variance)",
        fontsize=9,
    )


# ---------------------------------------------------------
# Plot PC time series on the lower row
# ---------------------------------------------------------
#
# Each principal component describes how strongly the
# corresponding EOF spatial pattern varies from year to year.
#
# Red bars indicate positive amplitudes.
# Blue bars indicate negative amplitudes.
#
# Together, the EOF map and its PC time series describe
# one mode of climate variability.
#

for mode in range(n_modes):

    ax_pc = fig.add_subplot(
        grid[0, mode]
    )

    pos_pc = ax_pc.get_position()

    new_pc_width = pos_pc.width * pc_width_scale
    new_pc_height = pos_pc.height * pc_height_scale

    new_pc_x = (
      pos_pc.x0
      + (pos_pc.width - new_pc_width) / 2
      + pc_x_shift)

    new_pc_y = (
      pos_pc.y0
      + (pos_pc.height - new_pc_height) / 2
      + pc_y_shift)

    ax_pc.set_position([
      new_pc_x,
      new_pc_y,
      new_pc_width,
      new_pc_height])

    pc = pcs.isel(
        mode=mode
    )

    pc_values = pc.values
    years = pc.year.values

    bar_colors = np.where(
      pc_values >= 0,
      "red",
      "blue")

    ax_pc.bar(
      years,
      pc_values,
      color=bar_colors,
      width=0.8)

    ax_pc.axhline(
        0,
        color="black",
        linewidth=0.8,
    )

    ax_pc.set_xlim(start_year - 1.,end_year + 1.)
    ax_pc.set_ylim(-4., 4.)

    ax_pc.set_xlabel("Year")

    if mode == 0:
        ax_pc.set_ylabel(
            "Standardized PC"
        )

    ax_pc.set_title(
        f"PC{mode + 1}",
        fontsize=12,
    )

    ax_pc.grid(True)


# ---------------------------------------------------------
# Shared colorbar and figure title
# ---------------------------------------------------------

cbar = fig.colorbar(
    cf,
    ax=map_axes,
    orientation="horizontal",
    pad=0.08,
    shrink=0.6,
)

cbar.ax.tick_params(labelsize=8)
cbar.set_label("Correlation (%)")

fig.suptitle(
    f"Leading North Atlantic DJF SLP EOF Modes "
    f"({analysis_label})",
    fontsize=16,
    y=0.98,
)

# ---------------------------------------------------------
# Save figure
# ---------------------------------------------------------

output_path = Path(__file__).with_suffix(".jpg")

plt.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight",
)

plt.show()
