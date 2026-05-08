# Week 03 (Day 6): Temporal Resolution and Panel Plots

## Overview

## Learning Objective
After completing this exercise, students will be able to:

- Understand temporal resolution in climate observations
- Compare daily, hourly, and minute datasets
- Create panel plots using matplotlib
- Use plt.subplot() to organize multiple figures
- Compare different visualization methods for the same dataset

---
## Panel Plot Layouts
The index value starts from the upper-left panel and increases from left to right.
### Example 1. Two vertical panels
```python
plt.subplot(2, 1, 1) # 1 row, 2 columns, first subplot
plt.subplot(2, 1, 2)
```

### Example 2. Two horizontal panels
```python
plt.subplot(1, 2, 1)
plt.subplot(1, 2, 2)
```

## Example 3. Four panels
```python
plt.subplot(2, 2, 1)
plt.subplot(2, 2, 2)
plt.subplot(2, 2, 3)
plt.subplot(2, 2, 4)
```

---

## Exercise: Plot Two Panels
In this exercise, students update `w03_06_2_panels.sample.py` to compare line and bar plot representations of precipitation data.

### Step 1: Copy the sample program and run it
```bash
cp w03_06_2_panels.sample.py w03_06_2_panels.py
python w03_06_2_panels.py
```

The subplot command:
```
plt.subplot(2, 1, 1)  # 1 row, 2 columns, first subplot
```

---

## Exercise: Compare Temporal Resolution

### Step 1. Copy the sample program
```bash
cp w03_06_2_panels.sample.py w03_06_2_panels.py
```

### Step 2. Download climate datasets
Download the following datasets from any station in the AgWeather (AgWX) network:

Daily observations
Hourly observations
Minute observations

Save all downloaded CSV files into the:
`data_raw` directory.

### Step 3. Fill in the missing sections.

Follow the steps in the sample code and update the missing sections.

### Step 4. Run the script
```bash
python w03_06_2_panels.py
```

---
## Exercise: Narrow Time Resolution

In this exercise, copy and run:

`w03_08_compare_temporal_resolution.sample.py`

This example uses a zoomed narrow time range to compare climate datasets with different temporal resolutions.

### Zooming into a Narrow Time Range

A shorter time window is used to better visualize differences among the datasets.
```python
xmin = data_dly.index.max() - pd.Timedelta(days=3)
xmax = data_dly.index.max() + pd.Timedelta(days=1)
plt.xlim([xmin, xmax])
```
Zooming into a narrow time range helps reveal:

Daily sampling intervals
Hourly temperature fluctuations
Minute-scale variability

This comparison demonstrates how temporal resolution influences the interpretation of climate observations.

---

## Exercise: Daily Average

Check the code of `w03_09_daily_avg.sample.py` and investigate the daily average.

```python
# Resample hourly and minute data to daily averages
# Aggregate sub-daily observations into daily mean values

data_h_daily_avg = data_hly.resample('D').mean()
data_m_daily_avg = data_min.resample('D').mean()
```

Compare the daily datasets with the daily-averaged datasets from hourly and minute data.
```python
plt.plot(data_dly.index, data_dly[var], marker='.', linestyle='-', color="black", label='Daily (original)',zorder=3)
plt.plot(data_h_daily_avg.index, data_h_daily_avg[var], marker='+', linestyle='-', color="blue", label='Daily from Hourly',zorder=2)
plt.plot(data_m_daily_avg.index, data_m_daily_avg[var], marker='.', linestyle='-', color="green", label='Daily from Minite',zorder=1,
linewidth=3)
```

Key Question
Do you expect the original daily observations and the calculated daily averages from hourly or minute data to be identical?

Consider:

How are daily observations originally calculated?
Are there missing hourly or minute observations?
Do averaging methods differ between datasets?
How might quality control or sensor timing affect the results?

---

## Exercise: Daily to monthly average

Check the code of `w03_10_monthly_ave.sample.py` and investigate the monthly average.

Calculate monthly averages. Daily observations are aggregated into monthly mean values using the pandas resample() function.

```python
# 'ME' represents month-end frequency.
#
# numeric_only=True ensures that only numeric
# variables are included in the averaging process.

data_mnt = data_dly.resample('ME').mean(numeric_only=True)
```

----

# Key Takeaways




