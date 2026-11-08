---
state: confirmed
source: human
priority: P0
kind: bug
---

## Depends on
- none

## Context
- chupa/__main__.py::_lint
- chupa/git.py::Git.git_common_dir
- chupa/config.py::load_config
- tests/integration/test_lint_verb.py::test_lint_skips_settled_tickets
- tests/regress_lint_carries.py
- tests/integration/test_cli.py::root
- tests/integration/test_cli.py::journal
- docs/host-authoring.md#Workflow

## Goal / Why
`chupa lint` with no stems skips tickets the journal records as settled (`merged`, `already_satisfied`) or `rejected`. Run inside a ticket worktree it skips nothing. `config.yaml` is committed with a relative `state_dir`, so in a worktree it resolves to `<worktree>/.chupa/state`. That directory does not exist, the journal reads empty, and lint checks every merged ticket against today's grammar.

Observed 2026-11-08: `core-drift-preflight` attempt 0 ran `./dev.py lint` in its worktree, got `37 of 393 tickets valid`, and bounced as `premise_failed` with a passing suite. That spent its only `premise_bounce` cap (`evidence/attempt0-lint-393.txt`). Any ticket whose Verification or agent runs `./dev.py lint` fails the same way.

After this change, lint run from a linked git worktree reads the journal of the main checkout, so it skips the same settled and rejected tickets it skips there.

## Scope in / Scope out
- In: `chupa/__main__.py` `_lint`. Before reading states, get `checkout.git.git_common_dir(checkout.repo)`. When its parent is not `checkout.repo.resolve()` (a linked worktree) and `checkout.config.state_dir` lies under `checkout.repo`, read states from `Journal(<main root> / state_dir.relative_to(checkout.repo), checkout.clock)`. Otherwise keep `checkout.journal`. Lint still writes nothing, in either checkout.
- In: `tests/integration/test_lint_verb.py`: new `test_lint_in_worktree_skips_main_settled_tickets`. In the `root` fixture repo, commit an invalid `tickets/merged/ticket.md` and a valid `tickets/active/ticket.md`, and record `merged` as `merged` in the main journal. Add a linked worktree with `git worktree add`, run `lint` with no stems and `cwd` at the worktree, and assert exit 0 and `lint: 1/1 tickets valid`. Asserting `1/2` with exit 1 would pass on the defect.
- In: new `tests/regress_lint_worktree_journal.py`, the carried reproducer. Like `tests/regress_lint_carries.py`, it puts the repo root on `sys.path`, builds the same scenario in a temp dir with real git, and calls `chupa.__main__.main(["lint"], cwd=<worktree>, ...)`.
  - Exit 0: prints `{"regression_result": "pass"}` and exits 0.
  - Exit 1 with the merged ticket reported: prints `{"regression_result": "defect"}` and exits 1.
  - Anything else: the traceback goes to stderr, and it prints `{"regression_result": "error"}` and exits 2.
- In: `docs/host-authoring.md` Workflow step 2: say that with no stems, lint run from a linked worktree uses the main checkout's journal.
- Out: how `load_config` resolves `state_dir` for other verbs, `status`, `drain`, `serve` and every other verb, and the settled-state set itself.

## Scope fence
- chupa/__main__.py
- tests/integration/test_lint_verb.py
- tests/regress_lint_worktree_journal.py
- docs/host-authoring.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_lint_verb.py` exits 0. It includes `test_lint_in_worktree_skips_main_settled_tickets`, which asserts `lint: 1/1 tickets valid` with exit 0 from the worktree, not `1/2` with exit 1.
2. `uv run python tests/regress_lint_worktree_journal.py` prints `{"regression_result": "pass"}` and exits 0 on the branch head.
3. `./dev.py test` exits 0, including the existing `test_lint_all_valid` assertion that lint creates no `.chupa` directory.
4. `docs/host-authoring.md` Workflow step 2 names the worktree case.

## Verification
```
./dev.py test tests/integration/test_lint_verb.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- lint writes to either checkout's state directory;
- `load_config` or the `state_dir` that any other verb uses changes;
- a ticket file gains a merged marker in place of the journal lookup;
- the reproducer prints `pass` on the merge base.

## Time budget
- expected: 25m
- stuck: 60m

## Regression
```
uv run python tests/regress_lint_worktree_journal.py
```
- carries: tests/regress_lint_worktree_journal.py
