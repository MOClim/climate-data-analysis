# Week 03 (Day 6): Temporal Resolution and Panel Plots

## Overview

This exercise introduces temporal resolution and panel plotting techniques for climate-data visualization. Students will compare daily, hourly, and minute observations and create subplot figures using `matplotlib`.

## Learning Objective

After completing this exercise, students will be able to:

- Compare climate datasets with different temporal resolutions
- Create panel plots using `plt.subplot()`
- Visualize climate observations using multiple plot types
- Interpret temporal variability in climate data

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

Check the code in `w03_09_daily_avg.sample.py` and investigate how daily averages are calculated from higher temporal resolution datasets.

Hourly and minute observations are resampled to daily frequency using the mean value for each day.

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

## Homework: Daily to Monthly Average

In this homework, use `w03_10_monthly_ave.sample.py` to calculate monthly averages from daily climate observations.

### Step 1. Copy the sample program

```python
cp w03_10_monthly_ave.sample.py w03_10_monthly_ave.py
```

### Step 2. Complete the monthly resampling code

Find this line in the sample code:

```python
data_mnt = data_dly.resample('ADD_TIME_FREQUENCY').mean()
```

Replace ADD_TIME_FREQUENCY with the correct pandas monthly frequency code.

Use:
```python
'ME'
```
to calculate monthly averages and assign each monthly value to the end of the month.

### Step 3. Complete the plot commands

Find the two empty plot commands:
```python
plt.plot()
plt.plot()
```

Update them to plot:

- Monthly average air temperature
- Original daily air temperature observations

- Use data_mnt.index and data_mnt[var] for the monthly average data.
- Use data_dly.index and data_dly[var] for the original daily data.

### Step 4. Run the script
```python
python w03_10_monthly_ave.py
```

### Step 5. Upload the script and JPEG outputs to Canvas (Homework3-Plot of monthly averaged data).


----

# Key Takeaways

- Monthly averages reduce short-term weather variability
- Temporal aggregation highlights seasonal climate patterns
- Aggregated datasets are easier to interpret for long-term analysis
- Daily variability becomes smoother after monthly averaging
- Resampling is an essential technique in climatology and geoscience data analysis




