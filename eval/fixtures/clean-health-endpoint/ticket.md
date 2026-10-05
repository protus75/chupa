---
state: confirmed
source: human
priority: P2
kind: feature
---

## Goal / Why
Add a lightweight `/healthz` endpoint so operators can see the running service version and uptime. This Flask project exposes `create_app()` in `tinyservice/app.py` and defines `__version__` in `tinyservice/__init__.py`.

## Scope in / Scope out
Add the endpoint and focused tests. Keep the existing `/` response unchanged. Authentication, dependency checks, and deployment configuration are out of scope.

## Scope fence
- `tinyservice/app.py`
- `tests/test_healthz.py`

## Acceptance criteria
1. `GET /healthz` returns HTTP 200 with a JSON object containing exactly `version` and `uptime_seconds`.
2. `version` equals `tinyservice.__version__`.
3. `uptime_seconds` is a nonnegative number measured from the creation of that app instance using a monotonic clock, and it does not decrease across requests.
4. Separate app instances have separate uptime start times, and `GET /` retains its existing response.

## Verification
Run `python -m pytest -q tests/test_healthz.py`.
