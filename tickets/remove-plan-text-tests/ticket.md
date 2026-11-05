---
priority: P1
kind: chore
source: human
state: confirmed
---

## Depends on
- remove-seeding

## Context
- tests/test_retro.py
- tests/test_host_contract.py

## On-demand
- tests/test_supervised_merge_hold.py
- tests/test_inbox.py
- tests/test_retro_box.py
- tests/test_scorecard.py
- tests/test_go_grade.py
- tests/test_hostfiles.py
- tests/test_baseline.py
- tests/test_config.py
- tests/test_status.py
- tests/test_bug_gate.py
- tests/test_fixture_host.py

## Goal / Why
About twenty tests open the real `CHUPA_PLAN.md` and assert that some plan unit exists, has its Owner/Records/Observable/Tests parts, or contains a phrase. They check the wording of a frozen history file, not anything chupa does, and they block removing the plan resolver they call. After this change no test reads the real plan file; every behavior test in these files stays.

## Scope in / Scope out
- In: delete these test functions: `test_supervised_hold_entry_unit` (`tests/test_supervised_merge_hold.py`), `test_report_inbox_entry_units` (`tests/test_inbox.py`), `test_retro_box_entry_unit` (`tests/test_retro_box.py`), `test_escape_entry_unit` and `test_scorecard_entry_unit` (`tests/test_scorecard.py`), `test_go_grade_entry_units` (`tests/test_go_grade.py`), `test_classifier_entry_unit` and `test_renderer_entry_unit` (`tests/test_hostfiles.py`), `test_baseline_entry_unit` (`tests/test_baseline.py`), `test_migrate_config_entry_unit` (`tests/test_config.py`), `test_status_entry_unit` (`tests/test_status.py`), `test_bug_gate_entry_units` (`tests/test_bug_gate.py`), `test_fixture_host_entry_units` (`tests/test_fixture_host.py`), `test_host_contract_entry_unit` (`tests/test_host_contract.py`).
- In: `tests/test_retro.py` `test_artifact_is_closed_and_proposals_pair_the_risks`: delete only its last four lines (the plan read and the two `19.P5.retro-drain-invoker` assertions); keep the `RetroArtifact` checks.
- In: `tests/test_host_contract.py` `test_host_contract_report_custody_and_cutover`: delete only the comment and loop asserting facts `in PLAN`; keep the rest.
- In: delete each module-level `PLAN = (ROOT / "CHUPA_PLAN.md").read_text()` and every import these deletions leave unused.
- Out: tests that write a disposable `CHUPA_PLAN.md` into a temp host (they do not read the real plan), `tests/test_specs.py`, `tests/test_plan_lint.py`, `tests/test_phase*_exit.py`, all engine code.

## Scope fence
- tests/test_supervised_merge_hold.py
- tests/test_inbox.py
- tests/test_retro_box.py
- tests/test_scorecard.py
- tests/test_go_grade.py
- tests/test_hostfiles.py
- tests/test_baseline.py
- tests/test_config.py
- tests/test_status.py
- tests/test_bug_gate.py
- tests/test_fixture_host.py
- tests/test_host_contract.py
- tests/test_retro.py

## Acceptance criteria
1. `grep -n -E "ROOT / \"CHUPA_PLAN.md\"|parents\[1\] / \"CHUPA_PLAN.md\"|_entry_units?\(" tests/test_supervised_merge_hold.py tests/test_inbox.py tests/test_retro_box.py tests/test_scorecard.py tests/test_go_grade.py tests/test_hostfiles.py tests/test_baseline.py tests/test_config.py tests/test_status.py tests/test_bug_gate.py tests/test_fixture_host.py tests/test_host_contract.py tests/test_retro.py` prints nothing (it would print a line if any real-plan read or entry-unit test were left).
2. `test_artifact_is_closed_and_proposals_pair_the_risks` and `test_host_contract_report_custody_and_cutover` still exist and pass, checked by `uv run pytest tests/test_retro.py tests/test_host_contract.py`.
3. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_retro.py tests/test_host_contract.py
uv run pytest -q
```

## Definition of rejected
Any engine file changes; any test that does not read the real plan is deleted or weakened.

## Time budget
- expected: 25m
- stuck: 60m
