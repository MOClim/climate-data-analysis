# ---------------------------------------------------------
# Area-Averaged Temperature 
# ---------------------------------------------------------
# This program reads NOAA NCEP/NCAR Reanalysis monthly
# 2-m air temperature data and calculates an area-weighted
# temperature for a selected region.
#
# Data source:
# NOAA Physical Sciences Laboratory (PSL)
# https://psl.noaa.gov/data/gridded/data.ncep.reanalysis.html
#
# Dataset:
# air.2m.mon.mean.nc
#
# Exercise:
# 1. Change the latitude and longitude boundaries below
#    to select a different region.
# 2. Update the plot title with the region name.
# 3. Compare temperature variability among regions.
#
# Example regions:
#
# North America
# lat_start, lat_end = 75, 15
# lon_start, lon_end = 190, 300
#
# Arctic
# lat_start, lat_end = 90, 60
# lon_start, lon_end = 0, 360
#
# Europe
# lat_start, lat_end = 70, 35
# lon_start, lon_end = -10, 40
#
# Tropics
# lat_start, lat_end = 20, -20
# lon_start, lon_end = 0, 360
# ---------------------------------------------------------

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

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
    target_lon_range = 'neg180_180' if lon1 < 0 or lon2 < 0 else '0_360'
    if target_lon_range == 'neg180_180' and (data.lon > 180).any():
        data = data.assign_coords(lon=((data.lon + 180) % 360 - 180)).sortby('lon')
    elif target_lon_range == '0_360' and (data.lon < 0).any():
        data = data.assign_coords(lon=(data.lon % 360)).sortby('lon')

    # --- Select region ---
    dat_region = data.sel(lat=slice(lat1, lat2), lon=slice(lon1, lon2))

    # --- Apply cosine-latitude weighting ---
    weights = np.cos(np.deg2rad(dat_region['lat']))
    dat_region_mean = dat_region.weighted(weights).mean(dim=['lat', 'lon'], skipna=True)

    # --- Assign name ---
    dat_region_mean.name = f"regional_mean_{lat1}_{lat2}_{lon1}_{lon2}"

    return dat_region_mean

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

# -----------------------------
# User settings
# -----------------------------
indir = filename = Path('../../data/')
filein = indir / "air.2m.mon.mean.nc"


# -----------------------------
# Load data
# -----------------------------
ds = xr.open_dataset(filein)
print(ds)

# Common variable name in NCEP/NCAR air.2m file
air = ds["air"]

# -----------------------------
# Convert K to degC 
# -----------------------------
air = air - 273.15
air.attrs["units"] = "degC"

# Annual mean using running mean function 
air_ann = calc_seasonal_mean(air, window=12, end_month=12)

# ---------------------------------------------------------
# Area-weighted mean
# ---------------------------------------------------------
# Grid cells become smaller toward the poles.
# Cosine(latitude) weighting accounts for the
# changing area represented by each grid cell.
# ---------------------------------------------------------

# Step 1: Select region
# Modify these values for your analysis
lat_str, lat_end = , 
lon_str, lon_end = , 

# Step 2: Add Region name
region_name = ''

air_region_mean = regional_weighted_mean(air_ann, lat_str, lat_end, lon_str, lon_end)



# -----------------------------
# Plot
# -----------------------------
plt.figure(figsize=(10, 4))
plt.plot(air_region_mean.year, air_region_mean, color="black", linewidth=1.5)

plt.xlabel("Year")
plt.ylabel("2-m air temperature (°C)")
plt.title(f"{region_name} area-averaged 2-m air temperature")
plt.grid(alpha=0.3)
plt.tight_layout()

# Save the plot as a JPEG file
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)

# Show the plot
plt.show()

