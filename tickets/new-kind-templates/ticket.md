---
priority: P1
kind: feature
source: human
state: confirmed
---

## Depends on
- bug-evidence-intake

## Context
- chupa/tickets.py
- chupa/__main__.py
- dev.py
- docs/how-chupa-works.md
- docs/host-authoring.md

## Goal / Why
`chupa new <stem>` writes one skeleton (`template()` in `chupa/tickets.py`): every required section empty and `kind: feature`. A bug ticket needs `## Regression` and evidence, so authors copy templates from docs instead, and those copies drift from the grammar. The templates belong beside the grammar, one per kind, so hosts never copy the format.

## Scope in / Scope out
- In: `template(kind)` in `chupa/tickets.py` for `feature`, `bug`, and `chore`, setting that `kind`. Each section holds one short `<...>` placeholder saying what goes there. The `bug` template adds `## Regression` with a placeholder command and one `- carries:` bullet, and its placeholder names the `regression_result` protocol. `feature` and `chore` have no `## Regression`.
- In: `chupa new <stem> --kind feature|bug|chore` (default `feature`) writes the matching template and lints it as today. For `bug` it also prints the evidence finding from the ticket checker. It never creates anything under `tickets/<stem>/evidence/`: any file there counts as evidence.
- In: `./dev.py new STEM [--kind K]` runs it.
- In: tests in `tests/test_tickets.py`: `test_template_per_kind` (each kind's template, with every `<...>` placeholder replaced by sample content and its Context paths created, passes `validate_ticket`; only `bug` has `## Regression`) and `test_new_bug_creates_no_evidence`.
- In: update `docs/how-chupa-works.md` sections 2.1 and 2.2 and the Workflow in `docs/host-authoring.md` to start from `chupa new <stem> --kind ...`.
- Out: the ticket grammar, intake, and the `lint` verb.

## Scope fence
- chupa/tickets.py
- chupa/__main__.py
- dev.py
- tests/test_tickets.py
- docs/how-chupa-works.md
- docs/host-authoring.md

## Acceptance criteria
1. `uv run pytest -q tests/test_tickets.py` exits 0, including `test_template_per_kind` and `test_new_bug_creates_no_evidence`.
2. `docs/how-chupa-works.md` sections 2.1 and 2.2 and `docs/host-authoring.md` name `chupa new <stem> --kind feature|bug|chore` and `./dev.py new`.
3. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_tickets.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if a filled template fails `validate_ticket`, if `new` writes any evidence file, or if the ticket grammar changes.

## Time budget
- expected: 30m
- stuck: 60m
