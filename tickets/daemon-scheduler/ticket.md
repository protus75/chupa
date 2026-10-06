---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase3-core

## Context
- chupa/drain.py
- chupa/tickets.py
- chupa/status.py
- chupa/seams.py

## Plan contract
- 19.I
- 19.P3.daemon-scheduler
- section 9

## Goal / Why
Build the dormant single-flight asyncio scheduler and debounced ticket watcher, with pending work re-prioritized before each free slot.

The entry unit owns the complete contract. The scheduler owns the memory-only pending queue and active dispatch slot; the watcher owns debounced change consumption and its last-known-good parsed cache. Reuse the bootstrap drain's authored_at, sort_key, and SETTLED, the existing ticket parser, and the existing last_states and reject_queue folds. Keep bootstrap production dispatch unchanged until scheduler-activation.

## Scope in / Scope out
- In: direct component construction with injected ticket reads/change delivery, journal, dispatch, clock, and Sleep. Only confirmed tickets whose predecessors are settled are ready; Reject verdict holds and caller-supplied quarantine/drought holds exclude work. Recompute holds, eligibility, and max_unmerged backpressure at every selection. Use the first ticket_intake timestamp for age, missing age last and stem as the final tiebreak.
- In: await each dispatch, including concurrent selection requests, and release its slot on success, exception, or cancellation. Debounce edits, restarting the wait on further edits. Valid edits and new P0 tickets change the next pick without preempting active work. Removal drops pending work; parsing failure preserves the complete old record and position, or excludes a new invalid stem, and writes only the watcher_parse_failure signal specified by the entry unit. A later valid parse replaces the cache.
- Out: daemon activation, changes to bootstrap dispatch, merge admission, cap draws, quarantine/drought decisions, new frontmatter or config, new event types, new watcher dependencies, seam changes, raw process calls, and notifications.

## Scope fence
- chupa/scheduler.py
- chupa/watcher.py
- tests/test_scheduler.py

## Acceptance criteria
1. `uv run pytest -q tests/test_scheduler.py` exercises both production components directly. The named tests `test_single_flight_dispatch` and `test_dispatch_failure_and_cancellation_release_slot` prove concurrent requests cannot overlap and every unwind path frees the slot.
2. `uv run pytest -q tests/test_scheduler.py` passes `test_eligibility_and_hold_release`, `test_priority_age_and_stem_order`, and `test_max_unmerged_backpressure`: confirmed-state eligibility, merged/already_satisfied predecessor settlement, Reject verdict folds, caller-supplied quarantine/drought release, distinct intake timestamps with first-event anchoring, missing age, priority/stem ordering without mtime, and limit hold/release are all discriminated.
3. `uv run pytest -q tests/test_scheduler.py` passes `test_watcher_debounce`, `test_watcher_reprioritizes_without_preemption`, and `test_watcher_removal_drops_pending`, using injected time to prove restarted debounce waits, partial writes, next-slot priority changes, removal, and absence of preemption.
4. `uv run pytest -q tests/test_scheduler.py` passes `test_watcher_parse_failure_preserves_last_good`, checking the exact EventType.SIGNAL envelope (ticket stem, null key) and body `{signal: watcher_parse_failure, path: tickets/<stem>/ticket.md, reason: <nonempty diagnostic>}`, owned by WATCHER_PARSE_FAILURE in the watcher, preservation of old sort position, exclusion of a new invalid stem, and valid recovery.
5. `uv run pytest -q tests/test_scheduler.py` passes `test_scheduler_and_watcher_are_dormant`: the transitive chupa import closure rooted at the CLI cannot reach either component, recognizes both import idioms, and the test demonstrates that reaching either component would fail its assertion. This is component evidence below production grade; activation migrates that assertion separately.
6. `uv run pytest -q` exits 0 with no test removed or skipped and bootstrap behavior unchanged.

## Verification
```
uv run pytest -q tests/test_scheduler.py
uv run pytest -q
```

## Definition of rejected
Reject if construction becomes production-reachable, an active dispatch is preempted, timing uses wall-clock sleeps, a second grammar or durable pending queue is introduced, an entry-unit fact is invented, or an edit leaves the fence. If the entry unit omits a needed fact, return premise_failed naming 19.P3.daemon-scheduler so section 11.4 hardens it first.

## Time budget
- expected: 60m
- stuck: 120m
