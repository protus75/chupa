---
priority: P1
kind: chore
agent_tier: medium
agent_effort: medium
source: box:retro_finding
state: confirmed
---

## Depends on

- none

## Context

- tests/unit/test_specs.py

## On-demand

- chupa/specs/requisition_review.md

## Goal / Why

The changed-text limit in `chupa/specs/requisition_review.md` lets the reviewer approve a ticket it has itself found unbuildable. On commit-lock-commands attempt 1 (retro/43), the review summary said criterion 3's `review since ...` could not be built because the CommitLock identity in `chupa/lockfile.py` records no verb and nothing in `chupa/` reads a process command line. It then said the problem sat in text a prior review had already judged, so it was not raised as a finding, and it approved. Implement spent a paid attempt, ended in `premise_failed`, used a `premise_bounce` cap and the stem went to the Reject queue.

The spec says "Raise a NEW finding only against text the diff shows changed". It exempts only dependents accounting and an invalid prior reply. It has no exception for a defect that makes a criterion impossible to satisfy.

After this change the limit never applies to a defect that makes a criterion or a `## Verification` command impossible to satisfy against merged code. The reviewer raises that as a finding whether or not the text changed, and never approves while its summary records such a defect. The exception stays narrow: style, wording that is only arguable, and concerns that are not impossibility are not covered, so settled text is not reopened every round.

Rule home: this is a rule for the requisition_review prompt spec, which is engine content shipped in the `chupa` package. It is not a CLAUDE.md or CORE_TEMPLATE rule.

## Scope in / Scope out

Scope in:

- Add one sentence to the Task section of `chupa/specs/requisition_review.md`, next to the changed-text limit paragraph. It says the changed-text limit never applies to a defect that makes a criterion or `## Verification` command impossible to satisfy against merged code, that such a defect is raised as a finding whether or not the text changed, and that the reviewer never approves while its summary records such a defect. It also says style and arguable wording are not hits.
- Bump the spec `version` to the next minor above the version on main.
- Update the version pin in `test_spec_lint_accepts_the_implement_and_requisition_specs` in `tests/unit/test_specs.py` to match.
- Add the test `test_requisition_review_spec_raises_impossible_criteria_unchanged` in `tests/unit/test_specs.py`. It renders the spec, takes the Task text, and asserts the new sentence's key phrases are present.
- Amend the Premise park sentence in section 6.7 of `docs/how-chupa-works.md` that says the next review "raises new findings only against changed text". It adds that a defect making a criterion or `## Verification` command impossible to satisfy against merged code is raised whether or not its text changed.

Scope out:

- Any other rule in the spec, including the existing changed-text, dependents, and invalid-prior sentences.
- Code changes, other specs, and the other open requisition-review tickets' closures.

## Scope fence

- chupa/specs/requisition_review.md
- tests/unit/test_specs.py
- docs/how-chupa-works.md

## Acceptance criteria

1. `chupa/specs/requisition_review.md` Task text states that the changed-text limit never applies to a defect that makes a criterion or Verification command impossible to satisfy against merged code. It also states that such a defect is raised whether or not the text changed, and that the reviewer never approves while the summary records one. The test `test_requisition_review_spec_raises_impossible_criteria_unchanged` in `tests/unit/test_specs.py` asserts these phrases. It fails if the sentence is missing, and it fails if the sentence does not also say style and arguable wording are not hits, so an unbounded exception is ruled out.
2. The existing sentences "Raise a NEW finding only against text the diff shows changed" and "Unchanged text that no changed statement touches is not reviewed again." stay in the Task text, so the exception is added without removing the limit. `test_requisition_review_spec_checks_changed_text_against_unchanged` in `tests/unit/test_specs.py` still passes.
3. The spec `version` is the next minor above the version on main, and the pin in `test_spec_lint_accepts_the_implement_and_requisition_specs` matches it. That test passes, so a spec that lints but has a stale version pin is ruled out.
4. The Premise park entry in section 6.7 of `docs/how-chupa-works.md` still says the next review raises new findings only against changed text, and also names the exception: a defect that makes a criterion or Verification command impossible to satisfy against merged code is raised whether or not its text changed.

## Verification

```
./dev.py test tests/unit/test_specs.py
```

## Definition of rejected

- The exception applies to anything other than a defect that makes a criterion or Verification command impossible to satisfy against merged code, for example to style or arguable wording.
- The spec edit removes or weakens the existing changed-text limit or the dependents-accounting and invalid-prior exemptions.
- Any file outside the fence is edited.

## Time budget

- expected: 20m
- stuck: 60m
