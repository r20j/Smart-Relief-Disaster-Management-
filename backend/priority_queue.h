#ifndef PRIORITY_QUEUE_H
#define PRIORITY_QUEUE_H

#define PQ_MAX 100  // change from MAX to PQ_MAX

typedef struct {
    int index;
    int priority;
} PQItem;

typedef struct {
    PQItem items[PQ_MAX];
    int size;
} PriorityQueue;

// Function declarations
void initQueue(PriorityQueue *pq);
int isEmpty(PriorityQueue *pq);
void insert(PriorityQueue *pq, int index, int priority);
PQItem extractMax(PriorityQueue *pq);

#endif
