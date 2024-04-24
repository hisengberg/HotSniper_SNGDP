import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math

total_cores = 64

def id_to_coordinate(core_id: int):
    """
    Convert core_id to coordinates (x,y)
    """
    global total_cores
    dim = int(math.sqrt(total_cores))
    core_x = core_id % dim
    core_y = core_id // dim
    return core_x, core_y


def compute_core_amd_list(core_ids):
    """
    Compute the AMD value for each core
    input: List of core_ids
    output: List of AMD values for each core
    """
    global total_cores
    core_coords = [id_to_coordinate(core_ids[i]) for i in range(len(core_ids))]  # Save the coordinates of each core_id in the input list to a list
    cores_amd = [0] * len(core_ids)
    for i in range(len(core_ids)):  # Iterate through each core_id
        d_sum = 0
        for j in range(int(pow(total_cores, 0.5))):  # y-axis
            for k in range(int(pow(total_cores, 0.5))):  # x-axis
                d = abs(core_coords[i][0] - k) + abs(core_coords[i][1] - j)
                d_sum += d
        cores_amd[i] = d_sum / total_cores
    return cores_amd


def plot_core_amd_distribution():
    global total_cores

    # Data preparation stage
    core_id_list = list(range(total_cores))
    core_id_amd_list = compute_core_amd_list(core_id_list)
    print(core_id_amd_list)

    dim = int(math.sqrt(total_cores))

    # Reshape data into matrix form
    matrix_data = np.reshape(core_id_amd_list, (dim, dim))
    print(matrix_data)

    # Set figure size
    fig = plt.figure(figsize=(10, 10))

    # Draw heatmap
    ax = fig.add_subplot(111)
    im = ax.imshow(matrix_data, cmap='OrRd_r')

    # Draw grid lines
    ax.set_xticks(np.arange(-.5, dim, 1), minor=True)
    ax.set_yticks(np.arange(-.5, dim, 1), minor=True)
    ax.grid(which='minor', color='black', linestyle='-', linewidth=1)

    # Put x-axis ticks on top and set labels
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    ax.set_xticks(np.arange(dim))
    ax.set_xticklabels(np.arange(dim))

    # Set y-axis labels
    ax.set_yticks(np.arange(dim))
    ax.set_yticklabels(np.arange(dim))

    # Show core IDs and data in each cell
    for i in range(matrix_data.shape[0]):
        for j in range(matrix_data.shape[1]):
            # Show core ID above each cell
            ax.text(j, i - 0.2, f'#{i * matrix_data.shape[1] + j}', ha='center', va='center', fontsize=15)
            # Show data below each cell
            ax.text(j, i + 0.25, f'{matrix_data[i, j]}', ha='center', va='center', fontsize=15)

    # Add a color bar and set colormap to reverse
    cbar = ax.figure.colorbar(im, ax=ax)
    # Display only ticks and labels for min and max values
    cbar.set_ticks([np.min(core_id_amd_list), np.max(core_id_amd_list)])
    # Get tick labels
    tick_labels = [str(label) for label in cbar.get_ticks()]

    # Set font size and type for tick labels
    cbar.ax.set_yticklabels(tick_labels, fontsize=12, fontweight='bold')

    cbar.set_label('Core AMD Value', rotation=90, labelpad=0.5, fontsize=12, fontweight='bold')  # Add a label to the color bar

    # Add annotations above and to the left of the heatmap
    ax.text(0.5, 1.05, 'Core X Coordinate', ha='center', va='bottom', transform=ax.transAxes, fontsize=12,
            fontweight='bold')
    ax.text(-0.06, 0.5, f'Core Y Coordinate', ha='center', va='center', transform=ax.transAxes,
            fontsize=12, fontweight='bold', rotation='vertical')

    # Save the generated heatmap to a specified path
    # save_path = directory  # Set custom path
    # save_name = 'NUCA_cache accesses Heatmap.png'  # Set custom name
    # fig.savefig(save_path + save_name)

    # Save as EPS file
    # plt.savefig('./Core AMD Value Distribution Chart.eps', format='eps', bbox_inches='tight', dpi=300)  # EPS file for LaTeX

    # Display the plot
    plt.show()



if __name__ == '__main__':
    plot_core_amd_distribution()