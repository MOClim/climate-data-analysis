# ---------------------------------------------------------
# Global Mean Temperature and Precipitation Time Series
# ---------------------------------------------------------
# Exercise:
# 1. Read global monthly 2-m air temperature data.
# 2. Read global monthly precipitation rate data.
# 3. Convert units:
#      air   : K to °C
#      prate : kg m-2 s-1 to mm/day
# 4. Calculate regional area-weighted mean time series.
# 5. Plot temperature and precipitation in two panels.
# ---------------------------------------------------------

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.ticker import MultipleLocator

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


def global_weighted_mean(data):
    """Calculate cosine-latitude-weighted global mean."""

    weights = np.cos(np.deg2rad(data.lat))

    global_mean = data.weighted(weights).mean(
        dim=("lat", "lon"),
        skipna=True
    )

    return global_mean

def calc_seasonal_anom(dat, window=5, end_month=1):
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

    # Compute monthly anomalies
    clm = dat.groupby("time.month").mean(dim="time")
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

# ---------------------------------------------------------
# Read data
# ---------------------------------------------------------
script_dir = Path(__file__).resolve().parent

# Check whether the script is inside the "solution" directory
if script_dir.name == "solution":
    # Move up two directory levels to reach the repository root
    repo_dir = script_dir.parents[2]
else:
    # Move up two directory levels to reach the repository root
    repo_dir = script_dir.parents[1]

air_file = repo_dir/ "data" / "air.2m.mon.mean.nc"
pr_file  = repo_dir / "data_raw" / "prate.mon.mean.nc"

ds_air = xr.open_dataset(air_file)
ds_pr = xr.open_dataset(pr_file)

air = ds_air["air"]
prate = ds_pr["prate"]


# ---------------------------------------------------------
# Unit conversion
# ---------------------------------------------------------

# Temperature: K to °C
air = air - 273.15
air.attrs["units"] = "°C"

# Precipitation rate: kg m-2 s-1 to mm/day
prate = prate * 86400
prate.attrs["units"] = "mm/day"


# Calculate annual anomalies
air_an_anm = calc_seasonal_anom(air,window=12,end_month=12)
prate_an_anm = calc_seasonal_anom(prate,window=12,end_month=12)

# ---------------------------------------------------------
# Calculate regional area-weighted means
# ---------------------------------------------------------
# Approximate North America box
lat_str, lat_end = 75, 15
lon_str, lon_end = 190, 300   # 0–360 longitude: 190E=170W, 300E=60W

R_NA_mean_air = regional_weighted_mean(air_an_anm, lat_str, lat_end, lon_str, lon_end)
R_NA_mean_prate = regional_weighted_mean(prate_an_anm, lat_str, lat_end, lon_str, lon_end)

# ---------------------------------------------------------
# Plot two panels
# ---------------------------------------------------------

fig, axes = plt.subplots(
    2, 1,
    figsize=(10, 6),
    sharex=True
)

# Panel 1: Temperature
axes[0].plot(
    R_NA_mean_air.year,
    R_NA_mean_air,
    linewidth=1.5,
    color="black"
)

axes[0].axhline(0, color="gray", linewidth=0.8)
axes[0].set_ylabel("Temperature anomaly (°C)")
axes[0].set_title("(a) North America Mean 2-m Air Temperature Anomaly", loc="left")
axes[0].yaxis.set_minor_locator(MultipleLocator(0.1))
axes[0].grid(which="major", linestyle="-", alpha=0.6)
axes[0].grid(which="minor", linestyle="--", alpha=0.3)


# Panel 2: Precipitation
axes[1].plot(
    R_NA_mean_prate.year,
    R_NA_mean_prate,
    linewidth=1.5,
    color="black"
)

axes[1].axhline(0, color="gray", linewidth=0.8)
axes[1].set_ylabel("Precipitation anomaly (mm/day)")
axes[1].set_xlabel("Year")
axes[1].set_title("(b) North America Mean Precipitation Rate Anomaly", loc="left")
axes[1].yaxis.set_minor_locator(MultipleLocator(0.01))
axes[1].grid(which="major", linestyle="-", alpha=0.6)
axes[1].grid(which="minor", linestyle="--", alpha=0.3)


# X-axis setting
axes[1].set_xlim(1948, 2025)
axes[1].set_xticks(np.arange(1950, 2030, 10))

plt.suptitle("Global Mean Temperature and Precipitation Anomalies")
plt.tight_layout()

output_path = Path(__file__).with_suffix(".jpg")
plt.savefig(output_path, dpi=300)

plt.show()

ds_air.close()
ds_pr.close()
