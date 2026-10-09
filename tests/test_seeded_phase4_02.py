"""Phase 4 admission 02: immutable authoring facts and ticket births.

Render arithmetic and entry-depth evidence use the recorded authoring head,
never live file or plan lengths. Live ticket reads retain the intake checks.
"""
from pathlib import Path

import pytest

from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent

AUTHORING_HEAD = 'eeb585f89c3377aa9f75287553e20ac736eb50f5'

IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

PAYLOADS = ('provider-cooldown-failover',)

BATCH = ('provider-cooldown-failover', 'phase4-continue-03')

REGISTRY_ADMISSIONS = (('watchdog-event-stream', 'notify-transport'),
 ('watchdog-detector', 'watchdog-activation'),
 ('provider-cooldown-failover',),
 ('reliability-battery',),
 ('reliability-run',),
 ('phase4-exit',))

UNSEEDED_SUFFIX = (('reliability-battery',), ('reliability-run',), ('phase4-exit',))

EDGES = {'provider-cooldown-failover': ('phase4-continue-02',),
 'phase4-continue-03': ('provider-cooldown-failover',)}

START = {'provider-cooldown-failover': ('high', 'high'), 'phase4-continue-03': ('medium', 'medium')}

FENCE_FLOORS = {'provider-cooldown-failover': ('chupa/providers.py',
                                'chupa/watchdog.py',
                                'chupa/timers.py',
                                'chupa/runner.py',
                                'chupa/restart.py',
                                'chupa/daemon.py',
                                'chupa/stages.py',
                                'chupa/merge.py',
                                'chupa/drain.py',
                                'chupa/serve.py',
                                'chupa/__main__.py',
                                'eval/shakeout/bench.py',
                                'eval/daemon_soak.py',
                                'tests/test_provider_cooldown_failover.py',
                                'tests/test_providers.py',
                                'tests/test_restart_timers.py',
                                'tests/test_stages.py',
                                'tests/test_serve.py',
                                'tests/test_merge.py',
                                'tests/test_mergequeue.py',
                                'tests/test_daemon_composition.py',
                                'chupa/audit.py',
                                'tests/test_audit.py'),
 'phase4-continue-03': ('tickets', 'tests/test_seeded_phase4_03.py')}

FENCE_ADDITIONS = {'provider-cooldown-failover': {'chupa/thresh.py': '19.L rule 4 and cited seam-owner closure: '
                                                   'Thresh.admit/run and _select own reservations '
                                                   'and breaker rechecks; integrate cooling '
                                                   'eligibility without duplicating those owners '
                                                   'or changing their signal records.',
                                'tests/test_thresh.py': '19.L rules 2-3: test_thresh_is_dormant '
                                                        'rejects chupa.thresh in the CLI import '
                                                        'closure; migrate this predecessor '
                                                        'assertion while keeping all FIFO, spill, '
                                                        'breaker and replay proofs.',
                                'chupa/driver.py': 'Cited seam-owner closure: Driver._run, done '
                                                   'and race own ticket deadlines, cost seconds '
                                                   'and exception-to-Finding mapping; consume '
                                                   'admission wait and distinguish a pre-call '
                                                   'drought from an executed failure.',
                                'chupa/llmeffect.py': 'Cited seam-owner closure: llm_call owns the '
                                                      'keyed LLM effect and its completion; '
                                                      'admission/identity must precede effect '
                                                      'intent while replay writes no new provider '
                                                      'outcome or cooldown.',
                                'chupa/requisition.py': 'Cited seam-owner closure: review_ticket '
                                                        'calls llm_call outside Driver.run and '
                                                        'catches provider exceptions as a snag; '
                                                        'carry drought through this ticket-owned '
                                                        'call without a false authoring failure or '
                                                        'spine draw.',
                                'eval/shakeout/providers.py': '19.L rule 5: _use_provider directly '
                                                              'constructs ProviderLLM at line 66; '
                                                              'supply the shared bench payload and '
                                                              'Timers to this fixture client.',
                                'eval/diagnose.py': '19.L rule 5: _run directly constructs '
                                                    'ProviderLLM at line 227 in a lock-held eval '
                                                    'lifetime; use the same provider admission '
                                                    'construction.',
                                'eval/harness.py': '19.L rule 5: _run directly constructs '
                                                   'ProviderLLM at line 362 in its eval lifetime; '
                                                   'use the same provider admission construction.'},
 'phase4-continue-03': {}}

HEADROOM_CHARS = 300000

IMPLEMENT_SPEC_CHARS = 4896

RENDER_OVERHEAD = 2000

