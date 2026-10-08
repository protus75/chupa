"""Phase 4 core authoring fixtures: sizes, contracts and partitions never remeasured.

Grammar still reads committed seed files; render arithmetic uses only this snapshot.
"""
from pathlib import Path

import pytest

from chupa.config import load_config
from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent

# The callback is absent for existing calls. No positional arguments, request/result
# records, constructor arity or production watched calls change in this admission.
# Direct provider/process and serve callers were read; no public-operation allowlist
# or negative assertion requires migration for this serve-only transport activation.

AUTHORING_HEAD = 'db6c6155065c189d24d59935aaa314a02b479b78'

IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

PAYLOADS = ('watchdog-event-stream', 'notify-transport')

BATCH = ('watchdog-event-stream', 'notify-transport', 'phase4-continue')

NEXT_ADMISSION = ('watchdog-detector', 'watchdog-activation')

UNSEEDED_SUFFIX = (('watchdog-detector', 'watchdog-activation'),
 ('provider-cooldown-failover',),
 ('reliability-battery',),
 ('reliability-run',),
 ('phase4-exit',))

EDGES = {'watchdog-event-stream': ('phase3-exit',),
 'notify-transport': ('phase3-exit', 'watchdog-event-stream'),
 'phase4-continue': ('watchdog-event-stream', 'notify-transport')}

FENCE_FLOORS = {'watchdog-event-stream': ('chupa/watchdog.py',
                           'chupa/providers.py',
                           'chupa/seams.py',
                           'tests/test_watchdog.py',
                           'tests/test_providers.py'),
 'notify-transport': ('chupa/notify.py',
                      'chupa/config.py',
                      'chupa/seams.py',
                      'chupa/serve.py',
                      'chupa/__main__.py',
                      'tests/test_notify.py',
                      'tests/test_config.py',
                      'tests/test_serve.py'),
 'phase4-continue': ('tickets', 'tests/test_seeded_phase4_01.py')}

FENCE_ADDITIONS = {'watchdog-event-stream': {}, 'notify-transport': {}, 'phase4-continue': {}}

HEADROOM_CHARS = 300000

IMPLEMENT_SPEC_CHARS = 4775

RENDER_OVERHEAD = 2000

PLAN_CHARS = {'19.I': 1811,
 '19.P4.watchdog-event-stream': 3441,
 '6': 38005,
 '9': 20021,
 '15': 17104,
 '19.P4.notify-transport': 4362,
 '13': 19807,
 '19.L': 20912,
 '19.P4': 5514,
 '19.P4.watchdog-detector': 4626,
 '19.P4.watchdog-activation': 4320}

FILE_CHARS = {'chupa/providers.py': 18857,
 'chupa/seams.py': 5551,
 'tests/test_providers.py': 27892,
 'chupa/llm.py': 2858,
 'chupa/driver.py': 16659,
 'chupa/runner.py': 35603,
 'chupa/redact.py': 1507,
 'chupa/config.py': 11901,
 'chupa/serve.py': 20113,
 'chupa/__main__.py': 11605,
 'tests/test_config.py': 9204,
 'tests/test_serve.py': 65939,
 'chupa/effects.py': 3229,
 'chupa/storm.py': 9850,
 'chupa/mergequeue.py': 16262,
 'tests/test_seeded_phase3_core.py': 5425}

AUTHORED = {'watchdog-event-stream': {'chars': 3782,
                           'plan': ('19.I', '19.P4.watchdog-event-stream', '6', '9', '15'),
                           'context': ('chupa/providers.py',
                                       'chupa/seams.py',
                                       'tests/test_providers.py',
                                       'chupa/llm.py',
                                       'chupa/driver.py',
                                       'chupa/runner.py',
                                       'chupa/redact.py'),
                           'on_demand': (),
                           'fenced_existing': ('chupa/providers.py',
                                               'chupa/seams.py',
                                               'tests/test_providers.py'),
                           'created': ('chupa/watchdog.py', 'tests/test_watchdog.py'),
                           'expected': 60,
                           'stuck': 90},
 'notify-transport': {'chars': 4780,
                      'plan': ('19.I', '19.P4.notify-transport', '6', '13', '15'),
                      'context': ('chupa/config.py',
                                  'chupa/seams.py',
                                  'chupa/serve.py',
                                  'chupa/__main__.py',
                                  'tests/test_config.py',
                                  'tests/test_serve.py',
                                  'chupa/effects.py',
                                  'chupa/providers.py',
                                  'chupa/redact.py',
                                  'chupa/storm.py',
                                  'chupa/mergequeue.py'),
                      'on_demand': (),
                      'fenced_existing': ('chupa/config.py',
                                          'chupa/seams.py',
                                          'chupa/serve.py',
                                          'chupa/__main__.py',
                                          'tests/test_config.py',
                                          'tests/test_serve.py'),
                      'created': ('chupa/notify.py', 'tests/test_notify.py'),
                      'expected': 60,
                      'stuck': 90},
 'phase4-continue': {'chars': 5826,
                     'plan': ('19.L',
                              '19.I',
                              '19.P4',
                              '19.P4.watchdog-detector',
                              '19.P4.watchdog-activation',
                              '19.P4.watchdog-event-stream',
                              '19.P4.notify-transport',
                              '9',
                              '13'),
                     'context': ('tests/test_seeded_phase3_core.py',),
                     'on_demand': (),
                     'fenced_existing': (),
                     'created': ('tests/test_seeded_phase4_01.py',),
                     'expected': 60,
                     'stuck': 90}}

