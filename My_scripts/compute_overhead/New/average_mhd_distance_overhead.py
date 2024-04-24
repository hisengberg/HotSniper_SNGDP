import math
from typing import List

# Define a global various
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


def coordinate_to_id(coordinate):
    """
    Convert core coordinates (x,y) to core_id
    """
    global total_cores
    dim = int(math.sqrt(total_cores))
    core_x, core_y = coordinate
    return core_x + core_y * dim


def test_coordinate_to_id():
    """
    Testing coordinate_to_id(coordinate) function
    """
    core_axis = (1,1)
    core_id = coordinate_to_id(core_axis)
    print(f'Core ID for coordinate {core_axis}: {core_id}')


def manhattan_distance(core1_id, core2_id):
    """
    Calculate the Manhattan distance between two points
    """
    return abs(core1_id[0] - core2_id[0]) + abs(core1_id[1] - core2_id[1])


def compute_core_amd_list(core_ids):
    """
    Compute the AMD value for each core
    input: List of core_ids
    output: List of AMD values for each core
    """
    global total_cores

    core_axis = [id_to_coordinate(core_ids[i]) for i in range(len(core_ids))]  # Save the coordinates of each core_id in the input list to a list
    cores_amd = [0] * len(core_ids)
    for i in range(len(core_ids)):  # Iterate through each core_id
        d_sum = 0
        for j in range(int(pow(total_cores, 0.5))):  # y-axis
            for k in range(int(pow(total_cores, 0.5))):  # x-axis
                d = abs(core_axis[i][0] - k) + abs(core_axis[i][1] - j)
                d_sum += d
        cores_amd[i] = d_sum / total_cores
    return cores_amd


def compute_core_amd(core_id):
    """
    Compute the AMD for each core
    input: Core_id
    output: AMD value for the core
    """
    global total_cores

    core_coord = id_to_coordinate(core_id)  # Convert the input core_id to coordinates
    d_sum = 0
    for j in range(int(pow(total_cores, 0.5))):  # y-axis
        for k in range(int(pow(total_cores, 0.5))):  # x-axis
            d = abs(core_coord[0] - k) + abs(core_coord[1] - j)
            d_sum += d
    core_amd = d_sum / total_cores
    return core_amd


def test_compute_core_amd_list():
    core_id_list = list(range(total_cores))
    # core_id_list = [4, 7, 27, 39]

    cores_amd = compute_core_amd_list(core_id_list)
    print(f'cores_id_list = {core_id_list}，\nTheir AMD values are {cores_amd}')


def test_compute_core_amd():
    core_id = 63
    core_amd = compute_core_amd(core_id)
    print(f'core_id = {core_id}，its AMD value is {core_amd}')



if __name__ == '__main__':
    # test_compute_core_amd_list()
    test_compute_core_amd()
    # test_coordinate_to_id()