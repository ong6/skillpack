---
id: heap-top-k
tier: A
required_elements: [state-definition, invariant, boundary-update, complexity-target]
---

# Heap top-k

## Discriminator

Does the algorithm need repeated access to the current extreme of a set that keeps changing, while the full ordering of the set is never used?

The second clause is what separates this from sorting. If you only ever touch the minimum or maximum, paying O(n log n) to order everything is waste. It rules in selecting the `k` largest from a stream, merging sorted sequences by repeatedly taking the smallest head, and scheduling where the next event is always the earliest end time. It rules out anything needing the median of both halves at once, which takes two heaps, or rank queries at arbitrary positions.

## Confusable with

| Looks like | Actually | Tell them apart by |
|---|---|---|
| Full sort | Both produce ordered output | If `k` is much smaller than `n`, or the input arrives as a stream with no known end, the heap wins and the sort may be impossible. |
| Monotonic stack | Both keep a partially ordered structure | The stack's eviction is driven by the incoming element; the heap's is driven by size or by a query. |
| Bucket or counting selection | Both find the top `k` | With a small bounded value range, counting is O(n) and beats O(n log k). Ask what the value range is. |

## Required elements

| element | what a complete statement sounds like | what a vague statement sounds like |
|---|---|---|
| `state-definition` | "A min-heap holding at most `k = 4` entries of `(frequency, item)`; its root is the smallest frequency among the current best four." | "I use a heap to track the top elements." |
| `invariant` | "After processing any prefix of the input, the heap contains exactly the `k` largest items of that prefix, or all of them if fewer than `k` have been seen." | "The heap always has the best items in it." |
| `boundary-update` | "Push every incoming item; if the size exceeds `k`, pop the root. That evicts the current smallest, which cannot be in the top `k` once a larger item arrives." | "I add things and remove them when the heap gets too big." |
| `complexity-target` | "O(n log k) time and O(k) space, against O(n log n) time and O(n) space for sorting everything and slicing." | "It is faster than sorting because the heap is small." |

## Complexity

O(n log k) time and O(k) space for selection, and O(N log k) for merging `k` sorted sequences of total length `N`. The brute force sorts the whole input at O(n log n) time and O(n) space, which is also the wrong shape for an unbounded stream.

## Failure modes

- Using a max-heap for top-k, which forces you to keep all `n` elements and gives O(n log n) with no space saving. `state-definition`
- Comparing tuples whose second field is not orderable, so ties raise on the tie-break comparison rather than resolving. `state-definition`
- Popping before the size check rather than after the push, which can evict the item just added and drop a valid answer. `boundary-update`
- Negating values to fake a max-heap and forgetting to negate them back in the returned result. `state-definition`
- Quoting O(n log k) while heapifying the entire input first, which is O(n) space and defeats the reason to use a heap. `complexity-target`

## Template

```python
import heapq

def top_k(items, k, score):
    heap = []
    for item in items:
        heapq.heappush(heap, (score(item), item))
        if len(heap) > k:
            heapq.heappop(heap)
    return [item for _, item in sorted(heap, reverse=True)]
```
