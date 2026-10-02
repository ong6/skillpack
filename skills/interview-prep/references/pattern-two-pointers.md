---
id: two-pointers
tier: A
required_elements: [state-definition, invariant, boundary-update, termination]
---

# Two pointers

## Discriminator

Does the array carry an order such that moving one end changes the objective monotonically, so that discarding one end permanently removes no valid answer?

That is the property being tested, and sortedness is only one way to get it. It rules in pair-sum on ordered values, in-place partitioning where the left region is "kept" and the right is "scanned", and palindromic comparison from both ends. It rules out any objective where moving `lo` inward could still leave a better answer behind `lo`, which is why unsorted pair-sum needs hashing instead. If the two indices both only ever move forward and the region between them has meaning, the pattern is sliding-window, not this.

## Confusable with

| Looks like | Actually | Tell them apart by |
|---|---|---|
| Sliding window | Two indices, but both advance in the same direction and the span between them is the answer | Ask whether the region between the pointers is the object being measured. If yes, it is a window. |
| Binary search | Both narrow a range | Two pointers moves one end by one step using a local comparison; binary search jumps to the midpoint using a global predicate. |
| Hashing | Both find pairs summing to a target | Hashing needs no order and returns original indices; two pointers needs order and destroys original indices if you sort. |

## Required elements

| element | what a complete statement sounds like | what a vague statement sounds like |
|---|---|---|
| `state-definition` | "`lo = 0` and `hi = n - 1` are indices into the sorted array; every element at index `< lo` or `> hi` has been ruled out as part of any answer." | "I keep a left and a right pointer and move them around the array." |
| `invariant` | "If a valid pair exists, both of its indices lie in `[lo, hi]`; discarding `lo` when `a[lo] + a[hi] < target` is safe because `a[hi]` is the largest partner `a[lo]` can ever get." | "The answer is always somewhere between the two pointers." |
| `boundary-update` | "Sum too small moves `lo += 1`; sum too large moves `hi -= 1`; equal returns. Exactly one pointer moves per iteration, so `hi - lo` strictly decreases." | "I move whichever pointer needs to move depending on the sum." |
| `termination` | "The loop condition is `lo < hi`; each iteration shrinks `hi - lo` by one, so from a gap of `n - 1` it runs at most `n - 1` times." | "It stops when the pointers meet." |

## Complexity

O(n) time and O(1) extra space on data that already carries the order. If you sort first, the sort dominates at O(n log n) time, and an in-place sort costs O(log n) stack. The brute force is the double loop over all pairs at O(n^2) time.

## Failure modes

- Sorting to enable the pattern and then returning positions in the sorted array when the caller wanted positions in the original input. `state-definition`
- Using `lo <= hi` where the two pointers must not reference the same element, which lets a single element pair with itself. `termination`
- Moving both pointers on the equality branch while collecting all matches, skipping a valid neighbouring pair. `boundary-update`
- Applying the pattern to values that are ordered but where the objective is not monotone in the endpoints, so discarding an end throws away the optimum. `invariant`
- Advancing past duplicates with a bare `lo += 1` inside the equality branch instead of a loop, which emits the same pair twice on runs of length three or more. `boundary-update`

## Template

```python
def two_pointer_scan(items, target):
    items.sort()
    lo, hi = 0, len(items) - 1
    results = []
    while lo < hi:
        total = items[lo] + items[hi]
        if total == target:
            results.append((lo, hi))
            lo += 1
            hi -= 1
            while lo < hi and items[lo] == items[lo - 1]:
                lo += 1
        elif total < target:
            lo += 1
        else:
            hi -= 1
    return results
```
