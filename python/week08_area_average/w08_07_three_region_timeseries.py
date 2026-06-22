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


def annual_anomaly(regional_mean):
    """Calculate annual mean temperature anomaly."""

    clim = regional_mean.groupby("time.month").mean("time")
    anom = regional_mean.groupby("time.month") - clim

    anom_ann = anom.resample(time="YS").mean()
    count_ann = anom.resample(time="YS").count()

    # Keep only complete years
    anom_ann = anom_ann.where(count_ann == 12, drop=True)

    return anom_ann


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
    sharey=True
)

for i, (name, lat1, lat2, lon1, lon2) in enumerate(regions):

    reg_mean = regional_weighted_mean(air, lat1, lat2, lon1, lon2)
    reg_anom = annual_anomaly(reg_mean)

    axes[i].plot(
        reg_anom.time.dt.year,
        reg_anom,
        linewidth=1.5
    )

    axes[i].axhline(0, color="gray", linewidth=0.8)
    axes[i].set_title(name, loc="left")
    axes[i].set_ylabel("Anomaly (°C)")
    axes[i].set_ylim(-3, 3)
    axes[i].yaxis.set_minor_locator(MultipleLocator(0.5))
    axes[i].grid(True, which="major", linestyle="-", alpha=0.6)
    axes[i].grid(True, which="minor", linestyle="--", alpha=0.3)

axes[-1].set_xlabel("Year")
axes[-1].set_xlim(1948, 2025)
axes[-1].set_xticks(np.arange(1950, 2030, 10))

plt.suptitle("Regional Area-Averaged 2-m Air Temperature Anomalies")
plt.tight_layout()

output_path = Path(__file__).with_suffix(".jpg")
plt.savefig(output_path, dpi=300)

plt.show()
ds.close()
