# Day 17: Map Projections with Cartopy

## Overview

Learn how to visualize weather and climate data using different Cartopy map projections. This lesson covers global projections (Plate Carree and Robinson) and regional mapping with the Lambert Conformal projection.

## Learning Objectives

By the end of this lesson, students will be able to:

1. Explain the difference between a data coordinate system and a map projection.
2. Use `transform=ccrs.PlateCarree()` when plotting latitude–longitude climate data.
3. Compare Plate Carree, Robinson, and Lambert Conformal projections.
4. Center a global map over the Pacific Ocean using `central_longitude=180`.
5. Add a cyclic point to avoid a blank seam at the longitude boundary.
6. Set a regional map extent using `ax.set_extent()`.
7. Modify the color range of an anomaly map using contour levels.

## Key Concepts

### Remote data access

Accessing remote climate datasets with **OPeNDAP**, using URLs such as
  `https://psl.noaa.gov/thredds/dodsC/...` to read NetCDF files directly from NOAA servers without downloading them first.

### OPeNDAP vs. Downloaded NetCDF Files

**OPeNDAP (Remote Access)**
- ✔ No need to download large datasets
- ✔ Always accesses the latest available data
- ✔ Saves local disk space
- ✘ Requires an internet connection
- ✘ Performance depends on network speed

**Downloaded NetCDF Files (Local Access)**
- ✔ Faster data access after download
- ✔ Works without an internet connection
- ✔ Suitable for repeated analyses
- ✘ Requires local storage
- ✘ Must be updated manually when newer data become available

  
### Projection vs. Transform

In Cartopy, `projection` and `transform` have different meanings.

```python
ax = plt.axes(projection=ccrs.Robinson())
```

The `projection` defines the map coordinate system used for the final figure.

```python
transform=ccrs.PlateCarree()
```

The `transform` tells Cartopy that the input data are arranged on a regular longitude–latitude grid. Most climate datasets downloaded from NOAA, NCAR, or similar archives use this type of grid.

---
### Exercise 1: Plate Carree Projection

```bash
cp w09_01_platecarree_airT_anomaly.sample.py w09_01_platecarree_airT_anomaly.py
```

This script introduces a simple latitude–longitude map. Plate Carree projection is useful for understanding gridded climate data because it displays longitude and latitude directly.

Important points:
- Open a NOAA PSL OPeNDAP dataset.
- Inspect the data structure and available time range.
- Calculate January 2026 2-m air temperature anomaly.
- Plot the anomaly on a latitude–longitude map.

##OPeNDAP dataset
```python
# Example NOAA PSL OPeNDAP URLs
air_url = "https://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis.derived/surface/air.mon.mean.nc"
prate_url = "https://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis.derived/surface/prate.sfc.mon.mean.nc"
sst_url = "https://psl.noaa.gov/thredds/dodsC/Datasets/COBE2/sst.mon.mean.nc"

ds = xr.open_dataset(air_url)
print(ds)
print(ds.time[-1].values)

# Step 1: Inspect the dataset structure and available time range.
# Run this section first and check the printed output.
# Once you understand the data format, comment out sys.exit()
# so the script can proceed to the remaining steps.
```

##Calculate January 2026 temperature anomaly
```python
# Example: January climatology
jan_clim = air_c.sel(time=slice("1991-01-01", "2020-12-31")).where(
    air_c["time.month"] == 1, drop=True
).mean("time")

# Example: January 2026 anomaly
jan_2026 = air_c.sel(time="2026-01-01")
anom = jan_2026 - jan_clim
```

##Projection and transform setting
```python
# projection: map coordinate system (output)
# transform : data coordinate system (input)

ax = plt.axes(projection=ccrs.PlateCarree())

cf = ax.contourf(
    anom.lon,
    anom.lat,
    anom,
    levels=levels,
    cmap="RdBu_r",
    transform=ccrs.PlateCarree()
)
```

---
### Exercise 2: Robinson projection
```bash
python w09_02_robinson_airT_anomaly.sample.py
```

