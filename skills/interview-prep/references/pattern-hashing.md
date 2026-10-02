---
id: hashing
tier: A
required_elements: [state-definition, iteration-order, dedup, complexity-target]
---

# Hashing

## Discriminator

Can each element be reduced to a key such that everything the answer needs about earlier elements is recoverable from that key alone, in constant time?

The key is the design decision, not the dictionary. A sorted letter tuple groups anagrams; a running prefix total groups equal-sum ranges; a normalised slope and anchor group collinear points. It rules in every problem where order is irrelevant but membership or count is not, and it rules out problems where the answer depends on the relative positions of elements that share a key, unless you store positions as the value.

## Confusable with

| Looks like | Actually | Tell them apart by |
|---|---|---|
| Two pointers | Both find pairs meeting a target | If the input is unordered and sorting would destroy required index information, use a map. |
| Prefix sum | Both use a running total | Prefix sum alone answers range queries by subtraction; add a map only when you must find which earlier prefix matches a value. |
| Union-find | Both group items | Grouping by a fixed computable key is hashing; grouping by transitive pairwise relations that arrive incrementally is union-find. |

## Required elements

| element | what a complete statement sounds like | what a vague statement sounds like |
|---|---|---|
| `state-definition` | "`seen` maps a value to the smallest index at which it appeared, so `seen[target - x]` gives the partner index directly." | "I use a hash map to remember what I have seen." |
| `iteration-order` | "For each `x` at index `i` I look up before I insert, so `x` cannot match itself; a value inserted at step `i` is only visible to steps after `i`." | "I go through the array and fill the map as I go." |
| `dedup` | "On a repeated key I keep the first index and ignore later ones, because the problem asks for the earliest valid pair." | "I handle duplicates in the map." |
| `complexity-target` | "O(n) time for one pass with O(1) expected lookups, and O(n) space in the worst case where all keys are distinct. Brute force is O(n^2)." | "Hash maps are constant time so this is fast." |

## Complexity

O(n) expected time with O(n) space. Worst-case lookup degrades under adversarial keys, which matters only in languages with a predictable hash. The brute force compares every pair at O(n^2).

## Failure modes

- Inserting before looking up, so an element satisfies the condition against itself. `iteration-order`
- Overwriting an existing key when the problem needs the first occurrence, or keeping the first when it needs the last. `dedup`
- Choosing a mutable key such as a list, or an unnormalised one such as an unreduced fraction, so structurally equal items land in different buckets. `state-definition`
- Storing only a boolean when the answer needs an index or count, forcing a second scan that reintroduces the quadratic term. `state-definition`
- Quoting O(n) while building the key costs O(k) per element, for example sorting each string, which is O(n k log k). `complexity-target`

## Template

```python
def first_matching_pair(items, target):
    seen = {}
    for index, value in enumerate(items):
        want = target - value
        if want in seen:
            return (seen[want], index)
        if value not in seen:
            seen[value] = index
    return None
```
