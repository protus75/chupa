---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
none

## Context
- chupa/hostfiles.py
- CLAUDE.md
- AGENTS.md
- docs/host-contract.md

## On-demand
- tests/test_hostfiles.py
- hosts/fixture/CLAUDE.md
- docs/how-chupa-works.md

## Goal / Why
`CORE_TEMPLATE` is the engine conduct block that `chupa core` writes into every host's CLAUDE.md/AGENTS.md, and the hard `core_drift` gate requires it. Today it is a compressed copy of chupa's own section A, so it includes rules for chupa's own codebase: pure Python with no shell scripts, all git through `git.py`, injectable seams, the journal, and so on. A host such as fungo, which uses bash scripts and has no `git.py`, must either take in rules that are wrong for it and rank above its own ("engine wins on process") or fail the gate. After this change the template carries only rules that hold for any host chupa runs work on. Chupa's own codebase rules live only in chupa's project-owned section A, which already states them, so chupa's agents lose nothing. Its earlier premise failure (the full suite was red on main because a test parsed a ticket naming a deleted file) was fixed on main by `da13b247`.

## Scope in / Scope out
- In: `chupa/hostfiles.py` `CORE_TEMPLATE` keeps its heading and opening paragraph unchanged and has exactly these six rules, in this order:
  - `- Build the simplest thing satisfying the ticket; no speculative features, gates, config knobs, or metadata. Every addition needs its earning incident. Why: accretion is the primary failure mode.`
  - `- Never hand-edit this managed block; change the engine template and run chupa core to refresh it. Why: the next render overwrites edits and exposes drift.`
  - `- Commit only on your own ticket branch. Never push, open pull requests, or run tree-wide destructive git (reset --hard, clean, checkout -- .); the engine merges reviewed work to local main. Why: local main is the blessed line.`
  - `- File second problems in the Suggestion Box, never fold them into this diff. Verify pre-existing failures on the base commit before filing. Why: folded fixes hide cause and expand scope.`
  - `- Read before write: read the owning artifact before writing a command, claim, or test. Why: guessed facts create costly bugs.`
  - `- Ticket frontmatter contains only fields read by scheduling, gates, or authoring/triage policy. Put ordering in depends and priority. Why: unused metadata and prose ordering drift.`
- In: the template text must not contain the string `chupa:core` (marker parsing counts every occurrence).
- In: re-render the managed block in `CLAUDE.md`, `AGENTS.md`, and `hosts/fixture/CLAUDE.md` with `hostfiles.render`, leaving every byte outside the block unchanged, except as below.
- In: `AGENTS.md` section A (outside the block) gains the **A hold ships with its release** bullet, copied verbatim from `CLAUDE.md` section A, because the block no longer carries that rule and AGENTS.md section A lacks it.
- In: `tests/test_hostfiles.py` gains `test_core_template_is_host_neutral`: `CORE_TEMPLATE` contains none of `git.py`, `Pure Python`, `seams`, `journal`, `shell=True`, `chupa:core`, and has exactly six lines starting with `- `. It fails on today's template (which names `git.py` and has 14 rules).
- In: `docs/host-contract.md` "Managed conduct and ticket ownership" adds one sentence: the block carries only process rules that hold for every host; codebase rules belong in the project-owned remainder. `docs/how-chupa-works.md` section 12 gets the same sentence.
- Out: marker grammar, `render`/`parse`/`classify_core`/`refresh`/`committed_core` logic, the `core_drift` gate and its severity, the remainder process-override lint, `CLAUDE.md`/`AGENTS.md` content outside the block other than the AGENTS.md bullet, `CHUPA_PLAN.md`.

## Scope fence
- chupa/hostfiles.py
- CLAUDE.md
- AGENTS.md
- hosts/fixture/CLAUDE.md
- tests/test_hostfiles.py
- docs/host-contract.md
- docs/how-chupa-works.md

## Acceptance criteria
1. `uv run pytest tests/test_hostfiles.py -k host_neutral` passes, and the same test fails if `CORE_TEMPLATE` still names `git.py` or has any number of `- ` rules other than six.
2. `classify_core` on the committed `CLAUDE.md`, `AGENTS.md`, and `hosts/fixture/CLAUDE.md` returns `current`, not `drifted`, checked by `uv run pytest -q` (the `core_drift` gate and the fixture-host tests).
3. `git diff main -- CLAUDE.md` shows changes only between the `chupa:core` marker lines; `git diff main -- AGENTS.md` shows changes only between the markers plus the one added section A bullet.
4. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_hostfiles.py -k host_neutral
uv run pytest -q
```

## Definition of rejected
A rule other than the six listed is in the template; any byte of `CLAUDE.md` outside the managed block changes; `AGENTS.md` changes outside the block beyond the one added bullet; marker or gate logic changes; `CHUPA_PLAN.md` changes.

## Time budget
- expected: 30m
- stuck: 60m
