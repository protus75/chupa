---
state: confirmed
source: human
priority: P0
kind: bug
---

## Depends on
- none

## Context
- chupa/tickets.py::template
- chupa/tickets.py::_intake_claims
- chupa/runner.py::_dead_dependents
- tests/integration/test_cli.py::test_new_templates_a_ticket_and_lints_it
- tests/integration/test_tickets.py::test_template_per_kind
- docs/how-chupa-works.md#3.2 Intake
- tests/regress_drain_deadline.py

## Goal / Why
`chupa new` writes its unfilled skeleton with `state: confirmed` (`chupa/tickets.py::template`). An unfinished, invalid ticket therefore claims to be confirmed, runnable work from the moment it lands on disk. Every scanner that trusts the `state` line treats a half-written ticket in the shared checkout as queued work. On 2026-11-11 that crashed `chupa reject` (evidence: `tickets/new-skeleton-draft-state/evidence/reject-crash.txt`): another session's skeleton passed `_dead_dependents`' `state: confirmed` filter and `parse_ticket` raised on it. The sibling ticket `reject-survives-invalid-ticket` fixes that one scanner. This ticket removes the cause: a skeleton is not confirmed until intake says so.

After this change the skeleton carries `state: draft`. Nothing else changes for the author. Intake already accepts a new hand-written stem in `draft` and stamps it `state: confirmed` when it commits it (`_intake_claims`), and `run`, `review`, `drain`, and `serve` all run intake first. Until intake commits it, scanners that filter on `state: confirmed` skip the skeleton.

## Scope in / Scope out
- In: `chupa/tickets.py::template`: the frontmatter line `state: confirmed` becomes `state: draft`. No other template change.
- In: `tests/integration/test_cli.py::test_new_templates_a_ticket_and_lints_it`: assert the authored text contains `state: draft` and not `state: confirmed`.
- In: `tests/integration/test_tickets.py`: add `test_new_skeleton_is_draft_until_intake`. It runs `chupa new aaa-wip` through `chupa.__main__.main` in the `repo` fixture (as `test_new_bug_copies_evidence` does), and asserts the written file's frontmatter `state` is `draft`. It then fills the placeholders the way `test_template_per_kind` does, runs `do_intake`, and asserts the committed `tickets/aaa-wip/ticket.md` at `HEAD` carries `state: confirmed`. The first assertion fails at base whatever else has merged; the second rules out a skeleton that intake can no longer confirm.
- In: `tests/regress_new_skeleton_draft.py` (new), the carried reproducer shaped like `tests/regress_drain_deadline.py`: it runs `pytest.main(["tests/integration/test_tickets.py", "-k", "skeleton_is_draft_until_intake", "-q", "-p", "no:cacheprovider"])` inside `contextlib.redirect_stdout(sys.stderr)` and prints exactly one JSON object: `pass` and exit 0 for pytest exit 0, `defect` and exit 1 for pytest exit 1, `error` and exit 2 otherwise.
- In: `docs/how-chupa-works.md`: in the `new` row of the command table (the one that begins ``| `new <stem> --kind``), add that the skeleton is written as `state: draft` and intake confirms it.
- Out: `chupa/runner.py` (the sibling ticket owns `_dead_dependents`), intake's claims, the `confirm` verb, other scanners, and every other template line.

## Scope fence
- chupa/tickets.py
- tests/integration/test_cli.py
- tests/integration/test_tickets.py
- tests/regress_new_skeleton_draft.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `uv run python tests/regress_new_skeleton_draft.py` prints `{"regression_result": "pass"}` and exits 0 on the branch head. On the base commit with the carried files overlaid it prints `defect`, because the skeleton's `state` is `confirmed`, not `draft`.
2. `./dev.py test tests/integration/test_cli.py` passes `test_new_templates_a_ticket_and_lints_it`, which asserts the skeleton text contains `state: draft`, not `state: confirmed`.
3. `./dev.py test tests/integration/test_tickets.py` passes `test_new_skeleton_is_draft_until_intake`, which asserts intake commits the filled skeleton as `state: confirmed`, not left `draft`, and passes `test_template_per_kind` unchanged, so a filled skeleton still validates.
4. `docs/how-chupa-works.md` states in the `new` command row that the skeleton is written as `state: draft`.
5. `./dev.py test` exits 0.

## Verification
```
uv run python tests/regress_new_skeleton_draft.py
./dev.py test tests/integration/test_cli.py tests/integration/test_tickets.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- `chupa/runner.py` or intake's claim rules change;
- the skeleton omits the `state` line or uses any value other than `draft`;
- any other template line changes;
- the reproducer prints `pass` on the merge base.

## Time budget
- expected: 20m
- stuck: 45m

## Regression
```
uv run python tests/regress_new_skeleton_draft.py
```
- carries: tests/regress_new_skeleton_draft.py
- carries: tests/integration/test_tickets.py
