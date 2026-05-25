# Day 12: Radiosonde Data and Skew-T Analysis

## Overview

This lesson introduces upper-air radiosonde observations and Skew-T log-P diagrams commonly used in atmospheric science and meteorology.

Students will learn how to:
- Download upper-air sounding data from a remote server
- Read radiosonde observations into a Pandas DataFrame
- Visualize vertical atmospheric profiles using a Skew-T diagram
- Analyze atmospheric stability and convection
- Interpret CAPE, LCL, dew point, and wind profiles

---
### Radiosonde Observations

Radiosondes measure vertical atmospheric profiles including:
- Pressure
- Temperature
- Dew point temperature
- Relative humidity
- Wind speed
- Wind direction
These observations are commonly collected twice daily using weather balloons.

### Skew-T Log-P Diagram
A Skew-T diagram is a thermodynamic chart used to visualize:
- Atmospheric stability
- Moisture structure
- Cloud formation potential
- Convection and CAPE
- Wind shear and vertical wind structure

Common Skew-T diagnostics include:
- LCL (Lifting Condensation Level)
- LFC (Level of Free Convection)
- CAPE (Convective Available Potential Energy)
- Dry and moist adiabats

---
## Data Source

Upper-air sounding data are obtained from the University of Wyoming sounding archive:

University of Wyoming Upper-Air Sounding Archive

This website can be used to:

Search sounding observations
Find station IDs
Explore historical radiosonde datasets

---
## Exercise 1: Read Remote Radiosonde Data

File: `w06_06_read_remote_data.py`

This exercise introduces remote atmospheric sounding data retrieval using the Siphon package and the University of Wyoming sounding archive.

### Key Functions
```python
WyomingUpperAir.request_data()
```
Downloads radiosonde observations from the remote server.

---
## Exercise 2: Create a Basic Skew-T Diagram

```pthon
cp w06_07_skew_T.sample.py w06_07_skew_T.py
```
This exercise introduces the construction of a Skew-T log-P diagram using radiosonde observations and `MetPy`.

Students learn how to:
- Extract atmospheric variables from sounding data
- Attach meteorological units using MetPy
- Plot temperature and dew point profiles
- Add atmospheric stability diagnostics
- Visualize wind barbs and adiabatic reference lines

### Key Functions
```python
mpplots.SkewT()
```
Creates a Skew-T plotting object.

```python
skewt.plot()
```
Plots temperature and dew point profiles.

```python
mpcalc.lcl()
```
Calculates the lifting condensation level (LCL).

```python
mpcalc.lfc()
```
Calculates the level of free convection (LFC).

```python
mpcalc.parcel_profile()
```
Calculates parcel ascent temperature profiles.

```python
skewt.shade_cape()
```
Shades the CAPE region on the diagram.

- 
## Exercise 3: Analyze a Large-CAPE Environment

File: `w06_08_skew_T_large_cape.py`

This exercise demonstrates a strongly unstable atmospheric sounding associated with large CAPE and deep convection.

Students learn how to:
- Identify unstable atmospheric environments
- Examine CAPE and parcel buoyancy
- Analyze severe-weather sounding structures
- Compare stable and unstable atmospheric profiles

### Suggested Discussion
- Why does large CAPE indicate a stronger potential for convection and thunderstorm development?
- How do temperature and dew point profiles influence atmospheric instability?

---
### Important Notes
The University of Wyoming sounding archive server occasionally becomes temporarily busy or unavailable.

If an HTTP 503 error occurs while downloading sounding data:
```text
requests.exceptions.HTTPError: Server Error (503)
```
wait briefly and retry the program.

---
## Key Takeaways
- Radiosondes provide vertical atmospheric observations including temperature, humidity, pressure, and wind.
- Skew-T diagrams help visualize atmospheric stability and moisture structure.
- CAPE is commonly used to identify unstable environments favorable for convection.
- `MetPy` and `Siphon` allow direct access and visualization of upper-air sounding data in Python.
- Atmospheric profiles can be analyzed to investigate cloud formation, instability, and severe weather potential.



