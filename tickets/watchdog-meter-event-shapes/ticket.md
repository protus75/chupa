---
priority: P0
kind: bug
source: human
state: confirmed
---

## Depends on
none

## Context
- chupa/watchdog.py
- tests/test_watchdog.py

## Plan contract
- section 9

## Goal / Why
`CallMeter._consume` (`chupa/watchdog.py`) meters every scrubbed provider event without raising, whatever the shape of its fields (section 9: the watchdog reads the adapter's event stream; a provider event is the CLI's object, not a chupa schema). Today it assumes `message` and `item` are objects: a real Claude event `{"type": "system", "subtype": "permission_denied", "message": "<text>"}` reaches `message.get('usage')` and raises `AttributeError: 'str' object has no attribute 'get'`, so every watched Claude call whose stream carries a tool denial (routinely, read-only Review) ends `infra_error` (seen on plan-gap-13's review).

## Scope in / Scope out
- In: `CallMeter._consume` reads `message`, `item`, `usage`, and `message.content` blocks only when each has the shape it expects (an object, or a list of objects for `content`), treating any other shape as absent; progress observation still happens for every event, and metering of well-shaped events is unchanged.
- In: `tests/test_watchdog.py` adds `test_meter_ignores_non_object_event_fields`: a watched call whose stream carries the permission_denied system event (string `message`), an `assistant` event whose `message.content` is a string, and an event whose `item` and `usage` are strings completes with its result, while the well-shaped usage and tool ids in the same stream are still metered.
- Out: the adapter, the event spool, the detector's thresholds, and every other consumer.

## Scope fence
- chupa/watchdog.py
- tests/test_watchdog.py

## Acceptance criteria
1. `uv run pytest -q tests/test_watchdog.py tests/test_watchdog_activation.py` exits 0, including `test_meter_ignores_non_object_event_fields`.
2. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_watchdog.py tests/test_watchdog_activation.py
uv run pytest -q
```

## Regression
```
uv run pytest -q tests/test_watchdog.py -k test_meter_ignores_non_object_event_fields
```
- carries: tests/test_watchdog.py

## Definition of rejected
Reject the branch if a well-shaped event's usage, cost, or tool id stops being metered, if any event stops counting as progress, if the adapter or spool changes, or if the regression test passes on the merge base.

## Time budget
- expected: 20m
- stuck: 60m
