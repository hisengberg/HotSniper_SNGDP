import matplotlib.pyplot as plt
import numpy as np

# Constructing data
x_labels = ['top-left', 'center', 'top-right', 'bottom-left', 'corner', 'bottom-right']
x = np.arange(len(x_labels))
run_time = np.array([36297700, 34231800, 38391200, 37034700, 35400400, 37244600])

# Setting figure size and font size
fig = plt.figure(figsize=(7, 7))  # Figure size is 7x7 inches
plt.rcParams.update({'font.size': 12})  # Set font size to 12

# Set font size to 12
plt.bar(x, run_time, color='dimgray')

plt.ylabel('Time (ms)')

# Convert y-axis unit from ns to ms
ax = plt.gca()  # Get the current Axes object
ax.tick_params(axis='y', labelsize=12)  # Set the font size of y-axis tick labels
# ax.set_ylim([0, 350000000])  # Set the upper limit of the y-axis
ax.set_yticklabels(['{:.0f}'.format(x/1e6) for x in ax.get_yticks()])  # Display y-axis tick labels multiplied by 10^6
plt.ylabel('Time (ms)')  # Modify the y-axis label

# Set y-axis tick labels, set their upper and lower limits, and their minimum tick value
# plt.yticks(np.arange(0, 350000000, 50))

# Display grid lines on y-axis
plt.grid(axis='y', linestyle='-')
plt.gca().set_axisbelow(True)  # Place grid lines below the bar chart

# Adjust subplot margins
plt.subplots_adjust(bottom=0.25)

# Set x-axis tick labels and rotate by 15 degrees
plt.xticks(x, x_labels, rotation=15)

# Save as EPS file
# plt.savefig('./simtime_of_llc_latency_impact.eps', format='eps', bbox_inches='tight', dpi=300)  # eps文件，用于LaTeX
# plt.savefig('./simtime_of_power_budget_impact.eps', format='eps', bbox_inches='tight', dpi=300)  # eps文件，用于LaTeX

# Display the plot
plt.show()