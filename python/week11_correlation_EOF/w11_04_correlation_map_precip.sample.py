# -------------------------------------------------------------
# Tropical Pacific SST and Global Precipitation Correlation Map
# -------------------------------------------------------------
#
# Create a global correlation map between annual Tropical Pacific
# SST anomalies and annual precipitation anomalies.
#
# Complete the following steps:
#
# 1. Read the monthly precipitation dataset.
# 2. Calculate monthly and annual precipitation anomalies.
# 3. Calculate the Pearson correlation coefficient between the
#    Tropical Pacific SST anomaly time series and annual
#    precipitation anomalies at every grid point.
# 4. Visualize the spatial correlation coefficients on a
#     global map using the Robinson projection.
#
# -------------------------------------------------------------

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pathlib import Path
from cartopy.util import add_cyclic_point

import warnings
warnings.filterwarnings(
    "ignore",
    message="invalid value encountered in create_collection",
    category=RuntimeWarning
)

def regional_weighted_mean(data, lat1, lat2, lon1, lon2):
    """Compute a cosine-latitude-weighted regional mean."""

    if "latitude" in data.coords:
        data = data.rename({"latitude": "lat"})
    if "longitude" in data.coords:
        data = data.rename({"longitude": "lon"})

    if (lon1 < 0 or lon2 < 0) and bool((data.lon > 180).any()):
        data = data.assign_coords(
            lon=((data.lon + 180) % 360 - 180)
        ).sortby("lon")
    elif lon1 >= 0 and lon2 >= 0 and bool((data.lon < 0).any()):
        data = data.assign_coords(lon=(data.lon % 360)).sortby("lon")

    if data.lat[0] < data.lat[-1]:
        lat_slice = slice(min(lat1, lat2), max(lat1, lat2))
    else:
        lat_slice = slice(max(lat1, lat2), min(lat1, lat2))

    region = data.sel(
        lat=lat_slice,
        lon=slice(min(lon1, lon2), max(lon1, lon2))
    )

    weights = np.cos(np.deg2rad(region.lat))
    dat_region_mean = region.weighted(weights).mean(
        dim=["lat", "lon"], skipna=True)

    return dat_region_mean

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

def linear_detrend(dat, min_coverage=0.9, dtrend=True):

   # Apply coverage mask
    valid_counts = dat.count(dim="year")
    total_years = dat["year"].size
    min_valid_years = int(total_years * min_coverage)
    sufficient_coverage = valid_counts >= min_valid_years
    dat_masked = dat.where(sufficient_coverage)

    # Optional detrending
    if dtrend:
        coeffs = dat_masked.polyfit(dim="year", deg=1)
        trend = xr.polyval(dat_masked["year"], coeffs.polyfit_coefficients)
        dat_out = dat_masked - trend
    else:
        dat_out = dat_masked

    return dat_out

# -------------------------------------------------------
# User settings
# -------------------------------------------------------

start_year = 1948
end_year = 2025

# Set to False to retain the long-term trend
use_detrended_data = True


# -------------------------------------------------------
# Read SST
# -------------------------------------------------------
indir = Path("../../data_raw")
sst_file = indir / "HadISST_sst.nc"

ds_sst = xr.open_dataset(sst_file)
sst = ds_sst["sst"]

sst = sst.where((sst != -1000) & (sst != -1.0e30))

# Rename coordinates to match the course examples
sst = sst.rename({"latitude": "lat","longitude": "lon"})

# -------------------------------------------------------
# Read precipitation data
# -------------------------------------------------------
# Step 1:
# Read the monthly precipitation dataset and
# store the precipitation variable as "prc".
#
# prc: monthly precipitation data
#
# Hint:
# Use ncdump to identify the variable and coordinate names.
#
# ncdump ../../data/prate.mon.mean.nc | less
#



# -------------------------------------------------------
# Annual mean anomalies
# -------------------------------------------------------

sst_anom = calc_seasonal_anom(sst,window=12,end_month=12)

# Step 2:
# Calculate the annual mean precipitation anomalies
# using calc_seasonal_anom() function.
#

prc_anom =

# Select the analysis period
# Restrict both annual anomaly datasets to the user-defined
# start and end years before further analysis.

sst_anom = sst_anom.sel(year=slice(start_year, end_year))
prc_anom = prc_anom.sel(year=slice(start_year,end_year))


# -------------------------------------------------------
# Regional averaged SST
# -------------------------------------------------------

# Tropical Pacific
tp_lat1, tp_lat2 = 10, -10
tp_lon1, tp_lon2 = 140, 280

tp_sst = regional_weighted_mean(sst_anom,
    tp_lat1, tp_lat2, tp_lon1, tp_lon2)


