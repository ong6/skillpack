---
id: graph-bfs
tier: A
required_elements: [state-definition, dedup, iteration-order, termination]
---

# Graph BFS

## Discriminator

Does the answer depend on the fewest edges to reach something, on a graph where every edge costs the same?

Uniform edge cost is the discriminating half. Once weights differ, the frontier-by-frontier expansion no longer visits nodes in distance order and you need Dijkstra, or a deque when the only weights are 0 and 1. It rules in shortest path on grids and unweighted graphs, level-by-level processing of a tree, and simultaneous spread from many sources. It rules out longest-path and count-all-paths questions, where marking a node visited once destroys the answer.

## Confusable with

| Looks like | Actually | Tell them apart by |
|---|---|---|
| Graph DFS | Both traverse the whole reachable set | If the question says shortest, fewest, or minimum number of steps, depth-first order gives no such guarantee. |
| Dijkstra | Both expand outward from a source | Check whether every edge has the same cost. If yes, the queue can be a plain FIFO and there is no need for a heap. |
| Topological sort | Both use a queue over a graph | Kahn's algorithm dequeues on in-degree reaching zero, not on distance, and it needs a directed acyclic graph. |

## Required elements

| element | what a complete statement sounds like | what a vague statement sounds like |
|---|---|---|
| `state-definition` | "A FIFO queue seeded with `(start, 0)`, and `dist` mapping each node to the number of edges on the shortest path found to it." | "I keep a queue of nodes to process and a visited set." |
| `dedup` | "A node is marked visited at enqueue time, not dequeue time, so it can never enter the queue twice and the queue holds at most `V` entries." | "I check whether I have already seen the node." |
| `iteration-order` | "Strict FIFO, so all nodes at distance `d` are dequeued before any at `d + 1`; the first time a node is dequeued its distance is final." | "I process nodes in the order they come off the queue." |
| `termination` | "The loop ends when the queue empties, which happens after at most `V` dequeues since each node is enqueued once and every edge is examined once, giving O(V + E)." | "It ends when there is nothing left to visit." |

## Complexity

O(V + E) time and O(V) space for the queue and the visited set. On an `r` by `c` grid that is O(r*c) with four or eight neighbour probes per cell. The brute force enumerates paths and is exponential.

## Failure modes

- Marking visited on dequeue instead of enqueue, which lets a node sit in the queue several times and blows the space bound on dense graphs. `dedup`
- Using a list with `pop(0)` as the queue, which is O(V) per removal and turns the traversal quadratic. `state-definition`
- Losing the level boundary by not snapshotting the queue length before draining a level, so per-level answers mix two distances. `iteration-order`
- Enqueuing all sources for a multi-source problem but seeding distances from only one, which reports distances relative to the wrong origin. `state-definition`
- Applying it to a weighted graph and reporting the first arrival as the minimum cost. `iteration-order`

## Template

```python
from collections import deque

def shortest_steps(start, goal, neighbours):
    queue = deque([start])
    dist = {start: 0}
    while queue:
        node = queue.popleft()
        if node == goal:
            return dist[node]
        for nxt in neighbours(node):
            if nxt not in dist:
                dist[nxt] = dist[node] + 1
                queue.append(nxt)
    return -1
```
