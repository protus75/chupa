---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- none

## Context
- chupa/__main__.py
- docs/how-chupa-works.md
- tests/test_cli.py

## Goal / Why
Python hosts need a coverage gate whose thresholds an implementing agent cannot quietly lower. Today chupa has no coverage check, and a single global `--cov-fail-under` cannot hold a hard-to-test file to a lower bar than the rest. After this change `python -m chupa covgate` reads a dedicated threshold file, `test-gate.toml`, and the coverage.py JSON report of the host's unit run. It exits 1 when the repository, a declared package, or any file is below its minimum. Keeping thresholds in their own file lets a host list that file in `engine_plane_safety_inventory`, so lowering a threshold always goes through a human ticket. The host runs covgate as a `review.mechanical` entry after its unit-test entry. covgate never runs tests itself.

## Scope in / Scope out
- In: new `chupa/covgate.py`, standard library only (`tomllib`, `json`), no coverage.py import.
  - Gate file grammar. Top-level table `[coverage]` with required number `default` and optional number `repository`, which defaults to `default`. Optional sub-tables `[coverage.packages]` and `[coverage.files]` map a repo-relative POSIX path to a number. Every number is in 0..100. Any other key or table, a missing `default`, or an out-of-range or non-number value is refused with the offending dotted key named. Optional `[unit]` with optional number `budget_seconds` (default 60, greater than 0) is accepted and validated here so the file has one grammar. The `testguard` ticket consumes it; covgate itself ignores the budget.
  - Report input: a coverage.py JSON report (`meta.format` 3). It uses `files.<path>.summary` fields `covered_lines`, `num_statements`, `covered_branches`, `num_branches` and `files.<path>.missing_lines`. A branch field absent from a summary counts as 0.
  - Percent for any set of files = 100 * (sum covered_lines + sum covered_branches) / (sum num_statements + sum num_branches). A set with zero statements and zero branches is 100. This equals coverage.py's own `percent_covered` for one file and for the totals.
  - Checks:
    - The repository: all files in the report must reach `repository`.
    - Each `[coverage.packages]` entry: the files at or under that path must reach its value. Paths match at a path boundary (`pkg` admits `pkg/a.py`, not `pkg2/a.py`).
    - Each file in the report must reach its minimum. Precedence: its own `[coverage.files]` entry, else the longest matching `[coverage.packages]` entry, else `default`.
  - Comparison is against the unrounded percent.
  - Each failure prints one line naming the path (or `repository`), its percent, the minimum and which entry set it. A file line also names its missing lines. Each line ends with the paved road: add unit tests that execute the missing lines. Lowering a threshold in the gate file is a human ticket's decision.
  - Public API, pure and needing no files in its tests:
    - `parse_gate(text) -> Gate` validates the gate file text. The result carries every threshold and `budget_seconds` (60 when `[unit]` or the key is absent). On a refusal it raises `GateInvalid(ValueError)`, whose `key` attribute holds the offending dotted key and whose message names it. The `testguard` ticket calls it.
    - `evaluate(gate, report) -> list[str]` takes the parsed report mapping and returns the failure lines; an empty list means pass.
- In: `chupa/__main__.py`: verb `covgate` with `--gate PATH` (default `test-gate.toml`) and `--report PATH` (default `coverage.json`), both relative to the invocation cwd. It dispatches before `load_config`, like `new`, so it runs in a host worktree without loading chupa config.
  - Exit 0: every check passes.
  - Exit 1: any check fails.
  - Exit 2: a missing or invalid gate file, or a missing or unparsable report. The refusal uses the `chupa covgate: <message> -- <what to do instead>` form.
- In: new `tests/test_covgate.py`.
- In: `docs/how-chupa-works.md` section 2.1 verbs table: a `covgate` row (no lock; what it reads; exit codes).
- Out: running pytest or coverage; `chupa/config.py`; any `config.yaml`; adding coverage or pytest-cov to `pyproject.toml`; the unit-test guard and time budget (ticket `testguard`); adopting the gate in this repo.

## Scope fence
- chupa/covgate.py
- chupa/__main__.py
- tests/test_covgate.py
- docs/how-chupa-works.md

## Acceptance criteria
1. A file entry overrides its package. With `default = 90`, package `pkg = 80` and file `pkg/hard.py = 50`, `pkg/hard.py` at 60% passes and `pkg/easy.py` at 85% passes. A test fails if `pkg/hard.py` is held to 80 or 90, or `pkg/easy.py` to 90. Checked by `uv run pytest tests/test_covgate.py`.
2. Package and repository minimums are aggregates, not per-file maxima. A package whose files are 100% (10 statements) and 0% (90 statements) is 10% and fails `pkg = 50`. A test fails if the package is judged by its best file or by an unweighted mean of file percents. Checked by `uv run pytest tests/test_covgate.py`.
3. Percent includes branches. A summary with 4 statements (3 covered) and 2 branches (1 covered) is 66.67%, not 75%, and fails a minimum of 70. Checked by `uv run pytest tests/test_covgate.py`.
4. Package paths match at a path boundary. Entry `pkg = 50` does not apply to `pkg2/a.py`, which falls back to `default`. Checked by `uv run pytest tests/test_covgate.py`.
5. Comparison is unrounded. A file at 8999 of 10000 statements (89.99%) fails `default = 90`. A file at 99999 of 100000 (99.999%) fails `default = 100`. A test fails if the percent is rounded before comparison. Checked by `uv run pytest tests/test_covgate.py`.
6. Report edge cases:
   - A summary without `covered_branches` and `num_branches`, with 3 of 4 statements covered, is 75% and passes a minimum of 75.
   - A file with 0 statements and 0 branches passes `default = 100`.
   - A declared package `pkg = 100` whose files all have 0 statements and 0 branches passes: both the package aggregate and each file count as 100%.

   A test fails on a KeyError, a ZeroDivisionError, or a 0% result. Checked by `uv run pytest tests/test_covgate.py`.
7. `parse_gate` raises `GateInvalid` for each of these, with `key` set to the offending dotted key, and never ignores it:
   - an unknown key (for example `[coverage] minimum = 90`);
   - a missing `default`;
   - a value of 101;
   - `[unit] budget_seconds = 0`, refused naming `unit.budget_seconds`.

   The parsed budget is 60 when `[unit]` is absent. Checked by `uv run pytest tests/test_covgate.py`.
8. The CLI cases run `main(["covgate", ...], cwd=tmp_path)` where `tmp_path` has no `config.yaml`:
   - an invalid gate file exits 2;
   - a missing report exits 2;
   - a below-minimum file exits 1 and prints its path and missing lines to stdout;
   - all passing exits 0.

   A test fails if covgate exits 2 with a config error. Checked by `uv run pytest tests/test_covgate.py`.
9. `docs/how-chupa-works.md` section 2.1 lists `covgate`.
10. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_covgate.py
uv run pytest -q
```

## Definition of rejected
covgate imports coverage.py or runs a test process; a threshold is silently defaulted when the gate file has an unknown or invalid key; `chupa/config.py` or a `config.yaml` changes; covgate loads chupa config.

## Time budget
- expected: 45m
- stuck: 120m
