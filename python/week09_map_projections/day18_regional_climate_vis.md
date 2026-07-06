# Day 18: Regional Climate Visualization

## Overview

In this lesson, you will learn how to create effective regional climate maps using Cartopy. Unlike global maps, regional maps require careful selection of the map projection, map extent, visualization settings, and geographic features. You will compare different regional domains, enhance maps with geographic features, and evaluate how visualization choices influence the interpretation of climate data.

---

## Learning Objectives

By the end of this lesson, you will be able to:

- Create regional climate maps using Lambert Conformal and Robinson projections.
- Customize the projection center and map extent for different regions.
- Add geographic features such as coastlines, borders, rivers, lakes, and gridlines.
- Compare visualization choices including colormaps and contour intervals.
- Design a regional climate map that effectively communicates scientific information.

---
## Key Concepts
- Regional map projections
- Lambert Conformal projection
- Robinson projection
- Map extent (`ax.set_extent()`)
- Geographic map features
- Colormaps (`cmap`)
- Contour levels (`levels`)
- Effective climate-map design

---
### Exercise 1: Lambert Conformal Projection

Create a regional air temperature anomaly map centered over North America.
```bash
python w09_06_Lambert_airT_anomaly.py
```

Topics
- Lambert Conformal projection
- Regional map extent
- North America visualization

```python
ax = plt.axes(
    projection=ccrs.LambertConformal(
        central_longitude=-100,
        central_latitude=45
    )
)
```

---
### Exercise 2: Customize a Regional Map

Modify the projection center, color range, and map extent to create a regional map over another mid-latitude region.
```bash
python w09_07_Lambert_USA.solution.py
```

Try changing
- `central_longitude`
- `central_latitude`
- `ax.set_extent()`
- `clevs`

**Setup the map range** 
```python
ax = plt.axes(
    projection=ccrs.LambertConformal(
        central_longitude=,
        central_latitude=
    )
)
```
```python
ax.set_extent(
    [, , , ],
    crs=ccrs.PlateCarree())
```

---
### Exercise 3. Regional Projection Examples

Create Lambert Conformal maps for another region. 
```bash
cp w09_07_Lambert_USA.py w09_08_Lambert_regions.py
```

Suggested regions
- Europe
- East Asia
- Australia

Compare how changing the projection center affects the final map.

---
### Exercise 4. Improve Map Readability

Enhance a regional climate map by adding geographic features.
```bash
python w09_09_Lambert_features.py
```

Experiment with
- Coastlines
- Borders
- Lakes
- Rivers
- Land and ocean shading
- Gridlines

Discuss which features improve readability without making the map too crowded.

```python
# These features provide geographic context for interpreting
# regional climate anomalies.
ax.add_feature(cfeature.LAND, facecolor="lightgray", zorder=0)
ax.add_feature(cfeature.OCEAN, facecolor="white", zorder=0)
ax.add_feature(cfeature.LAKES, facecolor="white", edgecolor="gray", linewidth=0.4)
ax.add_feature(cfeature.RIVERS, edgecolor="gray", linewidth=0.4)

# Political and coastline boundaries
ax.coastlines(linewidth=0.7)
ax.add_feature(cfeature.BORDERS, linewidth=0.5)
ax.add_feature(cfeature.STATES, linewidth=0.3)
```

---
### Exercise 5: Lambert Precipitation Projection with Map Features

```bash
cp w09_09_Lambert_features.py w09_10_Lambert_features_precip.py
```

#### Directions
- Replace the air-temperature dataset with the precipitation dataset.
- Calculate the January 2026 precipitation anomaly.
- Use a precipitation colormap (e.g., `BrBG`).
- Adjust the contour levels to improve the map.
  
---
### Exercise 6: Compare Visualization Choices

Visualization choices can greatly influence how climate anomalies are interpreted.
```bash
python w09_11_visualization_compare.py
```

Compare
- different colormaps
- different contour intervals
- different color ranges

Discuss
- Which figure is easiest to interpret?
- Which color range emphasizes regional anomalies?
- Which figure would be suitable for a scientific publication?

---
## Homework 8: Regional Climate Visualization

Create a regional precipitation anomaly map for one region of your choice.
```bash
cp w09_10_Lambert_features_precip.py w09_12_regional_features_precip.HW.py
```

### Choose one region
- North America
- South America
- Europe
- Africa
- East Asia
- Australia

### Requirements
- Read the precipitation NetCDF dataset.
- Compute the January 2026 precipitation anomaly.
- Select an appropriate projection.
    - `Lambert` Conformal for mid-latitude regions.
    - `Robinson` for regions crossing the equator (e.g., Africa).
- Select an appropriate map extent.
- Add at least three geographic features.
- Choose a suitable colormap and contour interval.
- Include a descriptive title and colorbar.

### Deliverables

Submit
- Python program
- Output figure (PNG or JPG)
  
---
## Key Takeaways
- Regional maps require an appropriate map projection and extent.
- Geographic features improve the readability of climate maps.
- Visualization choices such as colormaps and contour levels influence scientific interpretation.
- Different regions may require different map projections to minimize distortion.
