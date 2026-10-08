---
priority: P0
kind: bug
agent_tier: high
agent_effort: high
source: human
state: confirmed
---

## Depends on
- spec-gap-unit-detection

## Context
- chupa/drain.py
- chupa/runner.py
- chupa/status.py
- chupa/caps.py
- chupa/specs.py
- tests/test_drain.py
- tests/test_reject_queue.py
- tests/test_seed_path.py

## Plan contract
- section 9.1
- section 11.4
- section 13.5
- section 18
- 19.L

## Goal / Why
A spec-gap Reject arrival is bound to the plan bytes it judged. If the hardener already had the units and left them unchanged, the stem goes to the Reject queue at once with reason `spec_gap_unresolved`. The pre-daemon auto-keep never answers a plan-bound arrival. A commit that changes a bound unit releases it mechanically, drawing one `retry` unit. A plan-bound `premise_failed` is never premise-parked. A retired hardener is never dispatched again. The quiescence report names the unit to fix and the continuing command.

Why: section 11.4 DISPATCH step (1), HOLD AND RELEASE, and EXHAUSTION, and the Pre-daemon default verdict exception. Today `chupa/drain.py` `_select` auto-keeps every Reject arrival with `retry` budget, so a capped spec-gap arrival re-runs up to `caps.retry` times against byte-identical units. `premise_parked` parks a capped spec-gap `premise_failed` until its `ticket.md` changes, while the fault is the plan's (section 18), so the plan fix alone never releases it. The double-confirm refusal (`chupa/runner.py` `verdict`) looks only at the ticket blob, so the operator's plan fix cannot re-enqueue a seed whose `ticket.md` is unchanged.

## Scope in / Scope out
- In: `chupa/runner.py` spec-gap dispatch step (1). Let P be the stem's latest prior spec-gap terminal inside its `caps.lineage` window. D is the set of units in P's `plan_units` that P's `round` record covered and whose current `unit_sha` equals the recorded sha. When every gapped unit is in D, the terminal is `{to, stage, reason: "spec_gap_unresolved", dispatch: "reject_queue", routed: "reject_queue", plan_units}`, with no `hardening` draw. Otherwise steps (2) and (3) run as merged. A filed round covers G minus D.
- In: `chupa/drain.py`. A plan-bound arrival is a Reject arrival whose terminal carries `plan_units`. The auto-keep skips it. When any unit in its `plan_units` has a current `unit_sha` different from the recorded one and `retry` is unspent, the drain journals the machine-actor `reject_verdict` keep, and the re-offer draws one `retry` unit for any `to`, `premise_failed` included. `premise_parked` is false for a terminal carrying `round` or `plan_units`. A stem that `hardener_round` names with a closed round is never selected, and is never auto-kept.
- In: `chupa/drain.py` `_settle`. For a plan-bound arrival the parked line names its `reason`, each unit in `plan_units`, and the rounds that covered them with their hardeners' terminal `to`. The paved road reads "fix <unit> in CHUPA_PLAN.md, commit it, then uv run python -m chupa drain", and the daemon-era `confirm`/`reject` road follows it.
- In: `chupa/runner.py` `verdict`. A second consecutive operator `confirm` at an unchanged ticket blob is allowed when the stem's latest terminal carries `plan_units` and any of those units has a changed `unit_sha`.
- Out: the round fold and filing (merged); detection (merged); vocabulary closure; the copy refusal.

## Scope fence
- chupa/runner.py
- chupa/drain.py
- chupa/hardening.py
- tests/test_drain.py
- tests/test_reject_queue.py
- tests/test_seed_path.py
- tests/test_hardening.py

## Acceptance criteria
1. `uv run pytest -q tests/test_drain.py` exits 0 and includes `test_plan_bound_arrival_is_never_auto_kept_and_releases_on_a_unit_change`. A plan-bound `gate_failed` arrival with `retry` budget and unchanged units is neither kept nor re-run, and the drain reaches quiescence. Its parked line names the unit, `CHUPA_PLAN.md`, and `chupa drain`. After a commit that changes the unit's bytes, the next drain journals one machine-actor keep and one `retry` draw, then re-runs the stem.
2. `uv run pytest -q tests/test_drain.py` includes `test_plan_bound_premise_is_not_premise_parked`, where a plan-bound `premise_failed` releases on the unit change with no `ticket.md` edit. It also includes `test_retired_hardener_is_never_dispatched`, where the hardener of a closed round that ended `routed: reject_queue` is neither auto-kept nor re-run.
3. `uv run pytest -q tests/test_seed_path.py` exits 0 and includes `test_unchanged_units_after_a_closed_round_route_spec_gap_unresolved`. A held stem's round closes `already_satisfied` with the unit bytes unchanged, and the stem's next spec-gap terminal journals `reason: spec_gap_unresolved` with `routed: reject_queue`, draws no `hardening` unit, and files no round.
4. `uv run pytest -q tests/test_reject_queue.py` exits 0 and includes `test_confirm_after_a_plan_fix_of_a_bound_unit_is_not_a_double_confirm`. The existing double-confirm refusal test still passes.
5. `uv run pytest -q tests/test_daemon_composition.py tests/test_kill_cli_activation.py` exits 0 unchanged.
6. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_drain.py
uv run pytest -q tests/test_seed_path.py
uv run pytest -q tests/test_reject_queue.py
uv run pytest -q tests/test_daemon_composition.py tests/test_kill_cli_activation.py
uv run pytest -q
```

## Regression
```
uv run pytest -q tests/test_drain.py -k test_plan_bound_arrival_is_never_auto_kept_and_releases_on_a_unit_change
```
- carries: tests/test_drain.py

## Definition of rejected
Reject the branch if any machine path re-runs a plan-bound arrival whose bound units are byte-identical, if a machine release draws no `retry` unit, if a plan-bound terminal can be premise-parked, or if the regression test passes on the merge base.

## Time budget
- expected: 90m
- stuck: 180m
