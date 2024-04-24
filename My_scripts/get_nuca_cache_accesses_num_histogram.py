import re
import os
import math
import matplotlib.pyplot as plt
import numpy as np


def get_num_cache_accesses_histogram():
    # Preparation stage for data
    path = "../My_results/LLC_latency_impact_3-1/"
    dirs = [dir_name for dir_name in os.listdir(path) if os.path.isdir(os.path.join(path, dir_name))]
    for dir_name in dirs:
        # Separate path and filename
        print(dir_name)
        directory = f'{path}/{dir_name}/'
        filename = 'sim.out'
        file_path = os.path.join(directory, filename)
        with open(file_path, 'r', encoding='UTF-8') as f:
            # Traverse each line in the file
            for line in f:
                line = line.lstrip()  # Remove all leading whitespace characters (including spaces, tabs, newlines, etc.) from each line of the string, and return the modified string
                # If the current line starts with "NUCA cache", then read the next line
                if line.startswith("NUCA cache"):
                    targe_line = next(f).strip()  # Read the next line and remove whitespace characters
                    # Further confirm the specific line to be extracted
                    if targe_line.startswith("num cache accesses"):
                        str_data_list = re.findall(r'\d+', targe_line)
                        # Convert all elements in the string list to integers
                        int_data_list = list(map(int, str_data_list))
                        break
        print(int_data_list)
        total_accesses = sum(int_data_list)
        print(f"Total number of accesses: {total_accesses}\n")
        data_counts = len(int_data_list)

        x_values = list(range(data_counts))
        y_values = int_data_list

        # Generate a bar chart
        plt.bar(x_values, y_values)

        # Add x-axis ticks and labels
        # plt.xticks(x_values)
        plt.xlabel('Core ID')

        # Add y-axis ticks and labels
        # y_ticks = [2*10**5, 4*10**5, 6*10**5, 8*10**5, 1*10**6]
        # y_labels = ['$2·10^5$', '$4·10^5$', '$6·10^5$', '$8·10^5$', '$1·10^6$']
        # plt.yticks(y_ticks, y_labels)

        plt.ylabel('Number of NUCA Cache Accesses')

        # Add annotations
        plt.title(f'Total NUCA Cache Accesses: {total_accesses}')

        # Save the generated figure to the specified path
        save_path = directory  # Set custom path
        save_name = 'NUCA_cache accesses histogram.png'  # Set custom name
        # plt.savefig(save_path + save_name)

        # Save as EPS file
        eps_name = 'distribution_of_nuca_cache_accesses.eps'
        # plt.savefig(save_path + eps_name, format='eps', bbox_inches='tight', dpi=300)  # EPS file for LaTeX

        # Adjust subplot margins
        plt.subplots_adjust(left=0.15, bottom=0.1)

        # Show figure
        plt.show()


if __name__ == '__main__':
    get_num_cache_accesses_histogram()
