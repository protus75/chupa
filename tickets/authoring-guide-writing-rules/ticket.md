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

After this change, `chupa/docs/host-authoring.md` carries the adopted rules below, reworded as chupa-neutral guidance. Three of them earned their place with fungo run failures on 2026-11-13:
- `s11-fit-priors` asked for a test player with a birth date and no first-season value. The loader drops such rows, so the implementer stopped with `premise_failed` and the premise-bounce cap was spent. This is the producible-case rule.
- `s11-rates-first-season` and `s11-fit-priors` each stopped at requisition review with `invariant-untested`. This is the author self-check before review.
- `s11-sanity-checks-run` stopped at requisition review. Adding an entry to a table registry broke a test that loops over the registry, and "nothing else changes" forbade the import the change needed. This is the forced-edit rule for Scope in.

Rule home: these are host-general authoring method. Their home is the installed guide `chupa/docs/host-authoring.md`. They do not go in `CORE_TEMPLATE` in `chupa/hostfiles.py` (that holds session and engine conduct) or in this repo's `CLAUDE.md`/`AGENTS.md`.

Declined, so they are not added: a separate rule for a feature's enforcement check (it is folded into the split rule as an example); the batch self-check and the "when a batch" rule (handoff ceremony with no incident; `chupa lint` and `chupa review` already validate the set); "no retro tickets" (no incident in any host); "secrets are never written" (only hosts with authenticated sources need it, so it is host content); and fungo's stated-doc-edit rule (the existing `Scope fence` bullet already makes a ticket that changes documented behavior fence the document so docs and code land together; fungo can cite that bullet).

## Scope in / Scope out
Scope in. All edits are in `chupa/docs/host-authoring.md` unless a bullet names another file. Write plain, short sentences in the guide's existing voice. The quoted phrases below must appear verbatim, because the new test pins them.
- Workflow step 3: before the sentence about running `chupa review`, add an author self-check. Before review, check what review checks: no criterion contradicts merged behavior or an existing test outside the fence; all criteria can hold together; and every invariant the ticket states or cites "has a criterion whose test fails when the invariant is dropped".
- Workflow: add a step after step 4: "Never edit a settled or rejected ticket or its run record"; write a new ticket instead.
- `Depends on` bullet: add that merged code includes a test helper, fixture, fixture data set, or check rule that another ticket creates. A ticket that uses one "depends on the ticket that creates it".
- `Context` bullet: add that Context stays short. List the governing spec sections first, selected by heading. List a source file only when the agent must understand that module to avoid breaking it. Put large references in `On-demand`. Include the phrase "the governing spec sections first".
- `Goal / Why` bullet: add that the Goal quotes the rule the change serves and names its spec section, so the agent reads the right part of a long document. Add that a `kind: bug` Goal states four things: the observed wrong output and the command that produced it; the expected output and the spec that sets it; the suspected cause and "at least one other location the agent must inspect and rule out"; and, when an earlier ticket attempted the same bug, the fix shapes the agent must not ship. Why: an agent satisfies a misdiagnosed premise and ships a test that passes on it.
- `Scope in / Scope out` bullet: add that when Scope in limits what changes in a fenced file ("only", "nothing else changes"), it "names every edit the change forces there". Examples: the import a new name needs, and the expected set or skip list of every test that loops over a registry the ticket extends.
- `Scope fence` bullet: add that the fence names "the test modules and fixture directories the ticket owns", never a whole tests directory. Also add that when a `Depends on` ticket is not merged yet, the author reads its fence and criteria. Any test it creates that asserts behavior this ticket changes goes in this fence, and Scope in names the one expectation that may change.
- `Acceptance criteria` bullet: add four rules. (1) A criterion may assert absence, for example "rows of kind X are absent" or "nothing past the cutoff is read". (2) A criterion names the exact stored form, such as `blank -> null` or leading zeros kept, "never 'preserved' or 'as received'". (3) A placeholder for something nothing reads uses a made-up name, "never a real path a later ticket may start reading". (4) A case that must come from real code (a loader, a builder, a test helper) is checked in that code before the criterion is written. A case the code filters out or cannot build is "marked hand-built" with its reason, and the Goal does not promise it.
- `## Bug tickets` > `### Evidence`: add one sentence. Save the evidence "before any change that destroys it", such as deleting a file, reloading data, or a manual fix.
- New section `## Splitting and ordering`, placed after `## What each section is for`, with three bullets:
  - Pieces are independent when their scope fences do not overlap and neither uses the other's output (a helper, fixture, schema, or file layout). Independent pieces are separate tickets. Litmus: "could the two land as separate merges in either order without breaking main?" Keep pieces in one ticket only when landing one without the other breaks main. A change that spans several layers is usually several tickets, not one ticket with phases. Why: one agent editing independent surfaces cross-wires them, and one bad piece sinks the good ones.
  - A check that enforces a new feature uses the feature's output, so it is its own ticket that depends on the feature. The exception is when main would mislead while the feature lacks its check.
  - When one request yields several deliverables, list each one and mark it ticket, defer, or reject. Then write the foundation tickets before the tickets that depend on them.
- Keep the existing phrase "the next minor above the version on main" in the guide; `tests/integration/test_author.py` pins it.
- Create `tests/unit/test_host_authoring.py`. One test reads `chupa/docs/host-authoring.md` and asserts that each quoted phrase above is present, plus the heading `## Splitting and ordering`. Follow the style of `tests/unit/test_host_running.py`.

Scope out:
- `chupa/specs/author.md`, `chupa/specs/requisition_review.md` (review already checks the self-check items and forced fence edits), `CORE_TEMPLATE` in `chupa/hostfiles.py`, `CLAUDE.md`, `AGENTS.md`, `docs/how-chupa-works.md`, lint and gate code, and every declined rule named in Goal / Why.
- Existing guide text other than the bullets named above. The `## Path matching` section and the rest of `## Bug tickets` are unchanged.

## Scope fence
- chupa/docs/host-authoring.md
- tests/unit/test_host_authoring.py

## Acceptance criteria
1. `tests/unit/test_host_authoring.py` asserts that `chupa/docs/host-authoring.md` contains each quoted phrase from Scope in and the heading `## Splitting and ordering`, and `./dev.py test tests/unit/test_host_authoring.py` passes. A guide that leaves out any adopted rule (for example, the self-check without "has a criterion whose test fails when the invariant is dropped") fails the test.
2. `./dev.py test tests/integration/test_author.py` still passes. A guide that loses "the next minor above the version on main" fails it.
3. `./dev.py test tests/unit/test_docs_verb.py` passes. The guide stays at the installed path that `chupa new` prints; moving or renaming it fails the test.

## Verification
```
./dev.py test tests/unit/test_host_authoring.py tests/integration/test_author.py tests/unit/test_docs_verb.py
```

## Definition of rejected
- The guide gains a declined rule: a separate batch self-check, a no-retro-tickets rule, a secrets rule, or a stated-doc-edit rule beyond the existing `Scope fence` text.
- The guide names fungo, its stems, or its domain (players, seasons, priors) in the added text.
- Existing guide text outside the named bullets and Workflow steps is reworded or removed.
- Any file outside the scope fence changes.

## Time budget
- expected: 25m
- stuck: 60m
