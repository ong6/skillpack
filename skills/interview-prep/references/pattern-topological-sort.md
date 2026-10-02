---
id: topological-sort
tier: B
required_elements: [state-definition, invariant, iteration-order, termination]
---

# Topological sort

## Discriminator

Are the constraints all of the form "A must come before B", with no other cost, so that any ordering respecting every such pair is an acceptable answer?

The signal is a directed edge meaning precedence rather than distance. It rules in build and course ordering, dependency resolution, and the detection of impossible requirement sets, since a cycle is exactly what makes the constraints unsatisfiable. It rules out problems that additionally minimise something, such as total completion time, which needs scheduling theory, and undirected relations, which have no direction to respect.

## Confusable with

| Looks like | Actually | Tell them apart by |
|---|---|---|
| Graph BFS | Kahn's algorithm uses a queue | Nodes enter the queue when in-degree hits zero, not when first reached, so a node with two prerequisites waits for both. |
| Graph DFS | The reverse of the finishing order is a valid topological order | Either works; Kahn's variant detects the cycle by counting output nodes, which is easier to state than the on-stack rule. |
| dp on a DAG | Both process nodes in dependency order | If each node also accumulates a value from its predecessors, the ordering is the scaffolding and the recurrence is the answer. |

## Required elements

| element | what a complete statement sounds like | what a vague statement sounds like |
|---|---|---|
| `state-definition` | "`indegree[v]` counts prerequisites of `v` not yet placed; the queue holds exactly the nodes whose `indegree` has reached 0 and that have not been emitted." | "I count incoming edges and use a queue." |
| `invariant` | "Every node in `order` has all of its predecessors already in `order`, and every node in the queue has zero unmet prerequisites." | "The order respects the dependencies." |
| `iteration-order` | "Pop any zero-in-degree node, append it to `order`, then decrement each successor's in-degree; a successor is enqueued at the moment its count reaches 0, never before." | "I take nodes off the queue and process their neighbours." |
| `termination` | "The loop ends when the queue empties. If `len(order) < V`, the remaining nodes each still have a live prerequisite, which means a cycle, and I return the empty result." | "It stops when I have processed everything." |

## Complexity

O(V + E) time and O(V) space for the in-degree table and the queue. The brute force tries permutations and checks each against the constraints, at O(V! * E).

## Failure modes

- Counting out-degree rather than in-degree, which produces an order that is exactly reversed. `state-definition`
- Enqueuing a successor on every decrement rather than only when the count reaches zero, so a node with two prerequisites is emitted before the second one is placed. `iteration-order`
- Treating an empty queue as success without comparing `len(order)` to `V`, so a graph with a cycle returns a silently partial order. `termination`
- Building the adjacency in the opposite direction from the problem's stated pair convention, which inverts every constraint. `state-definition`
- Failing to seed the queue with every zero-in-degree node, which drops whole disconnected components. `invariant`

## Template

```python
from collections import deque

def topological_order(num_nodes, edges):
    adjacency = [[] for _ in range(num_nodes)]
    indegree = [0] * num_nodes
    for before, after in edges:
        adjacency[before].append(after)
        indegree[after] += 1
    queue = deque(v for v in range(num_nodes) if indegree[v] == 0)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for nxt in adjacency[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    return order if len(order) == num_nodes else []
```
