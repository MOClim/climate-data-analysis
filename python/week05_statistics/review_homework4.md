# Review Homework 4: Monthly Precipitation Variability

## Overview
In Homework 4, students modified the temperature variability analysis script to investigate monthly precipitation variability across Utah weather stations.

The exercise introduced:
- precipitation data analysis
monthly accumulation using .sum()
ensemble mean calculations
standard deviation (σ) spread visualization
multi-station climate-data comparison

Example script: `python/week04__QAQC_Statistics/solution/w04_09_std_spread.prc.HW_example.py`

---
### Homework Tasks Review
#### Step 1. Change the climate variable
Students modified the `varname` to:
```python
varname = 'precip'
```

### Step 2. Convert daily precipitation into monthly total
Students used:
```python
monthly_df = dataframe.resample('ME').sum()
```
- precipitation is accumulated
- `.sum()` calculates monthly total

### Step 3. Modify the title and y-axis
```python
main_title = f'Monthly Precipitation with ±1σ Spread in Utah ({start_year}-{end_year})'
plt.ylabel('Precipitation (mm)')
```

---
## Key Takeaways

Students learned how to:
- process climate time-series observations
- calculate monthly precipitation totals
- compare multiple station datasets
- calculate ensemble statistics
- visualize variability using ±1σ spread plots

These techniques are commonly used in:
- climate monitoring
- hydrological analysis
- observational climate-data QA/QC
- regional climate variability studies
