---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- flake-check

## Context
- chupa/config.py
- chupa/git.py
- tests/test_host_mechanical.py
- docs/host-contract.md

## On-demand
- chupa/stages.py
- docs/how-chupa-works.md

## Goal / Why
`flake-check` decides that a flaky test touches "code being edited" only when the test's own file changed. That misses the main case: the ticket edits production code that the flaky test runs, so its flakiness may be the ticket's bug, yet it gets quarantined. After this change a `review.mechanical` entry can also declare `coverage: <path>`, a coverage.py JSON report written with per-test contexts by `pytest-cov --cov-context=test`, `[tool.coverage.json] show_contexts = true` and `[tool.coverage.run] core = "ctrace"`. The last setting matters: on Python 3.14 coverage's default `sysmon` core silently drops contexts. A flaky test also counts as edited when its context appears on a line this branch changed. Integration runs without coverage keep the test-file rule.

## Scope in / Scope out
- In: `chupa/config.py`: `MechanicalCheck.coverage: str | None = None`, a worktree-relative path. `_check_references` refuses `coverage` without `results` on the same entry with `ConfigError` key `review.mechanical.<i>.coverage`.
- In: `chupa/stages.py`, flaky classification from `flake-check`:
  - When the entry declares `coverage` and at least one flaky test needs classifying, read `<worktree>/<coverage>` after run 2.
  - A test is "edited" if its file is among the changed files (unchanged rule), or some changed line in a changed file lists a context whose part before the first `|` equals the test's node ID.
  - Context format, from a real report: `files.<path>.contexts` maps a line-number string to a list such as `["tests/test_m.py::TestC::test_c|run", ""]`.
  - Changed lines come from walking each hunk body of `ctx.git.diff(ctx.repo, MAIN, stem)` per file while tracking the new-side line counter, never from hunk headers.
    - Each `+` line contributes its new-side number.
    - A pure deletion (a run of `-` lines with no `+` line directly before or after it in the hunk) contributes the new-side line just before it and the one just after it, clamped to at least 1. A replaced run is already covered by its `+` lines and contributes no neighbors.
    - Context lines never contribute.
  - When a flaky test needs classifying, the entry fails if the report is missing, the JSON is unreadable, `contexts` is absent, or no line lists a context containing `|`. That last case is a run without `--cov-context=test`, where every line lists only `""`. The finding names the path, with the paved road: run with `--cov-context=test`, and set `[tool.coverage.json] show_contexts = true` and `[tool.coverage.run] core = "ctrace"`.
- In: `tests/test_fixture_host.py`: the `review.mechanical[0].model_dump()` expectation gains `"coverage": None`.
- In: `tests/test_host_mechanical.py`: tests with an exec fake that writes the results and coverage files.
- In: `docs/host-contract.md`: `coverage` in the `MechanicalCheck` row of `config-fields`, and in the flaky-test paragraph the edited rule plus the required host setup (`--cov-context=test`, `show_contexts = true`, `core = "ctrace"`).
- In: `docs/how-chupa-works.md` section 5.4: the coverage edited rule.
- Out: coverage at merge; running coverage in the engine; coverage thresholds (that is `covgate`); any change to which tests are flaky, quarantined or released.

## Scope fence
- chupa/config.py
- chupa/stages.py
- tests/test_host_mechanical.py
- tests/test_fixture_host.py
- docs/host-contract.md
- docs/how-chupa-works.md

## Acceptance criteria
1. Code edit marks a flaky test edited. The branch changes `pkg/m.py` line 3 only, and the flaky test is `tests/test_a.py::test_x` (unchanged file). The coverage report lists `tests/test_a.py::test_x|run` on `pkg/m.py` line 3, so Check ends `gate_failed` with a finding naming the test and no `flake_detected` signal. A test fails if the test is quarantined. On the same branch, a flaky test whose context is only on `pkg/m.py` line 2 is quarantined and Check passes; a test fails if it is marked edited. Checked by `uv run pytest tests/test_host_mechanical.py`.
2. Unexecuted edit does not. The same branch, with the test's context listed only on `pkg/m.py` line 9 (unchanged), quarantines the test and Check passes. A test fails if any covered file counts, rather than only changed lines. Checked by `uv run pytest tests/test_host_mechanical.py`.
3. A real-git branch deletes old line 5 of a 10-line `pkg/m.py` and changes nothing else, so new-side lines 4 and 5 are contributed.
   - With the test's context only on new-side line 5, the test is edited and Check fails.
   - With its context only on new-side line 2 (a context line in the same hunk), the test is quarantined and Check passes.

   A test fails if the deletion is ignored and the test quarantined, or if an unchanged context line marks it edited. Checked by `uv run pytest tests/test_host_mechanical.py`.
4. Fail closed. With `coverage` declared and a flaky test present, the entry fails with a finding naming the coverage path when the report is missing, and also when its `contexts` list only `""`. A test fails if the entry passes or the test is quarantined in either case. With no flaky test, a missing report is not read and does not fail. Checked by `uv run pytest tests/test_host_mechanical.py`.
5. An entry declaring `coverage` without `results` is refused at config load with `ConfigError.key == "review.mechanical.0.coverage"`. A test fails if the load succeeds or the refusal names another key. `docs/host-contract.md` stays in lockstep with `chupa/config.py`. Checked by `uv run pytest tests/test_host_mechanical.py tests/test_host_contract.py`.
6. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_host_mechanical.py tests/test_host_contract.py tests/test_fixture_host.py
uv run pytest -q
```

## Definition of rejected
The engine runs coverage; a covered line that is neither changed nor adjacent to a pure deletion marks a test edited; a declared coverage report is silently skipped when a flaky test needs classifying; flaky detection, quarantine or release rules change.

## Time budget
- expected: 60m
- stuck: 150m
