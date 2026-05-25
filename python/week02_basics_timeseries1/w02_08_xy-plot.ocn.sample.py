from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Define the directory containing the climate dataset
data_dir = Path('../../data')

# Create the full file path for the NOAA ocean dataset
file_path = data_dir / 'NOAA.1850-2025.OCN.csv'

data = pd.read_csv(file_path, comment='#')

print(data.head())

plt.plot(data['Year'], data['Anomaly'], marker='o')

output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)

plt.show()

