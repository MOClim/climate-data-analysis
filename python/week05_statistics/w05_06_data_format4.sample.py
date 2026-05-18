"""
Exercise: Compare Different Scientific Data Formats

This script demonstrates how to create and visualize four common
scientific data formats used in climate and Earth science:
Pandas, NumPy, Xarray, and NetCDF.

Learning Objectives:
- Create simple scientific datasets
- Compare tabular and gridded data structures
- Visualize different data formats
- Create multi-panel figures using matplotlib
- Save figures as image files
"""

from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr
import netCDF4 as nc
import matplotlib.pyplot as plt

##################################################
# Create datasets
##################################################

# Pandas DataFrame
pd_data = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6],
    'C': [7, 8, 9]
})

# NumPy Array
np_data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

# Xarray DataArray
xr_data = xr.DataArray(
    np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
    dims=("latitude","longitude"),
    coords={"latitude": [90, 0, -90], "longitude": [0, 180, 360]}
)

# NetCDF4 Dataset
# NetCDF4 Dataset
file_path = Path('../../data_raw/example.nc')

# Create a NetCDF file
dataset = nc.Dataset(file_path, 'w', format='NETCDF4')

# Create dimensions
dataset.createDimension('time', 5)
dataset.createDimension('lat', 5)
dataset.createDimension('lon', 5)

# Create variables
times = dataset.createVariable('time', 'f4', ('time',))
lats = dataset.createVariable('lat', 'f4', ('lat',))
lons = dataset.createVariable('lon', 'f4', ('lon',))
temperature = dataset.createVariable(
    'temperature',
    'f4',
    ('time', 'lat', 'lon')
)

# Add coordinate values
times[:] = np.arange(5)
lats[:] = np.linspace(-90, 90, 5)
lons[:] = np.linspace(-180, 180, 5)

# Add temperature data
temperature[:] = np.random.uniform(-10, 40, (5, 5, 5))

# Close file
dataset.close()

# Read the NetCDF file
dataset = nc.Dataset(file_path)

# Select one time slice for plotting
nc_data = dataset.variables['temperature'][0, :, :]

# Read latitude and longitude
lats = dataset.variables['lat'][:]
lons = dataset.variables['lon'][:]

dataset.close()


##################################################
# Create a 2 x 2 panel figure
##################################################

# Create a 2 x 2 panel figure
fig, axs = plt.subplots(2, 2, figsize=(8, 8))

##################################################
# Plot Pandas DataFrame
##################################################

axs[0, 0].axis('off')

table = axs[0, 0].table(
    cellText=pd_data.values,
    colLabels=pd_data.columns,
    loc='center'
)

table.auto_set_font_size(False)
table.set_fontsize(10)

axs[0, 0].set_title('Pandas DataFrame')


##################################################
# Plot NumPy Array
##################################################

im1 = axs[1, 0].matshow(np_data, cmap='viridis')

for (i, j), val in np.ndenumerate(np_data):
    axs[1, 0].text(
        j,
        i,
        val,
        ha='center',
        va='center',
        color='white'
    )

axs[1, 0].set_title('NumPy Array')
axs[1, 0].set_xlabel('Column Index')
axs[1, 0].set_ylabel('Row Index')
axs[1, 0].set_xticks(np.arange(np_data.shape[1]))
axs[1, 0].set_yticks(np.arange(np_data.shape[0]))

# Move x-axis labels to bottom
axs[1, 0].xaxis.set_ticks_position('bottom')
axs[1, 0].xaxis.set_label_position('bottom')


##################################################
# Plot Xarray DataArray
##################################################

im2 = axs[0, 1].matshow(xr_data, cmap='viridis')

for (i, j), val in np.ndenumerate(xr_data):
    axs[0, 1].text(
        j,
        i,
        val,
        ha='center',
        va='center',
        color='white'
    )

axs[0, 1].set_title('Xarray DataArray')
axs[0, 1].set_xlabel('longitude')
axs[0, 1].set_ylabel('latitude')
axs[0, 1].set_xticks(np.arange(len(xr_data.longitude)))
axs[0, 1].set_xticklabels(xr_data.longitude.values)
axs[0, 1].set_yticks(np.arange(len(xr_data.latitude)))
axs[0, 1].set_yticklabels(xr_data.latitude.values)

# Move x-axis labels to bottom
axs[0, 1].xaxis.set_ticks_position('bottom')
axs[0, 1].xaxis.set_label_position('bottom')


##################################################
# Plot NetCDF Dataset
##################################################

im3 = axs[1, 1].matshow(nc_data, cmap='coolwarm')

axs[1, 1].set_title('NetCDF: Temperature at time index 0')

axs[1, 1].set_xlabel('longitude')
axs[1, 1].set_ylabel('latitude')

# Set longitude tick labels
axs[1, 1].set_xticks(np.arange(len(lons)))
axs[1, 1].set_xticklabels(lons.astype(int))

# Set latitude tick labels
axs[1, 1].set_yticks(np.arange(len(lats)))
axs[1, 1].set_yticklabels(lats.astype(int))

# Move x-axis labels to bottom
axs[1, 1].xaxis.set_ticks_position('bottom')
axs[1, 1].xaxis.set_label_position('bottom')


##################################################
# Add colorbars
##################################################

fig.colorbar(im1, ax=axs[0, 1], shrink=0.7)
fig.colorbar(im2, ax=axs[1, 0], shrink=0.7)
fig.colorbar(im3, ax=axs[1, 1], shrink=0.7)

# Save the plot as a JPEG file
output_path = Path(__file__).with_suffix('.jpg')
fig.savefig(output_path, dpi=300)

plt.show()

