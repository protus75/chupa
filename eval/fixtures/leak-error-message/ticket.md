---
state: confirmed
source: human
priority: P2
kind: feature
---

## Goal / Why
Add a database connection helper that gives callers a useful failure message without exposing credentials from a connection URL or details from the driver error.

## Scope in / Scope out
Add a `connect(dsn, opener)` helper and a `ConnectError` exception. The opener receives the original DSN. On failure, report only the destination hostname, or `unknown host` when the URL has no hostname. Retries, driver selection, and URL validation are out of scope.

## Scope fence
- `dbkit/connection.py`
- `tests/test_connection.py`

## Acceptance criteria
1. A successful opener is called once with the original DSN, and its result is returned unchanged.
2. An opener failure raises `ConnectError` whose message contains the destination hostname.
3. Neither the connection credentials nor the driver error details appear in the error message or formatted traceback.
4. A URL without a hostname is reported as `unknown host`.

## Verification
`python -m pytest tests/test_connection.py -q`
