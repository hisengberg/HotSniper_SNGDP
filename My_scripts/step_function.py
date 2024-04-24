import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

# Define segment information for the step function
segments = [(0, 0.5, 7), (0.5, 1, 6.25), (1, 1.5, 5.75), (1.5, 2, 5.5), (2, 2.5, 5), (2.5, 3, 4.75), (3, 3.5, 4.5)]

# Extract x and y values from the segment information
x_values = [0]  # Initialize x-axis data
y_values = [7]  # Initialize y-axis data

for segment in segments:
    x_values.extend([segment[0], segment[1]])
    y_values.extend([segment[2], segment[2]])

# Add the last point to complete the last segment
x_values.append(segments[-1][1])
y_values.append(segments[-1][2])

# Add additional points to ensure the line segments of the step function are always displayed
x_values.extend([3.5, 4])
y_values.extend([4.5, 4.5])

# Draw the step function graph
plt.step(x_values, y_values, where='post')
plt.xlim(0, 4)  # Set the display range of the x-axis
plt.xticks([0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5])  # Set x-axis ticks
plt.yticks([4, 4.25, 4.5, 4.75, 5, 5.5, 5.75, 6.25, 7])  # Set y-axis ticks

# Set the y-axis range slightly higher than the x-axis
plt.ylim(bottom=3.8)

# Format y-axis tick labels, remove trailing zeros
plt.gca().yaxis.set_major_formatter(StrMethodFormatter('{x:g}'))

plt.xlabel('$\mathbf{r_{c}(\\%)}$', fontweight='bold')
plt.ylabel('Assigned AMDmax', fontweight='bold')

# Mark known points
known_points = [(0.24, 7), (0.86, 6.25), (0.9, 6.25), (1.35, 5.75), (1.45, 5.75), (2.18, 5), (2.81, 4.75), (3.29, 4.5)]
plt.scatter([point[0] for point in known_points], [point[1] for point in known_points], color='red', label='PARSEC Benchmark Suit')
plt.legend(loc='right')

# Show legend
plt.legend()

plt.grid(True)

# Save as an EPS file
# plt.savefig('./step_function.eps', format='eps',  bbox_inches='tight', dpi=300)  # EPS file for LaTeX

plt.show()

