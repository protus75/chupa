---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- testreport

## Context
- chupa/flake.py
- chupa/config.py
- chupa/daemon.py
- tests/test_host_mechanical.py
- tests/test_flake.py
- docs/host-contract.md

## On-demand
- chupa/stages.py
- docs/how-chupa-works.md

## Goal / Why
Flaky tests are failures, and today chupa cannot see them. Detection and quarantine code exists in `chupa/flake.py`, but nothing calls it, because Check only sees a host command's exit code. After this change, a `review.mechanical` entry can declare `results: <path>`, the per-test results file written by `chupa.testreport`. When such an entry fails, Check reruns it once in the same worktree and compares per-test outcomes.
- A test that failed and then passed is flaky.
- A flaky test whose file this ticket changed fails the ticket: the implementer must make it deterministic.
- Any other flaky test is quarantined through `Flake.detect`, which files a Suggestion Box `failure_report` that becomes a fix ticket. That test then stops blocking tickets until it is released.
- Release happens in Check: when a quarantined test passes after its fix ticket merged, Check calls `Flake.release`.

So the hold ships with its release.

## Scope in / Scope out
- In: `chupa/config.py`: `MechanicalCheck.results: str | None = None`, a worktree-relative path.
- In: `chupa/stages.py` `check_hosts`, for an entry with `results` only. Entries without `results` behave exactly as today.
  - Before every run of the entry (first run, rerun, base run), delete `<worktree>/<results>` with `Path.unlink(missing_ok=True)`, as `gather_evidence` does for registered files, so a stale file is never read as fresh evidence. Read it with `chupa.testreport.read_results` after each run.
    - A missing or invalid file after an exit-0 run fails the entry. Its finding names the path, with the paved road: the command must write it via `-p chupa.testreport --chupa-results <path>`.
    - A missing or invalid file after a nonzero first run, or a first-run results file with no `failed` test, takes today's path unchanged.
  - When the first run exits nonzero and has at least one `failed` test, rerun the same argv once in the same worktree, with no code change in between. Spool it to `check/host-NN-rerun.txt`. A missing or invalid results file after the rerun fails the entry like the exit-0 case.
  - Classification:
    - "Flaky": failed in run 1 and passed in run 2.
    - "Edited": the test's file, which is the node ID before its first `::`, is one of the branch's changed files.
    - "Quarantined": in `Flake.quarantine().tests`.
  - Blocking tests:
    - every test `failed` in run 2 unless it is quarantined and not edited;
    - every flaky edited test;
    - every flaky, unedited, unquarantined test that `Flake.detect` did not quarantine (cap reached).
  - Each flaky, unedited, unquarantined test is passed to `Flake.detect`:
    - `RerunEvidence` is `(test_id, "fail", "pass", True, True, True)`;
    - the summary names the test and the stem;
    - `occurrence_id` is `arrival_id("flake-detection", stem, attempt, test_id, n)` from `chupa/storm.py`, where n is the entry index (the storm Box refuses a missing id);
    - the reason is `failed then passed on a bare rerun; detection <k>`, where k is 1 plus the number of identities for this test in `Flake.quarantine().detected` that are no longer active, written in bijective base-26 letters (1 is `a`, 26 is `z`, 27 is `aa`). Letters are used because `chupa/box.py` `normalize` strips digits and `/` tokens before hashing the signature. A test that flakes again after a release therefore gets a new Box signature and a fresh quarantine and fix ticket, never a silent dedup to its released identity. Construct `Flake` through `daemon.flake_detection` with `ctx.driver.journal`, the Box from `storm_producer`, and `ctx.config`. Its `escalate` callable records the cap message, and that message goes into the cap-blocked test's finding.
  - Verdict:
    - The entry fails if any test is blocking, or if run 2 exits nonzero with no `failed` test.
    - Otherwise it passes, and its report carries no findings.
    - A failing entry gets one finding per blocking test, naming the test and why it blocks. The paved road for an edited flaky test is to make it deterministic by faking time, IO and ordering. For a real failure the road is to fix it.
    - A failing entry then takes today's base-red path unchanged.
  - Release: after any run of an entry with `results` (run 2 when a rerun happened, else run 1), check each active quarantine identity whose test is `passed`. If its Box message is resolved to a ticket stem with a `merged` state transition in the journal, call `Flake.release(box_id=..., evidence=GreenRerunEvidence(test_id, fix_stem, ctx.driver.clock(), "pass", True, True, True))`. Never call `release` for an unmerged fix, because it raises then.
