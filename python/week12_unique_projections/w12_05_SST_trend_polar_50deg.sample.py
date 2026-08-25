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
# 8. Plot the Northern Hemisphere SST trend using filled contours.
# 9. Plot the Southern Hemisphere SST trend using filled contours.
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


def calc_seasonal_anom(dat, window=5, end_month=1, clim_period=None):
    """
    Calculate seasonal mean anomalies using a trailing running mean.
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
    dat_rm = anm.rolling(
        time=window,
        center=False,
        min_periods=window
    ).mean()

    # Select the ending month
    dat_tmp = dat_rm.sel(
        time=dat_rm["time"].dt.month == end_month
    )

    # Extract year
    years = dat_tmp["time"].dt.year

    # Create year-lat-lon DataArray
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

    # Fit linear trend
    coeffs = dat_fit_masked.polyfit(
        dim="year",
        deg=1
    )

    # Evaluate fitted trend
    trend_line = xr.polyval(
        dat_masked["year"],
        coeffs.polyfit_coefficients
    )

    # Convert slope from units/year to units/decade
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

indir = Path("../../data_raw")
sst_file = indir / "HadISST_sst.nc"

ds_sst = xr.open_dataset(sst_file)

# Task 1:
# Read the SST variable from the dataset.
sst = 

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
sst = sst.where() 

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
sst = sst.sel()


# ---------------------------------------------------------
# Calculate annual SST anomalies
# ---------------------------------------------------------

# Task 4:
# Use calc_seasonal_anom() to calculate 12-month mean anomalies.
# Use December as the ending month and the 1991-2020 climatology.
sst_anom = calc_seasonal_anom()


# ---------------------------------------------------------
# Calculate linear SST trend
# ---------------------------------------------------------

# Use linear_detrend() and return the trend information.
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
sst_trend_cyclic, lon_cyclic = add_cyclic_point()


# ---------------------------------------------------------
# Create Northern and Southern Hemisphere projections
# ---------------------------------------------------------

fig = plt.figure(figsize=(14, 7))

# Create a North Polar Stereographic subplot.
ax_nh = fig.add_subplot(
    1, 2, 1,
    projection=ccrs.NorthPolarStereo()
)

# Create a South Polar Stereographic subplot.
ax_sh = fig.add_subplot(
    1, 2, 2,
    projection=ccrs.SouthPolarStereo()
)


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
    ]).T
)


# ---------------------------------------------------------
# Plot settings
# ---------------------------------------------------------

levels = [
    -1.0, -0.5, -0.2, -0.1, -0.05, -0.02,
     0.0,
     0.02, 0.05, 0.1, 0.2, 0.5, 1.0
]

contour_levels = [
    -0.1, -0.05,
     0.0,
     0.05, 0.1
]


# ---------------------------------------------------------
# Northern Hemisphere
# ---------------------------------------------------------

# Zoom to 50°N-90°N.
ax_nh.set_extent(
    [-180, 180, 50, 90],
    crs=ccrs.PlateCarree()
)

ax_nh.set_boundary(
    circle,
    transform=ax_nh.transAxes
)

# Task 8:
# Plot filled SST trend contours.
cf_nh = ax_nh.contourf(
    lon_cyclic,
    sst_trend["lat"],
    sst_trend_cyclic,
    levels=___,
    cmap="seismic",
    extend="both",
    transform=ccrs.PlateCarree()
)

# Draw contour lines
cs_nh = ax_nh.contour(
    lon_cyclic,
    sst_trend["lat"],
    sst_trend_cyclic,
    levels=contour_levels,
    colors="black",
    linewidths=0.4,
    transform=ccrs.PlateCarree()
)

# Restrict contour labels to the inner polar region
lat_nh = sst_trend["lat"].values

sst_label_nh = np.where(
    lat_nh[:, np.newaxis] >= 68,
    sst_trend_cyclic,
    np.nan
)

cs_nh_label = ax_nh.contour(
    lon_cyclic,
    sst_trend["lat"],
    sst_label_nh,
    levels=contour_levels,
    colors="black",
    linewidths=0,
    transform=ccrs.PlateCarree()
)

ax_nh.clabel(
    cs_nh_label,
    inline=True,
    fontsize=7,
    colors="black",
    fmt="%.1f"
)

# Add land
ax_nh.add_feature(
    cfeature.LAND,
    facecolor="lightgray",
    zorder=2
)

# Add coastlines
ax_nh.coastlines(
    resolution="110m",
    linewidth=0.8,
    zorder=3
)

# Add country borders
ax_nh.add_feature(
    cfeature.BORDERS,
    linewidth=0.3,
    zorder=3
)

gl_nh = ax_nh.gridlines(
    crs=ccrs.PlateCarree(),
    linewidth=0.5,
    linestyle="--",
    alpha=0.6
)

gl_nh.ylocator = plt.FixedLocator(
    [50, 60, 70, 80]
)

ax_nh.set_title(
    "Northern Hemisphere",
    fontsize=13,
    pad=10
)


# ---------------------------------------------------------
# Southern Hemisphere
# ---------------------------------------------------------

# Zoom to 90°S-50°S.
ax_sh.set_extent(
    [-180, 180, -90, -50],
    crs=ccrs.PlateCarree()
)

ax_sh.set_boundary(
    circle,
    transform=ax_sh.transAxes
)

# Task 9:
# Plot filled SST trend contours.
cf_sh = ax_sh.contourf(
    lon_cyclic,
    sst_trend["lat"],
    sst_trend_cyclic,
    levels=___,
    cmap="seismic",
    extend="both",
    transform=ccrs.PlateCarree()
)

# Draw contour lines
cs_sh = ax_sh.contour(
    lon_cyclic,
    sst_trend["lat"],
    sst_trend_cyclic,
    levels=contour_levels,
    colors="black",
    linewidths=0.4,
    transform=ccrs.PlateCarree()
)

# Restrict contour labels to the inner polar region
lat_sh = sst_trend["lat"].values

sst_label_sh = np.where(
    lat_sh[:, np.newaxis] <= -68,
    sst_trend_cyclic,
    np.nan
)

cs_sh_label = ax_sh.contour(
    lon_cyclic,
    sst_trend["lat"],
    sst_label_sh,
    levels=contour_levels,
    colors="black",
    linewidths=0,
    transform=ccrs.PlateCarree()
)

ax_sh.clabel(
    cs_sh_label,
    inline=True,
    fontsize=7,
    colors="black",
    fmt="%.1f"
)

# Add land
ax_sh.add_feature(
    cfeature.LAND,
    facecolor="lightgray",
    zorder=2
)

# Add coastlines
ax_sh.coastlines(
    resolution="110m",
    linewidth=0.8,
    zorder=3
)

# Add country borders
ax_sh.add_feature(
    cfeature.BORDERS,
    linewidth=0.3,
    zorder=3
)

gl_sh = ax_sh.gridlines(
    crs=ccrs.PlateCarree(),
    linewidth=0.5,
    linestyle="--",
    alpha=0.6
)

gl_sh.ylocator = plt.FixedLocator(
    [-80, -70, -60, -50]
)

ax_sh.set_title(
    "Southern Hemisphere",
    fontsize=13,
    pad=10
)


# ---------------------------------------------------------
# Shared colorbar and figure title
# ---------------------------------------------------------

cbar = fig.colorbar(
    cf_nh,
    ax=[ax_nh, ax_sh],
    orientation="horizontal",
    pad=0.08,
    shrink=0.8,
    ticks=levels
)

cbar.set_label(
    "SST Trend (°C decade$^{-1}$)"
)

fig.suptitle(
    f"SST Trend (°C decade$^{{-1}}$) ({trend_start[:4]}-{trend_end[:4]})",
    fontsize=16,
    y=0.98
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
