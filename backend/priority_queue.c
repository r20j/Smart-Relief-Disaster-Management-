#include "priority_queue.h"

void initQueue(PriorityQueue *pq) {
    pq->size = 0;
}

int isEmpty(PriorityQueue *pq) {
    return pq->size == 0;
}

void insert(PriorityQueue *pq, int index, int priority) {
    PQItem item = {index, priority};
    int i = pq->size++;
    pq->items[i] = item;

    // Heapify up
    while(i != 0) {
        int parent = (i-1)/2;
        if(pq->items[parent].priority >= pq->items[i].priority) break;
        PQItem tmp = pq->items[parent];
        pq->items[parent] = pq->items[i];
        pq->items[i] = tmp;
        i = parent;
    }
}

PQItem extractMax(PriorityQueue *pq) {
    PQItem root = pq->items[0];
    pq->items[0] = pq->items[--pq->size];

    // Heapify down
    int i = 0;
    while(1) {
        int left = 2*i + 1;
        int right = 2*i + 2;
        int largest = i;

        if(left < pq->size && pq->items[left].priority > pq->items[largest].priority)
            largest = left;
        if(right < pq->size && pq->items[right].priority > pq->items[largest].priority)
            largest = right;

        if(largest == i) break;

        PQItem tmp = pq->items[i];
        pq->items[i] = pq->items[largest];
        pq->items[largest] = tmp;
        i = largest;
    }
    return root;
}
