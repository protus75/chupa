---
state: confirmed
source: seed
priority: P1
kind: feature
agent_tier: high
agent_effort: medium
---

## Depends on
- plan-contract-section-render

## Context
- chupa/drain.py
- chupa/runner.py
- tests/test_drain.py
- tests/test_terminal.py

## Plan contract
- 19.L
- 19.P2
- section 11

## Goal / Why
`chupa/caps.py` owns the failure-spine caps for `retry`, `diagnosis`, and `infra`: one closed cap vocabulary, the ONE lineage-scoped journal cap fold, and the ONE `consume` writer. An `infra_error` or `timeout` terminal draws an `infra` unit. A stem whose `diagnosis` or `infra` cap is spent is never re-offered, and its report names the spent cap verbatim.

Why: section 11.1 requires every non-ok terminal to draw from a named budget. Today only the drain's re-offer draws anything (`retry`). A crashing provider call or a hung stage loops through re-offers that the infra budget never sees. The fold also lives as a private helper in `chupa/drain.py`, but the ladder (escalation rung on the retry draw body) and the diagnosis call (its pre-call cap check and draw) both need ONE fold and ONE writer to build on. A second copy in either of them is the dual path section 2 bans. The `retry` cap and its re-offer accounting already shipped with the Phase 1 drain: this ticket MOVES them into the new owner and does not rebuild them.

Owner (section 9 ownership law, 19.P2 NAMES): `chupa/caps.py` owns the cap vocabulary, the fold, the spent-cap predicate, and the `cap_consumed` writer. `chupa/runner.py` owns the run's terminal handler and calls the writer for the infra draw. `chupa/drain.py` owns re-offer eligibility and calls the fold and the predicate.

## Scope in / Scope out
- In: a new `chupa/caps.py` with:
  - `CAPS`, the closed vocabulary `("diagnosis", "retry", "infra")`, in this exact order. The predicate below checks caps in this order.
  - `draws(events, stem, cap) -> int`: the lineage fold. It counts the stem's `cap_consumed` events whose body names `cap`, across every `ticket_sha`, and counts a draw with no `ticket_sha` too. `ticket_sha` never selects, clears, or refills a budget.
  - `remaining(caps_config, events, stem, cap) -> int`.
  - `spent(caps_config, events, stem) -> str | None`: the first cap in `CAPS` with zero remaining, or None.
  - `consume(journal, stem, cap, ticket_sha)`: the one writer. It journals `cap_consumed` with body `{"cap": cap, "ticket_sha": ticket_sha}`.
  - `spent_reason(cap) -> str`: returns exactly `"<cap> cap spent"`.
  - `draws`, `remaining`, and `consume` raise `ValueError` naming `CAPS` for a cap outside the vocabulary (fail closed).
- In: `chupa/drain.py` drops its `cap_draws` and `RETRY_CAP` definitions and calls `chupa/caps.py` in their place. This is a rename in place with every call site updated. Its existing re-offer draw goes through `consume`, with an unchanged body and position (the draw still precedes the `running` transition).
- In: the drain re-offers a parked stem only while `spent(...)` is None, which also requires `retry` budget. A stem with a spent `diagnosis` or `infra` cap is parked and reported with `spent_reason` plus the `(drawn/cap)` count, in the same shape as the existing `retry cap spent (n/n)` line. The paved road is the same one the retry-cap-spent park already prints. Existing retry report lines stay byte-identical.
- In: `chupa/runner.py` `drive`: when the run's terminal outcome is `infra_error` or `timeout`, it calls `consume(..., "infra", ticket_sha)` BEFORE journaling the terminal `state_transition` (section 11.2's dispatch-precedes-journal order). `ticket_sha` is the git blob SHA of the committed `tickets/<stem>/ticket.md`, read the way `chupa/drain.py` reads it. No other outcome draws `infra`.
- Out: the `premise_bounce` cap and its draw. Both land with the escalation-ladder and Reject-queue seeds, beside their release verbs (section 2: a hold never lands before its release). Do not add `premise_bounce` to `CAPS`.
- Out: the diagnosis call and its draw (the next seed batch). This ticket only makes a spent `diagnosis` cap block a re-offer.
- Out: Reject-queue routing, the `routed: reject_queue` marker, `confirm`/`reject`, the auto-keep, and the escalation rung. A spent cap parks and reports exactly as the Phase 1 retry-cap-spent park does.
- Out: harvest, the drought exemption (no drought classification exists yet), the driver's in-stage re-prompt allowance, and any change to `chupa/config.py`. The `Caps` model already carries every budget.

## Scope fence
- chupa/caps.py
- tests/test_caps.py
- chupa/drain.py
- chupa/runner.py
- tests/test_drain.py

## Acceptance criteria
1. `chupa/caps.py` defines `CAPS == ("diagnosis", "retry", "infra")`, and `chupa/drain.py` no longer defines `cap_draws` or `RETRY_CAP`. Both are checked by the `python -c` command in `## Verification`.
2. `tests/test_caps.py` proves the fold. It counts only `cap_consumed` events naming the asked cap and only for the asked stem. It counts draws across different `ticket_sha` values and draws carrying no `ticket_sha`. It returns `remaining == cap - draws`.
3. `tests/test_caps.py` proves that `consume`, `draws`, and `remaining` raise `ValueError` on a cap name outside `CAPS`, and that `consume` journals exactly `{"cap": ..., "ticket_sha": ...}` on the stem.
4. `tests/test_caps.py` drives the production runner through `chupa.__main__.main` with a FakeLLM whose implement call raises. The run terminals `infra_error`, and exactly one `infra` `cap_consumed` carrying the ticket's committed blob SHA is journaled immediately before that terminal `state_transition`. A `timeout` terminal draws the same way (the test may drive `runner.drive` with a stage seam returning `timeout`). A `gate_failed` terminal draws no `infra` unit.
5. `tests/test_caps.py` proves the drain never re-offers a parked stem whose `infra` cap is spent, and reports `infra cap spent (n/n)` even while `retry` budget remains. It proves the same for a spent `diagnosis` cap with `diagnosis cap spent (n/n)`.
6. Every existing test in `tests/test_drain.py` passes with its assertions unchanged. Only its import of the moved fold and cap name changes.
7. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run python -c "import chupa.caps as c, chupa.drain as d; assert c.CAPS == ('diagnosis', 'retry', 'infra'); assert not hasattr(d, 'cap_draws') and not hasattr(d, 'RETRY_CAP')"
uv run pytest -q tests/test_caps.py tests/test_drain.py tests/test_terminal.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- A second cap fold or `cap_consumed` writer survives outside `chupa/caps.py`.
- `premise_bounce` enters the vocabulary.
- An edit or a `ticket_sha` change refills a budget.
- The infra draw lands after the terminal `state_transition`.
- An existing `tests/test_drain.py` assertion is weakened.
- The diff touches a file outside the fence.

## Time budget
- expected: 60m
- stuck: 120m