DRAIN_MAX_TICKET_MINUTES = 180

MAX_SEEDS_PER_ADMISSION = 3

PLAN_CHARS = {'19.I': 1811,
 '19.P4.provider-cooldown-failover': 8157,
 '6': 38005,
 '15': 17104,
 '19.P3.thresh-runtime': 12153,
 '19.L': 20912,
 '19.P4': 5563,
 '19.P4.reliability-battery': 6888,
 '19.P4.reliability-run': 3372,
 '13': 19840}

FILE_CHARS = {'chupa/providers.py': 19824,
 'chupa/watchdog.py': 12133,
 'chupa/timers.py': 4966,
 'chupa/runner.py': 35603,
 'chupa/restart.py': 1951,
 'chupa/daemon.py': 26079,
 'chupa/stages.py': 59445,
 'chupa/merge.py': 18346,
 'chupa/drain.py': 31622,
 'chupa/serve.py': 20554,
 'chupa/__main__.py': 13381,
 'eval/shakeout/bench.py': 4698,
 'eval/daemon_soak.py': 35867,
 'tests/test_providers.py': 34459,
 'tests/test_restart_timers.py': 33950,
 'tests/test_stages.py': 32249,
 'tests/test_serve.py': 75256,
 'tests/test_merge.py': 34356,
 'tests/test_mergequeue.py': 53452,
 'tests/test_daemon_composition.py': 93706,
 'chupa/thresh.py': 9737,
 'tests/test_thresh.py': 24958,
 'chupa/driver.py': 20522,
 'chupa/llmeffect.py': 1364,
 'chupa/requisition.py': 8522,
 'eval/shakeout/providers.py': 5923,
 'eval/diagnose.py': 10358,
 'eval/harness.py': 19359,
 'chupa/seams.py': 8532,
 'chupa/effects.py': 3229,
 'chupa/journal.py': 10606,
 'chupa/notify.py': 7137,
 'tests/test_seeded_phase3_core.py': 5425,
 'chupa/audit.py': 5117,
 'tests/test_audit.py': 3588}

AUTHORED = {'provider-cooldown-failover': {'chars': 8254,
                                'plan': ('19.I',
                                         '19.P4.provider-cooldown-failover',
                                         '6',
                                         '15',
                                         '19.P3.thresh-runtime'),
                                'context': ('chupa/providers.py',
                                            'chupa/watchdog.py',
                                            'chupa/timers.py',
                                            'chupa/restart.py',
                                            'chupa/merge.py',
                                            'chupa/serve.py',
                                            'chupa/__main__.py',
                                            'eval/shakeout/bench.py',
                                            'chupa/thresh.py',
                                            'chupa/driver.py',
                                            'chupa/llmeffect.py',
                                            'chupa/requisition.py',
                                            'eval/shakeout/providers.py',
                                            'eval/diagnose.py',
                                            'eval/harness.py',
                                            'chupa/seams.py',
                                            'chupa/effects.py',
                                            'chupa/journal.py',
                                            'chupa/notify.py',
                                            'chupa/audit.py'),
                                'on_demand': ('eval/daemon_soak.py',
                                              'tests/test_daemon_composition.py',
                                              'tests/test_serve.py',
                                              'chupa/stages.py',
                                              'tests/test_mergequeue.py',
                                              'chupa/runner.py',
                                              'tests/test_providers.py',
                                              'tests/test_merge.py',
                                              'tests/test_restart_timers.py',
                                              'tests/test_stages.py',
                                              'chupa/drain.py',
                                              'chupa/daemon.py',
                                              'tests/test_thresh.py',
                                              'tests/test_audit.py'),
                                'fenced_existing': ('chupa/providers.py',
                                                    'chupa/watchdog.py',
                                                    'chupa/timers.py',
                                                    'chupa/runner.py',
                                                    'chupa/restart.py',
                                                    'chupa/daemon.py',
                                                    'chupa/stages.py',
                                                    'chupa/merge.py',
                                                    'chupa/drain.py',
                                                    'chupa/serve.py',
                                                    'chupa/__main__.py',
                                                    'eval/shakeout/bench.py',
                                                    'eval/daemon_soak.py',
                                                    'tests/test_providers.py',
                                                    'tests/test_restart_timers.py',
                                                    'tests/test_stages.py',
                                                    'tests/test_serve.py',
                                                    'tests/test_merge.py',
                                                    'tests/test_mergequeue.py',
                                                    'tests/test_daemon_composition.py',
                                                    'chupa/thresh.py',
                                                    'tests/test_thresh.py',
                                                    'chupa/driver.py',
                                                    'chupa/llmeffect.py',
                                                    'chupa/requisition.py',
                                                    'eval/shakeout/providers.py',
                                                    'eval/diagnose.py',
                                                    'eval/harness.py',
                                                    'chupa/audit.py',
                                                    'tests/test_audit.py'),
                                'created': ('tests/test_provider_cooldown_failover.py',),
                                'expected': 60,
                                'stuck': 90},
 'phase4-continue-03': {'chars': 5083,
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P4',
                                 '19.P4.reliability-battery',
                                 '19.P4.provider-cooldown-failover',
                                 '19.P4.reliability-run',
                                 '6',
                                 '13'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fenced_existing': (),
                        'created': ('tests/test_seeded_phase4_03.py',),
                        'expected': 60,
                        'stuck': 90}}

