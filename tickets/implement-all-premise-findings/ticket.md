---
state: confirmed
source: human
priority: P1
kind: chore
---

## Depends on
- none

## Context
- tests/test_specs.py

## On-demand
- specs/implement.md
- tests/test_stages.py
- docs/how-chupa-works.md

## Goal / Why
Implement replies `premise_failed` at the first file outside `## Scope fence` it hits, so a ticket that forces several unfenced files takes one full attempt per file. `review-before-dispatch` ran five attempts on 2026-11-06, each naming one more missing file (`tests/test_seed_path.py`, `chupa/drain.py`, `chupa/daemon.py`, `chupa/__main__.py`, `eval/shakeout/drain.py`). After this change the Implement prompt tells the model to find every forced file outside the fence before replying `premise_failed`, and to report each one as its own finding.

## Scope in / Scope out
- In: `specs/implement.md`: in the `premise_failed` bullet under Task, add: "Before replying `premise_failed` for a scope reason, work the change through every file the acceptance criteria and `## Verification` commands force, and report each forced file outside `## Scope fence` as its own finding; never stop at the first." Bump `version` to "2.3".
- In: `tests/test_specs.py`: the implement version pins in `test_spec_lint_accepts_the_implement_and_requisition_specs` and `test_implement_spec_consumer_read`; in `test_implement_spec_consumer_read`, assert the new sentence is in the rendered Task.
- In: `tests/test_stages.py`: the `spec: implement 2.2` pin in the run-record assertion.
- In: `docs/how-chupa-works.md` section 4.2: the `premise_failed` bullet says the findings name every forced file outside the fence, not only the first.
- Out: the packing-slip schema, finding codes, every other spec, the Diagnose and requisition review prompts.

## Scope fence
- specs/implement.md
- tests/test_specs.py
- tests/test_stages.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `specs/implement.md` is at version "2.3", lints clean, and its rendered Task contains the new sentence, checked by `uv run pytest tests/test_specs.py`.
2. `docs/how-chupa-works.md` section 4.2 states that `premise_failed` findings name every forced file outside the fence.
3. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_specs.py
uv run pytest -q
```

## Definition of rejected
The implement spec's major version changes; the packing-slip schema or finding codes change; any other spec changes.

## Time budget
- expected: 20m
- stuck: 45m
