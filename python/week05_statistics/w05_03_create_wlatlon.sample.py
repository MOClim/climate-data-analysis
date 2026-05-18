"""
Exercise: Add Latitude and Longitude Information to Station Data

This script reads UCRN station air temperature data, adds latitude and
longitude information from a station metadata file, and saves the updated
CSV files to a new directory.
"""

import os, sys
from pathlib import Path
import pandas as pd


# Read station metadata
station_latlon = pd.read_csv('../../data/station_locate.csv')

# Convert station_id to string for merging
station_latlon['station_id'] = station_latlon['station_id'].astype(str)

# Input and output directories
input_dir = Path("../../data/UCRN")
# Create a list of all CSV files
filenames = list(input_dir.glob('*.csv'))

output_dir = Path("../../data_raw/UCRN.latlon")
output_dir.mkdir(parents=True, exist_ok=True)


# Process each station file
for file_path in filenames:

    # Read air temperature data
    data = pd.read_csv(
        file_path,
        header=0,
        skiprows=26,
        usecols=["date_time", "station_id", "airt"]
    )

    # Convert date_time to datetime index
    data["date_time"] = pd.to_datetime(data["date_time"])
    data = data.set_index("date_time")

    # Get the first station ID value
    station_id = str(data['station_id'].iloc[0])

    # Find matching latitude and longitude
    match = station_latlon[station_latlon["station_id"] == station_id]

    if not match.empty:
        data["latitude"] = match["latitude"].iloc[0]
        data["longitude"] = match["longitude"].iloc[0]

    # Reorder columns
    data = data[["station_id", "latitude", "longitude", "airt"]]

    # Save updated file
    output_file = output_dir / file_path.name
    data.to_csv(output_file)

    print(f"Saved: {output_file}")
