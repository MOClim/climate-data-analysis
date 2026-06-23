# Day 16: Advanced Visualization for Climate Time Series

## Overview

In this lesson, we will improve climate time-series visualization using Python. We will compare temperature and precipitation anomalies across regions and variables using one-panel, multi-panel, and two-panel figures.

## Learning Objectives

By the end of this lesson, students will be able to:
* Create customized climate time-series plots
* Use major and minor grid lines
* Compare multiple regions on one figure
* Create multi-panel figures using `plt.subplots()`
* Plot temperature and precipitation anomalies
* Interpret regional and global climate variability

---
## Excersie 1: Understand the Reanalysis Dataset

### Step 1: Download of the Reanalysis Dataset

This lesson uses NOAA NCEP/NCAR Reanalysis monthly data. Temperature data is available at `../../data/air.2m.mon.mean.nc`.
Download monthly precipitation rate data (`prate.mon.mean.nc`).

Data source:
https://psl.noaa.gov/data/gridded/data.ncep.reanalysis.html

Required files:

```bash
mv ~/Downloads/prate.mon.mean.nc ../../data_raw/
```

### Step 2: Check NetCDF File Structure

Before running the scripts, check the data structure using `ncdump`.

```bash
ncdump -h ../../data/air.2m.mon.mean.nc
```
```bash
ncdump -h ../../data_raw/prate.mon.mean.nc
```

Look for:

```text
dimensions:
    time
    lat
    lon

variables:
    air(time, lat, lon)
    prate(time, lat, lon)
```

Important points:

* `air` is 2-m air temperature.
* `prate` is precipitation rate.
* Latitude may be ordered from north to south.
* Longitude may be expressed from 0° to 360°E.

---

### Exercise 2: Regional Precipitation Anomaly

Script:

```text
cp w08_06_precip_area-average.sample.py w08_06_precip_area-average.py
```

This program calculates area-averaged precipitation rate anomalies for a selected region.

Students will modify:

```python
filein = indir / ""
var_name = ""
region_name = ""

lat_str, lat_end = , 
lon_str, lon_end = , 
```

Precipitation unit conversion:

```python
prate = prate * 86400
```

This converts:

```text
kg m-2 s-1 → mm/day
```

Exercise:

1. Download `prate.mon.mean.nc`.
2. Set the correct data path.
3. Set `var_name = "prate"`.
4. Choose a region.
5. Plot annual precipitation anomalies.

---

### Exercise 3: Three-Panel Regional Temperature Time Series

Script:
```text
w08_07_three_region_timeseries.py
```

This program plots three regional temperature anomaly time series in separate panels.

Regions:
```python
regions = [
    ("North America", 75, 15, 190, 310),
    ("Tropical Pacific", 20, -20, 120, 280),
    ("Arctic", 90, 60, 0, 360),
]
```

Key visualization method:
```python
fig, axes = plt.subplots(
    3, 1,
    figsize=(10, 8),
    sharex=True,
    sharey=True
)
```

Exercise:

1. Change one of the regions.
2. Modify the y-axis range.
3. Compare which region shows the largest variability.
4. Explain why the Arctic and Tropical Pacific behave differently.

---
### Exercise 4: Three Regional Time Series on One Panel

Script:
```bash
cp w08_08_three_region_timeseries_onepanel.sample.py w08_08_three_region_timeseries_onepanel.py
```

This program plots three regional temperature anomaly time series on one panel.

This figure is useful for directly comparing:
- amplitude
- interannual variability
- long-term warming
- regional differences

Key plotting structure:
```python
for name, lat1, lat2, lon1, lon2 in regions:
    reg_mean = regional_weighted_mean(air, lat1, lat2, lon1, lon2)
    reg_anom = annual_anomaly(reg_mean)

    plt.plot(
        reg_anom.time.dt.year,
        reg_anom,
        linewidth=1.5,
        label=name
    )
```

Exercise:

1. Add a fourth region.
2. Change line thickness.
3. Modify the legend location.
4. Identify which region shows the strongest warming.

---

### Exercise 5: Global Temperature and Precipitation Two-Panel Plot

Script:
```bash
w08_09_global_temp_precip_twopanel.py
```

This program compares global mean temperature and precipitation anomalies in two panels.

Variables:

```text
air   → 2-m air temperature
prate → precipitation rate
```

