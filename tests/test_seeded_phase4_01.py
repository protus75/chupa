"""Phase 4 admission 01: permanent authoring snapshots, never live render arithmetic."""
from pathlib import Path

import pytest

from chupa.config import load_config
from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent

# Run-context caller additions are earned below. Constructor-only fixtures and
# historical seeding snapshots retain their existing contracts unchanged.
AUTHORING_HEAD = '676f4c0c42a970fc9b263382cb0c74c8a4801ddc'

IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

PAYLOADS = ('watchdog-detector', 'watchdog-activation')

BATCH = ('watchdog-detector', 'watchdog-activation', 'phase4-continue-02')

NEXT_ADMISSION = ('provider-cooldown-failover',)

UNSEEDED_SUFFIX = (('provider-cooldown-failover',), ('reliability-battery',), ('reliability-run',), ('phase4-exit',))

EDGES = {'watchdog-detector': ('phase4-continue',),
 'watchdog-activation': ('phase4-continue', 'watchdog-detector'),
 'phase4-continue-02': ('watchdog-detector', 'watchdog-activation')}

FENCE_FLOORS = {'watchdog-detector': ('chupa/watchdog.py', 'chupa/notify.py', 'tests/test_watchdog.py'),
 'watchdog-activation': ('chupa/watchdog.py',
                         'chupa/driver.py',
                         'chupa/stages.py',
                         'chupa/notify.py',
                         'chupa/drain.py',
                         'chupa/serve.py',
                         'chupa/__main__.py',
                         'tests/test_watchdog.py',
                         'tests/test_watchdog_activation.py',
                         'tests/test_daemon_composition.py',
                         'eval/shakeout/providers.py',
                         'eval/daemon_soak.py'),
 'phase4-continue-02': ('tickets', 'tests/test_seeded_phase4_02.py')}

FENCE_ADDITIONS = {'watchdog-detector': {},
 'watchdog-activation': {'chupa/author.py': '19.L rule 5: direct Driver.run caller at lines '
                                            '(155,); supply the revised expected/stuck and scope '
                                            'run context while retaining existing assertions.',
                         'chupa/rework.py': '19.L rule 5: direct Driver.run caller at lines '
                                            '(161,); supply the revised expected/stuck and scope '
                                            'run context while retaining existing assertions.',
                         'chupa/triage.py': '19.L rule 5: direct Driver.run caller at lines '
                                            '(163,); supply the revised expected/stuck and scope '
                                            'run context while retaining existing assertions.',
                         'eval/diagnose.py': '19.L rule 5: direct Driver.run caller at lines '
                                             '(175,); supply the revised expected/stuck and scope '
                                             'run context while retaining existing assertions.',
                         'eval/harness.py': '19.L rule 5: direct Driver.run caller at lines '
                                            '(185,); supply the revised expected/stuck and scope '
                                            'run context while retaining existing assertions.',
                         'tests/test_driver.py': '19.L rule 5: direct Driver.run caller at lines '
                                                 '(111, 172); supply the revised expected/stuck '
                                                 'and scope run context while retaining existing '
                                                 'assertions.',
                         'tests/test_echo_stage.py': '19.L rule 5: direct Driver.run caller at '
                                                     'lines (86,); supply the revised '
                                                     'expected/stuck and scope run context while '
                                                     'retaining existing assertions.',
                         'tests/test_kill_executor_abort.py': '19.L rule 5: direct Driver.run '
                                                              'caller at lines (84,); supply the '
                                                              'revised expected/stuck and scope '
                                                              'run context while retaining '
                                                              'existing assertions.',
                         'tests/test_kill_failure_suppression.py': '19.L rule 5: direct Driver.run '
                                                                   'caller at lines (261,); supply '
                                                                   'the revised expected/stuck and '
                                                                   'scope run context while '
                                                                   'retaining existing assertions.',
                         'tests/test_llm_effect.py': '19.L rule 5: direct Driver.run caller at '
                                                     'lines (81,); supply the revised '
                                                     'expected/stuck and scope run context while '
                                                     'retaining existing assertions.',
                         'tests/test_providers.py': '19.L rule 5: direct Driver.run caller at '
                                                    'lines (549, 581); supply the revised '
                                                    'expected/stuck and scope run context while '
                                                    'retaining existing assertions.',
                         'tests/test_requisition.py': '19.L rule 5: direct Driver.run caller at '
                                                      'lines (183,); supply the revised '
                                                      'expected/stuck and scope run context while '
                                                      'retaining existing assertions.',
                         'tests/test_serve.py': '19.L rule 5: direct Driver.run caller at lines '
                                                '(385,); supply the revised expected/stuck and '
                                                'scope run context while retaining existing '
                                                'assertions.',
                         'chupa/runner.py': 'Section 9 seam-owner closure: bind constructs the '
                                            'production Driver/LLM; harvest_failure owns timeout '
                                            'harvest and cleanup ordering.',
                         'chupa/requisition.py': '19.L rule 5: review_ticket invokes llm_call '
                                                 'through Driver.race outside Driver.run; bind '
                                                 'nested and standalone requisition calls to the '
                                                 'watched run context.'},
 'phase4-continue-02': {}}

