# ---------------------------------------------------------
# SST Trends in the Northern and Southern Hemispheres
# ---------------------------------------------------------
#
# This program examines long-term sea surface temperature (SST)
# trends in the Northern and Southern Hemispheres using polar
# stereographic map projections.
#
# Polar projections are useful for visualizing high-latitude
# climate change because they reduce distortion near the poles
# and emphasize spatial differences in ocean warming.
#
# In this exercise, you will examine SST trends in the polar
# regions and compare their spatial patterns between hemispheres.
#
# Tasks:
#
# 1. Read the SST variable from the HadISST dataset.
# 2. Mask SST values colder than -2.1°C.
# 3. Select SST data for the 1982-2025 analysis period.
# 4. Calculate annual SST anomalies relative to the
#    1991-2020 monthly climatology.
# 5. Add a cyclic longitude point to remove the map seam.
# 6. Calculate the linear SST trend in °C per decade.
# 7. Display the trends using North and South Polar
#    Stereographic projections.
# 8. Plot the SST trend using filled contours.
#
# ---------------------------------------------------------

from pathlib import Path
from cartopy.util import add_cyclic_point

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import sys

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
# Read monthly SST
# ---------------------------------------------------------
script_dir = Path(__file__).resolve().parent

# Check whether the script is inside the "solution" directory
if script_dir.name == "solution":
    # Move up two directory levels to reach the repository root
    repo_dir = script_dir.parents[2]
else:
    # Move up two directory levels to reach the repository root
    repo_dir = script_dir.parents[1]

sst_file = repo_dir / "data_raw" / "HadISST_sst.nc"

ds_sst = xr.open_dataset(sst_file)

# Task 1:
# Read the SST variable from the dataset.
if "sst" in ds_sst.data_vars:
    sst = ds_sst["sst"]
elif "SST" in ds_sst.data_vars:
    sst = ds_sst["SST"]
else:
    raise KeyError(
        "SST variable not found. "
        "Check the variable name in the NetCDF file.")

# Rename coordinates if necessary
if "latitude" in sst.coords:
    sst = sst.rename({"latitude": "lat"})

if "longitude" in sst.coords:
    sst = sst.rename({"longitude": "lon"})

# ---------------------------------------------------------
# Mask extreme SST values
# ---------------------------------------------------------

# Task 2:
# Keep SST values warmer than -2.1°C.
sst = sst.where(sst > -2.1)

# ---------------------------------------------------------
# Select analysis period
# ---------------------------------------------------------

start_year = 1982
end_year = 2025

clim_start = "1991-01-01"
clim_end = "2020-12-31"

trend_start = "1982-01-01"
trend_end = "2025-12-31"

# Task 3:
# Select SST data from start_year through end_year.
sst = sst.sel(time=slice(f"{start_year}-01-01", f"{end_year}-12-31"))


# ---------------------------------------------------------
# Calculate annual mean SST
# ---------------------------------------------------------

# Task 4:
# Use calc_seasonal_anom() to calculate 12-month mean anomalies.
# Use December as the ending month and the 1991-2020 climatology.
sst_anom = calc_seasonal_anom(sst, window=12, end_month=12, clim_period=[clim_start, clim_end])


# ---------------------------------------------------------
# Calculate linear SST trend
# ---------------------------------------------------------

_, trend_line, slope_decade = linear_detrend(
    sst_anom,
    trend_period=[trend_start, trend_end],
    return_trend=True
)

# SST trend is already in °C/decade
sst_trend = slope_decade

sst_trend.attrs["units"] = "°C decade^-1"
sst_trend.name = "SST trend"


# ---------------------------------------------------------
# Add cyclic longitude point
# ---------------------------------------------------------

# Task 5:
# Add a cyclic longitude point to remove the 0°/360° seam.
sst_trend_cyclic, lon_cyclic = add_cyclic_point(
    sst_trend.values,
    coord=sst_trend["lon"].values)


# ---------------------------------------------------------
# Create Northern and Southern Hemisphere projections
# ---------------------------------------------------------

fig, axs = plt.subplots( 1, 2, figsize=(10, 6))

# Replace the default axes with Cartopy projection axes
for ax in axs:
    ax.remove()

# Task 7:
# Create North and South Polar Stereographic projections.
axs[0] = fig.add_subplot(
    1, 2, 1,
    projection=ccrs.NorthPolarStereo())

