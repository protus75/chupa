---
priority: P0
kind: bug
agent_tier: high
agent_effort: high
source: human
state: confirmed
---

## Depends on
none

## Context
- chupa/runner.py
- chupa/drain.py
- chupa/caps.py
- chupa/audit.py
- chupa/journal.py
- chupa/config.py
- tests/test_seed_path.py
- tests/test_drain.py
- tests/test_caps.py

## Plan contract
- section 11.1
- section 11.4

## Goal / Why
A spec-gap hold can never loop. One round-state fold over the closed run-state vocabulary decides, for both the runner (await the round or file the next) and the drain (hold or release), whether a hardening round is open, and every held spec-gap terminal draws one unit of the lineage-scoped `hardening` cap.

Why: section 11.4 defines ROUND STATE as ONE fold used by the terminal handler and the eligibility fold, and section 11.1 makes a held spec-gap terminal draw from the `hardening` cap. Today `chupa/runner.py` `hold_on_hardening` treats any round whose hardener is not `merged` as open, while `chupa/drain.py` `awaited_hardening` treats `merged` and `already_satisfied` as closed and releases the hold. A hardener that ends `already_satisfied` therefore releases the stem, whose re-run draws nothing, re-detects the same gap, re-awaits the same finished round, and is released again. That cycle ran 334 times for `serve-activation`. The hardening cap is also counted per unit from `tickets/harden-*` directories, outside the journal cap fold.

## Scope in / Scope out
- In: a new module `chupa/hardening.py` owning `RoundState = Literal["open", "closed"]`, the closed map `ROUND_STATES` from every run state (`running` plus each member of `chupa.journal.TERMINAL_STATES`) to a `RoundState`, and `round_state(events, hardener) -> RoundState`. The fold is `closed` once any terminal `state_transition` of the hardener maps to `closed` or carries `routed: reject_queue`; otherwise it is `open`. The map follows section 11.4: `merged`, `already_satisfied`, `rejected`, and `premise_failed` close; `gate_failed`, `invalid_artifact`, `timeout`, and `infra_error` without `routed`, `abandoned`, `budget_exceeded`, and `running` stay open.
- In: `chupa/runner.py` `hold_on_hardening` asks `round_state` whether a row's latest round is open, in place of `!= "merged"`. Before awaiting or filing anything, it checks the lineage `hardening` cap. When the cap is spent, the terminal is `{to, stage, reason: "hardening cap spent", dispatch: "reject_queue", routed: "reject_queue"}`, with no signal, no draw, and no filing. Otherwise it draws exactly one `hardening` unit through `caps.consume`, using the stem's committed `ticket.md` blob as `ticket_sha`, and then awaits or files per row as today. The per-row `len(rounds) >= caps.hardening` glob count is deleted.
- In: `chupa/drain.py` `awaited_hardening` returns the awaited hardeners whose `round_state` is `open`, replacing the `SETTLED` membership test.
- In: `chupa/caps.py` keeps `CAPS` as the four spine caps that `spent` folds over. A new `DECLARED_CAPS = CAPS + ("hardening",)` is the set `draws`, `remaining`, and `consume` accept. `chupa/audit.py` defaults its declared-cap check to `DECLARED_CAPS`. In `chupa/config.py`, the `Caps.hardening` comment names the lineage scope.
- Out: hardening-ticket identity, naming, and composition; the `spec_gap_hold` signal; detection of spec gaps; the auto-keep; Reject-queue release; the premise park. Successor tickets own those.

## Scope fence
- chupa/hardening.py
- chupa/runner.py
- chupa/drain.py
- chupa/caps.py
- chupa/audit.py
- chupa/config.py
- tests/test_hardening.py
- tests/test_seed_path.py
- tests/test_drain.py

## Acceptance criteria
1. `uv run pytest -q tests/test_hardening.py` exits 0. It includes `test_round_state_maps_every_run_state`, which asserts `set(ROUND_STATES) == TERMINAL_STATES | {"running"}` and asserts each value is `open` or `closed`, so a new run state fails the suite until it is mapped. It also includes `test_round_state_closes_per_section_11_4`, which journals each terminal for one hardener and asserts the fold's result, including that a `gate_failed` carrying `routed: reject_queue` closes the round and that a later `running` never reopens a closed one. It also includes `test_hardening_draws_pass_the_declared_cap_audit`, which asserts that `audit` reports no `declared_cap` violation for a `hardening` draw.
2. `uv run pytest -q tests/test_seed_path.py` exits 0. It includes a new `test_already_satisfied_or_rejected_hardener_never_re_holds_forever`, parametrized over `already_satisfied` and `rejected`. It holds a registry-row seed on round 1 through `hold_on_hardening`, journals round 1's hardener terminal, and asserts that `awaited_hardening` no longer returns that hardener. It then asserts that the next `hold_on_hardening` files round 2 rather than awaiting round 1. It also asserts that every held terminal journals exactly one `cap_consumed {cap: hardening}`, and that once `caps.hardening` units are drawn the next call journals `reason: "hardening cap spent"` with `routed: reject_queue` and files nothing.
3. In `tests/test_seed_path.py`, `test_spent_hardening_cap_routes_the_stem_to_the_reject_queue` drives the cap through journaled `hardening` draws instead of pre-created `tickets/harden-*` directories. The other hardening tests there assert one `hardening` draw where they now assert none.
4. `uv run pytest -q tests/test_drain.py tests/test_caps.py tests/test_audit.py tests/test_daemon_composition.py tests/test_kill_cli_activation.py` exits 0 unchanged.
5. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_hardening.py
uv run pytest -q tests/test_seed_path.py
uv run pytest -q tests/test_drain.py tests/test_caps.py tests/test_audit.py tests/test_daemon_composition.py tests/test_kill_cli_activation.py
uv run pytest -q
```

## Regression
```
uv run pytest -q tests/test_seed_path.py -k test_already_satisfied_or_rejected_hardener_never_re_holds_forever
```
- carries: tests/test_seed_path.py

## Definition of rejected
Reject the branch if the runner and the drain classify a hardener terminal through different code, if `spent` begins to fold over `hardening` (a spent hardening cap must never block dispatch), if a held spec-gap terminal draws no `hardening` unit, or if the regression test passes on the merge base.

## Time budget
- expected: 60m
- stuck: 150m
