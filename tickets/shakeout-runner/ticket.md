---
state: confirmed
source: seed
priority: P2
kind: feature
agent_tier: medium
agent_effort: medium
---

## Depends on
- shakeout-driver

## Context
- chupa/runner.py

## Plan contract
- 19.L
- 19.P2
- section 11

## Goal / Why
The third shakeout battery group pins the terminal handler (`chupa/runner.py`: harvest -> dispatch -> journal -> wipe, section 11.2) with three members, run through the production drain on the bench with a FakeLLM and zero human input. Its Check run re-confirms every prior entry and machine-produces the cumulative report into its OUTBOX.

Why: the runner owns the run's single terminal, the `premise_bounce` draw, the diagnosis dispatch, and the identical-terminal short-circuit (section 11.4). A regression there silently loops a stem or loses the history its next attempt needs.

Owners (19.P2 Emits): this group fences ONLY `chupa/runner.py`, plus `eval/shakeout/` and `tests/test_shakeout.py`. A defect it exposes in the runner is fixed here. A defect anywhere else is filed as a second problem and the ticket replies `premise_failed`, naming it.

## Scope in / Scope out
- In: `eval/shakeout/runner.py` with `MEMBERS`, in this order:
  - `premise_false`: (1) Implement replies `premise_failed` with one `premise` finding. (2) The terminal is `premise_failed` at `implement` with exactly one `premise_bounce` `cap_consumed`, no `retry` draw, and the stem is not re-offered in the same drain. (3) The harvested `premise` finding.
  - `timeout_dead_ends`: (1) attempt 1 hangs past its stuck budget after its run record's `## Dead ends` names a unique marker, and diagnosis replies `retry` with a lesson naming the marker. (2) Attempt 2's Implement prompt carries attempt 1's terminal and that lesson in its prior-attempts section. (3) Attempt 1's journaled diagnosis `lessons`.
  - `identical_terminals`: (1) every attempt fails Review with the same finding code, and diagnosis always replies `retry`. (2) Once `IDENTICAL_K` consecutive terminals share one `reason`, the next terminal is dispatched `escalate` (a climb) or routed `reject_queue` at the exhausted ladder, never another same-rung `retry`. (3) The terminal bodies' `reason` and `dispatch` fields.
- In: `eval/shakeout/run.py`: `GROUPS` gains `"runner"` after `"driver"`.
- In: `tests/test_shakeout.py`: one test per member asserting its observable through `run_member`.
- Out: members owned by other modules, any production change outside `chupa/runner.py`, and any runner, bench, or schema edit beyond `GROUPS`.

## Scope fence
- chupa/runner.py
- eval/shakeout/
- tests/test_shakeout.py

## Acceptance criteria
1. The `python -m eval.shakeout.run --group runner` command in `## Verification` exits 0 and writes `tickets/shakeout-runner/shakeout-report.json` holding every prior member re-confirmed plus the three members above, each `green`.
2. `uv run pytest -q tests/test_shakeout.py` passes with one test per member asserting its named observable.
3. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run python -m eval.shakeout.run --group runner --prior tickets/shakeout-driver/shakeout-report.json --out tickets/shakeout-runner/shakeout-report.json
uv run pytest -q tests/test_shakeout.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- A member asserts only a terminal state name, or reads its detail from the terminal reason.
- The report is written by anything but `write_report`, or committed on the branch.
- The diff touches a file outside the fence.

## Time budget
- expected: 60m
- stuck: 120m
