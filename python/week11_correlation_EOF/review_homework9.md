[review_homework9.md](https://github.com/user-attachments/files/31393884/review_homework9.md)
# Homework 9 Review — SST Anomalies and Detrending

This review summarizes one possible solution for Homework 9. The objective was to calculate annual mean SST anomalies, remove the long-term linear trend, and compare the original and detrended SST variability. The analysis uses global SST anomaly maps together with Tropical Pacific mean time series to illustrate how detrending changes the SST anomalies.

---

## Example Output

The figure below compares the annual mean SST anomaly and detrended annual mean SST anomaly for a selected year, together with the corresponding Tropical Pacific mean time series.

The original SST anomaly contains both interannual variability and the long-term SST trend. After removing the fitted linear trend, the detrended anomaly emphasizes variability relative to that long-term change.

---

## Key Steps

### 1. Read the SST dataset

Load the HadISST monthly SST dataset.

```python
ds_file = repo_dir / "data_raw/HadISST_sst.nc"

ds = xr.open_dataset(ds_file)

sst = ds["sst"]
```

Mask land and missing values and rename the latitude and longitude coordinates to match the course examples.

```python
sst = sst.where(sst > -100)

sst = sst.rename({
    "latitude": "lat",
    "longitude": "lon"
})

sst.attrs["units"] = "degC"
```

The SST field is used to calculate annual mean anomalies and their long-term linear trend.

---

### 2. Calculate annual mean SST anomalies

Calculate 12-month mean SST anomalies relative to the 1991–2020 monthly climatology.

```python
clim_start = "1991-01-01"
clim_end = "2020-12-31"

anom = calc_seasonal_anom(
    sst,
    window=12,
    end_month=12,
    clim_period=[clim_start, clim_end]
)
```

The monthly climatology is first removed from the SST field. A 12-month running mean ending in December is then used to obtain the annual mean anomaly for each year.

Therefore, the resulting `anom` field has dimensions:

```text
year × latitude × longitude
```

---

### 3. Calculate detrended annual SST anomalies

Remove the long-term linear trend from the annual mean SST anomaly field.

```python
trend_start = "1949-01-01"
trend_end = "2020-12-31"

anom_detrended, trend_line, slope_decade = linear_detrend(
    anom,
    trend_period=[trend_start, trend_end],
    return_trend=True
)
```

The `linear_detrend()` function returns:

- `anom_detrended`: annual SST anomalies after removing the fitted trend
- `trend_line`: fitted linear trend evaluated over the full record
- `slope_decade`: linear SST trend in degC per decade

Conceptually,

```text
Annual SST anomaly
        ↓
Estimate linear trend
        ↓
Annual SST anomaly − fitted trend
        ↓
Detrended SST anomaly
```

Detrending removes the fitted long-term linear component while retaining shorter-timescale SST variability.

---

### 4. Calculate the Tropical Pacific mean time series

Define the Tropical Pacific region:

```python
lat1, lat2 = 20, -20
lon1, lon2 = 120, 220
```

This corresponds to:

```text
20°N–20°S
120°E–220°E
```

Calculate cosine-latitude-weighted regional means for the original anomaly, detrended anomaly, and fitted trend.

```python
reg_anom = regional_weighted_mean(
    anom,
    lat1, lat2,
    lon1, lon2
)

reg_detrended = regional_weighted_mean(
    anom_detrended,
    lat1, lat2,
    lon1, lon2
)

reg_trend = regional_weighted_mean(
    trend_line,
    lat1, lat2,
    lon1, lon2
)
```

Cosine-latitude weighting accounts for the decreasing surface area represented by longitude–latitude grid cells toward higher latitudes.

The Tropical Pacific trend is also calculated in degC per decade.

```python
_, _, reg_slope_decade = linear_detrend(
    reg_anom,
    trend_period=[trend_start, trend_end],
    return_trend=True
)
```

The underscore `_` is used for returned variables that are not needed.

---

### 5. Select a year for comparing the spatial patterns

Select one year from both the original and detrended SST anomaly fields.

```python
target_year = 1969

anom_target = anom.sel(
    year=target_year
)

detrended_target = anom_detrended.sel(
    year=target_year
)
```

The corresponding Tropical Pacific mean values are also selected.

```python
reg_anom_target = reg_anom.sel(
    year=target_year
)

reg_detrended_target = reg_detrended.sel(
    year=target_year
)
```

Using the same year allows the effect of detrending on the SST anomaly pattern to be compared directly.

---

### 6. Plot the original and detrended SST anomaly maps

Plot the annual mean SST anomaly using `contourf()`.

```python
cf1 = axes[0, 0].contourf(
    lon_cyclic,
    anom_target.lat,
    anom_cyclic,
    levels=levels,
    cmap=cmap,
    extend="both",
    transform=ccrs.PlateCarree()
)
```

Then plot the detrended anomaly using the same contour levels and colormap.

```python
cf2 = axes[0, 1].contourf(
    lon_cyclic,
    detrended_target.lat,
    detrended_cyclic,
    levels=levels,
    cmap=cmap,
    extend="both",
    transform=ccrs.PlateCarree()
)
```

The same contour levels are important because both fields have the same units. This allows the magnitude and spatial structure of the original and detrended SST anomalies to be compared directly.

For the example year, 1969, removing the long-term trend changes both the magnitude and spatial distribution of the anomaly because the fitted long-term SST component has been removed.

---

### 7. Plot the Tropical Pacific anomaly and linear trend

Plot the Tropical Pacific annual mean SST anomaly.

```python
axes[1, 0].plot(
    year,
    reg_anom,
    linewidth=1.5,
    color="black",
    label="Tropical Pacific annual anomaly"
)
```

Add the fitted linear trend.

```python
axes[1, 0].plot(
    year,
    reg_trend,
    linewidth=2.0,
    color="red",
    label=f"Trend = {float(reg_slope_decade):.2f} degC/decade"
)
```

The example calculation gives a positive Tropical Pacific SST trend over the selected 1949–2020 trend period.

The annual anomaly time series therefore contains both:

```text
Long-term SST change
        +
Interannual and decadal variability
```

---

### 8. Plot the detrended Tropical Pacific anomaly

Plot the Tropical Pacific detrended annual anomaly.

```python
axes[1, 1].plot(
    year,
    reg_detrended,
    linewidth=1.5,
    color="black",
    label="Tropical Pacific detrended annual anomaly"
)
```

After detrending, the fitted linear component has been removed.

Conceptually,

```text
Original anomaly
      ↓
Remove fitted linear trend
      ↓
Detrended anomaly
      ↓
Variability around the long-term trend
```

The detrended time series is therefore more appropriate when the objective is to examine SST variability without the fitted long-term linear change.

---

## Summary

Homework 9 introduces linear detrending of climate data.

The main analysis sequence is:

```text
Monthly SST
    ↓
Remove 1991–2020 monthly climatology
    ↓
Annual mean SST anomalies
    ↓
Estimate 1949–2020 linear trend
    ↓
Remove fitted trend
    ↓
Detrended annual SST anomalies
```

The map comparison shows how removing the long-term trend modifies the SST anomaly field for an individual year, while the Tropical Pacific time series shows the temporal component that is removed.

The important distinction is:

```text
Original SST anomaly
= long-term linear change + shorter-timescale variability

Detrended SST anomaly
= original anomaly − fitted linear trend
```

Detrending is useful when the scientific objective is to focus on interannual or decadal climate variability rather than the fitted long-term change.
