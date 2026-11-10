---
state: confirmed
source: human
priority: P1
kind: chore
---

## Depends on
- core-authoring-first

## Context
- chupa/hostfiles.py::CORE_TEMPLATE
- tests/integration/test_hostfiles.py::test_core_template_is_host_neutral

## Goal / Why
The managed block grew to 22 KB because rules were ported word for word and nothing limited its size or order. Chat sessions read only the start, so the ticket authoring rule, added late and placed near the end, went unread. `core-authoring-first` reorders and compresses the block once. This ticket stops it growing back: a test fails when the template no longer opens with the ticket authoring section or grows past 8192 bytes. Each failure message says what to do instead.

## Scope in / Scope out
- In: one new test in `tests/integration/test_hostfiles.py` with two assertions on `hostfiles.CORE_TEMPLATE`:
  - it starts with `## Ticket authoring`; the failure message says to keep ticket authoring rules in the first section and add new rules after it;
  - `len(CORE_TEMPLATE) <= 8192`; the failure message says to compress existing rules or move host-specific ones to the project's own rules outside the managed block.
- Out: `CORE_TEMPLATE` text, `chupa/hostfiles.py`, and every conduct file.

## Scope fence
- tests/integration/test_hostfiles.py

## Acceptance criteria
1. `./dev.py test tests/integration/test_hostfiles.py` passes on the template `core-authoring-first` leaves.
2. The new test fails, not passes, when `CORE_TEMPLATE` is monkeypatched to start with `## Engine conduct`, and fails when it is monkeypatched to 8193 bytes; both cases are covered in `tests/integration/test_hostfiles.py`.

## Verification
```
./dev.py test tests/integration/test_hostfiles.py
```

## Definition of rejected
The change edits `CORE_TEMPLATE` or any conduct file, or the size limit is not 8192 bytes.

## Time budget
- expected: 10m
- stuck: 30m
