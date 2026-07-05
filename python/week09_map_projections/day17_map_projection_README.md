# Day 17: Global Map Projections with Cartopy

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

**OPeNDAP dataset**
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

**Calculate January 2026 temperature anomaly**
```python
# Example: January climatology
jan_clim = air_c.sel(time=slice("1991-01-01", "2020-12-31")).where(
    air_c["time.month"] == 1, drop=True
).mean("time")

# Example: January 2026 anomaly
jan_2026 = air_c.sel(time="2026-01-01")
anom = jan_2026 - jan_clim
```

**Projection and transform setting**
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
cp w09_02_robinson_airT_anomaly.sample.py w09_02_robinson_airT_anomaly.py
```

This script introduces the Robinson projection for global climate visualization. Robinson projection provides a visually balanced global view and is often used for world maps.

Student task:

```python
ax = plt.axes(projection=ccrs.Robinson())
```

---
### Exercise 3: Pacific-Centered Robinson Projection

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

---
### Exercise 4: Pacific-Centered Precipitation Anomaly

```bash
cp w09_04_robinson_precip.sample.py w09_04_robinson_precip.py
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
dat_c.attrs["units"] = "mm/day"
```

If the output displays:
```bash
2026-02-01T00:00:00.000000000
0.0
0.0
```
the dataset was not read correctly. If this occurs, run the program again until the dataset is loaded successfully.

When the dataset is read successfully, you should see output similar to:
```bash
2026-02-01T00:00:00.000000000
-13.739066753187217
12.310793255455792
```

---
### Exercise 5: NetCDF 

In this exercise, you will modify the previous precipitation example to read data from a local NetCDF file instead of an online OPeNDAP server. You will also select a more suitable color map and color range for precipitation anomalies.

Before editing the program, inspect the NetCDF file from the command line:
```bash
ncdump ../../data_raw/prate.mon.mean.nc | less
```

Create a new program:

cp w09_04_robinson_precip.sample.py w09_05_robinson_precip_NetCDF.py

Complete the following tasks:
- Replace the OPeNDAP URL with the local NetCDF file.
- Read the precipitation dataset from the local file.
- Choose a color map that is suitable for precipitation anomalies.
- Adjust the contour levels (color range) to improve the visualization.
- Run the program and compare the result with the OPeNDAP version from Exercise 4.

#### Tips:
Replace the OPeNDAP reader:
```python
# OPeNDAP
ds = xr.open_dataset(prate_url)
```

with a local NetCDF file:
```python
from pathlib import Path

indir = Path("../../data_raw")
prate_file = indir / "prate.mon.mean.nc"
ds = xr.open_dataset(prate_file)
```

Try different Matplotlib colormaps by changing the `cmap` argument:
```python
cmap="BrBG"
cmap="PuOr"
cmap="RdBu_r"
cmap="BrBG_r"
```
Ref: https://matplotlib.org/stable/users/explain/colors/colormaps.html

You can also adjust the contour levels to improve the visualization:
```python
levels = range(-10, 11, 1)
levels = range(-14, 15, 2)
levels = range(-20, 21, 2)
```

---
## Key Takeaways
- Compare Plate Carree, Robinson, and Lambert Conformal projections.
- Shift the map center using `central_longitude`.
- Focus on a region using `ax.set_extent()`.
- Read climate data from OPeNDAP or local NetCDF files.
- Choose appropriate colormaps and contour levels for effective visualization.
