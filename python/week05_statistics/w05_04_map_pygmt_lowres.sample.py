"""
Exercise: Plot Weather Station Air Temperature on a Map using PyGMT

This script reads monthly averaged weather station air temperature data
and plots the observations on a low-resolution topographic map using PyGMT.

Learning Objectives:
- Read and combine multiple climate-data files
- Calculate monthly averaged station data
- Create maps using PyGMT
- Compare high- and low-resolution topography datasets
- Plot station observations using latitude and longitude
- Apply colormaps to climate variables
- Save map figures as image files
"""

import os,sys
from pathlib import Path

import numpy as np
import pandas as pd
import pygmt


def create_map(data, minlon, maxlon, minlat, maxlat, title):

    # Create figure
    fig = pygmt.Figure()

    # Topography colormap
    pygmt.makecpt(
        cmap='topo',
#        series='0/4000/500',
        series='-5000/8000/1000',
        continuous=True
    )

    # Plot topography
    # With shading:
    # - brightness changes depending on slope direction
    # - terrain looks more realistic
    # - but colors no longer exactly match the colorbar

    fig.grdimage(
        grid='@earth_relief_10m',
        region=[minlon, maxlon, minlat, maxlat],
        projection='M4i',
        shading=True,
        frame=True
    )

    # Plot coastlines and borders
    fig.coast(
        shorelines=True,
        borders=["2/0.5p,red"]
    )

    # Topography colorbar
    fig.colorbar(
      frame='+l"Topography (m)"',
      position="x11.5c/6.6c+w6c+jTC+v"
    )

    # Temperature colormap
    pygmt.makecpt(
        cmap='jet',
        series=[-20, 40]
    )

    # Plot station temperature
    fig.plot(
        x=data['longitude'],
        y=data['latitude'],
        style='c0.12i',
        fill=data['airt'],
        cmap=True,
        pen='black'
    )

    # Add title
    fig.basemap(frame=[f'+t"{title}"'])

    # Temperature colorbar
    fig.colorbar(
        frame='af+l"Air Temperature (°C)"'
    )

    return fig


#### Read station data ####

# Directory containing CSV files
input_dir = Path("../../data_raw/UCRN.latlon")

# Create a list of CSV files
filenames = list(input_dir.glob('*.csv'))

# Store monthly averaged data
monthly_dats = []

for file_path in filenames:

    # Read CSV file
    data = pd.read_csv(file_path)

    # Convert date_time column
    data['date_time'] = pd.to_datetime(data['date_time'])

    # Set datetime index
    data.set_index('date_time', inplace=True)

    # Calculate monthly average
    monthly_data = data.resample('ME').mean()

    # Add to list
    monthly_dats.append(monthly_data)

# Combine all station data
combined_data = pd.concat(monthly_dats)

# Convert index back to column
combined_data.reset_index(inplace=True)

# Create year and month columns
combined_data['year'] = combined_data['date_time'].dt.year
combined_data['month'] = combined_data['date_time'].dt.month

print(combined_data)

#### Map settings ####

minlon, maxlon = -115, -108
minlat, maxlat = 36.5, 42.5

years = np.arange(2022, 2026)
months = np.arange(1, 13)
print(years)
print(months)
print(" ")

# Output directory
figdir = "fig_all/"
os.makedirs(figdir, exist_ok=True)

#### Create monthly maps ####

for year in years:
    for month in months:

        # Select year and month
        dfig = combined_data[
            (combined_data['year'] == year) &
            (combined_data['month'] == month)
        ]

        # Skip empty data
        if dfig.empty:
            continue

        # Create title
        title = f"{year}-{month:02d}"

        # Create map
        fig = create_map(
            dfig,
            minlon,
            maxlon,
            minlat,
            maxlat,
            title
        )

        # Save figure
        figfile = figdir + f"temp_lowres_{year}-{month:02d}.png"

        fig.savefig(figfile, dpi=180)

        print("Saved:", figfile)