This script introduces the Robinson projection for global climate visualization. Robinson projection provides a visually balanced global view and is often used for world maps.

Student task:

```python
ax = plt.axes(projection=ccrs.Robinson())
```

### 3. Pacific-Centered Robinson Projection

```bash
python w09_03_robinson_rotated.py
```

This script centers the global map over the Pacific Ocean.

```python
ax = plt.axes(projection=ccrs.Robinson(central_longitude=180.))
```

This is useful for oceanographic and climate variability analysis, especially when studying the Pacific Ocean, ENSO, or basin-scale climate anomalies.

Because the longitude coordinate runs from 0° to 360°, a blank seam can appear at the map boundary. To avoid this, the script adds a cyclic point:

```python
anom_cyclic, lon_cyclic = add_cyclic_point(anom.values, coord=anom.lon)
```

### 4. Pacific-Centered Precipitation Anomaly

```bash
python w09_04_robinson_precip.sample.py
```

This script applies the same Pacific-centered Robinson projection to precipitation rate anomalies.

Important points:

- Use precipitation rate from NOAA PSL.
- Convert units from `kg m-2 s-1` to `mm/day`.
- Calculate January 2026 precipitation anomaly.
- Add a cyclic point before plotting.

Unit conversion:

```python
dat_c = dat * 86400
```

### 5. Lambert Conformal Projection for North America

```bash
python w09_06_Lambert_airT_anomaly.py
```

This script introduces the Lambert Conformal projection for regional climate analysis. Lambert Conformal is commonly used for mid-latitude weather and climate maps because it preserves shape reasonably well over limited regional domains.

Example projection:

```python
ax = plt.axes(
    projection=ccrs.LambertConformal(
        central_longitude=-100,
        central_latitude=45
    )
)
```

Example regional extent:

```python
ax.set_extent(
    [-150, -50, 15, 75],
    crs=ccrs.PlateCarree()
)
```

### 6. Lambert Conformal Projection over the United States

```bash
python w09_07_Lambert_USA.sample.py
```

This exercise focuses on the contiguous United States. Students complete the projection center, color levels, and map extent.

Recommended values:

```python
central_longitude=-96
central_latitude=39
```

```python
clevs = np.arange(-15, 15.1, 1)
```

```python
ax.set_extent(
    [-125, -66.5, 24, 50],
    crs=ccrs.PlateCarree()
)
```

The color range can be changed depending on the anomaly magnitude. For example:

```python
clevs = np.arange(-10, 10.1, 1)
```

uses a smaller range, while

```python
clevs = np.arange(-20, 20.1, 2)
```

uses a wider range with 2°C intervals.

## Suggested Exercise Flow

1. Run the Plate Carree example and inspect the dataset.
2. Complete the Robinson projection example.
3. Compare the Plate Carree and Robinson maps.
4. Run the Pacific-centered Robinson example and examine the map seam.
5. Run the precipitation anomaly example and compare temperature and precipitation patterns.
6. Complete the Lambert Conformal U.S. map exercise.
7. Modify the map center, map extent, and color range.

## Discussion Questions

1. Why is Plate Carree easy to understand but not always ideal for global visualization?
2. Why is Robinson projection useful for global climate maps?
3. Why does a Pacific-centered map require special treatment near the longitude boundary?
4. Why is Lambert Conformal appropriate for mid-latitude regional maps?
5. How does changing the color range affect the interpretation of temperature anomalies?

## Notes for Students

- Always check whether the data longitude range is `0–360` or `-180–180`.
- Use `transform=ccrs.PlateCarree()` when plotting regular latitude–longitude data.
- Use `ax.set_global()` for global maps.
- Use `ax.set_extent()` for regional maps.
- For anomaly maps, choose a balanced color range around zero.
- Use `extend="both"` when values exceed the selected color range.

## Expected Output

Students should create several map figures showing January 2026 climate anomalies using different projections. The final U.S. map should show 2-m air temperature anomalies over the contiguous United States using a Lambert Conformal projection.
