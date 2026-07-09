# ---------------------------------------------------------
# Regional Monthly and Annual Mean Anomalies
# ---------------------------------------------------------
# Purpose:
#   Compare monthly anomalies with annual mean anomalies for
#   regional temperature and precipitation.
#
# Directions:
#   Step 1: Calculate annual mean anomalies from monthly anomalies.
#   Step 2: Plot monthly and annual mean precipitation anomalies.
#
# Concept:
#   Monthly anomaly = monthly value - monthly climatology
#   Annual mean anomaly = average of 12 monthly anomalies in one year
# ---------------------------------------------------------
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.ticker import MultipleLocator


# ---------------------------------------------------------
# Functions
# ---------------------------------------------------------
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
    target_lon_range = "neg180_180" if lon1 < 0 or lon2 < 0 else "0_360"

    if target_lon_range == "neg180_180" and (data.lon > 180).any():
        data = data.assign_coords(
            lon=((data.lon + 180) % 360 - 180)
        ).sortby("lon")
    elif target_lon_range == "0_360" and (data.lon < 0).any():
        data = data.assign_coords(
            lon=(data.lon % 360)
        ).sortby("lon")

    # --- Select region ---
    dat_region = data.sel(lat=slice(lat1, lat2), lon=slice(lon1, lon2))

    # --- Apply cosine-latitude weighting ---
    weights = np.cos(np.deg2rad(dat_region["lat"]))
    dat_region_mean = dat_region.weighted(weights).mean(
        dim=["lat", "lon"],
        skipna=True
    )

    dat_region_mean.name = f"regional_mean_{lat1}_{lat2}_{lon1}_{lon2}"

    return dat_region_mean


def monthly_climatology_anomaly(monthly_mean, clim_start="1991-01-01", clim_end="2020-12-31"):
    """
    Calculate monthly anomalies relative to monthly climatology.

    This removes the climatological seasonal cycle.
    """

    clim = monthly_mean.sel(time=slice(clim_start, clim_end)).groupby(
        "time.month"
    ).mean("time")

#    clim = monthly_climatology(monthly_mean, clim_start, clim_end)
    anom = monthly_mean.groupby("time.month") - clim

    return anom


# ---------------------------------------------------------
# Read data
# ---------------------------------------------------------
indir = Path("../../data")
indir2 = Path("../../data_raw")

air_file = indir / "air.2m.mon.mean.nc"
pr_file = indir2 / "prate.mon.mean.nc"

ds_air = xr.open_dataset(air_file)
ds_pr = xr.open_dataset(pr_file)

air = ds_air["air"]
prate = ds_pr["prate"]


# ---------------------------------------------------------
# Unit conversion
# ---------------------------------------------------------
# Temperature: K to degC
air = air - 273.15
air.attrs["units"] = "degC"

# Precipitation rate: kg m-2 s-1 to mm/day
prate = prate * 86400
prate.attrs["units"] = "mm/day"


# ---------------------------------------------------------
# Calculate regional area-weighted means
# ---------------------------------------------------------
# Approximate North America box
lat_str, lat_end = 75, 15
lon_str, lon_end = 190, 300   # 0-360 longitude: 190E=170W, 300E=60W

air_NA = regional_weighted_mean(air, lat_str, lat_end, lon_str, lon_end)
pr_NA = regional_weighted_mean(prate, lat_str, lat_end, lon_str, lon_end)


# ---------------------------------------------------------
# Calculate monthly and annual mean anomalies
# ---------------------------------------------------------
clim_start = "1991-01-01"
clim_end = "2020-12-31"

# Monthly anomalies relative to monthly climatology
air_anom_monthly = monthly_climatology_anomaly(air_NA, clim_start, clim_end)
pr_anom_monthly = monthly_climatology_anomaly(pr_NA, clim_start, clim_end)

# Step 1: Calculate annual mean anomalies from monthly anomalies.
# Use resample(time="YE") to average monthly anomalies within each year.
# Keep only complete years with 12 monthly values.
air_anom_annual = 
pr_anom_annual = 

# ---------------------------------------------------------
# Plot two panels
# ---------------------------------------------------------
fig, axes = plt.subplots(
    2, 1,
    figsize=(11, 7),
    sharex=True
)

# ---------------------------------------------------------
# Panel 1: Temperature monthly and annual mean anomaly
# ---------------------------------------------------------
axes[0].plot(
    air_anom_monthly.time,
    air_anom_monthly,
    linewidth=0.7,
    color="gray",
    alpha=0.7,
    label="Monthly anomaly"
)
axes[0].plot(
    air_anom_annual.time,
    air_anom_annual,
    linewidth=2.0,
    color="black",
    label="Annual mean anomaly"
)
axes[0].axhline(0, color="gray", linewidth=0.8)
axes[0].set_ylabel("Temperature anomaly (degC)")
axes[0].set_title(
    "(a) North America 2-m Air Temperature Anomaly",
    loc="left"
)
axes[0].yaxis.set_minor_locator(MultipleLocator(0.5))
axes[0].legend(loc="upper left", frameon=False)
axes[0].grid(which="major", linestyle="-", alpha=0.6)
axes[0].grid(which="minor", linestyle="--", alpha=0.3)


# Step 2: Plot precipitation monthly anomaly and annual mean anomaly.
# Use the same plotting style as the temperature panel above.
# ---------------------------------------------------------
# Panel 2: Precipitation monthly and annual mean anomaly
# ---------------------------------------------------------
axes[1].plot(
    ,              # x-axis (time variable)
    ,              # y-axis (monthly precipitation anomaly)
    linewidth=,    # line width
    color="",      # line color
    alpha=,        # transparency (0 = transparent, 1 = opaque)
    label=""       # legend label
)

axes[1].plot(
    ,              # x-axis (time variable)
    ,              # y-axis (annual-mean precipitation anomaly)
    linewidth=,    # line width
    color="",      # line color
    label=""       # legend label
)

axes[1].axhline(0, color="gray", linewidth=0.8)
axes[1].set_ylabel("Precipitation anomaly (mm/day)")
axes[1].set_xlabel("Year")
axes[1].set_title(
    "(b) North America Precipitation Rate Anomaly",
    loc="left"
)
axes[1].yaxis.set_minor_locator(MultipleLocator(0.1))
axes[1].legend(loc="upper left", frameon=False)
axes[1].grid(which="major", linestyle="-", alpha=0.6)
axes[1].grid(which="minor", linestyle="--", alpha=0.3)


# ---------------------------------------------------------
# Common axis settings
# ---------------------------------------------------------
for ax in axes:
    ax.set_xlim(np.datetime64("1948-01-01"), np.datetime64("2025-12-31"))

axes[0].set_ylim(-3, 3)
axes[1].set_ylim(-0.7, 0.7)

plt.suptitle(
    "North America Monthly and Annual Mean Anomalies\n"
    "Relative to 1991-2020 Monthly Climatology",
    fontsize=14
)
plt.tight_layout()

output_path = Path(__file__).with_suffix(".jpg")
plt.savefig(output_path, dpi=300, bbox_inches="tight")

plt.show()

ds_air.close()
ds_pr.close()
