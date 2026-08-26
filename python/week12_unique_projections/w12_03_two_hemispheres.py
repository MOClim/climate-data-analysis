# ---------------------------------------------------------
# Northern and Southern Hemisphere Polar Projection Maps
# ---------------------------------------------------------
#
# This program introduces polar stereographic map projections
# for both hemispheres using DJF mean sea level pressure (SLP).
#
# Separate polar projections are needed to appropriately
# visualize high-latitude climate patterns in the Northern
# and Southern Hemispheres.
#
# In this example, we:
#
# 1. Read monthly sea level pressure data.
# 2. Calculate the DJF mean sea level pressure.
# 3. Add a cyclic longitude point to remove the map seam.
# 4. Create Northern and Southern Hemisphere polar projections.
# 5. Plot DJF sea level pressure using filled contours.
# 6. Overlay sea level pressure contour lines.
# 7. Compare SLP patterns between the two hemispheres.
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

def calc_seasonal_mean(dat, window=5, end_month=1):
    """
    Calculate seasonal mean using a trailing running mean, extract the final month (e.g., Mar for NDJFM),
    convert to year-lat-lon DataArray.

    Parameters:
    -----------
    dat : xr.DataArray
        Input data with dimensions (time, lat, lon) and datetime64 'time'.
    window : int
        Running mean window size (default is 5).
    end_month : int
        Target month used to extract seasonal means (final month of the trailing average).

    Returns:
    --------
    dat_out : xr.DataArray
        Seasonal mean with dimensions (year, lat, lon).
    """

    # Rename coordinates if necessary
    if "latitude" in dat.coords:
      dat = dat.rename({"latitude": "lat"})

    if "longitude" in dat.coords:
      dat = dat.rename({"longitude": "lon"})


    # Apply trailing running mean
    dat_rm = dat.rolling(time=window, center=False, min_periods=window).mean()

    # Filter for entries where month == end_month
    dat_tmp = dat_rm.sel(time=dat_rm["time"].dt.month == end_month)

    # Extract year from the end_month timestamps
    years = dat_tmp["time"].dt.year

    # Create clean DataArray with dimensions ['year', 'lat', 'lon']
    dat_out = xr.DataArray(
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

    return dat_out

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

# ---------------------------------------------------------
# Read monthly SLP
# ---------------------------------------------------------

indir = Path("../../data")
slp_file = indir / "slp.mon.mean.nc"

ds_slp = xr.open_dataset(slp_file)

slp = ds_slp["slp"]

# Convert Pa to hPa if needed.
if slp.attrs.get("units", "").lower() in ["pa", "pascal", "pascals"]:
    slp = slp / 100.0
    slp.attrs["units"] = "hPa"

# ----

# Northern Hemisphere map boundary
MIN_LAT = 20

# Optional climatology period.
# Set both to None to use the full time period in the file.
start_year = 1948
end_year = 2025

# ------------------------------------------------------------
# Select the analysis period
# ------------------------------------------------------------

if start_year is not None and end_year is not None:
    slp = slp.sel(
        time=slice(f"{start_year}-01-01", f"{end_year}-12-31")
    )


# ------------------------------------------------------------
# Calculate DJF mean
# ------------------------------------------------------------

# Calculate DJF seasonal means and then the climatological mean.
tmp = calc_seasonal_mean(slp, window=3, end_month=2)
slp_djf = tmp.mean(dim="year")

# Add cyclic longitude point to remove the map seam
slp_djf_cyclic, lon_cyclic = add_cyclic_point(
    slp_djf.values,
    coord=slp_djf["lon"].values
)

# ------------------------------------------------------------
# Create Northern and Southern Hemisphere polar projections
# ------------------------------------------------------------

fig, axs = plt.subplots( 1, 2, figsize=(10, 6))

# Replace the default axes with Cartopy projection axes
for ax in axs:
    ax.remove()

axs[0] = fig.add_subplot(
    1, 2, 1,
    projection=ccrs.NorthPolarStereo())

axs[1] = fig.add_subplot(
    1, 2, 2,
    projection=ccrs.SouthPolarStereo())


# ------------------------------------------------------------
# Circular map boundary
# ------------------------------------------------------------

theta = np.linspace(0, 2 * np.pi, 100)
center = [0.5, 0.5]
radius = 0.5

circle = mpath.Path(
    np.vstack([
        np.sin(theta) * radius + center[0],
        np.cos(theta) * radius + center[1]
    ]).T)

# ------------------------------------------------------------
# Plot settings
# ------------------------------------------------------------

levels = np.arange(960, 1041, 4)

extents = [
    [-180, 180, 20, 90],
    [-180, 180, -90, -20]]

titles = [
    "Northern Hemisphere",
    "Southern Hemisphere"]

lat_gridlines = [
    [20, 30, 40, 50, 60, 70, 80],
    [-80, -70, -60, -50, -40, -30, -20]]


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

    # Filled contours
    cf = ax.contourf(
        lon_cyclic,
        slp_djf["lat"],
        slp_djf_cyclic,
        levels=levels,
        cmap="coolwarm",
        extend="both",
        transform=ccrs.PlateCarree())

    # Contour lines
    cs = ax.contour(
        lon_cyclic,
        slp_djf["lat"],
        slp_djf_cyclic,
        levels=levels,
        colors="black",
        linewidths=0.5,
        transform=ccrs.PlateCarree())

    # Contour labels
    labels = ax.clabel(
        cs,
        levels=np.arange(984, 1037, 8),
        inline=True,
        fontsize=7,
        fmt="%d")

    # Keep contour labels inside circular boundary
    for txt in labels:

       txt.set_clip_on(True)

       txt.set_clip_path(
            circle,
            ax.transAxes)

       xy_display = txt.get_transform().transform(
            txt.get_position())

       xy_axes = ax.transAxes.inverted().transform(
            xy_display)

       distance = np.sqrt(
            (xy_axes[0] - 0.5) ** 2
            + (xy_axes[1] - 0.5) ** 2)

       if distance > 0.45:
            txt.set_visible(False)

    # Coastlines and borders
    ax.coastlines(
        resolution="110m",
        linewidth=0.8)

    ax.add_feature(
        cfeature.BORDERS,
        linewidth=0.4)

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
    "Sea Level Pressure (hPa)")


# ------------------------------------------------------------
# Figure title
# ------------------------------------------------------------

if start_year is not None and end_year is not None:

    title = (
        f"DJF Mean Sea Level Pressure "
        f"({start_year}-{end_year})")

else:

    title = "DJF Mean Sea Level Pressure"


fig.suptitle(title, fontsize=16, y=0.98)

# ------------------------------------------------------------
# Save and display
# ------------------------------------------------------------

output_path = Path(__file__).with_suffix(".jpg")

plt.savefig(output_path, dpi=300, bbox_inches="tight")

plt.show()

