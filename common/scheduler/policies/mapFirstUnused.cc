#include "mapFirstUnused.h"
#include <algorithm>
#include <iostream>
#include <map>
#include <set>

MapFirstUnused::MapFirstUnused(
	unsigned int coreRows, 
	unsigned int coreColumns, 
	std::vector<int> preferredCoresOrder)
	: coreRows(coreRows),
	coreColumns(coreColumns),
	preferredCoresOrder(preferredCoresOrder) 
{
	// 按core_id的顺序依次开核
	// for (unsigned int i = 0; i < coreRows * coreColumns; i++)
	// {
	// 	if (std::find(this->preferredCoresOrder.begin(), this->preferredCoresOrder.end(), i) == this->preferredCoresOrder.end()) 
	// 	{
	// 		this->preferredCoresOrder.push_back(i);
	// 	}
	// }
	this->preferredCoresOrder = {18,21,42,45,19,20,26,29,34,37,43,44,27,28,35,36};
}

std::vector<int> MapFirstUnused::map(String taskName, 
									int taskCoreRequirement, 
									const std::vector<bool> &availableCores, 
									const std::vector<bool> &activeCores)
{
	std::vector<int> cores;

	/* the test for confirming whether the preferredCoresOrder is right */ 
	std::cout << "\nThe preferred Cores Order is : ";
	for (std::vector<int>::iterator it = preferredCoresOrder.begin(); it != preferredCoresOrder.end(); it++)
    {
        std::cout << *it << " ";
    }
    std::cout << std::endl;
	/* end of test */

	// try to fill with preferred cores
	for (const int &c : preferredCoresOrder)
	{
		if (availableCores.at(c)) 
		{
			cores.push_back(c);
			if ((int)cores.size() == taskCoreRequirement)
			{
				return cores;
			}
		}
	}

	std::vector<int> empty;
	return empty;
}