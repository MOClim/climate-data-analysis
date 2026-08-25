# Homework 10 Review — ENSO and Global Precipitation

This review summarizes one possible solution for Homework 10. The objective was to extend the Tropical Pacific SST EOF analysis by calculating the correlation between the SST-derived principal components (PCs) and global DJF precipitation anomalies. The EOF modes are calculated from detrended Tropical Pacific SST, while the correlation maps show the precipitation patterns associated with each SST PC.

---

## Key Steps

### 1. Read the SST and precipitation datasets

Load the HadISST SST dataset and monthly precipitation dataset.

```python
sst_file = repo_dir / "data_raw" / "HadISST_sst.nc"

ds_sst = xr.open_dataset(sst_file)
sst = ds_sst["sst"]

prc_file = repo_dir / "data_raw" / "prate.mon.mean.nc"

ds_prc = xr.open_dataset(prc_file)
prc = ds_prc["prate"]
```

The SST field is used to calculate the EOF modes and PCs. The precipitation field is used later to calculate global correlation maps.

---

### 2. Calculate DJF SST and precipitation anomalies

Calculate 3-month seasonal anomalies ending in February.

```python
sst_anom = calc_seasonal_anom(
    sst,
    window=3,
    end_month=2
)

sst_anom = sst_anom.sel(
    year=slice(start_year, end_year)
)

prc_anom = calc_seasonal_anom(
    prc,
    window=3,
    end_month=2
)

prc_anom = prc_anom.sel(
    year=slice(start_year, end_year)
)
```

Because the 3-month running mean ends in February, each seasonal value represents December–January–February (DJF).

---

### 3. Select the Tropical Pacific SST domain

The EOF analysis is performed over the Tropical Pacific:

```python
lat1, lat2 = -20.0, 20.0
lon1, lon2 = 120.0, 280.0
```

Select this region from the global SST anomalies.

```python
sst_tp = sst_anom.sel(
    lat=lat_slice,
    lon=slice(lon1, lon2),
)
```

The precipitation anomalies remain global because the objective is to examine global precipitation patterns associated with Tropical Pacific SST variability.

```python
prc_global = prc_anom
```

---

### 4. Detrend SST and precipitation anomalies

Remove the long-term linear trend before calculating EOFs and correlations.

```python
sst_analysis = linear_detrend(
    sst_tp,
    min_coverage=0.9,
)

prc_global_analysis = linear_detrend(
    prc_global,
    min_coverage=0.9,
)
```

Detrending emphasizes interannual climate variability rather than long-term changes in SST and precipitation.

---

### 5. Calculate the first three Tropical Pacific SST EOF modes

Calculate three EOF modes from the detrended Tropical Pacific SST anomalies.

```python
pcs, eofs, variance_percent = compute_eof_analysis(
    sst_analysis,
    latlonEOF=latlonEOF,
    neval=3,
    normalize=normalize_eof,
    min_coverage=0.9,
)
```

The EOF analysis returns:

- `pcs`: principal-component time series
- `eofs`: EOF spatial patterns
- `variance_percent`: percentage of variance explained by each mode

For the example solution, PC1 represents the dominant mode of Tropical Pacific SST variability and explains substantially more variance than PC2 and PC3.

---

### 6. Calculate global precipitation correlations with the SST PCs

This is the major modification from the previous SST EOF exercise.

Instead of correlating the SST PCs with global SST anomalies, correlate the PCs with **global precipitation anomalies**.

```python
cor_map = correlation_with_pcs(
    prc_global_analysis,
    pcs,
    min_coverage=0.9,
)
```

The EOF modes and PCs still come from Tropical Pacific SST:

```text
Tropical Pacific SST
        ↓
      EOFs
        ↓
    PC1, PC2, PC3
        ↓
Global precipitation correlations
```

Therefore, each correlation map shows where DJF precipitation tends to vary with the corresponding Tropical Pacific SST mode.

---

### 7. Plot the precipitation correlation maps

Extract the correlation map for each PC inside the plotting loop.

```python
cdat = cor_map.isel(
    mode=mode
)
```

Plot the correlations using a diverging colormap.

```python
cf = ax_map.contourf(
    cdat.lon,
    cdat.lat,
    cdat,
    levels=levels,
    cmap="BrBG",
    extend="both",
    transform=ccrs.PlateCarree(),
)
```

A diverging colormap is appropriate because correlation coefficients contain both positive and negative values.

---
## Example Output

The resulting figure combines the PC time series with the corresponding global precipitation correlation patterns, allowing the SST modes and their associated precipitation variability to be examined together.

PC1 explains the largest fraction of Tropical Pacific SST variance. The precipitation correlation maps show how global precipitation variability is related to each SST EOF mode.
