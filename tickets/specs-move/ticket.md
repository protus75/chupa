---
state: confirmed
source: human
priority: P3
kind: chore
---

## Depends on
none

## Context
- chupa/runner.py
- chupa/policy.py
- chupa/serve.py

## On-demand
- watch.py
- eval/harness.py
- eval/diagnose.py
- config.yaml

## Goal / Why
chupa is to ship on PyPI (`pypi-package`). A wheel carries only the `chupa/` package, but the prompt specs live in `<repo>/specs/`, so an installed engine has no prompts (2026-11-06). This is the first of two tickets replacing `specs-in-package`, which needed 43 files against the 30-file diff budget.

After this change the specs live in `chupa/specs/`, every loader resolves them as `Path(__file__).resolve().parent / "specs"` (or the repo-root equivalent `<root>/chupa/specs`), and `<repo>/specs/` no longer exists. `spec-path-matchers` then repoints the diff and ticket matchers and the docs.

## Scope in / Scope out
- In: `git mv specs chupa/specs`, including `specs/ask/`. Spec text is unchanged.
- In: loaders:
  - `runner.SPECS_DIR` and `policy.SPECS`;
  - `watch.py`'s spec-version read (`ROOT / "specs"`);
  - `eval/harness.py` and `eval/diagnose.py`: `SPECS`, plus the docstring and help text naming `specs/review.md`.
- In: `serve.engine_trees` reads only `HEAD:chupa` (it fails once `HEAD:specs` is gone), returns that one tree id, and the `serve_handoff` signal body drops its `specs` key.
- In: `config.yaml` `engine_plane_safety_inventory` names `chupa/specs/` instead of `specs/`, so spec edits stay inventoried.
- In: tests that read the real spec files or assert the serve change: `tests/test_author.py` (`specs/author.md` load only), `tests/test_baseline.py`, `tests/test_diagnose_eval.py`, `tests/test_eval_harness.py`, `tests/test_fixture_host.py`, `tests/test_policy.py` (`ROOT / "specs"` only; the synthetic `specs/` fence and inventory strings stay), `tests/test_requisition.py`, `tests/test_serve.py`, `tests/test_specs.py`, `tests/test_stages.py`, `tests/test_watchdog_activation.py`.
- Out:
  - `chupa/specs.py` stays where it is; Python still imports the module over the new directory. `specs-module-into-package` moves it.
  - `drain.py`, `merge.py`, `tickets.py`, `author.py`, `triage.py`, `artifacts.py`, `stages.py`, `chupa/specs/retro.md`, and the docs: `spec-path-matchers`.
  - spec versions and the baseline identity; stored box files and journal events; `pyproject.toml`; `CHUPA_PLAN.md`.
- The diff is at most 29 files; touch no file outside `## Scope fence`.

## Scope fence
- specs/
- chupa/specs/
- chupa/runner.py
- chupa/policy.py
- chupa/serve.py
- watch.py
- eval/harness.py
- eval/diagnose.py
- config.yaml
- tests/test_author.py
- tests/test_baseline.py
- tests/test_diagnose_eval.py
- tests/test_eval_harness.py
- tests/test_fixture_host.py
- tests/test_policy.py
- tests/test_requisition.py
- tests/test_serve.py
- tests/test_specs.py
- tests/test_stages.py
- tests/test_watchdog_activation.py

## Acceptance criteria
1. `specs/` does not exist, `chupa/specs/review.md` does, and `runner.SPECS_DIR == policy.SPECS == chupa/specs`. The first Verification command checks all three.
2. `config.yaml` lists `chupa/specs/` and not `specs/` in `engine_plane_safety_inventory`. The second Verification command checks it.
3. The `serve_handoff` body in `tests/test_serve.py` is `{"signal": "serve_handoff", "chupa": <HEAD:chupa tree>}`, with no `specs` key.
4. `uv run pytest -q` exits 0.

## Verification
```
uv run python -c "from pathlib import Path; from chupa import runner, policy; assert not Path('specs').exists() and Path('chupa/specs/review.md').is_file(); assert runner.SPECS_DIR == policy.SPECS == Path('chupa/specs').resolve()"
uv run python -c "from chupa.config import load_config; from pathlib import Path; i = load_config(None, cwd=Path('.')).engine_plane_safety_inventory; assert 'chupa/specs/' in i and 'specs/' not in i"
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of the following holds:
- any loader still resolves specs outside the `chupa/` package;
- any loader accepts both `specs/` and `chupa/specs/` (no dual path);
- spec text changes;
- a file outside `## Scope fence` changes.

## Time budget
- expected: 60m
- stuck: 150m
