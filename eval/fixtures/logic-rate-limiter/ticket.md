---
state: confirmed
source: human
priority: P2
kind: feature
---

## Goal / Why
Add a token-bucket limiter that an API gateway can use to decide whether a request may proceed. The project imports Python modules from `src`.

## Scope in / Scope out
Implement a reusable `TokenBucket` with an injectable clock, configurable capacity and refill rate, and an `allow(tokens=1.0)` method. Use only the Python standard library. Gateway integration and shared state across processes are out of scope.

## Scope fence
- `src/gateway/rate_limit.py`
- `tests/test_rate_limit.py`

## Acceptance criteria
1. A new bucket starts full. A request succeeds when its cost equals the available tokens; a rejected request spends none.
2. Tokens refill at `refill_per_second`, including fractional amounts, and never exceed capacity.
3. If a clock sample moves backward, it grants no tokens and does not move the refill baseline. Returning to the previous clock value grants no additional tokens.
4. Nonpositive capacity, refill rate, or request cost raises `ValueError`.

## Verification
`PYTHONPATH=src python -m pytest -q tests/test_rate_limit.py`
