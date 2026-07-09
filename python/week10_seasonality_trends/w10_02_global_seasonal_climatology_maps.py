# ---------------------------------------------------------
# Global Seasonal Climatology Maps
# ---------------------------------------------------------
# Exercise:
# 1. Read monthly 2-m air temperature data.
# 2. Convert units:
#      air : K to °C
# 3. Calculate seasonal climatology for 1991-2020.
# 4. Plot global climatology maps for four seasons:
#      DJF : December-January-February
#      MAM : March-April-May
#      JJA : June-July-August
#      SON : September-October-November
# 5. Use a Robinson projection and a shared colorbar.
# ---------------------------------------------------------

import warnings
from pathlib import Path

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.util import add_cyclic_point
import sys
from matplotlib.colors import CSS4_COLORS


warnings.filterwarnings(
    "ignore",
    message="invalid value encountered in create_collection",
    category=RuntimeWarning
)


def seasonal_climatology(data, clim_start="1991-01-01", clim_end="2020-12-31"):
    """
    Calculate seasonal climatology from monthly data.

    Parameters
    ----------
    data : xarray.DataArray
        Monthly data with dimensions (time, lat, lon).
    clim_start, clim_end : str
        Climatology period.

    Returns
    -------
    clim_season : xarray.DataArray
        Seasonal climatology with dimension season.
    """

    # Select the climatology period
    data_clim = data.sel(time=slice(clim_start, clim_end))

    # Group by meteorological season and average over all years
    clim_season = data_clim.groupby("time.season").mean("time")

    # Reorder seasons for plotting
    clim_season = clim_season.sel(season=["DJF", "MAM", "JJA", "SON"])

    return clim_season


# ---------------------------------------------------------
# Read data
# ---------------------------------------------------------
indir = Path('../../data')
air_file = indir  / "air.2m.mon.mean.nc"

ds_air = xr.open_dataset(air_file)
air = ds_air["air"]

# ---------------------------------------------------------
# Unit conversion
# ---------------------------------------------------------
# Temperature: K to °C
air = air - 273.15
air.attrs["units"] = "°C"


# ---------------------------------------------------------
# Calculate seasonal climatology
# ---------------------------------------------------------
clim_start = "1991-01-01"
clim_end = "2020-12-31"

air_season_clim = seasonal_climatology(air, clim_start, clim_end)


# ---------------------------------------------------------
# Plot four seasonal climatology maps
# ---------------------------------------------------------
proj = ccrs.Robinson(central_longitude=180)
data_crs = ccrs.PlateCarree()

fig, axes = plt.subplots(
    2, 2,
    figsize=(12, 7),
    subplot_kw={"projection": proj}
)

# Use the same color scale for all four seasons
levels = np.arange(-40, 41, 5)
cmap = "turbo"

season_titles = {
    "DJF": "December-January-February",
    "MAM": "March-April-May",
    "JJA": "June-July-August",
    "SON": "September-October-November",
}

# Panel labels
panel_labels = ["(a)", "(b)", "(c)", "(d)"]

for ax, season, label in zip(axes.ravel(), ["DJF", "MAM", "JJA", "SON"], panel_labels):

    # Select seasonal climatology
    dat = air_season_clim.sel(season=season)

    # Add cyclic point to avoid a blank seam at the map boundary
    dat_cyclic, lon_cyclic = add_cyclic_point(dat.values, coord=dat.lon)

    cf = ax.contourf(
        lon_cyclic,
        dat.lat,
        dat_cyclic,
        levels=levels,
        cmap=cmap,
        extend="both",
        transform=data_crs
    )

    ax.set_global()
    ax.coastlines(linewidth=0.7)
    ax.add_feature(cfeature.BORDERS, linewidth=0.4)
    ax.gridlines(linewidth=0.3, color="gray", alpha=0.5, linestyle="--")

    ax.set_title(
        f"{label} {season}: {season_titles[season]}",
        loc="left"
    )

# Shared colorbar
cbar = plt.colorbar(
    cf,
    ax=axes,
    orientation="horizontal",
    shrink=0.7,
    pad=0.07
)
cbar.set_label("2-m air temperature climatology (°C)")

plt.suptitle(
    f"Global Seasonal 2-m Air Temperature Climatology ({clim_start[:4]}-{clim_end[:4]})",
    fontsize=14
)

plt.savefig(
    Path(__file__).with_suffix(".jpg"),
    dpi=300,
    bbox_inches="tight"
)

plt.show()

ds_air.close()
