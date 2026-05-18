import numpy as np
import pandas as pd
import xarray as xr
import netCDF4 as nc
import matplotlib.pyplot as plt

# Pandas DataFrame
pd_data = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6],
    'C': [7, 8, 9]
})
fig, ax = plt.subplots()
ax.axis('tight')
ax.axis('off')
table = ax.table(cellText=pd_data.values, colLabels=pd_data.columns, rowLabels=pd_data.index, loc='center')
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1.2, 1.2)
ax.set_title('Pandas DataFrame')

# Save the plot as a JPEG file
filename='p10_02.data_format4.pd.jpg'
plt.savefig(filename, format='jpeg', dpi=300)

plt.show()

# NumPy Array
np_data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
fig, ax = plt.subplots()
cax = ax.matshow(np_data, cmap='viridis')
fig.colorbar(cax)
for (i, j), val in np.ndenumerate(np_data):
    ax.text(j, i, val, ha='center', va='center', color='white')
ax.set_title('NumPy Array')
ax.set_xlabel('Column Index')
ax.set_ylabel('Row Index')
ax.set_xticks(np.arange(np_data.shape[1]))
ax.set_yticks(np.arange(np_data.shape[0]))

# Save the plot as a JPEG file
filename='p10_02.data_format4.nu.jpg'
plt.savefig(filename, format='jpeg', dpi=300)

plt.show()

# Xarray DataArray
xr_data = xr.DataArray(
    np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
    dims=("latitude","longitude"),
    coords={"latitude": [90, 0, -90], "longitude": [0, 180, 360]}
)
fig, ax = plt.subplots()
cax = ax.matshow(xr_data, cmap='viridis')
fig.colorbar(cax)
for (i, j), val in np.ndenumerate(xr_data):
    ax.text(j, i, val, ha='center', va='center', color='white')
ax.set_title('Xarray DataArray')
ax.set_xlabel('longitude')
ax.set_ylabel('latitude')
ax.set_xticks(np.arange(len(xr_data.longitude)))
ax.set_xticklabels(xr_data.longitude.values)
ax.set_yticks(np.arange(len(xr_data.latitude)))
ax.set_yticklabels(xr_data.latitude.values)

# Save the plot as a JPEG file
filename='p10_02.data_format4.xr.jpg'
plt.savefig(filename, format='jpeg', dpi=300)

plt.show()

# NetCDF4 Dataset
file_path = 'example.nc'
dataset = nc.Dataset(file_path, 'w', format='NETCDF4')
time_dim = dataset.createDimension('time', None)
lat_dim = dataset.createDimension('lat', 5)
lon_dim = dataset.createDimension('lon', 5)
times = dataset.createVariable('time', np.float64, ('time',))
lats = dataset.createVariable('lat', np.float32, ('lat',))
lons = dataset.createVariable('lon', np.float32, ('lon',))
temperature = dataset.createVariable('temperature', np.float32, ('time', 'lat', 'lon'))
precipitation = dataset.createVariable('precipitation', np.float32, ('time', 'lat', 'lon'))
dataset.description = 'Example dataset'
lats.units = 'degrees north'
lons.units = 'degrees east'
temperature.units = 'K'
precipitation.units = 'mm'
lats[:] = np.linspace(-90, 90, 5)
lons[:] = np.linspace(-180, 180, 5)
times[:] = np.arange(0, 5, 1)
temperature[:, :, :] = np.random.uniform(low=250, high=300, size=(5, 5, 5))
precipitation[:, :, :] = np.random.uniform(low=0, high=10, size=(5, 5, 5))
dataset.close()

dataset = nc.Dataset(file_path, 'r')
temperature = dataset.variables['temperature'][:]
precipitation = dataset.variables['precipitation'][:]
lats = dataset.variables['lat'][:]
lons = dataset.variables['lon'][:]
fig, axs = plt.subplots(1, 2, figsize=(14, 6))
cax1 = axs[0].matshow(temperature[0, :, :], cmap='coolwarm')
fig.colorbar(cax1, ax=axs[0])
axs[0].set_title('Temperature at time index 0')
axs[0].set_xlabel('Longitude Index')
axs[0].set_ylabel('Latitude Index')
cax2 = axs[1].matshow(precipitation[0, :, :], cmap='Blues')
fig.colorbar(cax2, ax=axs[1])
axs[1].set_title('Precipitation at time index 0')
axs[1].set_xlabel('Longitude Index')
axs[1].set_ylabel('Latitude Index')
# Correct way to set the title for the entire figure
fig.suptitle('NetCDF', fontsize=16)

# Save the plot as a JPEG file
filename='p10_02.data_format4.cdf.jpg'
plt.savefig(filename, format='jpeg', dpi=300)

plt.show()

