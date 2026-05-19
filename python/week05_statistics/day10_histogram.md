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

This exercise visualizes global sea surface temperature (SST) using several Cartopy map projections.

#### Download SST datasets
1. Download
Access to https://www.metoffice.gov.uk/hadobs/hadisst/data/download.html and download NetCDF format datasets.
```bash
mv ~Download/HadISST_sst.nc.gz .
```

2. Data 
To extract `HadISST_sst.nc.gz on Mac:
```bash
gunzip HadISST_sst.nc.gz
```
On Windows:
```bash
gzip -d HadISST_sst.nc.gz
```
or
```bash
tar -xzf HadISST_sst.nc.gz
```

3. Check the netCDF data
```bash
ncdump HadISST_sst.nc |less
```

4. Save the data
Move `HadISST_sst.nc` to data_raw directory.
```bash
mv HadISST_sst.nc ../../data_raw/
```

#### Read NetCDF data
Example:
```python
data_dir = Path('../../data_raw')
filename = data_dir / 'HadISST_sst.nc'

f = Dataset(filename, mode='r')

# Read longitude, latitude, and SST data
lons = f.variables['longitude'][:]
lats = f.variables['latitude'][:]
sst = f.variables['sst'][0, :, :]
```
This extracts one 2-dimensional SST map:
```python
(latitude, longitude)
```
from a 3-dimensional dataset:
```python
(time, latitude, longitude)
```

---
### Exercise 2: Compare Scientific Data Formats
```bash
cp w05_06_data_format4.sample.py w05_06_data_format4.py
```

#### Topics
- Pandas DataFrame
- NumPy Array
- Xarray DataArray
- NetCDF Dataset
- Multi-panel visualization

---
### Exercise 3: Monthly Temperature Histogram
This exercise is to learn how to download specific station data from the Utah Climate Center and create a histogram from long time series datasets.

#### Dataset Source
Utah Climate Center / Surface Weather and Climate Observations (SWCO)
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

