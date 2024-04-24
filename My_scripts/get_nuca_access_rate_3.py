import re
import os
import math
import matplotlib.pyplot as plt
import numpy as np


# Extract data from 'sim.out' file
def get_rc():
    # nuca access rate = total nuca access number / total core instructions
    # Data preparation stage
    path = '../My_results/result_2(LLC size=2MB)/x264/'
    dirs = [dir_name for dir_name in os.listdir(path) if os.path.isdir(os.path.join(path, dir_name))]
    # dirs = sorted(dirs, key=lambda x: x.split('parsec-')[1])  # Sort the 'dirs' files according to the alphabetical order of the benchmark
    # Sort 'dirs' names according to running time and AMDmax value
    sorted_dirs = sorted(dirs, key=lambda x: (x.split('_')[1], float(x.split('_AMDmax=')[-1].split('_')[0]) if 'AMDmax' in x else float('inf')))
    print(sorted_dirs, f'\n')

    benchmark_name_list = []  # Store the benchmark name of each file
    nuca_access_rate_list = []  # Store the nuca_access_rate_list of each file

    for dir_name in sorted_dirs:
        # Separate the path and file name for storage
        print(dir_name)
        directory = f'{path}/{dir_name}/'
        filename = 'sim.out'
        file_path = os.path.join(directory, filename)
        with open(file_path, 'r', encoding='UTF-8') as f:
            # Separate the path and file name for storage
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

                # If the current line starts with "Instructions", read it
                if line.startswith("Instructions"):
                    str_data_list = re.findall(r'\d+', line)  # Extract data
                    # Convert all elements in the string list to integer form
                    int_total_core_instructions_data_list = list(map(int, str_data_list))

        print(int_data_list)
        print(int_total_core_instructions_data_list)

        total_nuca_accesses = sum(int_data_list)
        total_core_instructions = sum(int_total_core_instructions_data_list)

        nuca_access_rate = total_nuca_accesses / total_core_instructions

        nuca_access_rate_list.append(nuca_access_rate)  # Add nuca_access_rate to the list
        print()

        # Extract the benchmark name, for example, parsec-x264-simsmall-8
        benchmark_name = dir_name.split('+')[-1].split('_')[-1]
        benchmark_name_list.append(benchmark_name)

    print(f"benchmark_name：{benchmark_name_list}")
    print(f"nuca_access_rate：{nuca_access_rate_list}")
    print()

    # Convert the list to an array
    nuca_access_rate_array = np.array(nuca_access_rate_list)
    # Calculate the mean and standard deviation
    average_rc = np.mean(nuca_access_rate_array)
    average_rc = average_rc * 100  # Display the average in percentage form
    print("average_rc =", average_rc, "%")
    std_deviation_rc = np.std(nuca_access_rate_array)
    print("std_deviation_rc =", std_deviation_rc)
    print()

    return benchmark_name_list, nuca_access_rate_list, path, average_rc, std_deviation_rc


def plot_bar_chart():
    benchmark_name_list, nuca_access_rate_list, path, average_rc, std_deviation_rc = get_rc()

    # Set the size of the figure and font size
    plt.figure(figsize=(10, 7))
    plt.rcParams.update({'font.size': 12})  # Set the font size to 12

    # Draw the bar chart
    plt.bar(benchmark_name_list, nuca_access_rate_list)

    # Set the title, x-axis name, and y-axis name
    plt.title('NUCA Accesses Rate of Each Benchmark')
    plt.xlabel('Benchmark Name')
    plt.ylabel('NUCA Accesses Rate')

    # Add annotations to show the average_rc and standard deviation in the graph
    plt.text(0.5, 1.08, f'average_rc = {average_rc}%\nstd_deviation_rc = {std_deviation_rc}', ha='center', va='bottom', transform=plt.gca().transAxes)

    plt.xticks(rotation=25)  # Rotate the x-axis by 90 degrees to prevent text overlap
    plt.xticks(fontsize=9)  # Set the font size of x-axis labels to 10

    # Adjust the margin of the subplot
    plt.subplots_adjust(bottom=0.30)

    # Save the generated image to the specified path
    save_path = path  # Set the custom path
    save_name = 'NUCA Accesses Rate of Each Benchmark.png'  # Set the custom name
    # plt.savefig(save_path + save_name)

    # Show the image
    plt.show()


def get_nuca_accesses_info():
    benchmark_name_list, nuca_access_rate_list, path, average_rc, std_deviation_rc = get_rc()

    save_path = path  # Set the file save path
    save_name = '3_nuca_accesses_rate_info.txt'  # Set the save file name
    file = open(save_path+save_name, "w")
    file.write(f'{str(benchmark_name_list)}\n')
    file.write(f'{str(nuca_access_rate_list)}\n')
    file.write(f'average_rc = {average_rc} %\n')
    file.write(f'std_deviation_rc = {std_deviation_rc}')
    file.close()


if __name__ == '__main__':
    get_rc()
    plot_bar_chart()
    get_nuca_accesses_info()
