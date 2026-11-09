---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
none

## Context
- chupa/tickets.py::intake
- chupa/status.py::last_states
- chupa/scheduler.py

## Goal / Why
`intake` in `chupa/tickets.py` builds its `states` map with a comprehension that is a verbatim copy of `chupa.status.last_states`. Two copies of the "latest run-state per stem" fold can drift; drain, scheduler, and rework already call `last_states`. After this change `intake` calls `last_states(journal.read())` and the copy is gone, so the fold has one definition.

`chupa/status.py` imports `chupa.tickets` at module level (`from chupa.tickets import INTAKE_SIGNAL`), so a module-level import of `chupa.status` in `chupa/tickets.py` would be circular. The repo already breaks such cycles with a function-local import (for example `from chupa.rework import settled_dependencies, supersedes_maps` inside a function in `chupa/scheduler.py`); `intake` does the same.

## Scope in / Scope out
- In: in `chupa/tickets.py` `intake`, replace the `states = {...}` comprehension with a function-local `from chupa.status import last_states` and `states = last_states(journal.read())`. The set of settled states checked against `states` stays as is.
- Out: moving `last_states` out of `chupa/status.py`; any other caller of `last_states`; the settled-state set literal in `intake`; tests (`tests/integration/test_tickets.py::test_settled_bug_is_not_rejudged_for_evidence` already covers the journal-state exemption and `test_bug_without_evidence_refused_at_intake` covers the non-exempt path).

## Scope fence
- chupa/tickets.py

## Acceptance criteria
1. `./dev.py test tests/integration/test_tickets.py -k "settled_bug_is_not_rejudged_for_evidence or bug_without_evidence_refused_at_intake"` exits 0: a `confirmed` bug whose journal's last transition is `merged`, `already_satisfied`, or `rejected` is committed, not refused for missing evidence, and a bug with no evidence and no settled journal state is still refused.
2. `chupa/tickets.py` contains no `e.body["to"]` comprehension over `journal.read()`, and `intake` calls `last_states`.
3. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_tickets.py -k "settled_bug_is_not_rejudged_for_evidence or bug_without_evidence_refused_at_intake"
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- `last_states` is moved out of `chupa/status.py` or a second copy of it is defined anywhere;
- `chupa/tickets.py` imports `chupa.status` at module level;
- any file outside `chupa/tickets.py` changes.

## Time budget
- expected: 10m
- stuck: 30m
