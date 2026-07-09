# Day 19: Climatology and Seasonality

## Overview

Climate data contain both long-term climate signals and regular seasonal variations. Before studying climate variability or long-term trends, it is important to understand the seasonal cycle and define a climatological reference period.

In this lesson, you will calculate monthly and seasonal climatology, compare different definitions of anomalies, and examine how monthly anomalies are combined into annual mean anomalies.

---

## Objectives

By the end of this lesson, you will be able to:
- Calculate regional monthly climatology.
- Visualize seasonal cycles of temperature and precipitation.
- Plot global climatology maps for the four meteorological seasons.
- Understand the difference between long-term mean anomalies and monthly climatology anomalies.
- Calculate annual mean anomalies from monthly anomalies.
- Apply the same workflow to sea surface temperature (SST).

---

### Exercise 1: Regional Seasonal Cycle

In the previous homework sample, annual-mean anomalies of 2-m air temperature and precipitation were calculated for North America.

```bash
python w08_10_regional_temp_precip_twopanel.HW.sample.py
```
Those anomalies were calculated by removing the climatological seasonal cycle.

In this exercise, we examine the climatology that was removed.

```bash
python w10_01_regional_seasonal_cycle.py
```
```python
clim_start = "1991-01-01"
clim_end = "2020-12-31"
air_clim = air_NA.sel(time=slice(clim_start, clim_end)).groupby("time.month").mean("time")
pr_clim = pr_NA.sel(time=slice(clim_start, clim_end)).groupby("time.month").mean("time")
```
These commands calculate the 1991–2020 monthly climatology for temperature and precipitation.

---

### Exercise 2: Global Seasonal Climatology Maps

Plot global climatological temperature for the four meteorological seasons (DJF, MAM, JJA, and SON).

Sample program:
```bash
python w10_02_global_seasonal_climatology_maps.py
```

```python
    # Select the climatology period
    data_clim = data.sel(time=slice(clim_start, clim_end))

    # Group by meteorological season and average over all years
    clim_season = data_clim.groupby("time.season").mean("time")

    # Reorder seasons for plotting
    clim_season = clim_season.sel(season=["DJF", "MAM", "JJA", "SON"])
```
`groupby("time.season")` groups the monthly data into the four meteorological seasons: 
DJF (December–February), MAM (March–May), JJA (June–August), and SON (September–November).

---

### Exercise 3: Monthly Anomalies

Compare two commonly used anomaly definitions.

**Long-term mean anomaly**
```
Monthly value − long-term mean
```
The seasonal cycle remains.

**Monthly climatology anomaly**
```
Monthly value − monthly climatology
```
The seasonal cycle is removed. Natural variability on interannual timescales appears, instead.

```bash
python w10_03_regional_monthly_anomaly_comparison.py
```
```python
# Anomaly relative to one long-term mean
clim_mean = monthly_mean.sel(time=slice(clim_start, clim_end)).mean("time")
anom_mean = monthly_mean - clim_mean

# Anomaly relative to monthly climatology
clim = monthly_mean.sel(time=slice(clim_start,clim_end)
       ).groupby("time.month").mean("time")
anom = monthly_mean.groupby("time.month") - clim
```
Both time series use monthly data. 
The long-term mean anomaly still contains the seasonal cycle, whereas the monthly climatology anomaly removes it, making year-to-year climate variability much easier to identify.

---

### Exercise 4: Annual Mean Anomalies

Calculate annual mean anomalies by averaging monthly anomalies.

Workflow:
```
Monthly data
        ↓
Monthly climatology
        ↓
Monthly anomaly
        ↓
Annual mean anomaly
```

To examine annual mean anomalies, revise the sample program.
```bash
cp w10_04_regional_anomaly.sample.py w10_04_regional_anomaly.py
```

Complete the following tasks:

- Calculate annual mean anomalies from monthly anomalies.
- Plot monthly and annual mean precipitation anomalies on the same figure.

Then execute the program:
```bash
python w10_04_regional_anomaly.py
```
The resulting figure compares monthly and annual mean anomalies. 
The monthly anomalies show higher-frequency variability, 
while the annual mean anomalies smooth out the monthly fluctuations and highlight lower-frequency (year-to-year) climate variability.

---

### Exercise 5: SST Example

Apply the same climatology and anomaly calculations to sea surface temperature.

Topics include:
- Reading HadISST data
- Monthly climatology
- Monthly anomaly
- Annual mean anomaly
- Regional SST time series

To calculate the annual mean anomaly of North Atlantic SST, revise the sample program.
```bash
cp w10_05_regional_sst_anomaly.sample.py w10_05_regional_sst_anomaly.py
```

Complete the following steps:
- Check a variable name of HadISST data using
  ```bash
  ncdump ../../data_raw/HadISST_sst.nc |less
  ```
- Read `../../data_raw/HadISST_sst.nc`
- Extract the SST variable
- Calculate monthly SST anomalies relative to the 1991–2020 monthly climatology using `monthly_climatology_anomaly()`
- Calculate annual mean anomalies by averaging monthly anomalies within each year using `resample(time="YE").mean()`

Then execute the program:
```bash
python w10_05_regional_sst_anomaly.py
```
This exercise applies the same anomaly calculation workflow to an ocean surface temperature dataset.

---

## Key Concepts

### Climatology
A climatology is the average climate calculated over a specified reference period.

For this course:
```
1991–2020
```
is used as the climatological reference period.

---

### Seasonal Cycle

The seasonal cycle represents the regular annual variation caused primarily by Earth's revolution around the Sun and the seasonal distribution of solar radiation.

---

### Monthly Climatology

Monthly climatology is the average value for each calendar month.

Example:
```
January climatology
= average of all January values
during 1991–2020.
```

---

### Monthly Anomaly

Monthly anomaly is calculated as
```
Monthly anomaly
=
Monthly value
−
Monthly climatology
```
This removes the regular seasonal cycle.

---

### Annual Mean Anomaly

Annual mean anomaly is obtained by averaging the twelve monthly anomalies within each year.
```
12 monthly anomalies
        ↓
Annual mean anomaly
```

---

## Key Takeaways
- Monthly climatology represents the average seasonal cycle over a reference period.
- Monthly climatology removes the regular seasonal cycle when calculating anomalies.
- Monthly climatology anomalies highlight climate variability more clearly than anomalies relative to a single long-term mean.
- Annual mean anomalies summarize year-to-year climate variability by averaging monthly anomalies.
- The same climatology and anomaly workflow can be applied to different climate variables, including air temperature, precipitation, and sea surface temperature (SST).