# -------------------------------------------------------
# Optional detrending
# -------------------------------------------------------


if use_detrended_data:
    sst_for_corr = linear_detrend(sst_anom)
    prc_for_corr = linear_detrend(prc_anom)
    tp_sst_for_corr = linear_detrend(tp_sst)
    analysis_label = "Detrended"
else:
    sst_for_corr = sst_anom_ann
    prc_for_corr = prc_anom_ann
    to_sst_for_corr = tp_sst
    analysis_label = "Annual Anomaly"


# -------------------------------------------------------
# Grid-point correlation
# -------------------------------------------------------

# Match the years shared by precipitation and Tropical Pacific SST
prc_for_corr, tp_sst_for_corr = xr.align(
    prc_for_corr, tp_sst_for_corr, join="inner")

# Calculate a Pearson correlation coefficient at 
# every latitude–longitude grid point.
corr_map = xr.corr(prc_for_corr, tp_sst_for_corr, dim="year")

# Add a cyclic longitude point to remove the seam at 180°
corr_cyclic, lon_cyclic = add_cyclic_point(
    corr_map.values, coord=corr_map.lon.values)

# Reconstruct xarray DataArray
corr_cyclic_xr = xr.DataArray(corr_cyclic,
    coords={"lat": corr_map.lat,"lon": lon_cyclic},
    dims=("lat", "lon"), name="Correlation coefficient",
    attrs=sst_for_corr.attrs)
print(corr_cyclic_xr)

# -------------------------------------------------------
# Create figure
# -------------------------------------------------------
# Create a figure with different-sized panels:

fig, axes = plt.subplots(
    2, 1, figsize=(12, 8),
    gridspec_kw={"height_ratios": [1, 2]},
    constrained_layout=True, squeeze=False)
print(axes.shape)

# Replace the upper Matplotlib Axes with Cartopy GeoAxes
axes[1, 0].remove()

proj = ccrs.Robinson(central_longitude=180)
axes[1, 0] = fig.add_subplot(2, 1, 2, projection=proj)


# Tropical Pacific SST 3.4 time series
axes[0, 0].plot(
    tp_sst_for_corr.year, tp_sst_for_corr,
    linewidth=1.8, label=f"Tropical Pacific SST {analysis_label}")

axes[0, 0].axhline(0, color="black", linewidth=0.8)
axes[0, 0].set_xlabel("Year")
axes[0, 0].set_ylabel("SST Anomaly (°C)")
axes[0, 0].set_title(f"Tropical Pacific {analysis_label} SST Anomaly")
axes[0, 0].grid(True)
axes[0, 0].legend()

# Correlation map

# Step 4: Plot the global correlation map
#
# Complete the xarray plot.contourf() function.
#
# Hint:
# Use the global correlation DataArray with cyclic longitude.
# Specify the following plotting parameters:
#   ax: Lower-left map panel (row=1, column=0)
#   transform: PlateCarree projection for the input data.
#   levels:  Contour levels for correlation coefficients
#   cmap:    Colormap for positive and negative correlation.

levels = np.arange(-1.0, 1.01, 0.1)

____.plot.contourf(
    ax=,        # Map axes: axes[1, 0]
    transform=, # PlateCarree projection (the original data format)
    level=,     # Contour levels
    cmap=,      # Colormap
    extend="both",
    cbar_kwargs={"label": "Correlation Coefficient","orientation": "horizontal",
        "pad": 0.06, "shrink": 0.85})

# Do not cover the correlation field over land
# axes[1, 0].add_feature(cfeature.LAND, facecolor="lightgray", zorder=2)

axes[1, 0].add_feature(cfeature.BORDERS, linewidth=0.4, zorder=3)
axes[1, 0].coastlines(linewidth=0.8, zorder=3)

# Draw latitude and longitude gridlines (no top labels)
axes[1, 0].gridlines(draw_labels={"bottom": "x", "left": "y", "right": "y"},
    linewidth=1,color="gray", alpha=0.5, linestyle="--")
axes[1, 0].set_global()

# Draw Tropical Pacific box
box_lon = [tp_lon1, tp_lon2, tp_lon2, tp_lon1, tp_lon1]
box_lat = [tp_lat1, tp_lat1, tp_lat2, tp_lat2, tp_lat1]

axes[1, 0].plot(
    box_lon,box_lat,
    color="black", linewidth=1.5,
    transform=ccrs.PlateCarree())

axes[1, 0].set_title(
    f"Correlation of Global precipitation with Tropical Pacific {analysis_label}")

output_path = Path(__file__).with_suffix(".jpg")
plt.savefig(output_path, dpi=300)
plt.show()
