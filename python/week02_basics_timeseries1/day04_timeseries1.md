## Exercise: Inspect and read a climate data file

In this exercise, we will inspect a NOAA global ocean temperature anomaly dataset and read it using `pandas`.

The data file is located in the project `data` directory:

```text
../../data/NOAA.1850-2025.OCN.csv
```

Open the file and look at its structure before reading it in Python.

### Data structure

The file has a short metadata header followed by the actual tabular data.

```text
# Title: Global Ocean January - December Average Temperature Anomalies
# Units: Degrees Celsius
# Base Period: 1901-2000
Year,Anomaly
1850,0
1851,0.06
1852,0.08
...
```

The first three lines start with `#`. These lines are metadata, not data values. They describe the dataset title, units, and base period. The tabular data begin with the column names:

```text
Year,Anomaly
```

The two columns are:

- `Year`: calendar year
- `Anomaly`: global ocean temperature anomaly in degrees Celsius, relative to the 1901–2000 base period

Run the sample script:

```bash
python w02_07_read-data.sample.py
```

This script reads the CSV file and prints basic information about the data, including column names, data types, dimensions, and a summary of the DataFrame.

A robust way to read this file is:

```python
from pathlib import Path
import pandas as pd

file_path = Path('../../data/NOAA.1850-2025.OCN.csv')

data = pd.read_csv(file_path, comment='#')

print(data.head())
print(data.dtypes)
print(data.shape)
print(data.columns)
print(data.info())
```

The option `comment='#'` tells `pandas` to ignore metadata lines beginning with `#`.

---

## Exercise: Make an x-y plot of the ocean temperature anomaly

In this exercise, we will make a time-series plot of the NOAA global ocean temperature anomaly data.

Run the sample script:

```bash
python w02_08_xy-plot.sample.py
```

The script should:

1. read `NOAA.1850-2025.OCN.csv` from the `data` directory,
2. plot `Year` on the x-axis and `Anomaly` on the y-axis,
3. save the figure as a JPEG file with the same base name as the Python script.

A recommended version is:

```python
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

file_path = Path('../../data/NOAA.1850-2025.OCN.csv')

data = pd.read_csv(file_path, comment='#')

plt.figure(figsize=(10, 5))
plt.plot(data['Year'], data['Anomaly'], marker='o', linestyle='-')

plt.title('Global Ocean Temperature Anomalies')
plt.xlabel('Year')
plt.ylabel('Temperature Anomaly (°C)')
plt.grid(True)

output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, format='jpeg', dpi=300)

plt.show()
```

The command

```python
Path(__file__).with_suffix('.jpg')
```

creates an output filename using the same name as the Python script, but with the extension changed from `.py` to `.jpg`.

For example:

```text
w02_08_xy-plot.sample.py  ->  w02_08_xy-plot.sample.jpg
```

### Open the saved JPEG file

After running the script, open the JPEG file from the terminal.

On macOS:

```bash
open w02_08_xy-plot.sample.jpg
```

On Windows:

```cmd
start "" w02_08_xy-plot.sample.jpg
```

If using PowerShell on Windows, this also works:

```powershell
start .\w02_08_xy-plot.sample.jpg
```
