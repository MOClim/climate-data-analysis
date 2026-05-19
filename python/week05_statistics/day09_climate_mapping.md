# Week 05 (Day 9): Climate Mapping with Cartopy and PyGMT

## Overview

This module introduces climate data visualization using Cartopy and PyGMT.
Students will learn how to create global maps, plot weather-station observations, and compare different topographic map styles using Python-based mapping libraries.

The exercises also demonstrate how to merge station metadata (latitude and longitude) with observational datasets before visualization.

## Learning Objectives

By the end of this module, students will be able to:
- Create global maps using Cartopy and PyGMT
- Understand map projections and geographic plotting
- Add coastlines, rivers, land, and ocean features to maps
- Read and process weather station datasets
- Merge observational data with latitude and longitude information
- Plot station observations on maps
- Compare high- and low-resolution topographic datasets
- Apply color maps and colorbars to climate variables
- Save figures as image files

---
### Exercise: Cartopy Global Maps

Copy the sample script:
```bash
cp w05_01_cartopy.sample.py w05_01_cartopy.py
```
In this exercise, students will learn how to create a simple global map using Cartopy.

Topics include:
- creating a Figure and GeoAxes object
- adding coastlines and geographic features

#### Creating a Figure object
A Figure object represents the entire plotting canvas. `figsize` controls the figure size in inches.
Example:
```python
fig = plt.figure(figsize=(10, 5))
```

#### Creating an Axes object
An Axes object represents the plotting region inside the Figure. 
Example: add_subplot(rows, columns, panel_number)
```python
ax = fig.add_subplot(1, 1, 1)
```

#### Creating a Cartopy GeoAxes object
In Cartopy, the Axes object becomes a GeoAxes object when a map projection is added.
Example:
```python
ax = fig.add_subplot(
    1, 1, 1,
    projection=ccrs.Robinson()
)
```

#### Applying the Robinson map projection
The Robinson projection is commonly used for global climate visualization.
Example:
```python
projection=ccrs.Robinson()
```

---
### Exercise: PyGMT Global Maps

Copy the sample script:
```bash
cp w05_02_pygmt.sample.py w05_02_pygmt.py
```

In this exercise, students will create a simple global map using PyGMT and learn the basic workflow for geographic visualization.

Topics include:
- creating a PyGMT Figure object
- configuring map projections
- creating a basemap

#### Create a Figure object
A Figure object represents the plotting canvas.
Example:
```python
fig = pygmt.Figure()
```

#### Create a basemap
`fig.basemap()` creates the map frame and projection.
Example:
```python
fig.basemap(
    region="g",
    projection="N12i",
    frame=True
)
```
- `region="g"` → global map
- `projection="N12i"` → Robinson projection
- `12i` → map width = 12 inches
- frame=True → draw map frame

---
### Exercise: Adding Latitude and Longitude Information

Copy the sample script:
```bash
cp w05_03_create_wlatlon.sample.py w05_03_create_wlatlon.py
```

In this exercise, students will combine weather station observations with station metadata containing latitude and longitude information.
The updated datasets will then be saved as new CSV files for later mapping exercises.

---
### Exercise: Mapping Weather Station Data with PyGMT

Files:
Copy the sample script:
```bash
w05_04_map_pygmt_highres.sample.py
w05_04_map_pygmt_lowres.sample.py
w05_04_map_pygmt_notop.sample.py
```

In this exercise, students will visualize monthly averaged weather-station air temperature data using PyGMT.

The exercises demonstrate how to:
- read multiple climate-data files
- calculate monthly averages
- plot station observations using latitude and longitude
- create topographic maps
- compare different map styles and resolutions

#### Convert datetime information
This converts the time column into a datetime index.
Example:
```python
data['date_time'] = pd.to_datetime(data['date_time'])
data.set_index('date_time', inplace=True)
```

#### Calculate monthly averages
Example:
```python
monthly_data = data.resample('ME').mean()
```
- `ME` → monthly end frequency
- `.mean()` → monthly average

#### Combine multiple station datasets
This combines all station observations into one dataset.
Example:
```python
combined_data = pd.concat(monthly_dats)
```

---

### Create an Animated GIF
After generating multiple PNG map figures, students can combine the images into an animated GIF using the ImageMagick magick command.

This is useful for:
- visualizing monthly climate variability
- creating time-evolving climate animations

Example Command:
```bash
magick -delay 50 -loop 2 fig_all/*.png airt_movie.gif
```
- `-delay 50` → animation speed
- `loop 2` → repeat animation twice
- `fig_all/*.png` → read all PNG files
- `airt_movie.gif` → output GIF filename

#### Open the GIF
MacOS:
```bash
open airt_movie.gif
```
Windows:
```bash
start airt_movie.gif
```

---
## Key Takeaways
- Cartopy and PyGMT provide different approaches for geographic visualization in Python.
- Geographic datasets often require latitude and longitude metadata before mapping.
- Climate observations can be visualized using station-based mapping techniques.
- Topographic resolution influences map appearance and processing speed.
- Colorbars and colormaps are important for interpreting climate variables visually.



