---
state: confirmed
source: human
priority: P0
kind: bug
---

## Depends on
- none

## Runs before
- intake-scope-explicit

## Context
- chupa/__main__.py::_review
- chupa/tickets.py::intake
- chupa/tickets.py::_pending
- chupa/tickets.py::_intake_claims
- chupa/runner.py::ticket_pending
- docs/how-chupa-works.md#3.2 Intake
- tests/regress_requisition_prior_review.py

## On-demand
- tests/integration/test_review_command.py
- tests/unit/test_git_commit.py
- chupa/docs/host-running.md

## Goal / Why
`chupa review <stem>` commits and confirms every other pending ticket in `tickets/`, not just the one it was asked to review. `_review` in `chupa/__main__.py` checks that `tickets/<stem>/` has pending changes, then calls `intake(repo, git, journal, fs)`, which has no stem argument. `intake` in `chupa/tickets.py` commits every pending `tickets/*/ticket.md` that lints clean as `chupa(<other>): ticket`, and `_intake_claims` stamps each new one `state: confirmed`. A half-written draft that happens to pass lint is committed as confirmed and is drainable without ever being reviewed. The authoring guide's workflow (`new`, `lint`, `review` until approve) makes this the normal path: an author reviewing ticket A sweeps in ticket B mid-draft.

The documented contract is narrower: `docs/how-chupa-works.md` section 2.1 says review commits "Pending changes under the ticket directory", and `chupa/docs/host-running.md` says "Pending edits are committed through intake". Evidence: `evidence/review-sweeps-other-stems.txt` (temp host repo; `review alpha` with draft `beta` pending committed `chupa(beta): ticket` with `state: confirmed`).

When this ticket is done, `review <stem>` commits only `<stem>`'s pending ticket and evidence. Every other pending ticket stays on disk, uncommitted, byte-identical, with no `ticket_intake` journal event.

## Scope in / Scope out
- In: `chupa/tickets.py::intake` gains a keyword-only parameter `stems: Collection[str] | None = None`. When it is a collection, the commit loop processes only pending stems in it; other pending stems are neither validated, stamped, written, committed, journaled, nor reported in `IntakeResult.refused`. The status read, evidence listing, and stray-staged-path check stay as they are over every pending stem, so another stem's staged `ticket.md` is still not "stray" and still never rides along (commits are already pathspec-limited by `only=`). `None` keeps today's behavior for every other caller.
- In: `chupa/__main__.py::_review` passes `stems={stem}` to its `intake` call. No other caller changes.
- In: `docs/how-chupa-works.md`: the `review <stem>` row in section 2.1 says only that ticket's pending changes are committed through intake and other pending tickets are left untouched; section 3.2's first line adds `review`, noting it intakes only its own stem.
- In: `chupa/docs/host-running.md`: the `review` row says only the named ticket's pending edits are committed through intake.
- In: new carried reproducer `tests/regress_review_intakes_own_stem.py`, modeled on `tests/regress_requisition_prior_review.py` and importing nothing from `tests/`. It builds a temp git host repo with a config, commits it, writes two pending tickets `alpha` and `beta` (both `state: draft`, both lint clean), and runs `chupa.__main__.main(["review", "alpha"])` with `chupa.__main__.ProviderLLM` patched to a `FakeLLM` that approves, inside `contextlib.redirect_stdout(io.StringIO())`. Its only stdout is the `regression_result` JSON line:
  - `pass`, exit 0: review exited 0, `chupa(alpha): ticket` is in `git log`, `chupa(beta): ticket` is not, and `tickets/beta/ticket.md` on disk still reads `state: draft`.
  - `defect`, non-zero exit: `chupa(beta): ticket` is in `git log`.
  - `error`, non-zero exit: anything else (review did not exit 0, or `alpha` was not committed).
- Out:
  - Every other `intake` caller (`run`, `confirm`, `reject`, the engine-handoff verdict path in `chupa/__main__.py`, `drain`, `serve`). Ticket `intake-scope-explicit` owns making the scope explicit at every caller.
  - Intake's auto-confirm of new hand-written stems.
  - `chupa/observe.py` and `vscode-chupa/`.

## Scope fence
- chupa/tickets.py
- chupa/__main__.py
- docs/how-chupa-works.md
- chupa/docs/host-running.md
- tests/unit/test_git_commit.py
- tests/integration/test_review_command.py
- tests/regress_review_intakes_own_stem.py

## Acceptance criteria
1. A new test in `tests/unit/test_git_commit.py`, built like `test_intake_skips_concurrent_commit` (fake git whose `status_porcelain` returns `?? tickets/one/ticket.md` and `?? tickets/two/ticket.md`), calls `tickets.intake(..., stems={"one"})`. The fake `_commit` records exactly one call, `("chupa(one): ticket", ["tickets/one/ticket.md"])`, not two; `result.committed == ("one",)`; and `"two"` is not in `result.refused`.
2. The same file: `tickets.intake(...)` with no `stems` and the same two pending stems commits both, so the default still sweeps.
3. A new test in `tests/integration/test_review_command.py` writes pending tickets `alpha` and `beta`, runs `review alpha` with an approving `FakeLLM`, and asserts: exit 0; `git log` subjects contain `chupa(alpha): ticket` and not `chupa(beta): ticket`; `git status --porcelain -- tickets/beta/` is non-empty; `tickets/beta/ticket.md` bytes equal what the test wrote; no journal `ticket_intake` signal has `ticket == "beta"`.
4. `docs/how-chupa-works.md` section 2.1's `review <stem>` row says other pending tickets are left untouched, and section 3.2's first line names `review`.
5. `chupa/docs/host-running.md`'s `review` row says only the named ticket's pending edits are committed.
6. The Regression command prints `{"regression_result": "pass"}` and exits 0 on the branch, and prints `defect` with a non-zero exit at the merge base.
7. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
- `review alpha` commits, stamps, rewrites, or journals pending ticket `beta`.
- `run`, `confirm`, `reject`, `drain`, or `serve` intake behavior changes.
- The stray-staged-path check now refuses a staged `ticket.md` of a pending stem outside `stems`.
- Intake's auto-confirm of new hand-written stems changes.

## Time budget
- expected: 30m
- stuck: 75m

## Regression
```
uv run python tests/regress_review_intakes_own_stem.py
```
- carries: tests/regress_review_intakes_own_stem.py
