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
# 2. Calculate area-weighted regional mean temperature
#    for three regions:
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
# 3. Calculate annual temperature anomalies by removing
#    the monthly climatology.
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

def annual_anomaly(regional_mean):
    """
    Calculate annual mean anomaly from monthly data.

    Steps
    -----
    1. Calculate monthly climatology.
    2. Subtract monthly climatology from monthly data.
    3. Average monthly anomalies into annual anomalies.
    4. Keep only complete years.
    """

    # Monthly climatology
    clim = regional_mean.groupby("time.month").mean("time")

    # Monthly anomaly
    anom = regional_mean.groupby("time.month") - clim

    # Annual mean anomaly
    anom_ann = anom.resample(time="YS").mean()

    # Count number of months in each year
    count_ann = anom.resample(time="YS").count()

    # Keep only complete years
    anom_ann = anom_ann.where(count_ann == 12, drop=True)

    return anom_ann

# ---------------------------------------------------------
# Step 1: Read the temperature dataset
# ---------------------------------------------------------
# Read monthly 2-m air temperature data from the
# NOAA NCEP/NCAR Reanalysis dataset.
#
# Unit: Kelvin (K)
# Convert to Celsius (°C) after reading.
# --------------------------------------------------------

script_dir = Path(__file__).resolve().parent

# Check whether the script is inside the "solution" directory
if script_dir.name == "solution":
    # Move up two directory levels to reach the repository root
    repo_dir = script_dir.parents[2]
else:
    # Move up two directory levels to reach the repository root
    repo_dir = script_dir.parents[1]

filein = repo_dir / "data/air.2m.mon.mean.nc"

ds = xr.open_dataset(filein)
air = ds["air"]

# Convert K to degC
air = air - 273.15
air.attrs["units"] = "degC"

# ---------------------------------------------------------
# Step 2: Define three analysis regions
# ---------------------------------------------------------
# Each tuple contains:
# (Region name, latitude start, latitude end,
#  longitude start, longitude end)
# ---------------------------------------------------------

regions = [
    ("North America", 75, 15, 190, 310),
    ("Tropical Pacific", 20, -20, 120, 280),
    ("Arctic", 90, 60, 0, 360),
]

# -----------------------------
# Plot three regional time series on one panel
# -----------------------------
plt.figure(figsize=(10, 4))

for name, lat1, lat2, lon1, lon2 in regions:

    # Calculate regional mean temperature
    reg_mean = regional_weighted_mean(air, lat1, lat2, lon1, lon2)

    # Calculate annual temperature anomaly`
    reg_anom = annual_anomaly(reg_mean)

    plt.plot(
        reg_anom.time.dt.year,
        reg_anom,
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

