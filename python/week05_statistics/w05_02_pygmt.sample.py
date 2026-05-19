"""
Create a Global Map using PyGMT

This script demonstrates how to create a simple global map using the PyGMT library.
The program applies the Robinson projection, draws coastlines, and saves the figure
as a JPEG image file.

PyGMT does not use matplotlib layout functions such as tight_layout().
Map spacing and layout are controlled directly within PyGMT commands.

Learning Objectives:
- Create a basic map using PyGMT
- Configure map projections and map regions
- Add coastlines and color settings
- Save a figure as an image file
"""

import pygmt
from pathlib import Path

# Create a new figure
fig = pygmt.Figure()

# Set up the projection and region for the map
# 'N' denotes the Robinson projection
# '12i' specifies the width of the map in inches
# "af" automatically draws axis annotations and frame lines
# "+t" adds a title to the map
# Define the map title
title = "Global Map using Robinson Projection"
fig.basemap(
    region="g",
    projection="N12i",
    frame=["af", f'+t{title}']
)


# Plot the coastlines
fig.coast(shorelines="1/0.5p", water="skyblue", land="gray", resolution="i")

# Save the plot as a JPEG file
output_path = Path(__file__).with_suffix('.jpg')
fig.savefig(output_path, dpi=300)

# Show the figure
fig.show()