HEADROOM_CHARS = 300000

IMPLEMENT_SPEC_CHARS = 4775

RENDER_OVERHEAD = 2000

PLAN_CHARS = {'19.I': 1811,
 '19.P4.watchdog-detector': 6418,
 '9': 20021,
 '19.P4.watchdog-event-stream': 3441,
 '19.P4.notify-transport': 4362,
 '19.P4.watchdog-activation': 4320,
 '19.L': 20912,
 '19.P4': 5514,
 '19.P4.provider-cooldown-failover': 8157,
 '19.P3.thresh-runtime': 12153,
 '6': 38005,
 '15': 17104,
 '13': 19807}

FILE_CHARS = {'chupa/watchdog.py': 402,
 'chupa/notify.py': 5815,
 'tests/test_watchdog.py': 7006,
 'chupa/providers.py': 19824,
 'chupa/seams.py': 8532,
 'chupa/driver.py': 16659,
 'tests/test_daemon_composition.py': 90814,
 'chupa/stages.py': 59184,
 'chupa/drain.py': 31622,
 'chupa/serve.py': 20554,
 'chupa/__main__.py': 12439,
 'chupa/author.py': 9686,
 'chupa/rework.py': 12275,
 'chupa/triage.py': 9981,
 'eval/diagnose.py': 10318,
 'eval/harness.py': 19319,
 'tests/test_driver.py': 16561,
 'tests/test_echo_stage.py': 4243,
 'tests/test_kill_executor_abort.py': 11416,
 'tests/test_kill_failure_suppression.py': 19486,
 'tests/test_llm_effect.py': 8306,
 'tests/test_providers.py': 34178,
 'tests/test_requisition.py': 11392,
 'tests/test_serve.py': 75217,
 'chupa/runner.py': 35603,
 'chupa/requisition.py': 8155,
 'tests/test_seeded_phase3_core.py': 5425,
 'chupa/thresh.py': 9737,
 'eval/shakeout/providers.py': 5732,
 'eval/daemon_soak.py': 35654}

AUTHORED = {'watchdog-detector': {'chars': 3857,
                       'plan': ('19.I',
                                '19.P4.watchdog-detector',
                                '9',
                                '19.P4.watchdog-event-stream',
                                '19.P4.notify-transport'),
                       'context': ('chupa/watchdog.py',
                                   'chupa/notify.py',
                                   'tests/test_watchdog.py',
                                   'chupa/providers.py',
                                   'chupa/seams.py',
                                   'chupa/driver.py',
                                   'chupa/thresh.py',
                                   'tests/test_daemon_composition.py'),
                       'on_demand': (),
                       'fenced_existing': ('chupa/watchdog.py',
                                           'chupa/notify.py',
                                           'tests/test_watchdog.py'),
                       'created': (),
                       'expected': 60,
                       'stuck': 90},
 'watchdog-activation': {'chars': 7459,
                         'plan': ('19.I',
                                  '19.P4.watchdog-activation',
                                  '9',
                                  '19.P4.watchdog-detector',
                                  '19.P4.watchdog-event-stream',
                                  '19.P4.notify-transport'),
                         'context': ('chupa/watchdog.py',
                                     'chupa/driver.py',
                                     'chupa/notify.py',
                                     'chupa/drain.py',
                                     'chupa/serve.py',
                                     'chupa/__main__.py',
                                     'tests/test_watchdog.py',
                                     'chupa/author.py',
                                     'chupa/rework.py',
                                     'chupa/triage.py',
                                     'eval/diagnose.py',
                                     'eval/harness.py',
                                     'tests/test_driver.py',
                                     'tests/test_echo_stage.py',
                                     'tests/test_kill_executor_abort.py',
                                     'tests/test_kill_failure_suppression.py',
                                     'tests/test_llm_effect.py',
                                     'tests/test_requisition.py',
                                     'chupa/requisition.py',
                                     'eval/shakeout/providers.py'),
                         'on_demand': ('tests/test_daemon_composition.py',
                                       'tests/test_serve.py',
                                       'chupa/stages.py',
                                       'chupa/runner.py',
                                       'tests/test_providers.py',
                                       'eval/daemon_soak.py'),
                         'fenced_existing': ('chupa/watchdog.py',
                                             'chupa/driver.py',
                                             'chupa/stages.py',
                                             'chupa/notify.py',
                                             'chupa/drain.py',
                                             'chupa/serve.py',
                                             'chupa/__main__.py',
                                             'tests/test_watchdog.py',
                                             'tests/test_daemon_composition.py',
                                             'chupa/author.py',
                                             'chupa/rework.py',
                                             'chupa/triage.py',
                                             'eval/diagnose.py',
                                             'eval/harness.py',
                                             'tests/test_driver.py',
                                             'tests/test_echo_stage.py',
                                             'tests/test_kill_executor_abort.py',
                                             'tests/test_kill_failure_suppression.py',
                                             'tests/test_llm_effect.py',
                                             'tests/test_providers.py',
                                             'tests/test_requisition.py',
                                             'tests/test_serve.py',
                                             'chupa/runner.py',
                                             'chupa/requisition.py',
                                             'eval/shakeout/providers.py',
                                             'eval/daemon_soak.py'),
                         'created': ('tests/test_watchdog_activation.py',),
                         'expected': 60,
                         'stuck': 90},
 'phase4-continue-02': {'chars': 4976,
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P4',
                                 '19.P4.provider-cooldown-failover',
                                 '19.P3.thresh-runtime',
                                 '6',
                                 '15',
                                 '13'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fenced_existing': (),
                        'created': ('tests/test_seeded_phase4_02.py',),
                        'expected': 60,
                        'stuck': 90}}

