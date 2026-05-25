# ==========================================================
# Example: Linear Trend Analysis and Detrending
#
# This script demonstrates how to:
# 1. Calculate a linear trend using regression
# 2. Create a trend line
# 3. Remove the trend from a dataset (detrending)
# 4. Visualize the original and detrended data
#
# Detrending is commonly used in climate and
# geoscience studies to isolate variability after
# removing long-term changes.
# ==========================================================

import numpy as np
import matplotlib.pyplot as plt  # Import matplotlib for plotting
from scipy.stats import linregress
from pathlib import Path

# Function to calculate a linear trend and detrended data
def cal_regression(years, data):

    # Fit a linear trend to the data
    slope, intercept, r_value, p_value, std_err = linregress(years, data)

    # Calculate the linear trend line
    trend = slope * years + intercept

    # Remove the trend from the original data
    dtrd_data = data - trend

    return dtrd_data, trend, slope

# ----------------------------------------------------------
# Example dataset:
# Annual temperature anomaly values
# ----------------------------------------------------------

years = np.array([2000, 2001, 2002, 2003, 2004, 2005])
data = np.array([0.2, 0.25, 0.45, 0.55, 0.58, 0.7])

# Calculate trend and detrended data
detrended_data, trend, slope = cal_regression(years, data)

# Print the results
print("Original Data:", data)
print("Trend Line:", trend)
print("Detrended Data:", detrended_data)
print("Slope of the Trend:", slope)

# ----- Plotting the results -----

# Create a figure and axis objects
plt.figure(figsize=(10, 5))

# Plot Original Data and Trend Line
plt.subplot(1, 2, 1)  # Create subplot 1: Original data and trend
plt.plot(years, data, 'o', label='Original Data', color='red')
plt.plot(years, trend, '--', label='Trend Line (Linear Fit)', color='blue')
plt.xlabel('Year')
plt.ylabel('Data Value')
plt.title('Original Data with Trend Line')
plt.legend()
plt.grid(True)

# Plot Detrended Data
plt.subplot(1, 2, 2)  # Create subplot 2: Detrended data
plt.plot(years, detrended_data, 'o-', label='Detrended Data', color='green')
plt.axhline(y=0, color='gray', linestyle='--')  # Add a horizontal line at y=0
plt.xlabel('Year')
plt.ylabel('Detrended Value')
plt.title('Detrended Data')
plt.legend()
plt.grid(True)

# Adjust layout and display the plots
plt.tight_layout()

# Save the plot as a JPEG file
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)

plt.show()


