"""Sole Phase 3 terminal admission; all render measurements are authoring fixtures.

No later engine, file-size or plan-length change updates these snapshots.
"""
from pathlib import Path

from chupa.config import load_config
from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent

AUTHORING_HEAD = 'ade780e3739e4c83aa154b9f56cb1ca531393665'

IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

PAYLOADS = ('phase3-exit',)

BATCH = ('phase3-exit',)

SUCCESSOR = None

TERMINAL_SUFFIX = (('phase3-exit',),)

EDGES = {'phase3-exit': frozenset({'phase3-continue-27'})}

FENCE_FLOORS = {'phase3-exit': ('tickets', 'tests/test_phase3_exit.py', 'tests/test_seeded_phase4_core.py')}

FENCE_ADDITIONS = {'phase3-exit': {}}

PLAN_IDS = ('19.L',
 '19.I',
 '19.P3',
 '19.P4',
 '19.P4.watchdog-event-stream',
 '19.P4.notify-transport',
 '6',
 '9',
 '13',
 '15')

CONTEXT = ('chupa/artifacts.py',
 'chupa/stages.py',
 'chupa/merge.py',
 'chupa/git.py',
 'chupa/effects.py',
 'chupa/seams.py',
 'chupa/serve.py',
 'tests/test_seeded_phase3_core.py',
 'tickets/soak-run/daemon-soak-report.json')

ON_DEMAND = ()

FILE_CHARS = {'chupa/artifacts.py': 8748,
 'chupa/stages.py': 59184,
 'chupa/merge.py': 18346,
 'chupa/git.py': 6640,
 'chupa/effects.py': 3229,
 'chupa/seams.py': 5551,
 'chupa/serve.py': 20113,
 'tests/test_seeded_phase3_core.py': 5425,
 'tickets/soak-run/daemon-soak-report.json': 1284}

PLAN_CHARS = {'19.L': 20912,
 '19.I': 1811,
 '19.P3': 16240,
 '19.P4': 5514,
 '19.P4.watchdog-event-stream': 3441,
 '19.P4.notify-transport': 4362,
 '6': 38005,
 '9': 20021,
 '13': 19807,
 '15': 17104}

TICKET_CHARS = 7933

IMPLEMENT_SPEC_CHARS = 4896

HEADROOM_CHARS = 300000

RENDER_OVERHEAD = 2000