ACTUAL_BASE_RENDER_CHARS = {'watchdog-detector': 203621, 'watchdog-activation': 288494, 'phase4-continue-02': 138621}

VALIDATED_ENTRIES = ('19.P4.watchdog-detector',
 '19.P4.watchdog-activation',
 '19.P4.watchdog-event-stream',
 '19.P4.notify-transport')

ENTRY_SHA = {'19.P4.watchdog-detector': '1d47af7c04bcd83df10567eef5673a59ca505ed183204a6e1b434e8ee9f6be82',
 '19.P4.watchdog-activation': 'ce93e98a38609216e5e29868311e0401627eabcf6321dcf73018a0197d67c63a',
 '19.P4.watchdog-event-stream': '96be0fcf025e1a70e73ab03aa16357837b493ccfe02086a29b8c14e63b4737ae',
 '19.P4.notify-transport': 'bd1848308625e1744bedf3f5b287f156cb0e4ff0f0cd9bac42b7ff223d697e63'}

ENTRY_PARTS = {'19.P4.watchdog-detector': ('Owner', 'Records', 'Observable', 'Tests'),
 '19.P4.watchdog-activation': ('Owner', 'Records', 'Observable', 'Tests'),
 '19.P4.watchdog-event-stream': ('Owner', 'Records', 'Observable', 'Tests'),
 '19.P4.notify-transport': ('Owner', 'Records', 'Observable', 'Tests')}

ENTRY_TESTS = {'watchdog-detector': ('test_spend_resets_only_on_observed_scope_mutation',
                       'test_spend_metering_and_threshold',
                       'test_watchdog_regions_and_notify_once',
                       'test_watchdog_hard_timeout_group_cleanup',
                       'test_detector_is_dormant',
                       'test_spiral_corpus'),
 'watchdog-activation': ('test_every_production_driver_surface_is_watched',
                         'test_production_soft_band_notifies_once_without_kill',
                         'test_production_hard_timeout_group_kill_is_harvested',
                         'test_production_watchdog_shares_active_executor')}

PRESERVATION = {'watchdog-detector': ('tests/test_notify.py',),
 'watchdog-activation': ('tests/test_drain.py',
                         'tests/test_stages.py',
                         'tests/test_merge.py',
                         'tests/test_mergequeue.py',
                         'tests/test_seed_path.py',
                         'tests/test_eval_harness.py',
                         'tests/test_diagnose_eval.py',
                         'tests/test_storm_notification_activation.py',
                         'tests/test_effects.py',
                         'tests/test_notify.py')}

CALLER_SNAPSHOT = {'chupa/author.py': (155,),
 'chupa/rework.py': (161,),
 'chupa/stages.py': (318, 536, 1138),
 'chupa/triage.py': (163,),
 'eval/diagnose.py': (175,),
 'eval/harness.py': (185,),
 'tests/test_daemon_composition.py': (667,),
 'tests/test_driver.py': (111, 172),
 'tests/test_echo_stage.py': (86,),
 'tests/test_kill_executor_abort.py': (84,),
 'tests/test_kill_failure_suppression.py': (261,),
 'tests/test_llm_effect.py': (81,),
 'tests/test_providers.py': (549, 581),
 'tests/test_requisition.py': (183,),
 'tests/test_serve.py': (385,),
 'tests/test_watchdog.py': (143,)}

DELIMITER_PATHS = ('eval/daemon_soak.py',)

