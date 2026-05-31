from datetime import datetime
from siphon.simplewebservice.wyoming import WyomingUpperAir
from metpy.units import units
import matplotlib.pyplot as plt
import metpy.plots as mpplots
import metpy.calc as mpcalc
import numpy as np
import pandas as pd
import sys
from pathlib import Path

# ---------------------------------------------------------
# Exercise: Create a Skew-T Diagram Using Radiosonde Data
#
# In this exercise, students will:
#   - Download upper-air sounding data from the
#     University of Wyoming archive
#   - Extract atmospheric variables such as
#     temperature, dew point, and wind
#   - Create a Skew-T diagram using MetPy
#   - Add atmospheric stability information such as
#     LCL, LFC, CAPE, and adiabatic lines
#
# Data Source:
#   University of Wyoming Upper-Air Sounding Archive
#   https://weather.uwyo.edu/upperair/sounding.shtml
#
#   Use this website to find station IDs and sounding data.
#
# Student Tasks:
#   Steps 1 & 2:
#      Run the program and inspect the downloaded data.
#      After checking the data, comment out sys.exit().
#
#   Step 3:
#      Enable plotting of temperature and dew point
#      profiles by setting:
#         func_pltdat = True
#
#   Step 4:
#      Add atmospheric analysis information by setting:
#         func_addinfo = True
#
# Suggested Exploration:
#   - Change the observation date (`doi`)
#   - Change the station ID (`sid`)
#   - Compare atmospheric stability under different
#     weather conditions
# ---------------------------------------------------------

# Define date and time of the sounding observation
# Format: year, month, day, hour (UTC)
doi = datetime(2025, 10, 10, 0)

# Define station ID and station name
sid = "SLC"
sname = 'Salt Lake City UT (USA)'


# ---------------------------------------------------------
# Read radiosonde sounding data into a Pandas DataFrame
# ---------------------------------------------------------
df = WyomingUpperAir.request_data(doi, sid)

## or read downloaded data
#filename = Path('../../data/2025101000-72572.csv')
#df = pd.read_csv(filename)

print(df)

# ---------------------------------------------------------
# Step 1:
# Display downloaded data
# ---------------------------------------------------------
sys.exit()

# ---------------------------------------------------------
# Remove duplicated pressure rows
#
# MetPy calculations require pressure values to be
# monotonic (continuously decreasing with height).
# ---------------------------------------------------------
df.drop_duplicates(subset=['pressure'], inplace=True)

# ---------------------------------------------------------
# Extract atmospheric variables and attach units
#
# Units are required for MetPy meteorological calculations.
# ---------------------------------------------------------
p = df['pressure'].to_numpy() * units(df.units['pressure'])       # hPa
t = df['temperature'].to_numpy() * units(df.units['temperature']) # deg C
td = df['dewpoint'].to_numpy() * units(df.units['dewpoint'])      # deg C
u = df['u_wind'].to_numpy() * units(df.units['u_wind'])           # knots
v = df['v_wind'].to_numpy() * units(df.units['v_wind'])           # knots

# ---------------------------------------------------------
# Step 2:
# Check the downloaded data first.
#
# After confirming the data looks correct,
# comment out the line below.
# ---------------------------------------------------------
sys.exit()

# ---------------------------------------------------------
# Create a Skew-T figure
# ---------------------------------------------------------
fig = plt.figure(figsize=(3.98, 5.5))

# Create Skew-T plotting object
skewt = mpplots.SkewT(fig)

# ---------------------------------------------------------
# Step 3:
# Set to True after checking the baseline plot
# ---------------------------------------------------------
func_pltdat = False

if func_pltdat:

   # Plot temperature profile
   skewt.plot(p, t, 'tab:red', linewidth=1,
              label='Temperature')

   # Plot dew point profile
   skewt.plot(p, td, 'tab:blue', linewidth=1,
              label='Dew Point')

