#ifndef DISASTER_H
#define DISASTER_H

#include "graph.h"
#include "priority_queue.h"

typedef struct {
    char name[50];
    int severity;
    int served;
    int distance;
} Area;

void runDisasterSimulation();

#endif
