# Day 23: Polar Projection Maps

## Learning Objectives

By the end of this lesson, you will be able to:

* Create polar stereographic maps using Cartopy.
* Display climate fields using contour and filled-contour plots.
* Create separate polar projections for the Northern and Southern Hemispheres.
* Compare seasonal atmospheric circulation patterns between DJF and JJA.
* Calculate and visualize long-term SST trends in the polar regions.

---

## Introduction

Polar regions are important components of the climate system and are experiencing substantial environmental changes. However, standard latitude-longitude map projections can strongly distort spatial patterns at high latitudes.

Polar stereographic projections provide a useful way to visualize climate fields around the North and South Poles.

In this lesson, you will use Cartopy to create polar projection maps of sea level pressure (SLP) and sea surface temperature (SST). You will first examine climatological atmospheric circulation patterns and then apply the same mapping techniques to investigate long-term SST trends in the polar oceans.

---

### Exercise 1: Northern Hemisphere Polar Projection

Create a Northern Hemisphere polar stereographic map of DJF mean sea level pressure.

```bash
python w12_01_contour_polar_map.py
```

Concepts:

* DJF seasonal means
* North Polar Stereographic projection
* Circular polar map boundaries
* Contour plots
* Cyclic longitude points
* Polar latitude gridlines

The North Polar Stereographic projection is created using:

```python
projection = ccrs.NorthPolarStereo()
```

The geographic extent determines how far the map extends from the pole:

```python
ax.set_extent(
    [-180, 180, 20, 90],
    crs=ccrs.PlateCarree()
)
```

In this example, the map displays the Northern Hemisphere from 20°N to the North Pole.

---

### Exercise 2: Filled Polar Projection

Add filled contours to the Northern Hemisphere DJF sea level pressure map.

```bash
python w12_02_fill_polar_map.py
```

Concepts:

* `contourf()` for filled climate fields
* `contour()` for contour lines
* Contour labels
* Colorbars
* Combining filled contours and contour lines

Filled contours provide a clearer visualization of the spatial structure of sea level pressure while contour lines retain quantitative information about pressure values.

---

### Exercise 3: Northern and Southern Hemisphere Polar Projections

Create separate polar stereographic maps for the Northern and Southern Hemispheres.

```bash
python w12_03_two_hemispheres.py
```

Concepts:

* `NorthPolarStereo()`
* `SouthPolarStereo()`
* Multiple map projections in one figure
* Shared contour levels and colorbars
* Hemispheric comparison of DJF sea level pressure

The two projections are created separately:

```python
ax_nh = fig.add_subplot(
    1, 2, 1,
    projection=ccrs.NorthPolarStereo()
)

ax_sh = fig.add_subplot(
    1, 2, 2,
    projection=ccrs.SouthPolarStereo()
)
```

Using the same contour levels and color scale allows direct comparison of sea level pressure patterns between the two hemispheres.

---

### Exercise 4: Compare DJF and JJA Sea Level Pressure

Copy the previous program and modify it to calculate and display **JJA mean sea level pressure** instead of DJF.

```bash
cp w12_03_two_hemispheres.py w12_04_JJA_two_hemispheres.py
```

Then edit:

```bash
w12_04_JJA_two_hemispheres.py
```

Tasks:

* Change the seasonal mean from DJF to JJA.
* Determine the appropriate `end_month` for the June-July-August seasonal mean.
* Rename the seasonal-mean variables from DJF to JJA.
* Update the figure title from DJF to JJA.
* Run the program and compare the JJA circulation patterns with the DJF patterns from Exercise 3.

```bash
python w12_04_JJA_two_hemispheres.py
```

Questions to consider:

* How does Northern Hemisphere sea level pressure change between DJF and JJA?
* How does Southern Hemisphere sea level pressure change between DJF and JJA?
* Which pressure systems become stronger or weaker between the two seasons?

---

### Exercise 5: Polar SST Trends

Complete the sample program to calculate and visualize long-term SST trends in the Northern and Southern Hemisphere polar regions.

First, copy the sample program:

```bash
cp w12_05_SST_trend_polar_50deg.sample.py w12_05_SST_trend_polar_50deg.py
```

Then complete the tasks marked in the program:

```bash
w12_05_SST_trend_polar_50deg.py
```

Tasks:

1. Read the SST variable from the HadISST dataset.
2. Mask SST values colder than -2.1°C.
3. Select SST data for the 1982–2025 analysis period.
4. Calculate annual SST anomalies relative to the 1991–2020 monthly climatology.
5. Add a cyclic longitude point to remove the map seam.
6. Calculate the linear SST trend in °C per decade.
7. Display the trends using North and South Polar Stereographic projections.
8. Plot the Northern Hemisphere SST trend using filled contours.
9. Plot the Southern Hemisphere SST trend using filled contours.

Run the completed program:

```bash
python w12_05_SST_trend_polar_50deg.py
```

Concepts:

* HadISST sea surface temperature
* Data masking
* Monthly climatology and annual SST anomalies
* Grid-point linear trends
* SST trends in °C per decade
* North and South Polar Stereographic projections
* High-latitude climate change
* Hemispheric comparison of ocean temperature trends

The maps focus on the high-latitude regions:

* Northern Hemisphere: 50°N–90°N
* Southern Hemisphere: 90°S–50°S

Using the same contour levels and color scale allows the magnitude and spatial pattern of SST trends to be compared directly between the Arctic and Southern Ocean regions.

---

## Key Takeaways

* Polar stereographic projections provide an effective way to visualize climate patterns at high latitudes.
* Circular polar maps reduce the visual distortion that occurs near the poles in standard latitude-longitude projections.
* Northern and Southern Hemisphere maps allow direct comparison of atmospheric and oceanic climate patterns.
* Seasonal SLP maps reveal substantial differences in atmospheric circulation between DJF and JJA.
* Polar SST trend maps reveal the spatially heterogeneous pattern of long-term ocean temperature change at high latitudes.
