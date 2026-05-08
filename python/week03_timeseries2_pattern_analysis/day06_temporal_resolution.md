#Week 03 (Day 6): Temporal Resolution and Panel Plots

## Overview

## Learning Objective
After completing this exercise, students will be able to:

- Understand temporal resolution in climate observations
- Compare daily, hourly, and minute datasets
- Create panel plots using matplotlib
- Use plt.subplot() to organize multiple figures
- Compare different visualization methods for the same dataset

---
## Panel Plot Layouts
### Example 1. Two vertical panels
```python
plt.subplot(2, 1, 1)
plt.subplot(2, 1, 2)
```

### Example 2. Two horizontal panels
```python
plt.subplot(1, 2, 1)
plt.subplot(1, 2, 2)
```

## Example 3. Four panels
```python
plt.subplot(2, 2, 1)
plt.subplot(2, 2, 2)
plt.subplot(2, 2, 3)
plt.subplot(2, 2, 4)
```

---

## Exercise: Plot Two Panels

### Step 1: Copy the sample program and run it
```bash
cp w03_06_2_panels.sample.py w03_06_2_panels.py
python w03_06_2_panels.py
```

The subplot command:
```
plt.subplot(2, 1, 1)  # 1 row, 2 columns, first subplot
```

---

