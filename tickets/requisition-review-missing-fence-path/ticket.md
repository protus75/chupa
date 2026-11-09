---
priority: P2
kind: chore
agent_tier: medium
agent_effort: medium
source: box:suggestion
state: confirmed
---

## Depends on
- none

## Context
- tests/unit/test_specs.py
- tests/integration/test_requisition.py

## On-demand
- chupa/specs/requisition_review.md

## Goal / Why
Ticket review approved `chupa-ruff-reclean` although `watch.py`, named in its `## Scope fence` and `## Verification` commands, had been deleted in cc6166bd (2026-11-06). Implement then bounced it as `premise_failed` on 2026-11-07. That cost one paid Implement attempt and one `premise_bounce` unit on a premise that was already false at review time. `chupa/tickets.py` checks that `## Context` and `## On-demand` paths exist, but not `## Scope fence` or `## Verification` paths. A lint cannot do this alone, because a fence may legitimately name a file the ticket creates. The requisition reviewer can read Scope in and tell a created file from a stale one. After this change `chupa/specs/requisition_review.md` carries a rule: a path in `## Scope fence` or in a `## Verification` command that does not exist at the review commit, and that Scope in does not say the ticket creates, is a `snag` finding naming that path. The rule is limited to paths absent at the review commit. A path the ticket creates, a path that is only an output (for example a `tmp_path` file or a report the command writes), and a path that exists are not hits.

## Scope in / Scope out
- In: `chupa/specs/requisition_review.md`: add one Task bullet for the stale-path rule with the stated limit, and bump `version` to the next minor above its value at the base commit ("3.3" when drafted; sibling spec tickets may have bumped it since).
- In: `tests/unit/test_specs.py`: the `requisition_review` version pin moves to that new version.
- In: `tests/integration/test_requisition.py`: `test_spec_loads_and_names_finding_keys` asserts the new rule phrases are in the spec source.
- Out: `chupa/tickets.py` and every lint, the author spec, every other spec, and `docs/`.

## Scope fence
- chupa/specs/requisition_review.md
- tests/unit/test_specs.py
- tests/integration/test_requisition.py

## Acceptance criteria
1. `chupa/specs/requisition_review.md` is at a version one minor above its value at the base commit. `./dev.py test tests/unit/test_specs.py` pins it, which rules out an unbumped spec.
2. The spec body contains the phrases `does not exist at the review commit` and `does not say the ticket creates`. `./dev.py test tests/integration/test_requisition.py` asserts both, which rules out a spec with no stale-path rule.
3. The spec body contains the limit phrase `a path the ticket creates is not a hit`. `./dev.py test tests/integration/test_requisition.py` asserts it, which rules out a rule that snags every fence entry the ticket adds as a new file.
4. The existing Task bullets stay: `./dev.py test tests/integration/test_requisition.py` still asserts `An unaccounted file is a `snag` finding naming it`, which rules out a change that weakens the existing closure text.
5. The spec body contains the output limit phrase `a path that is only an output of a command is not a hit`. `./dev.py test tests/integration/test_requisition.py` asserts it in `test_spec_loads_and_names_finding_keys`, which rules out a rule that snags output-only paths such as a coverage report file a `## Verification` command writes.

## Verification
```
./dev.py test tests/unit/test_specs.py
./dev.py test tests/integration/test_requisition.py
```

## Definition of rejected
The rule lacks the stated limit and snags created files; the rule snags output-only paths; the version is not bumped or the pin keeps the old value; existing Task bullets are weakened; any file outside `## Scope fence` changes.

## Time budget
- expected: 20m
- stuck: 45m
