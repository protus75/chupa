---
state: confirmed
source: seed
priority: P2
kind: feature
agent_tier: medium
agent_effort: medium
---

## Depends on
- shakeout-stages

## Context
- chupa/driver.py
- chupa/runner.py
- chupa/triage.py

## Plan contract
- 19.L
- 19.P2
- section 5
- section 11

## Goal / Why
The second shakeout battery group pins the one LLM-stage driver (`chupa/driver.py`) with two members, run through the production drain on the bench with a FakeLLM and zero human input. Its Check run re-confirms every `stages` entry (the double gate) and machine-produces the cumulative report into its OUTBOX.

Why: the driver's bounded re-prompt loop and its stuck-budget kill are the two places a model failure could otherwise loop or hang unbounded (section 5 invariant 2, section 15). Each needs a permanent fixture whose observable a faked run cannot produce.

Owners (19.P2 Emits): this group fences ONLY `chupa/driver.py`, plus `eval/shakeout/` and `tests/test_shakeout.py`. A defect it exposes in the driver is fixed here. A defect anywhere else is filed as a second problem and the ticket replies `premise_failed`, naming it.

## Scope in / Scope out
- In: `eval/shakeout/driver.py` with `MEMBERS`, in this order:
  - `invalid_output_exhausted`: (1) every Implement reply is unparseable or schema-invalid. (2) The attempt makes exactly the driver's bounded allowance of implement requests (the first call plus its re-prompts), each re-prompt rendering the prior validation error as a finding, then the terminal `invalid_artifact` at `implement`, and the drain proceeds to the next ticket. (3) The harvested `invalid_artifact` finding.
  - `stuck_budget_kill`: (1) the scripted Implement call hangs (the FakeLLM `HANG` item) past the ticket's stuck budget, with the bench clock advanced. (2) `abort_current` runs before the terminal, the terminal is `timeout` with one `infra` `cap_consumed` before it, the attempt is harvested, and a second eligible ticket still merges in the same drain. (3) The harvest's `reason`.
- In: `eval/shakeout/run.py`: `GROUPS` becomes `("stages", "driver")`.
- In: an injectable `sleep` seam on `Checkout` (`chupa/runner.py`, default `asyncio.sleep`), passed to `Driver` in place of raw `asyncio.sleep` at `chupa/runner.py` and `chupa/triage.py`, so the bench clock drives the stuck-budget timer. Production behavior is unchanged.
- In: `tests/test_shakeout.py`: one test per member asserting its observable through `run_member`.
- Out: members owned by other modules, any production change outside `chupa/driver.py` and the `Checkout` sleep seam, and any bench or schema edit beyond `GROUPS` and wiring the bench sleep.

## Scope fence
- chupa/driver.py
- chupa/runner.py
- chupa/triage.py
- chupa/__main__.py
- eval/shakeout/
- tests/test_shakeout.py

## Acceptance criteria
1. The `python -m eval.shakeout.run --group driver` command in `## Verification` exits 0 and writes `tickets/shakeout-driver/shakeout-report.json` holding every `stages` member re-confirmed plus both members above, each `green`.
2. `uv run pytest -q tests/test_shakeout.py` passes with one test per member asserting its named observable.
3. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run python -m eval.shakeout.run --group driver --prior tickets/shakeout-stages/shakeout-report.json --out tickets/shakeout-driver/shakeout-report.json
uv run pytest -q tests/test_shakeout.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- A member asserts only a terminal state name, or reads its detail from the terminal reason.
- The hang member waits real wall-clock time instead of advancing the injected clock.
- The report is written by anything but `write_report`, or committed on the branch.
- The diff touches a file outside the fence.

## Time budget
- expected: 45m
- stuck: 90m
