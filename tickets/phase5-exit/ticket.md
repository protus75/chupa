---
priority: P1
kind: feature
agent_tier: high
agent_effort: high
source: seed
state: confirmed
---

## Depends on
- phase5-continue-05

## Context
- chupa/retro.py
- chupa/scorecard.py
- chupa/baseline.py
- chupa/git.py
- chupa/seams.py
- chupa/specs.py
- chupa/stages.py
- chupa/config.py
- tests/test_seeded_phase3_core.py
- tickets/retro-box-activation/checks.json
- tickets/baseline-binding-reader/checks.json

## Plan contract
- 19.L
- 19.I
- 19.P5
- 19.P6
- section 13
- 19.P6.core-renderer
- 19.P6.core-drift-classifier
- section 8
- section 15

## Goal / Why
Read the Phase 5 exit evidence and admit exactly the Phase 6 core and its first continuation into the running drain.

## Scope in / Scope out
Start high/high because 19.L identifies phase exits as KNOWN-HARD. Create tests/test_phase5_exit.py for the named reads below and tests/test_seeded_phase6_core.py for authoring snapshots. No production change or separate Phase 5 report is specified. The tickets fence permits new seed files only; never alter existing tickets, checks, reports or run records. Read predecessor owners and merged tests before writing. Keep historical seeding fixtures immutable.

test_phase5_exit_dependency_coverage traverses committed predecessor tickets from phase5-continue-05 and proves transitive coverage of retro-drain-invoker, retro-box-activation, scorecard-reporting, status-projection, baseline-binding-reader and retro-doctor-cli, including registry consumption edges. Dispatch is the merged-presence proof; any additional entry check is only a bare squash-trailer read using the existing Git seam. Do not cross-check predecessor approvals as entry provenance. A rejected predecessor needs its merged same-goal replacement and rewired coverage under 19.L.

test_phase5_exit_committed_retro reads the lexicographically latest committed tickets/retro/<seq>.md. Machinery emitters are retro-drain-invoker and scorecard-reporting; the producer is the forced pre-exit retro after the final feature merge. That producer commits before this ticket dispatches. Receipt absence during phase5-continue-05 authoring is expected, while absence at this exit's run is an unmet read. Consume the existing Retro receipt JSON and its Surface scorecard table; never manufacture, refresh, hand-commit or substitute fixture evidence. Require finite numeric measurements.usd, integer known/unknown_calls in input_tokens and output_tokens, real existing check surfaces and ticket stems, and zero escapes and escape rates. Validate the report's provenance.head against committed history after the final feature merge and its spec_version against the governed retro spec; validate merge commit/stem references and check_observations against committed production invoices. Retain window_boundary, window_final_event and the real record shapes emitted by render_report. Prove actual production derivation with the wired-and-shaped evidence of production_evidence, project_scorecard and the forced hook, exercising their real compositions with injected seams; a symbol-presence scan cannot establish it. Named test_phase5_exit_retro_provenance rejects fabricated stems, surfaces, fixture provenance, malformed accounting and stale pre-feature receipts. Read runtime operands from the committed receipt; never require a live ignored journal or state directory in a clean checkout, nor a test-written receipt as the exit read. Unchanged tests/test_retro.py, tests/test_scorecard.py and tests/test_drain.py supply preservation and production-composition evidence.

test_phase5_exit_retro_box reads the merged tests/test_retro_box.py chain and retro-box-activation's committed checks.json through Invoice. Require passed, an unbypassed passing verification and rc=0 for its recorded command running tests/test_retro_box.py. Re-exercise test_completed_retro_proposals_reach_prompt_spec_merge unchanged at Check: production retro_finding -> Box -> triage/Author -> prompt-spec admission, with the existing bridge identities. Its emitter is retro-box-activation; no live daemon loop is required.

test_phase5_exit_baseline reads baseline-binding-reader's committed checks.json through Invoice with the same passing verification evidence for tests/test_baseline.py. Re-exercise merged test_baseline_states_and_latest_signal and test_baseline_routing_and_spec_drift, proving injected Phase 1 NO_GO is unbound and GO followed by a spec-major bump is REVOKED. Its emitter is baseline-binding-reader. No production GO is required before operator cutover. Keep these suites unchanged in Verification, outside Context and the write fence.

Read committed BEGIN_REGISTRY_P6/END_REGISTRY_P6 YAML without copying it to a source file. Author exactly core-renderer, core-drift-classifier and phase6-continue, never later payloads. Core payloads depend on phase5-exit; core-drift-classifier also depends on core-renderer; phase6-continue depends on both core payloads and carries position 1 with admissions[1:]. Preserve all row consumption and refuse forward edges. Bound the batch including continuation by seeding.max_seeds_per_admission and each stuck budget by drain.max_ticket_minutes. Ordinary rows and continuations start medium/medium; only deep: true rows are KNOWN-DEEP high/high and alone, and exits are KNOWN-HARD high/high.

