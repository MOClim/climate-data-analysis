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
# Step 1: Calculate DJF SLP anomalies.
#
clim_start = "1991-01-01"
clim_end = "2020-12-31"

# Complete the function call.
# Calculate DJF mean anomalies from monthly anomalies.
slp_anom = calc_seasonal_anom(slp, window=, end_month=, clim_period=[clim_start, clim_end])

# Convert longitude to -180° to 180°
slp_anom = slp_anom.assign_coords(lon=(slp_anom.lon + 180) % 360 - 180).sortby("lon")

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
    slp_analysis = linear_detrend(slp_anom, min_coverage=0.9)
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
# Step 2: Compute the first three EOF modes.
#
# Empirical Orthogonal Function (EOF) analysis identifies
# the dominant spatial patterns of climate variability.
#
# The function returns:
#   pcs              : Principal component time series
#   eofs             : Spatial patterns of variability
#   variance_percent : Percentage of variance explained
#                      by each EOF mode
#
# Complete the function call below.
#
# Hints:
#   1. Use the detrended DJF SLP anomaly data prepared above.
#   2. Set neval to the number of EOF modes to calculate.
#   3. latlonEOF specifies the North Atlantic analysis region.
#   4. normalize controls whether the input data are
#      standardized at each grid point.
#
pcs, eofs, variance_percent = compute_eof_analysis(
    ,                     # Input SLP anomaly data
    latlonEOF=latlonEOF,  # North Atlantic EOF domain
    neval=,               # Number of EOF modes
    normalize=normalize_eof,
    min_coverage=0.9)

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
# Calculate global DJF SLP correlation maps 
# -------------------------------------------------------------
#
# Step 3: Calculate correlation maps for PC1, PC2, and PC3.
#
# Pearson correlation measures the linear relationship
# between each PC and DJF SLP anomalies at each grid point.
#
# Complete the function call below.
#
# Hints:
#   1. Use the global DJF SLP anomaly data.
#   2. Use the principal components calculated in Task 2.
#   3. min_coverage=0.9 requires at least 90% valid data.
#
cor_map = correlation_with_pcs(
    ,         # Global DJF SLP anomalies
    ,         # Principal components
    min_coverage=0.9)


# ---------------------------------------------------------
# Display variance explained by each EOF mode
# ---------------------------------------------------------

print(f"Analysis period: "
    f"{int(slp_analysis.year.values[0])}-"
    f"{int(slp_analysis.year.values[-1])}")

for mode, value in enumerate(variance_percent,start=1):
    print(f"EOF{mode} variance explained: "
        f"{value:.2f}%")

# ---------------------------------------------------------
# Create figure
# ---------------------------------------------------------
# Create a figure with different-sized panels:
# Top row: PC time series
# Bottom row: Correlation maps
#
# Panel position and size controls

fig, axes = plt.subplots(
    2, 3, figsize=(11, 5),
    gridspec_kw={"height_ratios": [0.8, 2]},
    constrained_layout=False, squeeze=False)
fig.subplots_adjust(top=0.88)

print(axes.shape)

# Replace the upper Matplotlib Axes with Cartopy GeoAxes
axes[1, 0].remove()
axes[1, 1].remove()
axes[1, 2].remove()

proj = ccrs.PlateCarree(central_longitude=-30)
axes[1, 0] = fig.add_subplot(2, 3, 4, projection=proj)
axes[1, 1] = fig.add_subplot(2, 3, 5, projection=proj)
axes[1, 2] = fig.add_subplot(2, 3, 6, projection=proj)

# ---------------------------------------------------------
# Plot PC time series (upper row)
# ---------------------------------------------------------

years = pc1.year.values

# Set bar colors based on positive and negative PC values
colors1 = np.where(pc1.values >= 0, "red", "blue")
colors2 = np.where(pc2.values >= 0, "red", "blue")
colors3 = np.where(pc3.values >= 0, "red", "blue")

# PC1 time series
axes[0, 0].bar(years, pc1.values, color=colors1, width=0.8)

# PC2 time series
axes[0, 1].bar(years, pc2.values, color=colors2, width=0.8)

# PC3 time series
axes[0, 2].bar(years, pc3.values, color=colors3, width=0.8)

for mode in range(3):

  # Add zero reference lines
  axes[0, mode].axhline(0, color="black", linewidth=0.8)

  # Set axis limits
  axes[0, mode].set_xlim(start_year - 1, end_year + 1)

  axes[0, mode].set_ylim(-3, 3)

  # Axis labels
  axes[0, mode].set_xlabel("Year")

  # Gridlines
  axes[0, mode].grid(axis="y", alpha=0.3)

axes[0, 0].set_ylabel("Standardized PC")

# Titles
axes[0, 0].set_title("PC1")
axes[0, 1].set_title("PC2")
axes[0, 2].set_title("PC3")

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

levels = np.linspace(-0.8, 0.8, 9)

# Select the first three EOF modes
dat1 = eof_map.isel(mode=0)
dat2 = eof_map.isel(mode=1)
dat3 = eof_map.isel(mode=2)

dat1.plot.contourf(
   ax=axes[1, 0],
   transform=ccrs.PlateCarree(),
   levels=levels,
   cmap="RdBu_r",
   extend="both",
   add_colorbar=False
)

dat2.plot.contourf(
   ax=axes[1, 1],
   transform=ccrs.PlateCarree(),
   levels=levels,
   cmap="RdBu_r",
   extend="both",
   add_colorbar=False
)

dat3.plot.contourf(
   ax=axes[1, 2],
   transform=ccrs.PlateCarree(),
   levels=levels,
   cmap="RdBu_r",
   extend="both",
   add_colorbar=False
)

# Add map features
for mode in range(3):
    # Move the three maps upward
    pos = axes[1, mode].get_position()
    axes[1, mode].set_position([
        pos.x0 - pos.width * 0.1, pos.y0 - 0.02,
        pos.width * 1.3, pos.height * 1.3])
    axes[1, mode].set_extent([-90, 40, 20, 80], crs=ccrs.PlateCarree())
    #axes[1, mode].add_feature(
    #    cfeature.LAND, facecolor="lightgray", zorder=2)
    axes[1, mode].coastlines(linewidth=0.8)
    axes[1, mode].gridlines(
        linewidth=0.5, color="gray",
        alpha=0.5, linestyle="--"
    )

# Map titles
axes[1, 0].set_title(f"PC1 Correlation ({float(var1):.1f}%)")
axes[1, 1].set_title(f"PC2 Correlation ({float(var2):.1f}%)")
axes[1, 2].set_title(f"PC3 Correlation ({float(var3):.1f}%)")


# Shared horizontal colorbar
cbar = fig.colorbar(
    axes[1, 0].collections[0],
    ax=axes[1, :],
    orientation="horizontal", pad=0.12, shrink=0.5)

cbar.set_label("Correlation Coefficient")

# ---------------------------------------------------------
# ---------------------------------------------------------

fig.suptitle(
    f"Leading North Atlantic DJF SLP EOF Modes "
    f"({analysis_label})",
    fontsize=16, y=0.98)

# ---------------------------------------------------------
# Save figure
# ---------------------------------------------------------

output_path = Path(__file__).with_suffix(".jpg")

plt.savefig(output_path, dpi=300)
plt.show()
