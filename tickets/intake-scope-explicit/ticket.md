---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- none

## Context
- chupa/tickets.py::intake
- chupa/tickets.py::_pending
- chupa/__main__.py::_review
- chupa/__main__.py::_verdict
- chupa/runner.py::verdict_locked
- chupa/runner.py::_admit
- chupa/runner.py::apply_admission
- docs/how-chupa-works.md#3.2 Intake
- tests/unit/test_git_commit.py
- tests/unit/test_verdict_extension.py

## On-demand
- chupa/drain.py
- chupa/serve.py
- tests/integration/test_tickets.py
- tests/integration/test_review_command.py
- tests/integration/test_cli.py
- tests/integration/test_reject_queue.py
- tests/integration/test_drain.py
- tests/integration/test_provider_cooldown_failover.py
- tests/harness/reliability_battery.py
- chupa/docs/host-running.md

## Goal / Why
`intake` in `chupa/tickets.py` sweeps every pending `tickets/*/ticket.md` unless its caller narrows it, and nothing makes a caller decide. Verbs that name one stem inherited the sweep by calling it the way `drain` does: `review <stem>` (ticket `review-intakes-own-stem`), `run <stem>` (`runner._admit`), and `confirm`/`reject <stem>` (`runner.verdict_locked`, which the engine's `apply_admission` also calls, and the engine-handoff path in `chupa/__main__.py::_verdict`). Each one commits and auto-confirms other authors' half-written drafts that happen to lint clean, so those drafts become drainable without review. Ticket `review-intakes-own-stem` fixes `review` only; the next per-stem verb written the same way would bring the bug back.

When this ticket is done, `intake`'s scope is a required choice at every call site, every verb that names a stem intakes only that stem, and one test pins that rule for every such verb.

## Scope in / Scope out
- In: `chupa/tickets.py::intake` takes a keyword-only `stems: Collection[str] | None` with NO default. A collection limits the commit loop to those pending stems; other pending stems are not validated, stamped, written, committed, journaled, or reported in `refused`. `None` processes every pending stem. The status read, evidence listing, and stray-staged-path check stay over every pending stem. If ticket `review-intakes-own-stem` has merged, this removes the `= None` default it added; if not, this adds the parameter.
- In: per-stem callers pass `stems={stem}`: `chupa/__main__.py::_review`, `chupa/__main__.py::_verdict` (engine-handoff path), `chupa/runner.py::verdict_locked`, `chupa/runner.py::_admit`.
- In: sweeping callers pass `stems=None` explicitly: both calls in `chupa/drain.py` and the call in `chupa/serve.py`.
- In: every test and harness call of `intake` passes `stems` explicitly: `tests/unit/test_git_commit.py`, `tests/integration/test_tickets.py` (`do_intake` and the direct call), `tests/integration/test_drain.py`, `tests/integration/test_provider_cooldown_failover.py`, `tests/harness/reliability_battery.py`.
- In: `docs/how-chupa-works.md`: section 2.1 rows for `run <stem>`, `confirm`, and `reject` say they intake only the named ticket's pending changes; section 3.2's first line says `drain` and `serve` intake every pending ticket while `review`, `run`, `confirm`, and `reject` intake only the named stem.
- In: `chupa/docs/host-running.md` rows for `run`, `confirm`, and `reject` say other pending tickets are left untouched.
- Out:
  - Intake's auto-confirm of new hand-written stems, and the lint rules.
  - What `drain` and `serve` intake.
  - `chupa/observe.py` and `vscode-chupa/`.

## Scope fence
- chupa/tickets.py
- chupa/__main__.py
- chupa/runner.py
- chupa/drain.py
- chupa/serve.py
- docs/how-chupa-works.md
- chupa/docs/host-running.md
- tests/unit/test_git_commit.py
- tests/unit/test_verdict_extension.py
- tests/unit/test_intake_scope.py
- tests/integration/test_intake_scope.py
- tests/integration/test_tickets.py
- tests/integration/test_review_command.py
- tests/integration/test_cli.py
- tests/integration/test_reject_queue.py
- tests/integration/test_drain.py
- tests/integration/test_provider_cooldown_failover.py
- tests/harness/reliability_battery.py

## Acceptance criteria
1. New `tests/unit/test_intake_scope.py` asserts `inspect.signature(tickets.intake).parameters["stems"]` is keyword-only and its default is `inspect.Parameter.empty`, not `None`.
2. A test in `tests/unit/test_git_commit.py` uses a fake git like `test_intake_skips_concurrent_commit`'s, but its `status_porcelain` returns `?? tickets/one/ticket.md` and `?? tickets/two/ticket.md`, its `_commit` returns a sha, and its fake journal accepts `append`. It calls `tickets.intake(..., stems={"one"})` and asserts the fake `_commit` is called exactly once, with `("chupa(one): ticket", ["tickets/one/ticket.md"])`, and that `result.committed == ("one",)`, not `("one", "two")`. (If ticket `review-intakes-own-stem` already added this test, it is updated to the required keyword instead.)
3. A test in `tests/integration/test_intake_scope.py` stages `tickets/beta/ticket.md` with `git add`, with a body that fails lint, and leaves `tickets/alpha/ticket.md` pending and lint clean. `intake(..., stems={"alpha"})` raises no `IntakeRefused` and commits only alpha. Beta stays staged and uncommitted (`git diff --cached --name-only` still lists it), and `"beta"` is not in `result.refused`.
4. New `tests/integration/test_intake_scope.py` has one test parametrized over `review`, `run`, `confirm --yes`, and `reject --yes`, each against stem `alpha`, with no engine running. Before each, `tickets/alpha/ticket.md` and `tickets/beta/ticket.md` are both pending, lint clean, `state: draft`; model and stage seams are faked as `tests/integration/test_review_command.py` and `tests/integration/test_cli.py` fake them. After each verb: `git log` subjects contain no `chupa(beta): ticket`; `tickets/beta/ticket.md` bytes equal what the test wrote; `git status --porcelain -- tickets/beta/` is non-empty; no journal `ticket_intake` signal has `ticket == "beta"`. At base, the `run`, `confirm`, and `reject` cases fail on `chupa(beta): ticket`.
5. `tests/unit/test_verdict_extension.py`'s engine-handoff test asserts the mocked `intake` was awaited with `stems={"sample"}`, not without `stems`.
6. A test in `tests/integration/test_tickets.py` calls `intake(..., stems=None)` with two pending stems and asserts both are committed, so the sweep still works for `drain` and `serve`.
7. `docs/how-chupa-works.md` section 3.2's first line names `review`, `run`, `confirm`, and `reject` as intaking only the named stem, and `drain` and `serve` as intaking every pending ticket.
8. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
- `intake`'s `stems` parameter has a default value, or any call site omits it.
- `review`, `run`, `confirm`, or `reject` commits, stamps, rewrites, or journals a pending ticket other than the named stem.
- `drain` or `serve` stops committing every lint-clean pending ticket.
- Intake's auto-confirm of new hand-written stems changes.

## Time budget
- expected: 60m
- stuck: 120m