AUTHORED_TEXT = {
    'watchdog-detector': """---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase4-continue

## Context
- chupa/watchdog.py
- chupa/notify.py
- tests/test_watchdog.py
- chupa/providers.py
- chupa/seams.py
- chupa/driver.py
- chupa/thresh.py
- tests/test_daemon_composition.py

## Plan contract
- 19.I
- 19.P4.watchdog-detector
- section 9
- 19.P4.watchdog-event-stream
- 19.P4.notify-transport

## Goal / Why
Prove dormant deterministic spend/progress detection and hard-deadline cleanup.

## Scope in / Scope out
Construct only the detector. The cited entry supplies Owner, Records, Observable and Tests; chupa/watchdog.py owns deterministic spend/progress and time-region decisions, and chupa/notify.py retains notification custody. Consume the merged event stream and transport through injected seams. Keep production calls unwatched until watchdog-activation and preserve existing public notification signatures, spool capture and harvest behavior.

Prove real scope-path changes rather than tool requests, plan-unit range confinement and progress observation in each time region. Exercise duplicate-event accounting, optional usage, call-start estimate charging even for hung calls, strict threshold crossing and the existing missing-cost refusal. Follow the entry's first-completed-call basis and calibration rule; never derive the active basis from its own spend. test_spend_metering_and_threshold must assert the exact 1, 2, 0.5 USD sequence, equality at 3 and crossing at 3.5, identity-local bases, zero basis, re-prompt/progress retention and new-run reset. A hung calibration remains subject to the hard deadline. Prove warning retention through progress/retries, fresh-run warning identity, cap-wait exclusion, unset notification behavior, synchronous abort before cancellation and awaited cleanup. Cap-wait exclusion consumes the existing chupa/thresh.py Admission.waited_seconds / provider_cap_wait record through an injected seam, with no change to thresh.py; it remains outside the fence. Pin the corpus adapter-event fixtures inline as Python literals in tests/test_watchdog.py, with expected verdicts; no standalone fixture files or model judge.

Named obligations: test_spend_resets_only_on_observed_scope_mutation, test_spend_metering_and_threshold, test_watchdog_regions_and_notify_once, test_watchdog_hard_timeout_group_cleanup, test_detector_is_dormant, test_spiral_corpus. test_detector_is_dormant must discriminate the real production composition and fail if detection is wired. Reuse CoreRig from tests/test_daemon_composition.py as a read-only reference, never a substitute production graph. Run tests/test_notify.py unchanged as a preservation suite, outside the fence and Context.

Read Context and the governing entries before editing. Out: activation, provider cooldown/selection, new config or durable records, altered notification keys, second spool writers, historical seeding fixtures and ticket/plan edits.

## Scope fence
- chupa/watchdog.py
- chupa/notify.py
- tests/test_watchdog.py

## Acceptance criteria
1. `uv run pytest tests/test_watchdog.py tests/test_notify.py` exits 0 proving all six named detector obligations: scope mutation, metering, time regions, warning identity, abort cleanup and corpus replay.
2. `uv run pytest tests/test_watchdog.py tests/test_notify.py` exits 0 proving production dormancy and unchanged stream/transport behavior.

## Verification
```
uv run pytest tests/test_watchdog.py tests/test_notify.py
```

## Definition of rejected
Missing or contradictory governing facts return premise_failed, kind: spec_gap, naming the owning cited entry. A criteria-forced path outside the earned fence returns premise_failed; repair the contract or closure rather than invent facts or extend the registry.

## Time budget
- expected: 60m
- stuck: 90m

""",
    'watchdog-activation': """---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase4-continue
- watchdog-detector

## Context
- chupa/watchdog.py
- chupa/driver.py
- chupa/notify.py
- chupa/drain.py
- chupa/serve.py
- chupa/__main__.py
- tests/test_watchdog.py
- chupa/author.py
- chupa/rework.py
- chupa/triage.py
- eval/diagnose.py
- eval/harness.py
- tests/test_driver.py
- tests/test_echo_stage.py
- tests/test_kill_executor_abort.py
- tests/test_kill_failure_suppression.py
- tests/test_llm_effect.py
- tests/test_requisition.py
- chupa/requisition.py
- eval/shakeout/providers.py

## On-demand
- tests/test_daemon_composition.py
- tests/test_serve.py
- chupa/stages.py
- chupa/runner.py
- tests/test_providers.py
- eval/daemon_soak.py

## Plan contract
- 19.I
- 19.P4.watchdog-activation
- section 9
- 19.P4.watchdog-detector
- 19.P4.watchdog-event-stream
- 19.P4.notify-transport

## Goal / Why
Watch every production model call and prove warnings and harvested timeout through production composition.

## Scope in / Scope out
Activate the detector for every production model-call route, including Implement, review, rework, diagnosis, Author, triage and requisition review; future retro calls inherit this watched composition. The cited entry supplies Owner, Records, Observable and Tests. chupa/watchdog.py owns the watched LLM path, chupa/driver.py the run lifetime, chupa/stages.py ticket metadata and chupa/runner.py production binding and harvest custody. Keep Driver constructor/from_config arity, LLMRequest/LLMResult and LLM effect signatures unchanged. Extend the run-call interface to carry expected/stuck budgets and writable scope context; migrate every direct Driver.run caller in the fenced production, eval and test files in this commit. Ticketless calls use their real surface/run sequence and no writable output fence. No compatibility layer or unwatched production route is allowed.

chupa/requisition.py makes a separate llm_call through Driver.race; bind this path to the watched context too, including nested Author/Rework reviews, preserving its effect identity and failure semantics. Keep production serving identity/cost, Implement-only write grants and classification/routing behavior intact. No provider registry or threshold activation belongs here.

Named obligations: test_every_production_driver_surface_is_watched, test_production_soft_band_notifies_once_without_kill, test_production_hard_timeout_group_kill_is_harvested, test_production_watchdog_shares_active_executor. Reuse the real production graph from tests/test_daemon_composition.py and tests/test_serve.py with injected time and adapter events. Exercise every surface, retries, repeated calls and fresh run boundaries. Prove the soft warning's notify intent/completion pair, suppression after retrips/progress and a distinct next-run key, without auto-kill. Prove a hung real child and descendant are group-killed and reaped, the existing timeout result survives, and the existing runner lifts its harvest before deleting the worktree. Tests must not write their own harvest or checks.json evidence.

Transition fixtures: migrate tests/test_watchdog.py::test_event_stream_is_dormant and the sibling detector's test_detector_is_dormant to activated expectations, retaining their discriminating probes and stream/detector assertions. Preserve tests/test_providers.py::test_cli_failure_classifier_is_dormant until provider failover. Preserve merged serve partitioning, existing task/worker counts, and startup/poll notification reconciliation. Revised caller fixtures retain all effect replay, timeout, write-grant, classification, independent kill and failure-suppression assertions. Constructor-only fixtures do not earn fence additions.

Read Context and each On-demand file before editing; read predecessor tickets and grep callers, allowlists and negatives across chupa/, eval/ and tests/. Existing files are partitioned solely by measured headroom; the new tests/test_watchdog_activation.py is never Context. tests/test_notify.py and the other unfenced Verification suites are unchanged preservation obligations. Watched call and abort share the executor that spawned the child; notification and self-upgrade executors remain independent. Retain hold/control behavior, failure-spine ordering, redaction, capture and cleanup. Out: new terminals/signals/reports, provider failover, live-state reads, hand-authored receipts, historical seeding fixtures and ticket/plan edits.

## Scope fence
- chupa/watchdog.py
- chupa/driver.py
- chupa/stages.py
- chupa/notify.py
- chupa/drain.py
- chupa/serve.py
- chupa/__main__.py
- tests/test_watchdog.py
- tests/test_watchdog_activation.py
- tests/test_daemon_composition.py
- eval/shakeout/providers.py
- eval/daemon_soak.py
- chupa/author.py
- chupa/rework.py
- chupa/triage.py
- eval/diagnose.py
- eval/harness.py
- tests/test_driver.py
- tests/test_echo_stage.py
- tests/test_kill_executor_abort.py
- tests/test_kill_failure_suppression.py
- tests/test_llm_effect.py
- tests/test_providers.py
- tests/test_requisition.py
- tests/test_serve.py
- chupa/runner.py
- chupa/requisition.py

## Acceptance criteria
1. `uv run pytest tests/test_watchdog.py tests/test_watchdog_activation.py tests/test_daemon_composition.py tests/test_notify.py` exits 0 proving all four named activation obligations through real production composition, every surface/run context, soft warning once and harvested hard-timeout cleanup.
2. `uv run pytest tests/test_watchdog.py tests/test_watchdog_activation.py tests/test_daemon_composition.py tests/test_notify.py` exits 0 migrating predecessor dormancy fixtures while retaining identity/cost, grants, independent executors, hold/control and stream/detector/transport behavior.
3. `uv run pytest tests/test_driver.py tests/test_echo_stage.py tests/test_kill_executor_abort.py tests/test_kill_failure_suppression.py tests/test_llm_effect.py tests/test_providers.py tests/test_requisition.py tests/test_serve.py` exits 0 retaining revised caller assertions; `uv run pytest tests/test_drain.py tests/test_stages.py tests/test_merge.py tests/test_mergequeue.py tests/test_seed_path.py tests/test_eval_harness.py tests/test_diagnose_eval.py tests/test_storm_notification_activation.py tests/test_effects.py tests/test_notify.py` exits 0 preserving unfenced suites unchanged.

## Verification
```
uv run pytest tests/test_watchdog.py tests/test_watchdog_activation.py tests/test_daemon_composition.py tests/test_notify.py
uv run pytest tests/test_driver.py tests/test_echo_stage.py tests/test_kill_executor_abort.py tests/test_kill_failure_suppression.py tests/test_llm_effect.py tests/test_providers.py tests/test_requisition.py tests/test_serve.py
uv run pytest tests/test_drain.py tests/test_stages.py tests/test_merge.py tests/test_mergequeue.py tests/test_seed_path.py tests/test_eval_harness.py tests/test_diagnose_eval.py tests/test_storm_notification_activation.py tests/test_effects.py tests/test_notify.py
uv run pytest tests/test_shakeout.py tests/test_daemon_soak.py tests/test_daemon_soak_runner.py
```

## Definition of rejected
Missing or contradictory governing facts return premise_failed, kind: spec_gap, naming the owning cited entry. A criteria-forced path outside the earned fence returns premise_failed; repair the contract or closure rather than invent facts or extend the registry.

## Time budget
- expected: 60m
- stuck: 90m

""",
    'phase4-continue-02': """---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- watchdog-detector
- watchdog-activation

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P4
- 19.P4.provider-cooldown-failover
- 19.P3.thresh-runtime
- section 6
- section 15
- section 13

## Goal / Why
Author the deep provider admission and its successor for Check to review and lift.

## Scope in / Scope out
Parse BEGIN_REGISTRY_P4 through END_REGISTRY_P4 directly from committed CHUPA_PLAN.md. Position 02 carries admissions[2:]: [provider-cooldown-failover], [reliability-battery], [reliability-run], [phase4-exit]. Author only provider-cooldown-failover and phase4-continue-03. The successor carries admissions[3:] and depends on the payload; the payload depends on phase4-continue-02. Never rename, reorder, split, omit or add a row or author a later admission. This deep payload starts high/high on 19.L's known-deep evidence; the successor starts medium/medium. Bound each stuck budget by drain.max_ticket_minutes and the batch by seeding.max_seeds_per_admission.

Before authoring, run entry_unit_gap on 19.P4.provider-cooldown-failover and the required 19.P3.thresh-runtime. Run resolve_plan_contract for each needed entry, row citation and seeder-role contract against the merged plan. Missing or contradictory facts return premise_failed, kind: spec_gap, naming the owning entry; never invent facts or copy plan prose. The payload cites 19.I, its own entry, sections 6 and 15 and 19.P3.thresh-runtime as required by its Owner. The successor cites 19.L, 19.I, 19.P4, section 13 and every entry/row citation needed to author its next admission. Required future citation resolution cannot be omitted; future payload entry depth is validated by its owning pass, not preemptively for uncited later admissions.

Read row owners, predecessor tickets, direct callers and named tests. Grep public signatures, constructor/composition sites, allowlists and absence assertions across chupa/, eval/ and tests/. Earn additions only under 19.L rules 2-5 or cited seam-owner closure and pin exact path-specific reasons. Carry classifier/threshold predecessor dormancy fixtures, including tests/test_thresh.py, while preserving merged watchdog and serve behavior. Embed existing fenced paths unless measured headroom forces On-demand. Created paths, same-admission siblings, prompt specs and delimiter-bearing files never enter Context. Unchanged preservation suites belong only in Verification; historical seeding snapshots are immutable.

Use merged tests/test_seeded_phase3_core.py as the idiom. Create tests/test_seeded_phase4_02.py pinning the exact admission/successor, confirmed birth, intake grammar, edges, citation roles, needed entry depth, named obligations, earned fences and Context/On-demand partition. Record authoring head, idiom blob, ticket/file sizes and cited-unit lengths; max-effort base renders fit 300,000 characters using fixed authoring snapshots, never current sizes or plan lengths. Named tests: test_named_stems_cover_exactly_this_admission_and_successor, test_seed_passes_intake_lint_with_confirmed_seed_birth, test_dependencies_as_authored, test_stuck_budget_fits_the_drain_envelope, test_fence_contains_its_floor_and_only_earned_additions, test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract, test_successor_cites_next_admission_and_embeds_merged_earlier_idiom and test_context_closure_and_max_effort_render_use_authoring_snapshots.

Write new seeds directly and leave them uncommitted. Check owns requisition_review, this seeder's checks.json approvals and one ticket-plane seed lift. Keep approved bytes verbatim while ticket_sha matches; re-author only snagged seeds. Commit only the new batch test. Out: production implementation, existing tickets/run records, plan edits, Box messages, manual release, later admissions and historical test edits.

## Scope fence
- tickets
- tests/test_seeded_phase4_02.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase4_02.py` exits 0 proving exactly provider-cooldown-failover and phase4-continue-03, confirmed births, grammar, edges, bounded budgets, citation roles, entry depth, named obligations, earned closure and fixed-snapshot renders.
2. `tickets/phase4-continue-02/checks.json` records each approval before one ticket-plane seed lift; the code commit contains only the new batch test.
3. `uv run pytest -q` exits 0 preserving merged behavior and historical seeding snapshots.

## Verification
```
uv run pytest -q tests/test_seeded_phase4_02.py
uv run pytest -q
```

## Definition of rejected
Missing or contradictory governing facts return premise_failed, kind: spec_gap, naming the owning cited entry. A criteria-forced path outside the earned fence returns premise_failed; repair the contract or closure rather than invent facts or extend the registry.

## Time budget
- expected: 60m
- stuck: 90m

""",
}

