# ---------------------------------------------------------
# Multiple EOF Modes of Tropical Pacific SST
# ---------------------------------------------------------
#
# This program introduces Empirical Orthogonal Function (EOF)
# analysis using annual Tropical Pacific SST anomalies.
#
# EOF analysis identifies the dominant spatial patterns of
# climate variability and their corresponding time evolution.
#
# In this example, we:
#
# 1. Calculate annual SST anomalies.
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

def calc_eof_analysis(datA, latlonEOF, neval=3, normalize=False):
    """Calculate latitude-weighted EOFs and standardized PCs."""

    # Convert longitude to 0–360 and sort coordinates
    # Ensure latitude is ascending
    datA = datA.assign_coords(lon=datA.lon % 360).sortby("lon")
    datA = datA.sortby("lat")

    # Select the EOF analysis region
    lat1, lat2, lon1, lon2 = latlonEOF
    dat = datA.sel(lat=slice(lat1, lat2),lon=slice(lon1, lon2))

    # Standardize the data for correlation-based EOF analysis
    if normalize:
        dat = dat / dat.std(dim="year")

    # Latitude weighting: sqrt(cos(latitude))
    # Convert 1D latitude weights into a 2D column array (lat, 1).
    weights = np.sqrt(np.cos(np.deg2rad(dat.lat.values)))[:, np.newaxis]

    # Calculate EOFs
    dat = dat.rename({"year": "time"})
    solver = Eof(dat, weights=weights)

    # Extract EOF patterns, standardized PCs, and explained variance
    eofs = solver.eofsAsCovariance(neofs=neval, pcscaling=1)
    pcs = solver.pcs(npcs=neval, pcscaling=1)
    variance_percent = solver.varianceFraction(neigs=neval) * 100

    pcs = pcs.rename({"time": "year"})

    return pcs, eofs, variance_percent

def correlation_with_pcs(dat, pcs):
    """
    Calculate Pearson correlation maps between a climate field
    and all principal-component modes.

    Parameters
    ----------
    dat : xr.DataArray
        Climate field with dimensions (year, lat, lon).
    pcs : xr.DataArray
        Principal components with dimensions (year, mode).

    Returns
    -------
    corr : xr.DataArray
        Correlation maps with dimensions (mode, lat, lon).
    """
    # Match the years shared by the field and PCs
    dat, pcs = xr.align(dat,pcs,join="inner")

    # xarray broadcasts the mode dimension automatically
    corr = xr.corr(dat,pcs,dim="year")

    # Arrange dimensions consistently
    corr = corr.transpose("mode","lat","lon")

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
# Read SST
# ---------------------------------------------------------

indir = Path("../../data_raw")
sst_file = indir / "HadISST_sst.nc"

ds_sst = xr.open_dataset(sst_file)
sst = ds_sst["sst"]

sst = sst.where((sst != -1000) & (sst != -1.0e30))

# Rename coordinates to match the course examples
sst = sst.rename({"latitude": "lat","longitude": "lon"})

# ---------------------------------------------------------
# DJF mean anomalies
# ---------------------------------------------------------

sst_anom = calc_seasonal_anom(sst,window=3,end_month=2)
sst_anom = sst_anom.sel(year=slice(start_year, end_year))

# Optional detrending
if use_detrended_data:
    sst_analysis = linear_detrend(sst_anom, min_coverage=0.9)
    analysis_label = "Detrended"
else:
    sst_analysis = sst_anom
    analysis_label = "Annual Anomaly"

# -------------------------------------------------------------
# EOF analysis over the Tropical Pacific: first three modes
# -------------------------------------------------------------

pcs, eofs, variance_percent = calc_eof_analysis(
    sst_analysis,
    latlonEOF=latlonEOF,
    neval=3,
    normalize=normalize_eof)

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
# Calculate the correlation of the global SST anomalies onto standardized PC1
# -------------------------------------------------------------

eof_map = correlation_with_pcs(sst_analysis, pcs)
print(eof_map)

# Convert longitude from -180–180 to 0–360
eof_map = eof_map.assign_coords(lon=eof_map.lon % 360).sortby("lon")


# ---------------------------------------------------------
# Display variance explained by each EOF mode
# ---------------------------------------------------------

print(f"Analysis period: "
    f"{int(sst_analysis.year.values[0])}-"
    f"{int(sst_analysis.year.values[-1])}")

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

proj = ccrs.Robinson(central_longitude=180)
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
# SST variability.
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
        pos.x0 - pos.width * 0.2, pos.y0 - 0.08,
        pos.width * 1.5, pos.height * 1.5])

    axes[1, mode].set_global()
    axes[1, mode].add_feature(
        cfeature.LAND, facecolor="lightgray", zorder=2
    )
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
    f"Leading Tropical Pacific DJF SST EOF Modes "
    f"({analysis_label})",
    fontsize=16, y=0.98)

# ---------------------------------------------------------
# Save figure
# ---------------------------------------------------------

output_path = Path(__file__).with_suffix(".jpg")

plt.savefig(output_path, dpi=300)
plt.show()
