from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

file_path = Path('../../data_raw/NOAA.1850-2025.LND.csv')

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

