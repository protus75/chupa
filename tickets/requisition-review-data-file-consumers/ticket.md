---
priority: P2
kind: feature
agent_tier: medium
agent_effort: medium
source: box:retro_finding
state: draft
---

## Depends on
- none

## Context
- tests/unit/test_specs.py
- tests/integration/test_requisition.py

## On-demand
- chupa/specs/requisition_review.md

## Goal / Why
The `exit-receipt-machinery` seed passed requisition review twice. Its Scope in reshaped the `hosts/fixture` Author ticket data, which `tests/integration/test_inbox.py::test_report_replay_to_regression` reads. That test sat outside the fence, yet the seed's own preservation Verification ran it unchanged. The migration contradicted it. Implement found this and returned `premise_failed`, which caused a Reject-queue hold and a spent `premise_bounce` cap.

The snag rule in `chupa/specs/requisition_review.md` traces only referenced code symbols and bumped-constant values. It never asks who reads a data or fixture file whose shape Scope in changes. The coverage map cannot see these readers, because they do not execute fenced code.

After this change the review also traces the consumers of each data or fixture file whose shape Scope in changes. It snags only a consumer whose assertions or inputs the required reshape contradicts, and names that consumer. A consumer that merely loads the file, or reads only fields the reshape leaves unchanged, is not a finding.

## Scope in / Scope out
- In: `chupa/specs/requisition_review.md`: add one Task bullet. For each data or fixture file whose shape, fields, or values Scope in changes, find the test files that read it. Include any test that a `## Verification` command runs as an unchanged preservation suite. Snag, naming the test, each one outside the fence whose assertions or inputs the change contradicts. Say that a test which only loads the file or reads unchanged fields is not a finding. Bump the spec version minor from `3.3` to `3.4`.
- In: `tests/unit/test_specs.py`: the `requisition_review` version pin changes from `"3.3"` to `"3.4"`.
- In: `tests/integration/test_requisition.py`: next to the existing spec-source assertion for the coverage-dependents rule, assert that the spec source contains the new data-file consumer rule and its limit to contradicted consumers.
- In: `docs/how-chupa-works.md`: the `requisition_review.md` row in the spec table notes that the review also traces consumers of reshaped data files.
- Out: any change to `chupa/requisition.py`, the coverage map, or the data blocks; mechanical consumer detection; Implement or Check behavior.

## Scope fence
- chupa/specs/requisition_review.md
- tests/unit/test_specs.py
- tests/integration/test_requisition.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_requisition.py tests/unit/test_specs.py` exits 0. The spec-source test fails if the spec lacks the data-file consumer rule, and also fails if the rule lacks the limit to contradicted consumers (a rule that snags every file that loads the data would pass a presence-only check).
2. `grep -n "data or fixture file" chupa/specs/requisition_review.md` prints the new rule.
3. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_requisition.py tests/unit/test_specs.py
grep -n "data or fixture file" chupa/specs/requisition_review.md
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- the new rule snags a test that only loads or imports the data file without a contradicted assertion or input;
- the spec version is not bumped to `3.4`, or the `tests/unit/test_specs.py` pin still reads `3.3`;
- any file outside `## Scope fence` changes.

## Time budget
- expected: 20m
- stuck: 60m
