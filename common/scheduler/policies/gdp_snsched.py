#
# This file is part of GDP.
# Copyright (C) 2022 Hai Wang and Qinhui Yang.
#
# GDP is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# GDP is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License along
# with GDP. If not, see <https://www.gnu.org/licenses/>.
#

import numpy as np
import average_mhd_distance as amd
import time     # for testing runtime overhead


def gdp_map(A, temp_max, temp_amb, taskCoreRequirement, activeCores, availableCores, preferredCoresOrder, P_s):
    # The function to find the GDP optimized active core map.

    # Inputs:
    # A: system thermal model matrix, usually A = B^T G^{-1} B according to the GDP paper.
    # temp_max: temperature threshold scalar.
    # temp_amb: ambient temperature scalar.
    # taskCoreRequirement: the number of new active cores need to be mapped.
    # activeCores: boolean vector of the existing active core map, indicating if each core is active (True) or inactive (False). If you want to override some existing active cores, set them to False.
    # availableCores: boolean vector of the current inactive cores that can be activated (active core candidates), indicating if each core can be activated (True) or cannot be activated (False).
    # preferredCoresOrder: the user specified activation order vector, -1 indicates the end of the preferred cores. These cores should be activated first (if available) before GDP computation. If user do not specify any activation order, simply set all elements to -1.
    # P_s: static power vector, each element is the static power value of each core, use an all zero vector if no static power.

    # Output:
    # cores_to_activate: vector of the new active core indexes.

    # record start time
    start_time = time.time()

    # total core number of the multi/many core system
    core_num = availableCores.shape[0]  # .shape[0]: Read the length of the first dimension of the matrix.(.shape[0]表示读取矩阵第一维度的长度，即数组的行数；.shape[1]表示返回数组的列数)

    # find the user specified preferred cores that are still in available cores, they should be activated first without GDP computing
    inact_pref_cores = np.zeros(core_num) - 1  # initiate all elements to -1
    n_ipc = 0  # number of inactive preferred cores
    for core_id in preferredCoresOrder:
        if availableCores[core_id] == True and core_id != -1:
            inact_pref_cores[n_ipc] = core_id
            availableCores[core_id] = False
            activeCores[core_id] = True
            n_ipc = n_ipc + 1

    # Initiate cores_to_activate using inact_pref_cores, because we need to activate the inactive preferred cores first.
    cores_to_activate = inact_pref_cores[:taskCoreRequirement]  # all the inactive preferred cores should be activated first

    # If taskCoreRequirement <= n_ipc, then we are simply done without GDP computation. Otherwise (if taskCoreRequirement > n_ipc), we need to determine the remaining active cores using GDP iterations.
    if taskCoreRequirement > n_ipc:
        # initiate GDP iterations
        T_s = A @ P_s  # static power's impact on temperature, should be substracted from T_th later
        # np.full((core_num,), temp_max - temp_amb)表示这样的一个向量：里面的元素个数是core_num个，元素的值是temp_max - temp_amb
        T_th = np.full((core_num,), temp_max - temp_amb) - T_s  # threshold temperature vector
        if np.sum(activeCores) > 0:
            Ai = np.atleast_2d(A[activeCores][:, activeCores])  # np.atleast_2d 用于将一个或多个输入数组转换为至少二维的数组。如果输入数组本身就是二维或更高维的，则该函数不会做任何操作。
            T_th_i = T_th[activeCores]
            Pi = np.linalg.solve(Ai, T_th_i)  # power budget of the existing active cores
            T_rm = T_th[availableCores] - A[availableCores][:,activeCores] @ Pi  # temperature threshold headroom of the available cores (candidates) by substracting the existing active cores' thermal impact
        else:  # when there is no existing active core and no user preferred core
            T_rm = T_th[availableCores]

        Aa = np.atleast_2d(A[availableCores][:, availableCores])
        idx_available_cores = np.flatnonzero(availableCores)  # np.flatnonzero()函数用于返回数组中非零元素的索引。具体来说返回一个一维数组，其中包含输入数组中所有非零元素的索引。

        for i in range(n_ipc, taskCoreRequirement):
            if i == n_ipc:
                first_open_core = True
            else:
                first_open_core = False
            idx = 0
            if first_open_core:  # find the first core in available cores (candidates) which leads to the largest power budget (indicated by the largest inner product with T_rm)
                for j in range(1, idx_available_cores.shape[0]):
                    if np.inner(Aa[:][j], T_rm) > np.inner(Aa[:][idx], T_rm):  # A中谁与T_rm的内积最大，谁的功率预算就最大，就选谁开核
                        idx = j
            else:
                # 剩下的开核分布由gdp和amd共同决定
                # min_target = float('inf')  # 初始化目标函数为正无穷
                # min_target_cores = list(cores_to_activate[:i])  # 将目标函数最小时对应的开核分布初始化为仅由gdp确定的开核
                # for j in range(idx_available_cores.shape[0]):
                #     # 从余下的available cores中逐一挑出，放进min_target_cores列表中
                #     candidate = int(idx_available_cores[j])
                #     min_target_cores.append(candidate)
                #
                #     # 依次算出当前开核的平均曼哈顿距离
                #     amd_value = amd.average_manhattan_distance(min_target_cores)
                #
                #     availableCores[idx_available_cores[j]] = False
                #     activeCores[idx_available_cores[j]] = True
                #
                #     # update T_rm
                #     Ai = np.atleast_2d(A[activeCores][:, activeCores])
                #     T_th_i = T_th[activeCores]
                #     Pi = np.linalg.solve(Ai, T_th_i)
                #     T_rm = T_th[availableCores] - A[availableCores][:, activeCores] @ Pi
                #
                #     # 依次算成当前开核的T_rm的平均值
                #     mean_T_rm = np.mean(T_rm)
                #
                #     # 将当前开核的平均曼哈顿距离和T_rm平均值相加，获取两者相加最小时的当前开核分布
                #     a = 0.9
                #     target_value = a*(amd_value-1)/(5.3-1) + (1-a)*(mean_T_rm-6.6)/(32-6.6)
                #     if target_value < min_target:  # 更新最小的系统平均曼哈顿距离以及对应的开核分布
                #         min_target = target_value
                #         idx = j
                #
                #     availableCores[idx_available_cores[j]] = True
                #     activeCores[idx_available_cores[j]] = False
                #     min_target_cores = list(cores_to_activate[:i])

                # ------------------------------------------------------------------------------------------------------

                # 接下来寻找开核分布的时候，仅考虑曼哈顿距离的因素
                # min_amd = float('inf')  # 初始化系统的平均曼哈顿距离为正无穷
                # min_amd_cores = list(cores_to_activate[:i])  # 初始化系统平均曼哈顿距离最小时对应的开核列表仅为由gdp确定的初始开核
                # for j in range(idx_available_cores.shape[0]):
                #     # 从余下的available cores中逐一挑出，放进min_amd_cores列表中
                #     candidate = int(idx_available_cores[j])
                #     min_amd_cores.append(candidate)
                #     # 依次算出系统的平均曼哈顿距离
                #     amd_value = amd.average_manhattan_distance(min_amd_cores)
                #
                #     if amd_value < min_amd:  # 更新最小的系统平均曼哈顿距离以及对应的开核分布
                #         min_amd = amd_value
                #         idx = j
                #     min_amd_cores = list(cores_to_activate[:i])

                # ------------------------------------------------------------------------------------------------------

                # 选核算法5：gdp和SNSched
                # min_target = float('inf')  # 初始化系统的目标函数为正无穷
                # min_target_cores = list(cores_to_activate[:i])  # 初始化系统目标函数最小时对应的开核列表仅为由gdp确定的初始开核
                # for j in range(idx_available_cores.shape[0]):
                #     # 从余下的available cores中逐一挑出，放进min_target_cores列表中
                #     candidate = int(idx_available_cores[j])
                #     min_target_cores.append(candidate)
                #
                #     core_amd = amd.compute_core_amd(min_target_cores)
                #     # 依次算出当前开核中最大的AMD值
                #     max_core_amd = max(core_amd)
                #     # 依次算出当前开核中最大的AMD值和最小的AMD值之差
                #     # max_gap_core_amd = max(core_amd) - min(core_amd)
                #
                #     availableCores[idx_available_cores[j]] = False
                #     activeCores[idx_available_cores[j]] = True
                #
                #     Ai = np.atleast_2d(A[activeCores][:, activeCores])
                #     T_th_i = T_th[activeCores]
                #     Pi = np.linalg.solve(Ai, T_th_i)
                #     T_rm = T_th[availableCores] - A[availableCores][:, activeCores] @ Pi
                #
                #     # 依次算出当前开核情况下的T_rm的平均值
                #     mean_T_rm = np.mean(T_rm)
                #
                #     # 依次算出当前开核情况下的T_rm的二范数
                #     # norm_T_rm = np.linalg.norm(T_rm)
                #
                #     # 将当前开核分布中max_core_amd和T_rm平均值相加，获取两者相加最小时的当前开核分布
                #     a = 65  # 增大/减小a会使得前期下降更快速/缓慢
                #     b = 0.94  # 增大/减下b会使得整体下降更缓慢/快速
                #     c = 7  # 增大/减小c会使得图像整体上移/下移
                #     d = 0.1
                #     y = (a*(b**taskCoreRequirement)+c)*d
                #     rc = 1.305
                #     target_value = mean_T_rm + y * max_core_amd * rc
                #     if target_value < min_target:
                #         min_target = target_value
                #         idx = j
                #
                #     availableCores[idx_available_cores[j]] = True
                #     activeCores[idx_available_cores[j]] = False
                #     min_target_cores = list(cores_to_activate[:i])

                # ------------------------------------------------------------------------------------------------------

                # SNSched
                min_target = float('inf')  # 初始化系统的目标函数为正无穷
                min_target_cores = list(cores_to_activate[:i])  # 初始化系统目标函数最小时对应的开核列表仅为由gdp确定的初始开核

                for j in range(idx_available_cores.shape[0]):
                    # 从余下的available cores中逐一挑出，放进min_target_cores列表中
                    candidate = int(idx_available_cores[j])
                    min_target_cores.append(candidate)

                    core_amd = amd.compute_core_amd_list(min_target_cores)

                    # 依次算出当前开核中最大的AMD值
                    max_core_amd = max(core_amd)
                    # 依次算出当前开核中最大的AMD值和最小的AMD值之差
                    max_gap_core_amd = max(core_amd) - min(core_amd)

                    availableCores[idx_available_cores[j]] = False
                    activeCores[idx_available_cores[j]] = True

                    target_value = max_core_amd + max_gap_core_amd
                    if target_value < min_target:
                        min_target = target_value
                        idx = j

                    availableCores[idx_available_cores[j]] = True
                    activeCores[idx_available_cores[j]] = False
                    min_target_cores = list(cores_to_activate[:i])

                # ------------------------------------------------------------------------------------------------------

            # add the new active core (idx) to the existing active cores
            cores_to_activate[i] = idx_available_cores[idx]  # add the new active core (idx) to the list of cores to activate as the final output
            availableCores[idx_available_cores[idx]] = False
            activeCores[idx_available_cores[idx]] = True
            Aa = np.atleast_2d(A[availableCores][:, availableCores])
            idx_available_cores = np.flatnonzero(availableCores)

            # update T_rm
            Ai = np.atleast_2d(A[activeCores][:, activeCores])
            T_th_i = T_th[activeCores]
            Pi = np.linalg.solve(Ai, T_th_i)
            T_rm = T_th[availableCores] - A[availableCores][:, activeCores] @ Pi

    # record end time
    end_time = time.time()

    # compute runtime overhead
    execution_time = (end_time - start_time) * 1000  # convert to ms
    print('======================================================')
    print('gdp_map runtime overhead: {} ms'.format(execution_time))
    print('======================================================')

    return cores_to_activate


