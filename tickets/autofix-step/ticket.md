---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- none

## Context
- chupa/config.py
- tests/test_host_mechanical.py
- docs/host-contract.md
- chupa/git.py
- tests/test_host_contract.py

## On-demand
- chupa/stages.py
- docs/how-chupa-works.md

## Goal / Why
Hosts with a linter or formatter want an implementer's changed files auto-fixed and auto-formatted before Check judges them, so a ticket never fails or reworks over a fix a tool could apply. Implementers forget to run the tools, and a format-only retry burns an attempt. Today chupa has no step that changes the branch between Implement and Check. After this change a host declares `review.autofix` entries in `config.yaml`. At the start of Check, before anything else, the engine runs each entry with the branch's existing changed files appended to its argv. If those files changed, it commits them on the ticket branch as `chupa(<stem>): autofix`, so Verification, gates, host checks and Review all judge the fixed head. The engine names no tool: a Python host declares, for example, `[uv, run, ruff, check, --fix, --exit-zero]` and `[uv, run, ruff, format]`.

## Scope in / Scope out
- In: `chupa/config.py`: new strict model `AutofixCommand` with required `code: str` and `argv: Argv`. Add `Review.autofix: list[AutofixCommand] = []`.
- In: `chupa/stages.py` `check()`: before `gather_evidence`, when `slip.outcome == "ok"` and `ctx.config.review.autofix` is nonempty:
  - Files: `ctx.git.diff_names(ctx.repo, MAIN, stem)`, keeping only paths that are regular files in the worktree and not under `tickets/`, in diff order. Deleted files are therefore never passed. With no files left, skip the step entirely.
  - Run each entry in config order through `run_host_command` with argv `[*entry.argv, *files]`, code `entry.code` and spool name `check/autofix-NN.txt` (NN = 1-based entry index).
  - Before the first entry runs, snapshot the listed files' worktree bytes with `Path.read_bytes()` (the seam has no read; this matches `lift_outbox`). The commit set is the listed files whose bytes differ from that snapshot after the last entry. An implementer's uncommitted edit that no tool touched is never committed.
  - If every entry exits 0 and the commit set is nonempty, `git add` exactly the commit set and commit it in the worktree with message `chupa(<stem>): autofix`, limited to those files. Otherwise make no commit.
  - If any entry fails (nonzero, timeout, missing executable):
    - stop running further autofix entries;
    - restore every listed file to the branch head with `ctx.git.restore(worktree, files, source=stem)`, which keeps committed file modes. This also discards any uncommitted implementer edit to those files: Check judges only the committed head, and autofix never runs on a report-only branch, which is what `dirty_code` covers;
    - add that entry's report to the Invoice's reports.

    The failure counts as a hard failure everywhere `host_hard` does in `check()`: its findings are folded into `passed` and into the returned hard findings, and they block `_review_seeds`. The rest of Check (`gather_evidence`, gates, host checks) still runs on the unchanged head, so Check ends `gate_failed`. There is no base-red rerun for autofix entries.
  - Every successful entry's passing report is also added to the Invoice's reports.
- In: `tests/test_host_mechanical.py`: autofix tests, plus `review.autofix` config loading.
- In: `docs/host-contract.md`:
  - Add an `AutofixCommand` row and Review's `autofix: []` default to the `config-fields` block.
  - Add an `autofix:` example under `review:` in the `host-example` block, with a comment saying the changed files are appended.
  - Add a paragraph to "Checks and injectable seams" stating the run order, the file list, the commit message and failure behavior.
- In: `docs/how-chupa-works.md`: section 4.3 gets autofix as the first Check step. The section 11 `review` row names `autofix`.
- Out: chupa's own `config.yaml`; running autofix at merge or in the `serve` merge queue; base-red handling for autofix; any spec under `specs/`; review-surface handling; detecting tool config files in the host.

## Scope fence
- chupa/config.py
- chupa/stages.py
- tests/test_host_mechanical.py
- docs/host-contract.md
- docs/how-chupa-works.md

## Acceptance criteria
1. An autofix entry receives the branch's existing changed files appended to its argv. Given a branch that modifies `a.py`, deletes `b.py`, and has a file under `tickets/`, the argv ends with exactly `a.py`. A test fails if `b.py` or a `tickets/` path is appended, or the entry runs with no files. Checked by `uv run pytest tests/test_host_mechanical.py`.
2. When an entry rewrites a changed file, the ticket branch gains one commit with message `chupa(<stem>): autofix` containing that file. The Invoice's `produced_at_sha` equals the new branch head. A test fails if Check evaluates the pre-autofix head or the fix is left uncommitted. Checked by `uv run pytest tests/test_host_mechanical.py`.
3. When no entry changes a file, the branch head is unchanged after Check. A test fails if an empty autofix commit is created. Checked by `uv run pytest tests/test_host_mechanical.py`.
4. An entry exiting 1 ends Check `gate_failed` with a finding coded with that entry's `code`. Afterwards:
   - `git status --porcelain` in the worktree lists none of the listed files, including a changed file committed with mode 100755 that the failing entry rewrote (so a mode change counts as a failure);
   - a later autofix entry is not run;
   - no autofix commit exists;
   - in a seeding ticket (fence includes `tickets`), `_review_seeds` is not called.

   A test fails if Check passes, a partial fix is committed, or seed review runs. Checked by `uv run pytest tests/test_host_mechanical.py`.
5. With an uncommitted implementer edit to a changed file and an entry that rewrites nothing, no autofix commit is created, the edit stays uncommitted, and the branch head is unchanged. A test fails if the untouched edit is committed as `chupa(<stem>): autofix`. Checked by `uv run pytest tests/test_host_mechanical.py`.
6. With a slip outcome of `already_satisfied`, no autofix entry runs. Checked by `uv run pytest tests/test_host_mechanical.py`.
7. `review.autofix` loads from config. An entry with an unknown key, or with an empty `argv`, is refused. `docs/host-contract.md`'s field inventory and example stay in lockstep with `chupa/config.py`. Checked by `uv run pytest tests/test_host_mechanical.py tests/test_host_contract.py`.
8. `docs/how-chupa-works.md` section 4.3 lists autofix as Check's first step.
9. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_host_mechanical.py tests/test_host_contract.py
uv run pytest -q
```

## Definition of rejected
The engine names or presets a specific tool; autofix commits files outside the branch's own changed files; autofix runs on the main checkout or at merge; a failing autofix leaves modified files in the worktree; chupa's own `config.yaml` changes.

## Time budget
- expected: 60m
- stuck: 150m
