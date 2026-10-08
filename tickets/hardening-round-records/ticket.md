---
priority: P0
kind: bug
agent_tier: high
agent_effort: high
source: human
state: confirmed
---

## Depends on
- hardening-round-closure

## Context
- chupa/runner.py
- chupa/drain.py
- chupa/specs.py
- chupa/tickets.py
- chupa/stages.py
- chupa/effects.py
- tests/test_seed_path.py
- tests/test_drain.py
- tests/test_stages.py

## On-demand
- tests/test_daemon_composition.py

## Plan contract
- section 6.2
- section 11.4
- section 13.3

## Goal / Why
A hardening round's identity is its journaled `hardening_round` record. File names never identify a round. At most one round is open engine-wide. A held terminal carries its `round` and `plan_units`, and the hold reads the round from the terminal. The `spec_gap_hold` signal, the `tickets/harden-*` glob, and `tickets.py` `HARDENING_STEM` are gone.

Why: section 11.4 RECORDS makes the `hardening_round` signal the hardener's identity and puts `round` and `plan_units` on the held terminal. Today `chupa/runner.py` discovers rounds by globbing `tickets/harden-*/ticket.md` and matching `HARDENING_STEM`. Deleting a directory resets a round count, and any stem named `harden-*` passes the hardening cite role (`chupa/tickets.py` `_seed_cites`). Each gapped row files its own ticket, fenced to one unit, so concurrent rounds overlap. A gap spanning two units is unfixable because `ScopeFenceGate._unit_confined` admits a plan diff confined to ANY one anchor, never to all of them together. The filing Effect key `ticket-plane/<seeding>/<attempt>/harden/<row>` is attempt-scoped, so a reaped filer's re-run cannot replay its commit.

## Scope in / Scope out
- In: `chupa/specs.py` gains `unit_sha(plan, uid) -> str`: the sha256 hex of the unit's single resolved slice (the `_units` slice the `Plan contract` resolver injects), or the literal `absent` when the unit has no heading. It is the one unit-sha helper.
- In: `chupa/hardening.py` gains `ROUND_SIGNAL = "hardening_round"` and a fold over those records: each round's number, hardener stem (the record's envelope `ticket`), `units`, `filed_by`, `gaps`, and journal position. `round_state(events, round_number)` folds only the hardener terminals journaled after that round's record. `open_round(events)` returns the open round or None, and `hardener_round(events, stem)` returns the round a stem hardens or None.
- In: `chupa/runner.py`. The existing detectors' row stems map to unit ids `19.P<phase>.<row>`; these are G. A stem that `hardener_round` names is never hardened and routes as an ordinary terminal. Otherwise, after the existing `hardening` cap check and draw, the runner JOINS the open round when one exists. When none is open, it FILES round N = 1 + the count of `hardening_round` records, covering G. Filing commits `tickets/plan-gap-<N>/ticket.md` through `ctx.driver.effects.run` with key `ticket-plane/hardening/<N>`. It then journals the hardener's `ticket_intake` signal and the `hardening_round` signal `{round, units: {uid: unit_sha}, filed_by, gaps}` (envelope `ticket: plan-gap-<N>`), both built from the Effect's completion result. The held terminal is `{to, stage, reason: "spec_gap", dispatch: "spec_gap_hold", round, plan_units}`. The cap-spent terminal adds `plan_units`. No `spec_gap_hold` signal is written.
- In: `chupa/runner.py` hardening-ticket composition follows section 11.4 THE HARDENING TICKET. `## Plan contract` cites `19.L`, each gapped unit's phase unit, each gapped unit that exists, and each gapped row's `cite`. `## Scope fence` has one `CHUPA_PLAN.md#<unit>` per unit. The filer's `priority` carries over, and the starting capability is `high/high` when any gapped row is `deep` and `medium/medium` otherwise. Each criterion renders one gap fact as data.
- In: `chupa/drain.py`. A stem is HELD when its latest terminal has `dispatch: spec_gap_hold`, carries `round`, and `round_state` is `open`. A `spec_gap_hold` terminal without `round` reads as released (the versioning policy tolerates older bodies). Its quiescence line names the round number and its hardener stem. The release re-run still draws no `retry` unit.
- In: `chupa/tickets.py` deletes `HARDENING_STEM` and its `_seed_cites` branch, so a hardening ticket meets the seeding role's floor (`19.L` and a phase unit). `chupa/stages.py` `ScopeFenceGate._unit_confined` admits a plan diff only when removing ALL anchored units leaves main and head identical.
- Out: how spec gaps are detected (the row-keyed detectors stay as they are); plan-bound release; the auto-keep; the premise park; vocabulary closure.

## Scope fence
- chupa/hardening.py
- chupa/runner.py
- chupa/drain.py
- chupa/specs.py
- chupa/tickets.py
- chupa/stages.py
- tests/test_hardening.py
- tests/test_seed_path.py
- tests/test_drain.py
- tests/test_stages.py
- tests/test_specs.py
- tests/test_daemon_composition.py

## Acceptance criteria
1. `uv run pytest -q tests/test_hardening.py` exits 0. The suite covers the record fold and `round_state` anchored on the record. It includes `test_one_open_round_engine_wide`: a second spec-gap stem JOINS round 1 instead of filing round 2, and round 2 is filed only after round 1 closes. It includes `test_a_hardener_is_never_hardened`.
2. `uv run pytest -q tests/test_seed_path.py` exits 0. Its hardening tests assert the `plan-gap-1` ticket, its `hardening_round` record, and the held terminal body `{to, stage, reason, dispatch, round, plan_units}`, with no `spec_gap_hold` signal. A new `test_reaped_filer_replays_its_round_commit` runs the filing Effect twice for the same round and asserts one ticket-plane commit and one `hardening_round` record.
3. `uv run pytest -q tests/test_drain.py tests/test_daemon_composition.py` exits 0. Their spec-gap cases journal a `hardening_round` record and a held terminal with `round`, and assert the hold until the round closes and the free release after it. A new drain test asserts that a legacy `spec_gap_hold` terminal without `round` is released.
4. `uv run pytest -q tests/test_specs.py` exits 0 and includes `test_unit_sha_is_absent_for_a_missing_unit_and_tracks_unit_bytes`.
5. `uv run pytest -q tests/test_stages.py` exits 0 and includes `test_scope_fence_admits_a_plan_edit_confined_to_all_anchored_units`: a diff touching two anchored units passes, and a diff touching an anchored unit plus unanchored plan text fails.
6. `uv run pytest -q tests/test_tickets.py tests/test_kill_cli_activation.py` exits 0 unchanged.
7. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_hardening.py
uv run pytest -q tests/test_seed_path.py
uv run pytest -q tests/test_drain.py tests/test_daemon_composition.py
uv run pytest -q tests/test_specs.py
uv run pytest -q tests/test_stages.py
uv run pytest -q tests/test_tickets.py tests/test_kill_cli_activation.py
uv run pytest -q
```

## Regression
```
uv run pytest -q tests/test_hardening.py -k test_one_open_round_engine_wide
```
- carries: tests/test_hardening.py

## Definition of rejected
Reject the branch if any code still identifies a hardener or a round by its stem name or a ticket-directory glob, if two rounds can be open at once, if the round record is written before its commit Effect completes, or if `round_state` keeps a second classification of hardener terminals.

## Time budget
- expected: 90m
- stuck: 180m
