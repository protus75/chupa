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
- config.yaml

## On-demand
- chupa/drain.py
- chupa/serve.py
- chupa/merge.py
- chupa/tickets.py
- chupa/author.py
- chupa/triage.py
- chupa/box.py
- chupa/retro.py
- eval/harness.py
- eval/diagnose.py
- docs/how-chupa-works.md
- docs/host-contract.md

## Goal / Why
chupa is to ship on PyPI so a host installs it with `uv tool install chupa` instead of running it from a chupa checkout (2026-11-06). A wheel carries only the `chupa/` package. The prompt specs live outside it, in `<repo>/specs/`, and every loader finds them as `Path(__file__).resolve().parent.parent / "specs"`. An installed engine therefore has no prompts.

After this change:
- the specs live in `chupa/specs/`;
- every loader resolves them as `Path(__file__).resolve().parent / "specs"`, one path for a checkout and an install alike;
- `<repo>/specs/` no longer exists.

## Scope in / Scope out
- In: `git mv specs chupa/specs`, including any subdirectory present at the time (for example `specs/ask/` if `ask-prompt-verb` has merged). Spec text is unchanged except `chupa/specs/retro.md`, below.
- In: engine loaders resolve `chupa/specs/`:
  - `runner.SPECS_DIR` and `policy.SPECS`;
  - `chupa/ask.py`, if it exists;
  - `eval/harness.py` and `eval/diagnose.py` (`SPECS` and the docstring and help text naming `specs/review.md`);
  - the spec-version read in `watch.py`, or in `chupa/observe.py` if `observe-verbs-host-extension` has merged.
- In: repo-path matchers that look for spec files in a diff or ticket now look under `chupa/specs/`:
  - `drain.UPGRADE_PREFIXES` becomes `("chupa/",)`, which already covers the specs, and the module docstring says so;
  - `serve.engine_trees` reads only `HEAD:chupa`, and the `serve_handoff` signal body drops its `specs` key;
  - `merge.py`'s changed-spec regex matches `chupa/specs/[^/]+\.md`;
  - the `tickets.py` check that refuses a spec file in `## Context` matches a parent of `chupa/specs`.
- In: stored box data stays valid. `Message.proposed_spec_paths` (`box.py`) and `RetroProposal.proposed_spec_paths` (`retro.py`) keep their `^specs/[a-z0-9_-]+\.md$` pattern, because `Box.messages` re-validates every stored box file and 25 of them hold that form today. The field now means a spec path relative to the `chupa/` package:
  - `chupa/specs/retro.md` says "`specs/<name>.md` paths, relative to the `chupa/` package" instead of "repo-relative `specs/<name>.md` paths";
  - `author.py` and `triage.py` prefix each value with `chupa/` where they put `proposed_spec_paths` into a model request, so the model sees the real repo path.
- In: `config.yaml` `engine_plane_safety_inventory` names `chupa/specs/` instead of `specs/`, so spec edits stay inventoried.
- In: tests that read the real spec files, or assert the paths and values changed above, follow the move.
- In: docs.
  - `docs/how-chupa-works.md`: every `specs/` path in sections 1, 4.2, 4.4, 6.3, 6.5, 7.1 (self-upgrade) and 8.4.
  - `docs/host-contract.md`: the `engine_plane_safety_inventory` example and the Instance custody sentence on restarting when `chupa/` or `specs/` changes.
- Out:
  - spec content beyond the one `retro.md` sentence;
  - spec versions and the baseline identity (`baseline_identity` reads versions, not paths);
  - stored box files and journal events;
  - packaging (`pyproject.toml`), which is `pypi-package`;
  - `CHUPA_PLAN.md`.

## Scope fence
- specs/
- chupa/specs/
- chupa/runner.py
- chupa/policy.py
- chupa/drain.py
- chupa/serve.py
- chupa/merge.py
- chupa/tickets.py
- chupa/author.py
- chupa/triage.py
- chupa/ask.py
- chupa/observe.py
- watch.py
- eval/harness.py
- eval/diagnose.py
- config.yaml
- tests/test_author.py
- tests/test_baseline.py
- tests/test_closed_sets.py
- tests/test_diagnose_eval.py
- tests/test_drain_upgrade.py
- tests/test_eval_harness.py
- tests/test_fixture_host.py
- tests/test_merge.py
- tests/test_requisition.py
- tests/test_retro_box.py
- tests/test_serve.py
- tests/test_specs.py
- tests/test_stages.py
- tests/test_tickets.py
- tests/test_triage.py
- tests/test_watchdog_activation.py
- tests/test_ask.py
- tests/test_watch.py
- docs/how-chupa-works.md
- docs/host-contract.md
- chupa/__main__.py
- chupa/artifacts.py
- chupa/stages.py
- chupa/box.py
- chupa/retro.py
- tests/test_config.py
- tests/test_driver.py
- tests/test_echo_stage.py
- tests/test_llm_effect.py
- tests/test_mergequeue.py
- tests/test_policy.py
- tests/test_provider_cooldown_failover.py
- tests/test_retro.py
- tests/test_status.py

## Acceptance criteria
1. `specs/` does not exist and `chupa/specs/review.md` does. The first Verification command checks both, and fails if `runner.SPECS_DIR` is not `chupa/specs`.
2. `drain.UPGRADE_PREFIXES == ("chupa/",)`, not `("chupa/", "specs/")`. `tests/test_closed_sets.py` asserts it.
3. A merged commit touching `chupa/specs/b.md` triggers the drain handoff in `tests/test_drain_upgrade.py`, and `merge.py` reports `chupa/specs/a.md` and `chupa/specs/z.md` as `changed_spec_paths` in `tests/test_merge.py`.
4. A ticket whose `## Context` lists `chupa/specs/review.md` gets the "prompt spec" finding in `tests/test_tickets.py`.
5. A box message with `proposed_spec_paths: ["specs/review.md"]` still loads through `Box.messages`, and the Author request built from it holds `chupa/specs/review.md`, not `specs/review.md`. A test in `tests/test_author.py` checks this.
6. `config.yaml` lists `chupa/specs/` in `engine_plane_safety_inventory`. The second Verification command checks it.
7. `uv run pytest -q` exits 0.

## Verification
```
uv run python -c "from pathlib import Path; from chupa import runner, policy; assert not Path('specs').exists() and Path('chupa/specs/review.md').is_file(); assert runner.SPECS_DIR == policy.SPECS == Path('chupa/specs').resolve()"
uv run python -c "from chupa.config import load_config; from pathlib import Path; assert 'chupa/specs/' in load_config(None, cwd=Path('.')).engine_plane_safety_inventory"
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of the following holds:
- any loader still resolves specs outside the `chupa/` package;
- both `specs/` and `chupa/specs/` paths are accepted anywhere (no dual path);
- the `proposed_spec_paths` pattern changes, or a stored box file would fail to load;
- spec text changes beyond the one `retro.md` sentence;
- `pyproject.toml` changes.

## Time budget
- expected: 75m
- stuck: 180m
