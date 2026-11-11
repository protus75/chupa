---
state: confirmed
source: human
priority: P1
kind: chore
---

## Depends on
- none

## Context
- chupa/stages.py::DiffBudgetGate
- chupa/stages.py::DIFF_BUDGET_FILES
- chupa/stages.py::DIFF_BUDGET_INSERTED

## On-demand
- docs/how-chupa-works.md
- tests/integration/test_stages.py
- tests/integration/test_closed_sets.py

## Goal / Why
The `diff_budget` gate fails a diff with more than `DIFF_BUDGET_FILES = 30` changed files or more than `DIFF_BUDGET_INSERTED = 1500` inserted lines. Its stated purpose (the comment above the constants, and `CHUPA_PLAN.md` section 7) is that "every rendered review prompt fits the serving provider's bound". The renderer already measures every rendered prompt against `RENDER_BOUND_CHARS` and refuses an over-bound render, so that bound is guarded without the gate. What fills a review prompt is diff text, which the line cap tracks. The file count adds only a few header lines per file. The 30 was a bootstrap guess, never measured.

On 2026-11-11, `commit-lock` built for 32 minutes and then failed `diff_budget` at 42 files and 480 inserted lines, a third of the line cap. Its file count came from a one-line constructor change in about 35 test files. The owner ruled the file limit arbitrary and asked for it to go.

When this ticket is done, `diff_budget` caps inserted lines only. A mechanical change across many files passes when its line count fits.

## Scope in / Scope out
- In: `chupa/stages.py`:
  - Delete `DIFF_BUDGET_FILES`.
  - `DiffBudgetGate.check` fails only when `inserted_lines > DIFF_BUDGET_INSERTED`.
  - Its finding message becomes "diff is N inserted lines, over the budget of 1500 lines". The paved road is unchanged.
- In: `tests/integration/test_stages.py::test_diff_budget_caps_files_and_inserted_lines` is renamed `test_diff_budget_caps_inserted_lines`, and the `DIFF_BUDGET_FILES` import goes. It asserts:
  - A diff of 31 changed files within the line cap passes.
  - A diff of 1501 inserted lines fails, and its paved road says to split the ticket.
- In: `tests/integration/test_closed_sets.py::test_stages_closed_sets_and_constants` drops its `DIFF_BUDGET_FILES == 30` assertion and keeps `DIFF_BUDGET_INSERTED == 1500`.
- In: `docs/how-chupa-works.md`: the `diff_budget` row in the gates table reads "More than 1,500 inserted lines: split the ticket."
- Out:
  - `DIFF_BUDGET_INSERTED`'s value.
  - The render bound.
  - `gate_bypass`, and existing tickets that carry a `diff_budget` bypass.
  - The prompt specs, which name the diff budget without a file count.

## Scope fence
- chupa/stages.py
- docs/how-chupa-works.md
- tests/integration/test_stages.py
- tests/integration/test_closed_sets.py

## Acceptance criteria
1. `tests/integration/test_stages.py::test_diff_budget_caps_inserted_lines`:
   - `DiffBudgetGate().check` on evidence with 31 changed files and 10 inserted lines returns `pass`, not `fail`.
   - On evidence with 1501 inserted lines it returns `fail`, with a paved road containing `split the ticket`.
2. `grep -rn DIFF_BUDGET_FILES chupa tests` prints nothing.
3. The `diff_budget` row in `docs/how-chupa-works.md` names no file count.
4. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
- `DIFF_BUDGET_INSERTED` changes.
- Any other gate, or the render bound, changes.
- A new file-count limit appears under another name.

## Time budget
- expected: 15m
- stuck: 30m
