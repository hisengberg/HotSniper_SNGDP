/**
 * This header implements the "map to first unused core" policy
 */

#ifndef __MAP_SNGDP_H
#define __MAP_SNGDP_H

#include "mappingpolicy.h"

class MapSNGDP : public MappingPolicy {
public:
    MapSNGDP(unsigned int coreRows, unsigned int coreColumns, std::vector<int> preferredCoresOrder);
    virtual std::vector<int> map(String taskName, 
                                 int taskCoreRequirement, 
                                 const std::vector<bool> &availableCores, 
                                 const std::vector<bool> &activeCores);

private:
    unsigned int coreRows;
    unsigned int coreColumns;
    std::vector<int> preferredCoresOrder;
};

#endif
