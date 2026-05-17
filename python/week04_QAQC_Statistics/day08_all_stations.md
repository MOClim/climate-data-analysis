# Week 04 (Day 8): Reading and Plotting Multiple Station Data

## Overview

This lecture introduces how to read multiple climate station files automatically using Python. Students learn how to search for CSV files in a directory, read multiple UCRN station datasets, calculate monthly statistics, and visualize station-to-station variability.

## Learning Objectives

By the end of this module, you will be able to:

- read multiple CSV files automatically from a directory,
- use wildcard patterns to find station data files,
- extract station information from file metadata,
- convert daily observations to monthly values,
- calculate average and spread across multiple stations,
- create multi-station climate time-series plots.

## Topics Covered

- Reading multiple station datasets
- File paths and directory structure
- Wildcards using `*.csv`
- `Path().glob()`
- Monthly resampling with `resample()`
- Multi-station time-series visualization
- Station-to-station variability

---

## Reading Multiple Station Files Automatically

In this exercise, students learn how to read all station CSV files from a directory without manually typing each file name.

Instead of reading one file at a time, Python can search a folder and create a list of all matching CSV files.

Example:

```python
from pathlib import Path
filenames = list(Path('../../data/UCRN').glob('*.csv'))
```

This command:
- specifies the directory containing the UCRN station data,
- searches for all files ending with .csv,
- stores the file paths in a list called filenames.
This approach is useful when working with many climate station files because the same workflow can be applied to all stations automatically.

---
## Exercise: Read All Station Data

In this exercise, students learn how to automatically read multiple UCRN station datasets stored in a directory.

The datasets are already prepared in:

```bash
../../data/UCRN/
```

Python can automatically search this directory and create a list of all station CSV files:
```python
from pathlib import Path
filenames = list(Path('../../data/UCRN').glob('*.csv'))
```

Students can check the detected files using:
```python
print(filenames)
```
or print only the file names:
```python
for f in filenames:
    print(f.name)
```
This workflow avoids manually specifying each station file and allows the same analysis to be applied automatically to all stations.

---
## Exercise: Monthly Mean Air Temperature for All Stations

Students read air temperature data from all station files and convert daily observations to monthly averages.

The key workflow is:
```python
monthly_dats = []

for file_path in filenames:
    data = pd.read_csv(file_path, header=0, skiprows=26)
    data['date_time'] = pd.to_datetime(data['date_time'])
    data2 = data.set_index('date_time')

    monthly_dats.append(data2['airt'].resample('ME').mean())
```
Students should understand that:
- airt is the air temperature variable,
- `resample('ME')` groups data by month-end frequency,
- `.mean()` calculates the monthly average,
- monthly_dats stores the monthly time series for all stations.

---
## Exercise: Plot All Station Data

Students create a time-series plot showing monthly air temperature from all stations.
The loop below plots each station time series:
```python
for dat, loc in zip(monthly_dats, location_info):
    plt.plot(dat.index, dat, label=loc)
```
This command:
- loops through monthly data and station names together,
- plots each station on the same figure,
- labels each line using the station location.

---
## Exercise: Compare Station Variability

Students calculate statistics across all stations to examine spatial variability in climate observations.

Examples include:
- station average,
- maximum and minimum spread,
- ±1 standard deviation spread.

These plots help students compare regional climate variability across Utah stations.

---
## Key Takeaways

- Multiple station files can be read automatically using `Path().glob()`.
- Wildcards such as *.csv allow Python to find all CSV files in a directory.
- Loops make it possible to process many station datasets using the same commands.
- Monthly resampling helps convert daily observations into climate-scale summaries.
- Multi-station plots are useful for evaluating spatial variability in climate data.
