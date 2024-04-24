import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
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


def plot_mamd_candidates():
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
    ax.set_xticks(np.arange(-.5, 8, 1), minor=True)
    ax.set_yticks(np.arange(-.5, 8, 1), minor=True)
    ax.grid(which='minor', color='black', linestyle='-', linewidth=0)

    # Put x-axis ticks on top and set labels
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    ax.set_xticks(np.arange(dim))
    ax.set_xticklabels(np.arange(dim))

    # Set y-axis labels
    ax.set_yticks(np.arange(dim))
    ax.set_yticklabels(np.arange(dim))

    # Show core_ids and data in each cell
    for i in range(matrix_data.shape[0]):
        for j in range(matrix_data.shape[1]):
            # Show core ID above each cell
            core_number = i * matrix_data.shape[1] + j
            ax.text(j, i - 0.2, f'#{core_number}', ha='center', va='center', fontsize=18)
            # Show data below each cell
            ax.text(j, i + 0.25, f'{matrix_data[i, j]}', ha='center', va='center', fontsize=18)

            # Add a black border around specified squares
            MAMD_4 = [27,28,35,36]
            MAMD_4_25 = [19,20,26,27,28,29,34,35,36,37,43,44]
            MAMD_4_5 = [18,19,20,21,26,27,28,29,34,35,36,37,42,43,44,45]
            MAMD_4_75 = [11,12,18,19,20,21,25,26,27,28,29,30,33,34,35,36,37,38,42,43,44,45,51,52]
            MAMD_5 = [10,11,12,13,17,18,19,20,21,22,25,26,27,28,29,30,33,34,35,36,37,38,41,42,43,44,45,46,50,51,52,53]
            MAMD_5_5 = [3,4,9,10,11,12,13,14,17,18,19,20,21,22,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,41,42,43,44,45,46,49,50,51,52,53,54,59,60]
            MAMD_5_75 = [2,3,4,5,9,10,11,12,13,14,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,49,50,51,52,53,54,58,59,60,61]
            MAMD_6_25 = [1,2,3,4,5,6,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,
                               31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,57,58,59,60,61,62]
            MAMD_7 = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,
                               31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63]

            core_candidates = MAMD_4        
            if core_number in core_candidates:
                rect = plt.Rectangle((j - 0.5, i - 0.5), 1, 1, linewidth=4, edgecolor='black', facecolor='none')
                ax.add_patch(rect)

    # Save the generated heatmap to a specified path
    # save_path = directory  # Set custom path
    # save_name = 'NUCA_cache accesses Heatmap.png'  # Set custom name
    # fig.savefig(save_path + save_name)

    # Save as EPS file
    #plt.savefig('./AMDmax=7.eps', format='eps', bbox_inches='tight', dpi=300)  # EPS file for LaTeX

    # Display the plot
    plt.show()



if __name__ == '__main__':
    plot_mamd_candidates()