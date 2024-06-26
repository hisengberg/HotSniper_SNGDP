#include "dvfsFixedPower.h"
#include "powermodel.h"
#include <iomanip>
#include <iostream>

using namespace std;

DVFSFixedPower::DVFSFixedPower(const PerformanceCounters *performanceCounters, int coreRows, int coreColumns, int minFrequency, int maxFrequency, int frequencyStepSize, float perCorePowerBudget)
	: performanceCounters(performanceCounters), coreRows(coreRows), coreColumns(coreColumns), minFrequency(minFrequency), maxFrequency(maxFrequency), frequencyStepSize(frequencyStepSize), perCorePowerBudget(perCorePowerBudget) {
	
}

std::vector<int> DVFSFixedPower::getFrequencies(const std::vector<int> &oldFrequencies, const std::vector<bool> &activeCores) {
	std::vector<int> frequencies(coreRows * coreColumns);

	for (unsigned int coreCounter = 0; coreCounter < coreRows * coreColumns; coreCounter++) {
		if (activeCores.at(coreCounter)) {
			float power = performanceCounters->getPowerOfCore(coreCounter);
			float temperature = performanceCounters->getTemperatureOfCore(coreCounter);
			int frequency = oldFrequencies.at(coreCounter);
			float utilization = performanceCounters->getUtilizationOfCore(coreCounter);

			cout << "[Scheduler][DVFSFixedPower]: Core " << setw(2) << coreCounter << " :";
			cout << " P=" << fixed << setprecision(3) << power << " W";
			cout << " (budget: " << fixed << setprecision(3) << perCorePowerBudget << " W)  ";
			cout << " f=" << frequency << " MHz  ";
			cout << " T=" << fixed << setprecision(1) << temperature << " °C  ";
			cout << " utilization=" << fixed << setprecision(3) << utilization << endl;

			int expectedGoodFrequency = PowerModel::getExpectedGoodFrequency(frequency, power, perCorePowerBudget, minFrequency, maxFrequency, frequencyStepSize);
			frequencies.at(coreCounter) = expectedGoodFrequency;
		} else {
			frequencies.at(coreCounter) = minFrequency;
		}
	}

	return frequencies;
}