AUTHORED_TEXT = {'watchdog-event-stream': '---\n'
                          'priority: P1\n'
                          'kind: feature\n'
                          'agent_tier: medium\n'
                          'agent_effort: medium\n'
                          'source: seed\n'
                          'state: confirmed\n'
                          '---\n'
                          '\n'
                          '## Depends on\n'
                          '- phase3-exit\n'
                          '\n'
                          '## Context\n'
                          '- chupa/providers.py\n'
                          '- chupa/seams.py\n'
                          '- tests/test_providers.py\n'
                          '- chupa/llm.py\n'
                          '- chupa/driver.py\n'
                          '- chupa/runner.py\n'
                          '- chupa/redact.py\n'
                          '\n'
                          '## Plan contract\n'
                          '- 19.I\n'
                          '- 19.P4.watchdog-event-stream\n'
                          '- section 6\n'
                          '- section 9\n'
                          '- section 15\n'
                          '\n'
                          '## Goal / Why\n'
                          'Deliver scrubbed adapter events to a directly constructed consumer '
                          'before the provider call ends.\n'
                          '\n'
                          '## Scope in / Scope out\n'
                          'Implement the watchdog-event-stream row only. The injected '
                          '19.P4.watchdog-event-stream contract supplies Owner, Records, '
                          'Observable and Tests. chupa/watchdog.py owns the new per-call consumer; '
                          'the existing process and adapter owners remain responsible for delivery '
                          'and capture. Build construction evidence against the production '
                          'provider and process seams while production Driver calls retain their '
                          'unwatched behavior.\n'
                          '\n'
                          "Carry the entry's named obligations: "
                          'test_event_consumer_receives_before_terminal, '
                          'test_event_consumer_preserves_tool_identity_and_optional_usage, '
                          'test_event_stream_is_dormant, '
                          'test_inflight_events_are_scrubbed_and_capture_is_preserved and '
                          'test_event_callback_unwind_kills_group. Exercise both provider shapes, '
                          'incomplete stdout chunks, stderr drainage and exceptional unwind '
                          'through the real process-group seam. Retain the provider tests for '
                          'results, estimates, stdin delivery, surface write grants and abort '
                          "binding. Run tests/test_git.py unchanged to preserve the process seam's "
                          'existing timeout, cancellation, spawn and inherited-stdio obligations; '
                          'it is a preservation suite, not an edit target.\n'
                          '\n'
                          'Read the production call chain and direct callers across chupa/, eval/ '
                          'and tests/ before editing. Inspect eval/harness.py, '
                          'eval/shakeout/providers.py and eval/daemon_soak.py from disk; '
                          "delimiter-bearing files cannot be embedded. The entry's absent callback "
                          "must preserve current callers' arguments and behavior; do not migrate "
                          'unrelated ProcessExec callers or change LLMRequest/LLMResult or '
                          'constructor arity. The existing fenced paths are embedded. No '
                          'additional caller, allowlist or contradicted dormancy edit was earned '
                          'at authoring. If implementing the entry actually forces another path, '
                          'return premise_failed naming that closure instead of adding a parallel '
                          'call path.\n'
                          '\n'
                          'Journal retains durable-event ownership; the provider retains spool '
                          'ownership. No detector, push, spend kill, polling of finished spools, '
                          'cleanup redesign, new persisted record or activation belongs here. '
                          'Later registry rows own those changes. Do not edit historical seeding '
                          'tests, tickets, the plan, live state or preservation suites.\n'
                          '\n'
                          '## Scope fence\n'
                          '- chupa/watchdog.py\n'
                          '- chupa/providers.py\n'
                          '- chupa/seams.py\n'
                          '- tests/test_watchdog.py\n'
                          '- tests/test_providers.py\n'
                          '\n'
                          '## Acceptance criteria\n'
                          '1. `uv run pytest tests/test_watchdog.py tests/test_providers.py` exits '
                          '0 proving the five named entry obligations through the actual '
                          'provider/process seams, including delivery before completion and '
                          'scrubbed capture parity.\n'
                          '2. `uv run pytest tests/test_watchdog.py tests/test_providers.py` exits '
                          '0 proving production dormancy and unchanged results, optional usage, '
                          'tool identities, stdin, grants and abort behavior.\n'
                          '3. `uv run pytest tests/test_git.py` exits 0 preserving group cleanup '
                          'and unbounded inherited stdio.\n'
                          '\n'
                          '## Verification\n'
                          '```\n'
                          'uv run pytest tests/test_watchdog.py tests/test_providers.py\n'
                          'uv run pytest tests/test_git.py\n'
                          '```\n'
                          '\n'
                          '## Definition of rejected\n'
                          'A missing needed entry fact returns premise_failed, kind: spec_gap, '
                          'naming 19.P4.watchdog-event-stream. A criteria-forced file beyond the '
                          'fence returns premise_failed naming the file. Harden the contract or '
                          'correct the authoring closure; never invent an invariant or widen this '
                          'row.\n'
                          '\n'
                          '## Time budget\n'
                          '- expected: 60m\n'
                          '- stuck: 90m\n',
 'notify-transport': '---\n'
                     'priority: P1\n'
                     'kind: feature\n'
                     'agent_tier: medium\n'
                     'agent_effort: medium\n'
                     'source: seed\n'
                     'state: confirmed\n'
                     '---\n'
                     '\n'
                     '## Depends on\n'
                     '- phase3-exit\n'
                     '- watchdog-event-stream\n'
                     '\n'
                     '## Context\n'
                     '- chupa/config.py\n'
                     '- chupa/seams.py\n'
                     '- chupa/serve.py\n'
                     '- chupa/__main__.py\n'
                     '- tests/test_config.py\n'
                     '- tests/test_serve.py\n'
                     '- chupa/effects.py\n'
                     '- chupa/providers.py\n'
                     '- chupa/redact.py\n'
                     '- chupa/storm.py\n'
                     '- chupa/mergequeue.py\n'
                     '\n'
                     '## Plan contract\n'
                     '- 19.I\n'
                     '- 19.P4.notify-transport\n'
                     '- section 6\n'
                     '- section 13\n'
                     '- section 15\n'
                     '\n'
                     '## Goal / Why\n'
                     'Deliver existing escalation evidence through the configured notification '
                     'command with journal-backed replay.\n'
                     '\n'
                     '## Scope in / Scope out\n'
                     'Implement only notify-transport. Its injected entry governs Owner, Records, '
                     'Observable and Tests; chupa/notify.py owns the new transport and '
                     'pending-escalation reconciliation. Read the merged seams, Effects, config, '
                     'serve composition and emitter records first, and read chupa/journal.py from '
                     "disk for its event-write contract. The preceding stream seed's newly created "
                     'paths are not Context in this admission. No change to existing public call '
                     "signatures or constructor arity is presumed: retain the composition's "
                     'current callers while giving notifications their distinct executor at the '
                     'CLI root.\n'
                     '\n'
                     "Implement the entry's named tests: "
                     'test_notify_effect_once_and_conservative_resend, test_notify_key_domains, '
                     'test_notify_seam_uses_argv_and_secret_free_env, '
                     'test_notify_refuses_malformed_argv, '
                     'test_serve_reconciles_notifications_at_startup_and_poll and '
                     'test_serve_unset_notify_warns_once_and_preserves_pending. Prove through the '
                     'real serve graph that startup and later maintenance deliver old and new '
                     'storm, red-streak and tree-mismatch evidence, that restart suppresses '
                     "completed keys, and that failed delivery remains pending. Preserve config's "
                     'existing unset/valid/null tests. Test environment removal and diagnostic '
                     'scrubbing from configured secrets, using the real argv seam with a '
                     'notification executor separate from work and re-exec.\n'
                     '\n'
                     'At authoring, '
                     'tests/test_storm_notification_activation.py::test_storm_activation_does_not_hold_dispatch_or_notify '
                     "was read: its Effects.run refusal covers run/drain, not serve. The entry's "
                     'serve startup/poll activation does not contradict those assertions, so no '
                     'fence addition is earned. Run that file unchanged as a preservation suite, '
                     'retaining its dispatch order, lock, resume decision, hold release and '
                     'pending Box assertions. The deliverable changes transport only, never the '
                     'emitter, control decisions or hold semantics. Read direct callers and grep '
                     'old notify absence assertions, operation allowlists and emitter identities '
                     'across chupa/, eval/ and tests/ before writing; read delimiter-bearing '
                     'harnesses from disk. Existing fenced paths are Context and no On-demand '
                     'partition is earned. If the required implementation does contradict another '
                     'negative test, return premise_failed naming the missing fence rather than '
                     'widen this seed.\n'
                     '\n'
                     'Effects remains the only effect-record writer, Journal the event writer, Box '
                     "the queue writer and ControlInbox the decision writer. Keep serve's startup "
                     'recovery and cleanup behavior, including ordinary DaemonTasks exception '
                     'propagation, intact. Run tests/test_effects.py and '
                     'tests/test_daemon_composition.py unchanged as preservation suites, without '
                     'embedding or fencing them. Out: watchdog producers/activation, new '
                     'escalation signals, provider changes, dispatch or admission changes, new '
                     'knobs, historical test migration, ticket/plan edits and live state.\n'
                     '\n'
                     '## Scope fence\n'
                     '- chupa/notify.py\n'
                     '- chupa/config.py\n'
                     '- chupa/seams.py\n'
                     '- chupa/serve.py\n'
                     '- chupa/__main__.py\n'
                     '- tests/test_notify.py\n'
                     '- tests/test_config.py\n'
                     '- tests/test_serve.py\n'
                     '\n'
                     '## Acceptance criteria\n'
                     '1. `uv run pytest tests/test_notify.py tests/test_config.py '
                     'tests/test_serve.py` exits 0 proving all six entry test obligations, '
                     'including production reconciliation, replay, pending failures, status-only '
                     'startup and secret-free argv execution.\n'
                     '2. `uv run pytest tests/test_storm_notification_activation.py` exits 0 '
                     "unchanged, preserving run/drain's dispatch, hold, resume, lock, queue and "
                     'no-notify assertions.\n'
                     '3. `uv run pytest tests/test_effects.py tests/test_daemon_composition.py` '
                     'exits 0 preserving write-ahead custody, real composition, recovery and '
                     'cleanup.\n'
                     '\n'
                     '## Verification\n'
                     '```\n'
                     'uv run pytest tests/test_notify.py tests/test_config.py tests/test_serve.py\n'
                     'uv run pytest tests/test_storm_notification_activation.py\n'
                     'uv run pytest tests/test_effects.py tests/test_daemon_composition.py\n'
                     '```\n'
                     '\n'
                     '## Definition of rejected\n'
                     'Missing or contradictory needed facts return premise_failed, kind: spec_gap, '
                     'naming 19.P4.notify-transport. A required path outside this earned fence '
                     'returns premise_failed naming it; correct the closure rather than invent a '
                     'transport or widen the row.\n'
                     '\n'
                     '## Time budget\n'
                     '- expected: 60m\n'
                     '- stuck: 90m\n',
 'phase4-continue': '---\n'
                    'priority: P1\n'
                    'kind: feature\n'
                    'agent_tier: medium\n'
                    'agent_effort: medium\n'
                    'source: seed\n'
                    'state: confirmed\n'
                    '---\n'
                    '\n'
                    '## Depends on\n'
                    '- watchdog-event-stream\n'
                    '- notify-transport\n'
                    '\n'
                    '## Context\n'
                    '- tests/test_seeded_phase3_core.py\n'
                    '\n'
                    '## Plan contract\n'
                    '- 19.L\n'
                    '- 19.I\n'
                    '- 19.P4\n'
                    '- 19.P4.watchdog-detector\n'
                    '- 19.P4.watchdog-activation\n'
                    '- 19.P4.watchdog-event-stream\n'
                    '- 19.P4.notify-transport\n'
                    '- section 9\n'
                    '- section 13\n'
                    '\n'
                    '## Goal / Why\n'
                    "Author Phase 4's second admission and its one successor for Check to review "
                    'and lift.\n'
                    '\n'
                    '## Scope in / Scope out\n'
                    'Parse BEGIN_REGISTRY_P4 through END_REGISTRY_P4 directly from the committed '
                    'CHUPA_PLAN.md when this ticket runs. Position 01 begins admissions[1:]: '
                    '[watchdog-detector, watchdog-activation], [provider-cooldown-failover], '
                    '[reliability-battery], [reliability-run], [phase4-exit]. Author only the '
                    'first of that shrinking suffix and phase4-continue-02. The successor carries '
                    'admissions[2:] and depends on both newly authored payloads. Do not rename, '
                    'reorder, split, omit or add a row, and never author a later admission here. '
                    'Ordinary seeds start medium/medium; a later deep row or terminal starts '
                    "high/high only on 19.L's evidence. Bound each stuck budget by "
                    'drain.max_ticket_minutes and the batch by seeding.max_seeds_per_admission.\n'
                    '\n'
                    'Before authoring, validate the needed non-exit entries '
                    '19.P4.watchdog-detector and 19.P4.watchdog-activation with entry_unit_gap, '
                    'and resolve_plan_contract for those entries, their row citations and all '
                    'needed seeder-role contracts. Revalidate these cited contracts against the '
                    'merged plan when this continuation runs; uncited later admissions are checked '
                    'only by their owning pass. A missing or contradictory governing fact returns '
                    'premise_failed, kind: spec_gap, identifying its owning 19.P4 entry for '
                    'section 11.4; never supply invented facts or copy plan text. Each '
                    'implementation seed cites 19.I, its own entry and row citations. Both '
                    'payloads also cite the event-stream and notify-transport entries they '
                    'consume; activation additionally cites the detector entry. The successor '
                    'cites 19.L, 19.I, 19.P4, section 13 and every entry and row contract needed '
                    'for its next-admission authoring role. A required unit that does not resolve '
                    'stops that pass as spec_gap; never omit its citation. Required future units '
                    'are validated at the pass that authors their payloads, not preemptively by an '
                    'earlier batch.\n'
                    '\n'
                    'Both payloads depend on phase4-continue; watchdog-activation also depends on '
                    'watchdog-detector. The activation must carry every predecessor fixture whose '
                    'dormancy or negative assertion its behavior invalidates, with the real '
                    'production-composition proof required by 19.I. Read all row owners, '
                    'predecessor tickets, direct callers and named tests, and grep public '
                    'signatures, composition sites, allowlists and absence assertions across '
                    'chupa/, eval/ and tests/. Earn fence additions only under 19.L rules 2-5 or '
                    'cited seam-owner closure and pin exact path-specific reasons in the new batch '
                    'test. Existing fenced paths are embedded unless their measured render exceeds '
                    'headroom. Created paths, same-admission siblings, prompt specs and '
                    'delimiter-bearing files never enter Context. Preserve merged serve '
                    'partitioning and historical seeding snapshots; unchanged preservation suites '
                    'go only in Verification.\n'
                    '\n'
                    'Use the merged tests/test_seeded_phase3_core.py idiom. Create '
                    'tests/test_seeded_phase4_01.py pinning the exact batch, confirmed seed birth, '
                    'intake grammar, edges, citation roles, earned fences, named obligations and '
                    'Context/On-demand partition. Record authoring head, idiom blob, ticket/file '
                    'sizes and cited-unit lengths in that test, with max-effort base renders '
                    'bounded by 300,000 characters. Its render arithmetic uses fixed authoring '
                    'snapshots, never current sizes or current plan lengths. Named tests are '
                    'test_named_stems_cover_exactly_this_admission_and_successor, '
                    'test_seed_passes_intake_lint_with_confirmed_seed_birth, '
                    'test_dependencies_as_authored, test_stuck_budget_fits_the_drain_envelope, '
                    'test_fence_contains_its_floor_and_only_earned_additions, '
                    'test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract, '
                    'test_successor_cites_next_admission_and_embeds_merged_earlier_idiom and '
                    'test_context_closure_and_max_effort_render_use_authoring_snapshots.\n'
                    '\n'
                    'Write new seeds directly and leave them uncommitted. Check owns '
                    'requisition_review, tickets/phase4-continue/checks.json approvals and one '
                    'ticket-plane seed lift. Keep an approved seed verbatim while its bytes match '
                    'ticket_sha; re-author only snagged seeds. Commit only the new batch test. '
                    'Out: production implementation, existing tickets/run records, plan edits, Box '
                    'messages, manual release, later batches and edits to historical tests.\n'
                    '\n'
                    '## Scope fence\n'
                    '- tickets\n'
                    '- tests/test_seeded_phase4_01.py\n'
                    '\n'
                    '## Acceptance criteria\n'
                    '1. `uv run pytest -q tests/test_seeded_phase4_01.py` exits 0 proving '
                    'precisely watchdog-detector, watchdog-activation and phase4-continue-02 with '
                    'confirmed birth, grammar, consumption edges and bounded budgets.\n'
                    '2. `uv run pytest -q tests/test_seeded_phase4_01.py` exits 0 proving needed '
                    'entry depth, citation roles, named obligations, earned closure and '
                    'fixed-snapshot render feasibility.\n'
                    '3. `tickets/phase4-continue/checks.json` records requisition_review approve '
                    'for each seed before one ticket-plane seed lift; no seed enters the code '
                    'commit.\n'
                    '4. `uv run pytest -q` exits 0 preserving merged behavior and historical '
                    'seeding tests.\n'
                    '\n'
                    '## Verification\n'
                    '```\n'
                    'uv run pytest -q tests/test_seeded_phase4_01.py\n'
                    'uv run pytest -q\n'
                    '```\n'
                    '\n'
                    '## Definition of rejected\n'
                    'An absent or contradictory needed contract returns premise_failed, kind: '
                    'spec_gap, naming its owning 19.P4 entry. A criteria-forced file outside '
                    'earned closure returns premise_failed. Harden the cited entry or repair the '
                    'authoring fence; do not manufacture evidence or extend the registry.\n'
                    '\n'
                    '## Time budget\n'
                    '- expected: 60m\n'
                    '- stuck: 90m\n'}

