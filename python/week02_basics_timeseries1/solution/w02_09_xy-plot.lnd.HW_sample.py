from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# File paths for both datasets. Add data name for each path.
# Get the directory where this script is located
script_dir = Path(__file__).resolve().parent

# If the script is inside the "solution" folder,
# move up one additional directory level
if script_dir.name == "solution":
    repo_dir = script_dir.parents[2]
else:
    repo_dir = script_dir.parents[1]

# Create the path to the data directory
# using an absolute path based on the repository location
data_dir = repo_dir / "data_raw"

file_path = data_dir / 'NOAA.1850-2025.LND.csv'

data = pd.read_csv(file_path, comment='#')

print(data.head())

plt.plot(data['Year'], data['Anomaly'], marker='o')

plt.xlabel('Year')
plt.ylabel('Temperature Anomaly (°C)')
plt.title('Global Land Temperature Anomalies')
plt.grid(True)

output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)

plt.show()

