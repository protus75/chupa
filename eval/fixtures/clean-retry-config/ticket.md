---
state: confirmed
source: human
priority: P2
kind: feature
---

## Goal / Why

Allow callers to set the timeout for HTTP GET requests so clients with different latency needs can use different values.

## Scope in / Scope out

Add an optional `timeout` argument to `Client` and pass it to each GET request. Keep the existing 5.0-second default. Retries and other HTTP methods are out of scope.

## Scope fence

- `src/tinyhttp/client.py`
- `tests/test_client.py`

## Acceptance criteria

1. A client created without `timeout` passes `timeout=5.0` to `Session.get`.
2. A supplied timeout is passed unchanged to `Session.get`; clients can use different timeout values independently.
3. A successful GET calls `raise_for_status()` and returns the parsed JSON.
4. An `HTTPError` from `raise_for_status()` propagates without calling `json()`.

## Verification

`python -m pytest -q tests/test_client.py`
