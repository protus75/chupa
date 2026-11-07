---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
none

## Context
- chupa/config.py
- dev.py
- pyproject.toml
- config.yaml

## Goal / Why
On 2026-11-06 the pre-run review approved `serve-no-auto-triage` after only searching for the names being removed. The implementer's full suite then failed in three files outside the fence, which spent the ticket's one allowed bounce. Tests that run a file's code can be found mechanically instead: coverage.py records which test ran each line.

After this change `./dev.py covmap` runs the host's test suite under coverage and writes a small map from each source file to the test files that execute it: `<state_dir>/coverage-map.json`. A follow-up ticket (`requisition-coverage-dependents`) hands that map to the pre-run review. This ticket only builds the map.

## Scope in / Scope out
- In: `pyproject.toml`: add `pytest-cov` to the `dev` dependency group, and coverage settings the map needs: `[tool.coverage.run] core = "ctrace"` and `[tool.coverage.json] show_contexts = true` (the same settings section 5.4 of `docs/how-chupa-works.md` requires for flake classification). Update `uv.lock`.
- In: `chupa/config.py`: `Review` gains an optional `coverage_map` entry, closed shape `{argv: Argv, report: <repo-relative path>}`, default absent. `report` uses the same path rule as `MechanicalCheck.results`/`coverage` (non-blank, relative, no `..`).
- In: `config.yaml`: `review.coverage_map` with `argv: [uv, run, pytest, -q, --cov=chupa, --cov=eval, --cov-context=test, --cov-report=json:.chupa/coverage.json]` and `report: .chupa/coverage.json`. Keep `review` otherwise empty.
- In: new `chupa/covmap.py`:
  - `reduce_map(report) -> dict[str, list[str]]`: from a coverage.py JSON report with test contexts, map each measured source file to the sorted, de-duplicated test files (the part of each context before `::`, contexts without `|` ignored) that executed any of its lines. A file executed by no test maps to `[]`. It reuses the context reader in `chupa/stages.py`: rename `_coverage_contexts` to `coverage_contexts` and change it to take the parsed report dict; its stages.py call site does `json.loads(path.read_text())`. Same validation, same errors.
  - `build(...)`: runs `review.coverage_map.argv` in the repo root through the process exec seam, reads and afterwards unlinks `report` directly on disk (the stages.py pattern; the FileSystem seam has no read or delete), and writes `<state_dir>/coverage-map.json` as `{"sha": <main HEAD sha via git.py>, "files": reduce_map(...)}` through `fs.publish`. A nonzero command exit, or a missing or invalid report, is a refusal and leaves any previous map untouched.
- In: `chupa/__main__.py`: verb `covmap`. It loads config, takes no lock (it runs tests and writes only its own state file), and refuses with the `chupa covmap: <message> -- <what to do instead>` form when `review.coverage_map` is absent or the build is refused. Exit 0 on success, 2 on a refusal.
- In: `dev.py`: subcommand `covmap` that runs `chupa covmap`, and its line in the module docstring.
- In: new `tests/test_covmap.py`: `reduce_map` on an inline report (two source files, contexts from two test files, one `|`-less context, one unexecuted file); `build` with a `tmp_path` report, a fake exec and a fake filesystem: success writes the map with the sha and removes the raw report; nonzero exit and a missing report each refuse and keep the previous map.
- In: `tests/test_config.py`: `review.coverage_map` accepted; an absolute or `..` report path and an unknown key refused with the dotted key named.
- In: `docs/how-chupa-works.md`: section 2.1 verbs table gets a `covmap` row (no lock; what it runs and writes; exit codes); section 2.2 lists `./dev.py covmap`; `docs/host-running.md`'s verb table gets a `covmap` row (no lock; runs `review.coverage_map.argv` and writes `<state_dir>/coverage-map.json`; exit 0/2); section 11's `review` row mentions `coverage_map`, and `docs/host-contract.md` adds it to the field inventory.
- Out: any reader of the map (ticket `requisition-coverage-dependents`); rebuilding the map automatically (on merge, on a timer, or when stale); measuring code run in child processes; `covgate`; changing `./dev.py test`.

## Scope fence
- pyproject.toml
- uv.lock
- chupa/config.py
- config.yaml
- chupa/covmap.py
- chupa/stages.py
- chupa/__main__.py
- dev.py
- tests/test_covmap.py
- tests/test_config.py
- docs/how-chupa-works.md
- docs/host-contract.md
- docs/host-running.md

## Acceptance criteria
1. `./dev.py test tests/test_covmap.py tests/test_config.py` exits 0, including the `reduce_map` and `build` cases in Scope in.
2. `grep -n "_coverage_contexts" chupa/stages.py` prints nothing.
3. `./dev.py covmap` exits 0 in this repo and `.chupa/state/coverage-map.json` lists `tests/test_serve.py` under `chupa/serve.py`.
4. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/test_covmap.py tests/test_config.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- `./dev.py test` or `covgate` behavior changes;
- the map is rebuilt automatically anywhere;
- a refused build overwrites or deletes an existing map;
- `covmap` takes the engine lock.

## Time budget
- expected: 60m
- stuck: 180m
