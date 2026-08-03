# ---------------------------------------------------------
# Global Mean Temperature and Precipitation Time Series
# ---------------------------------------------------------
# Exercise:
# 1. Read global monthly 2-m air temperature data.
# 2. Read global monthly precipitation rate data.
# 3. Calculate global area-weighted mean time series.
# 4. Convert units:
#      air   : K to °C
#      prate : kg m-2 s-1 to mm/day
# 5. Plot temperature and precipitation in two panels.
# ---------------------------------------------------------

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.ticker import MultipleLocator

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

indir1 = Path("../../data/")
indir2 = Path("../../data_raw/")

air_file = indir1 / "air.2m.mon.mean.nc"
pr_file  = indir2 / "prate.mon.mean.nc"

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

# Calculate annual mean
air_an_anm = calc_seasonal_anom(air,window=12,end_month=12)
prate_an_anm = calc_seasonal_anom(prate,window=12,end_month=12)

# ---------------------------------------------------------
# Calculate global area-weighted means
# ---------------------------------------------------------

air_glb_mean = global_weighted_mean(air_an_anm)
prate_glb_mean = global_weighted_mean(prate_an_anm)


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
    air_glb_mean.year,
    air_glb_mean,
    linewidth=1.5,
    color="black"
)

axes[0].axhline(0, color="gray", linewidth=0.8)
axes[0].set_ylabel("Temperature anomaly (°C)")
axes[0].set_title("(a) Global Mean 2-m Air Temperature Anomaly", loc="left")
axes[0].yaxis.set_minor_locator(MultipleLocator(0.1))
axes[0].grid(which="major", linestyle="-", alpha=0.6)
axes[0].grid(which="minor", linestyle="--", alpha=0.3)


# Panel 2: Precipitation
axes[1].plot(
    prate_glb_mean.year,
    prate_glb_mean,
    linewidth=1.5,
    color="black"
)

axes[1].axhline(0, color="gray", linewidth=0.8)
axes[1].set_ylabel("Precipitation anomaly (mm/day)")
axes[1].set_xlabel("Year")
axes[1].set_title("(b) Global Mean Precipitation Rate Anomaly", loc="left")
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
