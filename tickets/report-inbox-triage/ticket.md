---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase6-continue-03
- bug-gate-grammar

## Context
- chupa/box.py
- chupa/triage.py
- chupa/author.py
- chupa/daemon.py
- chupa/serve.py
- tests/test_box.py
- tests/test_triage.py
- tests/test_author.py
- tests/test_serve.py
- chupa/tickets.py
- chupa/seams.py
- hosts/fixture/scaffold.py
- hosts/fixture/replay.py

## Plan contract
- 19.I
- 19.P6.report-inbox-triage
- 19.P6.bug-gate-grammar
- section 12

## Goal / Why
Turn bounded host reports into durable evidence and reviewed regression bug tickets.

## Scope in / Scope out
Implement intake and custody solely under the cited entry contracts. The new chupa/inbox.py owns schema/bounds and inbox-to-Box ingestion; the existing Box writes custody and queue identities. Keep existing public signatures and default behavior for non-host messages, extending Box's nullable report descriptor and providing report-specific enqueue under that same owner. Triage remains the sole sequential ingest consumer, Author the sole authored-ticket/evidence writer, and serve the live composition owner. Ingest before the pending check, including an initially empty queue. Read the existing bug grammar and fixture harness; sibling-created tests/test_bug_gate.py is not Context. Preserve existing failure, dedup, decision, tombstone, policy, review and storm behavior. No additional queue/consumer, no prompt-spec edits, no report-supplied command execution, no escape attribution, GO or report producer.

## Scope fence
- chupa/inbox.py
- chupa/box.py
- chupa/triage.py
- chupa/author.py
- chupa/daemon.py
- chupa/serve.py
- tests/test_box.py
- tests/test_triage.py
- tests/test_author.py
- tests/test_serve.py
- tests/test_inbox.py

## Acceptance criteria
1. `uv run pytest -q tests/test_inbox.py` exits 0; `test_report_inbox_entry_units` uses required_units, resolve_plan_contract and entry_unit_gap for both intake and bug entries, unique resolution, four depth parts and missing-part rejection.
2. `uv run pytest -q tests/test_inbox.py` proves closed schema/defaults, both origins and version handling in `test_report_schema_is_closed`. `test_report_evidence_bounds` checks metadata before reads, exact 1 MiB/64 KiB acceptance, post-read growth, missing/non-regular files and root escape.
3. `uv run pytest -q tests/test_inbox.py` checks bounded durable custody before message publication in `test_report_custody_precedes_enqueue` even after source deletion/change, and stable arrivals across custody/enqueue/consume crashes in `test_report_retry_ingests_once`. Malformed arrivals remain unconsumed with a repair diagnostic.
4. `uv run pytest -q tests/test_box.py` proves `test_host_report_signature` preserves digits and location bytes in the self-diagnosed tuple, distinguishes version/location, and deduplicates durable descriptors without changing engine message signatures or legacy message readability.
5. `uv run pytest -q tests/test_triage.py tests/test_serve.py` exercises bootstrap `test_report_ingested_before_pending_scan`, live `test_empty_box_report_intake` and `test_report_consumer_is_sequential` through production composition. An absent inbox performs no intake and bootstrap drain stays free of a Box consumer.
6. `uv run pytest -q tests/test_author.py tests/test_triage.py` proves `test_bug_report_evidence_ticket_plane_commit` copies evidence before bug validation/policy/requisition review, commits it with the ticket before resolution, and executes only the deterministic host harness. `test_bug_report_text_stays_untrusted` covers player prose through triage, Author and later prompts. `test_report_author_failure_is_decision` preserves the single-Author allowance and failure-decision path.
7. `uv run pytest -q tests/test_inbox.py` proves `test_report_replay_to_regression` follows custody and host replay into permanent regression evidence through the merged production bug Check, with head-pass and base-overlay-fail.
8. `uv run pytest -q` and `uv run pytest -q tests/test_plan_lint.py` exit 0; preserve unrelated behavior and historical seeding fixtures.

## Verification
```
uv run pytest -q tests/test_inbox.py tests/test_box.py tests/test_triage.py tests/test_author.py tests/test_serve.py
uv run pytest -q tests/test_bug_gate.py tests/test_storm_producer.py tests/test_drain.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
Missing or contradictory governing entry facts return premise_failed with kind: spec_gap and the owning unit. A criteria-forced path outside earned closure requires plan repair.

## Time budget
- expected: 60m
- stuck: 90m
