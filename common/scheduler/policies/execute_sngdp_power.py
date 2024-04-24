#
# This file is part of SNGDP.
# Copyright (C) 2024 Hai Wang and Jincheng Guo.
#
# SNGDP is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# SNGDP is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License along
# with SNGDP. If not, see <https://www.gnu.org/licenses/>.
# 

import sys
import scipy.io as spio
import numpy as np
import re
import sngdp

def execute_sngdp_power(core_num):
    
    print('[Scheduler] [SNGDP]: Starting the SNGDP power budgeting process by executing execute_sngdp_power.py')

    core_num = int(core_num)
    
    # read configurations from base.cfg, including max_temperature (threshold temperature), ambient_temperature, etc
    file_config = open('../config/base.cfg')
    for line in file_config:
        if line.startswith('max_temperature'):
            line_words = re.split('=|#|\s', line)  # split the line into words with splitor '=', '#', and whitespaces
            line_words = list(filter(None, line_words))  # filt out the whitespaces
            temp_max = float(line_words[1])
        if line.startswith('ambient_temperature'):
            line_words = re.split('=|#|\s', line)
            line_words = list(filter(None, line_words))
            temp_amb = float(line_words[1])
        if line.startswith('sngdp_mode'):
            line_words = re.split('=|#|\s', line)
            line_words = list(filter(None, line_words))
            sngdp_mode = line_words[1]
        if line.startswith('dvfs_epoch'):
            line_words = re.split('=|#|\s', line)
            line_words = list(filter(None, line_words))
            dvfs_epoch = int(line_words[1])
        if line.startswith('inactive_power'):
            line_words = re.split('=|#|\s', line)
            line_words = list(filter(None, line_words))
            inactive_power = float(line_words[1])
        if line.startswith('floorplan'):
            line_words = re.split('=|#|\s', line)
            line_words = list(filter(None, line_words))
            name_of_chip = re.split('/|\.', line_words[1])[-2]
    file_config.close()
        
    # load the multi-core system's thermal model matrices
    if sngdp_mode == 'steady':
        A = spio.loadmat('./gdp_thermal_matrices/'+name_of_chip+'_A.mat')['A']
    elif sngdp_mode == 'transient':
        if dvfs_epoch == 1000000:
            A = spio.loadmat('./gdp_thermal_matrices/'+name_of_chip+'_A_1ms.mat')['A_bar']
        else:
            raise Exception("sngdp current only supports dvfs_epoch = 1000000, please modify base.cfg")
    else:
        raise Exception("sngdp mode can only be steady and transient, please modify base.cfg")

    # load the current active core distribution in core_map. 'mapping.txt' is writen by SchedulerOpen::periodic in scheduler_open.cc for every DVFS cycle
    core_map = np.loadtxt('./system_sim_state/mapping.txt')
    core_map = np.asarray(core_map, dtype=bool)  # use bool type to extract Ai matrix from A(将 core_map 转换为布尔类型数组，这是为了从 A 矩阵中提取 Ai 矩阵时使用)

    # load the current temperature/power from files, ingore the first line which contains core names
    T_c = np.loadtxt('./InstantaneousTemperature.log',skiprows=1)  # current temperature
    P_k = np.loadtxt('./InstantaneousPower.log',skiprows=1)  # previous power consumption

    # formulate the static power vector: in hotsniper, every core (active or not) has the same static power
    P_s = np.full((A.shape[0],), inactive_power)
    
    # Compute power budget using sngdp power budgeting core function
    P = sngdp.sngdp_power(A, core_map, temp_max, temp_amb, P_s, P_k, T_c, sngdp_mode)
    
    print('[Scheduler] [SNGDP]: Power budget determined by SNGDP (W): ', P)

    # Write power budget P into file
    file_power = open('./system_sim_state/sngdp_power.txt', 'w')
    for power in P:
        file_power.write(str(np.asscalar(power))+' ')
    file_power.close()


if len(sys.argv) != 2:
    raise Exception('Please provide core number when calling sngdp_power.py')

execute_sngdp_power(sys.argv[1])



