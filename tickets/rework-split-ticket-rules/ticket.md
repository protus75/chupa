---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
none

## Context
- chupa/tickets.py
- chupa/rework.py

## On-demand
- chupa/specs/rework.md

## Goal / Why
`specs-in-package` failed the 30-file diff budget, and Rework proposed a split 8 times across two attempts (2026-11-06). Every proposal was refused by the ticket checker, almost always for the same two rules the Rework prompt never states:
- an `## On-demand` path not covered by `## Scope fence`;
- a `## Context` or `## On-demand` path that does not exist yet because a sibling successor creates it (`chupa/specs/retro.md`).
Each re-prompt fixed the named finding and broke another. One reply also put prose before its JSON.

After this change `chupa/specs/rework.md` states those rules, so a split's successors pass the ticket checker on the first call.

## Scope in / Scope out
- In: `chupa/specs/rework.md` `## Task` gains a short rule list matching `chupa/tickets.py`:
  - every `## On-demand` path is an existing file also covered by `## Scope fence`; a read-only reference goes in `## Context`;
  - `## Context` and `## On-demand` name only files that exist on main now; a file a sibling successor creates or moves appears only in `## Scope fence` and `## Verification`;
  - each acceptance criterion names its check in backticks;
  - each successor's diff, counting renamed files, fits the diff budget named in the findings.
- In: the `version` minor number goes up by one.
- In: `tests/test_rework.py` `test_rework_spec_render_and_driver`: its pinned rework spec version moves to `"1.1"` and its golden render sha256 is recomputed from the new spec.
- Out: `chupa/tickets.py` and `chupa/rework.py` behavior; other specs.

## Scope fence
- chupa/specs/rework.md
- tests/test_rework.py

## Acceptance criteria
1. `chupa/specs/rework.md` names the `## On-demand` fence rule and the exists-on-main rule, and still lints clean under `uv run pytest -q` (`tests/test_specs.py`).
2. `test_rework_spec_render_and_driver` in `tests/test_rework.py` passes with version `"1.1"` and the recomputed render hash.
3. `uv run pytest -q` exits 0.

## Verification
```
uv run python -c "from pathlib import Path; t = Path('chupa/specs/rework.md').read_text(); assert '## On-demand' in t and '## Scope fence' in t"
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of the following holds:
- the spec exceeds its line limit or fails spec lint;
- any file other than `chupa/specs/rework.md` and `tests/test_rework.py` changes.

## Time budget
- expected: 20m
- stuck: 60m
