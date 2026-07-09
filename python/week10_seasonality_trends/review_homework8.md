# Homework 8 Review — Regional Climate Visualization

This review summarizes one possible solution for Homework 9. The objective was to calculate the **January 2026 precipitation anomaly** relative to the **1991–2020 January climatology** and visualize the anomaly on a regional map using an appropriate Cartopy projection. The sample solution demonstrates one implementation for **Africa** using the Robinson projection.

---

## Example Output

The figure below shows the January 2026 precipitation anomaly over Africa.

Positive anomalies (green) indicate wetter-than-normal conditions, while negative anomalies (brown) indicate drier-than-normal conditions. Geographic features such as coastlines, borders, rivers, lakes, and gridlines provide geographic context that improves interpretation of regional climate patterns.

---

## Key Steps

### 1. Read the precipitation dataset

Load the monthly precipitation reanalysis dataset.

```python
ds = xr.open_dataset(prate_file)
prate = ds["prate"]
```

---

### 2. Convert precipitation units

The dataset stores precipitation in **kg m⁻² s⁻¹**, which is equivalent to **mm s⁻¹**. Convert the data to **mm day⁻¹** for easier interpretation.

```python
prate = prate * 86400
```

---

### 3. Calculate the January climatology

Compute the January climatology using the 1991–2020 reference period.

```python
ref = prate.sel(time=slice("1991-01-01", "2020-12-31"))

jan_clim = (
    ref.groupby("time.month")
       .mean("time")
       .sel(month=1)
)
```

The climatology represents the average January precipitation over the reference period.

---

### 4. Compute the January 2026 anomaly

Subtract the climatological January mean from the January 2026 precipitation.

```python
jan_2026 = prate.sel(time="2026-01-01").squeeze()

anom = jan_2026 - jan_clim
```

Positive values indicate wetter-than-normal conditions, while negative values indicate drier-than-normal conditions.

---

### 5. Create a regional map

Choose a projection appropriate for the selected region.

For Africa, the Robinson projection provides a balanced view because the continent spans both hemispheres.

```python
ax = plt.axes(
    projection=ccrs.Robinson(
        central_longitude=20
    )
)

ax.set_extent(
    [-30, 65, -50, 45],
    crs=ccrs.PlateCarree()
)
```

---

### 6. Add geographic features

Geographic features improve the readability of regional climate maps.

```python
ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.OCEAN)
ax.add_feature(cfeature.LAKES)
ax.add_feature(cfeature.RIVERS)

ax.coastlines()
ax.add_feature(cfeature.BORDERS)
```

Latitude–longitude gridlines also help relate anomaly patterns to geographic locations.

---

### 7. Plot the precipitation anomaly

Use a diverging colormap because precipitation anomalies contain both positive and negative values.

```python
clevs = np.arange(-5, 5.1, 0.5)

anom.plot(
    cmap="BrBG",
    levels=clevs,
    extend="both"
)
```

A labeled colorbar communicates the magnitude of the anomaly in **mm day⁻¹**.
