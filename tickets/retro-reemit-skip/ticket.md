---
state: confirmed
source: human
priority: P0
kind: bug
---

## Depends on
- none

## Context
- chupa/retro.py::Retro.__call__
- chupa/retro.py::Retro.emit_proposals
- chupa/retro.py::Retro.commit_report
- chupa/box.py::Box._enqueue
- chupa/box.py::RereportJournal.record

## On-demand
- tests/integration/test_retro_box.py

## Goal / Why
Every drain start runs the retro check (`Retro.__call__(forced=False)`), even when no retro is due. Before deciding, it calls `emit_proposals` for every completed retro report in the journal, and `emit_proposals` re-enqueues each of that report's proposals into the box. On 2026-11-11 that meant 40 reports and 55 proposals on every drain start. Every proposal is already in the box, and the re-enqueue is a no-op: its `occurrence_id` is deterministic, so the storm arrival and the re-report are deduplicated. But each enqueue still folds the full 24k-event journal several times (storm `record`, `_evidence`, `_history`, `recover`, and `RereportJournal.record`), and each `emit_proposals` re-reads the journal to find its own completion event.

Measured on a copy of `.chupa/state`, the not-due retro check took 52.4s and 372 `Journal.read()` calls before returning `None`. It is most of the 85-100s gap between `engine_start` and the first `stage_start` on every drain start (see `evidence/drain-start-journal-rereads.txt`).

When this ticket is done, a retro check whose reports' proposals are all in the box enqueues nothing. Crash recovery is kept: when a report committed but some of its proposals never reached the box, the next check enqueues only the missing ones.

## Scope in / Scope out
- In: `chupa/retro.py`:
  - `Retro.__call__` reads the journal once for its report scan and hands each completed report's event to `emit_proposals` instead of `emit_proposals` re-reading the journal to find it. `commit_report`'s call keeps working.
  - `emit_proposals` reads the box's messages once and skips every proposal whose `origin` (`retro-proposal/<report_key>/<proposal_id>`) already exists there.
  - The per-report `git show` stays; all 40 took 0.06s together.
- In: a unit test in `tests/unit/test_retro_proposal.py` (the coverage floor of 12 for `chupa/retro.py` in `test-gate.toml` is measured from the unit suite), a test in `tests/integration/test_retro_box.py`, and the carried reproducer `tests/regress_retro_reemit_skip.py`.
- Out:
  - `Journal.read()` performance, which is ticket `journal-incremental-read`.
  - Box, storm and re-report dedupe semantics.
  - Retro trigger selection and report writing.

## Scope fence
- chupa/retro.py
- tests/integration/test_retro_box.py
- tests/unit/test_retro_proposal.py
- tests/regress_retro_reemit_skip.py

## Acceptance criteria
1. `tests/integration/test_retro_box.py`: after a retro report has committed and its proposals are in the box, a second `Retro(...)(forced=False)` call that selects no trigger:
   - calls `Box.enqueue` zero times, not once per proposal;
   - leaves the box files and the journal byte-identical.
2. `tests/integration/test_retro_box.py`: when one of a committed report's two proposals is missing from the box, the next call enqueues exactly that one, and the box then holds both.
3. `tests/unit/test_retro_proposal.py` calls `Retro.emit_proposals` with a completed event, a fake `git._run` returning a receipt with two proposals, and a monkeypatched `storm_producer` whose fake box already lists one proposal's origin. Only the other proposal is enqueued, not both. It touches no disk or process.
4. `tests/regress_retro_reemit_skip.py` builds its own temporary repository, config, journal and box, and imports nothing from `tests/`. It seeds three committed retro reports whose proposals are already in the box, counts `Journal.read` calls during one `Retro(...)(forced=False)` call, and prints `pass` only when the count is at most 3. At base the count grows with each report and proposal.
5. The Regression command prints `{"regression_result": "pass"}` and exits 0 on the branch. At the merge base it prints `defect` and exits non-zero.
6. `./dev.py test` exits 0.

## Regression
```
uv run python tests/regress_retro_reemit_skip.py
```
- carries: tests/regress_retro_reemit_skip.py

## Verification
```
./dev.py test
```

## Definition of rejected
- A proposal missing from the box after a crash is no longer enqueued by the next retro check.
- A new journal event type or signal is added to mark proposals as emitted.
- Box, storm or re-report dedupe logic changes.

## Time budget
- expected: 40m
- stuck: 90m
