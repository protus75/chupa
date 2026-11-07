---
state: confirmed
source: human
priority: P3
kind: feature
---

## Depends on
none

## Context
- chupa/drain.py
- chupa/serve.py
- tests/test_drain_upgrade.py
- docs/how-chupa-works.md

## On-demand
- tests/test_drain.py

## Goal / Why
`drain` treats any admitted merge whose diff touches `UPGRADE_PREFIXES` (`chupa/`, `specs/`) as a self-upgrade. It then re-execs itself with `uv run --project <engine> python -m chupa`, where `<engine>` is `Path(__file__).resolve().parent.parent`. That is only right when the drained repo is chupa's own source tree.

On a host repo, a merge touching the host's own `chupa/` or `specs/` directory triggers a self-upgrade that never happened. For a pip-installed engine (`pypi-package`), `<engine>` is `site-packages`, so the re-exec fails (2026-11-06).

`serve` already makes this distinction. It watches the engine's own checkout trees, never the host's merges, and a non-git engine does not watch (docs section 7.2).

After this change, `drain` self-upgrades only when the repo it drains is the engine's own source tree. Anywhere else, a merge never hands off.

## Scope in / Scope out
- In: `chupa/drain.py`:
  - a module constant `ENGINE = Path(__file__).resolve().parent.parent`, the engine's source root;
  - `reexec_argv`'s default engine reads `ENGINE` at call time, not at definition time;
  - the merge check that sets `self.upgrade` additionally requires `self.c.repo.resolve() == ENGINE`;
  - the module docstring says a self-upgrade happens only when the drain runs in the engine's own source tree.
- In: `tests/test_drain_upgrade.py`:
  - tests that expect a handoff monkeypatch `drain.ENGINE` to the test repo, and keep their assertions;
  - `test_an_admission_outside_the_engine_plane_does_not_re_exec` also monkeypatches `drain.ENGINE` to its test repo and keeps its assertions, so it still checks the prefix match alone;
  - new `test_a_host_repo_merge_touching_chupa_does_not_re_exec`: with `drain.ENGINE` pointing at a different directory, a merge touching `chupa/a.py` spawns no child and journals no `drain_handoff`.
- In: `tests/test_drain.py`: `test_drain_retro_runs_only_when_due[self-upgrade]` and `test_stop_survives_self_upgrade_handoff` monkeypatch `drain.ENGINE` to their test root, and keep their assertions.
- In: `tests/test_daemon_composition.py`: the `handoff` case of `test_control_lifecycle_cleanup_on_exit_and_handoff` monkeypatches `drain.ENGINE` to its test root, and keeps its assertions.
- In: `docs/how-chupa-works.md` section 7.1, the **Self-upgrade** paragraph: it applies only when the drained repo is the engine's own source tree. A host repo, or a pip-installed engine, never self-upgrades; upgrade those by reinstalling.
- Out:
  - `serve`, which already watches only the engine checkout;
  - `UPGRADE_PREFIXES` values and `engine_trees` (`specs-in-package` changes those);
  - packaging.

## Scope fence
- chupa/drain.py
- tests/test_drain_upgrade.py
- tests/test_drain.py
- tests/test_daemon_composition.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `test_a_host_repo_merge_touching_chupa_does_not_re_exec` passes: with `ENGINE` not equal to the repo, the faked child's `spawns` is `[]`, not one spawn.
2. `test_a_self_upgrading_admission_hands_off_before_the_next_dispatch` still passes with `drain.ENGINE` set to its repo.
3. `test_an_admission_outside_the_engine_plane_does_not_re_exec` passes with `drain.ENGINE` set to its repo: a lookalike-prefix admission spawns no child.
4. `docs/how-chupa-works.md` section 7.1 states the own-source-tree condition.
5. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_drain_upgrade.py tests/test_drain.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of the following holds:
- a merge in a repo other than the engine's source tree can still hand off;
- `serve` changes;
- the check compares anything but the resolved repo path against `ENGINE`, such as a config flag or an environment variable.

## Time budget
- expected: 25m
- stuck: 75m
