import os
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

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
plt.title('World Map with Additional Features')

# Add gridlines
ax.gridlines()

# Save the plot as a JPEG file
filename='p09_01.cartopy.jpg'
plt.savefig(filename, format='jpeg', dpi=300)

# Display the map
#plt.show()

