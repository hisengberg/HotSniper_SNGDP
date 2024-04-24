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

import sys  # can realize the joint call of C++ and python.
import scipy.io as spio
import numpy as np
import re
import gdp
import matplotlib.pyplot as plt

from datetime import datetime  # Just to prevent core_mapping from being overwritten when batch is running.


def execute_gdp_mapping(taskCoreRequirement):
    print('[Scheduler] [GDP]: Starting the GDP mapping process by executing execute_gdp_mapping.py')

    taskCoreRequirement = int(taskCoreRequirement)

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
        if line.startswith('inactive_power'):
            line_words = re.split('=|#|\s', line)
            line_words = list(filter(None, line_words))
            inactive_power = float(line_words[1])
        if line.startswith('floorplan'):
            line_words = re.split('=|#|\s', line)
            line_words = list(filter(None, line_words))
            name_of_chip = re.split('/|\.', line_words[1])[-2]
    file_config.close()

    # load the mapping information from file info_for_mapping.txt, saved in mapGDP::map in mapGDP.cc
    mapping_info = np.loadtxt('./system_sim_state/info_for_mapping.txt', dtype=int)
    availableCores = mapping_info[0, :].astype('bool')
    activeCores = mapping_info[1, :].astype('bool')
    preferredCoresOrder = mapping_info[2, :]

    if np.sum(availableCores) < taskCoreRequirement:
        raise Exception('There are not enough available cores to meet the required core number of this task.')

    # load the multi-core system's thermal model matrices
    core_num = availableCores.shape[0]
    A = spio.loadmat('./gdp_thermal_matrices/' + name_of_chip + '_A.mat')['A']

    # formulate the static power vector: in hotsniper, every core (active or not) has the same static power
    P_s = np.full((A.shape[0],), inactive_power)

    # compute the new active core indexes using gdp_mapping
    cores_to_activate = gdp.gdp_map(A, temp_max, temp_amb, taskCoreRequirement, activeCores, availableCores, preferredCoresOrder, P_s)

    print('[Scheduler] [GDP]: GDP determined cores to activate: ', cores_to_activate)

    # write the GDP mapping results to file
    file_gdp_map = open('./system_sim_state/gdp_map.txt', 'w')
    for core in cores_to_activate:
        file_gdp_map.write(str(int(core)) + ' ')
    file_gdp_map.close()

    # -------------------------------------------------------------------------------------------------
    # draw the GDP mapping figure to file
    side_length = int(core_num ** 0.5)
    # create a 2D network
    grid = np.zeros((side_length, side_length), dtype=int)

    # set the position corresponding to the core number to 1
    for num in cores_to_activate:
        row = num // side_length
        col = num % side_length
        grid[int(row), int(col)] = 1

    # draw figure
    fig, ax = plt.subplots()
    ax.imshow(grid, cmap='binary_r', vmin=0, vmax=1)

    # add text labels to each grid
    for i in range(side_length):
        for j in range(side_length):
            # ax.text(j, i, f'#{str(i * side_length + j)}', ha="center", va="center", color="grey")
            ax.text(j, i, '#%s' % str(i * side_length + j), ha="center", va="center", color="grey")

    # draw grid lines
    ax.set_xticks(np.arange(-.5, side_length, 1), minor=True)
    ax.set_yticks(np.arange(-.5, side_length, 1), minor=True)
    ax.grid(which='minor', color='black', linestyle='-', linewidth=2)

    # hide horizontal and vertical coordinates
    ax.set_xticks([])
    ax.set_yticks([])

    # add core activing sequence as title
    plt.title(cores_to_activate)

    # in order to prevent the core_mapping image from being overwritten when the batch is running, use the suffix plus time to save the image
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d_%H-%M-%S")

    # save picture
    # specify the save path and file name (including the current time)
    save_path = "../benchmarks/system_sim_state/core_mapping_figure/"
    file_name = "core_mapping_{}.png".format(formatted_time)
    # file_name = "core_mapping.png"
    file_path = save_path + file_name
    plt.savefig(file_path)
    # -----------------------------------------------------------------------------------------------------------------

execute_gdp_mapping(sys.argv[1])
