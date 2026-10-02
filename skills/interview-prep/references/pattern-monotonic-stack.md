---
id: monotonic-stack
tier: B
required_elements: [state-definition, invariant, iteration-order, complexity-target]
---

# Monotonic stack

## Discriminator

For each element, does the answer depend only on the nearest neighbour on one side that beats it under a comparison, so that any element sitting between them can never be the answer for anything further along?

That last clause is what licenses the pop. If element `j` is smaller than the incoming `x` and lies to the right of a smaller element, `j` can never be the nearest smaller neighbour of anything after `x`, so discarding it is free. It rules in next-greater and previous-smaller queries, the largest rectangle under a histogram, and span counting. It rules out queries that need the nearest neighbour above a threshold rather than above the current element.

## Confusable with

| Looks like | Actually | Tell them apart by |
|---|---|---|
| Heap top-k | Both maintain an ordered collection | A heap can pop the extreme at any time; a stack only pops from the end being written, and the pop is triggered by the incoming element. |
| Sliding window with a deque | Both maintain monotonicity | A deque evicts from both ends because elements expire by position; a stack has no expiry rule. |
| Two pointers | Both make one pass over the array | If the answer for index `i` requires an unbounded number of prior candidates to remain live, two indices cannot hold enough state. |

## Required elements

| element | what a complete statement sounds like | what a vague statement sounds like |
|---|---|---|
| `state-definition` | "The stack holds indices, not values, and index `j` stays on the stack while no element after `j` is smaller than `a[j]`." | "I keep a stack of the elements I have seen." |
| `invariant` | "Values at the stacked indices are strictly increasing from bottom to top, so the entry directly below `i` is the previous smaller element of `i`." | "The stack stays sorted." |
| `iteration-order` | "Left to right for previous-smaller and for resolving next-smaller at pop time; each index is pushed exactly once and popped at most once." | "I loop through the array and use a stack." |
| `complexity-target` | "O(n) time because the total number of pops is bounded by the number of pushes, which is `n`; O(n) space for a stack that can hold every index. Brute force scans left from each index at O(n^2)." | "The inner while loop makes it look quadratic but it is fine." |

## Complexity

O(n) time, O(n) space. The brute force answers each index with a backward or forward scan at O(n^2).

## Failure modes

- Stacking values instead of indices, then being unable to compute the width or distance the answer requires. `state-definition`
- Choosing `>=` where `>` is needed on the pop comparison, which changes which of two equal elements is reported and double-counts spans. `invariant`
- Leaving the stack unflushed after the main loop, so elements with no bounding neighbour on the right get no answer. `iteration-order`
- Assuming the answer is written at push time when the pattern writes it at pop time, or the reverse, and mixing the two in one pass. `iteration-order`
- Calling the nested `while` loop quadratic and abandoning a correct O(n) solution. `complexity-target`

## Template

```python
def previous_smaller_indices(values):
    stack = []
    answer = [-1] * len(values)
    for i, value in enumerate(values):
        while stack and values[stack[-1]] >= value:
            stack.pop()
        if stack:
            answer[i] = stack[-1]
        stack.append(i)
    return answer
```
