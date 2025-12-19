#include "graph.h"
#include <stdio.h>

void initGraph(Graph *g) {
    g->n = 3; // example
    // initialize adjacency matrix
    g->dist[0][1] = 12;
    g->dist[0][2] = 15;
    g->dist[1][2] = 20;
}

int shortestPathDistance(Graph *g, int start, int end) {
    // temporarily return pre-defined distances for simulation
    return g->dist[start][end];
}