def gdp_power(A, core_map, temp_max, temp_amb, P_s, P_k, T_c, gdp_mode):
    # The function to compute the GDP power budget for a given active core map(该函数的功能是计算一个给定的开核分布的功率预算)
    # Inputs:
    # A: system matrix, usually A = B^T G^{-1} B according to the GDP paper
    # core_map: boolean vector of the active core map, indicating if each core is active (True) or inactive (False)
    # temp_max: temperature threshold scalar
    # temp_amb: ambient temperature scalar
    # P_s: static power vector, each element is the static power value of each core, use an all zero vector if no static power
    # P_k: power vector of all cores at the previous step (assume current time is t, power budgeting/DVFS step is h, P_k is the power from time t-h to t, and we want to compute the power budget P for time t to t+h)
    # T_c: temperature vector of all cores at the current time (at time t in the example of P_k)
    # gdp_mode: 'steady' for steady state GDP and 'transient' for transient GDP
    # Output:
    # P: power budget of the active cores according to core_map

    # record start time
    start_time = time.time()

    # Compute the static power's impact on temperature. If the static power is assumed to be constant (such as in HotSniper), this impact is constant and actually can be pre-computed only once outside
    T_s = A @ P_s  # static power's impact on temperature, should be substracted from T_th later

    # formulate the Ai matrix (a submatrix of A according to the active core mapping)
    Ai = np.atleast_2d(A[core_map][:, core_map])
    if gdp_mode == 'steady':  # for steady state GDP
        T_th = np.full((Ai.shape[0],), temp_max - temp_amb) - T_s[core_map]  # threshold temperature vector
    else:  # for transient GDP
        T_th = np.full((Ai.shape[0],), temp_max) - T_c[core_map] + Ai @ P_k[core_map] - T_s[core_map]

    # Compute power budget with current active core mapping, solve power budget P
    P = np.linalg.solve(Ai, T_th) + P_s[core_map]

    # record end time
    end_time = time.time()

    # compute runtime overhead
    execution_time = (end_time - start_time) * 1000  # convert to ms
    
    print('=============================================================')
    print('gdp_power runtime overhead: {} ms'.format(execution_time))
    print('=============================================================')

    return P