Before authoring, resolve_plan_contract resolves every role, row and entry citation; required_units and entry_unit_gap validate every needed non-exit entry's Owner, Records, Observable and Tests. Missing or contradictory governing facts return premise_failed with kind: spec_gap naming the owning cited unit. Core-renderer cites 19.I, 19.P6.core-renderer, sections 8 and 15. Core-drift-classifier cites 19.I, 19.P6.core-drift-classifier, 19.P6.core-renderer and section 8. Cite only ids; copy no cited unit prose. New chupa/hostfiles.py ownership and every core test obligation come from those two entry units. The continuation cites its seeding role and the entries governing its next admission, checking their depth before its own authoring; never invent missing contracts.

In tests/test_seeded_phase6_core.py pin all named renderer and classifier Tests obligations from the cited entries, including entry depth and missing-part rejection, first adoption, exact project-byte preservation, corruption refusal before any write, byte idempotence, branch-template golden, real routed CLI/no git, all four drift states, the full modal/imperative paragraph rules and acceptance boundaries, purity and production-gate dormancy. Preserve the later activation's ownership of core_drift registration and shared provider resolver. Apply 19.L rules 2-5 by scanning signatures, direct callers, compositions, public-operation allowlists and negatives across chupa/, eval/ and tests/. The row fence is the floor; record each earned addition's exact caller or contradicted assertion. An unearned forced edit needs contract repair. Existing fenced files default to Context; On-demand requires recorded overflow of 300,000 characters. Exclude created files, same-admission sibling creations, prompt specs and delimiter-bearing sources; preservation suites belong only in Verification. Use merged tests/test_seeded_phase3_core.py as idiom, never either new test of this admission as a seed's Context.

Renderer obligations to carry by name: test_renderer_entry_unit, test_core_first_adoption_preserves_project_bytes, test_core_refresh_preserves_remainder, test_core_marker_corruption_refuses_without_writes, test_core_render_is_byte_idempotent, test_core_golden_uses_branch_template, test_core_routed_conduct_files and test_core_refusal_and_no_git. Classifier obligations to carry by name: test_classifier_entry_unit, test_core_drift_classification, test_core_drift_refuses_marker_corruption, test_core_remainder_process_refusals, test_core_remainder_accepts_project_rules, test_core_drift_uses_branch_render, test_core_classifier_is_pure and test_core_classifier_unreachable_from_production_gates. These belong to their future payload tests, not assertions that hostfiles already exists.

Pin grammar, confirmed source: seed birth, exact identities, citations, dependency coverage, fence closure, depths, tiers, finite suffix and fixed maximum-effort render feasibility. Snapshot authoring head, idiom blob, entry hashes, all cited-unit lengths and file/ticket bytes and characters; render arithmetic reads only those recorded operands. Write the three new seed files directly and leave them uncommitted. Commit only the two new tests. Check performs requisition_review per seed, records approvals in tickets/phase5-exit/checks.json before one ticket-plane seed lift, retains approved bytes while ticket_sha matches, and re-authors only snagged seeds. No Box messages, manual release, Phase 6 implementation or seeding beyond that core and continuation.

## Scope fence
- tickets
- tests/test_phase5_exit.py
- tests/test_seeded_phase6_core.py

## Acceptance criteria
1. `uv run pytest -q tests/test_phase5_exit.py` exits 0 with test_phase5_exit_dependency_coverage proving all six Phase 5 payloads as transitive dependencies and their consumption edges.
2. `uv run pytest -q tests/test_phase5_exit.py` exits 0 with test_phase5_exit_committed_retro and test_phase5_exit_retro_provenance reading the latest real forced pre-exit tickets/retro/<seq>.md: scorecard, numeric spend/tokens, existing surfaces/stems, zero escapes and production provenance; emitters retro-drain-invoker + scorecard-reporting, producer forced pre-exit retro.
3. `uv run pytest -q tests/test_phase5_exit.py tests/test_retro_box.py` exits 0 with test_phase5_exit_retro_box reading retro-box-activation's passing committed checks.json and re-exercising its production proposal-to-prompt-spec chain.
4. `uv run pytest -q tests/test_phase5_exit.py tests/test_baseline.py` exits 0 with test_phase5_exit_baseline reading baseline-binding-reader's passing committed checks.json and proving NO_GO unbound and spec-major GO revocation.
5. `uv run pytest -q tests/test_seeded_phase6_core.py` exits 0 proving exactly core-renderer, core-drift-classifier and phase6-continue, their required entry test obligations, closure, role/depth checks and fixed render feasibility; tickets/phase5-exit/checks.json records approvals before the single seed lift, with only the new tests committed on the code branch.
6. `uv run pytest -q tests/test_plan_lint.py` and `uv run pytest -q` exit 0 preserving merged behavior and historical snapshots.

## Verification
```
uv run pytest -q tests/test_phase5_exit.py
uv run pytest -q tests/test_seeded_phase6_core.py
uv run pytest -q tests/test_phase5_exit.py tests/test_retro_box.py
uv run pytest -q tests/test_phase5_exit.py tests/test_baseline.py
uv run pytest -q tests/test_retro.py tests/test_scorecard.py tests/test_drain.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
At this ticket's run, any unmet exit read returns premise_failed naming the artifact and emitter. A governing gap returns premise_failed, kind: spec_gap naming its cited unit; a required edit beyond earned closure needs contract repair. Never conceal an unmet read with fixtures or live ignored state.

## Time budget
- expected: 60m
- stuck: 180m
