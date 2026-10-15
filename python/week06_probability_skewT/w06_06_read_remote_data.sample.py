from datetime import datetime
from siphon.simplewebservice.wyoming import WyomingUpperAir

# ---------------------------------------------------------
# Read upper-air sounding data from the University of Wyoming
# archive using the Siphon package.
#
# This example downloads a radiosonde observation
# for Salt Lake City (SLC) and stores the data
# in a Pandas DataFrame.
# 
# Data Source:
#   University of Wyoming Upper-Air Sounding Archive
#   https://weather.uwyo.edu/upperair/sounding.shtml
# ---------------------------------------------------------

# Define the date and time of the sounding observation
# Format: year, month, day, hour (UTC)
doi = datetime(2024, 8, 8, 0)

# Define station information
sid = "SLC"
sname = 'Salt Lake City UT (USA)'

# Request sounding data from the Wyoming archive
# and store it in a Pandas DataFrame
df = WyomingUpperAir.request_data(doi, sid)

# Display the first few rows of data
print(df)

# Display available column names
print(df.columns)
