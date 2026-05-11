# Homework 4 Review: Monthly Climate Averages

This exercise updates `w03_10_monthly_ave.sample.py` to create `w03_10_monthly_ave.solution.py`.

The exercise reads daily climate observations, converts the date column into datetime format, calculates monthly averages using `resample()`, and compares daily and monthly air temperature variability in a single figure.

---

## Main Tasks

###1. Calculate monthly averages using:

```python
data_mnt = data_dly.resample('ME').mean(numeric_only=True)
```

---
### 2. Plot daily and monthly air temperature data

```python
plt.plot(x_data, y_data, marker='.', linestyle='-', color="black", label='Monthly', zorder=3)
plt.plot(data_dly.index, data_dly[var], marker='.', linestyle='-', color="blue", label='Daily', zorder=1)
```

---

### 3. Save the figure

```python
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)
```

The figure is automatically saved as a JPG image.

---

# Learning Goals
Students learn how to:

- process climate time-series data with pandas,
- aggregate daily observations into monthly averages,
- compare temporal variability at different time scales,
- create and save scientific figures.