ACTUAL_BASE_RENDER_CHARS = {'watchdog-event-stream': 197970, 'notify-transport': 264863, 'phase4-continue': 100822}

VALIDATED_ENTRIES = ('19.P4.watchdog-event-stream',
 '19.P4.notify-transport',
 '19.P4.watchdog-detector',
 '19.P4.watchdog-activation')

VALIDATED_ROW_CITATIONS = {'watchdog-event-stream': ('6', '9', '15'), 'notify-transport': ('6', '13', '15')}

ENTRY_SHA = {'19.P4.watchdog-event-stream': '96be0fcf025e1a70e73ab03aa16357837b493ccfe02086a29b8c14e63b4737ae',
 '19.P4.notify-transport': 'bd1848308625e1744bedf3f5b287f156cb0e4ff0f0cd9bac42b7ff223d697e63',
 '19.P4.watchdog-detector': '6d61e33a0dfa2dc330c43a9cc8d18065ce2ea44b739b186df3e1524e7c4d8eb2',
 '19.P4.watchdog-activation': 'ce93e98a38609216e5e29868311e0401627eabcf6321dcf73018a0197d67c63a'}

ENTRY_TESTS = {'watchdog-event-stream': ('test_event_consumer_receives_before_terminal',
                           'test_event_consumer_preserves_tool_identity_and_optional_usage',
                           'test_event_stream_is_dormant',
                           'test_inflight_events_are_scrubbed_and_capture_is_preserved',
                           'test_event_callback_unwind_kills_group'),
 'notify-transport': ('test_notify_effect_once_and_conservative_resend',
                      'test_notify_key_domains',
                      'test_notify_seam_uses_argv_and_secret_free_env',
                      'test_notify_refuses_malformed_argv',
                      'test_serve_reconciles_notifications_at_startup_and_poll',
                      'test_serve_unset_notify_warns_once_and_preserves_pending')}

