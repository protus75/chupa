---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
- eval-drop-host-loop-report
- eval-drop-soak-battery-reports

## Runs before
- eval-move-shakeout

## Context
- chupa/artifacts.py::ShakeoutEntry
- chupa/artifacts.py::ShakeoutReport
- chupa/stages.py::KNOWN_ARTIFACTS
- chupa/merge.py
- eval/shakeout/run.py
- tests/integration/test_shakeout.py
- tests/unit/test_lift_decision.py
- docs/how-chupa-works.md#13. Eval report artifacts

## On-demand
- tests/integration/test_stages.py
- tests/integration/test_merge.py

## Goal / Why
The shakeout report (`shakeout-report.json`) was a bootstrap phase-completion proof. No engine path reads it at runtime. It is registered in `KNOWN_ARTIFACTS` only so a report-only ticket could lift and merge it. The seven committed copies under `tickets/shakeout-*/` are read by nothing. The engine still defines its schema (`SHAKEOUT_REPORT`, `SHAKEOUT_SPEC_VERSION`, `ShakeoutEntry`, `ShakeoutReport`). `eval/shakeout/run.py` still carries a `--group/--prior/--out` command (`write_report`, `_main`, `main`) that only one test calls. The generic report-lift and report-only-merge tests in `tests/integration/test_stages.py` and `tests/integration/test_merge.py` also use the shakeout report as their sample, which ties engine machinery tests to a bootstrap type.

After this change the engine no longer registers or defines the shakeout report. The generic report tests use a small test-local sample report. The shakeout members and `produce` stay as end-to-end regression checks. The review-baseline report remains the one registered report.

Simplest approach: move the two shakeout types into `eval/shakeout/run.py` unchanged. Register a test-only `SampleReport` through `monkeypatch.setitem` in the two generic test modules. Rejected: switching the generic tests to the review-baseline report, which needs the eval harness and its graded fixtures just to build sample bytes.

## Scope in / Scope out
- In: `chupa/artifacts.py`: remove `SHAKEOUT_REPORT`, `SHAKEOUT_SPEC_VERSION`, `ShakeoutEntry` and `ShakeoutReport`.
- In: `chupa/stages.py`: drop those imports and the `SHAKEOUT_REPORT` entry of `KNOWN_ARTIFACTS`, leaving only `REVIEW_BASELINE_REPORT`.
- In: `eval/shakeout/run.py`:
  - define `SHAKEOUT_SPEC_VERSION`, `ShakeoutEntry` and `ShakeoutReport` with the same fields and validators. They may import `Artifact`, `_Strict` and `NonBlank` from `chupa.artifacts`.
  - delete `write_report`, `_main`, `main` and the `__main__` block, plus the imports only they used.
  - change the module docstring so it no longer says "sole report writer".
  - keep `produce`, `run_member`, `Member`, `Observation`, `ShakeoutRefused` and `GROUPS`.
- In: `tests/integration/test_shakeout.py`: import `ShakeoutEntry` and `ShakeoutReport` from `eval.shakeout.run`. Delete `test_unknown_group_command_exits_two`, the only caller of the command.
- In: generic report tests.
  - `tests/integration/test_stages.py`:
    - define `SAMPLE_REPORT = "sample-report.json"` and `class SampleReport(Artifact)` with `entries: list[NonBlank]`.
    - add a module autouse fixture that runs `monkeypatch.setitem(stages.KNOWN_ARTIFACTS, SAMPLE_REPORT, SampleReport)`.
    - `_report_bytes()` returns `SampleReport(produced_by_spec_version=1, produced_at_sha="abc", entries=["one"]).model_dump_json()`.
    - replace every `SHAKEOUT_REPORT` with `SAMPLE_REPORT` and every `ShakeoutReport` with `SampleReport`.
  - `tests/integration/test_merge.py`:
    - add the same autouse registration, importing `SAMPLE_REPORT` and `SampleReport` from `tests.integration.test_stages`.
    - replace `SHAKEOUT_REPORT` with `SAMPLE_REPORT`.
    - in the `invalid-schema` case, register `SampleReport`'s mismatching stand-in the same way the test registers `ShakeoutEntry` today, for example `monkeypatch.setitem(KNOWN_ARTIFACTS, SAMPLE_REPORT, Finding)`.
  - `tests/unit/test_lift_decision.py`: use `chupa.artifacts.REVIEW_BASELINE_REPORT` where it uses `SHAKEOUT_REPORT` today.
  - `tests/integration/test_closed_sets.py`: remove the `SHAKEOUT_SPEC_VERSION` assertion and the `shakeout-report.json` row from the `KNOWN_ARTIFACTS` assertion.
