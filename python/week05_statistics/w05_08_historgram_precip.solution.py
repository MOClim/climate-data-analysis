import netCDF4 as nc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys

def read_pddata(filename,ihead):

  # Read the CSV, skipping metadata and setting missing values
  data = pd.read_csv(filename, skiprows=ihead, na_values='-')

  # Read only the columns from 1 to 12 (January to December)
  df_subset = data.iloc[:-1, 1:13]  # Selecting columns 1 through 12 (index 1 to 12 in Python's 0-indexed system)
  years = data.iloc[:-1,0]

  df = pd.DataFrame(df_subset)
  # Assign years to each row, assuming the first year is 1893
  #start_year = 1893
  #years = list(range(start_year, start_year + len(df)))

  # Initialize an empty DataFrame to collect the time series data
  final_df = pd.DataFrame()

  # Define the months in the correct order
  months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sept", "Oct", "Nov", "Dec"]

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

  # Format the index to display only year and month
  # Convert the index to DatetimeIndex
  final_df.index = pd.to_datetime(final_df.index, format='%Y-%m')

  # Filter the data for the years between 1950 and 2023
  filtered_df = final_df[(final_df.index >= '1950-01') & (final_df.index <= '2023-12')]

  return filtered_df

def pd_to_numpy(df):

  data = df
  # Remove the last row (Average row)
  data = data.drop(data.index[-1])

  # Replace "-" strings with np.nan
  data.replace("-", np.nan, inplace=True)

  # Combine all monthly data into a single series
  single_series = data.values.flatten()
  # Remove NaN values
  np_dat_wonan = single_series[~np.isnan(single_series)]
  
  return np_dat_wonan

### Read Main ###

# Step 1: Read the CSV data
indir = '../data/'
filename = indir + 'precipReport-report-1719460525.csv'

df = read_pddata(filename,0)
monthly_data = pd_to_numpy(df)


# Step 4: Create and plot the histogram
plt.figure(figsize=(10, 6))
plt.hist(monthly_data, bins=100, color='blue', edgecolor='black')
plt.title('Histogram of Precipitation at USU from 1950 to 2023')
plt.xlabel('Precipitation (mm)')
plt.ylabel('Frequency (months)')
plt.grid(True)

# Save the plot as a JPEG file
filename='p10_04.precip_hist.jpg'
plt.savefig(filename, format='jpeg', dpi=300)

plt.show()

