---
id: dp-2d
tier: B
required_elements: [state-definition, base-case, transition, iteration-order, complexity-target]
---

# Dynamic programming, two dimensions

## Discriminator

Do two quantities vary independently in the subproblem — two positions in two sequences, or one position plus a remaining budget — such that fixing either alone leaves the answer undetermined?

Independence is the test. If the second quantity is a function of the first, the table collapses to one dimension and the extra axis is wasted memory. It rules in alignment and edit distance between two strings, grid paths with per-cell costs, subset-sum and knapsack over a capacity, and interval dp where the state is a start and an end. It rules out a single sequence with only a local choice, which is one-dimensional.

## Confusable with

| Looks like | Actually | Tell them apart by |
|---|---|---|
| dp-1d with a rolling array | Both may end up using two rows | The state definition decides, not the implementation. Define `dp[i][j]` first, then compress if the transition reads only the previous row. |
| Graph BFS on a grid | Both walk a two-dimensional array | If moves can go in every direction and revisit cells, there is no acyclic order to fill in and it is a traversal. |
| Backtracking | Both explore two-index choices | If distinct paths reaching `(i, j)` are interchangeable for the remainder, memoise rather than enumerate. |

## Required elements

| element | what a complete statement sounds like | what a vague statement sounds like |
|---|---|---|
| `state-definition` | "`dp[i][j]` is the minimum edits turning the first `i` characters of `a` into the first `j` characters of `b`; the table is `(n + 1)` by `(m + 1)` and the answer is `dp[n][m]`." | "`dp[i][j]` is the answer for the two strings at positions `i` and `j`." |
| `base-case` | "`dp[i][0] = i` and `dp[0][j] = j`, since emptying a prefix of length `i` costs `i` deletions and building one of length `j` costs `j` insertions." | "The first row and column are initialised." |
| `transition` | "If `a[i-1] == b[j-1]` then `dp[i][j] = dp[i-1][j-1]`, otherwise `1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])` for delete, insert, replace." | "I take the minimum of the neighbouring cells and add one." |
| `iteration-order` | "Rows ascending, columns ascending inside each row, because every cell reads up, left, and up-left, all of which are already final under that order." | "I fill in the table row by row." |
| `complexity-target` | "O(n*m) time and O(n*m) space, dropping to O(min(n, m)) space with two rolling rows since no cell reads further back than one row. Brute force over all edit sequences is exponential." | "It is quadratic, which is much better than trying everything." |

## Complexity

O(n*m) time with O(n*m) space, reducible to O(min(n, m)) space when the transition reads at most one prior row, at the cost of losing the traceback. Interval dp over one sequence is O(n^2) states with an O(n) split loop, giving O(n^3). Brute force is exponential.

## Failure modes

- Filling only the first row and leaving the first column at zero, which makes deletions free from one side. `base-case`
- Iterating capacity ascending in a rolling one-row knapsack when items may not be reused, which reads the current row and lets one item be taken repeatedly. `iteration-order`
- Confusing the offset between table index `i` and character index `i - 1`, which compares the wrong pair on the diagonal branch. `state-definition`
- Filling an interval dp by ascending start index, so a cell reads a longer inner interval that has not been computed; the order must be by increasing length. `iteration-order`
- Compressing to two rows and then being asked to reconstruct the actual alignment, which the compressed table can no longer produce. `complexity-target`

## Template

```python
def solve(a, b):
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp[n][m]
```
