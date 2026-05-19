# Week 05 (Day 10): Advanced Climate Data Visualization and Histograms

## Overview

This module introduces advanced climate-data visualization techniques using:
- Cartopy map projections
- scientific data formats
- histogram analysis
- monthly and annual climate statistics

Students will visualize climate datasets using Cartopy, NetCDF, Xarray, and histograms.

## Topics
- Cartopy map projections
- NetCDF climate datasets
- Scientific data formats:
  - Pandas
  - NumPy
  - Xarray
  - NetCDF
- Temperature histograms
- Precipitation histograms
- Monthly vs annual climate statistics

---
### Exercise 1: Compare Map Projections using Cartopy
```bash
cp w05_05_various_projection_cartopy.sample.py w05_05_various_projection_cartopy.py
```

#### Dataset Source
Utah Climate Center / Southwest Climate Observations (SWCO)
https://climate.usu.edu/swco/

#### Download Instructions
1.  Open the SWCO website.
2.  Use the interactive station map and zoom in to Logan
3.  Select
    temperature, precipitation
4.  Select the USU weather station:
  COOP 425186
5.  Select:
  metric units
  Modify: Missing Data Value: M --> Nan
6. Click COOP, then select 
  Mean Temperature
  Precipitation
  --> Get Preview
8. Download all
9. received the link of the ZIP archive and click the link
10. Unzip the downloaded file.
   ```bash
   mv ~Download/xxx.zip .
   unzip xxx.zip
   ```
11. Move:
    ```bash
    mv map-server-report-xxxxxxxxx ../../data_raw/
    ```
12. Confirm the CSV file exists:
    ```bash
    less ../../data_raw/map-server-report-xxxxxxxxx/COOP/425186/dly-report.csv
    ```
---
#### Coding Steps

Step 1: Define the data directory
Example:
```python
from pathlib import Path

data_dir = Path(
    '../../data_raw/map-server-report-1779136575/COOP/425186'
)
```
Caution: `solution/w05_07_histogram.solution.py` uses the absolute path instead of the relative path like above. 

Define the CSV filename
Example:
```python
filename = data_dir / 'dly-report.csv'
```

Step 2: Read the CSV file
Example:
```python
df = pd.read_csv(
    filename,
    header=0,
    skiprows=19,
    na_values='nan'
)
```

