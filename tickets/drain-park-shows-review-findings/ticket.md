---
state: confirmed
source: human
priority: P0
kind: bug
---

## Depends on
- none

## Context
- chupa/drain.py::Parked
- chupa/drain.py::Report
- chupa/drain.py::_Drain._settle
- chupa/drain.py::_Drain._premise_road
- chupa/drain.py::_Drain._findings
- tests/integration/test_rework.py::requisition
- tests/regress_already_satisfied.py
- docs/how-chupa-works.md

## Goal / Why
When the requisition review (the buildability review before Implement) parks a ticket as `premise_failed`, the drain report says "answer the premise findings below" and then prints nothing below it. `_findings` lists only files under `tickets/<stem>/`, and a requisition park writes none: its findings exist only in the `reason` of the journal's `premise_failed` transition. On 2026-11-08 `vscode-verdict-menu` and `vscode-graph-segments` sat parked this way, and the operator had to read the raw journal to learn what to edit (evidence/drain-report.txt). After this change, the report prints the park's findings under its line.

## Scope in / Scope out
- In: `chupa/drain.py`. For a parked stem whose last transition is `premise_failed` at stage `requisition`, the `Parked` findings list starts with that transition's `reason` text, unchanged. The findings that follow are the existing ticket-plane file paths. Parks at any other stage are unchanged.
- In: a test in `tests/integration/test_drain.py`: a committed confirmed ticket whose requisition review returns `snag` with a finding message `M` appears under `parked:` with `M` printed under its line.
- In: `tests/regress_drain_park_findings.py`, the carried reproducer (shaped like `tests/regress_already_satisfied.py`). It prints `defect` when a requisition park's report omits its `reason`, and `pass` when the report includes it.
- In: `docs/how-chupa-works.md`, the drain Report step: a requisition park lists its review findings.
- Out: `chupa status`, the snapshot and the VS Code extension, the requisition stage itself, and writing any new ticket-plane artifact.

## Scope fence
- chupa/drain.py
- tests/integration/test_drain.py
- tests/regress_drain_park_findings.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_drain.py` passes. It includes a requisition park whose drain report prints the snag's finding message under the park line, not an empty findings list.
2. `./dev.py test tests/integration/test_drain_upgrade.py` passes unchanged: an implement-stage premise park still prints `parked until its committed ticket.md changes`.
3. `uv run python tests/regress_drain_park_findings.py` prints `{"regression_result": "pass"}` and exits 0.

## Verification
```
./dev.py test tests/integration/test_drain.py
./dev.py test tests/integration/test_drain_upgrade.py
```

## Definition of rejected
Reject the branch if the report rewords, truncates or summarizes the journal `reason`, if a park at a stage other than requisition changes its output, or if the change writes a new file under `tickets/<stem>/`.

## Time budget
- expected: 25m
- stuck: 60m

## Regression
```
uv run python tests/regress_drain_park_findings.py
```
- carries: tests/regress_drain_park_findings.py
