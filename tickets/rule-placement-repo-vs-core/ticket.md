---
state: confirmed
source: human
priority: P1
kind: chore
---

## Depends on
- none

## Context
- CLAUDE.md
- AGENTS.md
- chupa/hostfiles.py::CORE_TEMPLATE
- tests/integration/test_hostfiles.py::test_core_activation_first_adoption

## Goal / Why
Agent rules live in two places, and nothing tells an author which one a new rule belongs in. Repo rules are about working on chupa itself (its code, tests, layout, `./dev.py` verbs). They live in this repo's `CLAUDE.md` and `AGENTS.md`, outside the `<!-- chupa:core begin/end -->` block. Host rules are rules every host repo should follow (ticket authoring, diagnosis, chat and engine conduct). They live in `CORE_TEMPLATE` in `chupa/hostfiles.py`, and `chupa core` installs that into each host's managed block, this repo included. Today the only guidance is "never hand-edit this managed block". On 2026-11-11 the owner asked that every change to AI rules make this split explicit. If it isn't explicit, a host rule written only into this repo's files never reaches other hosts, and a repo-only rule put into the template is installed into hosts where it does not fit.

After this change, `CLAUDE.md` section A and the `## Engine conduct` section of `AGENTS.md` each carry one rule that names the two homes and says how to choose between them.

## Scope in / Scope out
- In: `CLAUDE.md`, section `## A. Engine conduct`: add one bullet directly after the `**Generated files are render targets, never write targets.**` bullet, in the same bold-lead plus `Why:` shape as its neighbours:
  - Bold lead: `**A rule has one of two homes.**`
  - Body: a rule about working on chupa itself (this repo's code, tests, layout, `./dev.py` verbs) goes in `CLAUDE.md` and `AGENTS.md` outside the managed block. A rule every host should follow goes in `CORE_TEMPLATE` in `chupa/hostfiles.py` and reaches every host, this repo included, through `chupa core`; it is never written only into this repo's files. A change that adds, moves, or edits an agent rule states which home each rule belongs in.
  - `Why:` a host rule written only here never reaches other hosts, and a repo rule in the template is installed where it does not fit (2026-11-11).
- In: `AGENTS.md`, section `## Engine conduct`: the same bullet, verbatim, directly after its `**Generated files are render targets, never write targets.**` bullet.
- Out: the managed block in either file, `chupa/hostfiles.py` and `CORE_TEMPLATE`, moving any existing rule between homes, and any gate or lint that enforces placement.

## Scope fence
- CLAUDE.md
- AGENTS.md

## Acceptance criteria
1. `CLAUDE.md` contains the bold lead `**A rule has one of two homes.**` after the `**Generated files are render targets, never write targets.**` bullet and outside the `<!-- chupa:core begin -->`/`<!-- chupa:core end -->` block, and its body names `CORE_TEMPLATE`, `chupa/hostfiles.py`, and `chupa core`.
2. `AGENTS.md` contains the same bullet text, byte-for-byte, after its `**Generated files are render targets, never write targets.**` bullet and outside the managed block.
3. `./dev.py test tests/integration/test_hostfiles.py` passes, including `test_core_activation_first_adoption`, which fails if the managed block in either file is edited instead of the text below it.
4. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_hostfiles.py
./dev.py test
```

## Definition of rejected
Reject the branch if the managed block in `CLAUDE.md` or `AGENTS.md` changes, if `chupa/hostfiles.py` changes, if any existing rule is moved or reworded, or if the two files' new bullets differ.

## Time budget
- expected: 10m
- stuck: 25m
