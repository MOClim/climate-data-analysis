# ---------------------------------------------------------
# Compare Area-Averaged Temperature Anomalies
# ---------------------------------------------------------
# This program compares temperature anomalies between
# two selected regions using NOAA NCEP/NCAR Reanalysis.
#
# Why use anomalies?
# Different regions have different average temperatures.
#
# Example:
#   Tropical Pacific : ~27°C
#   North America    : ~11°C
#
# To compare climate variability rather than mean
# temperature, we remove the average seasonal cycle.
#
# Anomaly = Temperature − Monthly Climatology
#
# Positive anomalies indicate warmer-than-average
# conditions, while negative anomalies indicate
# cooler-than-average conditions.
# ---------------------------------------------------------

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def regional_weighted_mean(data, lat1, lat2, lon1, lon2):
    """
    Calculate cosine-latitude-weighted regional mean.
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

    dat_region_mean = dat_region.weighted(weights).mean(
        dim=("lat", "lon"),
        skipna=True
    )

    return dat_region_mean

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
# User settings
# ---------------------------------------------------------

indir = Path("../../data/")
filein = indir / "air.2m.mon.mean.nc"

# Region 1: North America
region1_name = "North America"
lat1_start, lat1_end = 75, 15
lon1_start, lon1_end = 190, 300

# Region 2: Tropical Pacific
region2_name = "Tropical Pacific"
lat2_start, lat2_end = 20, -20
lon2_start, lon2_end = 120, 280


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

ds = xr.open_dataset(filein)
air = ds["air"][:-2]

# Convert Kelvin to Celsius
air = air - 273.15
air.attrs["units"] = "degC"

# ---------------------------------------------------------
# Calculate annual-mean anomalies using running mean
# ---------------------------------------------------------

air_an_anm = calc_seasonal_anom(air, window=12, end_month=12)

# ---------------------------------------------------------
# Calculate regional means
# ---------------------------------------------------------

r1_an_anm = regional_weighted_mean(
    air_an_anm,
    lat1_start,
    lat1_end,
    lon1_start,
    lon1_end
)

r2_an_anm = regional_weighted_mean(
    air_an_anm,
    lat2_start,
    lat2_end,
    lon2_start,
    lon2_end
)




# ---------------------------------------------------------
# Plot comparison
# ---------------------------------------------------------

plt.figure(figsize=(10, 4))

plt.plot(
    r1_an_anm.year,
    r1_an_anm,
    linewidth=1.5,
    label=region1_name
)

plt.plot(
    r2_an_anm.year,
    r2_an_anm,
    linewidth=1.5,
    label=region2_name
)

plt.axhline(0, color="gray", linewidth=0.8)

plt.xlabel("Year")
plt.ylabel("2-m air temperature anomaly (°C)")
plt.title("Comparison of Area-Averaged Temperature Anomalies")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

output_path = Path(__file__).with_suffix(".jpg")
plt.savefig(output_path, dpi=300)

plt.show()

ds.close()

