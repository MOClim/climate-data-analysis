# ---------------------------------------------------------
# Regional Climate Map: Visualization Comparison
# ---------------------------------------------------------
# This program compares how visualization choices affect the
# interpretation of a regional climate anomaly map.
#
# The same January 2026 2-m air temperature anomaly is plotted
# four times using different colormaps and contour levels.
# Students should compare the panels and decide which map most
# clearly communicates the regional temperature anomaly pattern.
#
# Main ideas:
#   1. Colormap choice affects scientific interpretation.
#   2. Color range controls the contrast of anomaly features.
#   3. Too narrow a range may saturate values.
#   4. Too wide a range may hide regional details.
# ---------------------------------------------------------

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pathlib import Path

import warnings
warnings.filterwarnings(
    "ignore",
    message="invalid value encountered in create_collection",
    category=RuntimeWarning
)

# ---------------------------------------------------------
# Read local NetCDF file
# ---------------------------------------------------------
# This script reads the 2-m air temperature file from the
# repository data directory.

script_dir = Path(__file__).resolve().parent

# Check whether the script is inside the "solution" directory
if script_dir.name == "solution":
    # Move up two directory levels to reach the repository root
    repo_dir = script_dir.parents[2]
else:
    # Move up two directory levels to reach the repository root
    repo_dir = script_dir.parents[1]

air_file = repo_dir / "data/air.2m.mon.mean.nc"
ds = xr.open_dataset(air_file)

print(ds)
print(ds.time[-1].values)

# ---------------------------------------------------------
# Calculate January 2026 air temperature anomaly
# ---------------------------------------------------------
# The anomaly is calculated relative to the 1991-2020
# January climatology.

air = ds["air"].load()

# Convert from Kelvin to Celsius
air_c = air - 273.15

# January climatology for 1991-2020
ref = air_c.sel(time=slice("1991-01-01", "2020-12-31"))
jan_clim = ref.groupby("time.month").mean("time").sel(month=1)

# January 2026 anomaly
jan_2026 = air_c.sel(time="2026-01-01").squeeze()
anom = jan_2026 - jan_clim

print("Minimum anomaly:", float(anom.min().values))
print("Maximum anomaly:", float(anom.max().values))

# ---------------------------------------------------------
# Lambert Conformal projection and map extent
# ---------------------------------------------------------
# These settings focus on the contiguous United States.

map_proj = ccrs.LambertConformal(
    central_longitude=-96,
    central_latitude=39
)

data_proj = ccrs.PlateCarree()

map_extent = [-125, -66.5, 24, 50]

# ---------------------------------------------------------
# Visualization options to compare
# ---------------------------------------------------------
# Each dictionary defines one panel.
# Students can modify cmap and levels to test other choices.

plot_settings = [
    {
        "title": "RdBu_r, -8 to 8 °C",
        "cmap": "RdBu_r",
        "levels": np.arange(-8, 8.1, 1),
    },
    {
        "title": "RdBu_r, -15 to 15 °C",
        "cmap": "RdBu_r",
        "levels": np.arange(-15, 15.1, 1),
    },
    {
        "title": "coolwarm, -15 to 15 °C",
        "cmap": "coolwarm",
        "levels": np.arange(-15, 15.1, 1),
    },
    {
        "title": "Spectral_r, -15 to 15 °C",
        "cmap": "Spectral_r",
        "levels": np.arange(-15, 15.1, 1),
    },
]

# ---------------------------------------------------------
# Create four-panel comparison figure
# ---------------------------------------------------------

fig, axes = plt.subplots(
    nrows=2,
    ncols=2,
    figsize=(13, 8),
    subplot_kw={"projection": map_proj}
)

axes = axes.ravel()

for ax, setting in zip(axes, plot_settings):

    cf = ax.contourf(
        anom.lon,
        anom.lat,
        anom,
        levels=setting["levels"],
        cmap=setting["cmap"],
        extend="both",
        transform=data_proj
    )

    # Focus on the selected regional domain
    ax.set_extent(map_extent, crs=data_proj)

    # Add map features
    ax.coastlines(linewidth=0.8)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.add_feature(cfeature.STATES, linewidth=0.3)
    ax.add_feature(cfeature.LAKES, linewidth=0.3, edgecolor="gray", facecolor="none")

    # Add gridlines
    gl = ax.gridlines(
        draw_labels=True,
        linewidth=0.4,
        color="gray",
        alpha=0.5,
        linestyle="--"
    )
    gl.top_labels = False
    gl.right_labels = False

    ax.set_title(setting["title"], fontsize=11)

    # Add an individual colorbar for each panel
    cbar = plt.colorbar(
        cf,
        ax=ax,
        orientation="vertical",
        shrink=0.75,
        pad=0.03
    )
    cbar.set_label("2-m Air Temperature Anomaly (°C)")

fig.suptitle(
    "January 2026 Air Temperature Anomaly: Visualization Comparison",
    fontsize=14,
    y=0.98
)

plt.tight_layout()

# ---------------------------------------------------------
# Save figure
# ---------------------------------------------------------

output_path = Path(__file__).with_suffix(".jpg")
plt.savefig(output_path, dpi=300, bbox_inches="tight")
plt.show()

# ---------------------------------------------------------
# Discussion questions
# ---------------------------------------------------------
# 1. Which panel best shows the regional anomaly pattern?
# 2. Which color range is too narrow or too wide?
# 3. Which colormap most clearly separates positive and
#    negative temperature anomalies?
# 4. Which figure would you choose for a scientific report?
