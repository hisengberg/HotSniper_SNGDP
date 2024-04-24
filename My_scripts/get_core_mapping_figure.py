'''
This code generates a distribution map of activated cores.
'''
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Define the total number of cores on the chip
total_cores = 9

# Define the IDs of activated cores
active_core_id = np.array([1, 3, 5, 7])

# Create a 2D grid
dim = int(math.sqrt(total_cores))
grid = np.zeros((dim, dim))     # Core distribution of dim x dim

# Set the positions corresponding to the core IDs to 1
for num in active_core_id:
    row = num // dim
    col = num % dim
    grid[row, col] = 1

# Plot the figure
fig, ax = plt.subplots()
ax.imshow(grid, cmap='binary_r', vmin=0, vmax=1)

# Add text annotations in each grid
for i in range(dim):
    for j in range(dim):
        ax.text(j, i, '#%s' % str(i * dim + j), ha="center", va="center", color="grey")

# Draw grid lines
ax.set_xticks(np.arange(-.5, dim, 1), minor=True)
ax.set_yticks(np.arange(-.5, dim, 1), minor=True)
ax.grid(which='minor', color='black', linestyle='-', linewidth=2)

# Add the sequence of activated cores as the title
plt.title(f'cores to activated: {active_core_id}')

# Hide x and y axes
ax.set_xticks([])
ax.set_yticks([])

# Save as EPS file
# plt.savefig('./mapping_n16_na4_2.eps', format='eps', bbox_inches='tight', dpi=300)  # EPS file for LaTeX
# plt.savefig('./dark_silicon.eps', format='eps', bbox_inches='tight', dpi=300)  # EPS file for LaTeX

# Display the plot
plt.show()