ACTUAL_BASE_RENDER_CHARS = {'provider-cooldown-failover': 291698, 'phase4-continue-03': 119813}

VALIDATED_DEPTH = {'19.P4.provider-cooldown-failover': None,
 '19.P3.thresh-runtime': None,
 '19.P4.reliability-battery': None,
 '19.P4.reliability-run': None}

ENTRY_PARTS = {'19.P4.provider-cooldown-failover': ('Owner', 'Records', 'Observable', 'Tests'),
 '19.P3.thresh-runtime': ('Owner', 'Records', 'Observable', 'Tests'),
 '19.P4.reliability-battery': ('Owner', 'Records', 'Observable', 'Tests'),
 '19.P4.reliability-run': ('Owner', 'Records', 'Observable', 'Tests')}

ENTRY_SHA = {'19.P4.provider-cooldown-failover': '9f10e1063176536930e9af578e464a733f580625bd70a20f55528f4a64669886',
 '19.P3.thresh-runtime': 'c0717d9c7371e5eb6792573d8820d1a095a7af9252d1587c90012c4dbc644877',
 '19.P4.reliability-battery': '56474392be97ed18f13d7a1015b283783c5cb7c94d2e57efd7c4a81f4973d5e8',
 '19.P4.reliability-run': 'e61ae1304153ff1c4befa66e17683b4a43a42139ad4d6ee0b80a770c2c4c5995'}

RESOLVED_CITATIONS = ('19.I',
 '19.P4.provider-cooldown-failover',
 '6',
 '15',
 '19.P3.thresh-runtime',
 '19.L',
 '19.P4',
 '19.P4.reliability-battery',
 '19.P4.reliability-run',
 '13')

VALIDATED_ROW_CITATIONS = {'provider-cooldown-failover': ('6', '15'), 'reliability-battery': ('6',)}

ENTRY_TESTS = ('test_quota_failure_arms_cooldown_without_infra_draw',
 'test_ordered_failover_preserves_served_identity',
 'test_all_candidates_cooling_recovers_on_timer_fired',
 'test_mid_run_drought_is_harvested_without_spine_draws',
 'test_single_candidate_cooldown_resumes_same_provider',
 'test_cooldown_reconstructs_and_rearms_new_windows',
 'test_one_provider_payload_and_timers_per_session',
 'test_provider_wait_excluded_from_ticket_and_watchdog_budgets',
 'test_executed_failures_preserve_classification_and_infra_accounting')

PREDECESSOR_ACTIVATION = {'tests/test_thresh.py': 'test_thresh_is_dormant',
 'tests/test_providers.py': 'test_cli_failure_classifier_is_dormant'}

PRESERVATION = ('tests/test_driver.py',
 'tests/test_drain.py',
 'tests/test_watchdog_activation.py',
 'tests/test_llm_effect.py',
 'tests/test_requisition.py',
 'tests/test_notify.py',
 'tests/test_shakeout.py',
 'tests/test_eval_harness.py',
 'tests/test_diagnose_eval.py',
 'tests/test_daemon_soak_runner.py')

DELIMITER_PATHS = ('eval/daemon_soak.py',)

PROVIDER_CONSTRUCTORS = {'chupa/runner.py': (96,),
 'chupa/__main__.py': (193,),
 'chupa/serve.py': (251,),
 'eval/shakeout/providers.py': (66,),
 'eval/diagnose.py': (227,),
 'eval/harness.py': (362,),
 'tests/test_providers.py': (97, 684)}

