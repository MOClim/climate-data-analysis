# Homework Review: Homework2 – Python Land Data

## Environment Setup
```bash
git pull origin main
git status
```
You can find the file in `solution` directory.
```bash
ls solution/w02_09_xy-plot.lnd.sample.py
```

This example demonstrates how to update the ocean temperature anomaly plotting example (`w02_08_xy-plot.ocn.sample.py`) to visualize global land temperature anomalies.

---

## Overview

The original script (`w02_08`) reads NOAA ocean temperature anomaly data and generates a simple XY plot.  
The updated script (`w02_09`) modifies the workflow to use land temperature anomaly data and improves the figure presentation with labels, titles, and grid lines.

Source files:

- `w02_08_xy-plot.ocn.sample.py`
- `solution/w02_09_xy-plot.lnd.sample.py`

---

## Main Updates

### 1. Update the Input Dataset

The original script reads the ocean temperature anomaly dataset:

```python
file_path = Path('../../data/NOAA.1850-2025.OCN.csv')
```

---

# Step-by-Step Explanation

## Step 1. Update the Dataset

The original script reads ocean temperature anomalies:

```python
file_path = Path('../../data/NOAA.1850-2025.OCN.csv')
```

The updated script reads land temperature anomalies:

```python
file_path = Path('../../data_raw/NOAA.1850-2025.LND.csv')
```

### Changes

| Original | Updated |
|---|---|
| `OCN` | `LND` |
| `data` | `data_raw` |

This modification changes the input dataset while preserving the rest of the workflow.

---

## Step 2. Read the CSV File

The pandas workflow remains unchanged:

```python
data = pd.read_csv(file_path, comment='#')
```

### Explanation

- `pd.read_csv()` reads tabular data from a CSV file
- `comment='#'` ignores metadata lines beginning with `#`
- the dataset is stored in a pandas DataFrame named `data`

---

## Step 3. Inspect the Dataset

The script prints the first few rows:

```python
print(data.head())
```
### Purpose

This helps verify:

- column names
- numerical values
- successful file loading

Typical columns include:

| Column | Description |
|---|---|
| `Year` | Observation year |
| `Anomaly` | Temperature anomaly (°C) |

---

# Step 4. Generate the XY Plot

The plotting command remains unchanged:

```python
plt.plot(data['Year'], data['Anomaly'], marker='o')
```

### Explanation

| Component | Purpose |
|---|---|
| `data['Year']` | x-axis values |
| `data['Anomaly']` | y-axis values |
| `marker='o'` | draw circular markers |

This creates a climate time-series visualization.

---

# Step 5. Add Figure Annotation

The updated script improves readability using axis labels and titles.

```python
plt.xlabel('Year')
plt.ylabel('Temperature Anomaly (°C)')
plt.title('Global Land Temperature Anomalies')
plt.grid(True)
```

### Purpose of Each Command

| Command | Purpose |
|---|---|
| `xlabel()` | label x-axis |
| `ylabel()` | label y-axis |
| `title()` | add figure title |
| `grid(True)` | display grid lines |

These additions improve scientific presentation quality.

---

The figure is automatically exported as a JPG image:

```python
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)
```
