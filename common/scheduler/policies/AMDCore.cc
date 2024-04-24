#include "AMDCore.h"
#include <algorithm>
#include <iostream>
#include <iomanip>
#include <map>
#include <set>
#include <cmath>
#include <iomanip>
#include <vector>
#include <functional>  // the result of google


AMDCore::AMDCore(unsigned int coreRows, unsigned int coreColumns, std::vector<int> preferredCoresOrder)
	            : m_coreRows(coreRows), m_coreColumns(coreColumns), m_preferredCoresOrder(preferredCoresOrder) 
{
	std::cout << "coreRows = " << m_coreRows << "\tcoreColums = " << m_coreColumns << std::endl;

	std::vector<int> cores;
	// 创建一个CoreIdInfo类，里面存放每个core所对应的坐标信息
	class CoreIdInfo
	{
	public:
		CoreIdInfo(unsigned int x, unsigned int y)
		{
			this->m_core_x = x;
			this->m_core_y = y;
			this->m_core_id = (y-1)*8+(x-1);
		}
	
		unsigned m_core_x;
		unsigned m_core_y;
		unsigned m_core_id;
	};

	std::vector<CoreIdInfo> core_id_info;
	for (unsigned int j = 1; j <= m_coreColumns; j++)  // Y-axis
	{
		for (unsigned int i = 1; i <= m_coreRows; i++)  // X-axis
		{
			CoreIdInfo c_id(i, j);  // 实例化一个类对象
			core_id_info.push_back(c_id);
		}
	}

	// 验证每个core和其所对应的坐标信息是否匹配
	for (std::vector<CoreIdInfo>::iterator it = core_id_info.begin(); it != core_id_info.end(); it++)
	{
		std::cout << "core_id = " << it->m_core_id 
				  << "\tcore_x = " << it->m_core_x 
				  << "\tcore_y = " << it->m_core_y << std::endl;  
	}
	std::cout << std::endl;

	double dist_sum = 0;
	double amd_core = 0;

	std::map<int, double> amdcore;

	// arrange the core according to the AMD value from small to large
	std::vector<std::pair<int, double>> amdcoreup;
	// 计算每个core的AMD值
	for (std::vector<CoreIdInfo>::iterator a = core_id_info.begin(); a != core_id_info.end(); a++)
	{
		for (std::vector<CoreIdInfo>::iterator b = core_id_info.begin(); b != core_id_info.end(); b++)
		{
			// calculate each core's AMD value
			int dist = abs(a->m_core_x - b->m_core_x) + abs(a->m_core_y - b->m_core_y);
			dist_sum += dist;
		}
		amd_core = dist_sum / (m_coreRows * m_coreColumns);
		dist_sum = 0;
	
		amdcore.insert(std::make_pair(a->m_core_id, amd_core));

		amdcoreup.push_back(std::make_pair(a->m_core_id, amd_core));
	}
	std::cout << std::endl;

	// test begin
	std::cout << "AMD value corresponding to each core" << std::endl;
	for (std::map<int, double>::iterator it = amdcore.begin(); it != amdcore.end(); it++)
    {
        std::cout << "core_id = " << it->first << "\t" << "AMD value = " << it->second << std::endl;
    }
    std::cout << std::endl;
	// test end

	sort(amdcoreup.begin(), amdcoreup.end(), cmp);

	// test begin
	std::cout << "sequencing cores using AMD values from small to large:" << std::endl; 
	for (std::vector<std::pair<int, double>>::iterator it = amdcoreup.begin(); it!= amdcoreup.end(); it++)
    {
        std::cout << "core_id = " << it->first << "\t" << "AMD值 = " << it->second << std::endl;
    }
    std::cout << std::endl;
	// test end

	for (std::vector<std::pair<int, double>>::iterator it = amdcoreup.begin(); it != amdcoreup.end(); it++)
	{
		this->m_preferredCoresOrder.push_back(it->first);
	}

}

std::vector<int> AMDCore::map(String taskName,
							  int taskCoreRequirement,
						      const std::vector<bool> &availableCores,
							  const std::vector<bool> &activeCores)
{
	std::vector<int> cores;
	// the test for confirming whether the preferredCoresOrder is right
	std::cout << "\nThe preferred Cores Order is : ";
	for (std::vector<int>::iterator it = m_preferredCoresOrder.begin(); it != m_preferredCoresOrder.end(); it++)
    {
        std::cout << *it << " ";
    }
    std::cout << std::endl;
	// end of test

	// try to fill with preferred cores
	for (const int &c : m_preferredCoresOrder)  // 范围for语句(range for statement)
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

bool AMDCore::cmp(const std::pair<int, double> &p1, const std::pair<int, double> &p2)
{
	return p1.second < p2.second;
}