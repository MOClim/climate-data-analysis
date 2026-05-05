import pandas as pd
import sys
from pathlib import Path

# --- Read Data ---

# Replace 'path_to_file.csv' with the actual path to your CSV file
file_path = Path('../../data/NOAA.1850-2025.OCN.csv')

# Read the CSV file
data = pd.read_csv(file_path, skiprows=4)

# Data information
print("")
print("data column information: ")
print(data.dtypes)
print("")
print("data dimension information: ")
print(data.shape)
print("")
print("data column information: ")
print(data.columns)
print("")
print("data all information: ")
print(data.info())
print("")