PRESERVATION = {'watchdog-event-stream': ('tests/test_git.py',),
 'notify-transport': ('tests/test_effects.py',
                      'tests/test_daemon_composition.py',
                      'tests/test_storm_notification_activation.py')}

CALLER_SNAPSHOT = {'group_exec_adapter_owner': 'chupa/providers.py',
 'adapter_invoke': ('chupa/providers.py', 'eval/harness.py'),
 'process_wrapper': 'eval/shakeout/providers.py',
 'serve_factory': ('chupa/__main__.py', 'chupa/serve.py'),
 'serve_construction': ('chupa/__main__.py',
                        'tests/test_serve.py',
                        'tests/test_daemon_composition.py'),
 'report_writer': ('eval/daemon_soak.py', 'tests/test_daemon_soak.py'),
 'report_runner': ('eval/daemon_soak.py', 'tests/test_daemon_soak_runner.py')}


def _birth(stem):
    return validate_ticket(stem, AUTHORED_TEXT[stem], ROOT, BATCH)


def _ticket(stem):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT, BATCH)


def render_chars(stem, extra=()):
    a = AUTHORED[stem]
    return (IMPLEMENT_SPEC_CHARS + a["chars"] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[pid] for pid in a["plan"])
            + sum(FILE_CHARS[path] for path in (*a["context"], *extra)))


