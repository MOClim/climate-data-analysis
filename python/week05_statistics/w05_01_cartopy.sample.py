
# matplotlib object names:
#
# Relationship:
# ----------------------------------------------------
# matplotlib.pyplot (plt)
#   -> creates and manages Figure objects
#
# Figure object (fig)
#   -> represents the entire plotting canvas
#   -> can contain one or more Axes objects
#
# Axes object (ax)
#   -> represents the plotting region inside the Figure
#   -> contains the actual plot or map
#
# In Cartopy:
# ax is a GeoAxes object with map projection support

import os
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
warnings.filterwarnings("ignore", message="invalid value encountered in create_collection")

# Create a new figure with a specific size
fig = plt.figure(figsize=(10, 5))

# Create a GeoAxes in the figure with the desired projection (Robinson projection)
ax = fig.add_subplot(1, 1, 1, projection=ccrs.Robinson())

# Set the global extent
ax.set_global()

# Add coastlines with a specific resolution
ax.coastlines(resolution='110m')

# Add land and ocean colors
ax.add_feature(cfeature.LAND, edgecolor='black')
ax.add_feature(cfeature.OCEAN, edgecolor='black')

# Add rivers
ax.add_feature(cfeature.RIVERS)

# Add a title to the map
ax.set_title('World Map with Additional Features')

# Add gridlines
ax.gridlines()

# Adjust spacing automatically
fig.tight_layout()

# Save the plot as a JPEG file
output_path = Path(__file__).with_suffix('.jpg')
fig.savefig(output_path, dpi=300)

# Display the map
plt.show()