- In: `docs/how-chupa-works.md` section 13: replace the eval report artifacts list with one line saying the review-baseline report (`review-baseline-report.json`, written by `eval/harness.py`) is the only registered report artifact.
- Unaffected: no other file outside the fence references the removed names. A grep for `Shakeout`, `SHAKEOUT_REPORT` and `SHAKEOUT_SPEC_VERSION` finds only an env-var name `SHAKEOUT_SECRET` in `eval/shakeout/providers.py`, which is unrelated. Coverage dependents of `chupa/artifacts.py`, `chupa/stages.py` and `chupa/merge.py` exercise the lift and merge machinery only through the two fenced generic test modules, so their behavior does not change.
- Out:
  - the committed `tickets/shakeout-*/` files (history);
  - moving `eval/shakeout/` under `tests/` (ticket `eval-move-shakeout`);
  - unregistering the review-baseline report or removing the report-only lift and merge path in `chupa/stages.py` and `chupa/merge.py`;
  - `chupa/merge.py` and `chupa/stages.py` lift code itself;
  - `chupa/mergequeue.py` receipt reasons.

## Scope fence
- chupa/artifacts.py
- chupa/stages.py
- eval/shakeout/run.py
- tests/integration/test_shakeout.py
- tests/integration/test_stages.py
- tests/integration/test_merge.py
- tests/integration/test_closed_sets.py
- tests/unit/test_lift_decision.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `uv run python -c "import chupa.artifacts as a, chupa.stages as s; assert not any(hasattr(a, n) for n in ('ShakeoutReport','ShakeoutEntry','SHAKEOUT_REPORT','SHAKEOUT_SPEC_VERSION')); assert set(s.KNOWN_ARTIFACTS) == {'review-baseline-report.json'}"` exits 0. This rules out a shakeout type left in the engine, and a registry still holding any bootstrap report.
2. `uv run python -c "import eval.shakeout.run as r; assert not any(hasattr(r, n) for n in ('write_report','main','_main')); r.ShakeoutReport; r.produce"` exits 0, ruling out a leftover command or a deleted harness.
3. `./dev.py test tests/integration/test_stages.py tests/integration/test_merge.py tests/unit/test_lift_decision.py` exits 0, so the generic report lift and report-only merge stay covered with the sample report.
4. `./dev.py test tests/integration/test_shakeout.py tests/integration/test_closed_sets.py` exits 0, still running `test_produce_stages_returns_six_green_entries`.
5. `./dev.py test` exits 0.

## Verification
```
uv run python -c "import chupa.artifacts as a, chupa.stages as s; assert not any(hasattr(a, n) for n in ('ShakeoutReport','ShakeoutEntry','SHAKEOUT_REPORT','SHAKEOUT_SPEC_VERSION')); assert set(s.KNOWN_ARTIFACTS) == {'review-baseline-report.json'}"
uv run python -c "import eval.shakeout.run as r; assert not any(hasattr(r, n) for n in ('write_report','main','_main')); r.ShakeoutReport; r.produce"
./dev.py test tests/integration/test_stages.py tests/integration/test_merge.py tests/unit/test_lift_decision.py
./dev.py test tests/integration/test_shakeout.py tests/integration/test_closed_sets.py
./dev.py test
```

## Definition of rejected
The shakeout report is still defined in or registered by `chupa/`; a generic lift or merge test is deleted rather than moved to the sample report; any `chupa/` code other than `chupa/artifacts.py` and `chupa/stages.py` changes; a committed file under `tickets/` changes; or any file outside the fence changes.

## Time budget
- expected: 40m
- stuck: 80m
