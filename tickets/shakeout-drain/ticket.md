---
state: confirmed
source: seed
priority: P2
kind: feature
agent_tier: medium
agent_effort: medium
---

## Depends on
- shakeout-runner

## Context
- chupa/drain.py
- tests/test_drain.py

## Plan contract
- 19.L
- 19.P2
- section 18

## Goal / Why
The fourth shakeout battery group pins the drain (`chupa/drain.py`: the eligibility scan, re-offers, and the premise park, section 18) with three members, run through the production drain on the bench with a FakeLLM and zero human input. Its Check run re-confirms every prior entry and machine-produces the cumulative report into its OUTBOX.

Why: the drain carries the whole self-build unattended (section 19). A drain that dispatches an unparseable ticket, re-asks an unchanged premise, or cannot land a red-then-green stem in one invocation either wastes the run or stalls it.

Owners (19.P2 Emits): this group fences ONLY `chupa/drain.py`, plus `eval/shakeout/` and `tests/test_shakeout.py`. A defect it exposes in the drain is fixed here. A defect anywhere else is filed as a second problem and the ticket replies `premise_failed`, naming it.

## Scope in / Scope out
- In: `eval/shakeout/drain.py` with `MEMBERS`, in this order:
  - `bad_schema`: (1) a committed ticket missing a required section, beside a valid one. (2) The invalid stem is never dispatched (no `running` transition, no request names it), it is listed under the report's invalid committed tickets with its finding, and the valid ticket merges. (3) The drain report's invalid-ticket line.
  - `premise_park_release`: (1) Implement replies `premise_failed`, then the ticket's committed `ticket.md` changes, then Implement succeeds. (2) A second drain with the ticket unchanged makes ZERO requests for it and reports it parked; after the content commit the next drain runs it and it merges. (3) The parked line's paved road.
  - `red_then_green`: (1) attempt 1 fails Review, attempt 2 is approved. (2) The stem merges in ONE drain invocation with exactly one `retry` `cap_consumed`. (3) Attempt 1's `review.md` findings.
- In: `eval/shakeout/run.py`: `GROUPS` gains `"drain"` after `"runner"`.
- In: `tests/test_shakeout.py`: one test per member asserting its observable through `run_member`.
- Out: members owned by other modules, any production change outside `chupa/drain.py`, and any runner, bench, or schema edit beyond `GROUPS`.

## Scope fence
- chupa/drain.py
- eval/shakeout/
- tests/test_shakeout.py

## Acceptance criteria
1. The `python -m eval.shakeout.run --group drain` command in `## Verification` exits 0 and writes `tickets/shakeout-drain/shakeout-report.json` holding every prior member re-confirmed plus the three members above, each `green`.
2. `uv run pytest -q tests/test_shakeout.py` passes with one test per member asserting its named observable.
3. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run python -m eval.shakeout.run --group drain --prior tickets/shakeout-runner/shakeout-report.json --out tickets/shakeout-drain/shakeout-report.json
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
