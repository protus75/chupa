---
priority: P1
kind: feature
source: human
state: confirmed
---

## Depends on
none

## Context
- chupa/config.py
- tests/test_config.py
- docs/host-contract.md
- tests/test_host_contract.py

## Goal / Why
Config accepts host review surfaces (`review.surfaces`, `ReviewSurface` in `chupa/config.py`), but no code runs them: a host that declares one gets no extra review and no warning. Running them is deferred until a host that uses them onboards. Until then config load refuses a declared surface instead of silently ignoring it.

## Scope in / Scope out
- In: loading a config whose `review.surfaces` is non-empty raises the existing `ConfigError` naming `review.surfaces`, with the paved road "remove review.surfaces entries; host review surfaces are not supported yet". An absent key or `surfaces: []` loads as today.
- In: `tests/test_config.py`'s `VALID` fixture drops its `surfaces` entry; add `test_review_surfaces_refused` (a non-empty list refuses with that message and road; an empty list loads).
- In: `docs/host-contract.md`'s copyable example sets `surfaces: []` with a comment saying surfaces are not supported yet, and the prose says config refuses a declared surface; `tests/test_host_contract.py::test_host_contract_example_loads` drops its `surfaces[0]` assertion and asserts the example's `surfaces` is empty.
- Out: removing the `ReviewSurface` model or the `surfaces` key, any surface execution, routing, specs, and the plan text.

## Scope fence
- chupa/config.py
- tests/test_config.py
- docs/host-contract.md
- tests/test_host_contract.py

## Acceptance criteria
1. `uv run pytest -q tests/test_config.py tests/test_host_contract.py` exits 0, including `test_review_surfaces_refused`.
2. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_config.py tests/test_host_contract.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if a non-empty `review.surfaces` loads, if an empty or absent one refuses, if the refusal lacks the paved road, or if the `surfaces` key or `ReviewSurface` model is removed.

## Time budget
- expected: 30m
- stuck: 60m
