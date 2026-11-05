---
priority: P2
kind: chore
source: human
state: confirmed
---

## Depends on
- remove-bootstrap-ingest

## Context
- docs/how-chupa-works.md

## On-demand
- chupa/__main__.py
- chupa/artifacts.py
- chupa/audit.py
- chupa/author.py
- chupa/baseline.py
- chupa/box.py
- chupa/caps.py
- chupa/checkpoint.py
- chupa/config.py
- chupa/control.py
- chupa/daemon.py
- chupa/doctor.py
- chupa/drain.py
- chupa/driver.py
- chupa/effects.py
- chupa/enginelog.py
- chupa/flake.py
- chupa/gates.py
- chupa/git.py

## Goal / Why
Module docstrings, comments, and a few operator messages in these files cite the bootstrap plan: `(CHUPA_PLAN.md section 6)`, `(section 11.2)`, plan unit ids such as `19.P3.daemon-scheduler` or `19.L`, design-decision ids such as `(D1)`, and bootstrap `Phase <n>` names. The plan is frozen history, so these citations send readers to a document that no longer describes the code. After this change, part 1 of 3, none of these files cites the plan.

## Scope in / Scope out
- In: in every fenced code file, delete each plan citation: `CHUPA_PLAN.md`, `plan section N`, `section N` / `Section N` / `section N.k` / `sections N, M` when it means a plan section, plan unit ids (`19.L`, `19.I`, `19.P<n>`, `19.P<n>.<stem>`), design-decision ids (`D<n>`), and bootstrap phase names (`Phase <n>`). Keep the sentence's own meaning; reword it if removing the citation leaves it broken; delete a docstring line or comment whose only content was the citation.
- In: operator-facing messages and paved roads in these files drop their plan citations the same way (for example `(section 6 provider preflight)` becomes `(provider preflight)`).
- In: a pointer may name `docs/how-chupa-works.md` where that doc describes the behavior, but never by section number.
- Out: behavior, names, identifiers, string values written to the journal or to artifacts, files outside the fence, `tests/` except as listed, `CHUPA_PLAN.md`.

## Scope fence
- chupa/__main__.py
- chupa/artifacts.py
- chupa/audit.py
- chupa/author.py
- chupa/baseline.py
- chupa/box.py
- chupa/caps.py
- chupa/checkpoint.py
- chupa/config.py
- chupa/control.py
- chupa/daemon.py
- chupa/doctor.py
- chupa/drain.py
- chupa/driver.py
- chupa/effects.py
- chupa/enginelog.py
- chupa/flake.py
- chupa/gates.py
- chupa/git.py

## Acceptance criteria
1. `grep -n -E "CHUPA_PLAN|[Ss]ections? [0-9]|\b19\.(L|I|P[0-9])|\bD[0-9]+\b|\bPhase [0-9]|\bplan 19\." chupa/__main__.py chupa/artifacts.py chupa/audit.py chupa/author.py chupa/baseline.py chupa/box.py chupa/caps.py chupa/checkpoint.py chupa/config.py chupa/control.py chupa/daemon.py chupa/doctor.py chupa/drain.py chupa/driver.py chupa/effects.py chupa/enginelog.py chupa/flake.py chupa/gates.py chupa/git.py` prints nothing (it prints a line for any citation left).
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
