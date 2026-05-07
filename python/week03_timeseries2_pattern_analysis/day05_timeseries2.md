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

## Exercise: Create an Area Plot

This exercise demonstrates how to create an area plot using NOAA ocean temperature anomaly data.

The script uses `fill_between()` in matplotlib to highlight:

- positive anomalies in red
- negative anomalies in blue

Source file: `w03_02_area-plot.sample.py` :contentReference[oaicite:0]{index=0}

---

### Step 1: Copy the sample file

Copy `w03_02_area-plot.sample.py` to `w03_02_area-plot.py` and run:

```bash
cp w03_02_area-plot.sample.py w03_02_area-plot.py
python w03_02_area-plot.py
```

---

### Step 2. Check the Output Figure

The script automatically generates and saves:

```text
w03_02_area-plot.jpg
```

The figure should display:

- positive anomalies shaded in red
- negative anomalies shaded in blue

---

## Exercise: Mauna Loa CO₂ Time Series

This exercise demonstrates how to download, read, and process Mauna Loa atmospheric CO₂ observations from NOAA.

Students will:

- download the CO₂ dataset
- inspect the raw data structure
- create a datetime column
- prepare the dataset for time-series analysis

---

### Step 1. Download the CO₂ Dataset

Download:

```text
co2_daily_mlo.csv
```

from the NOAA Global Monitoring Laboratory website:

```text
https://gml.noaa.gov/ccgg/trends/
```

Save the downloaded file into the course data directory.

Example:

```bash
mv ~/Download/co2_daily_mlo.csv ../../data_raw/
```

---

### Step 2: Check the Raw Data

Inspect the file using:

```bash
less ../../data_raw/co2_daily_mlo.csv
```

The dataset contains:

- metadata lines beginning with `#`
- no standard CSV column headers

```text
# NOTE: Due to the eruption of the Mauna Loa Volcano, measurements from Mauna Loa Observatory
# were suspended as of Nov. 29, 2022 and resumed in July 2023.
# Observations starting from December 2022 to July 4, 2023 are from a site at the
# Maunakea Observatories, approximately 21 miles north of the Mauna Loa Observatory.
#
1974,5,19,1974.3781,333.46
1974,5,20,1974.3808,333.64
1974,5,21,1974.3836,333.50
1974,5,22,1974.3863,333.21
```

---

### Step 3. Copy the Sample File

Copy:

```bash
cp p05_03.add_column.sample.py p05_03.add_column.py
```

Run:
```bash
python p05_03.add_column.py
```

---

### Step 4. Check the Data

Print the dataset to verify successful reading.

```python
print(data.head())
```

---

## Key Takeaways

- Climate data files often include metadata before tabular data
- `pandas` can read and inspect time-series data from CSV files
- `matplotlib` can be used to visualize time series (x-y plot)
- Clear axis labels and grid improve the readability of scientific figures
- The same workflow can be applied to different datasets