def test_named_stems_cover_exactly_the_core_admission_and_continuation():
    assert PAYLOADS == ("watchdog-event-stream", "notify-transport")
    assert BATCH == (*PAYLOADS, "phase4-continue")
    assert set(EDGES) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(AUTHORED) == set(BATCH)
    assert set(AUTHORED_TEXT) == set(ACTUAL_BASE_RENDER_CHARS) == set(BATCH)
    assert len(set(BATCH)) == 3 <= load_config(None, cwd=ROOT).seeding.max_seeds_per_admission


@pytest.mark.parametrize("stem", BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    birth, live = _birth(stem).frontmatter, _ticket(stem).frontmatter
    assert (birth.source, birth.state) == ("seed", "confirmed")
    # Rejection is lifecycle history; never restamp the fixed confirmed birth fixture.
    assert live.source == "seed" and live.state in {"confirmed", "rejected"}
    assert (birth.agent_tier, birth.agent_effort) == ("medium", "medium")
    assert (live.agent_tier, live.agent_effort) == ("medium", "medium")
    assert birth.priority == "P1" and birth.kind == "feature" and not birth.gate_bypass


@pytest.mark.parametrize("stem", BATCH)
def test_stuck_budget_fits_the_drain_envelope(stem):
    a = AUTHORED[stem]
    for t in (_birth(stem), _ticket(stem)):
        assert t.expected_minutes == a["expected"] == 60
        assert t.stuck_minutes == a["stuck"] == 90
        assert t.stuck_minutes <= load_config(None, cwd=ROOT).drain.max_ticket_minutes


def test_dependencies_as_authored():
    assert EDGES == {
        "watchdog-event-stream": ("phase3-exit",),
        "notify-transport": ("phase3-exit", "watchdog-event-stream"),
        "phase4-continue": PAYLOADS,
    }
    for stem in BATCH:
        assert _birth(stem).depends == _ticket(stem).depends == EDGES[stem]


@pytest.mark.parametrize("stem", BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    expected = (*FENCE_FLOORS[stem], *FENCE_ADDITIONS[stem])
    assert _birth(stem).scope_fence == _ticket(stem).scope_fence == expected
    assert FENCE_ADDITIONS == {name: {} for name in BATCH}
    # 19.L rules 2-3: the read named below refuses notification only in run/drain;
    # notify's startup/poll production flip is owned by serve, so no edit is forced.
    for t in (_birth("notify-transport"), _ticket("notify-transport")):
        assert "test_storm_activation_does_not_hold_dispatch_or_notify" in t.sections["Scope in / Scope out"]
        assert "covers run/drain, not serve" in t.sections["Scope in / Scope out"]
        assert "no fence addition is earned" in t.sections["Scope in / Scope out"]
    assert CALLER_SNAPSHOT["group_exec_adapter_owner"] in FENCE_FLOORS["watchdog-event-stream"]
    assert set(CALLER_SNAPSHOT["serve_factory"]) <= set(FENCE_FLOORS["notify-transport"])


@pytest.mark.parametrize("stem", PAYLOADS)
def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract(stem):
    assert VALIDATED_ROW_CITATIONS == {
        "watchdog-event-stream": ("6", "9", "15"),
        "notify-transport": ("6", "13", "15"),
    }
    expected = ("19.I", f"19.P4.{stem}", *VALIDATED_ROW_CITATIONS[stem])
    assert AUTHORED[stem]["plan"] == expected
    for t in (_birth(stem), _ticket(stem)):
        assert t.plan_contract == expected
        assert "19.L" not in t.plan_contract and "19.P4" not in t.plan_contract


def test_needed_core_and_continuation_entry_contracts_were_validated_at_authoring():
    assert VALIDATED_ENTRIES == (
        "19.P4.watchdog-event-stream", "19.P4.notify-transport",
        "19.P4.watchdog-detector", "19.P4.watchdog-activation",
    )
    assert set(ENTRY_SHA) == set(VALIDATED_ENTRIES)
    assert all(len(sha) == 64 for sha in ENTRY_SHA.values())
    assert {"19.L", "19.I", "19.P4", "13", "6", "9", "15", *VALIDATED_ENTRIES} == set(PLAN_CHARS)
    # entry_unit_gap and resolve_plan_contract ran before emission. Their unit lengths
    # and hashes are fixed receipts; the continuation cites its next payloads' repaired units; later units wait.
    assert all(PLAN_CHARS[uid] > 0 for uid in VALIDATED_ENTRIES)
    for stem in PAYLOADS:
        for t in (_birth(stem), _ticket(stem)):
            prose = t.sections["Scope in / Scope out"]
            assert "Owner, Records, Observable and Tests" in prose
            assert all(name in prose for name in ENTRY_TESTS[stem])
            owner = "chupa/watchdog.py" if stem == PAYLOADS[0] else "chupa/notify.py"
            assert f"{owner} owns" in prose


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    assert NEXT_ADMISSION == ("watchdog-detector", "watchdog-activation")
    assert UNSEEDED_SUFFIX == (
        NEXT_ADMISSION, ("provider-cooldown-failover",), ("reliability-battery",),
        ("reliability-run",), ("phase4-exit",),
    )
    assert len(AUTHORING_HEAD) == len(IDIOM_BLOB) == 40
    for t in (_birth("phase4-continue"), _ticket("phase4-continue")):
        assert t.plan_contract == (
            "19.L", "19.I", "19.P4", "19.P4.watchdog-detector",
            "19.P4.watchdog-activation", "19.P4.watchdog-event-stream",
            "19.P4.notify-transport", "9", "13",
        )
        assert t.context == ("tests/test_seeded_phase3_core.py",)
        prose = t.sections["Scope in / Scope out"]
        for needed in ("admissions[1:]", "admissions[2:]", "phase4-continue-02", "entry_unit_gap",
                       "resolve_plan_contract", "19.P4.watchdog-detector", "19.P4.watchdog-activation",
                       "kind: spec_gap", "fixed authoring snapshots", "re-author only snagged seeds"):
            assert needed in prose
        for admission in UNSEEDED_SUFFIX:
            assert all(stem in prose for stem in admission)
        assert "tests/test_seeded_phase4_01.py" not in (*t.context, *t.on_demand)


@pytest.mark.parametrize("stem", BATCH)
def test_context_closure_and_max_effort_render_use_authoring_snapshots(stem):
    a = AUTHORED[stem]
    assert a["chars"] == len(AUTHORED_TEXT[stem])
    for t in (_birth(stem), _ticket(stem)):
        assert t.context == a["context"]
        assert t.on_demand == a["on_demand"]
    assert set(a["fenced_existing"]) <= set(a["context"]) | set(a["on_demand"])
    assert set((*FENCE_FLOORS[stem], *FENCE_ADDITIONS[stem])) - {"tickets"} == (
        set(a["fenced_existing"]) | set(a["created"]))
    assert not set(a["context"]) & set(a["on_demand"])
    created = {path for sibling in BATCH for path in AUTHORED[sibling]["created"]}
    assert not created & set((*a["context"], *a["on_demand"]))
    assert not any(path.startswith("specs/") or path == "CHUPA_PLAN.md" for path in a["context"])
    assert not {"eval/daemon_soak.py", "eval/harness.py", "eval/shakeout/providers.py"} & set(a["context"])
    assert all(FILE_CHARS[path] > 0 for path in (*a["context"], *a["on_demand"]))
    assert ACTUAL_BASE_RENDER_CHARS[stem] <= render_chars(stem) <= HEADROOM_CHARS == 300_000
    for path in a["on_demand"]:
        assert render_chars(stem, (path,)) > HEADROOM_CHARS
    # The existing merged serve paths stay embedded; no on-demand move is needed.
    assert {"chupa/serve.py", "tests/test_serve.py"} <= set(AUTHORED["notify-transport"]["context"])


@pytest.mark.parametrize("stem", PAYLOADS)
def test_named_entry_verification_and_unchanged_preservation_suites(stem):
    primary = {
        "watchdog-event-stream": ("uv", "run", "pytest", "tests/test_watchdog.py", "tests/test_providers.py"),
        "notify-transport": ("uv", "run", "pytest", "tests/test_notify.py", "tests/test_config.py", "tests/test_serve.py"),
    }
    for t in (_birth(stem), _ticket(stem)):
        assert primary[stem] in t.verification
        preserved = PRESERVATION[stem]
        if stem == "notify-transport":
            assert ("uv", "run", "pytest", *preserved[:2]) in t.verification
            assert ("uv", "run", "pytest", preserved[2]) in t.verification
        else:
            assert ("uv", "run", "pytest", *preserved) in t.verification
        assert not set(PRESERVATION[stem]) & set((*t.scope_fence, *t.context, *t.on_demand))
        if stem == "notify-transport":
            assert ("uv", "run", "pytest", "tests/test_storm_notification_activation.py") in t.verification
        assert all("-k" not in argv and "-m" not in argv for argv in t.verification)
