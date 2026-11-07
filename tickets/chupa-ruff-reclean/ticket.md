---
state: confirmed
source: human
priority: P1
kind: chore
---

## Depends on
- none

## Context
- pyproject.toml

## Goal / Why
`chupa-ruff-src` left `chupa/`, `eval/`, `dev.py` and `watch.py` ruff-clean on 2026-11-06. Later merges reintroduced lint findings and format drift, because nothing checks ruff on merge yet. `chupa-test-gates` adds that check but cannot pass while the repo is dirty. This ticket makes the non-test Python tree and the two ticket evidence scripts clean again. The test tree is cleaned by `chupa-ruff-reclean-tests-a-l` and `chupa-ruff-reclean-tests-m-z`, so each diff stays under the diff budget.

## Scope in / Scope out
- In: run `uv run ruff check --fix` and `uv run ruff format` on the fenced paths, then fix the remaining findings by hand without changing behavior. Known ones:
  - E501 (line over 200) in `chupa/merge.py`, `chupa/observe.py`, `chupa/requisition.py`, `chupa/runner.py`, `chupa/serve.py`, `chupa/stats.py`, `chupa/status.py`, `eval/daemon_soak.py`: split the line.
  - E741 (variable named `l`) in `tickets/status-optional-locks/evidence/stale_lock.py`: rename the variable.
  - Any finding a later merge added in these paths; find them with `uv run ruff check chupa eval dev.py watch.py tickets/status-optional-locks/evidence/stale_lock.py tickets/graph-lane-cleanup/evidence/regress_graph_lanes.py`.
- Out: every file under `tests/`; `pyproject.toml` and its ruff settings; every `.md` file; any behavior change.

## Scope fence
- chupa
- eval
- dev.py
- watch.py
- tickets/status-optional-locks/evidence/stale_lock.py
- tickets/graph-lane-cleanup/evidence/regress_graph_lanes.py

## Acceptance criteria
1. `uv run ruff check chupa eval dev.py watch.py tickets/status-optional-locks/evidence/stale_lock.py tickets/graph-lane-cleanup/evidence/regress_graph_lanes.py` exits 0.
2. `uv run ruff format --check chupa eval dev.py watch.py tickets/status-optional-locks/evidence/stale_lock.py tickets/graph-lane-cleanup/evidence/regress_graph_lanes.py` exits 0.
3. `./dev.py test` exits 0.

## Verification
```
uv run ruff check chupa eval dev.py watch.py tickets/status-optional-locks/evidence/stale_lock.py tickets/graph-lane-cleanup/evidence/regress_graph_lanes.py
uv run ruff format --check chupa eval dev.py watch.py tickets/status-optional-locks/evidence/stale_lock.py tickets/graph-lane-cleanup/evidence/regress_graph_lanes.py
./dev.py test
```

## Definition of rejected
A finding is silenced with `noqa` or a new ignore instead of fixed; `pyproject.toml`, a file under `tests/`, or a markdown file changes; behavior changes.

## Time budget
- expected: 30m
- stuck: 90m
