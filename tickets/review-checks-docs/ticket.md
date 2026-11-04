---
priority: P1
kind: feature
source: human
state: confirmed
---

## Depends on
none

## Context
- tests/test_specs.py
- docs/how-chupa-works.md
- docs/host-authoring.md

## On-demand
- specs/review.md

## Goal / Why
Tickets must update the docs that describe the behavior they change (`docs/host-authoring.md`, `Scope fence`), and their acceptance criteria name those docs. The correctness reviewer (`specs/review.md`) only snags on lines the diff adds or changes, so a doc the diff should have changed and did not has no line to attach a finding to, and a stale doc merges unnoticed.

## Scope in / Scope out
- In: `specs/review.md` version "1.1" -> "1.2". Its `acceptance` snag also covers docs: a doc the ticket's acceptance criteria or `Scope in / Scope out` name is not updated to match the diff, or the diff changes behavior that a file under `docs/` or `README.md` describes and leaves that file stating the old behavior. The reviewer may search and read those files to find such a statement.
- In: the Admissibility paragraph allows this one finding without a changed line: it names the stale doc as `path` with `line` null, and quotes the outdated statement in `message`. Every other finding still attaches to a changed line.
- In: `tests/test_specs.py` adds `test_review_spec_checks_docs` (version "1.2", the doc rule and its admissibility exception present, placeholder set unchanged) and updates the version assertion in `test_review_spec_read_only` to "1.2".
- In: update `docs/how-chupa-works.md` section 4.4 to say Review also snags a stale or missing doc update.
- Out: the verdict vocabulary, finding codes, output schema, review inputs, `specs/implement.md`, and any engine code.

## Scope fence
- specs/review.md
- tests/test_specs.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `uv run pytest -q tests/test_specs.py` exits 0, including `test_review_spec_checks_docs`.
2. `specs/review.md` declares `version: "1.2"` and keeps its `ticket`, `diff`, and `retry_findings` inputs unchanged.
3. `docs/how-chupa-works.md` section 4.4 says Review snags a stale or missing doc update.
4. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_specs.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if the spec gains a new verdict, finding code, or input, if any finding other than a stale doc may skip its changed line, or if the version is not a minor bump.

## Time budget
- expected: 20m
- stuck: 45m
