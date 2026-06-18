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


def calculate_annual_anomaly(regional_mean):
    """
    Calculate monthly anomalies and annual mean anomalies.
    """

    # Monthly climatology
    clim = regional_mean.groupby("time.month").mean("time")

    # Monthly anomaly
    anom = regional_mean.groupby("time.month") - clim

    # Annual mean anomaly
    anom_ann = anom.resample(time="YS").mean()

    return anom_ann


# ---------------------------------------------------------
# User settings
# ---------------------------------------------------------

indir = Path("../../data/")
filein = indir / "air.2m.mon.mean.nc"

# Region 1: North America
region1_name = "North America"
lat1_start, lat1_end = 75, 15
lon1_start, lon1_end = 190, 310

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
# Calculate regional means
# ---------------------------------------------------------

region1_mean = regional_weighted_mean(
    air,
    lat1_start,
    lat1_end,
    lon1_start,
    lon1_end
)

region2_mean = regional_weighted_mean(
    air,
    lat2_start,
    lat2_end,
    lon2_start,
    lon2_end
)


# ---------------------------------------------------------
# Calculate annual anomalies
# ---------------------------------------------------------

region1_anom_ann = calculate_annual_anomaly(region1_mean)
region2_anom_ann = calculate_annual_anomaly(region2_mean)


# ---------------------------------------------------------
# Plot comparison
# ---------------------------------------------------------

plt.figure(figsize=(10, 4))

plt.plot(
    region1_anom_ann.time.dt.year,
    region1_anom_ann,
    linewidth=1.5,
    label=region1_name
)

plt.plot(
    region2_anom_ann.time.dt.year,
    region2_anom_ann,
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