AUTHORED_TEXT = ('---\n'
 'priority: P1\n'
 'kind: feature\n'
 'agent_tier: high\n'
 'agent_effort: high\n'
 'source: seed\n'
 'state: confirmed\n'
 '---\n'
 '\n'
 '## Depends on\n'
 '- phase3-continue-27\n'
 '\n'
 '## Context\n'
 '- chupa/artifacts.py\n'
 '- chupa/stages.py\n'
 '- chupa/merge.py\n'
 '- chupa/git.py\n'
 '- chupa/effects.py\n'
 '- chupa/seams.py\n'
 '- chupa/serve.py\n'
 '- tests/test_seeded_phase3_core.py\n'
 '- tickets/soak-run/daemon-soak-report.json\n'
 '\n'
 '## Plan contract\n'
 '- 19.L\n'
 '- 19.I\n'
 '- 19.P3\n'
 '- 19.P4\n'
 '- 19.P4.watchdog-event-stream\n'
 '- 19.P4.notify-transport\n'
 '- section 6\n'
 '- section 9\n'
 '- section 13\n'
 '- section 15\n'
 '\n'
 '## Goal / Why\n'
 'Prove the Phase 3 exit from committed production evidence and admit the Phase 4 core.\n'
 '\n'
 '## Scope in / Scope out\n'
 'This is the sole terminal payload of the Phase 3 registry. Start high/high because 19.L names '
 'phase exits known-hard. The predecessor edge covers soak-run and every preceding Phase 3 payload '
 'transitively. In tests/test_phase3_exit.py, name test_phase3_exit_dependency_coverage for that '
 'graph coverage, and test_phase3_exit_reads_committed_soak_report for the report read. The '
 'dependency graph is the merged-presence proof; any git read is at most the existing '
 'squash-trailer check, with no approval-provenance cross-check and no new Git operation.\n'
 '\n'
 'Read tickets/soak-run/daemon-soak-report.json using DaemonSoakReport and DAEMON_SOAK_MEMBERS. '
 'Require all ordered members green, matching observations and empty member auditors, and retain '
 'source provenance. Machinery emitters are daemon-soak and daemon-soak-runner; the later producer '
 'is soak-run. The exit consumes their committed production output. It never calls the writer to '
 'refresh that input, creates a substitute fixture as exit evidence, or reads the gitignored live '
 'state directory. An unmet read returns premise_failed naming the member or missing artifact. No '
 'separate Phase 3 report is specified by this registry row.\n'
 '\n'
 'Parse the next-phase registry directly from the committed plan. Author only '
 'watchdog-event-stream, notify-transport and phase4-continue from its first admission, preserving '
 'row identity and order. Use their cited entry contracts for owner, records, observables and '
 'named tests; the renderer injects those contracts. The implementing seeds cite 19.I, their own '
 'entry and row citations; both depend on phase3-exit and notify-transport also depends on '
 'watchdog-event-stream. The continuation depends on both core payloads, owns tickets plus its new '
 'tests/test_seeded_phase4_01.py, and uses the merged tests/test_seeded_phase3_core.py idiom. It '
 'names its next admission and shrinking suffix, and validates the contracts needed for that '
 'admission when it runs. Do not author later admissions here. Source is seed, birth is confirmed, '
 'ordinary starts are medium/medium, and budgets fit drain.max_ticket_minutes. Only the '
 'phase3-exit terminal starts high/high here.\n'
 '\n'
 'Create tests/test_seeded_phase4_core.py to pin the three identities, birth, grammar, dependency '
 'edges, citation roles, earned fences, Context partitions and fixed authoring snapshots for '
 "maximum-effort renders within 300,000 characters. Validate only the immediate Phase 4 core's "
 'needed non-exit entry units with entry_unit_gap and resolve_plan_contract, including row '
 'citations and seeder-role contracts. Missing governing facts return premise_failed, kind: '
 'spec_gap, identifying the cited owning unit; never manufacture a contract or copy its text.\n'
 '\n'
 'Before authoring, read the merged runner and canonical writer in eval/daemon_soak.py from disk '
 '(its engine delimiters exclude it from Context), artifacts registration, report '
 'purge/validation/lift, merge admission, Git/Effects, forced predecessor tickets and direct '
 'callers. Re-grep produce/write_report, KNOWN_ARTIFACTS, Artifact, public surfaces, allowlists '
 'and absence assertions across chupa/, eval/ and tests/. For the core notify production flip, '
 'inspect '
 'tests/test_storm_notification_activation.py::test_storm_activation_does_not_hold_dispatch_or_notify '
 'and fence that existing test if contradicted, retaining its unrelated assertions. Earn additions '
 'only under 19.L rules 2-5 or cited seam-owner closure, with exact paths and reasons in the new '
 'batch test. No signature change is presumed. Existing fenced paths default to Context; On-demand '
 'requires measured headroom overflow. Created paths, same-admission siblings, prompt-spec sources '
 "and delimiter-bearing files never enter Context. Preserve serve's merged-path partition and "
 'historical seeding snapshots.\n'
 '\n'
 'The following unchanged suites carry the named custody obligations:\n'
 'tests/test_daemon_soak.py: test_daemon_soak_command_writes_report_only_on_green, '
 'test_daemon_soak_schema_is_closed, test_daemon_soak_green_matches_observation_and_auditor, '
 'test_daemon_soak_writer_validates_before_write, test_daemon_soak_uses_registered_checks_lift.\n'
 'tests/test_daemon_soak_runner.py: test_daemon_soak_requires_member_local_evidence, '
 'test_daemon_soak_is_rederivable.\n'
 'tests/test_stages.py: test_verification_report_lifts_only_in_checks_commit, '
 'test_invalid_report_fails_check_without_lifting_checks_or_report, '
 'test_implement_report_is_not_lifted_and_stale_report_is_purged, '
 'test_named_missing_report_fails_even_when_other_commands_pass, '
 'test_outbox_only_check_requires_current_report, '
 'test_outbox_only_check_accepts_registered_report.\n'
 'tests/test_merge.py: test_outbox_only_admission_records_null_commit_and_retires.\n'
 '\n'
 'Preserve report-purge, schema-validation, named-report-required, checks-only custody and '
 'inherited byte-equal exclusion. Journal alone writes durable events; Box alone writes queue '
 'records; ControlInbox alone writes control decisions. Preserve Journal(state_dir, clock), '
 'append/read/close, bootstrap on-entry reconciliation and ordinary DaemonTasks exception '
 'propagation and cleanup. The checks lift alone commits registered reports. These suites run in '
 'Verification without being fenced or embedded.\n'
 '\n'
 'Write new seeds directly as uncommitted ticket-plane output. Check owns requisition_review, its '
 'checks.json approvals and the single seed lift; the code commit contains only the two new tests. '
 'Approved prior seeds remain verbatim while bytes match ticket_sha; re-author only snagged seeds. '
 'Out: production changes, existing tickets/run records, live-journal reads, manually refreshed '
 'reports, Box messages, plan edits, historical tests, extra admissions, verification filtering '
 'and manual release.\n'
 '\n'
 '## Scope fence\n'
 '- tickets\n'
 '- tests/test_phase3_exit.py\n'
 '- tests/test_seeded_phase4_core.py\n'
 '\n'
 '## Acceptance criteria\n'
 '1. `uv run pytest -q tests/test_phase3_exit.py` exits 0 proving '
 'test_phase3_exit_dependency_coverage over every preceding Phase 3 payload and '
 'test_phase3_exit_reads_committed_soak_report over all three production members from the '
 'committed report through its schema.\n'
 '2. `uv run pytest -q tests/test_seeded_phase4_core.py` exits 0 proving exactly the Phase 4 core '
 'and one continuation, confirmed seed birth, exact consumption edges, named entry obligations, '
 'earned closure and fixed-snapshot render feasibility.\n'
 '3. `tickets/phase3-exit/checks.json` records requisition_review approve for each emitted seed '
 'before its single ticket-plane seeds commit; seed files stay out of the code commit.\n'
 '4. `uv run pytest tests/test_daemon_soak.py tests/test_daemon_soak_runner.py` and `uv run pytest '
 'tests/test_stages.py tests/test_merge.py` exit 0 preserving production evidence and lane '
 'custody.\n'
 '\n'
 '## Verification\n'
 '```\n'
 'uv run pytest -q tests/test_phase3_exit.py\n'
 'uv run pytest -q tests/test_seeded_phase4_core.py\n'
 'uv run pytest tests/test_daemon_soak.py tests/test_daemon_soak_runner.py\n'
 'uv run pytest tests/test_stages.py tests/test_merge.py\n'
 '```\n'
 '\n'
 '## Definition of rejected\n'
 'An unmet committed exit read returns premise_failed naming it. Missing or contradictory '
 'governing core facts return premise_failed, kind: spec_gap, naming their cited owning hardenable '
 'unit for section 11.4. A criteria-forced path outside an earned fence returns premise_failed; '
 'never invent evidence or widen the registry.\n'
 '\n'
 '## Time budget\n'
 '- expected: 60m\n'
 '- stuck: 90m\n')

