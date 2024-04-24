#include "dvfsTSP.h"
#include "powermodel.h"
#include <iomanip>
#include <iostream>
// for testing runtime overhead
#include <chrono>

using namespace std;

DVFSTSP::DVFSTSP(ThermalModel *thermalModel, const PerformanceCounters *performanceCounters, int coreRows, int coreColumns, int minFrequency, int maxFrequency, int frequencyStepSize)
	: thermalModel(thermalModel), performanceCounters(performanceCounters), coreRows(coreRows), coreColumns(coreColumns), minFrequency(minFrequency), maxFrequency(maxFrequency), frequencyStepSize(frequencyStepSize){
	
}

std::vector<int> DVFSTSP::getFrequencies(const std::vector<int> &oldFrequencies, const std::vector<bool> &activeCores) {

	// record start time
	auto start_time = std::chrono::high_resolution_clock::now();

	std::vector<int> frequencies(coreRows * coreColumns);

	float tsp = thermalModel->tsp(activeCores);

	for (unsigned int coreCounter = 0; coreCounter < coreRows * coreColumns; coreCounter++) {
		if (activeCores.at(coreCounter)) {
			float power = performanceCounters->getPowerOfCore(coreCounter);
			float temperature = performanceCounters->getTemperatureOfCore(coreCounter);
			int frequency = oldFrequencies.at(coreCounter);
			float utilization = performanceCounters->getUtilizationOfCore(coreCounter);

			cout << "[Scheduler][DVFS_TSP]: Core " << setw(2) << coreCounter << ":";
			cout << " P=" << fixed << setprecision(3) << power << " W";
			cout << " (budget: " << fixed << setprecision(3) << tsp << " W)";
			cout << " f=" << frequency << " MHz";
			cout << " T=" << fixed << setprecision(1) << temperature << " °C";
			cout << " utilization=" << fixed << setprecision(3) << utilization << endl;

			int expectedGoodFrequency = PowerModel::getExpectedGoodFrequency(frequency, power, tsp, minFrequency, maxFrequency, frequencyStepSize);
			frequencies.at(coreCounter) = expectedGoodFrequency;
		} else {
			frequencies.at(coreCounter) = minFrequency;
		}
	}

	// record end time
	auto end_time = std::chrono::high_resolution_clock::now();

	// record runtime overhead
	auto runtime_overhead = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time);

	cout << "================================================================" << endl;
	cout << "TSP power budgeting runtime overhead :" << runtime_overhead.count() << " us" << endl;
	cout << "================================================================" << endl;

	return frequencies;
}
