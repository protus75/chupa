---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- retro-test-measurements

## Context
- chupa/retro.py::RetroProposal
- chupa/retro.py::RetroArtifact
- chupa/retro.py::Retro.emit_proposals
- chupa/box.py::Message
- chupa/box.py::Box.enqueue
- chupa/author.py::author
- chupa/triage.py
- chupa/observe.py::snapshot
- tests/integration/test_retro.py::test_artifact_is_closed_and_proposals_pair_the_risks
- tests/integration/test_retro_box.py::test_completed_retro_proposals_reach_prompt_spec_merge
- tests/integration/test_triage.py::test_retro_proposal_paths_in_triage_request
- tests/integration/test_author.py::test_author_uses_baseline_resolution
- docs/how-chupa-works.md#9.5 Retro

## On-demand
- chupa/specs/retro.md
- tests/integration/test_watch.py

## Goal / Why
A retro proposal may name only `specs/<name>.md` prompt specs. After `retro-test-measurements` the retro sees slow suites, slow tests and low-coverage files, but it cannot propose repairing the host's tests (2026-11-08). After this change a proposal can be a test repair: it names one issue from a closed list and the repo paths to change. It reaches the Suggestion Box as a `retro_finding` and is authored like any other proposal. The retro prompt describes each test issue, the evidence that shows it, and repairs that address it.

## Scope in / Scope out
- In: `chupa/box.py`.
  - Add `TestIssue = Literal["unit-io", "slow", "drift", "flaky", "coverage-hard", "over-mocking", "weak-assertion", "shared-state", "duplicate", "skip-rot"]`.
  - `Message` gains `test_issue: TestIssue | None = None` and `proposed_paths: list[RepoPath] = []`. `RepoPath` is a nonblank repo-relative path with no `..` segment and no leading `/`.
  - `_coherent` for a `retro_finding` requires exactly one of `proposed_spec_paths` and `proposed_paths` to be nonempty, and `test_issue` set exactly when `proposed_paths` is nonempty. Every other class refuses `test_issue` and `proposed_paths` as it refuses the existing proposal fields.
  - `Box.enqueue` accepts and stores both fields. Existing box files load unchanged.
- In: `chupa/retro.py`.
  - `RetroProposal` gains `test_issue` and `proposed_paths` with the same types. `proposed_spec_paths` defaults to `[]`, and a model validator enforces the same exactly-one rule.
  - `emit_proposals` hashes `proposal.model_dump(exclude_defaults=True)` for `proposal_id`. An existing spec proposal therefore keeps its id and is never re-filed.
- In: `chupa/specs/retro.md`, version `"1.3"`.
  - The Task gains a test-repair part. Use `measurements.tests`, `measurements.coverage`, flake and gate events, and test source read from the workspace as evidence. Propose a test repair only where the evidence shows the issue.
  - It lists each `TestIssue` with what shows it and example repairs:
    - `unit-io`: a unit test touches disk, network or a real process. Inject the seam or a fake, call the library function instead of shelling out, or move the test to the integration suite.
    - `slow`: a suite or test dominates `measurements.tests`. Fake the clock and sleeps, shrink fixtures, split a large test, run in parallel, or widen the scope of expensive shared setup.
    - `drift`: tests hand-build data that diverges from the code. Build it through one shared fixture or builder that uses the code's own types.
    - `flaky`: flake events. Isolate shared state, fake time, randomness and ordering, and check whether it fails only under parallel runs.
    - `coverage-hard`: a file's coverage stays low across runs. Move the hard-to-test code into its own small file, which may get a lower gate, and raise the rest to the default.
    - `over-mocking`: tests assert on mock calls or internals. Assert observable outputs, using fakes at the seam.
    - `weak-assertion`: a test also passes on a wrong result. Assert exact values that a likely wrong implementation would not produce.
    - `shared-state`: order dependence or leaked globals, environment or files. Use per-test fixtures, `tmp_path` and `monkeypatch`.
    - `duplicate`: repeated tests of one behavior. Parametrize or merge them.
    - `skip-rot`: tests skipped across runs. Fix or delete them.
  - The Output format gives both proposal shapes and the exactly-one rule.
- In: `chupa/author.py` and `chupa/triage.py` request JSON gain `"test_issue"` and `"proposed_paths"`. The paths pass through as-is, with no `chupa/` prefix.
- In: `chupa/observe.py` `snapshot` box message fields gain `Test issue` and `Proposed paths` rows when set.
- In: tests.
  - `tests/integration/test_retro.py::test_artifact_is_closed_and_proposals_pair_the_risks` also refuses:
    - a proposal with both path lists;
    - one with neither;
    - `test_issue` without `proposed_paths`;
    - an unknown issue;
    - a `..` path.

    A valid test proposal parses.
  - `tests/integration/test_retro_box.py`:
    - `test_test_proposal_reaches_box`: a test proposal becomes a `retro_finding` with its `test_issue` and `proposed_paths`.
    - `test_spec_proposal_id_unchanged`: the existing `PROPOSAL`'s `proposal_id` equals `sha256(json.dumps(PROPOSAL, sort_keys=True, separators=(",", ":"), ensure_ascii=False))[:16]`, which rules out re-filing old proposals.
  - `tests/integration/test_triage.py` and `tests/integration/test_author.py`: a test proposal's request carries `"test_issue"` and unprefixed `"proposed_paths"`.
  - `tests/integration/test_watch.py::test_snapshot_box_messages` shows the two new rows for a test proposal.
- In: `docs/how-chupa-works.md` section 9.5 describes the two proposal kinds and the test issue list.
- Out: new message classes, `box_policy` rows, merge-time retro signals, retro measurements, Check recording, and the VS Code extension's JavaScript.

## Scope fence
- chupa/box.py
- chupa/retro.py
- chupa/specs/retro.md
- chupa/author.py
- chupa/triage.py
- chupa/observe.py
- tests/integration/test_retro.py
- tests/integration/test_retro_box.py
- tests/integration/test_triage.py
- tests/integration/test_author.py
- tests/integration/test_watch.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_retro.py tests/integration/test_retro_box.py` exits 0, including `test_test_proposal_reaches_box` and `test_spec_proposal_id_unchanged`. The second rules out a changed id for an existing spec proposal.
2. `./dev.py test tests/integration/test_triage.py tests/integration/test_author.py tests/integration/test_watch.py` exits 0.
3. `chupa/specs/retro.md` has version `"1.3"` and names every `TestIssue` value.
4. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_retro.py tests/integration/test_retro_box.py
./dev.py test tests/integration/test_triage.py tests/integration/test_author.py tests/integration/test_watch.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- `proposed_spec_paths` is renamed, or an existing box file fails to load;
- an existing spec proposal gets a new `proposal_id`;
- a test proposal can name an absolute path or a `..` path;
- the issue list is open text instead of a closed `Literal`.

## Time budget
- expected: 60m
- stuck: 150m
