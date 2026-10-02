---
id: backtracking
tier: B
required_elements: [state-definition, dedup, termination, iteration-order]
---

# Backtracking

## Discriminator

Does the answer require the candidate solutions themselves rather than a count or an optimum, and does every partial candidate extend by choosing one item from a shrinking set of options?

Needing the objects is what rules out dynamic programming, which compresses many paths into one number and cannot then reconstruct them all. The second half rules in permutations, subsets, board placements, and grid word searches. When the question asks only how many, or only the best, check first whether overlapping subproblems make dp exponentially cheaper.

## Confusable with

| Looks like | Actually | Tell them apart by |
|---|---|---|
| Graph DFS | Both recurse and mark state | Backtracking unmarks on the way out, because the same element belongs to other candidates; a graph walk marks permanently. |
| dp-1d or dp-2d | Both explore choices | If distinct partial paths reaching the same state are interchangeable for the final answer, memoise. If the path itself is the answer, enumerate. |
| Iterative subset construction | Both generate all subsets | Bitmask iteration is flatter and faster when `n <= 20` and no pruning applies; backtracking wins when constraints prune whole subtrees. |

## Required elements

| element | what a complete statement sounds like | what a vague statement sounds like |
|---|---|---|
| `state-definition` | "`path` is the list of items chosen so far in order, and `start` is the index in the sorted candidate list below which no item may be reused." | "I build up a partial solution and pass it down the recursion." |
| `dedup` | "Candidates are sorted, and inside the loop I skip `items[i]` when `i > start and items[i] == items[i-1]`, which suppresses duplicate siblings while still allowing repeats along a single path." | "I use a set to avoid duplicates." |
| `termination` | "Recursion stops when `len(path) == k`, which appends a copy and returns; it also stops when the remaining candidates cannot reach `k`, so depth never exceeds `k`." | "It returns when the solution is complete." |
| `iteration-order` | "At each level the loop runs `i` from `start` to `n - 1`; the choose-recurse-undo triple must restore `path` to its pre-call contents before the next `i`." | "I loop through the options and recurse on each one." |

## Complexity

Output-sensitive: O(number of solutions * cost to copy one), commonly quoted as O(k * C(n, k)) for combinations, O(n * n!) for permutations, and O(n * 2^n) for subsets. Recursion depth is O(k) and the path costs O(k) space beyond the output. Pruning changes the constant and often the exponent in practice, never the worst-case bound.

## Failure modes

- Appending `path` itself to the results rather than a copy, so every stored solution mutates as the recursion continues. `state-definition`
- Undoing only some of the state changed at a level, for example popping the path but leaving a used flag set. `iteration-order`
- Deduplicating with a set over the finished results, which is correct but costs the full exponential enumeration the sibling-skip would have pruned. `dedup`
- Starting the inner loop at 0 when items may not be reused, generating every permutation of each combination. `iteration-order`
- No prune on infeasible prefixes, so the recursion explores subtrees that provably contain no solution. `termination`

## Template

```python
def enumerate_choices(items, k):
    items.sort()
    results = []
    path = []

    def recurse(start):
        if len(path) == k:
            results.append(path[:])
            return
        for i in range(start, len(items)):
            if i > start and items[i] == items[i - 1]:
                continue
            if len(path) + (len(items) - i) < k:
                break
            path.append(items[i])
            recurse(i + 1)
            path.pop()

    recurse(0)
    return results
```
