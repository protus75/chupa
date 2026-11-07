---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- none

## Context
- chupa/driver.py
- chupa/triage.py
- chupa/observe.py
- vscode-chupa/extension.js
- tests/test_watch.py
- tests/test_driver.py

## Goal / Why
In the extension's Recent Steps tree, a triage step looks like a generic stage. Its row reads `Triage start` or `Triage end (ok)` with the `debug-start` or `pass` icon, and it does not say which Suggestion Box message was triaged. The operator asked for three changes (2026-11-07):
- Triage gets its own icon.
- The icon is uncolored (theme foreground, white in a dark theme) when the step starts, and green when it completes.
- The row names the box message number.

The data is not in the engine log today. Triage calls `driver.run` with `run_seq=message.seq`, the box number (message `000337-…` has `seq` 337). But the driver's `stage_start` and `stage_end` events log only `stem`, `attempt` and `surface`, and for triage the stem is the pseudo-stem `triage`.

## Scope in / Scope out
- In: `chupa/driver.py` `Driver.run`: the `stage_start`/`stage_end` log context gains `"run_seq": seq`. `seq` is the run sequence the method already computes, so a ticketless surface logs the `run_seq` its caller passed. No other log field changes.
- In: `chupa/observe.py` `recent_steps`:
  - `triage` joins the surfaces that get their own kind prefix, so its kinds are `triage_start`, `triage_ok` and `triage_failed`.
  - A triage row's text names the box number: `Triage #337 start` and `Triage #337 end (ok)`, using the event's `run_seq`.
  - An event without `run_seq` (log lines written before this change) keeps today's `Triage start` text.
  - Every other surface's text and kind are unchanged.
- In: `vscode-chupa/extension.js` `StepsTree` icon table:
  - `triage_start` is `['inbox']`, with no color.
  - `triage_ok` is `['inbox', 'testing.iconPassed']` (green).
  - `triage_failed` is `['inbox', 'testing.iconFailed']`, matching the other surfaces' failed rows.
  - No other JavaScript changes.
- In: `tests/test_watch.py`: the following must hold.
  - `recent_steps` maps a triage `stage_start` with `run_seq` 337 to kind `triage_start` and text `Triage #337 start`, not `stage_start` or `Triage start`.
  - The matching `stage_end` with outcome `ok` maps to `triage_ok` and `Triage #337 end (ok)`.
  - A triage event without `run_seq` keeps the text `Triage start`.
  - `test_recent_steps_merges_engine_and_stage_events` keeps passing unchanged.
- In: `tests/test_driver.py`: a ticketless `run` with `ticket=None, run_seq=337` writes `stage_start` and `stage_end` log events whose `run_seq` is 337, not the journal-derived sequence.
- Out:
  - Step `path` resolution. For triage it points at the nonexistent `tickets/triage/ticket.md`; that is a separate problem.
  - The Suggestion Box view, `media/*.js`, `package.json`, `chupa/triage.py`, and the author, retro, and rework surfaces' kinds.

## Scope fence
- chupa/driver.py
- chupa/observe.py
- vscode-chupa/extension.js
- tests/test_watch.py
- tests/test_driver.py

## Acceptance criteria
1. `./dev.py test tests/test_watch.py` exits 0, including the triage test. That test rules out the generic `stage_start` kind, triage text without the box number, and dropped text for events without `run_seq`.
2. `./dev.py test tests/test_driver.py` exits 0, including the `run_seq` 337 log test.
3. `vscode-chupa/extension.js` maps `triage_start`, `triage_ok` and `triage_failed` to the `inbox` icon, with no color, `testing.iconPassed` and `testing.iconFailed` respectively.
4. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/test_watch.py
./dev.py test tests/test_driver.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following happens:
- The JavaScript builds the `#N` text or reads `run_seq`.
- Any non-triage step's text or kind changes.
- The journal gains a field.

## Time budget
- expected: 25m
- stuck: 75m
