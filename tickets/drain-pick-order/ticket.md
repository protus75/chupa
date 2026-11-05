---
state: confirmed
source: human
priority: P0
kind: chore
---

## Depends on
- serve-self-upgrade

## Context
- chupa/drain.py
- tests/test_drain.py
- chupa/scheduler.py

## On-demand
- docs/how-chupa-works.md

## Goal / Why
Drain's `_select` returns every fresh ticket before any re-offer, whatever their priority or age. An operator-kept ticket that is ready to run therefore waits behind all newer work: `implement-test-rules` and `remove-plan-gap-hardening` (P1, kept 2026-11-05) sat behind newer P1 and P2 tickets. The serve scheduler (`chupa/scheduler.py`) already picks one list by `sort_key`. After this change drain picks the same way: lowest priority value first, then the oldest authored ticket, then stem, whether the pick is fresh or a re-offer.

## Scope in / Scope out
- In: `chupa/drain.py` `_select`: one candidate list ordered by `sort_key`. Each entry keeps its re-offer flag, so `_run_one` still draws `retry` for a re-offer exactly as today. Eligibility (held, budget, storm, drought, over-budget, Reject-queue rules) is unchanged. The docstring states the order.
- In: `tests/test_drain.py`: tests for the new order. Update any existing test that asserts fresh-before-re-offer to assert the `sort_key` order instead.
- In: `docs/how-chupa-works.md` section 7.1 step 3: replace "Fresh tickets run before re-offers" with the single order.
- Out: quiescence re-offers and machine keep; eligibility; `sort_key`; the serve scheduler.

## Scope fence
- chupa/drain.py
- tests/test_drain.py
- tests/test_drain_upgrade.py
- tests/test_drain_reentry.py
- tests/test_seed_successor.py
- docs/how-chupa-works.md

## Acceptance criteria
1. Given an eligible P1 re-offer authored before an eligible fresh P1 ticket, `_select` returns the re-offer with its re-offer flag set. A test fails if the fresh ticket goes first. Checked by `uv run pytest tests/test_drain.py`.
2. Given an eligible P2 re-offer and an eligible fresh P1 ticket, the fresh P1 goes first. Checked by `uv run pytest tests/test_drain.py`.
3. A re-offer picked this way draws exactly one `retry` cap unit, as today. Checked by `uv run pytest tests/test_drain.py`.
4. `docs/how-chupa-works.md` section 7.1 states the single order.
5. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_drain.py tests/test_drain_upgrade.py
uv run pytest -q
```

## Definition of rejected
Eligibility changes; `sort_key` changes; re-offers stop drawing `retry`; fresh tickets are still preferred over an older re-offer at the same priority.

## Time budget
- expected: 30m
- stuck: 90m
