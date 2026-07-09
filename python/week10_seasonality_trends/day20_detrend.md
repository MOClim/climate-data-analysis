# Day 20: Linear Trend and Detrending

## Overview

Climate anomalies often contain both long-term trends and natural climate variability. To better understand variability, it is useful to estimate the long-term linear trend and remove it from the anomaly time series.

In this lesson, you will calculate linear trends, compare anomaly and detrended anomaly time series, and visualize detrended anomaly maps.

---

## Objectives
- Calculate linear trends using least-squares regression.
- Estimate climate trends in units of °C per decade.
- Remove linear trends from annual mean anomalies.
- Compare original and detrended anomaly time series.
- Visualize detrended annual anomaly maps.
- Interpret the influence of long-term trends on climate anomalies.

---

### Exercise 1: Linear Trend

Estimate the long-term linear trend of annual mean SST anomalies.

The program calculates annual mean SST anomalies, estimates the linear trend using least-squares regression, and overlays the fitted trend line on the annual anomaly time series.

```bash
python w10_06_linear_trend.py
```

```python
x = np.arange(da.sizes["time"])
y = da.values

# Fit a linear trend to the data
slope, intercept = np.polyfit(x, y, 1)

# Calculate the fitted trend line
trend = xr.DataArray(
        slope * x + intercept,
        coords={"time": da.time},dims=["time"])

# Convert the trend from per year to per decade
slope_decade = slope * 10
```
The fitted trend line is displayed together with the annual mean anomaly, and the trend is reported in units of **°C per decade**.

Try changing the trend analysis period and compare how the estimated trend changes.

---

### Exercise 2: Detrended Time Series

Remove the long-term linear trend from annual SST anomalies.

```bash
python w10_07_timeseries_detrend.py
```

```python
sst_NA_detrended, trend_line, slope_decade = linear_detrend(
    sst_NA_anom_annual,
    trend_start,
    trend_end
)
```
```python
# Center the year coordinate using the trend-analysis period
year_mean = float(year_fit.mean())
x_fit = year_fit - year_mean
x_all = year_all - year_mean

# Fit linear trend: anomaly = slope * centered_year + intercept
slope, intercept = np.polyfit(x_fit.values, da_fit.values, deg=1)

# Fitted linear trend line for all years
trend_line = xr.DataArray(
        slope * x_all + intercept,
        dims="time",
        coords={"time": da.time},
        name="linear_trend"
)
```
The left panel shows the original annual anomaly and fitted linear trend.

The right panel shows the detrended annual anomaly after removing the fitted trend.

---

### Exercise 3: Regional Detrending

Compare annual anomalies and detrended anomalies for multiple climate regions.

```bash
cp w10_08_three_region_detrend.sample.py w10_08_three_region_detrend.py
```

The program compares:
- North America
- Tropical Pacific
- Arctic

Each row contains:
- Original annual anomaly with fitted linear trend
- Detrended annual anomaly

After running the program, modify
```python
trend_start
trend_end
```
and compare how the estimated trends and detrended time series change.

---

### Exercise 4: Global Detrended Maps

Compare annual mean temperature anomaly maps before and after removing the linear trend.

```bash
python w10_09_detrended_airt_anom_map.py
```

The program:
- Calculates annual mean temperature anomalies.
- Estimates a linear trend at each grid point.
- Removes the fitted trend from each grid point.
- Compares annual anomaly and detrended anomaly maps.
- Displays the corresponding global mean time series.

```python
# Fit linear trend at each grid point:
# anomaly = slope * centered_year + intercept
#
# Compute the linear trend at all grid points simultaneously.
# np.polyfit() is suitable for a 1-D time series, but a 3-D field
# (time, lat, lon) would require looping over every grid point.
# This vectorized calculation is much faster and more efficient.

slope = (da_fit * x_fit).sum("time", skipna=True) / (
        x_fit ** 2).sum("time", skipna=True)
intercept = da_fit.mean("time", skipna=True)

# Fitted linear trend line for all years
trend_line = slope * x_all + intercept
trend_line.name = "linear_trend"

# Remove the full fitted trend line
da_detrended = da - trend_line
da_detrended.name = "detrended_anomaly"
```
The four-panel figure connects the map patterns with the global mean time series. This helps show how detrending changes both the spatial anomaly field and the time series for the selected year.

---

## Homework 9: Tropical Pacific SST Detrended Anomaly

Complete the homework program to compare annual SST anomalies and detrended annual SST anomalies.

Create a working copy of the sample program.

```bash
cp w10_10_detrended_sst_anom_map.HW.sample.py w10_10_detrended_sst_anom_map.HW.py
```

Complete the following tasks:
- Calculate detrended annual SST anomalies using `linear_detrend()`.
- Calculate the Tropical Pacific area-weighted annual mean time series.
- Plot annual SST anomaly and detrended anomaly maps.
- Plot the Tropical Pacific annual anomaly time series with the fitted linear trend.
- Plot the Tropical Pacific detrended annual anomaly time series.

Then execute

```bash
python w10_10_detrended_sst_anom_map.HW.py
```

The completed figure should contain:
- Annual SST anomaly map
- Detrended annual SST anomaly map
- Tropical Pacific annual anomaly with linear trend
- Tropical Pacific detrended annual anomaly

#### Submit
- Python program
- Output figure (PNG or JPG)

---

## Key Concepts

### Linear Trend

A linear trend describes the long-term rate of change in a climate variable.

In this course, trends are reported in

```
°C per decade
```

---

### Least-Squares Regression

The linear trend is estimated by fitting

```
y = ax + b
```

where

- **a** is the slope
- **b** is the intercept

The fitted line minimizes the squared differences between the observations and the regression line.

---

### Detrending

Detrending removes the fitted linear trend from an anomaly time series.

```
Detrended anomaly
=
Annual anomaly
−
Linear trend
```

This allows natural climate variability to be examined independently of the long-term trend.

---

### Spatial Detrending

The same detrending procedure can be applied independently at every grid point.

The resulting detrended maps highlight regional climate variability after removing the large-scale warming signal.

---

## Key Takeaways
- A linear trend quantifies the long-term rate of climate change.
- Climate trends are commonly expressed in units of °C per decade.
- Detrending removes the long-term linear trend from a climate time series, making natural climate variability easier to identify.
- Comparing anomaly and detrended anomaly time series reveals the contribution of long-term warming.
- Detrending can be applied to both time series and spatial maps to separate long-term climate change from regional climate variability.
- The same detrending workflow applies to different climate variables, including air temperature and sea surface temperature (SST).
natural variability.
