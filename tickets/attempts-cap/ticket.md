---
priority: P1
kind: feature
source: human
state: confirmed
agent_tier: high
agent_effort: high
---

## Depends on
none

## Context
- chupa/status.py
- chupa/daemon.py
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
- In: the attempts count lives inside `caps.spent` (and is reported by `caps.spent_reason`), the one function every cap consumer already calls: `runner.drive` and `failure_terminal`, `daemon.TicketWriter.consume_handoff` (the merge-conflict path), and `drain._select` / `_settle`. Add no separate attempts check in any caller, `_admit`, or the scheduler. `serve`'s scheduler holds Reject-queue stems, so routing at the terminal is what stops a spent stem there.
- In: `failure_terminal` counts the terminal it is about to journal, so the failure that reaches `caps.attempts` is itself routed to the Reject queue with reason "attempts cap spent"; no further attempt and no further model call follows.
- In: the drain report's spent-cap line (`drain._settle`) shows the failed-attempt count for `attempts` ("attempts cap spent (5/5)"), not a `cap_consumed` draw count; attempts are derived from terminals and journal no `cap_consumed` event, so `audit`'s declared-cap check is unchanged.
- In: new shipped defaults in `Caps`: `diagnosis: 3`, `retry: 3`, `infra: 3`, `premise_bounce: 1`, `hardening: 1`, `attempts: 5`; `quarantine` and `poison` unchanged. The existing `retry <= diagnosis` load check stays.
- In: an operator keep (`confirm`) still resets every count through `lineage`, `attempts` included; the machine auto-keep still never resets one.
- In: `docs/host-contract.md` shows the new keys and defaults in both places it lists `caps`.
- In: `tests/test_caps.py` adds `test_attempts_cap_counts_every_failed_terminal` (five mixed failures spend it; drought, budget, abandoned, and settled terminals do not count; an operator keep resets it) and `test_attempts_cap_routes_to_reject_queue` (the stem routes with reason "attempts cap spent" and makes no model call).
- In: existing tests change only where they assert or rely on the old default values.
- In: update `docs/how-chupa-works.md` section 6.4 (the `attempts` cap, new defaults, what counts as a failed attempt), so the doc matches the code when this merges.
- In: if `uv run pytest -q` fails only on tests that also fail on the merge base, those failures are pre-existing: Check excuses them (base-red). Commit the work and list them in the run record; never stop with `premise_failed` for them.
- In: `eval/shakeout/runner.py`'s `_premise_false` scenario sets `premise_bounce: 2` on its own bench config (as `_identical_terminals` already sets `retry` and `diagnosis`), so the shakeout battery keeps proving one premise bounce without a re-offer under the new defaults.
- Out: the escalation ladder's rung order, quarantine and poison caps, THRESH spend budgets, and the plan text.

## Scope fence
- docs/how-chupa-works.md
- chupa/config.py
- chupa/caps.py
- chupa/runner.py
- chupa/drain.py
- docs/host-contract.md
- tests/
- eval/shakeout/runner.py
- chupa/daemon.py

## Acceptance criteria
1. `uv run pytest -q tests/test_caps.py tests/test_config.py` exits 0, including `test_attempts_cap_counts_every_failed_terminal` and `test_attempts_cap_routes_to_reject_queue`.
2. `load_config` with no `caps` key yields `diagnosis 3, retry 3, infra 3, premise_bounce 1, hardening 1, attempts 5, quarantine 5, poison 2`.
3. `uv run pytest -q` exits 0.
4. `docs/how-chupa-works.md` section 6.4 and `docs/host-contract.md` show the `attempts` cap and the new defaults.

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
