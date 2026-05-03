# Week 02: Basics & Time Series Analysis (Part 1)

## Overview

This module introduces foundational Python tools for climate data analysis and develops essential techniques for handling and interpreting time series. Emphasis is placed on temporal structure, indexing, and exploratory diagnostics relevant to atmospheric and oceanographic datasets.

## Learning Objectives

By the end of this week, you should be able to:

* Apply core Python data structures for geophysical datasets
* Manipulate time-indexed data using `pandas` and `xarray`
* Perform basic temporal aggregation and resampling
* Visualize climate time series and identify variability patterns
* Interpret trends, seasonality, and anomalies in environmental data

## Topics Covered

* Python basics for scientific computing
* Introduction to time series in climate systems
* Temporal indexing and datetime handling
* Resampling (daily, monthly, seasonal scales)
* Rolling statistics and smoothing techniques

## Directory Structure

```
week02_basics_timeseries1/
│
├── w02_01.namelist.sample.py   # Python scripts for data processing
└── README.md                   # Module documentation
```
---

## Environment Setup
Activate the virtual environment
```bash
conda activate climate-analysis
```

List available environments (if forgotten)
```bash
conda info --envs
```

---

## Example Workflow

1. Load climate dataset (e.g., NetCDF, CSV)
2. Convert time coordinates to datetime objects
3. Subset data by time range
4. Compute monthly or seasonal means
5. Plot time series and identify patterns

## Recommended Libraries

* `numpy` — numerical computation
* `pandas` — time series handling
* `xarray` — labeled multidimensional arrays
* `matplotlib` — visualization

---
## Exercise: Modify the Namelist

This exercise introduces basic file operations and code editing within a Unix-like environment.

### Step 1: Create a new file
```bash
cp w02_01_namelist.sample.py w02_01_namelist.py
ls
```

### Step 2: Edit the code
```bash
vi w02_01_namelist.py
```
- Press i to enter insert mode
- Add a new fruit name to the list
- Press ESC, then type :wq and press Enter to save and exit

### Step 3: Run the code
```bash
python w02_01_namelist.py
```

### Learning Focus
- File duplication and version control practice
- Basic terminal-based editing (vi)
- Execution of Python scripts
- Understanding simple data structures (lists)

---

## Notes

Temporal analysis is fundamental in climate science, where variability spans multiple scales—from synoptic events to decadal oscillations. Careful handling of time coordinates and aggregation methods is essential for robust interpretation.

## Next Steps

Week 03 will extend these concepts toward more advanced temporal diagnostics and pattern recognition in climate datasets.
