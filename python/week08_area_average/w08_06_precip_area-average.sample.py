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
# Step 1: Download monthly precipitartion rate data 
# ---------------------------------------------------------
# Step 2: Add your data directory and dataset information
# ---------------------------------------------------------
indir = Path("")
filein = indir / ""



ds = xr.open_dataset(filein)
print(ds)

# ---------------------------------------------------------
# # Step 3: Variable name inside the NetCDF file
# ---------------------------------------------------------
# Example:
# air
# prate
var_name = ""

# Precipitation rate
prate = ds[var_name]

# Convert kg m-2 s-1 to mm/day
prate = prate * 86400
prate.attrs["units"] = "mm/day"

# Annual mean using running mean function
prate_an_anm = calc_seasonal_anom(prate,window=12, end_month=12)

# ---------------------------------------------------------
# Step 4: Define analysis region and regional name
# ---------------------------------------------------------

region_name = ""

lat_str, lat_end = , 
lon_str, lon_end = , 

# Area average
reg_an_anm = regional_weighted_mean(
    prate_an_anm,
    lat_str,
    lat_end,
    lon_str,
    lon_end
)


# -----------------------------
# Plot
# -----------------------------
plt.figure(figsize=(10, 4))

colors = np.where(reg_an_anm >= 0, "blue", "red")

plt.bar(
    reg_an_anm.year,
    reg_an_anm,
    color=colors,
    width=0.8,
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
