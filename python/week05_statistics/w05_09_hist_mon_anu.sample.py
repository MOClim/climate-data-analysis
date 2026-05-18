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
  for i, year in enumerate(years):
    # Extract the row data
    row_data = df.iloc[i, :].values
    
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

  # Filter the data for the years between 1950 and 2023
  filtered_df = final_df[(final_df.index >= '1950-01') & (final_df.index <= '2023-12')]

  return filtered_df

def pd_to_numpy(data):

  # Combine all monthly data into a single series
  single_series = data.values.flatten()
  # Remove NaN values
  np_dat_wonan = single_series[~np.isnan(single_series)]
  
  return np_dat_wonan

### Read Main ###

# Step 1: Read the CSV data
indir = '../data/'

filename = indir + 'temperatureReport-report-1727300365.csv'
df_temp = read_pddata(filename,2)

filename = indir + 'precipReport-report-1719460525.csv'
df_prc = read_pddata(filename,0)

# Resample the data to annual frequency and calculate the mean for temperature
# Resample the data to annual frequency and calculate the sum for precipitation
annual_avg_temp = df_temp.resample('Y').mean()
annual_sum_prc = df_prc.resample('Y').sum()

# convert panda monthly and annual data to numpy
monthly_temp = pd_to_numpy(df_temp)
annual_temp = pd_to_numpy(annual_avg_temp)
monthly_prc = pd_to_numpy(df_prc)
annual_prc = pd_to_numpy(annual_sum_prc)

# Step 4: Create and plot the histogram
plt.figure(figsize=(12, 6))

# *** Create four histograms for the following data:
# Choose appropriate bin sizes to ensure that 
# the histograms effectively represent the data.
# Monthly Temperature
# Annual Temperature
# Monthly Precipitation
# Annual Precipitation

plt.subplot(2, 2, 1)

plt.subplot(2, 2, 3)

plt.subplot(2, 2, 2)

plt.subplot(2, 2, 4)

# Add the main title to the figure
plt.suptitle('USU from 1950 to 2023', fontsize=16)

# Adjust the spacing between the plots
plt.subplots_adjust(hspace=0.5)  # Increase this value to add more space vertically


# Save the plot as a JPEG file
filename='p10_05.hist_mon_anu.jpg'
plt.savefig(filename, format='jpeg', dpi=300)

plt.show()

