---
id: binary-search-on-answer
tier: A
required_elements: [discriminator, invariant, boundary-update, termination]
---

# Binary search on answer

## Discriminator

Is there a predicate over the candidate range that flips from false to true exactly once, so that testing one candidate tells you which half to discard?

The candidate range need not be an array. It is often a numeric answer such as a capacity, a speed, or a deadline, with a feasibility check that is cheap to evaluate. The predicate must be monotone: if capacity `c` works then every capacity above `c` works. It rules out objectives that are feasible in disconnected intervals, and it rules in the common shape where an O(n) checker turns an unsearchable space into O(n log R).

## Confusable with

| Looks like | Actually | Tell them apart by |
|---|---|---|
| Plain binary search on a sorted array | Halving a range | Ask what the midpoint means. If it is an index into stored data it is array search; if it is a hypothetical answer scored by a checker it is this pattern. |
| Greedy | Both aim at a minimum feasible value | Greedy constructs the answer in one pass; this pattern guesses the answer and verifies it. If you cannot prove a greedy exchange argument, guess and check. |
| Two pointers | Both narrow `lo` and `hi` | The midpoint jump is the tell. Two pointers moves an end by one based on a local comparison. |

## Required elements

| element | what a complete statement sounds like | what a vague statement sounds like |
|---|---|---|
| `discriminator` | "`feasible(c)` is 'the load can be split into at most `k` groups when each group is capped at `c`', and it is monotone: if a cap of 8 works, a cap of 9 works, so the true-region is a suffix of `[max(a), sum(a)]`." | "I can binary search this because the answer space is sorted." |
| `invariant` | "`lo` is always a candidate not yet proven feasible and `hi` is always known feasible, so the smallest feasible value is in `[lo, hi]` at every step." | "The answer stays inside the search range." |
| `boundary-update` | "`mid = lo + (hi - lo) // 2`; feasible sets `hi = mid` keeping `mid` as a live candidate, infeasible sets `lo = mid + 1` discarding it." | "If it works I go left, otherwise I go right." |
| `termination` | "Each iteration strictly shrinks `hi - lo` because `hi = mid < hi` and `lo = mid + 1 > lo`, so the `while lo < hi` loop runs at most log2(sum(a)) times and exits with `lo == hi`." | "It ends when the range is empty." |

## Complexity

O(C * log R) time, where `C` is the cost of one feasibility check and `R` is the width of the candidate range. Space is whatever the checker needs, commonly O(1). The brute force tries every candidate value in ascending order at O(C * R).

## Failure modes

- Writing `lo = mid` on the feasible branch, which stops shrinking the range whenever `hi == lo + 1` and loops forever. `termination`
- Setting the initial bounds too narrow, so the true answer sits outside `[lo, hi]` and the loop converges on a wrong feasible value. `invariant`
- Using a feasibility check that is not monotone, for example one with an equality condition, so the false-true boundary is not unique. `discriminator`
- Mixing the two branch styles, one taking `mid` and the other `mid + 1` in the same direction, so the returned `lo` is off by one from the minimum. `boundary-update`
- Searching over a real-valued range with an exact `lo < hi` condition instead of a fixed iteration count or an epsilon, which never terminates in floating point. `termination`

## Template

```python
def smallest_feasible(lo, hi, feasible):
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if feasible(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


def feasible(candidate):
    used = 1
    running = 0
    for value in items:
        if running + value > candidate:
            used += 1
            running = 0
        running += value
    return used <= limit
```
