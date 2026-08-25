# Day 21: Correlation Analysis and Correlation Maps

##Learning Objectives
By the end of this lesson, you will be able to:
- Compare climate variables using scatter plots.
- Quantify linear relationships using the Pearson correlation coefficient.
- Calculate correlations between two climate time series.
- Create global spatial correlation maps.
- Interpret global climate teleconnections associated with Tropical Pacific SST anomalies.

---
## Introduction

Many climate phenomena are linked through large-scale teleconnections. 
For example, sea-surface temperature (SST) anomalies in the Tropical Pacific influence atmospheric circulation, 
precipitation, and surface air temperature around the globe.

Correlation analysis provides a simple statistical method for measuring the strength of the linear relationship 
between two variables. 
In this lesson, you will begin by comparing two global climate time series using scatter plots 
and then extend the analysis to calculate correlation coefficients at every grid point, producing global correlation maps.

---
### Exercise 1: Scatter Plot of Two Climate Variables
Compare annual global mean SST anomalies and global mean air temperature anomalies using a scatter plot.

```bash
python w11_01_scatter_plot.py
```
Concepts
- Global area-weighted averages
- Annual anomalies using `calc_seasonal_anom` function
- Scatter plots
- Linear regression
- Pearson correlation coefficient

#### Linear Regression
Linear regression finds the straight line that best represents the relationship between two variables.
```
y = ax + b
```
where:

x is the input variable

y is the predicted variable

a is the slope

b is the intercept

The slope describes how much y changes when x increases by one unit.

In this exercise:

x = global mean SST anomaly

y = global mean air temperature anomaly
```python
# -------------------------------------------------------
# Linear regression
# -------------------------------------------------------
slope, intercept, xfit, yfit = linear_fit_xy(sst_anom, air_anom)
```
The outputs are:

slope: slope of the regression line
intercept: y-intercept of the regression line
xfit: x-values used to draw the fitted line
yfit: predicted y-values along the fitted line

The fitted line is calculated as:
```
y_fit = slope×x_fit + intercept
```
The slope shows how much y changes when x increases by one unit.

---
### Exercise 2: Correlation Using Detrended Anomalies
Remove the long-term warming trend before comparing global SST and air temperature anomalies.

```bash
python w11_02_scatter_plot_clim_anom.py
```
Concepts
- Monthly climatology
- Annual anomalies
- Linear detrending
- Correlation after removing long-term trends

---
### Exercise 3: Global SST Correlation Map
Calculate the Pearson correlation coefficient between Tropical Pacific SST anomalies and SST anomalies at every grid point.

```bash
python w11_03_correlation_map.py
```
Concepts
- Regional mean time series
- Grid-point correlation
- Robinson map projection
- Spatial teleconnection patterns

---
### Exercise 4: Tropical Pacific SST and Global Precipitation
Complete the sample program by creating a global precipitation correlation map using Tropical Pacific SST anomalies.

```bash
cp w11_04_correlation_map_precip.sample.py w11_04_correlation_map_precip.py
```

Tasks:
- Read the precipitation dataset.
- Calculate annual precipitation anomalies.
- Compute the Pearson correlation coefficient between Tropical Pacific SST and precipitation.
- Plot the global precipitation correlation map.

Expected output:
- Tropical Pacific SST anomaly time series
- Global precipitation correlation map

---
### Exercise 5: Tropical Pacific SST and Global Air Temperature
Complete the sample program by creating a global air-temperature correlation map.

```bash
cp w11_05_correlation_map_airT.sample.py w11_05_correlation_map_airT.py
```
Tasks:
- Read the air temperature dataset.
- Calculate annual air temperature anomalies.
- Compute the Pearson correlation coefficient between Tropical Pacific SST and air temperature.
- Plot the global air temperature correlation map.

Expected output:
- Tropical Pacific SST anomaly time series (the same as the time series of `w11_04_correlation_map_precip.jpg`)
- Global air temperature correlation map

---
## Key Takeaways
- Pearson correlation measures the strength and direction of a linear relationship between two variables.
- Scatter plots provide a visual interpretation of climate relationships.
- Removing long-term trends helps isolate interannual climate variability.
- Grid-point correlation maps reveal spatial teleconnection patterns.
- Tropical Pacific SST anomalies influence climate conditions across many regions of the world through large-scale atmospheric circulation.