AUTHORED_TEXT = {
    'provider-cooldown-failover': """---
priority: P1
kind: feature
agent_tier: high
agent_effort: high
source: seed
state: confirmed
---

## Depends on
- phase4-continue-02

## Context
- chupa/providers.py
- chupa/watchdog.py
- chupa/timers.py
- chupa/restart.py
- chupa/merge.py
- chupa/serve.py
- chupa/__main__.py
- eval/shakeout/bench.py
- chupa/thresh.py
- chupa/driver.py
- chupa/llmeffect.py
- chupa/requisition.py
- eval/shakeout/providers.py
- eval/diagnose.py
- eval/harness.py
- chupa/seams.py
- chupa/effects.py
- chupa/journal.py
- chupa/notify.py
- chupa/audit.py

## On-demand
- eval/daemon_soak.py
- tests/test_daemon_composition.py
- tests/test_serve.py
- chupa/stages.py
- tests/test_mergequeue.py
- chupa/runner.py
- tests/test_providers.py
- tests/test_merge.py
- tests/test_restart_timers.py
- tests/test_stages.py
- chupa/drain.py
- chupa/daemon.py
- tests/test_thresh.py
- tests/test_audit.py

## Plan contract
- 19.I
- 19.P4.provider-cooldown-failover
- section 6
- section 15
- 19.P3.thresh-runtime

## Goal / Why
Activate shared provider admission, quota cooldown and subsequent-call failover over the configured candidates. The registry marks this cross-module admission deep, earning high/high under 19.L.

## Scope in / Scope out
Activate the provider admission described by the cited entries. chupa/providers.py owns selection and session cooling state, chupa/thresh.py keeps slot/breaker custody, and chupa/timers.py keeps every durable deadline write. Extend the existing drain/serve production graph and its composition harness. Keep current public Driver.run/from_config, Checkout, build_daemon_core, resolve and LLM request/result signatures; thread the new session state through the existing composition without requiring unrelated caller migrations. Migrate all direct ProviderLLM constructor sites in the fence in one change.

Compose one registry/cooldown payload and one Timers owner for each lock-held drain or serve lifetime, including refreshed config snapshots and ticketless surfaces. Route implement, review, rework, diagnosis, requisition review, triage, Author and future retro through that shared state. Eval roots and scripted benches use the same construction. Select once before the LLM effect and carry that choice through adapter events, watchdog metering, result, completion and harvested run identity. Preserve preflight and snapshot-local config/writer redaction. Clean up owned admission/timer waits with cancellation and awaited completion before releasing the lock.

On a classified quota failure, persist its cooldown using the entry's exact Timer identity and envelope before later routing acts. End and harvest the failed attempt, emit the existing soft report, and avoid an infra draw or inline retry. Exercise a duplicate pending window, a later fresh window, restart before/equal/after expiry, and failed arm/fire appends. Skip unavailable candidates in configured order, retain inherited and pinned models, and preserve the predecessor's FIFO and strict spill boundary. A single-candidate fixture must cool and resume its same identity.

Prove pre-dispatch drought with no running offer or model execution. Journal the entry-defined structured provider_drought transition, project its hold from that field, and release it automatically when routing recovers. A mid-run refusal follows the existing harvest/terminal/cleanup route exactly once, retaining earlier attempt evidence and drawing no cap, diagnosis, escalation ladder or Reject arrival. Cover nested requisition review as well as ordinary stages. Quota holds wait for the earliest relevant Timers deadline; expiry equality and breaker recovery permit fresh selection. Keep normal infra accounting and bounded unknown-failure evidence for executed failures, classifier Finding roads, auth alerts and existing notification/Box custody. Add no event/signal vocabulary or alternate failure spine.

Migrate test_thresh_is_dormant in tests/test_thresh.py and test_cli_failure_classifier_is_dormant in tests/test_providers.py to discriminating activation proofs. Retain the predecessor concurrency, FIFO/reselection, breaker, replay and six-class classifier tests. Preserve merged watchdog event capture, soft warning and group-kill behavior. Admission wait must be excluded from both ticket time and watchdog regions, including cancellation and replay; preserve the sole threshold signal writers and shapes. Read the predecessor tickets thresh-runtime, watchdog-detector and watchdog-activation before editing.

Named obligations in tests/test_provider_cooldown_failover.py: test_quota_failure_arms_cooldown_without_infra_draw, test_ordered_failover_preserves_served_identity, test_all_candidates_cooling_recovers_on_timer_fired, test_mid_run_drought_is_harvested_without_spine_draws, test_single_candidate_cooldown_resumes_same_provider, test_cooldown_reconstructs_and_rearms_new_windows, test_one_provider_payload_and_timers_per_session, test_provider_wait_excluded_from_ticket_and_watchdog_budgets, test_executed_failures_preserve_classification_and_infra_accounting. Each proves all cases assigned by the own entry, through injected seams and a multi-candidate fixture registry. The session test must cover real drain and serve lifetimes, repeated dispatches/config refresh, every ticket-owned and ticketless construction site, and awaited wait cleanup. The wait test must discriminate a queued call from a hung executing call. Extend the real production composition harness rather than creating another graph.

Read every Context and On-demand path before writing. On-demand is the measured headroom partition, including delimiter-bearing eval/daemon_soak.py. Use the existing effect and exception mapping owners in chupa/llmeffect.py and chupa/driver.py; no duplicate effect, classifier, routing or Timer implementation. Keep unfenced Verification suites unchanged as preservation evidence. Out: live provider/config alterations, real-model calls, wall-clock waits, new modules, knobs, signals, terminals, reports, provider dependencies, plan/ticket edits and historical seeding snapshots.

## Scope fence
- chupa/providers.py
- chupa/watchdog.py
- chupa/timers.py
- chupa/runner.py
- chupa/restart.py
- chupa/daemon.py
- chupa/stages.py
- chupa/merge.py
- chupa/drain.py
- chupa/serve.py
- chupa/__main__.py
- eval/shakeout/bench.py
- eval/daemon_soak.py
- tests/test_provider_cooldown_failover.py
- tests/test_providers.py
- tests/test_restart_timers.py
- tests/test_stages.py
- tests/test_serve.py
- tests/test_merge.py
- tests/test_mergequeue.py
- tests/test_daemon_composition.py
- chupa/audit.py
- tests/test_audit.py
- chupa/thresh.py
- tests/test_thresh.py
- chupa/driver.py
- chupa/llmeffect.py
- chupa/requisition.py
- eval/shakeout/providers.py
- eval/diagnose.py
- eval/harness.py

## Acceptance criteria
1. The first `uv run pytest` Verification command exits 0 with all nine named provider obligations, exact cooldown/drought records, identity stamps, bounded failure accounting and predecessor activation proofs.
2. The two targeted `uv run pytest` Verification commands exit 0 preserving production composition, injected wait accounting, preflight, replay, grants, redaction and active-executor abort binding.
3. `uv run pytest -q` exits 0; unchanged preservation suites and historical seeding snapshots remain green.

## Verification
```
uv run pytest tests/test_provider_cooldown_failover.py tests/test_providers.py tests/test_thresh.py tests/test_restart_timers.py tests/test_stages.py tests/test_serve.py tests/test_merge.py tests/test_mergequeue.py tests/test_daemon_composition.py tests/test_watchdog.py tests/test_audit.py
uv run pytest tests/test_driver.py tests/test_drain.py tests/test_watchdog_activation.py tests/test_llm_effect.py tests/test_requisition.py tests/test_notify.py tests/test_shakeout.py tests/test_eval_harness.py tests/test_diagnose_eval.py tests/test_daemon_soak_runner.py
uv run pytest -q
```

## Definition of rejected
Missing or contradictory governing facts return premise_failed, kind: spec_gap, naming the owning cited entry. If the criteria require a path outside the earned fence, repair the contract or closure rather than inventing facts or changing the registry.

## Time budget
- expected: 60m
- stuck: 90m
""",
    'phase4-continue-03': """---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- provider-cooldown-failover

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P4
- 19.P4.reliability-battery
- 19.P4.provider-cooldown-failover
- 19.P4.reliability-run
- section 6
- section 13

## Goal / Why
Author the closed reliability battery admission and its successor for Check to review and lift.

## Scope in / Scope out
Parse BEGIN_REGISTRY_P4 through END_REGISTRY_P4 from committed CHUPA_PLAN.md. Position 03 carries admissions[3:]: [reliability-battery], [reliability-run], [phase4-exit]. Author exactly reliability-battery and phase4-continue-04; the payload depends on phase4-continue-03 and the successor depends on reliability-battery. The successor carries admissions[4:]. Keep all registry rows and admission order intact. Both new seeds start medium/medium. Cap the batch with seeding.max_seeds_per_admission and each stuck budget with drain.max_ticket_minutes.

Before writing, run entry_unit_gap for 19.P4.reliability-battery and its required cited 19.P4.provider-cooldown-failover. Run resolve_plan_contract for all needed entry units, registry row citations and seeder-role citations against the merged plan, including the required next-successor citation 19.P4.reliability-run. Missing or contradictory facts stop as premise_failed, kind: spec_gap, naming the owning cited entry; do not invent facts. Validate future entry depth in its owning pass, without preemptively inspecting uncited later admissions. Cite plan units rather than copying their prose.

The battery implements its own entry and registry row, citing 19.I, 19.P4.reliability-battery, 19.P4.provider-cooldown-failover and section 6. New eval/reliability_battery.py owns the runner/writer; chupa/artifacts.py owns the closed models and chupa/stages.py owns report registration. It constructs the machinery only; reliability-run later produces the report. The successor cites 19.L, 19.I, 19.P4, section 13 and all entry/row citations its next admission needs. Do not author reliability-run or phase4-exit in this pass.

Read owners, predecessor tickets, direct callers and named tests. Grep signatures, construction sites, public allowlists and contradicted/absence assertions across chupa/, eval/ and tests/. Earn additions only under 19.L rules 2-5 or cited seam-owner closure, recording each path's precise reason. Existing fenced paths default to Context; measured headroom alone moves them On-demand. Created paths, same-admission siblings, prompt specs and delimiter-bearing files never enter Context. Unchanged preservation suites go only in Verification. Keep all historical seeding tests immutable.

Use merged tests/test_seeded_phase3_core.py as the idiom. Create tests/test_seeded_phase4_03.py with test_named_stems_cover_exactly_this_admission_and_successor, test_seed_passes_intake_lint_with_confirmed_seed_birth, test_dependencies_as_authored, test_stuck_budget_fits_the_drain_envelope, test_fence_contains_its_floor_and_only_earned_additions, test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract, test_successor_cites_next_admission_and_embeds_merged_earlier_idiom and test_context_closure_and_max_effort_render_use_authoring_snapshots. Pin exact identity, confirmed birth, intake grammar, edges, citation roles, required entry depth, every named obligation, earned closure and Context/On-demand partition. Record authoring head, idiom blob, ticket/file sizes and cited-unit lengths. Use fixed authoring snapshots for max-effort base renders under 300,000 characters; never recompute against live sizes or plan lengths.

Write the two seeds directly and leave them uncommitted. Check owns requisition_review, this seeder's checks.json approvals and one ticket-plane seed lift. Preserve approved bytes while ticket_sha matches; re-author only snagged seeds. Commit only the new batch test. Out: implementation, existing tickets or run records, plan edits, Box messages, manual release, later admissions and historical test edits.

## Scope fence
- tickets
- tests/test_seeded_phase4_03.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase4_03.py` exits 0 proving exactly the battery and successor, grammar, confirmed birth, edges, budgets, citation roles, required entry depth, named obligations, closure and fixed-snapshot renders.
2. `tickets/phase4-continue-03/checks.json` records each approval before one ticket-plane seed lift; the code commit contains only the new batch test.
3. `uv run pytest -q` exits 0 preserving merged behavior and historical seeding snapshots.

## Verification
```
uv run pytest -q tests/test_seeded_phase4_03.py
uv run pytest -q
```

## Definition of rejected
Missing or contradictory governing facts return premise_failed, kind: spec_gap, naming the owning cited entry. If the criteria require a path outside the earned fence, repair the contract or closure rather than inventing facts or changing the registry.

## Time budget
- expected: 60m
- stuck: 90m
""",
}

