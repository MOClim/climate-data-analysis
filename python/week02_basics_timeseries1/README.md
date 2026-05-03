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
├── notebooks/        # Jupyter notebooks with lecture and practice material
├── data/             # Sample datasets (e.g., temperature, precipitation)
├── scripts/          # Python scripts for data processing
└── README.md         # Module documentation
```

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

## Notes

Temporal analysis is fundamental in climate science, where variability spans multiple scales—from synoptic events to decadal oscillations. Careful handling of time coordinates and aggregation methods is essential for robust interpretation.

## Next Steps

Week 03 will extend these concepts toward more advanced temporal diagnostics and pattern recognition in climate datasets.
