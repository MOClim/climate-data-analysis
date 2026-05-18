import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import cartopy.crs as ccrs
from cartopy import feature
import os, sys

# reading in netCDF file
indir = '../data/'
filename = indir + 'HadISST_sst.nc'
f = Dataset(filename, mode='r')
lons = f.variables['longitude'][:]
lats = f.variables['latitude'][:]
dat = f.variables['sst'][0,:,:]
f.close()

# Mask the data: replace -1000 with NaN
fld = np.where(dat == -1000, np.nan, dat)
fld = np.where(fld == -1.e+30, np.nan, fld)


# define contour levels
levels = np.arange(0, 26, 1)

# set up figure and map projection
fig = plt.figure(figsize=(16., 8))

# Set global font size
plt.rcParams.update({'font.size': 20})

# PlateCarree (equidistant cylindrical projection)
ax1 = plt.subplot(2, 4, 1, projection=ccrs.PlateCarree(central_longitude=180))
ax1.set_extent([-180, 180, -90, 90], crs=None)
ax1.coastlines(resolution='110m', linewidth=0.5)
ax1.gridlines(linewidth=0.5, color='black', alpha=0.5, linestyle=':')
ax1.set_title('PlateCaree', fontsize=12)
ax1.contourf(lons, lats, fld, levels, transform=ccrs.PlateCarree(),
cmap=plt.cm.viridis, extend='both')

# Robinson
ax2 = plt.subplot(2, 4, 2, projection=ccrs.Robinson())
ax2.coastlines(resolution='110m', linewidth=0.5)
ax2.gridlines(linewidth=0.5, color='black', alpha=0.5, linestyle=':')
ax2.set_title('Robinson', fontsize=12)
ax2.contourf(lons, lats, fld, levels, transform=ccrs.PlateCarree(),
cmap=plt.cm.viridis, extend='both')

# Mollweide
ax3 = plt.subplot(2, 4, 3, projection=ccrs.Mollweide())
ax3.coastlines(resolution='110m', linewidth=0.5)
ax3.gridlines(linewidth=0.5, color='black', alpha=0.5, linestyle=':')
ax3.set_title('Mollweide', fontsize=12)
ax3.contourf(lons, lats, fld, levels, transform=ccrs.PlateCarree(),
cmap=plt.cm.viridis, extend='both')

# LambertConformal
ax4 = plt.subplot(2, 4, 4, projection=ccrs.LambertConformal())
ax4.coastlines(resolution='110m', linewidth=0.5)
ax4.gridlines(linewidth=0.5, color='black', alpha=0.5, linestyle=':')
ax4.set_title('LambertConformal', fontsize=12)
ax4.contourf(lons, lats, fld, levels, transform=ccrs.PlateCarree(),
cmap=plt.cm.viridis, extend='both')

# NearsidePerspective
ax5 = plt.subplot(2, 4, 5,
projection=ccrs.NearsidePerspective(
satellite_height=2500000.0,
central_longitude=-1.253741,
central_latitude=51.758845))
ax5.coastlines(resolution='110m', linewidth=0.5)
ax5.add_feature(feature.BORDERS, linestyle='-', linewidth=0.25)
ax5.gridlines(linewidth=0.5, color='black', alpha=0.5, linestyle=':')
ax5.set_title('NearsidePerspective', fontsize=12)
ax5.contourf(lons, lats, fld, levels, transform=ccrs.PlateCarree(),
cmap=plt.cm.viridis, extend='both')

# InterruptedGoodeHomolosine
ax6 = plt.subplot(2, 4, 6, projection=ccrs.InterruptedGoodeHomolosine())
ax6.coastlines(resolution='110m', linewidth=0.5)
ax6.gridlines(linewidth=0.5, color='black', alpha=0.5, linestyle=':')
ax6.set_title('InterruptedGoodeHomolosine', fontsize=12)
ax6.contourf(lons, lats, fld, levels, transform=ccrs.PlateCarree(),
cmap=plt.cm.viridis, extend='both')

# RotatedPole
ax7 = plt.subplot(2, 4, 7, projection=ccrs.RotatedPole(pole_latitude=37.5,
pole_longitude=177.5))
ax7.coastlines(resolution='110m', linewidth=0.5)
ax7.gridlines(linewidth=0.5, color='black', alpha=0.5, linestyle=':')
ax7.set_title('RotatedPole', fontsize=12)
ax7.contourf(lons, lats, fld, levels, transform=ccrs.PlateCarree(),
cmap=plt.cm.viridis, extend='both')

# Orthographic
ax8 = plt.subplot(2, 4, 8, projection=ccrs.Orthographic())
ax8.coastlines(resolution='110m', linewidth=0.5)
ax8.gridlines(linewidth=0.5, color='black', alpha=0.5, linestyle=':')
ax8.set_title('Orthographic', fontsize=12)
myplot = ax8.contourf(lons, lats, fld, levels, transform=ccrs.PlateCarree(),
cmap=plt.cm.viridis, extend='both')

# add colorbar
plt.subplots_adjust(left=0.05, bottom=-0.02, right=0.95, top=0.975)
cbaxes = fig.add_axes([0.3, 0.05, 0.35, 0.02])
cbar = plt.colorbar(myplot, orientation='horizontal', cax = cbaxes, pad=0)
cbar.set_label('sea surface temperature [C]', rotation=0, fontsize=14)
cbar.ax.tick_params(labelsize=5, length=0)

#plt.tight_layout()  # Automatically adjusts subplot layout to prevent overlap

# Save the figure to a file
# Save the plot as a JPEG file
filename='p10_01.various_projection_cartopy.jpg'
plt.savefig(filename)

# Show the figure
plt.show()
