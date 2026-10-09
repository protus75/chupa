---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase4-continue

## Context
- chupa/watchdog.py
- chupa/notify.py
- tests/test_watchdog.py
- chupa/providers.py
- chupa/seams.py
- chupa/driver.py
- chupa/thresh.py
- tests/test_daemon_composition.py

## Plan contract
- 19.I
- 19.P4.watchdog-detector
- section 9
- 19.P4.watchdog-event-stream
- 19.P4.notify-transport

## Goal / Why
Prove dormant deterministic spend/progress detection and hard-deadline cleanup.

## Scope in / Scope out
Construct only the detector. The cited entry supplies Owner, Records, Observable and Tests; chupa/watchdog.py owns deterministic spend/progress and time-region decisions, and chupa/notify.py retains notification custody. Consume the merged event stream and transport through injected seams. Keep production calls unwatched until watchdog-activation and preserve existing public notification signatures, spool capture and harvest behavior.

Prove real scope-path changes rather than tool requests, plan-unit range confinement and progress observation in each time region. Exercise duplicate-event accounting, optional usage, call-start estimate charging even for hung calls, strict threshold crossing and the existing missing-cost refusal. Follow the entry's first-completed-call basis and calibration rule; never derive the active basis from its own spend. test_spend_metering_and_threshold must assert the exact 1, 2, 0.5 USD sequence, equality at 3 and crossing at 3.5, identity-local bases, zero basis, re-prompt/progress retention and new-run reset. A hung calibration remains subject to the hard deadline. Prove warning retention through progress/retries, fresh-run warning identity, cap-wait exclusion, unset notification behavior, synchronous abort before cancellation and awaited cleanup. Cap-wait exclusion consumes the existing chupa/thresh.py Admission.waited_seconds / provider_cap_wait record through an injected seam, with no change to thresh.py; it remains outside the fence. Pin the corpus adapter-event fixtures inline as Python literals in tests/test_watchdog.py, with expected verdicts; no standalone fixture files or model judge.

Named obligations: test_spend_resets_only_on_observed_scope_mutation, test_spend_metering_and_threshold, test_watchdog_regions_and_notify_once, test_watchdog_hard_timeout_group_cleanup, test_detector_is_dormant, test_spiral_corpus. test_detector_is_dormant must discriminate the real production composition and fail if detection is wired. Reuse CoreRig from tests/test_daemon_composition.py as a read-only reference, never a substitute production graph. Run tests/test_notify.py unchanged as a preservation suite, outside the fence and Context.

Read Context and the governing entries before editing. Out: activation, provider cooldown/selection, new config or durable records, altered notification keys, second spool writers, historical seeding fixtures and ticket/plan edits.

## Scope fence
- chupa/watchdog.py
- chupa/notify.py
- tests/test_watchdog.py

## Acceptance criteria
1. `uv run pytest tests/test_watchdog.py tests/test_notify.py` exits 0 proving all six named detector obligations: scope mutation, metering, time regions, warning identity, abort cleanup and corpus replay.
2. `uv run pytest tests/test_watchdog.py tests/test_notify.py` exits 0 proving production dormancy and unchanged stream/transport behavior.

## Verification
```
uv run pytest tests/test_watchdog.py tests/test_notify.py
```

## Definition of rejected
Missing or contradictory governing facts return premise_failed, kind: spec_gap, naming the owning cited entry. A criteria-forced path outside the earned fence returns premise_failed; repair the contract or closure rather than invent facts or extend the registry.

## Time budget
- expected: 60m
- stuck: 90m

