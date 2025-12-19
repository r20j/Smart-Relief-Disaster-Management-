#include "graph.h"
#include "priority_queue.h"
#include <stdio.h>
#include <string.h>
#include "disaster.h"

void runDisasterSimulation() {
    Graph g;
    initGraph(&g);

    Area areas[3];
    strcpy(areas[0].name, "Area A"); areas[0].severity = 5; areas[0].served = 0;
    strcpy(areas[1].name, "Area B"); areas[1].severity = 10; areas[1].served = 0;
    strcpy(areas[2].name, "Area C"); areas[2].severity = 3; areas[2].served = 0;

    PriorityQueue pq;
    initQueue(&pq);
    for(int i=0;i<3;i++) insert(&pq, i, areas[i].severity);

    printf("=== SMART DISASTER RELIEF RESOURCE ALLOCATOR ===\n\n");
    printf("List of Affected Areas:\n");
    printf("-----------------------------------\n");
    for(int i=0;i<3;i++)
        printf("%d. %-8s | Severity: %-2d | Pending\n", i+1, areas[i].name, areas[i].severity);
    printf("-----------------------------------\n\n");
    printf("Starting Relief Allocation...\n");
    printf("===================================\n\n");

    while(!isEmpty(&pq)) {
        PQItem item = extractMax(&pq);
        int idx = item.index;
        printf(">> Next Priority Area: %s (Severity %d)\n", areas[idx].name, areas[idx].severity);
        printf("   Finding shortest path from Center to %s...\n", areas[idx].name);
        int dist = shortestPathDistance(&g, 0, idx+1);
        areas[idx].distance = dist;
        areas[idx].served = 1;
        printf("   Shortest path distance: %d km\n", dist);
        printf("   Relief Delivered Successfully to %s!\n", areas[idx].name);
        printf("-----------------------------------\n\n");
    }

    printf(" All affected areas have been served successfully! \n\n");
    printf("Summary Report:\n");
    printf("-----------------------------------\n");
    for(int i=0;i<3;i++)
        printf("%-8s → Served   (Severity: %d, Distance: %d km)\n", areas[i].name, areas[i].severity, areas[i].distance);
    printf("-----------------------------------\n\n");
    printf(" Simulation Complete — All Reliefs Delivered Efficiently!\n");
}
