# Day 15: Area-Averaged Temperature Analysis

## Learning Objectives

By the end of this lesson, students will be able to:

Inspect the structure of a NetCDF climate dataset
Visualize global temperature fields on a map
Compute area-weighted regional averages
Compare temperature variability among different regions
Understand the concepts of climatology and anomalies

### Dataset
This lesson uses monthly 2-m air temperature from the NOAA NCEP/NCAR Reanalysis. 

#### Data source
NOAA NCEP/NCAR Reanalysis Data
```bash
air.2m.mon.mean.nc
```
---
### Examine the NetCDF Structure

Before performing any analysis, inspect the file structure using ncdump.

```bash
ncdump -h air.2m.mon.mean.nc
```

```text
Example output:

dimensions:
    lon = 144 ;
    lat = 73 ;
    time = UNLIMITED ;

variables:
    float air(time, lat, lon) ;
```
Questions:
- What are the dimensions of the dataset?
- What variable stores temperature?
- How are latitude, longitude, and time represented?

---
### Exercise 1: Plot a Global Temperature Map

Program:
```text
w08_01_global_temp_map_rotated.py
```
This script visualizes monthly climatological temperature on a global map and demonstrates Cartopy projections. 
It also shows how to change the map center using `central_longitude`.

```python
# Create a Atlantic-centered map (0° longitude at the center).
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

# Create a Pacific-centered map (180° longitude at the center).
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(central_longitude=180))
```

---
### Exercise 2: Compute a Regional Average

```bash
w08_02_area_average_NA.py
```
This script computes an area-weighted average temperature over North America using cosine-latitude weighting.

Key concept:
Because grid cells become smaller toward the poles, latitude weighting is required when computing regional averages.
```python
weights = np.cos(np.deg2rad(lat))
```

---
### Exercise 3: Create Your Own Regional Analysis

```bash
cp w08_03_area_averaged.sample.py w08_03_area_averaged.py 
```

Modify the latitude and longitude boundaries and assign a region name.

#### Exercise
- Choose a region and Modify the latitude and longitude boundaries.
- Update the region name.
- Generate a regional temperature time series.

#### Questions:
- Does the region show long-term warming?
- Which years appear unusually warm or cold?

---
### Exercise 4: Compare Two Regions

```bash
w08_04_area-averaged_comparison.py
```
This script compares temperature anomalies between two regions.

#### Why use anomalies?
Different regions have different average temperatures.
To compare climate variability, we remove the average seasonal cycle:
```
Anomaly = Temperature − Monthly Climatology
```
```python
# Monthly climatology
clim = regional_mean.groupby("time.month").mean("time")

# Monthly anomaly
anom = regional_mean.groupby("time.month") - clim

# Annual mean anomaly
anom_ann = anom.resample(time="YS").mean()
```    
Positive anomalies indicate warmer-than-average conditions.
Negative anomalies indicate cooler-than-average conditions.

---
### Exercise 5: Customized Visualization of North America Temperature Anomaly
Script:
```bash
w08_05_area-average_vis.py
```
This exercise extends the area-averaged temperature analysis by improving the figure appearance using customized axis settings, minor ticks, and grid lines.

Improve the figure by adding:
- Major and minor ticks
- Grid lines
- Horizontal zero reference line
- Customized axis ranges

Key Visualization Commands

Major ticks:
```python
plt.xticks(np.arange(1950, 2025, 10))
plt.yticks(np.arange(-1, 1, 0.2))
```
Minor ticks:
```python
plt.gca().xaxis.set_minor_locator(MultipleLocator(1))
plt.gca().yaxis.set_minor_locator(MultipleLocator(0.2))
```
Reference line:
```python
plt.axhline(0, color='gray', linestyle='-')
```
Grid lines:
```python
plt.grid(which='major', linestyle='-', linewidth=0.7, alpha=0.7)
plt.grid(which='minor', linestyle='--', linewidth=0.4, alpha=0.5)
```

---
## Key Takeaways
- NetCDF files contain dimensions, variables, and metadata.
- Cartopy can visualize global climate fields using different map projections.
- Regional averages should use cosine-latitude weighting.
- Climatology represents the long-term average seasonal cycle.
- Anomalies help compare climate variability among different regions.
- Land regions generally exhibit larger temperature variability than ocean regions.
