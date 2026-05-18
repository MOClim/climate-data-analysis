import netCDF4 as nc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys

def read_pddata(filename,ihead):

  # Read the CSV, skipping metadata and setting missing values
  data = pd.read_csv(filename, skiprows=ihead, na_values='-')

  # Read only the columns from 1 to 12 (January to December)
  df = pd.DataFrame(data.iloc[:-1, 1:13])  # Selecting columns 1 through 12 (index 1 to 12 in Python's 0-indexed system)
  years = data.iloc[:-1,0]

  # Define the months in the correct order
  months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sept", "Oct", "Nov", "Dec"]

  # Initialize an empty DataFrame to collect the time series data
  final_df = pd.DataFrame()
  # Loop through each year and corresponding row of data
  for idx, year in enumerate(years):
     # Extract the row data
     row_data = df.iloc[idx, :].values
    
     # Create a DataFrame for this year with month, value, and datetime
     temp_df = pd.DataFrame({
        'Month': months,
        'Value': row_data
     })
     # Correct the month abbreviation for "Sept"
     temp_df['Month'] = temp_df['Month'].replace('Sept', 'Sep')
    
     # Create the date column by combining the year and month
     temp_df['Date'] = pd.to_datetime(temp_df['Month'] + f"-{year}", format="%b-%Y")
 
     # Set the Date as index
     temp_df.set_index('Date', inplace=True)
 
     # Append to the final DataFrame
     final_df = pd.concat([final_df, temp_df[['Value']]])


  print(final_df)

  # Filter the data for the years between 1950 and 2023
  filtered_df = final_df[(final_df.index >= '1950-01') & (final_df.index <= '2023-12')]

  return filtered_df


### Read Main ###

# Step 1: Read the CSV data
indir = '../data/'
filename = indir + 'temperatureReport-report-1727300365.csv'

df = read_pddata(filename,2)


# Step 2: Convert Pandas into NumPy with any invalid data (like missing values) removed.

# Combine all monthly data into a single series (.floatten())
single_series = df.values.flatten()

# Remove NaN values 
all_data = single_series[~np.isnan(single_series)]

# ---- Plotting ----
# Step 3: Create and plot the histogram
plt.figure(figsize=(10, 6))
plt.hist(all_data, bins=100, color='orange', edgecolor='black')
plt.title('Histogram of Temperature at USU from 1950 to 2023')
plt.xlabel('Temperature (C)')
plt.ylabel('Frequency (months)')
plt.grid(True)

# Save the plot as a JPEG file
filename='p10_03.temp_hist.jpg'
plt.savefig(filename, format='jpeg', dpi=300)

plt.show()

