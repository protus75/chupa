---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase5-continue-03
- scorecard-reporting
- retro-box-activation

## Context
- chupa/status.py
- tests/test_status.py
- chupa/scorecard.py
- tests/test_scorecard.py
- chupa/box.py
- tests/test_box.py
- chupa/retro.py
- tests/test_retro.py
- chupa/__main__.py
- tests/test_cli.py

## Plan contract
- 19.I
- 19.P5.status-projection
- section 13

## Goal / Why
The production status command adds its current-window scorecard with real provenance and preserves the existing read-only projection.

## Scope in / Scope out
Implement the cited STATUS entry through the existing status and CLI owners. Extend the immutable projection with the window scorecard and deterministic provenance rendering. Use project_window, production_evidence and project_scorecard; do not build another journal fold for the window. Production status supplies its injected clock, Git.rev_parse HEAD and the loaded retro spec version. Keep lifetime spending and current-window spending distinct. Read invoices at their recorded completion commits. Preserve initial and completed-retro boundary behavior, token accounting, signal totals, sorted surfaces, bypass handling, rate arithmetic, prune threshold and zero escapes.

Preserve all Status operands, all old section labels and text, empty sections, and Reject queue recovery text. Queue reads include confirmed-class tombstones and journaled reopens, without mutating either. No writer, model, lock acquisition, retro trigger, notification, or scheduled push. Migrate the direct-render/CLI equality assertion in tests/test_status.py only as real provenance requires, retaining its byte-preservation proof. Preserve the existing project calling shape for journal-only clients and last_states/reject_queue; no caller migration outside this fence is earned. tests/test_serve.py compares only retained state fields, and tests/test_reject_queue.py checks the retained Reject queue text.

Create test_status_entry_unit in tests/test_status.py. It proves required_units for this seed and phase5-continue-03, a single heading via resolve_plan_contract, and all four entry_unit_gap parts. Named obligations: test_status_entry_unit, test_status_current_window_scorecard, test_status_production_provenance, test_status_preserves_sections_and_is_write_free, test_status_surfaces_confirmed_class_tombstones, test_status_on_an_empty_journal, test_status_projects_the_journal, test_status_is_deterministic. The new current-window test must use completed production Check evidence, distinguish incomplete intents and mutable invoices, and exercise all window operands and empty evidence. The provenance test exercises main(["status"]) in a disposable git repository. The write-free test retains old text on populated and empty inputs and forbids every write seam while comparing repository, journal and queue bytes. Extend existing CLI tests only for appended output.

Keep every tests/test_retro.py assertion unchanged and preserve predecessor scorecard and Box proofs. Reuse their window selection and evidence APIs without changing public signatures or constructors. Module ownership is defined by 19.P5.status-projection; no new module is needed. Entry tests belong in the entry test owner; no future test is Context. Leave baseline reading, retro/doctor verbs and the phase exit to their rows.

## Scope fence
- chupa/status.py
- tests/test_status.py
- chupa/scorecard.py
- tests/test_scorecard.py
- chupa/box.py
- tests/test_box.py
- chupa/retro.py
- tests/test_retro.py
- chupa/__main__.py
- tests/test_cli.py

## Acceptance criteria
1. `uv run pytest -q tests/test_status.py tests/test_cli.py tests/test_scorecard.py tests/test_box.py tests/test_retro.py` exits 0 proving every named STATUS obligation, real production provenance and unchanged predecessor evidence.
2. `uv run pytest -q tests/test_serve.py tests/test_reject_queue.py` exits 0 preserving journal-only clients and Reject text.
3. `uv run pytest -q tests/test_plan_lint.py` and `uv run pytest -q` exit 0.

## Verification
```
uv run pytest -q tests/test_status.py tests/test_cli.py tests/test_scorecard.py tests/test_box.py tests/test_retro.py
uv run pytest -q tests/test_serve.py tests/test_reject_queue.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
Missing governing facts return premise_failed with kind: spec_gap and the owning cited unit; a criteria-forced path outside earned closure needs contract repair.

## Time budget
- expected: 60m
- stuck: 180m
