# DSA reps

## Contents

- [Generating the problem](#generating-the-problem)
- [Plan rep](#plan-rep)
- [Timed round](#timed-round)
- [Grading output](#grading-output)
- [Running code](#running-code)
- [Round buffer template](#round-buffer-template)

Two rep types share one pattern queue and one bank. A **plan rep** grades the plan said out loud
before any code; twenty minutes is a complete session. A **timed round** is a full 45-minute coding
round. Short day or a pattern overdue on a plan element: plan rep. Interview loop within two weeks or
the candidate asks for a mock round: timed round.

Discriminators beat recognition cues. "Sorted array" misfires both ways; "is there a predicate that
flips from false to true exactly once?" can be checked before code. Interleave: never two reps of
the same pattern back to back, because blocked practice builds fluency that collapses when nothing
announces the pattern.

## Generating the problem

1. Build it from the pattern file's **Discriminator** section, never from a known problem's title.
   A known problem's name never enters the generation.
2. Re-skin it to a domain the candidate works in.
3. Structural cues only; never restate a known problem's setup in new words.
4. Similarity gate: if the result is recognisable as a known problem, change the **structure** (what
   is returned, a constraint that moves the complexity target, produce versus count). Renaming
   variables is a copy.
5. Persist nothing generated. The bank stores pattern, verdict, elements, due date and a note about
   the reasoning, never the problem.
6. Do not name the pattern until grading: naming it hands over the `discriminator` element.

## Plan rep

1. Give the problem, then ask: "Before you write anything: what are you going to do, and why that?"
2. Grade every `required_elements` id from the pattern file as present, vague or missing, with the
   quoted span beside each ([state.md](state.md#marks-and-verdicts)).
3. Name the broken element in one line, quoting them: "`iteration-order` was missing. You said
   'then I fill in the table': in which direction, and what must each cell already have?"
4. Let them recover a missing element; the verdict still records the unprompted plan.
5. If time remains, they code it and you run it ([Running code](#running-code)). Only a plan with
   every element present can reach `coded`; a vague element stays `half` however the code runs.
6. Append the bank row and the rep-log row. Close with one line: verdict, the element that broke,
   when the pattern is next due. No session summary.

## Timed round

Interviewer setup, before the clock:

- Pick the pattern from `scripts/due.py` and a problem that also tests a Live carry.
- Write the prompt in interviewer voice: at most two examples, no title, no constraints.
- Keep a hidden list of **material facts** only: answers that change the algorithm, a branch, a
  bound, a data structure or the return contract. Answer only what is asked; never hint a hidden
  fact exists.
- The buffer is a plain-text file in `practice/` (template below), opened in the candidate's
  editor. Write the prompt into it. Write each clarification answer into the file under their
  question as well as in chat. Below the prompt the buffer stays blank: no stage headings, no
  "invariant:" prompts. They bring the sequence; a stage they skip is scored as skipped.
- No compiler, execution or autocomplete for the candidate. Mid-round the interviewer corrects
  nothing and executes nothing. Read the file whenever they say "submitted".

| Minutes | Stage | Expected |
|---|---|---|
| 0–5 | Understand | Restate the operation; ask what is needed. No question quota: score material facts caught and assumptions made; canned questions that cannot change the solution count against. |
| 5–10 | Design | Invariant or loop-body assignment in words; the seed and what breaks without it; time and auxiliary space (excluding input and output); three tests (minimal, boundary, adversarial), each naming the bug it targets. |
| 10–30 | Implement | A complete function in the buffer, named variables, one idea per line. Pseudocode or an unfinished core path does not pass. |
| 30–36 | Verify | Dry-run the example and the adversarial test against the written code, one value per line. Patch by rewriting the block. |
| 36–44 | Evolve | One follow-up that stresses or breaks the structure; they modify design or code and state the new cost. If they anticipated it, mark it strong and give a second, different one. |
| 44–45 | Close | Final complexity and the remaining known risk. |
| 45–50 | Re-install | After the debrief, every block the correction touched is rewritten from blank, unaided. Do not show the fixed code first. |

Use the real clock: record the end time with `date` at the start, schedule background alerts for
five minutes left and time up, and compute "time left" from `date` before each interviewer turn.

Five axes, 0–2 each: `specification · mechanism · implementation · verification · adaptation`.
Pass needs at least 8/10 with no zero in mechanism, implementation or verification. Bank verdict:
a fail is `failed`. A pass is graded on the design stage's plan: any required element vague or
missing is `half`; all present is `named-clean` when the first plan statement had them all, else
`coded`. `missing` lists the design-stage elements that were missing or vague.

## Grading output

In chat, never an HTML page or artifact. A timed round gets all six parts in this order; a plan
rep gets parts 2 and 3 (and 4 if they coded), then its one-line close.

1. One-line pass or fail verdict with the post-round execution result (cases failed of cases run).
2. The score table: five axes for a timed round, or element marks with quotes for a plan rep, one
   line of reason each.
3. **You wrote vs actually**: one bullet per defect, quoting their line and ending with the
   **trigger**, the clause in the prompt that should have fired the right move.
4. **Reference solution, always, including on a pass.** Run it first and say it is verified. Human
   style: spelled-out names, one idea per line, no comprehensions, comments saying why. Then "the
   bit to memorise": the one line people get wrong. Where a confusable twin exists (last-true
   versus first-true search, produce versus count, count versus longest), show both blocks so they
   diff line by line, with a small table telling them apart.
5. **Primitives refreshed** for each data structure the rep touched: one sentence, the Python to
   type, operation costs, the gotcha.
6. Ask for the re-install.

No LaTeX math delimiters: variables, complexities and expressions go in backticks (`k`,
`O(n log n)`). Terminals do not render `$...$`.

## Running code

Write the candidate's code and a fresh reference solution to a temp dir, never the state folder,
with a cases file:

```json
{"function": "solve", "unordered": false, "cases": [{"args": [[1, 2, 3]], "expected": 6}]}
```

Then, from this skill's folder:

```bash
python3 scripts/run_cases.py /tmp/rep/solution.py /tmp/rep/cases.json
```

It prints one JSON line (`passed`, `total`, per-case `got`/`want`/`error`) and exits 0 only when
all pass. Stdlib only. Set `"unordered": true` when any ordering of a list answer is correct. Write
reference solutions fresh: standard algorithms are fine to write, editorial prose is not copied.

## Round buffer template

```markdown
# Timed round: YYYY-MM-DD

Timer started: ______

Plain text, no running code, no headings handed to you. You drive: restate, ask, design, code,
verify, adapt, close. Say "submitted at minute M" whenever you want it read.

## Prompt

(interviewer writes the prompt here; clarification answers go under each question)

## Your buffer

---

(after time: Q/A transcript, follow-up given, five-axis table, skipped stages, verified solution,
re-install block)
```
