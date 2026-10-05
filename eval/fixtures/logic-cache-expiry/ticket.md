---
state: confirmed
source: human
priority: P2
kind: feature
---

## Goal / Why

Add a TTL cache to the JSON configuration loader so repeated loads avoid disk reads while configurations remain fresh.

## Scope in / Scope out

Add a loader with an injectable monotonic clock and a separate cache entry per resolved path. Expire entries lazily when `load` is called. A cached value expires when elapsed time is at least the TTL. Keep JSON parsing errors visible to callers. Background refresh and file watching are out of scope.

## Scope fence

- `config_loader.py`
- `tests/test_config_loader.py`

## Acceptance criteria

1. The first load of a path reads its JSON value.
2. Loads before the TTL expires return the same cached object, even if the file changes.
3. A load at or after the exact expiry instant reads the file again and returns its current value.
4. Different paths have independent cache entries, and nonpositive TTL values raise `ValueError`.

## Verification

`python -m pytest -q tests/test_config_loader.py`
