# Homework 5 Review — Monthly vs Annual Histogram Analysis

## Overview
This homework introduced histogram analysis using long-term climate observations from the USU station (1893–2010). 
Students practiced resampling daily observations into monthly and annual datasets and compared how averaging changes climate distributions.

Example script: `python/week05_statistics/solution/w05_09_hist_mon_anu.HW_sample.py`

---
## Step 1: Create Monthly and Annual Datasets

Use Pandas `resample()` to calculate monthly and annual climate statistics.
- Temperature uses `mean()` because temperature is averaged over time
- Precipitation uses `sum()` because precipitation accumulates over time

```python
df_temp_mon = df['tmid'].resample('ME').mean()
df_temp_anu = df['tmid'].resample('YE').mean()

df_prc_mon = df['pcpn'].resample('ME').sum()
df_prc_anu = df['pcpn'].resample('YE').sum()
```

---
## Step 2: Create Temperature Histogram

Edit the number of histogram bins for monthly and annual temperature data.
A larger bin number produces a more detailed distribution.

```python
plt.hist(temp_mon, bins=100, color='orange', edgecolor='black')
plt.hist(temp_anu, bins=20, color='orange', edgecolor='black')
```

---
## Step 3: Create Precipitation Histogram

Monthly precipitation often shows a right-skewed distribution because large precipitation events occur less frequently.
Annual precipitation totals are generally smoother because precipitation is accumulated over longer periods.

```python
plt.hist(prc_mon, bins=100, color='blue', edgecolor='black')
plt.hist(prc_anu, bins=20, color='blue', edgecolor='black')
```

This homework demonstrated how temporal averaging changes climate data distributions. 
Monthly datasets preserve short-term variability, while annual datasets smooth fluctuations and produce narrower histogram distributions.