APPROVED_SEED_SHA256 = {'provider-cooldown-failover': '813c4fc7a714553deaa68001bd06983eae7e30fc3ac1d6d61c235f6ba6d078e2'}

REQUIRED_UNITS = {'provider-cooldown-failover': ('19.P4.provider-cooldown-failover', '19.P3.thresh-runtime'),
 'phase4-continue-03': ('19.P4.reliability-battery',
                        '19.P4.provider-cooldown-failover',
                        '19.P4.reliability-run')}

RESOLVED_FUTURE_CITATIONS = ('19.P4.reliability-run', '19.P4.reliability-battery', '19.L', '19.I', '19.P4', '13')

RESOLVED_UNIT_SHA = {'19.P4.reliability-run': 'e61ae1304153ff1c4befa66e17683b4a43a42139ad4d6ee0b80a770c2c4c5995',
 '19.P4.reliability-battery': '56474392be97ed18f13d7a1015b283783c5cb7c94d2e57efd7c4a81f4973d5e8',
 '19.L': '66e84cac9dacd539b1b29b3e51c82dfdade10c5228e8faea15a6adc8716ef4aa',
 '19.I': 'cfc0b1be4cfe88be240b6ae604660bd9d27a660cebbd7cad73ceca448091553c',
 '19.P4': '4d86e388bf537a8642a7961b275832ebf30b336efab9dbe861862c9a9147135d',
 '13': '62498fb56d1b5fae322306359b35345a8c0beae1f40c670c7fb5d5722b0a649f'}

