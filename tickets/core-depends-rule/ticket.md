---
state: confirmed
source: human
priority: P1
kind: chore
---

## Depends on
- none

## Context
- chupa/hostfiles.py
- tests/test_hostfiles.py
- tests/test_gates.py
- docs/how-chupa-works.md

## Goal / Why
The managed `chupa:core` block tells every agent "Put ordering in depends and priority." That reads as permission to use `## Depends on` for ordering. A `depends` used only for order blocks every ticket behind it when the first one fails, and it did on 2026-11-05. `CLAUDE.md` section A and `docs/host-authoring.md` already say `depends` is only for a ticket whose merged code this one needs. After this change the managed block says the same, in every routed conduct file.

## Scope in / Scope out
- In: `chupa/hostfiles.py` `CORE_TEMPLATE`, in the last bullet. Replace "Put ordering in depends and priority. Why: unused metadata and prose ordering drift." with "Use depends only for a ticket whose merged code this one needs; put all other ordering in priority. Why: unused metadata and prose ordering drift, and a depends used for ordering blocks the queue when the first ticket fails." The bullet count stays six.
- In: re-render the managed block in `CLAUDE.md`, `AGENTS.md` and `hosts/fixture/CLAUDE.md` with `hostfiles.render` (what `chupa core` runs). Text outside the markers stays byte-identical.
- In: `tests/test_hostfiles.py`: assert the template contains "Use depends only for a ticket whose merged code this one needs" and no longer contains "Put ordering in depends".
- Out: any other template bullet; `CLAUDE.md` section A and `docs/host-authoring.md` (already updated); the `core_drift` gate.

## Scope fence
- chupa/hostfiles.py
- CLAUDE.md
- AGENTS.md
- hosts/fixture/CLAUDE.md
- tests/test_hostfiles.py

## Acceptance criteria
1. `uv run pytest tests/test_hostfiles.py` passes. The new assertion fails if the template keeps "Put ordering in depends" or lacks the new rule.
2. The `chupa:core` blocks in `CLAUDE.md`, `AGENTS.md` and `hosts/fixture/CLAUDE.md` equal `hostfiles.render` output, so `uv run pytest tests/test_gates.py` and the `core_drift` gate pass.
3. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_hostfiles.py tests/test_gates.py
uv run pytest -q
```

## Definition of rejected
A hand-edited managed block that differs from `hostfiles.render` output; any other template bullet changes; project text outside the markers changes.

## Time budget
- expected: 20m
- stuck: 60m
