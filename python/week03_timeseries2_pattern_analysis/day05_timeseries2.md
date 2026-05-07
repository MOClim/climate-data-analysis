# Week 03 (Day 5): Reading and Plotting Climate Time Series part 2

## Overview


## Learning Objectives

By the end of this module, you will be able to:

*

## Topics Covered

* 


---

## Exercise: Create Comparable Plots

In this exercise, students update `w03_01_xy2-plot.sample.py` to compare land and ocean temperature anomalies on the same figure.

The original file contains placeholder text that must be replaced with:

- CSV file paths
- plot colors
- ocean plotting commands
- figure title

Source file: `w03_01_xy2-plot.sample.py` :contentReference[oaicite:0]{index=0}

---

### Step 1: Add CSV File Names

Replace the placeholder text with the correct CSV file paths.

Original:

```python
land_file_path = Path('ENTER_FULL_PATH_TO_LAND_FILE.csv')
ocean_file_path = Path('ENTER_FULL_PATH_TO_OCEAN_FILE.csv')
```
Example:

```python
land_file_path = Path('../../data_raw/NOAA.1850-2025.LND.csv')
ocean_file_path = Path('../../data_raw/NOAA.1850-2025.OCN.csv')
```
---

### Step 2: Choose Plot Colors

Replace the placeholder color names.

Original:

```python
land_color = 'ENTER_LAND_COLOR'
ocean_color = 'ENTER_OCEAN_COLOR'
```

Example:

```python
land_color = 'red'
ocean_color = 'blue'
```

Students may choose other matplotlib named colors.
<a href="https://matplotlib.org/2.0.2/examples/color/named_colors.html" target="_blank">
Matplotlib Named Colors</a>

---

### Step 3: Plot the Land Data

The land dataset is already plotted in the sample file.

```python
plt.plot(
    land_data['Year'],
    land_data['Anomaly'],
    marker='o',
    linestyle='-',
    color=land_color,
    label='Land',
    zorder=1
)
```

Marker types: https://matplotlib.org/stable/api/markers_api.html

---

### Step 4: Add a Figure Title

Replace the placeholder title.

Original:

```python
fig_title = 'YOUR_FIGURE_TITLE'
```

Example:

```python
fig_title = 'Global Land and Ocean Temperature Anomalies'
```

---

## Exercise: XY Area Plot

### Step 1: copy `w03_02_area-plot.sample.py` to `w03_02_area-plot.py` and run:

```bash
cp w03_02_area-plot.sample.py w03_02_area-plot.py
python w03_02_area-plot.py
```

The script reads the CSV file and prints basic information about the DataFrame, including column names, data types, dimensions, and summary information.


---

## Exercise: Make an x-y plot of the ocean temperature anomaly

---

## Key Takeaways

- Climate data files often include metadata before tabular data
- `pandas` can read and inspect time-series data from CSV files
- `matplotlib` can be used to visualize time series (x-y plot)
- Clear axis labels and grid improve the readability of scientific figures
- The same workflow can be applied to different datasets
