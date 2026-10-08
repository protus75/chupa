---
priority: P1
kind: feature
agent_tier: high
agent_effort: high
source: seed
state: confirmed
---

## Depends on
- phase3-continue-21

## Context
- chupa/merge.py
- chupa/serve.py
- tests/test_merge.py
- tests/test_mergequeue.py
- tests/test_serve.py
- chupa/runner.py
- chupa/daemon.py
- chupa/mergequeue.py

## Plan contract
- 19.I
- 19.P3.serve-merge-admission
- section 9

## Goal / Why
Serve-selected settled runs reach the existing serial admission queue and return their own admission result.

## Scope in / Scope out
Implement the complete governing contract in 19.P3.serve-merge-admission, including all Owner, Records, Observable and Tests obligations. The cited entry supplies every named invariant, record custody and sole writer; the renderer supplies its bytes. Cite, never copy unit text or invent replacement record shapes. This deep registry row starts high/high. Preserve its registry floor.

The additions chupa/runner.py and chupa/daemon.py are earned by the entry's explicit 19.L rule 5 caller/seam-owner closure: drive owns settlement and TicketWriter owns post-unwind handoff consumption. Both are existing Context. Re-grep merge, compose_pipeline, bind, prepare_pipeline, TicketWriter, DaemonAdmission, offer/process, inline assertions, production absence assertions and public surfaces across chupa/, eval/ and tests/ before any further closure addition. Preserve existing caller signatures where the entry requires them. The measured direct admission callers are runner.drive and tests/test_merge.py / tests/test_mergequeue.py; composition callers also include tests/test_daemon_composition.py. Default bind consumers (CLI run/drain, eval/shakeout/bench.py and their tests) remain inline. No further path is earned by those unchanged callers. The existing production harness remains an unchanged preservation suite. Never fence or migrate historical seeding tests.

Read the merged production owners and their direct callers before edits, including chupa/stages.py, chupa/__main__.py, chupa/control.py, chupa/drain.py, chupa/git.py, chupa/journal.py, chupa/effects.py, chupa/reconcile.py, chupa/restart.py and chupa/timers.py. Preserve the bootstrap dispatch result, inline admission signature, Journal(state_dir, clock) and append/read/close signatures, bootstrap on-entry reconciliation, and ordinary DaemonTasks exception propagation and cleanup. Journal stays the sole durable event writer, Box the sole queue-record writer, and ControlInbox the sole control-decision writer, under the governing citations.

Prove activation using the real CLI/async serve entrypoint and merged production-composition harness with scripted callbacks, injected seams, disposable synthetic repositories and asyncio barriers. The entry's Tests obligation governs the evidence and auditor; fabricated terminals, commits or records cannot substitute. Do not treat predecessor ready-fixture queue offers as activation evidence. Run every unfenced suite in Verification as unchanged preservation suites; neither fence nor embed those suites. Out: notify transport, recovery disposition, run-lane admission, live host work, real-model calls, wall-clock waits, config expansion and speculative records.

## Scope fence
- chupa/merge.py
- chupa/serve.py
- tests/test_merge.py
- tests/test_mergequeue.py
- tests/test_serve.py
- chupa/runner.py
- chupa/daemon.py

## Acceptance criteria
1. `uv run pytest tests/test_merge.py tests/test_mergequeue.py tests/test_serve.py tests/test_daemon_composition.py tests/test_rework.py tests/test_cli.py tests/test_drain.py tests/test_control.py tests/test_audit.py` exits 0 and fulfills `test_daemon_prechecks_precede_offer` exactly as governed by 19.P3.serve-merge-admission Tests, with Records custody and Observable evidence from that same citation.
2. `uv run pytest tests/test_merge.py tests/test_mergequeue.py tests/test_serve.py tests/test_daemon_composition.py tests/test_rework.py tests/test_cli.py tests/test_drain.py tests/test_control.py tests/test_audit.py` exits 0 and fulfills `test_bootstrap_pipeline_keeps_inline_admission` exactly as governed by 19.P3.serve-merge-admission Tests, with Records custody and Observable evidence from that same citation.
3. `uv run pytest tests/test_merge.py tests/test_mergequeue.py tests/test_serve.py tests/test_daemon_composition.py tests/test_rework.py tests/test_cli.py tests/test_drain.py tests/test_control.py tests/test_audit.py` exits 0 and fulfills `test_inline_admission_does_not_use_merge_queue` exactly as governed by 19.P3.serve-merge-admission Tests, with Records custody and Observable evidence from that same citation.
4. `uv run pytest tests/test_merge.py tests/test_mergequeue.py tests/test_serve.py tests/test_daemon_composition.py tests/test_rework.py tests/test_cli.py tests/test_drain.py tests/test_control.py tests/test_audit.py` exits 0 and fulfills `test_admission_mode_is_explicit` exactly as governed by 19.P3.serve-merge-admission Tests, with Records custody and Observable evidence from that same citation.
5. `uv run pytest tests/test_merge.py tests/test_mergequeue.py tests/test_serve.py tests/test_daemon_composition.py tests/test_rework.py tests/test_cli.py tests/test_drain.py tests/test_control.py tests/test_audit.py` exits 0 and fulfills `test_serve_routes_settled_run_to_composed_queue_once` exactly as governed by 19.P3.serve-merge-admission Tests, with Records custody and Observable evidence from that same citation.
6. `uv run pytest tests/test_merge.py tests/test_mergequeue.py tests/test_serve.py tests/test_daemon_composition.py tests/test_rework.py tests/test_cli.py tests/test_drain.py tests/test_control.py tests/test_audit.py` exits 0 and fulfills `test_serve_admission_rebases_regates_and_retires` exactly as governed by 19.P3.serve-merge-admission Tests, with Records custody and Observable evidence from that same citation.
7. `uv run pytest tests/test_merge.py tests/test_mergequeue.py tests/test_serve.py tests/test_daemon_composition.py tests/test_rework.py tests/test_cli.py tests/test_drain.py tests/test_control.py tests/test_audit.py` exits 0 and fulfills `test_serve_admission_refusal_keeps_main_green` exactly as governed by 19.P3.serve-merge-admission Tests, with Records custody and Observable evidence from that same citation.
8. `uv run pytest tests/test_merge.py tests/test_mergequeue.py tests/test_serve.py tests/test_daemon_composition.py tests/test_rework.py tests/test_cli.py tests/test_drain.py tests/test_control.py tests/test_audit.py` exits 0 and fulfills `test_serve_conflict_handoff_runs_after_admission_unwinds` exactly as governed by 19.P3.serve-merge-admission Tests, with Records custody and Observable evidence from that same citation.
9. `uv run pytest tests/test_merge.py tests/test_mergequeue.py tests/test_serve.py tests/test_daemon_composition.py tests/test_rework.py tests/test_cli.py tests/test_drain.py tests/test_control.py tests/test_audit.py` exits 0 and fulfills `test_serve_admission_holds_and_cleanup` exactly as governed by 19.P3.serve-merge-admission Tests, with Records custody and Observable evidence from that same citation.

## Verification
```
uv run pytest tests/test_merge.py tests/test_mergequeue.py tests/test_serve.py tests/test_daemon_composition.py tests/test_rework.py tests/test_cli.py tests/test_drain.py tests/test_control.py tests/test_audit.py
```

## Definition of rejected
A governing entry lacks a required fact or contradicts merged behavior, or a criteria-forced edit cannot be earned under the fence: return premise_failed naming the unit for section 11.4 hardening. Never invent missing facts.

## Time budget
- expected: 60m
- stuck: 90m
