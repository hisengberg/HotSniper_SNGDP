'''
The function of this code is to obtain the 'Total num nuca cache accesses' of each benchmark in a set of experimental data.
That is, the numerator of rc.
'''
import re
import os
import math
import matplotlib.pyplot as plt
import numpy as np


# Extract data from 'sim.out' file
def get_total_num_nuca_cache_accesses():
    # Data preparation stage
    path = '../My_results/result_2(LLC size=2MB)/x264/'
    dirs = [dir_name for dir_name in os.listdir(path) if os.path.isdir(os.path.join(path, dir_name))]
    # print(dirs)
    # dirs = sorted(dirs, key=lambda x: x.split('parsec-')[1])  # Sort the 'dirs' files according to the alphabetical order of the benchmark
    # Sort 'dirs' names according to running time and AMDmax value
    sorted_dirs = sorted(dirs, key=lambda x: (x.split('_')[1], float(x.split('_AMDmax=')[-1].split('_')[0]) if 'AMDmax' in x else float('inf')))
    # print(sorted_dirs, '\n')

    benchmark_name_list = []  # Store the benchmark of each file
    total_nuca_accesses_list = []  # Store the total_real_nuca_accesses of each file

    for dir_name in sorted_dirs:
        # Separate the path and file name for storage
        print(dir_name)
        directory = f'{path}/{dir_name}/'
        filename = 'sim.out'
        file_path = os.path.join(directory, filename)
        with open(file_path, 'r', encoding='UTF-8') as f:
            # Traverse each line in the file
            for line in f:
                line = line.lstrip()  # Remove all leading whitespace characters (including spaces, tabs, newlines, etc.) from each line of the string and return the modified string
                # If the current line starts with "NUCA cache", read the next line
                if line.startswith("NUCA cache"):
                    targe_line = next(f).strip()  # Read the next line and remove whitespace characters
                    # Further confirm the specific line to be extracted
                    if targe_line.startswith("num cache accesses"):
                        str_data_list = re.findall(r'\d+', targe_line)  # Extract data
                        # Convert all elements in the string list to integer form
                        int_data_list = list(map(int, str_data_list))
                        break
        # print(int_data_list)
        total_nuca_accesses = sum(int_data_list)
        total_nuca_accesses_list.append(total_nuca_accesses)    # Add total_nuca_accesses to the list

        # Extract the benchmark name, for example, parsec-x264-simsmall-8
        benchmark_name = dir_name.split('+')[-1].split('_')[-1]
        benchmark_name_list.append(benchmark_name)

        print(benchmark_name_list)
        print(total_nuca_accesses_list)
        print()

    return benchmark_name_list, total_nuca_accesses_list, path

def plot_bar_chart():
    benchmark_name_list, total_nuca_accesses_list, path = get_total_num_nuca_cache_accesses()

    # Set the size of the figure and font size
    plt.figure(figsize=(10, 6))
    plt.rcParams.update({'font.size': 12})  # Set the font size to 12

    # Draw the bar chart
    plt.bar(benchmark_name_list, total_nuca_accesses_list)

    # Set the title, x-axis name, and y-axis name
    plt.title('Total NUCA Accesses of Each Benchmark')
    plt.xlabel('Benchmark Name')
    plt.ylabel('Total NUCA Accesses')

    plt.xticks(rotation=25)  # Rotate the x-axis by 90 degrees to prevent text overlap
    plt.xticks(fontsize=9)  # Set the x-axis label font size to 9

    # Adjust the margin of the subplot
    plt.subplots_adjust(bottom=0.30)

    # Save the generated image to the specified path
    save_path = path  # Set the custom path
    save_name = 'Total NUCA Accesses of Each Benchmark.png'  # Set the custom name
    # plt.savefig(save_path + save_name)

    # Show the image
    plt.show()

def get_nuca_accesses_info():
    benchmark_name_list, total_nuca_accesses_list, path = get_total_num_nuca_cache_accesses()

    save_path = path  # Set the file save path
    save_name = '1_total_nuca_accesses_info.txt'  # Set the save file name
    file = open(save_path+save_name, "w")
    file.write(f'{str(benchmark_name_list)}\n')
    file.write(str(total_nuca_accesses_list))
    file.close()

if __name__ == '__main__':
    get_total_num_nuca_cache_accesses()
    plot_bar_chart()
    get_nuca_accesses_info()
