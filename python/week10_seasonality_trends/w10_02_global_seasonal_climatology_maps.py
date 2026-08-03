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

from pathlib import Path

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.util import add_cyclic_point
import sys
from matplotlib.colors import CSS4_COLORS

import warnings
warnings.filterwarnings(
    "ignore",
    message="invalid value encountered in create_collection",
    category=RuntimeWarning
)

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
    print(clim_season.dims)
    # Reorder seasons for plotting
    clim_season = clim_season.sel(season=["DJF", "MAM", "JJA", "SON"])
    print("clim_seaso_sel: ")
    print(clim_season.dims)

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

season_names = ["DJF", "MAM", "JJA", "SON"]
end_months = [2, 5, 8, 11]

air_season_clim = xr.concat(
    [
        calc_seasonal_mean(air, window=3, end_month=m)
        for m in end_months
    ],
    dim="season",
)

tmp = air_season_clim.assign_coords(season=season_names)
air_season_clim=tmp.mean('year')
print(air_season_clim)
print(air_season_clim.coords)
print(air_season_clim.dims)

#air_season_clim2 = seasonal_climatology(air, clim_start, clim_end)


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
