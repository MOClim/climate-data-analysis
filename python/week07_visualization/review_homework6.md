# Homework 6 Review – Skew-T Diagram for an Inversion Day

## Overview
This homework review summarizes the major tasks and learning objectives from Homework 6.
Students practiced:
- Reading upper-air sounding data
- Creating Skew-T log-P diagrams
- Identifying atmospheric stability and inversion layers
- Analyzing severe weather environments using thermodynamic profiles
- Working with station IDs, dates, and UTC time

---
## Homework Tasks Review

### Step 1: Define Sounding Date and Time
Students selected a radiosonde observation date and time.
```python
# Define date and time of the sounding observation
# Format: year, month, day, hour (UTC)
doi = datetime(2024, 1, 29, 12)
```
Key Concepts
- Radiosonde observations are commonly available at 00 UTC and 12 UTC.
- Mountain Time (MST) is 7 hours behind UTC.
- Correct UTC conversion is important when analyzing weather events.

### Step 2: Define Station ID
Students selected a sounding station.
```python
sid = "SLC"
sname = 'Salt Lake City (USA)'
```

---
## Example: Temperature Inversion
An inversion occurs when temperature increases with height.
Common inversion environments include:
- Nocturnal cooling
- Subsidence under high pressure
- Frontal boundaries

Inversions can suppress vertical mixing and convection.