VALIDATED_ROW_CITATIONS = {'watchdog-detector': ('9',), 'watchdog-activation': ('9',)}

REGISTRY_ADMISSIONS = (('watchdog-event-stream', 'notify-transport'),
 ('watchdog-detector', 'watchdog-activation'),
 ('provider-cooldown-failover',),
 ('reliability-battery',),
 ('reliability-run',),
 ('phase4-exit',))

APPROVED_SEED_SHA256 = {'watchdog-activation': '3a6ddbcf099ab17db2bcf64854dc37b8f2880003c8949ef9211d5a4525fa7b29',
 'phase4-continue-02': 'b15687e4f69040ff04d1f72d44ea9dc1d2b5e0c438e8fbf78ec1ae309d450a53'}

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
    assert PAYLOADS == ("watchdog-detector", "watchdog-activation")
    assert BATCH == (*PAYLOADS, "phase4-continue-02")
    assert len(set(BATCH)) == 3 <= load_config(None, cwd=ROOT).seeding.max_seeds_per_admission
    assert set(EDGES) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(AUTHORED) == set(BATCH)
    assert set(AUTHORED_TEXT) == set(ACTUAL_BASE_RENDER_CHARS) == set(BATCH)


@pytest.mark.parametrize("stem", BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    birth, live = _birth(stem).frontmatter, _ticket(stem).frontmatter
    assert (birth.source, birth.state) == ("seed", "confirmed")
    assert live.source == "seed" and live.state in {"confirmed", "rejected"}
    assert (birth.agent_tier, birth.agent_effort) == ("medium", "medium")
    assert (live.agent_tier, live.agent_effort) == ("medium", "medium")
    assert birth.kind == "feature" and birth.priority == "P1" and not birth.gate_bypass


def test_dependencies_as_authored():
    assert EDGES == {"watchdog-detector": ("phase4-continue",),
                     "watchdog-activation": ("phase4-continue", "watchdog-detector"),
                     "phase4-continue-02": PAYLOADS}
    for stem in BATCH:
        assert _birth(stem).depends == _ticket(stem).depends == EDGES[stem]


@pytest.mark.parametrize("stem", BATCH)
def test_stuck_budget_fits_the_drain_envelope(stem):
    for t in (_birth(stem), _ticket(stem)):
        assert t.expected_minutes == AUTHORED[stem]["expected"] == 60
        assert t.stuck_minutes == AUTHORED[stem]["stuck"] == 90
        assert t.stuck_minutes <= load_config(None, cwd=ROOT).drain.max_ticket_minutes


@pytest.mark.parametrize("stem", BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    fence = (*FENCE_FLOORS[stem], *FENCE_ADDITIONS[stem])
    assert _birth(stem).scope_fence == _ticket(stem).scope_fence == fence
    assert all(reason.startswith(("19.L rule 5:", "Section 9 seam-owner closure:"))
               for reason in FENCE_ADDITIONS[stem].values())
    if stem == "watchdog-activation":
        assert set(CALLER_SNAPSHOT) <= set(fence)
        assert {"chupa/requisition.py", "chupa/runner.py"} <= set(FENCE_ADDITIONS[stem])
        for t in (_birth(stem), _ticket(stem)):
            scope = t.sections["Scope in / Scope out"]
            for negative in ("test_event_stream_is_dormant", "test_detector_is_dormant"):
                assert negative in scope and "tests/test_watchdog.py" in fence
            assert "test_cli_failure_classifier_is_dormant" in scope
            assert "Driver constructor/from_config arity" in scope
            assert "merged serve partitioning" in scope
    else:
        assert FENCE_ADDITIONS[stem] == {}


@pytest.mark.parametrize("stem", PAYLOADS)
def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract(stem):
    expected = ("19.I", f"19.P4.{stem}", "9",
                *(("19.P4.watchdog-detector",) if stem == "watchdog-activation" else ()),
                "19.P4.watchdog-event-stream", "19.P4.notify-transport")
    for t in (_birth(stem), _ticket(stem)):
        assert t.plan_contract == AUTHORED[stem]["plan"] == expected
        assert "19.P4" not in t.plan_contract and "19.L" not in t.plan_contract
        assert all(name in t.sections["Scope in / Scope out"] for name in ENTRY_TESTS[stem])
    assert set(ENTRY_SHA) == set(ENTRY_PARTS) == set(VALIDATED_ENTRIES)
    assert all(parts == ("Owner", "Records", "Observable", "Tests") for parts in ENTRY_PARTS.values())
    assert all(len(sha) == 64 for sha in ENTRY_SHA.values())
    assert all(PLAN_CHARS[uid] > 0 for uid in VALIDATED_ENTRIES)


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    assert NEXT_ADMISSION == ("provider-cooldown-failover",)
    assert UNSEEDED_SUFFIX == (NEXT_ADMISSION, ("reliability-battery",),
                               ("reliability-run",), ("phase4-exit",))
    assert len(AUTHORING_HEAD) == len(IDIOM_BLOB) == 40
    for t in (_birth("phase4-continue-02"), _ticket("phase4-continue-02")):
        assert t.plan_contract == ("19.L", "19.I", "19.P4", "19.P4.provider-cooldown-failover",
                                   "19.P3.thresh-runtime", "6", "15", "13")
        assert t.context == ("tests/test_seeded_phase3_core.py",)
        scope = t.sections["Scope in / Scope out"]
        for required in ("admissions[2:]", "admissions[3:]", "phase4-continue-03", "entry_unit_gap",
                         "resolve_plan_contract", "kind: spec_gap", "high/high", "medium/medium",
                         "tests/test_thresh.py", "fixed authoring snapshots", "re-author only snagged seeds"):
            assert required in scope
        assert all(name in scope for admission in UNSEEDED_SUFFIX for name in admission)
        assert "tests/test_seeded_phase4_02.py" not in (*t.context, *t.on_demand)


@pytest.mark.parametrize("stem", BATCH)
def test_context_closure_and_max_effort_render_use_authoring_snapshots(stem):
    a = AUTHORED[stem]
    assert a["chars"] == len(AUTHORED_TEXT[stem])
    for t in (_birth(stem), _ticket(stem)):
        assert t.context == a["context"] and t.on_demand == a["on_demand"]
    assert set(a["fenced_existing"]) <= set(a["context"]) | set(a["on_demand"])
    assert set((*FENCE_FLOORS[stem], *FENCE_ADDITIONS[stem])) - {"tickets"} == (
        set(a["fenced_existing"]) | set(a["created"]))
    assert not set(a["context"]) & set(a["on_demand"])
    created = {path for sibling in BATCH for path in AUTHORED[sibling]["created"]}
    assert not created & set((*a["context"], *a["on_demand"]))
    assert not set(a["context"]) & set(DELIMITER_PATHS)
    assert not any(p.startswith("specs/") or p == "CHUPA_PLAN.md" for p in a["context"])
    assert all(FILE_CHARS[p] > 0 for p in (*a["context"], *a["on_demand"]))
    assert ACTUAL_BASE_RENDER_CHARS[stem] <= render_chars(stem) <= HEADROOM_CHARS == 300_000
    for path in set(a["on_demand"]) - set(DELIMITER_PATHS):
        assert render_chars(stem, (path,)) > HEADROOM_CHARS, path


@pytest.mark.parametrize("stem", PAYLOADS)
def test_named_obligations_and_preservation_partition(stem):
    for t in (_birth(stem), _ticket(stem)):
        assert all(name in t.sections["Scope in / Scope out"] for name in ENTRY_TESTS[stem])
        commands = {arg for argv in t.verification for arg in argv}
        assert set(PRESERVATION[stem]) <= commands
        assert not set(PRESERVATION[stem]) & set((*t.scope_fence, *t.context, *t.on_demand))
        assert "tests/test_watchdog.py" in commands
        if stem == "watchdog-activation":
            assert {"tests/test_watchdog_activation.py", "tests/test_daemon_composition.py"} <= commands
            assert "real production graph" in t.sections["Scope in / Scope out"]
            assert "harvest before deleting the worktree" in t.sections["Scope in / Scope out"]
        else:
            assert "production composition" in t.sections["Scope in / Scope out"]


def test_detector_authoring_clears_prior_snags():
    for t in (_birth("watchdog-detector"), _ticket("watchdog-detector")):
        scope = t.sections["Scope in / Scope out"]
        assert "chupa/thresh.py" in t.context and "chupa/thresh.py" not in t.scope_fence
        assert "Admission.waited_seconds / provider_cap_wait" in scope
        assert "injected seam" in scope and "no change to thresh.py" in scope
        assert "inline as Python literals in tests/test_watchdog.py" in scope
        assert "no standalone fixture files" in scope
        assert "first-completed-call basis and calibration rule" in scope
        assert "1, 2, 0.5 USD" in scope and "equality at 3 and crossing at 3.5" in scope
        assert "hung calibration" in scope
    assert PLAN_CHARS["19.P4.watchdog-detector"] == 6418


def test_registry_rows_and_approved_seed_snapshots():
    import hashlib

    assert REGISTRY_ADMISSIONS[1] == PAYLOADS
    assert REGISTRY_ADMISSIONS[2:] == UNSEEDED_SUFFIX
    assert VALIDATED_ROW_CITATIONS == {stem: ("9",) for stem in PAYLOADS}
    for stem, digest in APPROVED_SEED_SHA256.items():
        assert hashlib.sha256(AUTHORED_TEXT[stem].encode()).hexdigest() == digest
