#include "mapSNGDP.h"
#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <fstream>

using namespace std;

// Just do initiation. Note that unlike the firstunused method, preferredCoresOrder do not contain the cores not specified by user, because their order should be computed at runtime by MapSNGDP::map
MapSNGDP::MapSNGDP(unsigned int coreRows, unsigned int coreColumns, std::vector<int> preferredCoresOrder)
			: coreRows(coreRows), coreColumns(coreColumns), preferredCoresOrder(preferredCoresOrder) 
{
	for (unsigned int i = 0; i < coreRows * coreColumns; i++) {
		if (std::find(this->preferredCoresOrder.begin(), this->preferredCoresOrder.end(), i) == this->preferredCoresOrder.end()) {
			this->preferredCoresOrder.push_back(-1); // put "-1", meaning the order has not been determined yet, should be determined by MapSNGDP::map
		}
	}
}


std::vector<int> MapSNGDP::map(String taskName, int taskCoreRequirement, const std::vector<bool> &availableCores, const std::vector<bool> &activeCores) {
	std::vector<int> cores;

	/* SNGDP mapping core code begin */

	// write availableCores and activeCores in info_for_mapping.txt as inputs to sngdp_mapping.py
	ofstream mapping_info_file("./system_sim_state/info_for_mapping.txt");
	for (unsigned int i = 0; i < availableCores.size(); i++){
	  mapping_info_file << availableCores[i] << "\t";
	}
	mapping_info_file << endl;
	for (unsigned int i=0; i<activeCores.size();i++){
	  mapping_info_file << activeCores[i] << "\t";
	}
	mapping_info_file << endl;
	for (unsigned int i=0; i<preferredCoresOrder.size();i++){
	    mapping_info_file << preferredCoresOrder[i] << "\t";
	}
	mapping_info_file << endl;

	// execute execute_sngdp_mapping.py to compute the active core mapping, the outputs are written in file sngdp_map.txt
	string filename = "../common/scheduler/policies/execute_sngdp_mapping.py "+to_string(taskCoreRequirement);
	string command = "python3 "+filename;
	system(command.c_str());

	// load the sngdp mapping from file, and activate the cores according to the sngdp mapping
	int core_to_activate;
	ifstream file_sngdp_map("./system_sim_state/sngdp_map.txt");  // read files and create stream objects.
	for (int coreCounter = 0; coreCounter < taskCoreRequirement; coreCounter++)
	{
		file_sngdp_map >> core_to_activate;
		cores.push_back(core_to_activate);
	}
	file_sngdp_map.close();
	return cores;

	/* SNGDP mapping core code end */

	std::vector<int> empty;
	return empty;
}
