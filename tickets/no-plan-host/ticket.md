---
priority: P1
kind: bug
source: human
state: confirmed
---

## Depends on
none

## Context
- docs/how-chupa-works.md
- tickets/no-plan-host/evidence/unguarded-plan-reads.txt
- chupa/tickets.py
- chupa/author.py
- chupa/rework.py
- chupa/daemon.py
- chupa/runner.py
- chupa/requisition.py
- tests/test_author.py
- tests/test_reject_queue.py

## On-demand
- chupa/stages.py

## Goal / Why
`CHUPA_PLAN.md` exists only in chupa's own repo, but six runtime paths read it with a bare `read_text()` and no existence check (listed in the evidence file). On a host repo without it, the Author stage (`author.py`), Rework (`rework.py`, `daemon.apply_rework`), and dead-dependency handling after a kill (`runner._dead_dependents`) raise `FileNotFoundError`. `parse_ticket` and `validate_ticket` already treat an absent plan as `plan=None`; these paths must do the same.

## Scope in / Scope out
- In: one function in `chupa/tickets.py` beside `PLAN_FILE` that returns the plan text under a given root, or `None` when the file is absent. Every runtime read of the plan in `chupa/` goes through it: `author.py`, `rework.py`, `daemon.py`, `runner.py` (`_dead_dependents` and `hardening_text`), and `stages.py` (seed review).
- In: `requisition.review_ticket` accepts `plan=None`; with no plan, the ticket has no plan units to resolve or harden, and review proceeds on the ticket and its Context alone. That covers both uses inside it, `hardenable_units` and `_base_render`; existing callers passing `plan=""` keep working.
- In: `tests/test_no_plan_host.py` adds, each in a temp repo with no `CHUPA_PLAN.md`: `test_author_without_plan` (Author writes and reviews a ticket from a Box message with a scripted model), `test_rework_without_plan` (a Rework `update` proposal is validated and reviewed), and `test_kill_without_plan_files_dead_dependency` (`reject` of a stem with a confirmed dependent files its dead-dependency report).
- In: `tests/regress_no_plan_host.py`, the carried reproducer: in a temp repo with no `CHUPA_PLAN.md` it runs the dead-dependency path of `reject`; it prints `{"regression_result": "pass"}` and exits 0 when that completes, prints `{"regression_result": "defect"}` and exits 1 on a `FileNotFoundError` naming `CHUPA_PLAN.md`, and prints `{"regression_result": "error"}` and exits 2 on any other failure. Diagnostics go to stderr only.
- In: update `docs/how-chupa-works.md` section 13 (plan reads go through one function and tolerate an absent plan), so the doc matches the code when this merges.
- In: the already-guarded plan reads in `chupa/drain.py` and `chupa/__main__.py` also go through the one function, so no `read_text()` of the plan remains elsewhere in `chupa/`.
- In: if `uv run pytest -q` fails only on tests that also fail on the merge base, those failures are pre-existing: Check excuses them (base-red). Commit the work and list them in the run record; never stop with `premise_failed` for them.
- Out: removing the bootstrap plan machinery, plan lint, `## Plan contract` grammar, and every behavior when the plan file exists.

## Scope fence
- docs/how-chupa-works.md
- chupa/tickets.py
- chupa/author.py
- chupa/rework.py
- chupa/daemon.py
- chupa/runner.py
- chupa/stages.py
- chupa/requisition.py
- tests/test_no_plan_host.py
- tests/regress_no_plan_host.py
- chupa/drain.py
- chupa/__main__.py

## Acceptance criteria
1. `uv run python tests/regress_no_plan_host.py` prints exactly `{"regression_result": "pass"}` and exits 0.
2. `uv run pytest -q tests/test_no_plan_host.py` exits 0 with `test_author_without_plan`, `test_rework_without_plan`, and `test_kill_without_plan_files_dead_dependency`.
3. `chupa/` contains no `read_text()` of the plan file outside the one function in `chupa/tickets.py`.
4. `uv run pytest -q` exits 0.
5. `docs/how-chupa-works.md` section 13 says plan reads go through one function and an absent plan is tolerated.

## Verification
```
uv run python tests/regress_no_plan_host.py
uv run pytest -q tests/test_no_plan_host.py
uv run pytest -q
```

## Regression
```
uv run python tests/regress_no_plan_host.py
```
- carries: tests/regress_no_plan_host.py

## Definition of rejected
Reject the branch if any path in `chupa/` can still raise because `CHUPA_PLAN.md` is absent, if behavior changes when the plan exists, or if the reproducer prints anything besides the result object on stdout.

## Time budget
- expected: 45m
- stuck: 90m