def _birth(stem):
    return validate_ticket(stem, AUTHORED_TEXT[stem], ROOT, BATCH)


def _ticket(stem):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT, BATCH)


def render_chars(stem, extra=()):
    a = AUTHORED[stem]
    return (IMPLEMENT_SPEC_CHARS + a["chars"] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[uid] for uid in a["plan"])
            + sum(FILE_CHARS[path] for path in (*a["context"], *extra)))


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert BATCH == ("provider-cooldown-failover", "phase4-continue-03")
    assert REGISTRY_ADMISSIONS[2] == PAYLOADS == (BATCH[0],)
    assert REGISTRY_ADMISSIONS[3:] == UNSEEDED_SUFFIX == (
        ("reliability-battery",), ("reliability-run",), ("phase4-exit",))
    assert len(set(BATCH)) == len(BATCH) <= MAX_SEEDS_PER_ADMISSION
    assert set(EDGES) == set(START) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(AUTHORED) == set(BATCH)


@pytest.mark.parametrize("stem", BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    birth = _birth(stem)
    assert (birth.frontmatter.source, birth.frontmatter.state) == ("seed", "confirmed")
    assert (birth.frontmatter.agent_tier, birth.frontmatter.agent_effort) == START[stem]
    current = _ticket(stem)
    assert (current.frontmatter.source, current.frontmatter.state) == ("seed", "confirmed")
    assert START == {"provider-cooldown-failover": ("high", "high"),
                     "phase4-continue-03": ("medium", "medium")}
    if stem == BATCH[0]:
        assert "registry marks" in birth.sections["Goal / Why"]


@pytest.mark.parametrize("stem", BATCH)
def test_dependencies_as_authored(stem):
    assert EDGES == {"provider-cooldown-failover": ("phase4-continue-02",),
                     "phase4-continue-03": ("provider-cooldown-failover",)}
    assert _birth(stem).depends == _ticket(stem).depends == EDGES[stem]


@pytest.mark.parametrize("stem", BATCH)
def test_stuck_budget_fits_the_drain_envelope(stem):
    a = AUTHORED[stem]
    assert 0 < a["expected"] < a["stuck"] <= DRAIN_MAX_TICKET_MINUTES
    for t in (_birth(stem), _ticket(stem)):
        assert (t.expected_minutes, t.stuck_minutes) == (a["expected"], a["stuck"])


@pytest.mark.parametrize("stem", BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    expected = set(FENCE_FLOORS[stem]) | set(FENCE_ADDITIONS[stem])
    for t in (_birth(stem), _ticket(stem)):
        assert set(t.scope_fence) == expected
    assert not set(FENCE_FLOORS[stem]) & set(FENCE_ADDITIONS[stem])
    assert all(reason.startswith(("19.L rule", "Cited seam-owner closure"))
               for reason in FENCE_ADDITIONS[stem].values())
    if stem == BATCH[0]:
        assert set(PROVIDER_CONSTRUCTORS) <= expected
        assert set(PREDECESSOR_ACTIVATION) <= expected
        assert {"chupa/llmeffect.py", "chupa/driver.py", "chupa/requisition.py", "chupa/thresh.py"} <= expected
    else:
        assert not FENCE_ADDITIONS[stem]
    assert not any(path.startswith("tests/test_seeded") for path in expected
                   if path not in AUTHORED[stem]["created"])


def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract():
    stem = BATCH[0]
    expected = {"19.I", "19.P4.provider-cooldown-failover", "6", "15", "19.P3.thresh-runtime"}
    for t in (_birth(stem), _ticket(stem)):
        assert set(t.plan_contract) == expected == set(AUTHORED[stem]["plan"])
        assert "19.P4" not in t.plan_contract and "19.L" not in t.plan_contract
    assert VALIDATED_ROW_CITATIONS[stem] == ("6", "15")
    assert REQUIRED_UNITS[stem] == ("19.P4.provider-cooldown-failover", "19.P3.thresh-runtime")
    assert set(VALIDATED_DEPTH) == {u for units in REQUIRED_UNITS.values() for u in units}
    assert all(gap is None for gap in VALIDATED_DEPTH.values())
    assert all(parts == ("Owner", "Records", "Observable", "Tests") for parts in ENTRY_PARTS.values())
    assert all(len(digest) == 64 for digest in ENTRY_SHA.values())
    assert expected <= set(RESOLVED_CITATIONS)


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    stem = BATCH[1]
    expected = {"19.L", "19.I", "19.P4", "19.P4.reliability-battery",
                "19.P4.provider-cooldown-failover", "19.P4.reliability-run", "6", "13"}
    assert len(AUTHORING_HEAD) == len(IDIOM_BLOB) == 40
    assert VALIDATED_ROW_CITATIONS["reliability-battery"] == ("6",)
    assert expected <= set(RESOLVED_CITATIONS)
    assert set(RESOLVED_FUTURE_CITATIONS) <= set(RESOLVED_CITATIONS)
    assert REQUIRED_UNITS[stem] == ("19.P4.reliability-battery",
                                    "19.P4.provider-cooldown-failover", "19.P4.reliability-run")
    assert all(len(digest) == 64 for digest in RESOLVED_UNIT_SHA.values())
    for t in (_birth(stem), _ticket(stem)):
        assert set(t.plan_contract) == expected
        assert t.context == ("tests/test_seeded_phase3_core.py",)
        assert t.scope_fence == ("tickets", "tests/test_seeded_phase4_03.py")
        scope = t.sections["Scope in / Scope out"]
        for fact in ("admissions[3:]", "admissions[4:]", "phase4-continue-04", "medium/medium",
                     "entry_unit_gap", "resolve_plan_contract", "19.P4.reliability-run", "kind: spec_gap",
                     "fixed authoring snapshots", "re-author only snagged seeds", "checks.json"):
            assert fact in scope
        assert all(stem in scope for admission in UNSEEDED_SUFFIX for stem in admission)
        assert "tests/test_seeded_phase4_03.py" not in (*t.context, *t.on_demand)


@pytest.mark.parametrize("stem", BATCH)
def test_context_closure_and_max_effort_render_use_authoring_snapshots(stem):
    a = AUTHORED[stem]
    assert a["chars"] == len(AUTHORED_TEXT[stem])
    for t in (_birth(stem), _ticket(stem)):
        assert (t.context, t.on_demand) == (a["context"], a["on_demand"])
    assert set(a["fenced_existing"]) <= set(a["context"]) | set(a["on_demand"])
    assert set((*FENCE_FLOORS[stem], *FENCE_ADDITIONS[stem])) - {"tickets"} == (
        set(a["fenced_existing"]) | set(a["created"]))
    assert not set(a["context"]) & set(a["on_demand"])
    created = {p for sibling in BATCH for p in AUTHORED[sibling]["created"]}
    assert not created & set((*a["context"], *a["on_demand"]))
    assert not set(a["context"]) & set(DELIMITER_PATHS)
    assert not any(p.startswith("specs/") or p == "CHUPA_PLAN.md" for p in a["context"])
    assert all(FILE_CHARS[p] > 0 for p in (*a["context"], *a["on_demand"]))
    assert ACTUAL_BASE_RENDER_CHARS[stem] <= render_chars(stem) <= HEADROOM_CHARS == 300_000
    for path in set(a["on_demand"]) - set(DELIMITER_PATHS):
        assert render_chars(stem, (path,)) > HEADROOM_CHARS, path


def test_named_obligations_and_preservation_partition():
    assert len(ENTRY_TESTS) == 9 and len(set(ENTRY_TESTS)) == 9
    for t in (_birth(BATCH[0]), _ticket(BATCH[0])):
        scope = t.sections["Scope in / Scope out"]
        assert all(name in scope for name in ENTRY_TESTS)
        assert all(name in scope for name in PREDECESSOR_ACTIVATION.values())
        assert "existing drain/serve production graph" in scope
        assert "no cap, diagnosis, escalation ladder or Reject arrival" in scope
        assert "before the LLM effect" in scope and "before releasing the lock" in scope
        assert "excluded from both ticket time and watchdog regions" in scope
        commands = {arg for argv in t.verification for arg in argv}
        assert set(PRESERVATION) <= commands
        assert not set(PRESERVATION) & set((*t.scope_fence, *t.context, *t.on_demand))
        assert {"tests/test_provider_cooldown_failover.py", "tests/test_providers.py",
                "tests/test_thresh.py", "tests/test_restart_timers.py", "tests/test_stages.py",
                "tests/test_serve.py", "tests/test_merge.py", "tests/test_mergequeue.py",
                "tests/test_daemon_composition.py", "tests/test_watchdog.py"} <= commands


def test_approved_provider_seed_is_preserved_verbatim():
    import hashlib

    stem = PAYLOADS[0]
    digest = APPROVED_SEED_SHA256[stem]
    assert hashlib.sha256(AUTHORED_TEXT[stem].encode()).hexdigest() == digest
    assert hashlib.sha256((ROOT / ticket_path(stem)).read_bytes()).hexdigest() == digest
