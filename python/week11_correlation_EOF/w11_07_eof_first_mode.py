# -------------------------------------------------------------
# EOF1 and Global SST Correlation
# -------------------------------------------------------------

from pathlib import Path

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from eofs.xarray import Eof
import sys

import warnings
warnings.filterwarnings(
    "ignore",
    message="invalid value encountered in create_collection",
    category=RuntimeWarning,
)

def calc_seasonal_anom(dat, window=12, end_month=12, clim_period=None):
    """
    Calculate seasonal mean anomaly using a trailing running mean, extract the final month (e.g., Mar for NDJFM),
    convert to year-lat-lon DataArray, apply minimum coverage mask, and optionally remove trend.

    Parameters:
    -----------
    dat : xr.DataArray
        Input data with dimensions (time, lat, lon) and datetime64 'time'.
    window : int
        Running mean window size (default is 12).
    end_month : int
        Target month used to extract seasonal means (final month of the trailing average).
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

def linear_detrend(
    dat,
    min_coverage=0.9,
    dtrend=True,
    trend_period=None,
    return_trend=False
):
    """
    Remove the long-term linear trend from annual data.

    Parameters
    ----------
    dat : xr.DataArray
        Annual data with a "year" dimension.
    min_coverage : float
        Minimum fraction of valid years required.
    dtrend : bool
        If True, remove the fitted linear trend.
    trend_period : list, optional
        Start and end dates used to estimate the trend.
    return_trend : bool
        If True, also return the trend line and slope per decade.

    Returns
    -------
    dat_out : xr.DataArray
        Masked annual data with the linear trend removed.
    trend_line : xr.DataArray, optional
        Fitted linear trend evaluated over the full record.
    slope_decade : xr.DataArray, optional
        Linear slope in units per decade.
    """
    if trend_period is None:
        dat_fit = dat
    else:
        start, end = trend_period
        start_year = int(str(start)[:4])
        end_year = int(str(end)[:4])
        dat_fit = dat.sel(year=slice(start_year, end_year))

    # Apply coverage mask
    valid_counts = dat_fit.count(dim="year")
    total_years = dat_fit["year"].size
    min_valid_years = int(total_years * min_coverage)

    sufficient_coverage = valid_counts >= min_valid_years
    dat_masked = dat.where(sufficient_coverage)
    dat_fit_masked = dat_fit.where(sufficient_coverage)

    # Fit the trend using only the selected trend period
    coeffs = dat_fit_masked.polyfit(dim="year", deg=1)

    # Evaluate the fitted line over the full data period
    trend_line = xr.polyval(
        dat_masked["year"],
        coeffs.polyfit_coefficients
    )

    # Extract slope and convert from units/year to units/decade
    slope_year = coeffs.polyfit_coefficients.sel(degree=1)
    slope_decade = slope_year * 10

    if dtrend:
        dat_out = dat_masked - trend_line
    else:
        dat_out = dat_masked

    if return_trend:
        return dat_out, trend_line, slope_decade
    else:
        return dat_out

def compute_eof_analysis(
    datA,
    latlonEOF=(30.0, 50.0, -125.0, -100.0),
    neval=3,
    normalize=False,
    min_coverage=0.9,
):
    """Calculate latitude-weighted EOFs and standardized PCs."""

    # Ensure longitude is 0-360 and sorted.
    if float(datA.lon.min()) < 0:
        datA = datA.assign_coords(
            lon=(datA.lon % 360)
        ).sortby("lon")

    lat_min, lat_max, lon_min, lon_max = latlonEOF

    lon_min = lon_min if lon_min >= 0 else lon_min + 360
    lon_max = lon_max if lon_max >= 0 else lon_max + 360

    # Flip latitude if needed.
    if datA["lat"][0] > datA["lat"][-1]:
        datA = datA.isel(lat=slice(None, None, -1))

    # Subset the EOF domain.
    datA_eof = datA.sel(
        lat=slice(lat_min, lat_max),
        lon=slice(lon_min, lon_max),
    )

    # Latitude weighting.
    clat = np.sqrt(np.cos(np.deg2rad(datA_eof["lat"])))
    clat = clat.broadcast_like(datA_eof)
    datY = datA_eof * clat

    # Standardization gives correlation-based EOFs.
    if normalize:
        dat_std = datY.std(dim="year")
        datY = datY / dat_std

    datY = datY.transpose("year", "lat", "lon")

    # Mask grid points with insufficient temporal coverage.
    valid_count = datY.notnull().sum(dim="year")
    required_count = int(np.ceil(datY.sizes["year"] * min_coverage))
    datY = datY.where(valid_count >= required_count)

    datY = datY.rename({"year": "time"})

    weights = np.sqrt(np.cos(np.deg2rad(datY.lat.values)))[:,np.newaxis]

    solver = Eof(datY,weights=weights)

    eofs = solver.eofsAsCovariance(neofs=neval,pcscaling=1)
    pcs = solver.pcs(npcs=neval,pcscaling=1)
    variance_percent = solver.varianceFraction(neigs=neval) * 100

    pcs = pcs.rename({"time": "year"})

    for mode, value in enumerate(variance_percent.values,start=1):
      print(
        f"EOF{mode} variance explained: "
        f"{value:.1f}%"
      )

    return pcs, eofs, variance_percent

def correlation_with_pcs(dat, pcs):
    """
    Calculate Pearson correlation maps between a climate field
    and all principal-component modes.

    Parameters
    ----------
    dat : xr.DataArray
        Climate field with dimensions (year, lat, lon).
    pcs : xr.DataArray
        Principal components with dimensions (year, mode).

    Returns
    -------
    corr : xr.DataArray
        Correlation maps with dimensions (mode, lat, lon).
    """

    # Match the years shared by the field and PCs
    dat, pcs = xr.align(
        dat,
        pcs,
        join="inner",
    )


    # xarray broadcasts the mode dimension automatically
    corr = xr.corr(
        dat,
        pcs,
        dim="year",
    )

    # Arrange dimensions consistently
    corr = corr.transpose(
        "mode",
        "lat",
        "lon",
    )

    corr.name = "correlation"

    return corr

# -------------------------------------------------------------
# User settings
# -------------------------------------------------------------

indir = Path("../../data_raw")
sst_file = indir / "HadISST_sst.nc"

start_year = 1948
end_year = 2025

# Tropical Pacific EOF domain
lat1, lat2 = -20.0, 20.0
lon1, lon2 = 120.0, 280.0
latlonEOF = (lat1, lat2, lon1, lon2)

# Set False to retain the long-term trend.
use_detrended_data = True

# False: covariance-based EOF
# True: correlation-based EOF
normalize_eof = False


# -------------------------------------------------------------
# Read SST
# -------------------------------------------------------------

ds_sst = xr.open_dataset(sst_file)
sst = ds_sst["sst"]

sst = sst.where(
    (sst != -1000) &
    (sst != -1.0e30)
)

if "latitude" in sst.coords:
    sst = sst.rename({"latitude": "lat"})

if "longitude" in sst.coords:
    sst = sst.rename({"longitude": "lon"})

if bool((sst.lon < 0).any()):
    sst = sst.assign_coords(
        lon=(sst.lon % 360)
    ).sortby("lon")


# -------------------------------------------------------------
# Annual SST anomalies
# -------------------------------------------------------------

sst_djf_anom = calc_seasonal_anom(sst,window=3,end_month=2)
sst_djf_anom = sst_djf_anom.sel(year=slice(start_year, end_year))

# -------------------------------------------------------------
# Optional detrending
# -------------------------------------------------------------

if use_detrended_data:
    sst_analysis = linear_detrend(
        sst_djf_anom,
        min_coverage=0.9,
    )
    analysis_label = "Detrended"
else:
    sst_analysis = sst_djf_anom
    analysis_label = "Annual Anomaly"


# -------------------------------------------------------------
# EOF analysis over the Tropical Pacific: first three modes
# -------------------------------------------------------------

pcs, eofs, variance_percent = compute_eof_analysis(
    sst_analysis,
    latlonEOF=latlonEOF,
    neval=3,
    normalize=normalize_eof,
    min_coverage=0.9,
)

# Optional sign reversal for EOFs and PCs
pcs = -pcs
eofs = -eofs

# Separate individual modes
pc1 = pcs.isel(mode=0)
pc2 = pcs.isel(mode=1)
pc3 = pcs.isel(mode=2)

eof1 = eofs.isel(mode=0)
eof2 = eofs.isel(mode=1)
eof3 = eofs.isel(mode=2)

var1 = variance_percent.isel(mode=0)
var2 = variance_percent.isel(mode=1)
var3 = variance_percent.isel(mode=2)


# -------------------------------------------------------------
# Calculate the correlation of the global SST anomalies onto standardized PC1
# -------------------------------------------------------------

cor_map = correlation_with_pcs(sst_analysis, pcs)


# -------------------------------------------------------------
# Create figure
# -------------------------------------------------------------

fig = plt.figure(
    figsize=(11, 8),
    constrained_layout=True,
)

grid = fig.add_gridspec(
    2,
    1,
    height_ratios=[1, 2],
)


# -------------------------------------------------------------
# PC1 time series
# -------------------------------------------------------------

years = pc1.year.values
values = pc1.values

colors = np.where(
    values >= 0,
    "red",
    "blue",
)

ax0 = fig.add_subplot(grid[0, 0])

ax0.bar(
    years,
    values,
    color=colors,
    width=0.6,
)

ax0.axhline(
    0,
    color="black",
    linewidth=1.0,
)

ax0.set_xlim(start_year-1.,end_year+1.)
ax0.set_ylim(-2., 3.)

ax0.set_xlabel("Year")
ax0.set_ylabel("Standardized PC1")
ax0.set_title(
    f"Tropical Pacific DJF SST PC1 "
    f"({float(var1):.1f}% Variance Explained)"
)
ax0.grid(
    axis="y",
    alpha=0.3,
)


# -------------------------------------------------------------
# Global regression map
# -------------------------------------------------------------

projection = ccrs.Robinson(
    central_longitude=180
)

ax1 = fig.add_subplot(
    grid[1, 0],
    projection=projection,
)

levels = np.arange(-0.9, 0.91, 0.1)

cf = ax1.contourf(
    cor_map.lon,
    cor_map.lat,
    cor_map.isel(mode=0),
    levels=levels,
    cmap="RdBu_r",
    extend="both",
    transform=ccrs.PlateCarree(),
)


ax1.add_feature(
    cfeature.LAND,
    facecolor="lightgray",
    zorder=2,
)
ax1.coastlines(
    linewidth=0.8,
    zorder=3,
)
ax1.add_feature(
    cfeature.BORDERS,
    linewidth=0.4,
    zorder=3,
)
# Draw latitude and longitude lines
ax1.gridlines(draw_labels=True, linewidth=1, color='gray', alpha=0.5, linestyle='--')
ax1.set_global()

# Draw the Tropical Pacific EOF domain.
box_lon = [lon1, lon2, lon2, lon1, lon1]
box_lat = [lat1, lat1, lat2, lat2, lat1]

ax1.plot(
    box_lon,
    box_lat,
    color="black",
    linewidth=1.5,
    transform=ccrs.PlateCarree(),
)

ax1.set_title(
    f"Global DJF SST Correlation onto Tropical Pacific PC1 "
    f"({analysis_label})"
)

cbar = fig.colorbar(
    cf,
    ax=ax1,
    orientation="horizontal",
    pad=0.06,
    shrink=0.85,
)
cbar.set_label("Correlation")

output_path = Path(__file__).with_suffix(".jpg")
plt.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight",
)
plt.show()
