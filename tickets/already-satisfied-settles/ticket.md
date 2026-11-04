---
priority: P1
kind: bug
source: human
state: confirmed
---

## Depends on
none

## Context
- docs/how-chupa-works.md
- tickets/already-satisfied-settles/evidence/journal-excerpt.txt
- chupa/runner.py
- chupa/status.py
- chupa/drain.py
- tests/test_drain.py
- tests/test_status.py

## Goal / Why
`already_satisfied` is a settled outcome (the ticket settles as a no-op; `SETTLED` in `chupa/drain.py`), but `drive` in `chupa/runner.py` sends it down the failure path: it skips only the harvest, then pays for a diagnosis call and lets `failure_terminal` route the terminal to the Reject queue. `harden-serve-activation-3`, `plan-gap-32` and `plan-gap-34` each finished `already_satisfied`, paid for a diagnosis that answered `reject`, and journaled `routed: reject_queue`. `status` and the drain now list them as awaiting a verdict, while the `reject` verb refuses them as settled. Two readers disagree about the same stems.

## Scope in / Scope out
- In: `drive` journals an `already_satisfied` result as its settled terminal (`to: already_satisfied`, its stage, reason `already_satisfied`) and removes the worktree, with no diagnosis call, no cap draw, no dispatch, and no `routed` marker.
- In: one definition of the settled states (`merged`, `already_satisfied`) shared by `reject_queue` in `chupa/status.py`, the `reject` verb in `chupa/runner.py`, and the drain in `chupa/drain.py`; `reject_queue` never returns a stem whose latest terminal is settled, whatever its recorded `routed` marker.
- In: `tests/test_drain.py` adds `test_already_satisfied_settles_without_diagnosis` (a scripted `already_satisfied` Implement makes no further LLM call, journals no `cap_consumed` and no `routed` marker, and leaves no worktree), and drops the `diagnosis_reply()` steps its existing scripts queue after `already_satisfied` results.
- In: `tests/test_status.py` adds `test_settled_stem_never_awaits_verdict` (a journal whose `already_satisfied` terminal carries `routed: reject_queue` yields an empty `reject_queue`, and a `merged` stem never appears either).
- In: `tests/regress_already_satisfied.py`, the carried reproducer: it feeds `status.reject_queue` a journal whose `already_satisfied` terminal carries `routed: reject_queue` (the shape in the evidence file). It prints `{"regression_result": "pass"}` and exits 0 when the stem is absent, prints `{"regression_result": "defect"}` and exits 1 when it is present, and prints `{"regression_result": "error"}` and exits 2 on any other failure. Diagnostics go to stderr only.
- In: update `docs/how-chupa-works.md` sections 6.1 (drop the known-defect note), 6.6, and 10.3 (`already_satisfied` is settled, never awaiting a verdict), so the doc matches the code when this merges.
- Out: the outcome vocabulary, the `already_satisfied` proof rule in Implement, journal history, and every other failure-path behavior.

## Scope fence
- docs/how-chupa-works.md
- chupa/runner.py
- chupa/status.py
- chupa/drain.py
- tests/test_drain.py
- tests/test_status.py
- tests/regress_already_satisfied.py

## Acceptance criteria
1. `uv run python tests/regress_already_satisfied.py` prints exactly `{"regression_result": "pass"}` and exits 0.
2. `uv run pytest -q tests/test_drain.py tests/test_status.py` exits 0, including `test_already_satisfied_settles_without_diagnosis` and `test_settled_stem_never_awaits_verdict`.
3. `uv run pytest -q` exits 0.

## Verification
```
uv run python tests/regress_already_satisfied.py
uv run pytest -q tests/test_drain.py tests/test_status.py
uv run pytest -q
```

## Regression
```
uv run python tests/regress_already_satisfied.py
```
- carries: tests/regress_already_satisfied.py

## Definition of rejected
Reject the branch if an `already_satisfied` result still makes a diagnosis call or reaches the Reject queue, if a settled stem can appear in `reject_queue`, if the settled set is defined in more than one place, or if any non-settled failure routes differently.

## Time budget
- expected: 45m
- stuck: 90m
