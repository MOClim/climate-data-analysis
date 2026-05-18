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
## Exercise: Read and Plot All Station Data

File: `w04_05_daily_allloc.sample.py`

Copy the sample script:

    cp w04_05_daily_allloc.sample.py w04_05_daily_allloc.py

In this exercise, students read multiple UCRN station files automatically and plot all station time series on the same figure.

Python first searches the data directory and creates a list of all CSV files:
```python
    filenames = list(Path('../../data/UCRN').glob('*.csv'))
```
This command finds all files ending with `.csv` in the `../../data/UCRN/` directory. This is useful because students do not need to type each station file name manually.

Each station file is then read into a pandas DataFrame and stored in a list:
```python
    dataframes = []

    for file_path in filenames:
        df = pd.read_csv(file_path, index_col='date_time',
                         parse_dates=True, header=0, skiprows=26,
                         usecols=['date_time', varname])
        dataframes.append(df[varname])
```
`dataframes` is a list that stores data from all station files.
`dataframe` or `df` represents one station dataset at a time inside the loop.

After the data are read, each station time series can be plotted using `zip()`:
```python
    for dat, loc in zip(dataframes, location_info):
        plt.plot(dat.index, dat, label=loc)
```
`zip()` combines the station data and station names so that Python can loop through them together.

This allows each time series to be plotted with its corresponding station label.

This command:
- loops through monthly data and station names together,
- plots each station on the same figure,
- labels each line using the station location.

---
## Exercise: Monthly Mean Air Temperature for All Stations

Copy the sample script:
```bash
cp w04_06_monthly_allloc.sample.py w04_06_monthly_allloc.py
```

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
## Exercise: Compare Station Variability

Copy the sample script:
```bash
cp w04_07_maxmin_spread.sample.py w04_07_maxmin_spread.py
```

In this exercise, students compare climate variability across multiple stations using maximum and minimum ranges.

## Exercise: Compare Station Variability

Copy the sample script: 
```bash
cp w04_07_maxmin_spread.sample.py w04_07_maxmin_spread.py
```

In this exercise, students compare climate variability across multiple stations using maximum and minimum envelopes.

Students first combine all station datasets into a single DataFrame:
```python
    combined_data = pd.concat(monthly_dats, axis=1)
```
The maximum and minimum values across all stations are then calculated for each time step:
```python
    max_values = combined_data.max(axis=1)
    min_values = combined_data.min(axis=1)
```
The shaded region between the maximum and minimum values represents the station-to-station spread:
```python
    plt.fill_between(combined_data.index,
                     min_values,
                     max_values,
                     color='skyblue',
                     alpha=0.4)
```
This shaded area shows the full range of climate variability across Utah stations.

- Large spread:
  indicates greater differences among stations.

- Small spread:
  indicates more similar climate conditions across stations.

---

## Exercise: +/- 1 Sigma Spread

Copy the sample script:
```bash
cp w04_08_std_spread.sample.py w04_08_std_spread.py   
```

In this exercise, students calculate the mean and standard deviation across multiple stations.

Students practice:

- calculating standard deviation using `.std()`,
- computing ±1 sigma spread,
- visualizing variability around the station mean,
- comparing temperature and precipitation variability.

These exercises introduce basic statistical analysis for climate datasets and demonstrate how uncertainty or spread can be visualized in time-series plots.

---

## Homework 4: Monthly Precipitation Variability

Create a precipitation version of the standard-deviation spread plot.

Steps:

1. Copy the sample script:
```python
    cp w04_08_std_spread.sample.py w04_09_std_spread.prc.py
```

2. Open the copied script and change the variable from air temperature to precipitation:
```python
    varname = 'precip'
```

3. Update the monthly calculation for precipitation accumulation:
```python
    monthly_df = dataframe.resample('ME').sum()
```

4. Update the plot title and y-axis label for precipitation.

5. Run the script and confirm that a JPEG figure is created.

6. Upload both files to Canvas:

```text
w04_09_std_spread.prc.py
w04_09_std_spread.prc.jpg
```

Goal: Practice modifying an existing climate-data analysis script to examine monthly precipitation variability across multiple stations using ±1σ spread. 

---
## Key Takeaways

- Multiple station files can be read automatically using `Path().glob()`.
- Wildcards such as *.csv allow Python to find all CSV files in a directory.
- Loops make it possible to process many station datasets using the same commands.
- Monthly resampling helps convert daily observations into climate-scale summaries.
- Multi-station plots are useful for evaluating spatial variability in climate data.
