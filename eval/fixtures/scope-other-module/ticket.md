---
state: confirmed
source: human
priority: P2
kind: feature
---

## Goal / Why
Add `median()` to `ministats.stats` so callers can summarize finite numeric samples.

## Scope in / Scope out
Implement `median(values: Sequence[float]) -> float` and focused tests. It must sort values without changing the input, return the middle value for odd lengths and the average of the two middle values for even lengths, and raise `ValueError` for an empty sequence. README and other documentation changes are out of scope.

## Scope fence
- `src/ministats/stats.py`
- `tests/test_stats.py`

## Acceptance criteria
- Odd-length samples return the middle value regardless of input order.
- Even-length samples return the average of the two middle values.
- Negative and repeated values are handled correctly.
- Calling `median()` does not change the input sequence.
- An empty sequence raises `ValueError` with the message `median requires at least one value`.

## Verification
`python -m pytest -q tests/test_stats.py`
`python -m pytest -q`
