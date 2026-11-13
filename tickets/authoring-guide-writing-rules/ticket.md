---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
- none

## Context
- chupa/docs/host-authoring.md
- tests/integration/test_author.py::test_author_spec_requires_criteria_to_name_wrong_results
- tests/unit/test_host_running.py

## Goal / Why
The fungo host reviewed its own authoring docs on 2026-11-13 and found 22 rules that are general ticket-writing method, not fungo content. Fungo is removing them from its docs and offered them to chupa. `chupa/docs/host-authoring.md` is where every host's author is sent (`chupa new` prints its path), so a general rule that lives only in one host's docs never reaches the other hosts.

This ticket adopts only the critical rules: those whose absence stops a run (a premise bounce, a forced file outside the fence, a requisition snag round, or a bug ticket chupa refuses). After this change, `chupa/docs/host-authoring.md` carries these six rules, reworded as chupa-neutral guidance. Three of them earned their place with fungo run failures on 2026-11-13:
- `s11-fit-priors` asked for a test record that the real loader drops, so the implementer stopped with `premise_failed` and the premise-bounce cap was spent. This is the producible-case rule.
- `s11-rates-first-season` and `s11-fit-priors` each stopped at requisition review with `invariant-untested`. This is the author self-check before review.
- `s11-sanity-checks-run` stopped at requisition review. Adding an entry to a registry broke a test that loops over the registry, and "nothing else changes" forbade the import the change needed. This is the forced-edit rule for Scope in.

The other three stop runs by mechanism. A ticket that uses another ticket's fixture or test helper without `Depends on` can be scheduled before that fixture is merged. A test an unmerged predecessor creates, left outside this fence, is a forced file outside the fence and makes the ticket impossible. A bug whose evidence was destroyed cannot be filed, because every ticket read refuses a bug without evidence.

Rule home: these are host-general authoring method. Their home is the installed guide `chupa/docs/host-authoring.md`. They do not go in `CORE_TEMPLATE` in `chupa/hostfiles.py` (that holds session and engine conduct) or in this repo's `CLAUDE.md`/`AGENTS.md`. The other fungo rules are either queued as Suggestion Box items or declined, and none of them is part of this ticket.

## Scope in / Scope out
Scope in. All edits are in `chupa/docs/host-authoring.md` unless a bullet names another file. Write plain, short sentences in the guide's existing voice. The quoted phrases below must appear verbatim, because the new test pins them.
- Workflow step 3: before the sentence about running `chupa review`, add an author self-check. Before review, check what review checks: no criterion contradicts merged behavior or an existing test outside the fence; all criteria can hold together; and every invariant the ticket states or cites "has a criterion whose test fails when the invariant is dropped".
- `Depends on` bullet: add that merged code includes a test helper, fixture, fixture data set, or check rule that another ticket creates. A ticket that uses one "depends on the ticket that creates it".
- `Scope in / Scope out` bullet: add that when Scope in limits what changes in a fenced file ("only", "nothing else changes"), it "names every edit the change forces there". Examples: the import a new name needs, and the expected set or skip list of every test that loops over a registry the ticket extends.
- `Scope fence` bullet: add that when a `Depends on` ticket is not merged yet, the author "reads its fence and criteria". Any test it creates that asserts behavior this ticket changes goes in this fence, and Scope in "names the one expectation that may change".
- `Acceptance criteria` bullet: add that a case that must come from real code (a loader, a builder, a test helper) is checked in that code before the criterion is written. A case the code filters out or cannot build is "marked hand-built" with its reason, and the Goal does not promise it.
- `## Bug tickets` > `### Evidence`: add one sentence. Save the evidence "before any change that destroys it", such as deleting a file, reloading data, or a manual fix.
- Keep the existing phrase "the next minor above the version on main" in the guide; `tests/integration/test_author.py` pins it.
- Create `tests/unit/test_host_authoring.py`. One test reads `chupa/docs/host-authoring.md` and asserts that each quoted phrase above is present. Follow the style of `tests/unit/test_host_running.py`.

Scope out:
- `chupa/specs/author.md`, `chupa/specs/requisition_review.md` (review already checks the self-check items and forced fence edits), `CORE_TEMPLATE` in `chupa/hostfiles.py`, `CLAUDE.md`, `AGENTS.md`, `docs/how-chupa-works.md`, lint and gate code.
- Every other fungo rule, whether queued as a suggestion or declined: splitting and ordering, Context length, Goal citing its rule, narrow test fences, other criterion-writing rules, bug Goal rigor, settled-ticket edits, batch self-check, retro tickets, secrets, and stated doc edits.
- Existing guide text other than the bullets named above. The `## Path matching` section and the rest of `## Bug tickets` are unchanged.

## Scope fence
- chupa/docs/host-authoring.md
- tests/unit/test_host_authoring.py

## Acceptance criteria
1. `tests/unit/test_host_authoring.py` asserts that `chupa/docs/host-authoring.md` contains each quoted phrase from Scope in, and `./dev.py test tests/unit/test_host_authoring.py` passes. A guide missing any quoted phrase fails the test; for example, a self-check without "has a criterion whose test fails when the invariant is dropped" fails.
2. `./dev.py test tests/integration/test_author.py` still passes. A guide that loses "the next minor above the version on main" fails it. Both tests read the guide at `chupa/docs/host-authoring.md`, so moving or renaming it fails both.

## Verification
```
./dev.py test tests/unit/test_host_authoring.py tests/integration/test_author.py
```

## Definition of rejected
- The guide gains a rule this ticket does not adopt, for example a splitting section, a Context length rule, or a bug Goal template.
- The guide names fungo, its stems, or its domain in the added text.
- Existing guide text outside the named bullets is reworded or removed.
- Any file outside the scope fence changes.

## Time budget
- expected: 20m
- stuck: 45m
