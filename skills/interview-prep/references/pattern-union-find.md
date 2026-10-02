---
id: union-find
tier: B
required_elements: [state-definition, invariant, transition, complexity-target]
---

# Union-find

## Discriminator

Is the relation being tracked an equivalence — reflexive, symmetric, transitive — that only ever gains members, with membership queries interleaved between the additions?

Monotone growth is the constraint that makes the structure applicable, because there is no efficient way to split a set back apart. It rules in incremental connectivity, detecting the edge that closes a cycle in an undirected graph, and grouping items by chained equalities. It rules out anything with edge deletion, and anything directed, since "A points to B" is not symmetric.

## Confusable with

| Looks like | Actually | Tell them apart by |
|---|---|---|
| Graph DFS | Both find connected components | If the whole edge list is available up front and no query happens mid-stream, one depth-first pass is O(V + E) and simpler. |
| Hashing into groups | Both bucket items | A hash key is computed from one item alone; union-find groups items whose relation is only known pairwise and transitively. |
| Topological sort | Both process edges to reveal structure | Union-find ignores direction entirely. If reversing an edge would change the answer, it is the wrong structure. |

## Required elements

| element | what a complete statement sounds like | what a vague statement sounds like |
|---|---|---|
| `state-definition` | "`parent[i]` is `i`'s representative, with `parent[i] == i` marking a root; `size[r]` counts members of the tree rooted at `r`, valid only for roots." | "I keep an array pointing each node at its parent." |
| `invariant` | "Two elements are in the same set exactly when `find` returns the same root for both, and every element reaches its root by following `parent` in finitely many steps." | "The array tells me which group each element is in." |
| `transition` | "`union(a, b)` resolves both roots; if they differ, the smaller tree's root gets `parent[small] = large` and `size[large] += size[small]`, and the component count drops by one." | "I join the two sets together." |
| `complexity-target` | "Near-constant amortised per operation with path compression and union by size, so `m` operations cost O(m * alpha(n)); O(n) space. Re-running a traversal after each edge would be O(m * (V + E))." | "It is basically constant time." |

## Complexity

O(alpha(n)) amortised per `find` or `union` with both path compression and union by size or rank, and O(n) space. With neither optimisation a chain of unions degrades `find` to O(n). Recomputing connectivity from scratch after each edge is O(m * (V + E)).

## Failure modes

- Comparing `parent[a] == parent[b]` instead of `find(a) == find(b)`, which is only correct on trees of depth one. `invariant`
- Attaching roots without union by size or rank, producing a linear chain and an O(n) `find`. `complexity-target`
- Reading `size` on a non-root element after a union, where the value is stale. `state-definition`
- Attaching `parent[a] = b` using the raw elements rather than their roots, which merges the wrong subtrees and can create a cycle in the parent array. `transition`
- Decrementing the component count on every `union` call, including calls where both elements already shared a root. `transition`

## Template

```python
class DisjointSet:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.groups = n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.size[ra] > self.size[rb]:
            ra, rb = rb, ra
        self.parent[ra] = rb
        self.size[rb] += self.size[ra]
        self.groups -= 1
        return True
```
