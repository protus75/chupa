---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase6-continue-04
- bug-gate-grammar
- report-inbox-triage

## Context
- chupa/scorecard.py
- chupa/git.py
- chupa/retro.py
- chupa/__main__.py
- tests/test_scorecard.py
- tests/test_git.py
- tests/test_retro.py
- tests/test_cli.py
- tests/test_mergequeue.py
- chupa/triage.py
- tests/test_triage.py

## Plan contract
- 19.I
- 19.P6.escape-column
- 19.P6.bug-gate-grammar
- 19.P6.report-inbox-triage
- section 10
- section 14

## Goal / Why
Attribute resolved host bugs to reviewed squash candidates and show their passed-surface escapes in the shared scorecard.

## Scope in / Scope out
Implement the cited escape entry in its existing owners: Git for the first-parent read, triage for durable attribution, scorecard for the pure fold, and retro/status for shared collection and rendering. The registry fence gains chupa/triage.py and tests/test_triage.py for the entry's sequential-consumer ownership. Preserve existing public call signatures and composition. Keep report custody and bug authoring in their merged owners; add no queue, ticket writer, report schema, event vocabulary, provider call, hold, host-loop report or exit receipt.

## Scope fence
- chupa/scorecard.py
- chupa/git.py
- chupa/retro.py
- chupa/__main__.py
- tests/test_scorecard.py
- tests/test_git.py
- tests/test_retro.py
- tests/test_cli.py
- tests/test_mergequeue.py
- chupa/triage.py
- tests/test_triage.py

## Acceptance criteria
1. `uv run pytest -q tests/test_scorecard.py` passes with `test_escape_entry_unit` checking required_units for own and cited entries, unique resolve_plan_contract resolution, four entry_unit_gap parts, and rejection when each part is missing.
2. `uv run pytest -q tests/test_git.py` passes with `test_escape_first_parent_trailers` proving ordered first-parent single-SHA and BASE-exclusive range reads, changed paths and the squash trailer pair through the process seam. `test_escape_refusals` covers malformed or option-shaped input, unknown/side-branch endpoints, reversed/empty ranges, invalid/duplicate/missing trailers and process commits. Use full lowercase SHAs only; unavailable candidates are unattributed.
3. `uv run pytest -q tests/test_triage.py` passes with `test_resolved_bug_escape_attribution` exercising production Git, real report custody and bug resolution, path narrowing and passed Check/review provenance. Triage owns ESCAPE_ATTRIBUTION and completes the entry's exact result through Effects, keyed by box identity; admitted checks come from their completed lift commit and approving review evidence, preserving approved-SHA carry. Failed/bypassed gates, unfinished intents, later attempts and unproven surfaces contribute nothing.
4. `uv run pytest -q tests/test_triage.py` passes with `test_escape_attribution_retry` proving crash/rescan replay and recovery after resolution without another Author invocation or duplicate counts; read failures leave attribution incomplete and give a diagnostic repair road. `test_escape_unattributed_reports` covers non-bugs, unresolved/tombstone/decision resolutions, missing evidence and invalid ancestry, with an empty matches list and explanatory confidence note when attribution is unavailable. Bootstrap drain still consumes no Box.
5. `uv run pytest -q tests/test_scorecard.py` passes with `test_escape_counts_once_per_report_ticket_surface` proving report/ticket/passed-surface dedup across overlapping matches and duplicate completions, bypass/failure exclusion, unknown unproven surfaces, historical merges and retro boundaries. `test_escape_rates_and_pruning` proves the existing evaluated-ticket denominator, zero denominators and nonzero escapes preventing pruning at 25. Historical surfaces may have zero current-window evaluations. Keep zero-escape predecessor tests green without attribution, and preserve catch, bypass, spend, tokens, trigger and boundary operands.
6. `uv run pytest -q tests/test_retro.py tests/test_cli.py` passes with `test_escape_report_projection` and `test_status_escape_projection` exercising production collection and identical shared rendering while forbidding reads/writes, Git, models and mutations inside the pure projection.
7. `uv run pytest -q tests/test_mergequeue.py` passes with `test_escape_squash_trailer_identity` proving the existing producer's ticket/reviewed-SHA pair and approval carry. `uv run pytest -q tests/test_plan_lint.py` and `uv run pytest -q` pass with historical seeding fixtures unchanged.

## Verification
```
uv run pytest -q tests/test_scorecard.py tests/test_git.py tests/test_triage.py tests/test_retro.py tests/test_cli.py tests/test_mergequeue.py
uv run pytest -q tests/test_inbox.py tests/test_author.py tests/test_serve.py tests/test_status.py tests/test_phase5_exit.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
A missing governing entry fact is premise_failed with kind: spec_gap naming its owner; a criteria-forced fence addition without closure evidence requires plan repair.

## Time budget
- expected: 60m
- stuck: 90m