Unit conversions:

```python
air = air - 273.15
prate = prate * 86400
```

Key functions:

```python
global_weighted_mean()
annual_anomaly()
```

Exercise:

1. Compare the trend in temperature and precipitation.
2. Which variable shows a clearer long-term trend?
3. Which variable has stronger year-to-year variability?
4. Why is precipitation noisier than temperature?

#### Key Visualization Skills

Today’s scripts introduce:
```python
plt.subplots()
```

for multi-panel figures,
```python
plt.legend()
```

for comparing multiple time series,
```python
MultipleLocator()
```

for minor tick spacing,

and
```python
plt.grid(which="major")
plt.grid(which="minor")
```
---

### Homework 7: Regional Temperature and Precipitation Anomalies

## Task
Create a two-panel time series plot showing:
1. Regional mean 2-m air temperature anomaly
2. Regional mean precipitation rate anomaly

Choose **one region** and analyze both variables for the same latitude–longitude box.
Use the sample program as a reference:
```text
cp w08_09_global_temp_precip_twopanel.py w08_10_regional_temp_precip_twopanel.HW.py
```

## Required Information
Choose one region from the list below or define your own region.

### Example Regions

```text
North America
Latitude : 75°N to 15°N
Longitude: 190°E to 310°E

Tropical Pacific
Latitude : 20°N to 20°S
Longitude: 120°E to 280°E

Southern Ocean
Latitude : 90°S to 60°S
Longitude: 0°E to 360°E

Europe
Latitude : 70°N to 35°N
Longitude: 10°W to 40°E
```

## Datasets
### Dataset 1: Air Temperature
```text
File name: air.2m.mon.mean.nc
Variable name: air
Unit: °C
```

### Dataset 2: Precipitation Rate
```text
File name: prate.mon.mean.nc
Variable name: prate
Unit: mm/day
```

Data source: NOAA Physical Sciences Laboratory
https://psl.noaa.gov/data/gridded/data.ncep.reanalysis.html

## Requirements
Your figure must include:
- Two panels using `plt.subplots()`
- Regional area-weighted averages using cosine-latitude weighting
- Annual anomalies relative to monthly climatology
- Region name in the figure title
- Proper axis labels and units
- Panel labels for temperature and precipitation

## Questions
Answer in 2–4 sentences on word/google docs:
1. Does your selected region show a clear warming trend?
2. Does precipitation show a similar long-term trend?
3. Which variable has stronger year-to-year variability?
4. Why might temperature and precipitation behave differently?

## Submission
Upload the following files to the Canvas Homework 7 page:
```text
w08_10_regional_temp_precip_twopanel.HW.py
w08_10_regional_temp_precip_twopanel.HW.jpg
questions.pdf
```


---

### Homework 7: Global Temperature and Precipitation Anomalies

### Task
Create a two-panel time series plot showing:
1. Global mean 2-m air temperature anomaly
2. Global mean precipitation rate anomaly

using NOAA NCEP/NCAR Reanalysis data.

Use the sample program:

```text
cp w08_09_global_temp_precip_twopanel.py w08_10_global_temp_precip_twopanel.HW.py
```

### Required Information

#### Dataset 1: Global Air Temperature

File name:
```text
air.2m.mon.mean.nc
```

Variable name:
```python
air (°C)
```

#### Dataset 2: Global Precipitation Rate

File name:
```text
prate.mon.mean.nc
```

Variable name:
```python
prate (mm/day)
```

#### Data Source
NOAA Physical Sciences Laboratory (PSL)
https://psl.noaa.gov/data/gridded/data.ncep.reanalysis.html

#### Requirements
Your figure must include:
- Two panels using `plt.subplots()`
- Global area-weighted averages using cosine-latitude weighting
- Annual anomalies relative to monthly climatology
- Proper axis labels and units
- Figure title and panel labels

#### Submission
Upload the following files to the Canvas Homework 7 page:
```text
w08_10_global_temp_precip_twopanel.HW.py
w08_10_global_temp_precip_twopanel.HW.jpg
```

---
### Key Takeaway
- Effective visualization helps reveal climate signals and variability more clearly.
- Multi-panel figures allow comparison of multiple regions or variables in one figure.
- Temperature anomalies generally show clearer long-term warming trends than precipitation anomalies.
- Climate variability differs substantially between land, ocean, and polar regions.
