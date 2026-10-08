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

## Context
- chupa/providers.py
- chupa/seams.py
- tests/test_providers.py
- chupa/llm.py
- chupa/driver.py
- chupa/runner.py
- chupa/redact.py

## Plan contract
- 19.I
- 19.P4.watchdog-event-stream
- section 6
- section 9
- section 15

## Goal / Why
Deliver scrubbed adapter events to a directly constructed consumer before the provider call ends.

## Scope in / Scope out
Implement the watchdog-event-stream row only. The injected 19.P4.watchdog-event-stream contract supplies Owner, Records, Observable and Tests. chupa/watchdog.py owns the new per-call consumer; the existing process and adapter owners remain responsible for delivery and capture. Build construction evidence against the production provider and process seams while production Driver calls retain their unwatched behavior.

Carry the entry's named obligations: test_event_consumer_receives_before_terminal, test_event_consumer_preserves_tool_identity_and_optional_usage, test_event_stream_is_dormant, test_inflight_events_are_scrubbed_and_capture_is_preserved and test_event_callback_unwind_kills_group. Exercise both provider shapes, incomplete stdout chunks, stderr drainage and exceptional unwind through the real process-group seam. Retain the provider tests for results, estimates, stdin delivery, surface write grants and abort binding. Run tests/test_git.py unchanged to preserve the process seam's existing timeout, cancellation, spawn and inherited-stdio obligations; it is a preservation suite, not an edit target.

Read the production call chain and direct callers across chupa/, eval/ and tests/ before editing. Inspect eval/harness.py, eval/shakeout/providers.py and eval/daemon_soak.py from disk; delimiter-bearing files cannot be embedded. The entry's absent callback must preserve current callers' arguments and behavior; do not migrate unrelated ProcessExec callers or change LLMRequest/LLMResult or constructor arity. The existing fenced paths are embedded. No additional caller, allowlist or contradicted dormancy edit was earned at authoring. If implementing the entry actually forces another path, return premise_failed naming that closure instead of adding a parallel call path.

Journal retains durable-event ownership; the provider retains spool ownership. No detector, push, spend kill, polling of finished spools, cleanup redesign, new persisted record or activation belongs here. Later registry rows own those changes. Do not edit historical seeding tests, tickets, the plan, live state or preservation suites.

## Scope fence
- chupa/watchdog.py
- chupa/providers.py
- chupa/seams.py
- tests/test_watchdog.py
- tests/test_providers.py

## Acceptance criteria
1. `uv run pytest tests/test_watchdog.py tests/test_providers.py` exits 0 proving the five named entry obligations through the actual provider/process seams, including delivery before completion and scrubbed capture parity.
2. `uv run pytest tests/test_watchdog.py tests/test_providers.py` exits 0 proving production dormancy and unchanged results, optional usage, tool identities, stdin, grants and abort behavior.
3. `uv run pytest tests/test_git.py` exits 0 preserving group cleanup and unbounded inherited stdio.

## Verification
```
uv run pytest tests/test_watchdog.py tests/test_providers.py
uv run pytest tests/test_git.py
```

## Definition of rejected
A missing needed entry fact returns premise_failed, kind: spec_gap, naming 19.P4.watchdog-event-stream. A criteria-forced file beyond the fence returns premise_failed naming the file. Harden the contract or correct the authoring closure; never invent an invariant or widen this row.

## Time budget
- expected: 60m
- stuck: 90m
