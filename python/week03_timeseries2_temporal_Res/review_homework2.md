# Homework 2 Review

This exercise updates `w02_08_xy-plot.ocn.sample.py` to create `w02_09_xy-plot.lnd.sample.py`.

The goal is to switch from NOAA ocean temperature anomalies to land temperature anomalies and improve the figure formatting.

---

# Main Changes

## 1. Update the Input Dataset

Original:

```python
file_path = Path('../../data/NOAA.1850-2025.OCN.csv')
```

Updated:

```python
file_path = Path('../../data_raw/NOAA.1850-2025.LND.csv')
```

Changes:

- `OCN` → `LND`
- `data` → `data_raw`

---

## 2. Keep the CSV Workflow

```python
data = pd.read_csv(file_path, comment='#')
```

This reads the CSV file and ignores metadata lines beginning with `#`.

---

## 3. Create the XY Plot

```python
plt.plot(data['Year'], data['Anomaly'], marker='o')
```

- x-axis: `Year`
- y-axis: `Anomaly`

---

## 4. Add Figure Labels

```python
plt.xlabel('Year')
plt.ylabel('Temperature Anomaly (°C)')
plt.title('Global Land Temperature Anomalies')
plt.grid(True)
```

These commands improve readability and scientific presentation.

---

## 5. Save the Figure

```python
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)
```

The figure is automatically saved as a JPG image.

---

# Learning Goals

Students learn how to:

- modify datasets and file paths
- improve scientific figure formatting
- save publication-quality graphics
