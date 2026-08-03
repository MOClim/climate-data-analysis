# ---------------------------------------------------------
# Three-Panel Regional Temperature Anomaly Time Series
# ---------------------------------------------------------

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.ticker import MultipleLocator

def regional_weighted_mean(data, lat1, lat2, lon1, lon2):
    """Calculate cosine-latitude-weighted regional mean."""

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

    # Select latitude correctly
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

# -----------------------------
# Load data
# -----------------------------
indir = Path("../../data/")
filein = indir / "air.2m.mon.mean.nc"

ds = xr.open_dataset(filein)
air = ds["air"]

# Convert K to degC
air = air - 273.15
air.attrs["units"] = "degC"

# annual mean anomaly using running mean
air_an_anm = calc_seasonal_anom(air, window=12, end_month=12)

# -----------------------------
# Define regions
# -----------------------------
regions = [
    ("North America", 75, 15, 190, 310),
    ("Tropical Pacific", 20, -20, 120, 280),
    ("Arctic", 90, 60, 0, 360),
]


# -----------------------------
# Plot three panels
# -----------------------------
fig, axes = plt.subplots(
    3, 1,
    figsize=(10, 8),
    sharex=True,
    sharey=False
)

for i, (name, lat1, lat2, lon1, lon2) in enumerate(regions):

    reg_mean = regional_weighted_mean(air_an_anm, lat1, lat2, lon1, lon2)

    axes[i].plot(
        reg_mean.year,
        reg_mean,
        linewidth=1.5
    )

    axes[i].axhline(0, color="gray", linewidth=0.8)
    axes[i].set_title(name, loc="left")
    axes[i].set_ylabel("Anomaly (°C)")
    axes[i].yaxis.set_minor_locator(MultipleLocator(0.5))
    axes[i].grid(True, which="major", linestyle="-", alpha=0.6)
    axes[i].grid(True, which="minor", linestyle="--", alpha=0.3)

axes[0].set_ylim(-1, 1)
axes[1].set_ylim(-1, 1)
axes[2].set_ylim(-2, 3)

axes[-1].set_xlabel("Year")
axes[-1].set_xlim(1948, 2025)
axes[-1].set_xticks(np.arange(1950, 2030, 10))

plt.suptitle("Regional Area-Averaged 2-m Air Temperature Anomalies")
plt.tight_layout()

output_path = Path(__file__).with_suffix(".jpg")
plt.savefig(output_path, dpi=300)

plt.show()
ds.close()
