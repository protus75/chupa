---
priority: P1
kind: chore
source: human
state: confirmed
---

## Depends on
- remove-plan-text-tests

## Context
- chupa/driver.py
- docs/how-chupa-works.md

## On-demand
- chupa/drain.py
- chupa/stages.py
- chupa/tickets.py
- tests/test_drain.py
- tests/test_stages.py
- tests/test_driver.py
- tests/test_tickets.py
- tests/test_closed_sets.py

## Goal / Why
Two pieces exist only for the bootstrap's phase-exit tickets: the drain forces a retro before any stem named `phase<N>-exit`, and the `## Exit-read window` ticket section freezes journal events into `.chupa/exit-read-window.json` for the implementer. The phases are finished, no ticket file uses `## Exit-read window`, and a stem's name should never change how it is scheduled. The five `tests/test_phase*_exit.py` files check the bootstrap plan's phase registries. After this change a stem named `phase5-exit` is an ordinary ticket and `## Exit-read window` is an unknown section.

## Scope in / Scope out
- In: `chupa/drain.py`: delete the forced retro before a `phase[0-8]-exit` pick, and the `re` import if unused.
- In: `chupa/tickets.py`: drop `Exit-read window` from `OPTIONAL_SECTIONS` and delete its parsing.
- In: `chupa/stages.py`: delete `resolve_exit_window`, the exit-window note in `implement_stage`, and the window resolve/materialize in `implement`. `chupa/driver.py`: delete `materialize_exit_window`.
- In: delete `tests/test_phase2_exit.py`, `tests/test_phase3_exit.py`, `tests/test_phase4_exit.py`, `tests/test_phase5_exit.py`, `tests/test_phase6_exit.py`.
- In: `tests/test_drain.py` `test_drain_retro_due_quiescence_and_pre_exit`: delete the `pre-exit` scenario and the `phase5-exit` branch in `drive`; rewrite `selected-failure` without phase-exit stems so it still proves a failed retro is journaled `retro_failed` once per attempt and the drain still reaches quiescence.
- In: delete `test_exit_window_is_materialized_before_the_real_implement_call` (`tests/test_stages.py`) and `test_exit_read_window_materialization` (`tests/test_driver.py`).
- In: `tests/test_tickets.py` `test_grammar_refusals`: the `## Exit-read window` case now expects the unknown-section refusal. `tests/test_closed_sets.py`: update `OPTIONAL_SECTIONS` and `SECTIONS`.
- In: add `test_phase_exit_stem_gets_no_forced_retro` to `tests/test_drain.py`: with a retro route configured, a drain that dispatches a stem named `phase5-exit` runs no retro before it (it fails if the name still triggers one).
- In: `docs/how-chupa-works.md` section 13: delete the forced-retro part of the phase-exits bullet; keep a line listing the eval report artifacts.
- Out: the retro's own triggers (25 merges, 7 days, failure spike, quiescence), the eval benches and `KNOWN_ARTIFACTS`, `## Plan contract`, `CHUPA_PLAN.md`.

## Scope fence
- chupa/drain.py
- chupa/tickets.py
- chupa/stages.py
- chupa/driver.py
- tests/test_phase2_exit.py
- tests/test_phase3_exit.py
- tests/test_phase4_exit.py
- tests/test_phase5_exit.py
- tests/test_phase6_exit.py
- tests/test_drain.py
- tests/test_stages.py
- tests/test_driver.py
- tests/test_tickets.py
- tests/test_closed_sets.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `grep -rn -E "Exit-read window|exit_window|exit-read-window|phase\[0-8\]-exit" chupa` prints nothing.
2. A `phase5-exit` stem gets no retro before its dispatch (the test fails if its name still forces one), checked by `uv run pytest tests/test_drain.py -k "phase_exit_stem_gets_no_forced_retro or retro_due_quiescence"`.
3. No `tests/test_phase*_exit.py` file exists.
4. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_drain.py -k "phase_exit_stem_gets_no_forced_retro or retro_due_quiescence"
uv run pytest -q
```

## Definition of rejected
Any other retro trigger changes; eval benches or registered report artifacts change; `## Plan contract` handling changes.

## Time budget
- expected: 45m
- stuck: 90m
