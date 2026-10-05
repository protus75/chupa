---
state: confirmed
source: human
priority: P2
kind: feature
---

## Goal / Why

Add a small wrapper for network calls that may fail briefly. It should retry transient connection and timeout failures with exponential backoff.

## Scope in / Scope out

In scope: a synchronous `retry_call` function with configurable attempt count and delays, plus unit tests. Out of scope: asynchronous calls, jitter, and logging.

## Scope fence

- `retry.py`
- `tests/test_retry.py`

## Acceptance criteria

- Return the operation's result on success, making no more than `max_attempts` total calls.
- Retry only `ConnectionError` and `TimeoutError` (including their subclasses); propagate any other exception immediately.
- Before each retry, sleep for `min(base_delay * 2**attempt, max_delay)`, where `attempt` starts at zero. Never sleep after the final failure.
- Raise `ValueError` when `max_attempts` is below 1, `base_delay` is negative, or `max_delay` is below `base_delay`.

## Verification

`python -m pytest -q tests/test_retry.py`
