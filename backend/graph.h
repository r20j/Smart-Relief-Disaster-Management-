// graph.h
#ifndef GRAPH_H
#define GRAPH_H

#define GRAPH_MAX 10

typedef struct {
    int n;
    int dist[GRAPH_MAX][GRAPH_MAX];
    char names[GRAPH_MAX][50];
} Graph;

// Function declarations
void initGraph(Graph *g);
int shortestPathDistance(Graph *g, int start, int end);
void dijkstra(Graph *g, int start, int target);

#endif
