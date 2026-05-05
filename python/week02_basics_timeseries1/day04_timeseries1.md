# Week 02 (Day 4): Reading and Plotting Climate Time Series

## Overview

This module introduces basic time-series analysis using a NOAA global ocean temperature anomaly dataset. Students will inspect a climate data file, read it with pandas, examine its structure, and create a simple x-y plot.

## Learning Objectives

By the end of this module, you will be able to:

* Inspect the structure of a climate data file
* Read a CSV file using pandas
* Interpret basic DataFrame information
* Create an x-y plot of a climate time series
* Save a figure as a JPEG file
* Open the saved figure from the command line

## Topics Covered

* CSV data structure
* Metadata and tabular data
* pandas DataFrame basics
* x-y plotting with matplotlib
* Figure output and file opening commands

---

## Exercise: Inspect and read a climate data file

### Step 1: Inspect the data file

```bash
cd python/week02_basics_timeseries1
less ../../data/NOAA.1850-2025.OCN.csv
```

### Step 2: Understand the data structure
The file has metadata lines followed by tabular data:

```text
# Title: Global Ocean January - December Average Temperature Anomalies
# Units: Degrees Celsius
# Base Period: 1901-2000
Year,Anomaly
1850,0
1851,0.06
1852,0.08
...
```

The lines beginning with `#` are metadata. The tabular data begin with:
```text
Year,Anomaly
```

The two columns are:
- `Year`: calendar year
- `Anomaly`: global ocean temperature anomaly in degrees Celsius, relative to the 1901–2000 base period

### Step 3: Run the sample script:

```bash
cp w02_07_read-data.sample.py w02_07_read-data.py
python w02_07_read-data.py
```
The script reads the CSV file and prints basic information about the DataFrame, including column names, data types, dimensions, and summary information.

### Step 5: Recommended reading method

```python
from pathlib import Path
import pandas as pd

file_path = Path('../../data/NOAA.1850-2025.OCN.csv')

data = pd.read_csv(file_path, comment='#')

print(data.head())
print(data.dtypes)
print(data.shape)
print(data.columns)
print(data.info())
```
The option `comment='#'` tells `pandas` to ignore metadata lines beginning with `#`.

---

## Exercise: Make an x-y plot of the ocean temperature anomaly

In this exercise, we will make a time-series plot of the NOAA global ocean temperature anomaly data.

### Step 1: Run the sample script:

```bash
cp w02_08_xy-plot.sample.py w02_08_xy-plot.py
python w02_08_xy-plot.py
```

### Step 2: Check what the script does

The script should:

1. read `NOAA.1850-2025.OCN.csv` from the `data` directory,
2. plot `Year` on the x-axis and `Anomaly` on the y-axis,
3. save the figure as a JPEG file with the same base name as the Python script.

### Step 3: Examine the code
```python
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

data = pd.read_csv(file_path, skiprows=4, names=['Year', 'Anomaly'])
print(data.head())

plt.plot(data['Year'], data['Anomaly'], marker='o')
```
- `pandas` (`pd`): used to read and handle tabular climate data (CSV)
- `matplotlib.pyplot` (`plt`): used to create plots (time series visualization)
- `pathlib.Path`: used to handle file paths in a portable way
- `names=['Year','Anomaly']` assigns column names manually
- `data['Year']` and `data['Anomaly']` are columns in a pandas DataFrame
  - `Year` is used as the x-axis
  - `Anomaly` (temperature anomaly, °C) is plotted on the y-axis
- The anomaly represents the deviation from a climatological baseline (1901–2000 mean, °C)
 
### Step 4: Understand the output filename

```python
Path(__file__).with_suffix('.jpg')
```

This creates an output filename using the same name as the Python script, but changes the extension from `.py` to `.jpg`.

For example:

```text
w02_08_xy-plot.py  ->  w02_08_xy-plot.jpg
```

### Step 4: Open the saved JPEG file

On macOS:

```bash
open w02_08_xy-plot.jpg
```

On Windows:

```cmd
start w02_08_xy-plot.jpg
```

On Windows PowerShell:

```powershell
start .\w02_08_xy-plot.jpg
```
---

## Exercise: Modify the plotting script

Open `w02_08_xy-plot.py` and update the plotting section:

```python
plt.plot(data['Year'], data['Anomaly'], marker='o')

plt.xlabel('Year')
plt.ylabel('Temperature Anomaly (°C)')
plt.title('Global Ocean Temperature Anomalies')
plt.grid(True)
```

---

## Homework: Plot land temperature anomalies

In this exercise, you will apply the same workflow to a different dataset.

### Step 1: Open the NOAA website

https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/global/time-series

### Step 2: Set the options

- Time Scale: 12-Month
- Month: December
- Start Year: 1850
- End Year: 2025
- Region: Global
- Surface: Land

### Step 3: Generate the plot

Click the "Plot" button.

### Step 4: Download the data

Click "CSV" to download the dataset.

### Step 5: Save the file

Save the file to your project directory:
```bash
cd ~Documents/course/climate-data-analysis
mkdir data_raw
mv ~/Download/data.csv data_raw/NOAA.1850-2000.LND.csv
```
- `mkdir`: Create a new directory
- `mv`: move data

---
### Step 6: (Homework)

Copy `w02_08_xy-plot.py` to a new file, `w02_09_xy-plot.land.py` and use it to:
- read the downloaded CSV file
- plot the time series (Year vs Anomaly)
