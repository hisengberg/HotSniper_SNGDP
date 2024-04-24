import os
from tabulate import tabulate
from resultlib import *


def main():
    headers = [
        'date',
        'config',
        'tasks',
        'sim. time (ns)',
        # 'avg resp time (ns)',
        # 'resp times (ns)',
        # 'peak power / thread (W)',
        # 'avg power (W)',
        # 'energy (J)',
    ]
    rows = []
    runs = sorted(list(get_runs()))
    for run in runs:
        if has_properly_finished(run):
            config = get_config(run)
            # energy = get_energy(run)
            tasks = get_tasks(run)
            if len(tasks) > 40:
                tasks = tasks[:37] + '...'
            rows.append([
                get_date(run),
                config,
                tasks,
                '{:,}'.format(get_total_simulation_time(run)),                              # 'sim. time (ns)'
                # '{:,}'.format(get_average_response_time(run)),                              # 'avg resp time (ns)'
                # '  '.join('{:,}'.format(r) for r in get_individual_response_times(run)),    # 'resp times (ns)'
                # '{:.2f}'.format(get_peak_power_consumption_single_thread(run)),           # 'peak power / thread (W)'
                # '{:.2f}'.format(get_average_power_consumption(run)),                      # 'avg power (W)'
                # '{:.2f}'.format(energy) if energy != '-' else '-',                        # 'energy (J)'
            ])
    print(tabulate(rows, headers=headers))


if __name__ == '__main__':
    main()
