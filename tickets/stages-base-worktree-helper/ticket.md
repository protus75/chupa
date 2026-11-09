---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
- none

## Context
- chupa/stages.py::prepare_worktree
- chupa/stages.py::_gather_bug
- chupa/stages.py::gather_evidence
- chupa/stages.py::check_hosts
- tests/integration/test_merge.py::context
- tests/integration/test_stages.py::test_full_gather_evidence_reuses_safety_gatherer

## Goal / Why
`chupa/stages.py` sets up a detached merge-base worktree with the same five lines in three places: the regression base in `_gather_bug` (`.regression-base/<stem>`), the base-red rerun in `gather_evidence` (`.base/<stem>`), and the host-check baseline in `check_hosts` (`.base/<stem>`). Each assembles the path under `ctx.config.worktree_root`, removes a stale worktree left at that path, creates the parent directory, and runs `worktree_add_detached`. The copies have already drifted: `check_hosts` lacks the `assert ctx.config.worktree_root is not None` the other two carry. After this change one helper owns that setup and all three sites call it, so a fix to base-worktree setup lands once.

## Scope in / Scope out
- In: `chupa/stages.py` gains one module-level helper, `async def _base_worktree(ctx: StageContext, kind: str, stem: str, base: str) -> Path`, placed after `prepare_worktree`. In order it asserts `ctx.config.worktree_root is not None` (same comment style as `StageContext.worktree`), builds `ctx.config.worktree_root / kind / stem`, removes the worktree there with `ctx.git.worktree_remove` when the path exists, creates its parent with `mkdir(parents=True, exist_ok=True)`, runs `ctx.git.worktree_add_detached(ctx.repo, path, base)`, and returns the path.
- In: the three sites replace their setup lines with `base_worktree = await _base_worktree(ctx, ".regression-base", ticket.stem, base)` in `_gather_bug`, `await _base_worktree(ctx, ".base", stem, base)` in `gather_evidence`, and `await _base_worktree(ctx, ".base", ticket.stem, base)` in `check_hosts`. Each site keeps its own `try` / `except` / `finally: await ctx.git.worktree_remove(ctx.repo, base_worktree)` exactly as today; only the setup lines move.
- Minimum chosen: a plain helper returning the path, not an `asynccontextmanager` that also owns removal. The removal is one identical line per site, but `_gather_bug` returns from inside its `try` and catches `GitError` from its body, so a context manager would restructure that block beyond moving setup lines; a plain helper removes the duplication with no control-flow change.
- In: one new test in `tests/integration/test_stages.py`, `test_base_worktree_clears_a_stale_worktree`. Using the `repo` fixture and `context(repo, [])` from `tests.integration.test_merge`, it records the first commit's sha, checks out a detached worktree at `ctx.config.worktree_root / ".base" / STEM` at that sha with `ctx.git.worktree_add_detached`, writes an untracked `stale.txt` into it, commits a change on `main` in `repo`, then calls `stages._base_worktree(ctx, ".base", STEM, second_sha)`. It asserts the returned path is `ctx.config.worktree_root / ".base" / STEM`, `stale.txt` is absent from it, and `await ctx.git.rev_parse(path, "HEAD")` equals the second sha, then removes the worktree. A helper that skips the stale-worktree removal fails it: `worktree_add_detached` raises `GitError` on the existing path, or the old checkout at the first sha with `stale.txt` survives.
- Existing tests that already drive the three call sites and must stay green unchanged: regression base — `tests/integration/test_bug_gate.py::test_regression_overlay_proves_defect` and `tests/integration/test_inbox.py` (asserts `.regression-base/<stem>` is removed); verify base-red — `tests/integration/test_stages.py::test_base_red_command_is_recorded_and_filed_without_failing_check`, `tests/integration/test_stages.py::test_full_gather_evidence_reuses_safety_gatherer`, `tests/integration/test_mergequeue.py::test_verification_uses_rebased_worktree`, `tests/integration/test_merge.py::test_base_red_verification_does_not_refuse_merge_regating`; host check base — `tests/integration/test_host_mechanical.py::test_base_red_entry_is_preexisting` and `tests/integration/test_mergequeue.py::test_host_checks_have_no_base_red_exemption`. `tests/integration/test_rework.py` monkeypatches `ctx.git.worktree_add_detached`; the helper still calls it through `ctx.git`, so that patch keeps applying.
- Coverage: the change removes more `chupa/stages.py` lines than it adds and touches no `tests/unit` path, so the `chupa/stages.py` unit floor in `test-gate.toml` is not lowered.
- Out: `prepare_worktree` (it branches rather than detaching and also prunes and deletes branches); the bodies of the three `try` blocks; the worktree directory names; `chupa/git.py`; any documentation, since no behavior changes.

## Scope fence
- chupa/stages.py
- tests/integration/test_stages.py

## Acceptance criteria
1. `uv run python -c "import ast,pathlib; src=pathlib.Path('chupa/stages.py').read_text(); n=sum(isinstance(c,ast.Call) and getattr(c.func,'attr','')=='worktree_add_detached' for c in ast.walk(ast.parse(src))); assert n==1, n"` exits 0: exactly one `worktree_add_detached` call remains in `chupa/stages.py`, not three.
2. `./dev.py test tests/integration/test_stages.py -k test_base_worktree_clears_a_stale_worktree` exits 0; the test rules out a helper that leaves a stale worktree in place (a `GitError` on add, or `stale.txt` still present at the old sha).
3. `./dev.py test` exits 0, including every existing test named in Scope in for the three call sites.

## Verification
```
uv run python -c "import ast,pathlib; src=pathlib.Path('chupa/stages.py').read_text(); n=sum(isinstance(c,ast.Call) and getattr(c.func,'attr','')=='worktree_add_detached' for c in ast.walk(ast.parse(src))); assert n==1, n"
./dev.py test tests/integration/test_stages.py -k test_base_worktree_clears_a_stale_worktree
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- a call site's `try` body, `except` clause, or `finally` removal changes beyond replacing the setup lines;
- the helper owns worktree removal on exit (a context manager or callback) instead of returning the path;
- an existing test's assertion is changed or deleted;
- a base worktree directory name or location changes.

## Time budget
- expected: 20m
- stuck: 60m
