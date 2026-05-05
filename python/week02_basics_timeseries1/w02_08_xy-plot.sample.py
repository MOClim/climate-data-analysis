from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

file_path = Path('../../data/NOAA.1850-2025.OCN.csv')

data = pd.read_csv(file_path, skiprows=4, names=['Year', 'Anomaly'])

print(data.head())

plt.plot(data['Year'], data['Anomaly'], marker='o')

output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)

plt.show()

