[day22_EOF.md](https://github.com/user-attachments/files/31391653/day22_EOF.md)
# Day 22: Empirical Orthogonal Function (EOF) Analysis

## Overview

In this class, we introduce **Empirical Orthogonal Function (EOF) analysis** and apply it to winter (DJF) climate variability.

EOF analysis decomposes a space-time climate field into:

- **EOF spatial patterns**, which describe dominant spatial structures of variability;
- **principal components (PCs)**, which describe the temporal evolution of each EOF mode; and
- **variance explained**, which measures the fraction of total variance represented by each mode.

We begin with the Niño 3.4 index and SST correlation maps, then calculate EOF modes of Tropical Pacific SST. We finally apply the same analysis framework to North Atlantic sea-level pressure (SLP).

---

## Learning Objectives

By the end of this class, you should be able to:

1. Calculate DJF climate anomalies from monthly data.
2. Calculate a regional, area-weighted climate index such as Niño 3.4.
3. Calculate grid-point correlations using `xr.corr()`.
4. Explain the basic purpose of EOF analysis.
5. Calculate latitude-weighted EOFs and principal components.
6. Interpret variance explained by individual EOF modes.
7. Relate a principal component to global climate fields using correlation maps.
8. Apply the EOF workflow to a different climate variable and geographic domain.

---
Previous scripts (such as `w11_05_correlation_map_airT.sample.py`) calculate the correlation between spatial SST patterns and area-averaged SST. 

The next step is to use a climate index (such as the **Niño 3.4 Index**) to examine the spatial correlation pattern associated with ENSO.

# Exercise 1. Niño 3.4 Index and Global SST Correlation

Start with:

```bash
python w11_06_Nino34_correlation_map.py
```

This script calculates DJF SST anomalies, constructs the Niño 3.4 index, detrends the SST anomalies, and calculates the Pearson correlation between Niño 3.4 and SST at every grid point.

The Niño 3.4 region is:

- Latitude: **5°S–5°N**
- Longitude: **170°W–120°W**

The regional mean is calculated using cosine-latitude weighting.

The main correlation calculation is:

```python
corr_map = xr.corr(
    sst_for_corr,
    nino34_for_corr,
    dim="year"
)
```

The resulting map shows the global SST pattern associated with interannual variability in the Niño 3.4 region.

### Questions to consider

- Where are the strongest positive SST correlations with Niño 3.4?
- Where are negative correlations found?
- Why is the equatorial Pacific pattern physically consistent with ENSO?
- Why do we detrend SST before examining interannual climate variability?

---

# Exercise 2. From a Climate Index to EOF Analysis

The Niño 3.4 index is defined using a **pre-selected geographic region**.

EOF analysis instead determines **dominant** spatial patterns directly from the variability of the climate field.

For EOF analysis, the climate field can be represented conceptually as:

\[
X(t,x,y)
\]

EOF analysis decomposes this field into spatial patterns and time series:

\[
X(t,x,y) \approx \sum_{k=1}^{K} PC_k(t)\,EOF_k(x,y)
\]

where:

- \(EOF_k(x,y)\) is the spatial pattern of mode \(k\);
- \(PC_k(t)\) is the temporal amplitude of that mode;
- each EOF mode explains a fraction of the total variance.

EOF1 explains the largest possible fraction of variance, EOF2 explains the largest remaining fraction, and so on.

---

# Exercise 3. First EOF Mode of Tropical Pacific SST

Run:

```bash
python w11_07_eof_first_mode.py
```

The EOF analysis is calculated over the Tropical Pacific domain:

- Latitude: **20°S–20°N**
- Longitude: **120°E–280°E**

The script first calculates DJF SST anomalies and removes the long-term linear trend.

The EOF calculation uses the `eofs` package:

```python
from eofs.xarray import Eof
```

and constructs the solver using latitude weighting:

```python
weights = np.sqrt(
    np.cos(np.deg2rad(datY.lat.values))
)[:, np.newaxis]

solver = Eof(
    datY,
    weights=weights
)
```

Latitude weighting is important because the physical area represented by a grid cell decreases toward the poles.

The first EOF mode and PC are then calculated from:

```python
eofs = solver.eofsAsCovariance(
    neofs=neval,
    pcscaling=1
)

pcs = solver.pcs(
    npcs=neval,
    pcscaling=1
)
```

The fraction of variance explained is calculated using:

```python
variance_percent = (
    solver.varianceFraction(
        neigs=neval
    ) * 100
)
```

---

## PC1 and the ENSO Pattern

The first PC describes the year-to-year amplitude of the leading SST variability mode.

The script also calculates a global SST correlation map with PC1:

```python
cor_map = correlation_with_pcs(
    sst_analysis,
    pcs
)
```

For Tropical Pacific SST, EOF1 is expected to resemble the dominant ENSO-related SST variability pattern.

Compare the PC1 time series with the Niño 3.4 time series from the previous example.

### Questions to consider

- Do the largest positive and negative PC1 years resemble strong El Niño and La Niña years?
- How similar is the PC1 correlation map to the Niño 3.4 correlation map?
- Why are they similar even though Niño 3.4 and EOF1 are calculated differently?
- What information does EOF analysis provide that a fixed regional index does not?

---

# Exercise 4. Multiple EOF Modes

Next, run:

```bash
python w11_09_eof_multiple_modes.py
```

This script calculates the first three EOF modes of detrended Tropical Pacific DJF SST.

The number of modes is controlled by:

```python
n_modes = 3
```

and:

```python
pcs, eofs, variance_percent = compute_eof_analysis(
    sst_analysis,
    latlonEOF=latlonEOF,
    neval=3,
    normalize=normalize_eof,
    min_coverage=0.9,
)
```

The program calculates:

- PC1, PC2, and PC3;
- the variance explained by each mode; and
- global SST correlation maps associated with each PC.

For the supplied analysis, EOF1 explains much more variance than EOF2 or EOF3, showing that one dominant mode accounts for a large fraction of Tropical Pacific SST variability.

### Important interpretation

The sign of an EOF is arbitrary.

For example:

```python
pcs = -pcs
eofs = -eofs
```

does **not** change the physical mode. It only reverses the sign convention of both the EOF and its corresponding PC.

---

# Exercise 5. Covariance-Based and Correlation-Based EOFs

The scripts include:

```python
normalize_eof = False
```

With:

```python
normalize_eof = False
```

the analysis is covariance based.

If:

```python
normalize_eof = True
```

each grid point is standardized before EOF analysis:

```python
dat_std = datY.std(dim="year")
datY = datY / dat_std
```

This produces a correlation-based EOF analysis.

For this class, keep:

```python
normalize_eof = False
```

unless instructed otherwise.

---

# Exercise 6. In-Class Exercise: North Atlantic SLP EOFs

Use:

```bash
w11_10_eof_multiple_modes_NAO.sample.py
```

This script applies the same EOF framework to **DJF sea-level pressure over the North Atlantic**.

The EOF domain is:

- Latitude: **20°N–80°N**
- Longitude: **90°W–40°E**

The input dataset is:

```python
slp.mon.mean.nc
```

The sample script intentionally contains incomplete function calls.

Complete the following three tasks.

---

## Task 1: Calculate DJF SLP Anomalies

Complete:

```python
slp_anom = calc_seasonal_anom(
    slp,
    window=,
    end_month=,
    clim_period=[clim_start, clim_end]
)
```

Use a 3-month seasonal mean ending in February so that the resulting field represents DJF.

The climatology period is:

```python
clim_start = "1991-01-01"
clim_end = "2020-12-31"
```

---

## Task 2: Calculate the First Three North Atlantic EOF Modes

Complete:

```python
pcs, eofs, variance_percent = compute_eof_analysis(
    ,
    latlonEOF=latlonEOF,
    neval=,
    normalize=normalize_eof,
    min_coverage=0.9,
)
```

Use the detrended SLP anomalies as the EOF input and calculate three modes.

Examine:

- the PC time series;
- the spatial correlation pattern for each mode; and
- the percentage of variance explained.

### Interpretation

The leading North Atlantic winter SLP mode should show a large-scale pressure seesaw resembling the **North Atlantic Oscillation (NAO)**.

---

## Task 3: Calculate Correlation Maps with the PCs

Complete:

```python
cor_map = correlation_with_pcs(
    ,
    ,
    min_coverage=0.9,
)
```

Calculate correlations between global DJF SLP anomalies and all three North Atlantic PCs.

After completing the script, confirm that three PC time series and three corresponding SLP correlation maps are produced.

---

# Homework 10: ENSO and Global Precipitation

## Objective

For homework, extend the Tropical Pacific EOF analysis to investigate how ENSO-related SST variability is associated with **global precipitation**.

Use the structure of:

```bash
w11_09_eof_multiple_modes.py
```

as your starting point.

Create:

```bash
w11_11_ENSO_precip.HW.py
```

---

## Homework Directions

Modify the multiple-EOF SST program so that:

1. **Tropical Pacific SST** is still used to calculate EOF1, EOF2, and EOF3.
2. The precipitation dataset is read from:

```python
prate.mon.mean.nc
```

3. DJF precipitation anomalies are calculated using the same seasonal-anomaly framework.
4. Precipitation is detrended consistently with SST when:

```python
use_detrended_data = True
```

5. The SST PCs are calculated from the Tropical Pacific SST field.
6. The global correlation field is calculated between **precipitation anomalies and the SST PCs**, rather than between SST anomalies and the SST PCs.
7. The final figure shows:
   - PC1, PC2, and PC3 time series; and
   - global precipitation correlation maps corresponding to PC1, PC2, and PC3.

The key change is the field passed into:

```python
correlation_with_pcs()
```

The EOFs and PCs still come from Tropical Pacific SST, but the correlation maps should use global precipitation.

For example, the workflow should conceptually be:

```python
pcs, eofs, variance_percent = compute_eof_analysis(
    sst_analysis,
    latlonEOF=latlonEOF,
    neval=3,
    normalize=normalize_eof,
    min_coverage=0.9,
)

cor_map = correlation_with_pcs(
    prc_global_analysis,
    pcs,
    min_coverage=0.9,
)
```

Use an appropriate diverging colormap for precipitation correlations.
**Check your result**: Your final figure should show the PC1, PC2, and PC3 time series together with the corresponding global precipitation correlation maps.

---

# Summary

The workflow developed in this class is:

```text
Monthly climate data
        ↓
Seasonal anomalies
        ↓
Optional detrending
        ↓
Select EOF domain
        ↓
Latitude-weighted EOF analysis
        ↓
EOF spatial modes + PC time series
        ↓
Variance explained
        ↓
Correlation of PCs with global climate fields
```

EOF analysis is a powerful method for identifying dominant modes of climate variability. In this exercise, it provides a data-driven representation of Tropical Pacific SST variability and allows the associated atmospheric and hydrologic teleconnection patterns to be examined using global correlation maps.
