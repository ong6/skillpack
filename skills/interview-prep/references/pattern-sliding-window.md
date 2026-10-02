---
id: sliding-window
tier: A
required_elements: [state-definition, invariant, boundary-update, complexity-target]
---

# Sliding window

## Discriminator

Is the answer a contiguous run, and does extending the run on the right make the constraint monotonically harder to satisfy, so that shrinking from the left is the only repair needed?

Monotonicity is the whole test. Counting distinct characters, summing non-negative numbers, and tracking a frequency deficit all satisfy it. A sum over an array containing negatives does not, because extending right can make the sum smaller, and the left pointer then has no correct direction to move. It also rules out any problem where the answer may be a subsequence rather than a contiguous run.

## Confusable with

| Looks like | Actually | Tell them apart by |
|---|---|---|
| Two pointers | Two indices over one array | Check whether elements outside the pointers are discarded forever (two pointers) or whether the span itself is being measured (window). |
| Prefix sum with a hash map | Both handle "subarray summing to k" | If values can be negative, the window loses monotonicity and prefix sums are required. |
| Fixed-size aggregation | A window of constant width | A fixed width needs no shrink condition, only an add-one-drop-one step; state the width as a constant rather than deriving it. |

## Required elements

| element | what a complete statement sounds like | what a vague statement sounds like |
|---|---|---|
| `state-definition` | "`counts` maps each character in `s[left:right+1]` to its occurrence count, and `bad` is the number of keys in `counts` whose value exceeds one." | "I keep a hash map of what is in the window." |
| `invariant` | "At the top of every iteration `bad == 0`, so the window holds no repeated character; after appending `s[right]` I shrink from the left until that is true again." | "I keep the window valid as I go." |
| `boundary-update` | "`right` advances one index per outer iteration and never retreats; `left` advances only inside the shrink loop and never passes `right`, so each index is added once and removed at most once." | "I move right forward and pull left up when the window breaks." |
| `complexity-target` | "O(n) time because each index enters and leaves the window once, and O(k) space for the count map over an alphabet of size `k`. The brute force scores every one of the O(n^2) subarrays." | "It should be linear, better than checking everything." |

## Complexity

O(n) time with O(k) space, where `k` bounds the distinct keys tracked. The brute force enumerates all O(n^2) contiguous ranges, and O(n^3) if each range is re-scanned to evaluate the constraint.

## Failure modes

- Using the window on sums that include negative numbers, where shrinking from the left can increase the objective and the loop stalls at a non-optimal answer. `invariant`
- Recording the best answer before the shrink loop restores validity, so an invalid window gets reported. `invariant`
- Deleting a key from the count map only when its value hits zero on some paths, leaving stale zero entries that inflate a distinct-key count. `state-definition`
- Resetting `left` to `right + 1` on a violation instead of shrinking one step at a time, which skips valid windows that start inside the discarded span. `boundary-update`
- Claiming O(n) while the shrink loop rescans the window body on each step, which is O(n^2). `complexity-target`

## Template

```python
def longest_valid_window(items):
    counts = {}
    left = 0
    best = 0
    for right, value in enumerate(items):
        counts[value] = counts.get(value, 0) + 1
        while not window_is_valid(counts):
            drop = items[left]
            counts[drop] -= 1
            if counts[drop] == 0:
                del counts[drop]
            left += 1
        best = max(best, right - left + 1)
    return best
```
