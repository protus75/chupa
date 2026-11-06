---
state: confirmed
source: human
priority: P1
kind: bug
---

## Depends on
none

## Context
- chupa/tickets.py
- chupa/stages.py
- tests/test_tickets.py

## Goal / Why
`graph-lane-cleanup` passed lint with `- carries: vscode-chupa/media/graph.js`. The check gate then rejected it twice on `bug_evidence` ("implementation paths cannot be carried"), after two full implement runs whose code passed every other gate (2026-11-06). The test/fixture rule lives only in the check gate (`stages._gather_bug`), so lint cannot catch it at authoring.

After this change lint rejects a `carries:` prefix with no `tests`, `test`, `fixtures`, or `fixture` path component, and the gate and lint read that set from one constant in `chupa/tickets.py`.

## Scope in / Scope out
- In: `tickets.py`: a module constant naming the four directory names; `_regression` emits a finding for a prefix none of whose path components is in it, with a paved road naming a carried reproducer under `tests/`.
- In: `stages._gather_bug` imports that constant in place of its inline set; its per-file check is otherwise unchanged.
- In: `tests/test_tickets.py`: one case each for a rejected implementation prefix and an accepted `tests/` prefix.
- In: `tests/regress_lint_carries.py`: the carried reproducer.
- Out: the gate's per-file check, the regression result protocol, the retry policy, existing tickets.
- Touch no file outside `## Scope fence`.

## Scope fence
- chupa/tickets.py
- chupa/stages.py
- tests/test_tickets.py
- tests/regress_lint_carries.py

## Acceptance criteria
1. A bug ticket whose `## Regression` carries `vscode-chupa/media/graph.js` fails `validate_ticket` with a finding naming that prefix; one carrying `tests/` or `tests/regress_x.py` passes. `tests/regress_lint_carries.py` checks the rejected case and reports `pass`.
2. `chupa/stages.py` holds no inline `{"tests", "test", "fixtures", "fixture"}` literal.
3. `uv run pytest -q` exits 0.

## Verification
```
uv run python tests/regress_lint_carries.py
uv run pytest -q
```

## Regression
```
uv run python tests/regress_lint_carries.py
```
- carries: tests/regress_lint_carries.py

## Definition of rejected
Reject the branch if any of the following holds:
- lint and the gate each keep their own copy of the directory-name set;
- the gate's check is removed or weakened;
- a file outside `## Scope fence` changes.

## Time budget
- expected: 30m
- stuck: 90m
