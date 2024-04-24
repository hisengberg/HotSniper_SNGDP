# For the same benchmark, change different MAMD values and compare the run-time under different mappings.
import matplotlib.pyplot as plt
import numpy as np

# Date construction
#--------------------------------- Only for 'fluidanimate' and 'x264' --------------------------------
# x_labels = ['SNSched', '4.25', '4.5', '4.75', '5', '5.5', '5.75', '6.25', '7\n(GDP)', 'PCGov\n(AMDmax=5)']
# x = np.arange(len(x_labels))
# y = np.array([])
#----------------------------------------------------------------------------------------------------
x_labels = ['4.5\n(SNSched_tsp)', '4.5\n(SNSched_gdp)', '4.75', '5', '5.5', '5.75', '6.25', '7\n(GDP)', 'PCGov\n(AMDmax=5)']
x = np.arange(len(x_labels))
y = np.array([277120500, 274314200, 282340300, 271050300, 273306500, 279422000, 272564800, 281118200, 309528200])

# Set the size of the figure and font size
fig = plt.figure(figsize=(16, 9))  # Figure size is 16x9 inches
plt.rcParams.update({'font.size': 12})  # Set font size to 12

# Draw bar chart
plt.bar(x, y, color='dimgray')

# Set legend and labels
plt.legend()  # Set legend
#------------------------------------
plt.xlabel('blackscholes-16-simlarge')
# plt.xlabel('bodytrack-16-simlarge')
# plt.xlabel('canneal-16-simsmall')
# plt.xlabel('dedup-16-simsmall')
# plt.xlabel('fluidanimate-9-simlarge')
# plt.xlabel('streamcluster-16-simlarge')
# plt.xlabel('swaptions-16-simlarge')
# plt.xlabel('x264-9-simmedium')
#------------------------------------

plt.ylabel('Time (ms)')
plt.title('The runtime with different AMDmax')

# Set x-axis tick labels and rotate by 30 degrees
# plt.xticks(x, x_labels, rotation=30)
plt.xticks(x, x_labels)

# Convert the unit 'ns' on the y-axis to 'ms' for display
ax = plt.gca()  # Get the current Axes object
ax.tick_params(axis='y', labelsize=12)  # Set the font size of the y-axis tick labels
# ax.set_ylim([0, 350000000])  # Set the upper limit of the y-axis
ax.set_yticklabels(['{:.0f}'.format(x/1e6) for x in ax.get_yticks()])  # Display the y-axis tick labels multiplied by 10^6
plt.ylabel('Time (ms)')  # Modify the y-axis label

# Set y-axis tick labels, their upper and lower limits, and the minimum scale value
# plt.yticks(np.arange(0, 350000000, 50))

# Display grid lines on the y-axis
plt.grid(axis='y', linestyle='-')
plt.gca().set_axisbelow(True)  # Place grid lines below the bars

# Adjust subplot margins
plt.subplots_adjust(bottom=0.25)

# Show the plot
plt.show()
