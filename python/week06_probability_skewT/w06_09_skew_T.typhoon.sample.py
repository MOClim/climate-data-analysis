from datetime import datetime
from siphon.simplewebservice.wyoming import WyomingUpperAir
from metpy.units import units
import matplotlib.pyplot as plt
import metpy.plots as mpplots
import metpy.calc as mpcalc
import numpy as np
import sys
from pathlib import Path

# ---------------------------------------------------------
# Exercise 4: Typhoon-Related Skew-T Analysis
#
# This exercise analyzes a typhoon-related atmospheric
# environment using radiosonde observations from
# Hachijojima, Japan.
#
# Student directions:
#
# Step 1. Set the station ID to:
#       47678  (Hachijojima, Japan)
#
#     Select the sounding date:
#       2024-08-14
#
#    Radiosonde archives use UTC time.
#    Japan Standard Time (JST) is UTC + 9 hours.
#
#    Example:
#       Aug 14 12 UTC
#       = Aug 14 evening in Japan
#
# Run the script and examine:
#       - temperature profile
#       - dewpoint profile
#       - CAPE region
#       - wind barbs
#       - LCL and LFC
#
# Compare the sounding structure with
#    typical tropical or typhoon environments.
# ---------------------------------------------------------


# Step 1: Define sounding date, time, and station ID information
doi = datetime(, , , )
sid = '' 
sname = ''

# Download sounding data into a Pandas DataFrame
df = WyomingUpperAir.request_data(doi, sid)
print(df)

# Remove duplicated pressure levels
#
# Some calculations require pressure values to be
# continuously decreasing with height.
#
df.drop_duplicates(subset=['pressure'], inplace=True)

#
# Extract atmospheric variables and attach units
#
p = df['pressure'].to_numpy() * units(df.units['pressure']) # hPa
t = df['temperature'].to_numpy() * units(df.units['temperature']) # deg C
td = df['dewpoint'].to_numpy() * units(df.units['dewpoint']) # deg C
u = df['u_wind'].to_numpy() * units(df.units['u_wind']) # knots
v = df['v_wind'].to_numpy() * units(df.units['v_wind']) # knots

# ---------------------------------------------------------
# Create a Skew-T figure
# ---------------------------------------------------------

fig = plt.figure(figsize=(3.98, 5.5))

# Create Skew-T plotting object
skewt = mpplots.SkewT(fig)


# Plot temperature and dew point profiles
func_pltdat = True

if func_pltdat:

   # Plot air temperature profile
   skewt.plot(p, t, 'tab:red',
              linewidth=1,
              label='Temperature')

   # Plot dew point temperature profile
   skewt.plot(p, td, 'tab:blue',
              linewidth=1,
              label='Dew Point')


# Add atmospheric stability information
func_addinfo = True

if func_addinfo:

   # LCL (Lifting Condensation Level): 
   # Height where rising air first becomes saturated
   lcl_pressure, lcl_temperature = mpcalc.lcl(p[0], t[0], td[0])

   skewt.plot(lcl_pressure, lcl_temperature, color='black', marker='o',markersize=3, markerfacecolor='black',label='LCL')

   # LFL (lifting condensation level): 
   # Height where the air parcel becomes buoyant
   lfc_pressure, lfc_temperature = mpcalc.lfc(p, t, td)

   skewt.plot(lfc_pressure, lfc_temperature, color='gold', marker='o',markersize=3, markerfacecolor='gold', zorder=3, label='LFL')

   # Equilibrium Level (EL): 
   # Calculate parcel ascent profile
   prof = mpcalc.parcel_profile(p, t[0], td[0])
   
   # Plot parcel ascent profile
   skewt.plot(p, prof, color='black', linewidth=0.5, label='Equilibrium Level')

   # Shade CAPE region
   skewt.shade_cape(p, t, prof, color='lightcoral', alpha=0.4, label='CAPE')

   # Plot 0°C isotherm
   skewt.ax.axvline(0, color='c', linestyle='-', linewidth=0.5, label='0°C Isotherm')

   # Add dry adiabatic reference lines
   t0 = np.arange(-50, 150, 10) * units.degree_Celsius

   skewt.plot_dry_adiabats(t0, color='red', linestyle='--', linewidth=0.5,label='Dry Adiabats')

   # Add moist adiabatic reference lines
   skewt.plot_moist_adiabats(linestyle='--', linewidth=0.5, label='Moist Adiabats')

   # plot wind barbs
   mask = p >= 100 * units.hectopascal

   interval = np.logspace(2, 3, num=50) * units.hPa

   idx = mpcalc.resample_nn_1d(p[mask], interval)

   skewt.plot_barbs(p[mask][idx], u[mask][idx], v[mask][idx], color='black',linewidth=0.75, length=5)

# Format x-axis
skewt.ax.set_xlim(-40, 35)
skewt.ax.set_xlabel('Temperature [\u00B0C]', fontsize=7)
skewt.ax.tick_params(axis='x', which='major', labelsize=6)

# Format y-axis
skewt.ax.set_ylim(p[0], 100)
skewt.ax.set_ylabel('Pressure [hPa]', fontsize=7)
skewt.ax.tick_params(axis='y', which='major', labelsize=6)

# add title
skewt.ax.set_title(f'{sid} {sname} {doi.strftime("%Y-%m-%d %H UTC")}', fontsize=8)

if func_pltdat:
   # Show the legend
   plt.legend(fontsize=6,loc='upper right', bbox_to_anchor=(0.9, 1))

# save plot
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)

plt.close()