PRESERVATION_OBLIGATIONS = {'tests/test_daemon_soak.py': ('test_daemon_soak_command_writes_report_only_on_green',
                               'test_daemon_soak_schema_is_closed',
                               'test_daemon_soak_green_matches_observation_and_auditor',
                               'test_daemon_soak_writer_validates_before_write',
                               'test_daemon_soak_uses_registered_checks_lift'),
 'tests/test_daemon_soak_runner.py': ('test_daemon_soak_requires_member_local_evidence',
                                      'test_daemon_soak_is_rederivable'),
 'tests/test_stages.py': ('test_verification_report_lifts_only_in_checks_commit',
                          'test_invalid_report_fails_check_without_lifting_checks_or_report',
                          'test_implement_report_is_not_lifted_and_stale_report_is_purged',
                          'test_named_missing_report_fails_even_when_other_commands_pass',
                          'test_outbox_only_check_requires_current_report',
                          'test_outbox_only_check_accepts_registered_report'),
 'tests/test_merge.py': ('test_outbox_only_admission_records_null_commit_and_retires',)}

CLOSURE_REASONS = {'tickets': 'registry floor; only new Phase 4 seed files, no existing record edits',
 'tests/test_phase3_exit.py': 'registry floor; creates committed-report and dependency-coverage '
                              'proofs',
 'tests/test_seeded_phase4_core.py': 'registry floor; creates immediate core admission snapshot '
                                     'assertions'}

CUSTODY = ('report-purge',
 'schema-validation',
 'named-report-required',
 'checks-only',
 'inherited byte-equal exclusion',
 'Journal alone writes durable events',
 'Box alone writes queue records',
 'ControlInbox alone writes control decisions',
 'Journal(state_dir, clock)',
 'append/read/close',
 'bootstrap on-entry reconciliation',
 'ordinary DaemonTasks exception propagation and cleanup')

