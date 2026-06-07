# Homework 6 Review — Monthly vs Annual Histogram Analysis

## Overview
This homework reviews how to interpret a Skew-T diagram during a winter inversion event using radiosonde observations from Salt Lake City, Utah.

Students analyzed atmospheric temperature structure, moisture conditions, and wind profiles to identify a lower-atmospheric inversion associated with stable winter weather conditions.

Example script: `python/week06_02_skewT/solution/w06_10_skew_T.Inversion.HW_sample.py`

---
### Question 1
Which UTC time best represents the morning atmospheric conditions on January 29, 2024?

Salt Lake City operates on Mountain Standard Time (MST), which is 7 hours behind UTC during winter.

The radiosonde launch times are:
- 00 UTC
- 12 UTC

The 12 UTC sounding corresponds to approximately 5 AM MST, which best represents the morning atmospheric conditions before daytime heating develops.

Therefore, the correct observation time is:
```python
doi = datetime(2024, 1, 29, 12)
```

---
### Science Questions
#### Did a temperature inversion occur?

Yes. A clear lower-tropospheric temperature inversion is visible on the Skew-T diagram.

Normally, atmospheric temperature decreases with height. However, in this sounding, temperature increases with height within the lower atmosphere near the surface.

This indicates stable atmospheric conditions and suppressed vertical mixing.

#### Where does the inversion layer appear?

The inversion layer appears in the lower atmosphere below approximately:

800–700 hPa

Near the surface, colder air is trapped beneath relatively warmer air aloft.

This structure is commonly observed during wintertime valley inversions in northern Utah.

#### How can the inversion contribute to poor air quality?

Temperature inversions suppress vertical air mixing.

As a result:
- Cold dense air becomes trapped near the surface
- Pollutants accumulate within the shallow boundary layer
- Winds remain weak
- Visibility and air quality can deteriorate

These conditions often lead to winter haze and elevated particulate pollution in urban valleys.

---
### Atmospheric Interpretation

#### Temperature and Dew Point
The temperature profile (red line) shows stable lower-atmospheric structure.
The dew point profile (blue line) remains relatively close to the temperature profile in the lower atmosphere, indicating moist and stagnant air.

#### Wind Barbs
Winds are generally weak in the lower atmosphere.
Weak winds help maintain the inversion by limiting vertical mixing.

#### Stability

The sounding indicates:
- Strong static stability
- Suppressed convection
- Minimal CAPE
- Favorable conditions for persistent cold-air pooling

---
## Key Takeaways
- Winter inversions commonly form under high-pressure systems and weak winds.
- Temperature inversions trap cold air and pollutants near the surface.
- Skew-T diagrams are useful for diagnosing atmospheric stability and boundary-layer structure.
- Radiosonde observations provide valuable vertical atmospheric information for weather and air-quality analysis.