axs[1] = fig.add_subplot(
    1, 2, 2,
    projection=ccrs.SouthPolarStereo())


# ---------------------------------------------------------
# Circular map boundary
# ---------------------------------------------------------

theta = np.linspace(0, 2 * np.pi, 100)
center = [0.5, 0.5]
radius = 0.5

circle = mpath.Path(
    np.vstack([
        np.sin(theta) * radius + center[0],
        np.cos(theta) * radius + center[1]
    ]).T)


# ---------------------------------------------------------
# Plot settings
# ---------------------------------------------------------

# Common trend range for direct hemispheric comparison.
# Filled contour levels
levels = [
    -1.,-0.5,-0.2,-0.1,-0.05,-0.02,  
     0.0,
     0.02,  0.05, 0.1, 0.2, 0.5, 1.]

# Contour lines are less dense than the filled shading.
contour_levels = [-0.1, -0.05, 0.0, 0.05, 0.1]

extents = [
    [-180, 180, 20, 90],
    [-180, 180, -90, -20]]

titles = [
    "Northern Hemisphere",
    "Southern Hemisphere"]

lat_gridlines = [
    [50, 60, 70, 80],
    [-80, -70, -60, -50]]

# ------------------------------------------------------------
# Plot Northern and Southern Hemispheres
# ------------------------------------------------------------

for i, ax in enumerate(axs):

    # Set map extent
    ax.set_extent(
        extents[i],
        crs=ccrs.PlateCarree())

    # Circular map boundary
    ax.set_boundary(
        circle,
        transform=ax.transAxes)

    # Task 8:
    # Plot filled SST trend contours.
    cf = ax.contourf(
        lon_cyclic,
        sst_trend["lat"],
        sst_trend_cyclic,
        levels=levels,
        cmap="seismic",
        extend="both",
        transform=ccrs.PlateCarree())

    # Contour lines
    cs = ax.contour(
        lon_cyclic,
        sst_trend["lat"],
        sst_trend_cyclic,
        levels=levels,
        colors="black",
        linewidths=0.5,
        transform=ccrs.PlateCarree())

    # -----------------------------------------------------
    # Mask outer region only for contour-label placement
    # -----------------------------------------------------

    lat = sst_trend["lat"].values

    if i == 0:

        # Northern Hemisphere:
        # place labels poleward of 68°N
        sst_label = np.where(
            lat[:, np.newaxis] >= 68,
            sst_trend_cyclic,
            np.nan)

    else:

        # Southern Hemisphere:
        # place labels poleward of 68°S
        sst_label = np.where(
            lat[:, np.newaxis] <= -68,
            sst_trend_cyclic,
            np.nan)

    # Invisible contours used only for label placement
    cs_label = ax.contour(
        lon_cyclic,
        sst_trend["lat"],
        sst_label,
        levels=contour_levels,
        colors="black",
        linewidths=0,
        transform=ccrs.PlateCarree())

    # Add contour labels
    ax.clabel(
        cs_label,
        inline=True,
        fontsize=7,
        fmt="%.1f",
        colors="black")

    # Add land
    ax.add_feature(
        cfeature.LAND,
        facecolor="lightgray",
        zorder=2)

    # Add coastlines
    ax.coastlines(
        resolution="110m",
        linewidth=0.8,
        zorder=3)

    # Add country borders
    ax.add_feature(
        cfeature.BORDERS,
        linewidth=0.3,
        zorder=3)

    # Gridlines
    gl = ax.gridlines(
        crs=ccrs.PlateCarree(),
        linewidth=0.5,
        linestyle="--",
        alpha=0.6)

    gl.ylocator = plt.FixedLocator(
        lat_gridlines[i])

    # Panel title
    ax.set_title(
        titles[i],
        fontsize=13,
        pad=10)

# ------------------------------------------------------------
# Shared colorbar
# ------------------------------------------------------------

cbar = fig.colorbar(
    cf,
    ax=axs,
    orientation="horizontal",
    pad=0.08,
    shrink=0.8)

cbar.set_label(
    "SST Trend (°C decade$^{-1}$)")

fig.suptitle(
    f"SST Trend ({trend_start[:4]}-{trend_end[:4]})",
    fontsize=16, y=0.98)

# ---------------------------------------------------------
# Save figure
# ---------------------------------------------------------

output_path = Path(__file__).with_suffix(".jpg")

plt.savefig( output_path, dpi=300, bbox_inches="tight")

plt.show()
