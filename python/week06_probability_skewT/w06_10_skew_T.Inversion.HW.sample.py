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
# Homework 6: Skew-T Diagram for an Inversion Day
# ---------------------------------------------------------
#
# Objective:
# Create a Skew-T diagram using radiosonde sounding data
# from Salt Lake City during a winter inversion event.
#
# Background:
# Temperature inversions commonly occur in northern Utah
# valleys during winter. Cold air becomes trapped near the
# surface beneath warmer air aloft, which can worsen air
# pollution and reduce visibility.
#
# Homework Tasks:
#
# Step 1:
# Read the sounding data from Salt Lake City.
#
# Step 2:
# Use the correct morning sounding time for
# January 29, 2024.
#
# Hint:
# Salt Lake City launches radiosondes at:
# 00 UTC and 12 UTC
#
# Mountain Standard Time (MST) is 7 hours behind UTC.
#
# Question:
# Which UTC time best represents the morning
# atmospheric conditions on January 29, 2024?
#
# Plot the following variables on the Skew-T diagram:
# - Temperature
# - Dew point temperature
# - Wind barbs
#
# Evaluate the lower atmosphere and identify whether
# a temperature inversion exists.
# - Where the inversion layer appears
# - How the inversion may contribute to poor air quality
#
# Expected Output:
# Save the Skew-T diagram as a JPEG image.
#
# Data Source:
# University of Wyoming Upper-Air Sounding Archive
# https://weather.uwyo.edu/upperair/sounding.shtml
#
# ---------------------------------------------------------
# Import required Python packages
# ---------------------------------------------------------

# Step 1 and 2: Add required information
# define date of interest, time, station ID and station name
# sid is the radiosonde station ID used to download
doi = datetime(, , , )
sid = ""
sname = ''

# read data into a Pandas dataframe
df = WyomingUpperAir.request_data(doi, sid)
print(df)

# remove duplicated pressure value rows to comply with monotonicity requirement
df.drop_duplicates(subset=['pressure'], inplace=True)

# extract variables from dataframe into unit-registered metpy variables
p = df['pressure'].to_numpy() * units(df.units['pressure']) # hPa
t = df['temperature'].to_numpy() * units(df.units['temperature']) # deg C
td = df['dewpoint'].to_numpy() * units(df.units['dewpoint']) # deg C
u = df['u_wind'].to_numpy() * units(df.units['u_wind']) # knots
v = df['v_wind'].to_numpy() * units(df.units['v_wind']) # knots


# ---- Create a skew-T diagram ----
# set up figure and axis adding skewt figure
fig = plt.figure(figsize=(3.98, 5.5))

# set up plot
skewt = mpplots.SkewT(fig)

# *** Step 2: Set `func_pltdat = True` **after** checking the JPEG file to plot the Skew-T baseline.
func_pltdat = True

if func_pltdat:
   # plot atmospheric data
   skewt.plot(p, t, 'tab:red', linewidth=1, label='Temperature')
   skewt.plot(p, td, 'tab:blue', linewidth=1, label='Dew Point')


# *** Step 3: Set `func_addinfo = True` **after** checking T and DWT plot
func_addinfo = True

if func_addinfo:

   # The LCL (Lifting Condensation Level): the height at which rising air 
   # becomes saturated and cloud formation begins.
   lcl_pressure, lcl_temperature = mpcalc.lcl(p[0], t[0], td[0])
   skewt.plot(lcl_pressure, lcl_temperature, color='black', marker='o',markersize=3, markerfacecolor='black',label='LCL')

   # The LFL (lifting condensation level): the height at which a rising air parcel cools to its dew point, becoming saturated and forming clouds.
   lfc_pressure, lfc_temperature = mpcalc.lfc(p, t, td)
   skewt.plot(lfc_pressure, lfc_temperature, color='gold', marker='o',markersize=3, markerfacecolor='gold', zorder=3, label='LFL')

   # The Equilibrium Level (EL): the altitude where a rising air parcel cools to the same temperature as its surroundings, causing it to stop rising further and indicating the top of cloud development.
   prof = mpcalc.parcel_profile(p, t[0], td[0])
   skewt.plot(p, prof, color='black', linewidth=0.5, label='Equilibrium Level')

   # CAPE: the amount of energy available for convection in the atmosphere, indicating the potential for the development of thunderstorms and strong updrafts.
   skewt.shade_cape(p, t, prof, color='lightcoral', alpha=0.4, label='CAPE')

   # Plot slanted line at constant T (0 degree C isotherm)
   skewt.ax.axvline(0, color='c', linestyle='-', linewidth=0.5, label='0°C Isotherm')

   # Add the relevant special lines
   t0 = np.arange(-50, 150, 10) * units.degree_Celsius
   skewt.plot_dry_adiabats(t0, color='red', linestyle='--', linewidth=0.5,label='Dry Adiabats')
   skewt.plot_moist_adiabats(linestyle='--', linewidth=0.5, label='Moist Adiabats')

   # plot wind barbs
   mask = p >= 100 * units.hectopascal
   interval = np.logspace(2, 3, num=50) * units.hPa
   idx = mpcalc.resample_nn_1d(p[mask], interval)
   skewt.plot_barbs(p[mask][idx], u[mask][idx], v[mask][idx], color='black',linewidth=0.75, length=5)

## format x-axes
skewt.ax.set_xlim(-40, 35)
skewt.ax.set_xlabel('Temperature [\u00B0C]', fontsize=7)
skewt.ax.tick_params(axis='x', which='major', labelsize=6)

# formt y-axis
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

