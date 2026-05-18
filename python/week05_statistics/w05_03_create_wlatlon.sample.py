import pandas as pd
import numpy as np
import sys, os
import glob

def update_location_info(data,file_path):

  # Extract the station IDs from the second line of each file
  with open(file_path, 'r') as file:
   lines = file.readlines()
   if len(lines) > 1:
     second_line = lines[1].strip()
     # Extract the station ID after the colon
     tstation_id = second_line.split(': ')[1]
     station_id = tstation_id.split('"')[0]  # Splits at the dash and takes the first part
  return station_id
 
#### Station lat/lon information ###

station_latlon = pd.read_csv('../data/station_locate.csv')

# Convert station_id to string for merging
station_latlon['station_id'] = station_latlon['station_id'].astype(str)

#### Station ID and data ###
outdir = '../data_UCRN.latlon/'
# Create directory if it doesn't exist
os.makedirs(outdir, exist_ok=True)


# Directory containing the data files
indir = '../data_UCRN/'
# List all CSV files in the directory
file_paths = glob.glob(os.path.join(indir, '*.csv'))
print("File Paths")
print(file_paths)

for file_path in file_paths:
  # Read the CSV file, assuming data starts from the first row (so no skiprow command)
  data = pd.read_csv(file_path, header=0, skiprows=4,usecols=['date_time', 'station_id', 'airt'])

  data['date_time'] = pd.to_datetime(data['date_time'])
  data.set_index('date_time',inplace=True)

  # Display the result
  print(data.head())

  station_id = update_location_info(data,file_path)
  print("Station ID:", station_id)

  #### Merged data with lat and lon information ###
  matching_station = station_latlon[station_latlon['station_id'] == station_id]
  if not matching_station.empty:
   data['latitude'] = matching_station['latitude'].values[0]
   data['longitude'] = matching_station['longitude'].values[0]

  # Display the result
  print(data.head())

  filename = os.path.basename(file_path)
  print('Save to :'+outdir+filename) 

  # Assuming 'df' is your DataFrame
  data.to_csv(outdir+filename, index=True)
  del data