CALLER_SNAPSHOT = {'write_report': ('eval/daemon_soak.py', 'tests/test_daemon_soak.py'),
 'produce': ('eval/daemon_soak.py', 'tests/test_daemon_soak_runner.py'),
 'next_core_contradicted_assertion': 'tests/test_storm_notification_activation.py::test_storm_activation_does_not_hold_dispatch_or_notify'}


DEPENDENCY_SNAPSHOT = {'phase3-continue-27': ('soak-run',),
 'soak-run': ('phase3-continue-26',),
 'phase3-continue-26': ('daemon-soak-runner',),
 'daemon-soak-runner': ('phase3-continue-25',),
 'phase3-continue-25': ('daemon-soak',),
 'daemon-soak': ('phase3-continue-24',),
 'phase3-continue-24': ('outbox-only-admission',),
 'outbox-only-admission': ('phase3-continue-23',),
 'phase3-continue-23': ('worker-recovery-disposition',),
 'worker-recovery-disposition': ('phase3-continue-22',),
 'phase3-continue-22': ('serve-merge-admission',),
 'serve-merge-admission': ('phase3-continue-21',),
 'phase3-continue-21': ('serve-activation',),
 'serve-activation': ('phase3-continue-20',),
 'phase3-continue-20': ('checkpoint-push',),
 'checkpoint-push': ('phase3-continue-19',),
 'phase3-continue-19': ('storm-dispatch-hold',),
 'storm-dispatch-hold': ('phase3-continue-18',),
 'phase3-continue-18': ('storm-producer-wiring', 'storm-notification-activation'),
 'storm-producer-wiring': ('phase3-continue-17',),
 'phase3-continue-17': ('journal-roll', 'storm-ledger'),
 'journal-roll': ('phase3-continue-16',),
 'phase3-continue-16': ('flake-detection', 'flake-release'),
 'flake-detection': ('phase3-continue-15',),
 'phase3-continue-15': ('restart-timers',),
 'restart-timers': ('phase3-continue-14',),
 'phase3-continue-14': ('heartbeat',),
 'heartbeat': ('phase3-continue-13',),
 'phase3-continue-13': ('kill-cli-activation',),
 'kill-cli-activation': ('phase3-continue-12',),
 'phase3-continue-12': ('kill-worker-stop', 'kill-failure-suppression'),
 'kill-worker-stop': ('phase3-continue-11',),
 'phase3-continue-11': ('kill-signal-journal', 'kill-executor-abort'),
 'kill-signal-journal': ('phase3-continue-10',),
 'phase3-continue-10': ('admission-holds-activation',),
 'admission-holds-activation': ('phase3-continue-09', 'pause-resume-activation'),
 'phase3-continue-09': ('dispatch-pause-boundary', 'pause-resume-activation'),
 'dispatch-pause-boundary': ('phase3-continue-08',),
 'phase3-continue-08': ('background-consumers', 'control-inbox'),
 'background-consumers': ('phase3-continue-07',),
 'phase3-continue-07': ('merge-queue-activation', 'rework-activation'),
 'merge-queue-activation': ('phase3-continue-06',),
 'phase3-continue-06': ('scheduler-activation',),
 'scheduler-activation': ('phase3-continue-05',),
 'phase3-continue-05': ('dispatch-admission-boundary', 'dispatch-config-snapshot'),
 'dispatch-admission-boundary': ('phase3-continue-04',),
 'phase3-continue-04': ('thresh-runtime',),
 'thresh-runtime': ('phase3-continue-03',),
 'phase3-continue-03': ('rework-stage',),
 'rework-stage': ('phase3-continue-02',),
 'phase3-continue-02': ('merge-queue',),
 'merge-queue': ('phase3-continue',),
 'phase3-continue': ('daemon-scheduler', 'seed-successor-proof'),
 'daemon-scheduler': ('phase3-core',),
 'phase3-core': ('phase2-exit',),
 'phase2-exit': ('shakeout-providers', 'diagnosis-eval-run'),
 'shakeout-providers': ('shakeout-merge',),
 'shakeout-merge': ('shakeout-recovery',),
 'shakeout-recovery': ('shakeout-drain',),
 'shakeout-drain': ('shakeout-runner',),
 'shakeout-runner': ('shakeout-driver',),
 'shakeout-driver': ('shakeout-stages',),
 'shakeout-stages': ('shakeout-report-lane', 'verification-base-attribution'),
 'shakeout-report-lane': ('invariant-auditor',),
 'invariant-auditor': ('requisition-seed-path',),
 'requisition-seed-path': ('requisition-author-path',),
 'requisition-author-path': ('requisition-review', 'author-stage'),
 'requisition-review': ('author-stage',),
 'author-stage': ('box-triage', 'box-start-policy'),
 'box-triage': ('box-start-policy', 'suggestion-box'),
 'box-start-policy': ('escalation-ladder', 'suggestion-box'),
 'escalation-ladder': ('reject-queue-verbs',),
 'reject-queue-verbs': ('second-problems-filing', 'suggestion-box'),
 'second-problems-filing': ('suggestion-box',),
 'suggestion-box': ('spine-diagnosis',),
 'spine-diagnosis': ('spine-caps', 'spine-harvest', 'spine-harvest-orphans'),
 'spine-caps': ('plan-contract-section-render',),
 'plan-contract-section-render': (),
 'spine-harvest': ('spine-caps',),
 'spine-harvest-orphans': ('spine-harvest',),
 'verification-base-attribution': ('box-triage',),
 'diagnosis-eval-run': ('diagnosis-eval-harness',),
 'diagnosis-eval-harness': ('spine-diagnosis',),
 'seed-successor-proof': ('phase3-core',),
 'dispatch-config-snapshot': ('phase3-continue-04', 'dispatch-admission-boundary'),
 'rework-activation': ('phase3-continue-06', 'merge-queue-activation'),
 'control-inbox': ('phase3-continue-07', 'background-consumers'),
 'pause-resume-activation': ('phase3-continue-08', 'dispatch-pause-boundary'),
 'kill-executor-abort': ('phase3-continue-10', 'kill-signal-journal'),
 'kill-failure-suppression': ('phase3-continue-11', 'kill-worker-stop'),
 'flake-release': ('phase3-continue-15', 'flake-detection'),
 'storm-ledger': ('phase3-continue-16', 'journal-roll'),
 'storm-notification-activation': ('phase3-continue-17', 'storm-producer-wiring')}
