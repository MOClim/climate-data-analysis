# ---------------------------------------------------------
# Regional Climate Data Analysis Template
# ---------------------------------------------------------
# Instructions:
# 1. Download a NetCDF climate dataset of monthly precipitation rate.
#    https://psl.noaa.gov/data/gridded/data.ncep.reanalysis.html
#
# 2. Put the data file in ../../data_raw/
#
# 3. Update:
#      - file name
#      - variable name
#      - region name
#      - latitude range
#      - longitude range
#
# 4. Run the program to calculate area-averaged time series.
#
# Example region: North America
# Latitude : 75N to 15N
# Longitude: 190E to 300E
# ---------------------------------------------------------


import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.ticker import MultipleLocator


def regional_weighted_mean(data, lat1, lat2, lon1, lon2):
    """Compute cosine-latitude-weighted regional mean."""

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

    if data.lat[0] > data.lat[-1]:
        dat_region = data.sel(lat=slice(lat1, lat2), lon=slice(lon1, lon2))
    else:
        dat_region = data.sel(lat=slice(lat2, lat1), lon=slice(lon1, lon2))

    weights = np.cos(np.deg2rad(dat_region.lat))

    return dat_region.weighted(weights).mean(
        dim=("lat", "lon"),
        skipna=True
    )


def calculate_annual_anomaly(regional_mean):
    """Calculate monthly anomalies and annual mean anomalies."""

    clim = regional_mean.groupby("time.month").mean("time")
    anom = regional_mean.groupby("time.month") - clim
    anom_ann = anom.resample(time="YS").mean()

    return anom_ann


# -----------------------------
# User settings
# -----------------------------
# ---------------------------------------------------------
# Data directory and dataset information
# ---------------------------------------------------------
script_dir = Path(__file__).resolve().parent

# Check whether the script is inside the "solution" directory
if script_dir.name == "solution":
    # Move up two directory levels to reach the repository root
    repo_dir = script_dir.parents[2]
else:
    # Move up two directory levels to reach the repository root
    repo_dir = script_dir.parents[1]

filein = repo_dir / "data_raw/prate.mon.mean.nc"

# ---------------------------------------------------------
# Variable name inside the NetCDF file
# ---------------------------------------------------------
var_name = "prate"

# ---------------------------------------------------------
# Define analysis region and regional name
# ---------------------------------------------------------

region_name = "North America"

lat_str, lat_end = 75, 15
lon_str, lon_end = 190, 300

# -----------------------------
# Load data
# -----------------------------
ds = xr.open_dataset(filein)
print(ds)

# Precipitation rate
prate = ds[var_name]

# ---------------------------------------------------------
# Unit conversion:
# kg m-2 s-1 = mm/s
# mm/day = precipitation rate * 86400
# ---------------------------------------------------------
prate = prate * 86400
prate.attrs["units"] = "mm/day"

# -----------------------------
# Area average
# -----------------------------
prate_mean = regional_weighted_mean(
    prate,
    lat_str,
    lat_end,
    lon_str,
    lon_end
)

prate_ann_anom = calculate_annual_anomaly(prate_mean)


# -----------------------------
# Plot
# -----------------------------
plt.figure(figsize=(10, 4))

plt.plot(
    prate_ann_anom.time.dt.year,
    prate_ann_anom,
    color="black",
    linewidth=1.5
)

plt.axhline(0, color="gray", linestyle="-")

plt.xlabel("Year")
plt.ylabel("Precipitation rate anomaly (mm/day)")
plt.title(f"{region_name} area-averaged precipitation rate anomaly")

plt.xticks(np.arange(1950, 2030, 10))
plt.gca().xaxis.set_minor_locator(MultipleLocator(1))
plt.gca().yaxis.set_minor_locator(MultipleLocator(0.2))

plt.grid(which="major", linestyle="-", linewidth=0.7, alpha=0.7)
plt.grid(which="minor", linestyle="--", linewidth=0.4, alpha=0.5)

plt.tight_layout()

output_path = Path(__file__).with_suffix(".jpg")
plt.savefig(output_path, dpi=300)

plt.show()
ds.close()
