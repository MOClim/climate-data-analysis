# Day 11: Correlation, Histograms, and Detrending in Climate Data

## Overview

This lesson introduces several statistical techniques commonly used in climate and Earth system science:

Annual histograms and probability distributions
Correlation analysis between climate variables
Time-range dependent climate relationships
Linear trend analysis
Detrending climate time series

Students will practice using `Pandas`, `NumPy`, `Matplotlib`, and `SciPy` to analyze long-term climate datasets and interpret variability and trends in geoscience data.

---

## Learning Objectives

By the end of this lesson, students should be able to:
- Create histograms using both frequency counts and probabilities
- Calculate correlations between climate variables
- Compare correlations across different time periods
- Understand and calculate linear trends
- Remove long-term trends from climate datasets (detrending)
- Interpret detrended climate variability

---
## Exercise 1: Annual Histograms and Probability Distributions

File: `w06_01_hist_anu_density.py`

In this exercise, students calculate annual-mean temperature and annual accumulated precipitation from daily climate observations. The script then visualizes the distributions using histograms.

Students compare:
- Frequency histogram → number of years in each bin
- Probability histogram → fraction (probability) of occurrence

### Key Function: Probability Histogram
```python
y_values = counts / counts.sum()
```
This converts histogram counts into probabilities.
```
P_i = \frac{n_i}{\sum n_i}
```
where:
- `n_i`= count in each bin
- `\sum n_i`=total number of observations
The probabilities from all bins sum to 1.

### Histogram Calculation
```python
counts, bins = np.histogram(data, bins=nbins)
```

### Plot Histogram
```python
plt.bar(bin_centers, y_values)
```

---
## Exercise 2: Correlation Between Land and Ocean Temperatures

File: `w06_02_correlation.py`

This script compares global land and ocean temperature anomalies and calculates their correlation coefficient.

Before running the script, students need to download the land temperature anomaly data from the NOAA Climate at a Glance website:
https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/global/time-series
Save the file in the data_raw directory.
Example:
data_raw/NOAA.1850-2025.LND.csv

The ocean temperature anomaly file should already be saved in the data directory:
```python
ocean_file_path = data_dir / 'NOAA.1850-2025.OCN.csv'
land_file_path = data_dir2 / 'NOAA.1850-2025.LND.csv'
```

Key Function: Correlation
```python
correlation = land_data.corr(ocean_data)
```
This calculates the correlation coefficient between land and ocean temperature anomalies.

A value close to 1 means the two datasets increase and decrease together strongly. A value close to 0 means the relationship is weak.

---
## Exercise 3: Correlation Analysis for Different Time Ranges

```bash
cp w06_03_cor_timerange.sample.py w06_03_cor_timerange.py
```

This exercise extends correlation analysis by allowing students to select different analysis periods.

Students investigate how correlations may vary depending on:
- climate era
- observational period
- long-term variability

### Step 1: Add the selected periods
```python
# Choose the start and end years for correlation analysis
start_year =
end_year =

# Extract the temperature anomaly data for the selected period
land_data = tland_data['Anomaly'].loc[start_year:end_year]
ocean_data = tocean_data['Anomaly'].loc[start_year:end_year]

# Calculate the correlation coefficient between land and ocean temperatures
correlation = land_data.corr(ocean_data)
```

### Suggested Exercises

Try comparing:
- 1900–1950
- 1950–2000
- 1980–2025
How does the correlation change?

---
## Exercise 4: Linear Trend Analysis and Detrending

File: `w06_04_detrend.py`

This lesson introduces the concept of removing long-term trends from climate data.

Students learn how to:
- Calculate linear trends using regression
- Create trend lines
- Remove trends from datasets
- Visualize detrended variability

### Key Function: Linear Regression
```python
slope, intercept, r_value, p_value, std_err = linregress(years, data)
```
This calculates the linear trend using regression.

### Create Trend Line
```python
trend = slope * years + intercept
```
This creates the linear trend line.

### Detrending
```python
dtrd_data = data - trend
```
This removes the long-term trend from the original data to isolate short-term variability.

---
## Exercise 5: Climate Trend Analysis and Detrended Correlation

```bash
cp w06_05_climate_detrend.sample.py w06_05_climate_detrend.py
```
This exercise demonstrates how long-term warming trends can influence correlations between climate datasets.

Students will:
- Calculate linear trends for land and ocean temperature anomalies
- Remove long-term warming trends (detrending)
- Compare original and detrended climate variability
- Examine how correlations change after detrending

### Suggested Discussion
Why might detrended correlations differ from correlations calculated using the original data?

Long-term warming trends may increase correlations because both datasets rise over time. Detrending removes the shared long-term trend and highlights short-term climate variability instead.

---
## Key Takeaway

- Histograms help visualize climate data distributions.
- Probability histograms show relative occurrence instead of raw counts.
- Correlation analysis measures relationships between climate variables.
- Climate correlations can vary for different time periods.
- Linear regression estimates long-term climate trends.
- Detrending removes long-term warming signals to examine short-term variability.
- Shared climate trends can strongly influence correlations.
