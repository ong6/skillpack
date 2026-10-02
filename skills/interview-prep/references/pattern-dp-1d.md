---
id: dp-1d
tier: A
required_elements: [state-definition, base-case, transition, iteration-order]
---

# Dynamic programming, one dimension

## Discriminator

Can the answer at position `i` be written as a function of the answers at a bounded set of earlier positions, with no other information about how those earlier positions were reached?

The second clause is the memorylessness test, and it is what most misapplications fail. If two different ways of reaching `i` would lead to different futures, one index is not enough state and the table needs another dimension. It rules in linear scans over sequences with a local choice at each step, coin and step counting over one changing quantity, and problems where a running best-so-far is compared against a fresh start.

## Confusable with

| Looks like | Actually | Tell them apart by |
|---|---|---|
| Greedy | Both scan once and keep a running best | Greedy commits to a local choice permanently. If a locally worse choice at `i` can win later, the table must keep both. |
| dp-2d | Both fill a table | Count the independent quantities that change. Two sequences, or an index plus a remaining budget, is two dimensions. |
| Prefix sum | Both fill a linear array left to right | Prefix sum has no comparison in its transition, only accumulation. A `max` or `min` in the recurrence marks dp. |

## Required elements

| element | what a complete statement sounds like | what a vague statement sounds like |
|---|---|---|
| `state-definition` | "`dp[i]` is the best total achievable considering the first `i` items and having taken item `i - 1`, so the answer is `max(dp)` rather than `dp[n]`." | "`dp[i]` is the answer up to index `i`." |
| `base-case` | "`dp[0] = 0` for the empty prefix and `dp[1] = a[0]`; the array is length `n + 1` so the transition never indexes below zero." | "I initialise the first entry." |
| `transition` | "`dp[i] = max(dp[i - 1], dp[i - 2] + a[i - 1])` for `i` from 2 to `n`, the two branches being skip and take." | "Each entry is built from the ones before it." |
| `iteration-order` | "Ascending `i`, because `dp[i]` reads `dp[i - 1]` and `dp[i - 2]`, which must already be final. In the rolling-array form the two saved variables replace those reads and update in the same order." | "I fill the array from left to right." |

## Complexity

O(n) time and O(n) space, reducible to O(1) space when the transition reads only a fixed window of previous cells and the answer is a single value rather than the table. The brute force enumerates all subsets or all paths at O(2^n).

## Failure modes

- Defining the state as "the answer up to `i`" without pinning down whether item `i` is included, which makes the transition unwritable. `state-definition`
- An off-by-one between a length-`n` and a length-`n + 1` table, so the base case occupies a cell the transition later overwrites. `base-case`
- Overwriting a rolling variable before the transition has read its old value, which silently uses the current row where the previous one was meant. `iteration-order`
- Seeding the table with 0 where the problem needs negative infinity for unreachable states, so an impossible configuration reads as achievable with value zero. `base-case`
- Returning `dp[n]` when the state definition makes the answer the maximum over all cells. `state-definition`

## Template

```python
def solve(values):
    n = len(values)
    dp = [0] * (n + 1)
    dp[1] = values[0] if n else 0
    for i in range(2, n + 1):
        skip = dp[i - 1]
        take = dp[i - 2] + values[i - 1]
        dp[i] = max(skip, take)
    return dp[n]
```
