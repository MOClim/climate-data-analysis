import pandas as pd
import numpy as np
import sys, os
import glob
import pygmt

def create_maps(dat,lons,lats,minlon,maxlon,minlat,maxlat,titleX):

 #define etopo data file
 topo_data = '@earth_relief_30s' #30 arc second global relief (SRTM15+V2.1 @ 1.0 km)

 # Visualization
 fig = pygmt.Figure()

 # make color pallets
 pygmt.makecpt(
    cmap='topo',
    series='-8000/8000/1000',
    continuous=True
 )

 #plot high res topography
 fig.grdimage(
    grid=topo_data,
    region=[minlon, maxlon, minlat, maxlat],
    projection='M4i',
    shading=True,
    frame=True
    )

 # plot coastlines
 fig.coast(
    region=[minlon, maxlon, minlat, maxlat],
    projection='M4i',
    shorelines=True,
    frame=True
    )
 fig.coast(borders=["2/0.5p,red"])

 ## Plot colorbar
 # Default is horizontal colorbar
 fig.colorbar(
    frame='+l"Topography (m)"',
    position="x11.5c/6.6c+w6c+jTC+v"
    )

 # Color options and data range
 pygmt.makecpt(cmap="jet", series=[-20,40])

 # Plot temperature at each weather station
 fig.plot(
    x=lons,
    y=lats,
    style='c0.1i',
    color=dat['airt'],
    cmap=True,
    pen='black'
    )

# Main and colorbar titles
 fig.basemap(frame=["a", f'WSne+t"{titleX}"'])
 fig.colorbar(frame='af+l"Air Temperature (oC)"')

 return(fig)



#### Read the station data created by p09_03.py ###

# Directory containing the data files
indir = '../data_UCRN.latlon/'

# List all CSV files in the directory
file_paths = glob.glob(os.path.join(indir, '*.csv'))
print("File Paths")
print(file_paths)

# Read the data from each file and merge with station location data
monthly_dats = []
for file_path in file_paths:

    data = pd.read_csv(file_path)
    data['date_time'] = pd.to_datetime(data['date_time'])
    data.set_index('date_time',inplace=True)

    # Calculate monthly averaged data
    monthly_data = data.resample('M').mean()

    # Convert station_id back to integer
    monthly_data['station_id'] = monthly_data['station_id'].astype(int)

    # Adds monthly_data to a list called all_data.
    monthly_dats.append(monthly_data)
    del data, monthly_data


# Combine all the dataframes stored in monthly_dats into a single dataframe
combined_data = pd.concat(monthly_dats)
# For efficient data manipulation 
combined_data.reset_index(inplace=True)

# Create year and month columns
combined_data['year'] = combined_data['date_time'].dt.year
combined_data['month'] = combined_data['date_time'].dt.month

print("Merged Data")
print(combined_data)

#-------

## map range
minlon, maxlon = -115, -108
minlat, maxlat = 36.5, 42.5

yrall = np.arange(2020,2024,dtype='int')
mnall = np.arange(1,13,dtype='int')

figdir = "fig_all/"
# Create directory if it doesn't exist
os.makedirs(figdir, exist_ok=True)

for year in yrall:
  for month in mnall:

   # Filter data for the specified year and month
   dfig = combined_data[(combined_data['year'] == year) & (combined_data['month'] == month)]
   print(dfig)

   if dfig.size == 0:
     print('not fig')
   else:
     titleX = f'{year}-'+'{:02d}'.format(month)
     print(titleX)

     ## Generate fake coordinates in the range for plotting
     fig = create_maps(dfig,dfig['longitude'],dfig['latitude'],minlon,maxlon,minlat,maxlat,titleX)

     # save figure as pdf
     figfile = figdir + "temp_"+f'{year}-'+'{:02d}'.format(month)+'.png'
     fig.savefig(figfile, crop=True, dpi=180)

