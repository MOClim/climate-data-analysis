# Homework 8 Review — Regional Temperature and Precipitation Anomalies

This review summarizes one possible solution for Homework 8. 
The objective was to calculate regional annual anomalies of 2-m air temperature and precipitation rate using cosine-latitude area weighting, then compare their long-term behavior in a two-panel time series. The sample solution demonstrates one implementation for the North America region.

## Example Output

The figure below shows the annual anomalies of regional mean temperature and precipitation for North America.

**(a) North America Mean 2-m Air Temperature Anomaly**
Annual mean temperature anomalies relative to the monthly climatology.
A clear warming trend is evident after the 1980s.
**(b) North America Mean Precipitation Rate Anomaly**
Annual precipitation anomalies relative to the monthly climatology.
Large year-to-year fluctuations are present, while the long-term trend is much weaker than for temperature.

---
### Key Steps
#### 1. Read the datasets

Load the two monthly reanalysis datasets.
```python
ds_air = xr.open_dataset(air_file)
ds_pr  = xr.open_dataset(pr_file)

air   = ds_air["air"]
prate = ds_pr["prate"]
```

---
#### 2. Convert units

The datasets use different units than those desired for plotting.

**Temperature (K -> C)**
air = air - 273.15

**Precipitation (kg m⁻² s⁻¹ -> mm day⁻¹)**
prate = prate * 86400

---
#### 3. Calculate the regional area-weighted mean

The most important new concept in this homework is computing a regional mean using cosine-latitude weighting.

```python
weights = np.cos(np.deg2rad(dat_region["lat"]))

dat_region_mean = dat_region.weighted(weights).mean(
    dim=["lat","lon"]
)
```
Why use cosine(latitude)?
- Grid cells become smaller toward the poles.
- A simple arithmetic mean would overrepresent high-latitude grid cells.
- Cosine weighting provides a more accurate regional average.

---
#### Calculate annual anomalies

Monthly climatology is first removed, then annual means are computed.
```python
clim = monthly_mean.groupby("time.month").mean("time")
anom = monthly_mean.groupby("time.month") - clim
anom_ann = anom.resample(time="YS").mean()
```

---
#### 5. Create a two-panel figure

The figure is created using
```python
fig, axes = plt.subplots(
    2, 1,
    sharex=True
)
```
**Panel (a)**
Regional temperature anomaly

**Panel (b)**
Regional precipitation anomaly

Both panels include
- zero reference line
- axis labels
- titles
- grid lines
- common x-axis

---
### Discussion Questions
- Does your selected region show a clear warming trend?
- Does precipitation show a similar long-term trend?
- Which variable has stronger year-to-year variability?
- Why might temperature and precipitation behave differently?
