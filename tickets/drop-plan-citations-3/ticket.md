---
priority: P2
kind: chore
source: human
state: confirmed
---

## Depends on
- drop-plan-citations-2

## Context
- docs/how-chupa-works.md

## On-demand
- chupa/runner.py
- chupa/scheduler.py
- chupa/scorecard.py
- chupa/seams.py
- chupa/serve.py
- chupa/specs.py
- chupa/stages.py
- chupa/status.py
- chupa/storm.py
- chupa/thresh.py
- chupa/tickets.py
- chupa/timers.py
- chupa/triage.py
- chupa/watchdog.py
- chupa/watcher.py
- eval/daemon_soak.py
- eval/harness.py
- eval/host_loop.py
- eval/reliability_battery.py
- eval/shakeout/bench.py

## Goal / Why
Module docstrings, comments, and a few operator messages in these files cite the bootstrap plan: `(CHUPA_PLAN.md section 6)`, `(section 11.2)`, plan unit ids such as `19.P3.daemon-scheduler` or `19.L`, design-decision ids such as `(D1)`, and bootstrap `Phase <n>` names. The plan is frozen history, so these citations send readers to a document that no longer describes the code. After this change, part 3 of 3, none of these files cites the plan.

## Scope in / Scope out
- In: in every fenced code file, delete each plan citation: `CHUPA_PLAN.md`, `plan section N`, `section N` / `Section N` / `section N.k` / `sections N, M` when it means a plan section, plan unit ids (`19.L`, `19.I`, `19.P<n>`, `19.P<n>.<stem>`), design-decision ids (`D<n>`), and bootstrap phase names (`Phase <n>`). Keep the sentence's own meaning; reword it if removing the citation leaves it broken; delete a docstring line or comment whose only content was the citation.
- In: operator-facing messages and paved roads in these files drop their plan citations the same way (for example `(section 6 provider preflight)` becomes `(provider preflight)`).
- In: a pointer may name `docs/how-chupa-works.md` where that doc describes the behavior, but never by section number.
- In: `docs/how-chupa-works.md`: section 13 drops its opening sentence about building from the plan; if only the eval report artifacts line remains, retitle the section "Eval report artifacts".
- Out: behavior, names, identifiers, string values written to the journal or to artifacts, files outside the fence, `tests/` except as listed, `CHUPA_PLAN.md`.

## Scope fence
- chupa/runner.py
- chupa/scheduler.py
- chupa/scorecard.py
- chupa/seams.py
- chupa/serve.py
- chupa/specs.py
- chupa/stages.py
- chupa/status.py
- chupa/storm.py
- chupa/thresh.py
- chupa/tickets.py
- chupa/timers.py
- chupa/triage.py
- chupa/watchdog.py
- chupa/watcher.py
- eval/daemon_soak.py
- eval/harness.py
- eval/host_loop.py
- eval/reliability_battery.py
- eval/shakeout/bench.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `grep -n -E "CHUPA_PLAN|[Ss]ections? [0-9]|\b19\.(L|I|P[0-9])|\bD[0-9]+\b|\bPhase [0-9]|\bplan 19\." chupa/runner.py chupa/scheduler.py chupa/scorecard.py chupa/seams.py chupa/serve.py chupa/specs.py chupa/stages.py chupa/status.py chupa/storm.py chupa/thresh.py chupa/tickets.py chupa/timers.py chupa/triage.py chupa/watchdog.py chupa/watcher.py eval/daemon_soak.py eval/harness.py eval/host_loop.py eval/reliability_battery.py eval/shakeout/bench.py` prints nothing (it prints a line for any citation left).
2. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q
```

## Definition of rejected
Any behavior, identifier, journal value, or artifact value changes; any file outside the fence changes.

## Time budget
- expected: 30m
- stuck: 60m
