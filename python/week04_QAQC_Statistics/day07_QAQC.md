# Week 04 (Day 7): Reading and Plotting Climate Time Series part 2

## Overview
This module introduces

## Learning Objectives

By the end of this module, you will be able to:
- 

## Topics Covered
-

---

## Subroutine Description

The `w04_01_*` exercises introduce reusable Python subroutines (functions) for scientific plotting and QA/QC workflows.

Students learn how to:
- organize code using functions,
- pass variables into subroutines,
- reuse plotting routines for different datasets,
- improve readability and reproducibility of scientific programs.

Example:

```python
def plot_data(data, var, title, ylabel):
```
This plotting subroutine is reused throughout later exercises for visualization and QA/QC analysis.

---

## Exercise: Minutes Time Series Plot

In this exercise, students copy `w04_01_UCRN.sample.py` to `w04_01_UCRN.py` and run the script. :contentReference[oaicite:0]{index=0}

The script reads minute climate observations, converts timestamps into datetime format, and creates a temperature time-series plot.

Students should replace the placeholder values with:

- CSV file paths
- plot colors

The figure is automatically saved as a JPG image.

---

## Exercise: Minutes Time Series Plot using fig, ax

In this exercise, students copy `w04_02_UCRN.ax.sample.py` to `w04_02_UCRN.ax.py`, and create a minute climate time-series plot using the matplotlib object-oriented workflow:

```python
fig, ax = plt.subplots()
```
- fig represents the entire figure container.
- ax represents the plotting axis where data are drawn.

Using fig and ax provides a cleaner, more flexible plotting workflow than `plt.figure()` and `plt.subplot()`.

The script reads minute climate observations, converts timestamps into datetime format, and plots temperature observations using a reusable plotting function.

Students should modify:
- CSV file paths,
- plot colors.

The figure is automatically saved as a JPG image.

---

## Exercise: QC1 Data Range Test

In this exercise, students copy `w04_03_QC1_range.sample.py` to `w04_03_QC1_range.py`, and apply a first-level quality control (QC1) procedure to minute temperature observations using `w04_03_QC1_range.sample.py`. :contentReference[oaicite:0]{index=0}

The QC1 test detects values outside a physically realistic temperature range and replaces them with `NaN`.

The script uses:

```python
fig, ax = plt.subplots(2, 1)
```
to compare:
- original observations,
- QC1-modified observations.

### Student Workflow
Step 1. Modify the QC1 minimum and maximum threshold values:
```bash
min_temp = -40.
max_temp =  50.
```
Step 2. Run the script and generate the QC1 plots.
Step 3. Compare the original and QC datasets.
Step 4. Evaluate whether unrealistic values were removed without excluding valid environmental variability.

---

## Exercise: QC2 Time Derivative Test

In this exercise, students apply a second-level quality control (QC2) procedure to minute temperature observations using `w04_04_QC2_time_derivative.sample.py`. :contentReference[oaicite:0]{index=0}

QC2 detects unrealistically large temporal changes using the squared time derivative:

```python
(dT/dt)^2
```
The script compares:
- original observations,
- QC1 range-filtered observations,
- QC2 time-derivative-filtered observations,
- squared time-derivative values.

### Student Workflow
1. Modify the QC2 criteria value:
```python
criteria = ??
```
2. Run the script and generate the QC plots.
3. Compare the original and QC datasets.
4. Evaluate how different criteria values affect spike detection and data removal.

---

## Key Takeaways
- 
