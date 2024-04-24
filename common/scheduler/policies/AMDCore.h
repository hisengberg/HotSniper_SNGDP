/**
 * This header implements the "map to cores that AMD value is small" policy
 */

#ifndef __AMDCore_H
#define __AMDCore_H

#include "mappingpolicy.h"

class AMDCore : public MappingPolicy
{
    friend class Core;
public:
    // Constructor(有参构造函数)
    AMDCore(unsigned int coreRows, unsigned int coreColumns, std::vector<int> preferredCoresOrder);

    virtual std::vector<int> map(String taskName, 
                                int taskCoreRequirement, 
                                const std::vector<bool> &availableCores, 
                                const std::vector<bool> &activeCores);

private:
    unsigned int m_coreRows;
    unsigned int m_coreColumns;
    std::vector<int> m_preferredCoresOrder;

public:
    // static:静态成员函数
    static bool cmp(const std::pair<int, double> &p1, const std::pair<int, double> &p2);

};


#endif