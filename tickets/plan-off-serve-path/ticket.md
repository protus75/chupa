---
priority: P1
kind: chore
source: human
state: confirmed
---

## Depends on
- remove-plan-gap-hardening
- remove-seeding

## Context
- chupa/watcher.py
- docs/how-chupa-works.md

## On-demand
- chupa/tickets.py
- chupa/drain.py
- chupa/serve.py
- chupa/daemon.py
- chupa/__main__.py
- chupa/runner.py
- eval/reliability_battery.py
- eval/daemon_soak.py
- tests/test_serve.py
- tests/test_daemon_composition.py
- tests/test_scheduler.py

## Goal / Why
`drain`, `serve`, the watcher, and Rework read `CHUPA_PLAN.md` and pass its text into every ticket parse, and they re-parse every ticket file on disk, finished ones included. 257 finished tickets carry a `## Plan contract`, so the next ticket (removing that section from the format) would otherwise make every drain report them invalid and every `serve` start journal 257 parse failures. After this change no runtime path reads the plan, and the drain scan and the watcher skip tickets that are finished (last journal state `merged`, `already_satisfied`, or `rejected`), the same rule `lint` already uses.

## Scope in / Scope out
- In: `chupa/tickets.py`: `parse_ticket`'s `plan` becomes keyword-only with default `None` (the next ticket deletes it); `validate_ticket` keeps passing `read_plan(repo)` for now. When `plan` is `None`, `## Plan contract` items are still parsed as bullets of plan ids, but they are not resolved against a plan: no `PlanContractError` and no "plan is absent" finding. When a plan is passed, resolution is unchanged, so `lint` and `validate_ticket` still verify citations. This bridge lasts until `remove-plan-grammar` deletes the section.
- In: `chupa/drain.py` `_scan`: skip a stem whose last journal state is in `SETTLED | {"rejected"}` before parsing it; stop reading the plan and stop passing `plan`; `_offer_material` stops including the plan file. Drop the `read_plan`/`PLAN_FILE` imports if unused.
- In: `chupa/watcher.py`: delete the `plan` parameter; a change for a stem whose last journal state is in `SETTLED | {"rejected"}` is dropped (removed from the cache and scheduler, never parsed, no `watcher_parse_failure`).
- In: delete the `plan` parameter from `serve.Serve`, `serve.serve`, `daemon.daemon_core`, `__main__.build_daemon_core`, and `__main__.build_serve`, and stop calling `read_plan` in `__main__`; `serve.py`'s re-parse and `daemon.apply_rework`'s parse stop passing `plan`; `runner._dead_dependents` stops passing `plan`.
- In: `eval/reliability_battery.py`, `eval/daemon_soak.py`: stop passing `plan` and stop writing a `CHUPA_PLAN.md` into their temp hosts.
- In: tests that pass `plan=` into these builders or into `parse_ticket` drop the argument and any now-unused `PLAN` constant: `tests/test_serve.py`, `tests/test_daemon_composition.py`, `tests/test_scheduler.py`, `tests/test_daemon_admission.py`, `tests/test_restart_timers.py`, `tests/test_daemon_soak.py`, `tests/test_provider_cooldown_failover.py`, `tests/test_storm_notification_activation.py`.
- In: add `test_drain_scan_skips_finished_tickets` to `tests/test_drain.py`: a merged stem and a rejected stem whose `ticket.md` no longer parses are absent from the drain report's invalid list, while an unsettled unparseable ticket is still listed (it fails if finished tickets are parsed, or if live ones are skipped).
- In: add `test_watcher_skips_finished_tickets` to `tests/test_scheduler.py`: a change for a merged stem with an unparseable `ticket.md` journals no `watcher_parse_failure` and publishes nothing, while the same change for an unsettled stem still journals one.
- In: `docs/how-chupa-works.md` sections 7.1 and 7.2: the drain scan and the watcher skip finished tickets.
- Out: the `## Plan contract` section syntax and its resolution when a plan is passed, `chupa/specs.py`, fence anchors, the watchdog, `validate_ticket`, `lint`, `CHUPA_PLAN.md`.

## Scope fence
- chupa/tickets.py
- chupa/drain.py
- chupa/watcher.py
- chupa/serve.py
- chupa/daemon.py
- chupa/__main__.py
- chupa/runner.py
- eval/reliability_battery.py
- eval/daemon_soak.py
- tests
- docs/how-chupa-works.md

## Acceptance criteria
1. `grep -n -E "read_plan|plan=|PLAN_FILE" chupa/drain.py chupa/watcher.py chupa/serve.py chupa/daemon.py chupa/__main__.py chupa/runner.py eval/reliability_battery.py eval/daemon_soak.py` prints nothing.
2. Finished tickets are skipped and live ones are not, by both the drain scan and the watcher, checked by `uv run pytest tests/test_drain.py tests/test_scheduler.py -k "skips_finished_tickets"`.
3. `docs/how-chupa-works.md` sections 7.1 and 7.2 state the skip.
4. `parse_ticket` on a ticket with a `## Plan contract` section and no plan returns the ticket with no finding, while the same text with a plan that lacks the cited id still raises the existing finding. Checked by `uv run pytest tests/test_tickets.py`.
5. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_drain.py tests/test_scheduler.py -k "skips_finished_tickets"
uv run pytest tests/test_tickets.py
uv run pytest -q
```

## Definition of rejected
An unsettled ticket is skipped; `lint` or `validate_ticket` behavior changes; `## Plan contract` resolution changes when a plan is passed.

## Time budget
- expected: 45m
- stuck: 90m
