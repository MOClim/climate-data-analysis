# ---------------------------------------------------------
# Multiple EOF Modes of Tropical Pacific DJF SST
# ---------------------------------------------------------
#
# This program introduces Empirical Orthogonal Function (EOF)
# analysis using DJF Tropical Pacific SST anomalies.
#
# EOF analysis identifies the dominant spatial patterns of
# climate variability and their corresponding time evolution.
#
# In this example, we:
#
# 1. Calculate DJF SST anomalies.
# 2. Remove the long-term linear trend.
# 3. Compute the first three EOF modes.
# 4. Plot the principal component (PC) time series.
# 5. Plot the corresponding EOF spatial patterns.
# 6. Compare the variance explained by each EOF mode.
#

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
    """Calculate latitude-weighted EOFs and standardized PCs."""

    # Ensure longitude is 0–360 and sorted
    if float(datA.lon.min()) < 0:
        datA = datA.assign_coords(
            lon=(datA.lon % 360)
        ).sortby("lon")

    lat_min, lat_max, lon_min, lon_max = latlonEOF

    lon_min = lon_min if lon_min >= 0 else lon_min + 360
    lon_max = lon_max if lon_max >= 0 else lon_max + 360

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

    datY = datY.transpose(
        "year",
        "lat",
        "lon",
    )

    datY = datY.rename(
        {"year": "time"}
    )

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

# Tropical Pacific EOF domain
lat1, lat2 = -20.0, 20.0
lon1, lon2 = 120.0, 280.0
latlonEOF = (lat1, lat2, lon1, lon2)

# Number of EOF modes to calculate and plot
n_modes = 3

# Set False to retain the long-term linear trend.
use_detrended_data = True

# False: covariance-based EOF
# True: correlation-based EOF
normalize_eof = False

# ---------------------------------------------------------
# Read SST and precipitation 
# ---------------------------------------------------------

script_dir = Path(__file__).resolve().parent

# Check whether the script is inside the "solution" directory
if script_dir.name == "solution":
    repo_dir = script_dir.parents[2]
else:
    repo_dir = script_dir.parents[1]

sst_file = repo_dir / "data_raw" / "HadISST_sst.nc"

ds_sst = xr.open_dataset(sst_file)
sst = ds_sst["sst"]

sst = sst.where(
    (sst != -1000) &
    (sst != -1.0e30)
)

if "latitude" in sst.coords:
    sst = sst.rename({"latitude": "lat"})

if "longitude" in sst.coords:
    sst = sst.rename({"longitude": "lon"})

if bool((sst.lon < 0).any()):
    sst = sst.assign_coords(
        lon=(sst.lon % 360)
    ).sortby("lon")


prc_file = repo_dir / "data_raw" / "prate.mon.mean.nc"
ds_prc = xr.open_dataset(prc_file)
prc = ds_prc["prate"]

# ---------------------------------------------------------
# Annual mean anomalies
# ---------------------------------------------------------

sst_anom = calc_seasonal_anom(sst,window=3,end_month=2)
sst_anom = sst_anom.sel(year=slice(start_year, end_year))

prc_anom = calc_seasonal_anom(prc,window=3,end_month=2)
prc_anom = prc_anom.sel(year=slice(start_year, end_year))

# ---------------------------------------------------------
# Select the Tropical Pacific
# ---------------------------------------------------------

if sst_anom.lat[0] < sst_anom.lat[-1]:
    lat_slice = slice(lat1, lat2)
else:
    lat_slice = slice(lat2, lat1)

# Global Precipitation anomalies
prc_global = prc_anom

# Tropical Pacific data used for EOF calculation
sst_tp = sst_anom.sel(
    lat=lat_slice,
    lon=slice(lon1, lon2),
)

# ---------------------------------------------------------
# Optional detrending
# ---------------------------------------------------------

if use_detrended_data:
    sst_analysis = linear_detrend(
        sst_tp,
        min_coverage=0.9,
    )

    prc_global_analysis = linear_detrend(
        prc_global,
        min_coverage=0.9,
    )

    analysis_label = "Detrended"
else:
    sst_analysis = sst_tp
    prc_global_analysis = prc_global
    analysis_label = "Annual Anomaly"

# -------------------------------------------------------------
# EOF analysis over the Tropical Pacific: first three modes
# -------------------------------------------------------------

pcs, eofs, variance_percent = compute_eof_analysis(
    sst_analysis,
    latlonEOF=latlonEOF,
    neval=3,
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
# Calculate the correlation of the global precipitation anomalies onto standardized PC1
# -------------------------------------------------------------

cor_map = correlation_with_pcs(
    prc_global_analysis,
    pcs,
    min_coverage=0.9,
)


# ---------------------------------------------------------
# Display variance explained by each EOF mode
# ---------------------------------------------------------

print(
    f"Analysis period: "
    f"{int(sst_analysis.year.values[0])}-"
    f"{int(sst_analysis.year.values[-1])}"
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

projection = ccrs.Robinson(
    central_longitude=180
)

levels = np.linspace(-0.8, 0.8, 9)


# ---------------------------------------------------------
# Plot EOF maps on the upper row
# ---------------------------------------------------------
#
# Each EOF map represents one dominant spatial mode of
# SST variability.
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

    pos_map = ax_map.get_position()

    new_width = pos_map.width * map_width_scale
    new_height = pos_map.height * map_height_scale

    new_x = pos_map.x0 + (pos_map.width - new_width) / 2
    new_y = pos_map.y0 + (pos_map.height - new_height) / 2 + map_y_shift

    ax_map.set_position([
      new_x,
      new_y,
      new_width,
      new_height,
     ])

    cdat = cor_map.isel(mode=mode)

    cf = ax_map.contourf(
        cdat.lon,
        cdat.lat,
        cdat,
        levels=levels,
        cmap="BrBG",
        extend="both",
        transform=ccrs.PlateCarree(),
        zorder=1,
    )

    ax_map.set_global()

    ax_map.add_feature(
        cfeature.LAND,
        facecolor="none",
        edgecolor="none",
        zorder=2,
    )

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
        f"Correlation of SST with PC{mode + 1}"
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
    f"Leading Tropical Pacific DJF SST EOF Modes "
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
