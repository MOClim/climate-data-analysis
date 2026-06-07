# ---------------------------------------------------------
# Visualization Tips for Scientific Figures
# ---------------------------------------------------------
# This program demonstrates several basic visualization
# techniques commonly used in scientific graphics.
#
# Topics:
#   - Colorblind-friendly palettes
#   - High contrast colors
#   - Patterns and textures
#
# Students can:
#   - Modify colors and hatch styles
#   - Change figure titles and labels
#   - Experiment with different visualization styles
#
# Matplotlib colormap reference:
# https://matplotlib.org/stable/users/explain/colors/colormaps.html
# ---------------------------------------------------------

import matplotlib.pyplot as plt
from pathlib import Path

# ---------------------------------------------------------
# Visualization Tips for Scientific Figures
# ---------------------------------------------------------

fig, axes = plt.subplots(3, 1, figsize=(10, 6))

# ---------------------------------------------------------
# Panel 1: High Contrast Colors
# ---------------------------------------------------------
axes[0].set_title(
    'Tip 1: Use High Contrast Colors',
    fontsize=16,
    fontweight='bold'
)

axes[0].bar(
    [0, 1],
    [0.5, 0.5],
    color=['#FF0000', '#00FF00'],
    edgecolor='black'
)

axes[0].bar(
    [2, 3],
    [0.5, 0.5],
    color=['#0000FF', '#FFFF00'],
    edgecolor='black'
)

axes[0].set_xticks([0, 1, 2, 3])
axes[0].set_xticklabels(['Red', 'Green', 'Blue', 'Yellow'])
axes[0].set_yticks([])

# ---------------------------------------------------------
# Panel 2: Patterns and Textures
# ---------------------------------------------------------
axes[1].set_title(
    'Tip 2: Use Patterns and Textures',
    fontsize=16,
    fontweight='bold'
)

axes[1].bar(
    [0, 1],
    [0.5, 0.5],
    color='grey',
    hatch='/',
    edgecolor='black'
)

axes[1].bar(
    [2, 3],
    [0.5, 0.5],
    color='grey',
    hatch='\\',
    edgecolor='black'
)

axes[1].set_xticks([0, 1, 2, 3])
axes[1].set_xticklabels(
    ['Pattern 1', 'Pattern 2', 'Pattern 3', 'Pattern 4']
)
axes[1].set_yticks([])

# ---------------------------------------------------------
# Panel 3: Colorblind-Friendly Palette
# ---------------------------------------------------------
axes[2].set_title(
    'Tip 3: Colorblind-Friendly Palette',
    fontsize=16,
    fontweight='bold'
)

colors = ['#440154', '#31688e', '#35b779', '#fde725']

axes[2].bar(
    [0, 1, 2, 3],
    [0.5, 0.5, 0.5, 0.5],
    color=colors,
    edgecolor='black'
)

axes[2].set_xticks([0, 1, 2, 3])
axes[2].set_xticklabels(
    ['Viridis 1', 'Viridis 2', 'Viridis 3', 'Viridis 4']
)
axes[2].set_yticks([])

# Adjust spacing between panels
plt.tight_layout()

# Save one merged JPEG file
output_path = Path(__file__).with_suffix('.jpg')
plt.savefig(output_path, dpi=300)

plt.show()
