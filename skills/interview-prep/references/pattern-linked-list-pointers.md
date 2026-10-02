---
id: linked-list-pointers
tier: B
required_elements: [state-definition, invariant, boundary-update, termination]
---

# Linked list pointers

## Discriminator

Is the structure reachable only by following `next` from a single entry point, so that position `k` cannot be read without `k` steps and the answer must be built from a fixed number of simultaneous cursors?

The absence of random access is the constraint that generates the technique: a gap of `k` between two cursors substitutes for arithmetic on indices, and a two-speed pair substitutes for a visited set. It rules in offset-from-the-end queries, midpoint location, cycle detection in constant space, and in-place reversal. It rules out anything requiring you to walk backwards, unless the list is doubly linked or you reverse a segment first.

## Confusable with

| Looks like | Actually | Tell them apart by |
|---|---|---|
| Two pointers on an array | Two cursors advancing | The list version cannot decrement or compute `hi - lo`, so every termination argument must be phrased in steps taken, not in index arithmetic. |
| Hashing for cycle detection | Both detect a revisit | The map is O(n) space and easier; the two-speed pair is O(1) space. Say which one the constraint demands. |
| Recursion over the list | Both traverse once | Recursion costs O(n) stack, which fails an explicit O(1) space requirement. |

## Required elements

| element | what a complete statement sounds like | what a vague statement sounds like |
|---|---|---|
| `state-definition` | "`lead` and `trail` are node references with `lead` exactly `k = 3` nodes ahead of `trail`, and `dummy.next = head` so `trail` can stop one node before the target." | "I use a fast pointer and a slow pointer." |
| `invariant` | "After every advance, the number of nodes strictly between `trail` and `lead` stays at `k - 1`, so when `lead` is null `trail` sits at the node `k` from the end." | "The gap between the pointers stays the same." |
| `boundary-update` | "Both advance one node per iteration after the initial `k`-step lead; `lead = lead.next` runs first so a null check on `lead` guards the `trail` move." | "I move both pointers forward each time." |
| `termination` | "The loop ends when `lead is None`. On a list without a cycle each iteration consumes one node, so it runs at most `n - k` times; with a two-speed pair the gap closes by one per step inside a cycle of length `c`, so they meet within `c` steps." | "It stops at the end of the list." |

## Complexity

O(n) time and O(1) extra space. The brute force materialises the list into an array for random access at O(n) space, or makes two passes to count the length first, which is still O(n) time but reads the list twice.

## Failure modes

- Dereferencing `fast.next.next` without checking `fast.next`, which throws on lists of even length. `boundary-update`
- Skipping the dummy head, so deleting the first node needs a separate branch that then gets tested last and written wrong. `state-definition`
- Advancing the lead cursor `k` times when the gap must be `k + 1` to leave `trail` on the predecessor of the target. `invariant`
- Running a two-speed pair on a list with a cycle while expecting the null-terminated exit condition, giving an infinite loop. `termination`
- Losing the rest of the list during in-place reversal by reassigning `node.next` before saving it. `state-definition`

## Template

```python
def node_before_kth_from_end(head, k):
    dummy = Node(None, head)
    lead = dummy
    trail = dummy
    for _ in range(k):
        if lead.next is None:
            return None
        lead = lead.next
    while lead.next is not None:
        lead = lead.next
        trail = trail.next
    return trail
```
