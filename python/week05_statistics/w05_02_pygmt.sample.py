import pygmt

# Create a new figure
fig = pygmt.Figure()

# Set up the projection and region for the map
# 'N' denotes the Robinson projection
# '12i' specifies the width of the map in inches
fig.basemap(region="g", projection="N12i", frame=["af", "+t\"Global Map using Robinson Projection\""])

# Plot the coastlines
fig.coast(shorelines="1/0.5p", water="skyblue", land="gray", resolution="i")

# Save the figure to a file
# Save the plot as a JPEG file
filename='p09_02.pygmt.jpg'
fig.savefig(filename)


# Show the figure
fig.show()
