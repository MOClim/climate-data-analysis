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

This exercise shows how to read a global surface air temperature climatology file and visualize one month on a world map.

Students learn how to:

- Open a NetCDF file using `xarray`
- Select one month using `isel(time=month_idx)`
- Plot gridded temperature data on a global map
- Add coastlines, gridlines, a colorbar, and a title
- Save the output figure as a JPEG file

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

### Suggested Student Direction

Try changing:

```python
month_idx = 0
```

to another value between `0` and `11`.

Also try different diverging colormaps:

```python
color_name = 'bwr'
color_name = 'seismic'
color_name = 'coolwarm'
color_name = 'RdBu_r'
```

Diverging colormaps are useful for temperature fields when the color scale is centered around a reference value or when colder and warmer regions should be visually separated.

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

### Key Data Step

```python
filename = indir / 'precip.mon.v401.ltm.1981-2010.nc'
ds = xr.open_dataset(filename, use_cftime=True)
dat = ds['precip'].isel(time=month_idx)
```

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

### Important Note: Save Output Safely

Use a separate output filename so the original NetCDF file is not overwritten.

```python
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)
```

This saves the figure with the same base name as the script and a `.jpg` extension.

---

## Exercise 3: Visualization Tips for Scientific Figures

File: `w07_03_visualization.py`

This exercise introduces basic design principles for scientific figures.

Students compare:

- High contrast colors
- Patterns and textures
- Colorblind-friendly palettes

The script creates one merged JPEG figure with three panels.

### Key Function: Multi-Panel Figure

```python
fig, axes = plt.subplots(3, 1, figsize=(10, 6))
```

This creates three vertically stacked panels in one figure.

### Panel 1: High Contrast Colors

```python
axes[0].bar(
    [0, 1],
    [0.5, 0.5],
    color=['#FF0000', '#00FF00'],
    edgecolor='black'
)
```

Students can compare how different color combinations affect readability.

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

### Save One Merged JPEG File

```python
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)
```

This saves all three panels into one JPEG file.

---

## Suggested Discussion

Why should temperature and precipitation maps use different types of colormaps?

Temperature maps often benefit from diverging colormaps when showing colder and warmer values relative to a central reference. Precipitation is generally non-negative, so sequential colormaps better represent increasing precipitation intensity.

Why might patterns or hatching be useful in scientific figures?

Patterns help communicate categories when colors are difficult to distinguish, especially for printed figures, grayscale figures, or viewers with color vision deficiency.

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