PHASE3_PREDECESSORS = ('daemon-scheduler',
 'seed-successor-proof',
 'merge-queue',
 'rework-stage',
 'thresh-runtime',
 'dispatch-admission-boundary',
 'dispatch-config-snapshot',
 'scheduler-activation',
 'merge-queue-activation',
 'rework-activation',
 'background-consumers',
 'control-inbox',
 'dispatch-pause-boundary',
 'pause-resume-activation',
 'admission-holds-activation',
 'kill-signal-journal',
 'kill-executor-abort',
 'kill-worker-stop',
 'kill-failure-suppression',
 'kill-cli-activation',
 'heartbeat',
 'restart-timers',
 'flake-detection',
 'flake-release',
 'journal-roll',
 'storm-ledger',
 'storm-producer-wiring',
 'storm-notification-activation',
 'storm-dispatch-hold',
 'checkpoint-push',
 'serve-activation',
 'serve-merge-admission',
 'worker-recovery-disposition',
 'outbox-only-admission',
 'daemon-soak',
 'daemon-soak-runner',
 'soak-run')

def _authored():
    return validate_ticket("phase3-exit", AUTHORED_TEXT, ROOT)


def _ticket():
    # Rejected is later lifecycle history; confirmed birth belongs to the authoring snapshot.
    return validate_ticket("phase3-exit", (ROOT / ticket_path("phase3-exit")).read_text(), ROOT)


def render_chars(extra=()):
    return (IMPLEMENT_SPEC_CHARS + TICKET_CHARS + RENDER_OVERHEAD
            + sum(PLAN_CHARS[pid] for pid in PLAN_IDS)
            + sum(FILE_CHARS[path] for path in (*CONTEXT, *extra)))


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert BATCH == PAYLOADS == ("phase3-exit",)
    assert SUCCESSOR is None and TERMINAL_SUFFIX == (PAYLOADS,)
    assert set(EDGES) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(BATCH)
    assert len(BATCH) <= load_config(None, cwd=ROOT).seeding.max_seeds_per_admission


def test_seed_passes_intake_lint_with_confirmed_seed_birth():
    birth = _authored().frontmatter
    assert (birth.source, birth.state) == ("seed", "confirmed")
    live = _ticket().frontmatter
    assert live.source == "seed" and live.state in {"confirmed", "rejected"}
    assert (birth.agent_tier, birth.agent_effort) == ("high", "high")
    assert (live.agent_tier, live.agent_effort) == ("high", "high")
    assert "19.L" in _authored().plan_contract


