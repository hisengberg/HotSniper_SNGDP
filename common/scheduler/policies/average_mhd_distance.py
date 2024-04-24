import math

# define a global various
total_cores = 64

def id_to_coordinate(core_id: int):
    global total_cores
    side_length = int(math.sqrt(total_cores))
    core_x = core_id % side_length
    core_y = core_id // side_length  # 取的是结果的最小整数
    return core_x, core_y

def coordinate_to_id(coordinate):
    global total_cores
    side_length = int(math.sqrt(total_cores))
    core_x, core_y = coordinate
    return core_x + core_y * side_length

def manhattan_distance(core1_id, core2_id) -> int:
    """
    计算两个点的曼哈顿距离
    """
    return abs(core1_id[0] - core2_id[0]) + abs(core1_id[1] - core2_id[1])

#这个函数没被用到，但是也不删了，就留着吧
def average_manhattan_distance(ids) -> float:
    """
    计算n个core的平均曼哈顿距离
    input: 存放core_id的列表
    output: 这些core_id的平均曼哈顿距离
    """
    # 使用循环将每个点的坐标计算出来，并将坐标存储在一个列表中
    coordinates = []
    for core_id in ids:
        coordinate = id_to_coordinate(core_id)
        coordinates.append(coordinate)

    total_distance = 0
    for i in range(len(coordinates)):
        for j in range(i + 1, len(coordinates)):
            total_distance += manhattan_distance(coordinates[i], coordinates[j])
    return total_distance / (len(coordinates) * (len(coordinates) - 1) / 2)  # 由于每个点都要与其他所有点均计算一遍曼哈顿距离，因为有len(coordinates) * (len(coordinates) - 1) / 2种不同的点对组合

def compute_core_amd_list(core_ids):
    """
    计算每个core的AMD值
    input: 存放core_id的列表、总核心数
    output: 由每个core的AMD值所组成的列表
    """
    global total_cores
    core_coords = [id_to_coordinate(core_ids[i]) for i in range(len(core_ids))]  # 将输入列表中的每个core_id的坐标保存到一个列表中
    cores_amd = [0] * len(core_ids)
    for i in range(len(core_ids)):  # 每个core_id进行一次遍历
        d_sum = 0
        for j in range(int(pow(total_cores, 0.5))):  # y轴
            for k in range(int(pow(total_cores, 0.5))):  # x轴
                d = abs(core_coords[i][0] - k) + abs(core_coords[i][1] - j)
                d_sum += d
        cores_amd[i] = d_sum / total_cores
    return cores_amd

def compute_core_amd(core_id):
    """
    input: Core_id
    output: AMD(core_id)
    """
    global total_cores
    core_coord = id_to_coordinate(core_id)  # 将输入的core_id转换为坐标
    d_sum = 0
    for j in range(int(pow(total_cores, 0.5))):  # y轴
        for k in range(int(pow(total_cores, 0.5))):  # x轴
            d = abs(core_coord[0] - k) + abs(core_coord[1] - j)
            d_sum += d
    core_amd = d_sum / total_cores
    return core_amd

#-------------------------------------------------------------------------------
def test_system_amd():
    # core_list = list(range(64))
    core_list = [27, 28, 36, 35]
    value = average_manhattan_distance(core_list)
    print(value)

def test_core_amd():
    core_ids = 0
    amd = compute_core_amd(core_ids)
    print(amd)

def test_core_amd_list():
    core_ids_list = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
    amd_list = compute_core_amd_list(core_ids_list)
    print(amd_list)

if __name__ == '__main__':
    # test_system_amd()
    # test_core_amd()
    test_core_amd_list()