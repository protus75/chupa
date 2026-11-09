---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
none

## Context
- chupa/stats.py::window_start
- chupa/stats.py::project_stats
- chupa/journal.py::Event
- tests/integration/test_stats.py::test_projection_windows_durations_cycles_and_invoices

## Goal / Why
`chupa/stats.py` writes the same fold twice: "for each ticket, the latest `STATE_TRANSITION` event whose `to` is in `SETTLED` and whose `ts` is at or before `now`". `window_start` (the `t` unit branch) keeps the fold's timestamps in `latest`; `project_stats` keeps the events in `settled` before narrowing them to the window. Two copies of one rule can drift apart; after this change one private function owns it.

## Scope in / Scope out
- In: `chupa/stats.py` gains one private function `_latest_settled(events, now)` returning `{stem: Event}`, the last event per stem in journal order matching that exact condition (`type == EventType.STATE_TRANSITION`, truthy `ticket`, `body.get("to") in SETTLED`, `datetime.fromisoformat(ts) <= now`).
- In: `window_start`'s `t` branch takes its times from `_latest_settled(events, now)` (each event's `datetime.fromisoformat(ts)`), replacing its loop; the sort and return expression stay as they are.
- In: `project_stats` builds `settled` from `_latest_settled(events, now)`, replacing its loop; the following `inside` narrowing line stays as it is.
- In: new `tests/unit/test_stats.py`, a unit test with no disk access that builds `chupa.journal.Event` values directly (`Event(1, EventType.STATE_TRANSITION, ts, stem, None, {"to": state})`, aware-UTC `ts` strings). Events: stem `a` `merged` at 10:00, stem `a` `rejected` at 11:00, stem `b` `merged` at 13:00; `now` is 12:00.
  - `window_start(events, now, "1t")` equals 11:00, not 13:00 (a settle after `now` is excluded) and not 10:00 (a later settle replaces an earlier one for the same stem).
  - `project_stats(events, {}, {}, now=now, window="7d")["throughput"]["settled"]` equals `{"merged": 0, "already_satisfied": 0, "rejected": 1}`, not a count that includes `a`'s earlier `merged`.
- Existing coverage: `test_projection_windows_durations_cycles_and_invoices` in `tests/integration/test_stats.py` already covers the `2t` window cutoff and the settled projection (`cycles`, `ladder.outcomes`); it stays unchanged and must still pass.
- Out: the `escalated` set and the `terminals` / `escalations` lists in `project_stats` (lines ~120-122) use different filters (`dispatch == "escalate"`, `to not in {...}`) and are not this fold; the `events` pre-filter at the top of `project_stats`; the main-loop `> now` skip; `chupa/__main__.py`; any change to stats output.

## Scope fence
- chupa/stats.py
- tests/unit/test_stats.py

## Acceptance criteria
1. `grep -c 'in SETTLED' chupa/stats.py` prints `1`, not `2`: the condition appears once, inside `_latest_settled`.
2. `./dev.py test tests/unit/test_stats.py` exits 0; its test asserts `window_start(events, now, "1t")` is 11:00, not 13:00 or 10:00, and the settled throughput is `rejected: 1`, `merged: 0`.
3. `./dev.py test tests/integration/test_stats.py` exits 0 with `tests/integration/test_stats.py` unchanged.
4. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/unit/test_stats.py
./dev.py test tests/integration/test_stats.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- the settled condition still appears in more than one place in `chupa/stats.py`;
- `_latest_settled` is public, takes extra parameters or flags, or returns timestamps instead of events;
- `tests/integration/test_stats.py` is edited, or any stats output value changes;
- the new unit test reads or writes the filesystem.

## Time budget
- expected: 15m
- stuck: 45m