- In: `chupa/daemon.py`: `flake_detection`'s docstring no longer says dormant.
- In: `tests/test_flake.py`: delete `test_flake_detection_is_dormant` and `test_flake_release_is_dormant`; they pin dormancy this ticket ends.
- In: `tests/test_fixture_host.py`: the `review.mechanical[0].model_dump()` expectation gains `"results": None`.
- In: `tests/test_host_mechanical.py`: the activation tests. Use an exec fake that writes the results file for each run.
- In: `docs/host-contract.md`: `results` in the `MechanicalCheck` row of `config-fields` (default unset), and a paragraph in "Checks and injectable seams" giving the rerun, classification, quarantine and release rules.
- In: `docs/how-chupa-works.md`:
  - Section 5.4 gains the `results` rerun rules.
  - Section 6.4's `quarantine` cap row drops "(not wired)".
  - Section 6.7's "Flaky tests" bullet describes the live behavior.
- Out:
  - flaky handling at merge (inline merge and the `serve` queue rerun commands without classification);
  - coverage-based edit detection (ticket `flake-edit-coverage`);
  - rerunning only the failed tests;
  - any change to `chupa/flake.py`'s rules;
  - chupa's own `config.yaml`.

## Scope fence
- chupa/config.py
- chupa/stages.py
- chupa/daemon.py
- tests/test_host_mechanical.py
- tests/test_flake.py
- tests/test_fixture_host.py
- docs/host-contract.md
- docs/how-chupa-works.md

## Acceptance criteria
1. Unedited flaky test is quarantined. Run 1 exits 1 with `tests/test_a.py::test_x` failed, and run 2 exits 0 with it passed. The test file is not among the branch's changed files.
   - The entry passes.
   - The journal gains one `flake_detected` signal for that test.
   - The Box gains one `failure_report` naming it.
   - `check/host-01-rerun.txt` is spooled.
   - Running the same Check again (replay) adds no second Box message or `flake_detected` signal.

   A test fails if Check fails or nothing is quarantined. Checked by `uv run pytest tests/test_host_mechanical.py`.
2. Edited flaky test blocks. The same runs, with `tests/test_a.py` among the branch's changed files: Check ends `gate_failed` with a finding naming `tests/test_a.py::test_x`, and no `flake_detected` signal is journaled. A test fails if an edited flaky test is quarantined or passes. Checked by `uv run pytest tests/test_host_mechanical.py`.
3. Real failure blocks and is never quarantined. A test failed in both runs fails Check with a finding naming it, and no `flake_detected` signal is journaled. Checked by `uv run pytest tests/test_host_mechanical.py`.
4. Quarantine holds. With `tests/test_a.py::test_x` already quarantined and unedited, a run where it fails in both runs while every other test passes ends Check `ok`. With its file edited, the same runs fail Check. Checked by `uv run pytest tests/test_host_mechanical.py`.
5. Release.
   - The quarantined test passes in a run, and its Box message is resolved to ticket `fix-x` with a `merged` transition: the journal gains a `flake_released` signal and the test leaves `Flake.quarantine().tests`.
   - With `fix-x` resolved but not merged: no release, and Check does not raise.

   Checked by `uv run pytest tests/test_host_mechanical.py`.
6. Re-flake after release. A test detected, then released after its fix merged, that fails then passes again is quarantined anew: a new `flake_detected` signal, a new Box message whose id differs from the released identity's `box_id`, and Check passes. A test fails if it blocks Check or dedups to the released identity. Checked by `uv run pytest tests/test_host_mechanical.py`.
7. Cap. With `caps.quarantine` already filled, a new unedited flaky test fails Check, with a finding carrying the cap message. Checked by `uv run pytest tests/test_host_mechanical.py`.
8. Fail closed and unchanged paths.
   - A declared `results` file missing after an exit-0 run fails the entry with a finding naming the path.
   - A results file left by run 1, followed by a run 2 that writes none, also fails the entry with the path finding.
   - Run 2 exiting 1 with no `failed` test fails the entry.
   - An entry without `results` makes exactly the calls it made before (no rerun).

   Checked by `uv run pytest tests/test_host_mechanical.py`.
9. `review.mechanical[].results` loads from config. `docs/host-contract.md` stays in lockstep with `chupa/config.py`, checked by `uv run pytest tests/test_host_contract.py`. `tests/test_flake.py` passes without the two dormancy tests and `tests/test_fixture_host.py` passes, checked by `uv run pytest tests/test_flake.py tests/test_fixture_host.py`.
10. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_host_mechanical.py tests/test_host_contract.py tests/test_flake.py tests/test_fixture_host.py
uv run pytest -q
```

## Definition of rejected
A flaky test of a changed test file is quarantined instead of blocking; an entry without `results` is rerun; `Flake.release` is called for an unmerged fix; `chupa/flake.py` changes; merge-time host checks change.

## Time budget
- expected: 90m
- stuck: 180m
