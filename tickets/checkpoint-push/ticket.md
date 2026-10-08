---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase3-continue-19

## Context
- chupa/daemon.py
- chupa/git.py
- tests/test_git.py
- tests/test_mergequeue.py
- chupa/journal.py
- chupa/effects.py
- chupa/timers.py
- chupa/box.py
- chupa/storm.py
- chupa/config.py
- chupa/seams.py
- chupa/__main__.py

## Plan contract
- 19.I
- 19.P3.checkpoint-push
- section 10

## Goal / Why
Local main gains a dormant restart-safe checkpoint push boundary whose failed windows retry without delaying admission.

## Scope in / Scope out
19.P3.checkpoint-push is the complete governing contract for every Owner, Records, Observable and Tests obligation. The renderer injects those parts verbatim: implement every named Tests obligation, record custody and sole writer through that citation; never copy unit text into this seed or invent caller-read records. chupa/checkpoint.py is owned by its cited Owner. Production invocation stays dormant until serve-activation.

Keep the registry floor exactly. Add only the public Git operation specified by the entry; migrate only its pinned public-operation enumeration in tests/test_git.py::test_option_shaped_or_empty_refs_are_refused_before_exec and extend test_op_argv as governed there. tests/test_mergequeue.py stays unchanged and embedded solely because the registry floor explicitly includes it. No public signature changes or direct caller migration are earned. Before editing re-grep flipped symbols, old assertion values, public surfaces, production absence assertions and direct callers across chupa/, eval/ and tests/. Do not migrate historical seeding tests.

Read real CLI run/drain and build_daemon_core and the merged production-composition harness before writing; preservation suites are read as needed and run unchanged in Verification only. Preserve Journal(state_dir, clock) and append/read/close signatures and all direct callers, bootstrap on-entry reconciliation, inline admission and ordinary DaemonTasks exception propagation and cleanup. Journal remains the sole durable event writer, Box the sole queue-record writer and ControlInbox the sole control-decision writer. The cited Records governs failure occurrence identity and crash replay; use the supplied production storm_producer Box and existing arrival_id, never a replacement writer. Exercise through injected seams, scripted callbacks, disposable repositories and asyncio barriers, never live remotes, real-model calls or wall-clock waits.

Out: serve activation, daemon-mode merge routing, notification transport, optional mirror, config flags, task graphs, manual HGATE release, verification filtering, unearned records and unrelated refactors.

## Scope fence
- chupa/checkpoint.py
- chupa/daemon.py
- chupa/git.py
- tests/test_checkpoint.py
- tests/test_git.py
- tests/test_mergequeue.py

## Acceptance criteria
1. `uv run pytest tests/test_checkpoint.py tests/test_git.py tests/test_mergequeue.py tests/test_effects.py tests/test_restart_timers.py tests/test_box.py tests/test_daemon_composition.py` exits 0, proving the complete Owner, Records, Observable and Tests contract in 19.P3.checkpoint-push, including its exact shapes, writers and failure/replay custody.
2. The same Verification command exercises all named obligations: `test_checkpoint_merge_and_daily_triggers`, `test_checkpoint_success_advances_once`, `test_checkpoint_failed_push_refires`, `test_checkpoint_failure_occurrence_identity`, `test_checkpoint_failure_report_crash_replay`, `test_checkpoint_crash_windows`, `test_checkpoint_timer_survives_restart_and_roll`, `test_checkpoint_boundary_is_dormant`, `test_op_argv`, `test_option_shaped_or_empty_refs_are_refused_before_exec`. Each name covers its entire cited obligation, not only its title.
3. `uv run pytest tests/test_checkpoint.py tests/test_git.py tests/test_mergequeue.py tests/test_effects.py tests/test_restart_timers.py tests/test_box.py tests/test_daemon_composition.py` proves dormant production wiring and unchanged admission/main-green behavior; only the cited Git public-operation test changes and every unfenced preservation suite runs unchanged.

## Verification
```
uv run pytest tests/test_checkpoint.py tests/test_git.py tests/test_mergequeue.py tests/test_effects.py tests/test_restart_timers.py tests/test_box.py tests/test_daemon_composition.py
```

## Definition of rejected
Return premise_failed naming a missing or contradictory 19.P3.checkpoint-push fact for section 11.4 hardening, or a criteria-forced path outside this fence; never invent records, replacement writers or a second path.

## Time budget
- expected: 60m
- stuck: 120m
