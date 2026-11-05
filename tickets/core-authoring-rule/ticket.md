---
state: confirmed
source: human
priority: P1
kind: chore
---

## Depends on
- ticket-review-command

## Context
- chupa/hostfiles.py
- tests/test_hostfiles.py
- tickets/core-host-neutral/ticket.md

## On-demand
- CLAUDE.md
- AGENTS.md
- hosts/fixture/CLAUDE.md

## Goal / Why
Hosts get engine process rules only through `chupa core`, which writes `CORE_TEMPLATE` into their `CLAUDE.md`/`AGENTS.md`. Nothing there tells an agent how to write a ticket, so chat-session AIs write fences that miss forced files: on 2026-11-05 four tickets failed `premise_failed` on fence gaps and five more carried the same defect. `ticket-review-command` added `chupa review <stem>`, which runs the buildability review. After this change the managed block carries a seventh rule telling every host's agents to run that review and repair its findings before handing a ticket over, and chupa's own conduct files carry the re-rendered block.

## Scope in / Scope out
- In: `chupa/hostfiles.py` `CORE_TEMPLATE` keeps its heading, opening paragraph, and six existing rules byte-identical and appends exactly this seventh rule as the last line before the closing `"""`:
  - `- After writing or editing a ticket whose dependencies have merged, run chupa review <stem> and repair every finding until it approves; fence every file the change forces, including callers, importers, and tests that pin a changed name, value, or version. Why: a forced file outside the fence makes the ticket impossible.`
- In: re-render the managed block in `CLAUDE.md`, `AGENTS.md`, and `hosts/fixture/CLAUDE.md` with `hostfiles.render`, leaving every byte outside the block unchanged.
- In: `tests/test_hostfiles.py`: `test_core_template_is_host_neutral` expects exactly seven `- ` rules instead of six; regenerate `GOLDEN` with the file's own `__main__` helper.
- Out: marker grammar, `render`/`parse`/`classify_core`/`refresh` logic, the `core_drift` gate, every byte of `CLAUDE.md`/`AGENTS.md`/`hosts/fixture/CLAUDE.md` outside the managed block, `docs/` (no doc lists the block's rules).

## Scope fence
- chupa/hostfiles.py
- CLAUDE.md
- AGENTS.md
- hosts/fixture/CLAUDE.md
- tests/test_hostfiles.py

## Acceptance criteria
1. `CORE_TEMPLATE` has exactly seven `- ` rules and none of the host-neutral banned terms, checked by `uv run pytest tests/test_hostfiles.py -k host_neutral` (fails at six rules or with the rule text naming `journal`).
2. `classify_core` on the committed `CLAUDE.md`, `AGENTS.md`, and `hosts/fixture/CLAUDE.md` returns `current`, not `drifted`, checked by `uv run pytest -q` (the `core_drift` gate, `test_core_activation_first_adoption`, and the fixture-host tests).
3. `git diff main -- CLAUDE.md AGENTS.md hosts/fixture/CLAUDE.md` shows changes only between the `chupa:core` marker lines.
4. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_hostfiles.py -k host_neutral
uv run pytest -q
```

## Definition of rejected
Any of the six existing rules changes; the new rule's text differs from the line given; a byte outside a managed block changes; marker or gate logic changes.

## Time budget
- expected: 20m
- stuck: 60m
