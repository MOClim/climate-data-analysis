# ---------------------------------------------------------
# Three-Region Temperature Anomaly Comparison
# ---------------------------------------------------------
# This program compares area-averaged temperature
# anomalies in three different regions.
#
# Workflow:
# 1. Read monthly 2-m air temperature data from
#    NOAA NCEP/NCAR Reanalysis.
#
# 2. Calculate annual temperature anomalies by removing
#    the monthly climatology.
#
# 3. Calculate area-weighted regional mean temperature
#    anomaly for three regions:
#
#    - North America
#      Latitude : 75N to 15N
#      Longitude: 190E to 310E
#
#    - Tropical Pacific
#      Latitude : 20N to 20S
#      Longitude: 120E to 280E
#
#    - Arctic
#      Latitude : 90N to 60N
#      Longitude: 0E to 360E
#
# 4. Plot the three regional time series on one panel
#    to compare long-term warming and variability.
# ---------------------------------------------------------

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.ticker import MultipleLocator

def regional_weighted_mean(data, lat1, lat2, lon1, lon2):
    """
    Calculate cosine-latitude-weighted regional mean.

    Parameters
    ----------
    data : xarray.DataArray
        Input data with dimensions time, lat, lon.
    lat1, lat2 : float
        Latitude range.
    lon1, lon2 : float
        Longitude range.

    Returns
    -------
    regional_mean : xarray.DataArray
        Area-averaged regional time series.
    """

    # Convert longitude system if needed
    if lon1 < 0 or lon2 < 0:
        if (data.lon > 180).any():
            data = data.assign_coords(
                lon=((data.lon + 180) % 360 - 180)
            ).sortby("lon")
    else:
        if (data.lon < 0).any():
            data = data.assign_coords(
                lon=(data.lon % 360)
            ).sortby("lon")

    # Select latitude range correctly
    if data.lat[0] > data.lat[-1]:
        dat_region = data.sel(
            lat=slice(lat1, lat2),
            lon=slice(lon1, lon2)
        )
    else:
        dat_region = data.sel(
            lat=slice(lat2, lat1),
            lon=slice(lon1, lon2)
        )

    # Cosine-latitude weighting
    weights = np.cos(np.deg2rad(dat_region.lat))

    regional_mean = dat_region.weighted(weights).mean(
        dim=("lat", "lon"),
        skipna=True
    )

    return regional_mean

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
# Step 1: Read the temperature dataset
# ---------------------------------------------------------
# Read monthly 2-m air temperature data from the
# NOAA NCEP/NCAR Reanalysis dataset.
#
# Unit: Kelvin (K)
# Convert to Celsius (°C) after reading.
# --------------------------------------------------------




# ---------------------------------------------------------
# Step 2: Calculate annual-mean temperature
# output: air_an_mean
# ---------------------------------------------------------



# ---------------------------------------------------------
# Step 3: Define three analysis regions
# ---------------------------------------------------------
# Each tuple contains:
# (Region name, latitude start, latitude end,
#  longitude start, longitude end)
# ---------------------------------------------------------



# -----------------------------
# Plot three regional time series on one panel
# -----------------------------
plt.figure(figsize=(10, 4))

for name, lat1, lat2, lon1, lon2 in regions:

    # Calculate regional mean temperature
    reg_mean = regional_weighted_mean(air_an_anm, lat1, lat2, lon1, lon2)

    plt.plot(
        reg_mean.year,
        reg_mean,
        linewidth=1.5,
        label=name
    )

plt.axhline(0, color="gray", linewidth=0.8)

plt.xlabel("Year")
plt.ylabel("2-m air temperature anomaly (°C)")
plt.title("Comparison of Regional Area-Averaged Temperature Anomalies")

plt.xlim(1948, 2025)
plt.ylim(-3, 3)

plt.xticks(np.arange(1950, 2030, 10))
plt.gca().xaxis.set_minor_locator(MultipleLocator(1))
plt.gca().yaxis.set_minor_locator(MultipleLocator(0.5))

plt.grid(which="major", linestyle="-", alpha=0.6)
plt.grid(which="minor", linestyle="--", alpha=0.3)

plt.legend()
plt.tight_layout()

output_path = Path(__file__).with_suffix(".jpg")
plt.savefig(output_path, dpi=300)

plt.show()
ds.close()

