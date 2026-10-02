---
id: graph-dfs
tier: A
required_elements: [state-definition, dedup, termination, complexity-target]
---

# Graph DFS

## Discriminator

Does the answer for a node require the answers for everything reachable below it to be complete first, or does it require only that the reachable set be enumerated at all?

Both readings select depth-first. The first covers subtree aggregation, where a value must come back up the recursion. The second covers connectivity questions where any traversal order works and depth-first is simply the cheapest to write. It rules out shortest-path-by-edge-count, where finishing order carries no distance information. Cycle detection in a directed graph also lands here, because it needs the on-current-path state that only a depth-first walk maintains.

## Confusable with

| Looks like | Actually | Tell them apart by |
|---|---|---|
| Graph BFS | Both flood the reachable set | For pure connectivity or component counting either works; pick BFS when recursion depth could reach `V` and blow the stack. |
| Backtracking | Both recurse and undo | Depth-first marks a node visited permanently; backtracking unmarks on the way out because the same node may appear in another candidate solution. |
| Union-find | Both count connected components | If edges arrive one at a time and components must be queried between arrivals, union-find is incremental and depth-first is not. |

## Required elements

| element | what a complete statement sounds like | what a vague statement sounds like |
|---|---|---|
| `state-definition` | "`state[node]` is one of unvisited, on-stack, or done; `on-stack` means the node is an ancestor of the current call, which is what a back edge into it proves." | "I keep track of which nodes I have visited." |
| `dedup` | "A node moves to `done` when its call returns and is never re-entered, so each node is expanded exactly once even when several ancestors point at it." | "I skip nodes that are already in the visited set." |
| `termination` | "Every call either returns immediately on a non-unvisited node or marks its node on-stack before recursing, so the recursion depth is bounded by `V` and no node can be re-entered from its own subtree." | "The recursion stops when there are no unvisited neighbours." |
| `complexity-target` | "O(V + E) time, O(V) space for the state array plus recursion depth up to `V`, which is why I would rewrite it with an explicit stack for `V` above 10^5. Brute force over all paths is exponential." | "It visits every node so it is linear." |

## Complexity

O(V + E) time and O(V) space. Recursive form costs O(V) stack in the worst case, so an explicit stack is required when depth can approach the interpreter's limit. Path enumeration without memoisation is exponential.

## Failure modes

- Using a single boolean visited flag for directed cycle detection, which cannot distinguish a back edge from a cross edge into a finished node and reports cycles that do not exist. `state-definition`
- Recursing without checking the state at the top of the call, so a node with many parents is expanded once per parent. `dedup`
- Forgetting to clear the on-stack mark when the call returns, so unrelated later branches look like ancestors. `termination`
- Recursing on a path-shaped graph of 10^5 nodes and hitting the default recursion limit. `complexity-target`
- Mutating the graph while iterating a node's adjacency list, which skips neighbours. `state-definition`

## Template

```python
def explore(start, neighbours):
    state = {}
    order = []

    def visit(node):
        state[node] = "on-stack"
        for nxt in neighbours(node):
            if state.get(nxt) == "on-stack":
                raise ValueError("cycle")
            if nxt not in state:
                visit(nxt)
        state[node] = "done"
        order.append(node)

    visit(start)
    return order
```