def test_stuck_budget_fits_the_drain_envelope():
    for ticket in (_authored(), _ticket()):
        assert ticket.expected_minutes == 60
        assert ticket.stuck_minutes == 90
        assert ticket.stuck_minutes <= load_config(None, cwd=ROOT).drain.max_ticket_minutes


def test_dependencies_as_authored():
    assert set(_authored().depends) == set(_ticket().depends) == EDGES["phase3-exit"]
    reached = set()
    pending = list(EDGES["phase3-exit"])
    while pending:
        stem = pending.pop()
        if stem not in reached:
            reached.add(stem)
            pending.extend(DEPENDENCY_SNAPSHOT.get(stem, ()))
    assert set(PHASE3_PREDECESSORS) <= reached
    assert DEPENDENCY_SNAPSHOT["phase3-continue-27"] == ("soak-run",)
    assert len(PHASE3_PREDECESSORS) == 37


def test_fence_contains_its_floor_and_only_earned_additions():
    assert not FENCE_ADDITIONS["phase3-exit"]
    assert set(_ticket().scope_fence) == set(_authored().scope_fence) == set(FENCE_FLOORS["phase3-exit"])
    assert set(CLOSURE_REASONS) == set(FENCE_FLOORS["phase3-exit"])
    assert all(CLOSURE_REASONS.values())
    assert CALLER_SNAPSHOT["write_report"] == ("eval/daemon_soak.py", "tests/test_daemon_soak.py")
    assert CALLER_SNAPSHOT["produce"] == ("eval/daemon_soak.py", "tests/test_daemon_soak_runner.py")


def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract():
    # This admission has no non-exit implementation row; its terminal has the seeder role.
    for ticket in (_authored(), _ticket()):
        assert set(ticket.plan_contract) == set(PLAN_IDS)
        assert {"19.L", "19.I", "19.P3", "19.P4", "13"} <= set(ticket.plan_contract)
        entries = {pid for pid in ticket.plan_contract if pid.startswith("19.P4.")}
        assert entries == {"19.P4.watchdog-event-stream", "19.P4.notify-transport"}
        assert {"6", "9", "15"} <= set(ticket.plan_contract)


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    assert SUCCESSOR is None
    assert "tests/test_seeded_phase3_core.py" in _ticket().context
    assert len(AUTHORING_HEAD) == len(IDIOM_BLOB) == 40
    assert not set(CONTEXT) & {"tests/test_seeded_phase3_25.py", "tests/test_seeded_phase3_26.py",
                               "tests/test_seeded_phase3_27.py"}


def test_context_closure_and_max_effort_render_use_authoring_snapshots():
    for ticket in (_authored(), _ticket()):
        assert ticket.context == CONTEXT
        assert ticket.on_demand == ON_DEMAND
    assert not ON_DEMAND
    assert set(FILE_CHARS) == set(CONTEXT)
    assert set(PLAN_CHARS) == set(PLAN_IDS)
    assert TICKET_CHARS == len(AUTHORED_TEXT)
    assert all(n > 0 for n in (*FILE_CHARS.values(), *PLAN_CHARS.values()))
    created = set(FENCE_FLOORS["phase3-exit"]) - {"tickets"}
    assert not created & set(CONTEXT)
    assert not any(path.startswith("specs/") for path in CONTEXT)
    assert render_chars() <= HEADROOM_CHARS
    for path in ON_DEMAND:
        assert render_chars((path,)) > HEADROOM_CHARS


def test_payloads_run_preservation_suites_without_fencing_or_embedding_them():
    ticket = _ticket()
    commands = {tuple(argv) for argv in ticket.verification}
    assert ("uv", "run", "pytest", "tests/test_daemon_soak.py", "tests/test_daemon_soak_runner.py") in commands
    assert ("uv", "run", "pytest", "tests/test_stages.py", "tests/test_merge.py") in commands
    assert not set(PRESERVATION_OBLIGATIONS) & (set(ticket.scope_fence) | set(ticket.context))
    assert sum(len(names) for names in PRESERVATION_OBLIGATIONS.values()) == 14
    assert len(CUSTODY) == 12
    assert "tickets/soak-run/daemon-soak-report.json" in CONTEXT
    # Verification only reads the producer's committed output; no report-generation command.
    assert all("eval.daemon_soak" not in argv for argv in ticket.verification)