# ---------------------------------------------------------
# Step 4:
# Add atmospheric stability analysis information
# ---------------------------------------------------------
func_addinfo = False

if func_addinfo:

   # ------------------------------------------------------
   # LCL:
   # Height where rising air first becomes saturated
   # ------------------------------------------------------
   lcl_pressure, lcl_temperature = mpcalc.lcl(
       p[0], t[0], td[0]
   )

   skewt.plot(
       lcl_pressure,
       lcl_temperature,
       color='black',
       marker='o',
       markersize=3,
       markerfacecolor='black',
       label='LCL'
   )

   # ------------------------------------------------------
   # LFC:
   # Height where air parcel becomes positively buoyant
   # ------------------------------------------------------
   lfc_pressure, lfc_temperature = mpcalc.lfc(p, t, td)

   skewt.plot(
       lfc_pressure,
       lfc_temperature,
       color='gold',
       marker='o',
       markersize=3,
       markerfacecolor='gold',
       zorder=3,
       label='LFC'
   )

   # ------------------------------------------------------
   # Parcel ascent profile
   # ------------------------------------------------------
   prof = mpcalc.parcel_profile(p, t[0], td[0])

   skewt.plot(
       p,
       prof,
       color='black',
       linewidth=0.5,
       label='Parcel Profile'
   )

   # ------------------------------------------------------
   # CAPE shading
   #
   # Indicates atmospheric instability and potential
   # thunderstorm development.
   # ------------------------------------------------------
   skewt.shade_cape(
       p, t, prof,
       color='lightcoral',
       alpha=0.4,
       label='CAPE'
   )

   # ------------------------------------------------------
   # Plot 0°C isotherm
   # ------------------------------------------------------
   skewt.ax.axvline(
       0,
       color='c',
       linestyle='-',
       linewidth=0.5,
       label='0°C Isotherm'
   )

   # ------------------------------------------------------
   # Add dry and moist adiabatic reference lines
   # ------------------------------------------------------
   t0 = np.arange(-50, 150, 10) * units.degree_Celsius

   skewt.plot_dry_adiabats(
       t0,
       color='red',
       linestyle='--',
       linewidth=0.5,
       label='Dry Adiabats'
   )

   skewt.plot_moist_adiabats(
       linestyle='--',
       linewidth=0.5,
       label='Moist Adiabats'
   )

   # ------------------------------------------------------
   # Plot wind barbs
   # ------------------------------------------------------
   mask = p >= 100 * units.hectopascal

   interval = np.logspace(2, 3, num=50) * units.hPa

   idx = mpcalc.resample_nn_1d(
       p[mask], interval
   )

   skewt.plot_barbs(
       p[mask][idx],
       u[mask][idx],
       v[mask][idx],
       color='black',
       linewidth=0.75,
       length=5
   )

# ---------------------------------------------------------
# Format x-axis
# ---------------------------------------------------------
skewt.ax.set_xlim(-40, 35)
skewt.ax.set_xlabel('Temperature [°C]', fontsize=7)
skewt.ax.tick_params(axis='x', which='major', labelsize=6)

# ---------------------------------------------------------
# Format y-axis
# ---------------------------------------------------------
skewt.ax.set_ylim(p[0], 100)
skewt.ax.set_ylabel('Pressure [hPa]', fontsize=7)
skewt.ax.tick_params(axis='y', which='major', labelsize=6)

# ---------------------------------------------------------
# Add figure title
# ---------------------------------------------------------
skewt.ax.set_title(
    f'{sid} {sname} {doi.strftime("%Y-%m-%d %H UTC")}',
    fontsize=8
)

# Display legend
if func_pltdat:
   plt.legend(fontsize=6,
              loc='upper right',
              bbox_to_anchor=(0.9, 1))

# ---------------------------------------------------------
# Save figure as JPEG
# ---------------------------------------------------------
output_path = Path(__file__).with_suffix('.jpg')

plt.savefig(output_path, dpi=300)

plt.close()
