---
id: intervals
tier: B
required_elements: [state-definition, iteration-order, invariant, boundary-update]
---

# Intervals

## Discriminator

Is each input a pair of endpoints on one axis, where the answer depends only on how the endpoints interleave and not on anything inside the span?

If the interior matters, for example a weight distributed across the span, this becomes a sweep with an accumulator or a difference array rather than a merge. It rules in merging overlapping ranges, counting maximum concurrent occupancy, and inserting one range into a sorted disjoint set. It rules out problems where ranges live on two axes at once, which need a sweep plus an ordered structure over the second axis.

## Confusable with

| Looks like | Actually | Tell them apart by |
|---|---|---|
| Sorting alone | Both begin with a sort | The sort key is the decision. Merging sorts by start; counting concurrency sorts endpoint events, or sorts by start with a min-heap of ends. |
| Heap top-k | Both may hold active ranges | You need the heap only when the answer depends on which ranges are currently open, not merely how many. |
| Prefix sum | Both can count coverage | On a small integer axis a difference array is O(range) and simpler; on large or sparse coordinates, sort the events. |

## Required elements

| element | what a complete statement sounds like | what a vague statement sounds like |
|---|---|---|
| `state-definition` | "`current = [start, end]` is the open merged block; `output` holds finished blocks that can no longer grow because every remaining input starts at or after `current[1]`." | "I track the interval I am currently building up." |
| `iteration-order` | "Sorted ascending by start, ties broken by end. Once sorted, an interval can only overlap the block immediately preceding it." | "I sort the intervals first." |
| `invariant` | "Everything in `output` is pairwise disjoint and sorted, and `current[0]` is at least the end of the last block in `output`." | "The output stays merged." |
| `boundary-update` | "If `item[0] <= current[1]` then `current[1] = max(current[1], item[1])`; otherwise append `current` and set `current = item`. The max matters because a fully contained interval must not shorten the block." | "I extend the end if they overlap, otherwise start a new one." |

## Complexity

O(n log n) time dominated by the sort, with O(n) output space and O(1) working space beyond it. On a bounded integer axis a difference array gives O(n + R). The brute force compares every pair for overlap at O(n^2) and still needs a merge pass.

## Failure modes

- Taking `current[1] = item[1]` on the overlap branch, which truncates the block whenever one interval fully contains another. `boundary-update`
- Sorting by end when merging, which breaks the guarantee that only the previous block can overlap. `iteration-order`
- Getting the touching case wrong: `[1,2]` and `[2,3]` merge under a closed-interval reading and stay separate under a half-open one, and the problem's convention decides. `boundary-update`
- Forgetting to append the final `current` after the loop, dropping the last block. `invariant`
- Processing start and end events in the wrong relative order at an identical coordinate, which shifts a concurrency count by one. `iteration-order`

## Template

```python
def merge_intervals(items):
    if not items:
        return []
    items.sort(key=lambda pair: (pair[0], pair[1]))
    output = []
    current = list(items[0])
    for start, end in items[1:]:
        if start <= current[1]:
            current[1] = max(current[1], end)
        else:
            output.append(current)
            current = [start, end]
    output.append(current)
    return output
```
