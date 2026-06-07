# Day 13: Global Maps and Scientific Visualization

## Overview

This lesson introduces basic geoscience visualization methods for gridded climate datasets and scientific figures.

Students will practice reading NetCDF files, selecting variables and months, plotting global maps with `Cartopy`, choosing appropriate colormaps, and applying basic accessibility principles such as contrast, patterns, and colorblind-friendly palettes.

---

## Learning Objectives

By the end of this lesson, students should be able to:

- Read monthly climatology data from NetCDF files using `xarray`
- Select a specific month from a gridded climate dataset
- Create global maps using `Cartopy` and `Matplotlib`
- Choose appropriate colormaps for temperature and precipitation fields
- Adjust color ranges using `vmin` and `vmax`
- Save figures using the script filename with a `.jpg` extension
- Improve scientific figures using contrast, hatching, and colorblind-friendly colors

---

## Exercise 1: Global Surface Air Temperature Map

File: `w07_01_global_temp_map.py`

Exercise 1: Global Temperature Map

File: w07_01_global_temp_map.py

This exercise introduces the concept of a colormap (cmap) for scientific visualization.

Students learn how to:
- Read global temperature data from a NetCDF file
- Plot data on a global map using Cartopy
- Apply a colormap to visualize temperature differences

### Key Data Step: Read NetCDF Data

```python
filename = Path('../../data/air.2x2.250.mon.1991-2020.ltm.comb.nc')
ds = xr.open_dataset(filename, use_cftime=True)
```

### Key Step: Select a Month

```python
month_idx = 0
dat = ds['air'].isel(time=month_idx)
```

`month_idx = 0` selects January. Students can change this value to display another month.

### Key Step: Plot on a Global Map

```python
img = ax.pcolormesh(
    dat['lon'], dat['lat'], dat.squeeze(),
    cmap=cmap,
    transform=ccrs.PlateCarree(),
    shading='auto',
    vmin=dmin,
    vmax=dmax
)
```

---

## Exercise 2: Global Precipitation Map

File: `w07_02_global_precip_map.py`

This exercise reads monthly precipitation climatology data and plots the global precipitation distribution.

Students learn how to:

- Read precipitation data from a NetCDF file
- Select a monthly precipitation field
- Use a sequential colormap for non-negative data
- Avoid overwriting the input NetCDF file when saving output figures

### Data Source

NOAA PSL UDel Air Temperature and Precipitation data:
https://psl.noaa.gov/data/gridded/data.UDel_AirT_Precip.html

### Choosing an Appropriate Colormap

Precipitation is usually non-negative, so a sequential colormap is usually more appropriate than a diverging colormap.

Good examples include:

```python
color_name = 'viridis'
color_name = 'viridis_r'
color_name = 'Blues'
color_name = 'GnBu'
color_name = 'YlGnBu'
```

Diverging colormaps such as `bwr` or `seismic` are better for anomaly data with meaningful positive and negative values around a central value.

### Matplotlib Colormap Reference

https://matplotlib.org/stable/users/explain/colors/colormaps.html

---

## Exercise 3: Visualization Tips for Scientific Figures

File: `w07_03_visualization.py`

This exercise demonstrates several basic visualization techniques used in scientific graphics.

Topics include:
- Colorblind-friendly palettes
- High-contrast colors
- Patterns and textures

Students also learn how to manually choose:
- Colors using color names or hexadecimal color codes
- Line and pattern styles using Matplotlib options

### Panel 1: High Contrast Colors

```python
axes[0].bar(
    [0, 1],
    [0.5, 0.5],
    color=['#FF0000', '#00FF00'],
    edgecolor='black'
)
```

### Panel 2: Patterns and Textures

```python
axes[1].bar(
    [0, 1],
    [0.5, 0.5],
    color='grey',
    hatch='/',
    edgecolor='black'
)
```

Hatching helps distinguish categories when color alone is not sufficient.

### Panel 3: Colorblind-Friendly Palette

```python
colors = ['#440154', '#31688e', '#35b779', '#fde725']
```

This example uses colors from the Viridis-style palette, which is commonly used for scientific visualization.

### Discussion
Why is figure design important for scientific communication?

---

## Key Takeaway

- NetCDF files are commonly used for gridded climate data.
- `xarray` is useful for reading and selecting climate variables.
- `Cartopy` allows climate data to be plotted on map projections.
- Colormap choice should match the structure of the data.
- Sequential colormaps are appropriate for non-negative variables such as precipitation.
- Diverging colormaps are useful for anomaly-like or signed data.
- `Path(__file__).with_suffix('.jpg')` safely creates an output figure name from the script name.
- High contrast, hatching, and colorblind-friendly palettes improve scientific communication.
