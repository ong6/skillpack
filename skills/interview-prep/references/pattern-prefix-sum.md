---
id: prefix-sum
tier: B
required_elements: [state-definition, base-case, transition, iteration-order]
---

# Prefix sum

## Discriminator

Is the quantity asked for over a range expressible as a difference of two cumulative values taken at the range endpoints?

The operation must have an inverse for the subtraction to work: addition and XOR qualify, maximum does not. It rules in repeated range-sum queries, counting ranges whose total equals a target when combined with a map, and running-balance problems where a value of zero marks equality between two categories. It rules out range minimum or maximum queries, which need a sparse table or a segment tree.

## Confusable with

| Looks like | Actually | Tell them apart by |
|---|---|---|
| Sliding window | Both answer questions about contiguous ranges | Negative values break the window's monotonicity but leave prefix arithmetic intact. Ask whether values can be negative. |
| Hashing | Both use a map keyed on a computed value | Prefix sum defines the key; hashing is the lookup mechanism. State the prefix definition first, then say the map stores counts of prior prefixes. |
| dp-1d | Both fill a linear array left to right | Prefix sum has a fixed closed-form transition with no choice at each cell; dp compares alternatives. |

## Required elements

| element | what a complete statement sounds like | what a vague statement sounds like |
|---|---|---|
| `state-definition` | "`pre[i]` is the sum of the first `i` elements, so `pre` has length `n + 1` and the sum of `a[l..r]` inclusive is `pre[r + 1] - pre[l]`." | "I build an array of running sums." |
| `base-case` | "`pre[0] = 0` represents the empty prefix, which is what makes ranges starting at index 0 work without a special case." | "I start the array at zero." |
| `transition` | "`pre[i + 1] = pre[i] + a[i]` for every `i` from 0 to `n - 1`." | "Each entry adds the next element." |
| `iteration-order` | "Strictly left to right, because `pre[i + 1]` reads `pre[i]`, which must already hold its final value." | "I loop through the array in order." |

## Complexity

O(n) preprocessing and O(1) per range query, with O(n) space for the prefix array. The counting variant that pairs prefixes with a map is O(n) time and O(n) space in one pass. The brute force re-sums each queried range at O(n) per query.

## Failure modes

- Sizing the prefix array at `n` instead of `n + 1` and then special-casing `l == 0` inside the query, which usually loses the empty-prefix case. `base-case`
- Mixing inclusive and exclusive endpoint conventions between construction and query, giving answers off by one element at one end. `state-definition`
- Seeding the count map with `{0: 1}` for the two-dimensional or subarray-count variants and forgetting it, so ranges beginning at index 0 are never counted. `base-case`
- Incrementing the map with the current prefix before querying it, which lets a range of length zero satisfy the target. `iteration-order`
- Building prefixes over an operation with no inverse, such as maximum, and subtracting anyway. `transition`

## Template

```python
def build_prefix(values):
    prefix = [0] * (len(values) + 1)
    for i, value in enumerate(values):
        prefix[i + 1] = prefix[i] + value
    return prefix


def count_ranges_with_total(values, target):
    counts = {0: 1}
    running = 0
    found = 0
    for value in values:
        running += value
        found += counts.get(running - target, 0)
        counts[running] = counts.get(running, 0) + 1
    return found
```
