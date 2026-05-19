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

#### Download SST Datasets
Dataset source: HadISST sea surface temperature
https://www.metoffice.gov.uk/hadobs/hadisst/data/download.html

1. Download the NetCDF file:
```bash
HadISST_sst.nc.gz
```

2. Move the downloaded file to your working directory:
```bash
mv ~Downloads/HadISST_sst.nc.gz .
```

2. Unzip the file
On Mac/Linux:
```bash
gunzip HadISST_sst.nc.gz
```
On Windows, use one of the following:
```bash
gzip -d HadISST_sst.nc.gz
```
or unzip it using File Explorer or 7-Zip.

3. Check the NetCDF file:
```bash
ncdump HadISST_sst.nc |less
```

4. Move the NetCDF file to the `data_raw` directory:
```bash
mv HadISST_sst.nc ../../data_raw/
```

#### Read NetCDF data
Example:
```python
data_dir = Path('../../data_raw')
filename = data_dir / 'HadISST_sst.nc'
```
Opens the NetCDF file in read-only mode.
```python
f = Dataset(filename, mode='r')
```
Reads longitude and latitude values and extract SST at the first time step for all latitudes and longitudes.
```python
# Read longitude, latitude, and SST data
lons = f.variables['longitude'][:]
lats = f.variables['latitude'][:]
sst = f.variables['sst'][0, :, :]
```
This extracts one 2-dimensional SST map:
```text
(latitude, longitude)
```
from a 3-dimensional dataset:
```text
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

This exercise demonstrates how to download weather-station observations from the Utah Climate Center and create a histogram from long-term climate datasets.

#### Dataset Source
Utah Climate Center / Surface Weather and Climate Observations (SWCO)
https://climate.usu.edu/swco/

---

#### Download Instructions
1. Open the SWCO website.

2. Use the interactive station map and zoom into Logan, Utah.

3. Select:
   - Temperature
   - Precipitation

4. Select the USU weather station:
   - COOP 425186

5. Select:
   - Metric units
   - Missing Data Value:
     `M → nan`

6. Click:
   - COOP
   - Mean Temperature
   - Precipitation

7. Click:
   - Get Preview

8. Download all files.

9. Open the download link for the ZIP archive.

10. Move and unzip the downloaded file:
   ```bash
   mv ~Download/xxx.zip .
   unzip xxx.zip
   ```

11. Move the extracted directory:
    ```bash
    mv map-server-report-xxxxxxxxx ../../data_raw/
    ```
    
12. Confirm the CSV file exists:
    ```bash
    less ../../data_raw/map-server-report-xxxxxxxxx/COOP/425186/dly-report.csv
    ```
    
---
#### Coding Steps

#### Step 1: Define the data directory
Example:
```python
from pathlib import Path

data_dir = Path(
    '../../data_raw/map-server-report-1779136575/COOP/425186'
)
```
Caution:
```bash
solution/w05_07_histogram.solution.py
```
uses an absolute path instead of the relative path above.

#### Step 2: Define the CSV filename
Example:
```python
filename = data_dir / 'dly-report.csv'
```
This creates the full path to the CSV file.

#### Step 3: Read the CSV file
Example:
```python
df = pd.read_csv(
    filename,
    header=0,
    skiprows=19,
    na_values='nan'
)
```
Meaning:
- `header=0`
  → first row contains variable names
- `skiprows=19`
  → skip metadata rows
- `na_values='nan'`
  → treat "nan" as missing values

---
### Exercise 4: Monthly Precipitation Histogram

```bash
cp w05_08_historgram_precip.sample.py w05_08_historgram_precip.py
```

#### Trace Precipitation

In precipitation datasets, T means trace precipitation.
A trace value indicates that precipitation was observed, but the amount was too small to measure accurately.

Because T is text, pandas may read the precipitation column as a string instead of numeric data.

Convert it before analysis:
```python
df['pcpn'] = df['pcpn'].replace('T', 0.0)
df['pcpn'] = pd.to_numeric(df['pcpn'], errors='coerce')
```
- `replace('T', 0.0)` treats trace precipitation as 0.0 mm
- `pd.to_numeric()` converts the column to numbers
- `errors='coerce'` changes invalid values into NaN

Then monthly precipitation can be calculated:
```python
df_mon = df['pcpn'].resample('ME').mean()
```

---
### Homework 5: Monthly vs Annual Histogram Analysis

```bash
cp w05_09_hist_mon_anu.HW_sample.py w05_09_hist_mon_anu.HW.py
```

#### Homework Tasks
1. Create:
  - monthly datasets
  - annual datasets
    
2. Calculate:
  - monthly mean temperature
  - annual mean temperature
  - monthly precipitation totals
  - annual precipitation totals

3. Create histograms for:
  - monthly temperature
  - annual temperature
  - monthly precipitation
  - annual precipitation

4. Compare:
  - monthly vs annual distributions
  - temperature vs precipitation variability

5. Modify histogram bin numbers for each panel.

#### Submission

Upload the following files to the Canvas Homework 5 page:
```bash
w05_09_hist_mon_anu.HW.py
w05_09_hist_mon_anu.HW.jpg
```

---
## Key takeaway
