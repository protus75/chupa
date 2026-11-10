---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
- none

## Runs before
- eval-drop-soak-battery-reports

## Context
- chupa/artifacts.py::HOST_LOOP_REPORT
- chupa/artifacts.py::_check_producing_run
- chupa/artifacts.py::HostLoopEntry
- chupa/artifacts.py::HostLoopReport
- chupa/artifacts.py::ExitReads
- chupa/artifacts.py::ExitReceipt
- chupa/stages.py::KNOWN_ARTIFACTS
- eval/host_loop.py
- tests/integration/test_host_loop.py
- tests/unit/test_artifacts.py
- docs/how-chupa-works.md#13. Eval report artifacts

## Goal / Why
The host-loop report (`host-loop-report.json`) and exit receipt (`exit-receipt.json`) were bootstrap phase-completion proofs. Nothing in the engine reads them at runtime: they are only registered in `KNOWN_ARTIFACTS` so a report-only ticket could lift and merge them, and the two committed copies under `tickets/phase6-exit/` are read by nothing. The engine still carries their schemas (`chupa/artifacts.py` `HOST_LOOP_REPORT` through `ExitReceipt`), and `eval/host_loop.py` still carries a `--out/--receipt/--baseline` producer and receipt writer that only its own tests call.

After this change the engine no longer registers or defines either artifact, and the receipt and report-writing code is gone. The end-to-end harness itself stays: `FixtureLoop`, `produce` and `LoopRefused` still drive a supervised fixture `serve`, and their tests keep running as end-to-end regression checks.

Simplest approach: move the two observation types the harness still builds (`HostLoopEntry`, `HostLoopReport`) and their constants into `eval/host_loop.py` unchanged, and delete the receipt path outright. Rejected: rewriting the harness to return plain dicts, which churns the end-to-end tests for no gain.

## Scope in / Scope out
- In: `chupa/artifacts.py`: remove `HOST_LOOP_REPORT`, `EXIT_RECEIPT`, `HOST_LOOP_MEMBERS`, `HOST_LOOP_EXPECTED`, `HostLoopEntry`, `HostLoopReport`, `ExitReads` and `ExitReceipt`.
- In: `chupa/stages.py`: drop those imports and the `HOST_LOOP_REPORT` and `EXIT_RECEIPT` entries of `KNOWN_ARTIFACTS`.
- In: `eval/host_loop.py`:
  - define `HOST_LOOP_MEMBERS`, `HOST_LOOP_EXPECTED`, `HostLoopEntry` and `HostLoopReport` with the same fields and validators as today. They may import `_Strict`, `NonBlank`, `_check_producing_run` and `_check_integer_version` from `chupa.artifacts`.
  - delete `canonical`, `write_report`, `regenerate`, `write_receipt`, `committed_bytes`, `_main`, `main`, the `__main__` block, and imports only they used.
  - keep `FixtureLoop`, `_run_member`, `produce` and `LoopRefused`.
- In: `tests/integration/test_host_loop.py`:
  - import the moved names from `eval.host_loop`.
  - delete the receipt, canonical-bytes and `_main` tests (the tests that call `regenerate`, `write_receipt`, `committed_bytes`, `canonical` or `_main`).
  - keep `test_host_loop_closed_schema`, `test_host_loop_drives_supervised_fixture_serve`, `test_host_loop_report_regression_and_escape` and `test_host_loop_requires_member_auditor_green`.
- In: `tests/integration/test_stages.py`: delete `test_host_loop_and_receipt_registered_checks_lift` (the parametrized test over `host-loop-report.json` and `exit-receipt.json`).
- In: `tests/integration/test_closed_sets.py`:
  - remove the `HOST_LOOP_EXPECTED` and `HOST_LOOP_MEMBERS` assertions from `test_artifacts_closed_sets_and_constants`.
  - remove the `exit-receipt.json` and `host-loop-report.json` rows from the `KNOWN_ARTIFACTS` assertion in `test_stages_closed_sets_and_constants`.
