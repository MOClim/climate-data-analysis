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

def monthly_clm_anom(dat, clim_period=None):
    """Calculate monthly anomalies relative to monthly climatology."""

    # Monthly climatology
    if clim_period is None:
        clm = dat.groupby("time.month").mean("time")
    else:
        start, end = clim_period
        clm = (
            dat.sel(time=slice(start, end))
            .groupby("time.month")
            .mean("time")
        )

    anom = dat.groupby("time.month") - clm

    return anom


def calc_seasonal_anom(dat, window=5, end_month=1, clim_period=None):
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

    # Monthly climatology
    if clim_period is None:
        clm = dat.groupby("time.month").mean("time")
    else:
        start, end = clim_period
        clm = (
            dat.sel(time=slice(start, end))
            .groupby("time.month")
            .mean("time")
        )

    # Monthly anomalies
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
# Calculate monthly and annual mean anomalies
# ---------------------------------------------------------
clim_start = "1991-01-01"
clim_end = "2020-12-31"


# Step 1: Calculate annual mean anomalies from monthly anomalies.
# Use calc_seasonal_anom to average monthly anomalies within each year.

air_anom = calc_seasonal_anom()
pr_anom = calc_seasonal_anom()


# Monthly anomalies relative to monthly climatology
air_mon_anom = monthly_clm_anom(air, clim_period=[clim_start, clim_end])
pr_mon_anom = monthly_clm_anom(prate, clim_period=[clim_start, clim_end])

# ---------------------------------------------------------
# Calculate regional area-weighted means
# ---------------------------------------------------------
# Approximate North America box
lat_str, lat_end = 75, 15
lon_str, lon_end = 190, 300   # 0-360 longitude: 190E=170W, 300E=60W

air_anom_NA = regional_weighted_mean(air_anom, lat_str, lat_end, lon_str, lon_end)
pr_anom_NA = regional_weighted_mean(pr_anom, lat_str, lat_end, lon_str, lon_end)

air_mon_anom_NA = regional_weighted_mean(air_mon_anom, lat_str, lat_end, lon_str, lon_end)
pr_mon_anom_NA = regional_weighted_mean(pr_mon_anom, lat_str, lat_end, lon_str, lon_end)

# Convert year coordinates to datetime for plotting
air_time = np.array([np.datetime64(f"{y}-01-01") for y in air_anom_NA.year.values])
pr_time = np.array([np.datetime64(f"{y}-01-01") for y in pr_anom_NA.year.values])

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
    air_mon_anom_NA.time,
    air_mon_anom_NA,
    linewidth=0.7,
    color="gray",
    alpha=0.7,
    label="Monthly anomaly"
)
axes[0].plot(
    air_time,
    air_anom_NA,
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
