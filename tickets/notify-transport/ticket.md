---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase3-exit
- watchdog-event-stream

## Context
- chupa/config.py
- chupa/seams.py
- chupa/serve.py
- chupa/__main__.py
- tests/test_config.py
- tests/test_serve.py
- chupa/effects.py
- chupa/providers.py
- chupa/redact.py
- chupa/storm.py
- chupa/mergequeue.py

## Plan contract
- 19.I
- 19.P4.notify-transport
- section 6
- section 13
- section 15

## Goal / Why
Deliver existing escalation evidence through the configured notification command with journal-backed replay.

## Scope in / Scope out
Implement only notify-transport. Its injected entry governs Owner, Records, Observable and Tests; chupa/notify.py owns the new transport and pending-escalation reconciliation. Read the merged seams, Effects, config, serve composition and emitter records first, and read chupa/journal.py from disk for its event-write contract. The preceding stream seed's newly created paths are not Context in this admission. No change to existing public call signatures or constructor arity is presumed: retain the composition's current callers while giving notifications their distinct executor at the CLI root.

Implement the entry's named tests: test_notify_effect_once_and_conservative_resend, test_notify_key_domains, test_notify_seam_uses_argv_and_secret_free_env, test_notify_refuses_malformed_argv, test_serve_reconciles_notifications_at_startup_and_poll and test_serve_unset_notify_warns_once_and_preserves_pending. Prove through the real serve graph that startup and later maintenance deliver old and new storm, red-streak and tree-mismatch evidence, that restart suppresses completed keys, and that failed delivery remains pending. Preserve config's existing unset/valid/null tests. Test environment removal and diagnostic scrubbing from configured secrets, using the real argv seam with a notification executor separate from work and re-exec.

At authoring, tests/test_storm_notification_activation.py::test_storm_activation_does_not_hold_dispatch_or_notify was read: its Effects.run refusal covers run/drain, not serve. The entry's serve startup/poll activation does not contradict those assertions, so no fence addition is earned. Run that file unchanged as a preservation suite, retaining its dispatch order, lock, resume decision, hold release and pending Box assertions. The deliverable changes transport only, never the emitter, control decisions or hold semantics. Read direct callers and grep old notify absence assertions, operation allowlists and emitter identities across chupa/, eval/ and tests/ before writing; read delimiter-bearing harnesses from disk. Existing fenced paths are Context and no On-demand partition is earned. If the required implementation does contradict another negative test, return premise_failed naming the missing fence rather than widen this seed.

Effects remains the only effect-record writer, Journal the event writer, Box the queue writer and ControlInbox the decision writer. Keep serve's startup recovery and cleanup behavior, including ordinary DaemonTasks exception propagation, intact. Run tests/test_effects.py and tests/test_daemon_composition.py unchanged as preservation suites, without embedding or fencing them. Out: watchdog producers/activation, new escalation signals, provider changes, dispatch or admission changes, new knobs, historical test migration, ticket/plan edits and live state.

## Scope fence
- chupa/notify.py
- chupa/config.py
- chupa/seams.py
- chupa/serve.py
- chupa/__main__.py
- tests/test_notify.py
- tests/test_config.py
- tests/test_serve.py

## Acceptance criteria
1. `uv run pytest tests/test_notify.py tests/test_config.py tests/test_serve.py` exits 0 proving all six entry test obligations, including production reconciliation, replay, pending failures, status-only startup and secret-free argv execution.
2. `uv run pytest tests/test_storm_notification_activation.py` exits 0 unchanged, preserving run/drain's dispatch, hold, resume, lock, queue and no-notify assertions.
3. `uv run pytest tests/test_effects.py tests/test_daemon_composition.py` exits 0 preserving write-ahead custody, real composition, recovery and cleanup.

## Verification
```
uv run pytest tests/test_notify.py tests/test_config.py tests/test_serve.py
uv run pytest tests/test_storm_notification_activation.py
uv run pytest tests/test_effects.py tests/test_daemon_composition.py
```

## Definition of rejected
Missing or contradictory needed facts return premise_failed, kind: spec_gap, naming 19.P4.notify-transport. A required path outside this earned fence returns premise_failed naming it; correct the closure rather than invent a transport or widen the row.

## Time budget
- expected: 60m
- stuck: 90m
