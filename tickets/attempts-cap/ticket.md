---
priority: P1
kind: feature
source: human
state: confirmed
---

## Depends on
none

## Context
- docs/how-chupa-works.md
- chupa/config.py
- chupa/caps.py
- chupa/runner.py
- chupa/drain.py
- docs/host-contract.md
- tests/test_caps.py
- tests/test_config.py

## Goal / Why
Each spine cap (`chupa/caps.py`) counts on its own and nothing bounds a ticket's total failures: with the shipped defaults (diagnosis 6, retry 6, infra 6, premise_bounce 2, hardening 3) one lineage can fail more than 20 times before any single cap is spent. `phase7-continue` failed 10 times without reaching a cap. A ticket that has not landed after a handful of attempts is badly authored or the model is guessing; it belongs with a human.

## Scope in / Scope out
- In: a new `caps.attempts` (shipped default 5): the total failed attempts per lineage. A failed attempt is a non-ok terminal `state_transition` of the stem (`gate_failed`, `premise_failed`, `infra_error`, `timeout`) inside the existing `lineage` window. Cost-free parks do not count: an `infra_error` with reason `provider_drought`, `budget_exceeded`, an `abandoned` reap, and settled or `rejected` terminals.
- In: `spent` treats `attempts` like the other spine caps, so a stem at its total routes to the Reject queue with the recorded reason "attempts cap spent", the drain stops re-offering it, and no further model call is made.
- In: new shipped defaults in `Caps`: `diagnosis: 3`, `retry: 3`, `infra: 3`, `premise_bounce: 1`, `hardening: 1`, `attempts: 5`; `quarantine` and `poison` unchanged. The existing `retry <= diagnosis` load check stays.
- In: an operator keep (`confirm`) still resets every count through `lineage`, `attempts` included; the machine auto-keep still never resets one.
- In: `docs/host-contract.md` shows the new keys and defaults in both places it lists `caps`.
- In: `tests/test_caps.py` adds `test_attempts_cap_counts_every_failed_terminal` (five mixed failures spend it; drought, budget, abandoned, and settled terminals do not count; an operator keep resets it) and `test_attempts_cap_routes_to_reject_queue` (the stem routes with reason "attempts cap spent" and makes no model call).
- In: existing tests change only where they assert or rely on the old default values.
- In: update `docs/how-chupa-works.md` section 6.4 (the `attempts` cap, new defaults, what counts as a failed attempt), so the doc matches the code when this merges.
- Out: the escalation ladder's rung order, quarantine and poison caps, THRESH spend budgets, and the plan text.

## Scope fence
- docs/how-chupa-works.md
- chupa/config.py
- chupa/caps.py
- chupa/runner.py
- chupa/drain.py
- docs/host-contract.md
- tests/

## Acceptance criteria
1. `uv run pytest -q tests/test_caps.py tests/test_config.py` exits 0, including `test_attempts_cap_counts_every_failed_terminal` and `test_attempts_cap_routes_to_reject_queue`.
2. `load_config` with no `caps` key yields `diagnosis 3, retry 3, infra 3, premise_bounce 1, hardening 1, attempts 5, quarantine 5, poison 2`.
3. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_caps.py tests/test_config.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if a stem can fail more than `caps.attempts` times in one lineage, if a cost-free park counts toward it, if the machine auto-keep resets any count, or if a test changes for any reason other than the new defaults or the new cap.

## Time budget
- expected: 60m
- stuck: 120m