- In: `tests/unit/test_artifacts.py`:
  - `test_producing_run_check` calls `chupa.artifacts._check_producing_run` directly instead of building a `HostLoopEntry`: `"member-0/0"` passes, and each of `"nosep"`, `"member/x1"` and `"Upper/0"` raises `ValueError` with the same message. That keeps the test independent of any report type later tickets remove.
  - `test_integer_version_check` drops its `HostLoopReport` and `ExitReceipt` rows.
- In: `docs/how-chupa-works.md` section 13: remove "host loop" and "exit receipt" from the list. In `hosts/fixture/README.md`, drop "produce exit reports" and replace "and runtime report production" with "and runtime production".
- Unaffected: the other coverage-dependent test files of `chupa/artifacts.py` and `chupa/stages.py` reference none of the removed names (a grep for `HostLoop`, `ExitReceipt`, `ExitReads`, `HOST_LOOP_` and `EXIT_RECEIPT` outside the fenced files finds only test names and a path-string check in `tests/integration/test_fixture_host.py` that does not import them), so their behavior does not change.
- Out: the committed `tickets/phase6-exit/` report files (history; nothing reads them); moving `eval/host_loop.py` under `tests/` (ticket `eval-move-soak-battery-host-loop`); the other report types; `eval/harness.py` and the review-baseline report.

## Scope fence
- chupa/artifacts.py
- chupa/stages.py
- eval/host_loop.py
- tests/integration/test_host_loop.py
- tests/integration/test_stages.py
- tests/integration/test_closed_sets.py
- tests/unit/test_artifacts.py
- docs/how-chupa-works.md
- hosts/fixture/README.md

## Acceptance criteria
1. `uv run python -c "import chupa.artifacts as a, chupa.stages as s; assert not any(hasattr(a, n) for n in ('HostLoopReport','HostLoopEntry','ExitReceipt','ExitReads','HOST_LOOP_REPORT','EXIT_RECEIPT')); assert 'host-loop-report.json' not in s.KNOWN_ARTIFACTS and 'exit-receipt.json' not in s.KNOWN_ARTIFACTS"` exits 0, ruling out a type left behind in the engine or still registered.
2. `uv run python -c "import eval.host_loop as h; assert not any(hasattr(h, n) for n in ('write_receipt','regenerate','committed_bytes','write_report','main','_main')); h.HostLoopReport; h.produce"` exits 0, ruling out a leftover producer and a deleted harness.
3. `./dev.py test tests/integration/test_host_loop.py` exits 0 and still runs `test_host_loop_drives_supervised_fixture_serve`, so the end-to-end harness keeps working.
4. `./dev.py test tests/unit/test_artifacts.py tests/integration/test_closed_sets.py tests/integration/test_stages.py` exits 0.
5. `./dev.py test` exits 0.

## Verification
```
uv run python -c "import chupa.artifacts as a, chupa.stages as s; assert not any(hasattr(a, n) for n in ('HostLoopReport','HostLoopEntry','ExitReceipt','ExitReads','HOST_LOOP_REPORT','EXIT_RECEIPT')); assert 'host-loop-report.json' not in s.KNOWN_ARTIFACTS and 'exit-receipt.json' not in s.KNOWN_ARTIFACTS"
uv run python -c "import eval.host_loop as h; assert not any(hasattr(h, n) for n in ('write_receipt','regenerate','committed_bytes','write_report','main','_main')); h.HostLoopReport; h.produce"
./dev.py test tests/integration/test_host_loop.py
./dev.py test tests/unit/test_artifacts.py tests/integration/test_closed_sets.py tests/integration/test_stages.py
./dev.py test
```

## Definition of rejected
`HostLoopReport` or `ExitReceipt` is still defined in or registered by `chupa/`; the end-to-end host-loop tests are deleted rather than kept; a committed file under `tickets/` changes; or any file outside the fence changes.

## Time budget
- expected: 30m
- stuck: 60m
