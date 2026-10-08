"""Admission 26: the separate report run and terminal seeder.

Render arithmetic uses permanent authoring snapshots, independent of later tree growth.
Check owns requisition approval and the ticket-plane lift; this test pins authored closure.
"""

from pathlib import Path

import pytest

from chupa.config import load_config
from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent
PAYLOADS = ("soak-run",)
BATCH = (*PAYLOADS, "phase3-continue-27")
SUFFIX = (("soak-run",), ("phase3-exit",))
EDGES = {"soak-run": frozenset({"phase3-continue-26"}),
         "phase3-continue-27": frozenset({"soak-run"})}
FENCE_FLOORS = {"soak-run": ("tickets/soak-run/daemon-soak-report.json",),
                "phase3-continue-27": ("tickets", "tests/test_seeded_phase3_27.py")}
FENCE_ADDITIONS = {stem: () for stem in BATCH}
HEADROOM_CHARS = 300_000
RENDER_OVERHEAD = 2_000

AUTHORING_HEAD = 'c529c35103a106fcbdb532148aa79614b7ed28a0'

MERGED_IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

IMPLEMENT_SPEC_CHARS = 4775

PLAN_CHARS = {'19.I': 1811, '19.P3.soak-run': 2713, '19.L': 20858, '19.P3': 16240, '13': 19708}

FILE_CHARS = {'chupa/artifacts.py': 8748,
 'chupa/stages.py': 59170,
 'chupa/merge.py': 18346,
 'chupa/git.py': 6640,
 'chupa/effects.py': 3229,
 'chupa/seams.py': 5551,
 'chupa/serve.py': 20113,
 'chupa/daemon.py': 26079,
 'chupa/journal.py': 10606,
 'chupa/box.py': 10000,
 'chupa/control.py': 9879,
 'chupa/reconcile.py': 2715,
 'chupa/audit.py': 5117,
 'chupa/restart.py': 1951,
 'chupa/timers.py': 4966,
 'tests/test_seeded_phase3_core.py': 5425}

FILE_BYTES = {'chupa/artifacts.py': 8748,
 'chupa/stages.py': 59170,
 'chupa/merge.py': 18346,
 'chupa/git.py': 6640,
 'chupa/effects.py': 3229,
 'chupa/seams.py': 5551,
 'chupa/serve.py': 20113,
 'chupa/daemon.py': 26079,
 'chupa/journal.py': 10606,
 'chupa/box.py': 10000,
 'chupa/control.py': 9879,
 'chupa/reconcile.py': 2715,
 'chupa/audit.py': 5117,
 'chupa/restart.py': 1951,
 'chupa/timers.py': 4966,
 'tests/test_seeded_phase3_core.py': 5425}

SNAPSHOTS = {'soak-run': {'chars': 4980,
              'bytes': 4980,
              'plan': ('19.I', '19.P3.soak-run'),
              'context': ('chupa/artifacts.py',
                          'chupa/stages.py',
                          'chupa/merge.py',
                          'chupa/git.py',
                          'chupa/effects.py',
                          'chupa/seams.py',
                          'chupa/serve.py',
                          'chupa/daemon.py',
                          'chupa/journal.py',
                          'chupa/box.py',
                          'chupa/control.py',
                          'chupa/reconcile.py',
                          'chupa/audit.py',
                          'chupa/restart.py',
                          'chupa/timers.py'),
              'on_demand': (),
              'fenced_existing': (),
              'created': ('tickets/soak-run/daemon-soak-report.json',),
              'expected': 30,
              'stuck': 60,
              'birth': ('seed', 'confirmed', 'medium', 'medium'),
              'base_render': 207662},
 'phase3-continue-27': {'chars': 7134,
                        'bytes': 7134,
                        'plan': ('19.L', '19.I', '19.P3', '13'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fenced_existing': (),
                        'created': ('tests/test_seeded_phase3_27.py',),
                        'expected': 60,
                        'stuck': 90,
                        'birth': ('seed', 'confirmed', 'medium', 'medium'),
                        'base_render': 75933}}

CLOSURE_SNAPSHOT = {'searched_roots': ('chupa/', 'eval/', 'tests/'),
 'patterns': ('produce|write_report',
              'KNOWN_ARTIFACTS|Artifact',
              'public|__all__|allowlist|not hasattr|absence',
              'build_daemon_core|compose_pipeline',
              'purge|lift_outbox|model_validate_json'),
 'write_report_callers': ('eval/daemon_soak.py', 'tests/test_daemon_soak.py'),
 'produce_callers': ('eval/daemon_soak.py', 'tests/test_daemon_soak_runner.py'),
 'rules_2_5': 'No flipped assertions, activation, new module, signature or public operation; no '
              'additions earned.',
 'terminal_lookahead': 'phase3-exit governed by 19.P3, not a non-exit entry; no speculative fence '
                       'additions.',
 'path_reasons': {'chupa/artifacts.py': ('Context',
                                         'merged closed report schema and Artifact provenance'),
                  'chupa/stages.py': ('Context',
                                      'merged registered purge, validation and checks lift'),
                  'chupa/merge.py': ('Context',
                                     'current lift evidence, null-commit admission and retirement'),
                  'chupa/git.py': ('Context', 'argv-only Git custody seam'),
                  'chupa/effects.py': ('Context', 'completion-keyed lift/admission Effects'),
                  'chupa/seams.py': ('Context', 'injected filesystem and process execution'),
                  'chupa/serve.py': ('Context', 'merged production serve graph and lifetime'),
                  'chupa/daemon.py': ('Context', 'DaemonTasks exception propagation and cleanup'),
                  'chupa/journal.py': ('Context', 'sole durable event writer; append/read/close'),
                  'chupa/box.py': ('Context', 'sole queue-record owner'),
                  'chupa/control.py': ('Context', 'ControlInbox decision-before-mutation owner'),
                  'chupa/reconcile.py': ('Context', 'bootstrap on-entry recovery disposition'),
                  'chupa/audit.py': ('Context', 'member-local invariant auditor'),
                  'chupa/restart.py': ('Context', 'reconcile before dispatch'),
                  'chupa/timers.py': ('Context', 'recurring injected-clock cycles'),
                  'tests/test_seeded_phase3_core.py': ('Context', 'merged earlier seeding idiom')},
 'report_floor': ('tickets/soak-run/daemon-soak-report.json', 'created; sole producer deliverable'),
 'successor_floor': ('tests/test_seeded_phase3_27.py', 'created; terminal authoring proof'),
 'excluded_context': {'eval/daemon_soak.py': 'delimiter-bearing runner; read on disk',
                      'tests/test_daemon_soak.py': 'unchanged preservation suite',
                      'tests/test_daemon_soak_runner.py': 'unchanged preservation suite',
                      'tests/test_stages.py': 'unchanged preservation suite',
                      'tests/test_merge.py': 'unchanged preservation suite',
                      'tests/test_seeded_phase3_25.py': 'historical snapshot; never embed',
                      'tests/test_seeded_phase3_26.py': 'same-admission creation; never embed'}}

OBLIGATIONS = ('test_daemon_soak_command_writes_report_only_on_green',
 'test_daemon_soak_requires_member_local_evidence',
 'test_daemon_soak_is_rederivable',
 'test_daemon_soak_schema_is_closed',
 'test_daemon_soak_green_matches_observation_and_auditor',
 'test_daemon_soak_writer_validates_before_write',
 'test_daemon_soak_uses_registered_checks_lift',
 'test_verification_report_lifts_only_in_checks_commit',
 'test_invalid_report_fails_check_without_lifting_checks_or_report',
 'test_implement_report_is_not_lifted_and_stale_report_is_purged',
 'test_named_missing_report_fails_even_when_other_commands_pass',
 'test_outbox_only_check_requires_current_report',
 'test_outbox_only_check_accepts_registered_report',
 'test_outbox_only_admission_records_null_commit_and_retires')

CUSTODY = ('report-purge',
 'schema-validation',
 'named-report-required',
 'checks-only',
 'inherited byte-equal exclusion',
 'ticket-plane/soak-run/<attempt>/checks',
 'null commit',
 'single retirement',
 'Journal alone writes durable events',
 'Box alone writes queue records',
 'ControlInbox alone writes control decisions',
 'Journal(state_dir, clock)',
 'append/read/close',
 'bootstrap on-entry reconciliation',
 'ordinary DaemonTasks exception propagation and cleanup')

DELIMITER_SAFE = ('chupa/artifacts.py',
 'chupa/stages.py',
 'chupa/merge.py',
 'chupa/git.py',
 'chupa/effects.py',
 'chupa/seams.py',
 'chupa/serve.py',
 'chupa/daemon.py',
 'chupa/journal.py',
 'chupa/box.py',
 'chupa/control.py',
 'chupa/reconcile.py',
 'chupa/audit.py',
 'chupa/restart.py',
 'chupa/timers.py',
 'tests/test_seeded_phase3_core.py')

PRESERVATION_SUITES = ('tests/test_daemon_soak.py',
 'tests/test_daemon_soak_runner.py',
 'tests/test_stages.py',
 'tests/test_merge.py')

CONTRACT_CHECK = {'19.P3.soak-run': 'entry_unit_gap returned None; resolved at authoring head',
 '19.I': 'resolved',
 '19.L': 'resolved',
 '13': 'resolved',
 '19.P3': 'resolved; terminal lookahead'}



def _ticket(stem):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT, BATCH)


def _text(stem):
    return (ROOT / ticket_path(stem)).read_text()


def render_chars(a):
    return (IMPLEMENT_SPEC_CHARS + a["chars"] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[pid] for pid in a["plan"])
            + sum(FILE_CHARS[path] for path in a["context"]))


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert BATCH == ("soak-run", "phase3-continue-27")
    assert SUFFIX == (("soak-run",), ("phase3-exit",))
    assert len(set(BATCH)) == len(BATCH)
    assert set(EDGES) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(SNAPSHOTS) == set(BATCH)
    assert len(BATCH) <= load_config(None, cwd=ROOT).seeding.max_seeds_per_admission
    assert len(AUTHORING_HEAD) == len(MERGED_IDIOM_BLOB) == 40
    assert set(CONTRACT_CHECK) == {"19.P3.soak-run", "19.I", "19.L", "13", "19.P3"}


@pytest.mark.parametrize("stem", BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    fm = _ticket(stem).frontmatter
    assert SNAPSHOTS[stem]["birth"] == ("seed", "confirmed", "medium", "medium")
    assert fm.source == "seed"
    # Rejection is lifecycle history, not a different authored birth.
    assert fm.state in {"confirmed", "rejected"}
    assert (fm.agent_tier, fm.agent_effort) == ("medium", "medium")
    assert (fm.priority, fm.kind) == ("P1", "feature")


@pytest.mark.parametrize("stem", BATCH)
def test_stuck_budget_fits_the_drain_envelope(stem):
    t, a = _ticket(stem), SNAPSHOTS[stem]
    assert (t.expected_minutes, t.stuck_minutes) == (a["expected"], a["stuck"])
    assert 0 < t.expected_minutes <= t.stuck_minutes <= load_config(None, cwd=ROOT).drain.max_ticket_minutes


@pytest.mark.parametrize("stem", BATCH)
def test_dependencies_as_authored(stem):
    assert set(_ticket(stem).depends) == EDGES[stem]


@pytest.mark.parametrize("stem", BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    assert set(_ticket(stem).scope_fence) == set(FENCE_FLOORS[stem]) | set(FENCE_ADDITIONS[stem])
    assert not FENCE_ADDITIONS[stem]
    assert CLOSURE_SNAPSHOT["searched_roots"] == ("chupa/", "eval/", "tests/")
    assert CLOSURE_SNAPSHOT["write_report_callers"] == ("eval/daemon_soak.py", "tests/test_daemon_soak.py")
    assert CLOSURE_SNAPSHOT["produce_callers"] == ("eval/daemon_soak.py", "tests/test_daemon_soak_runner.py")
    assert "no additions earned" in CLOSURE_SNAPSHOT["rules_2_5"]
    assert "not a non-exit entry" in CLOSURE_SNAPSHOT["terminal_lookahead"]
    for path in SNAPSHOTS[stem]["context"]:
        partition, reason = CLOSURE_SNAPSHOT["path_reasons"][path]
        assert partition == "Context" and reason
    assert CLOSURE_SNAPSHOT["report_floor"][0] == FENCE_FLOORS["soak-run"][0]


def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract():
    t = _ticket("soak-run")
    assert t.plan_contract == SNAPSHOTS[t.stem]["plan"] == ("19.I", "19.P3.soak-run")
    assert not {"19.L", "19.P3"} & set(t.plan_contract)
    assert set(OBLIGATIONS) == {
        "test_daemon_soak_command_writes_report_only_on_green",
        "test_daemon_soak_requires_member_local_evidence",
        "test_daemon_soak_is_rederivable",
        "test_daemon_soak_schema_is_closed",
        "test_daemon_soak_green_matches_observation_and_auditor",
        "test_daemon_soak_writer_validates_before_write",
        "test_daemon_soak_uses_registered_checks_lift",
        "test_verification_report_lifts_only_in_checks_commit",
        "test_invalid_report_fails_check_without_lifting_checks_or_report",
        "test_implement_report_is_not_lifted_and_stale_report_is_purged",
        "test_named_missing_report_fails_even_when_other_commands_pass",
        "test_outbox_only_check_requires_current_report",
        "test_outbox_only_check_accepts_registered_report",
        "test_outbox_only_admission_records_null_commit_and_retires",
    }
    text = _text(t.stem)
    for obligation in (*OBLIGATIONS, *CUSTODY):
        assert obligation in text
    for fact in ("owns no code or test module", "Leave the report uncommitted",
                 "never hand-copy, patch or Git-add", "No test-authored fixture report",
                 "source-HEAD provenance", "fresh Check production"):
        assert fact in text


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket("phase3-continue-27")
    assert t.plan_contract == SNAPSHOTS[t.stem]["plan"] == ("19.L", "19.I", "19.P3", "13")
    assert t.context == ("tests/test_seeded_phase3_core.py",)
    text = _text(t.stem)
    for fact in ("admissions[27:]", "phase3-exit only", "sole payload", "without a successor",
                 "starts high/high", "depends on phase3-continue-27",
                 "parent checked soak-run, not the terminal", "terminal now against 19.P3",
                 "entry_unit_gap", "resolve_plan_contract", "ticket_sha",
                 "fixed authoring snapshots", "300,000-character headroom",
                 "chupa(phase3-continue-27): seeds"):
        assert fact in text
    for obligation in OBLIGATIONS:
        assert obligation in text
    for fact in ("Journal alone writes durable events", "Box alone writes queue records",
                 "ControlInbox alone writes control decisions", "Journal(state_dir, clock)",
                 "append/read/close", "ordinary DaemonTasks exception propagation and cleanup"):
        assert fact in text


@pytest.mark.parametrize("stem", BATCH)
def test_context_closure_and_max_effort_render_use_authoring_snapshots(stem):
    a, t = SNAPSHOTS[stem], _ticket(stem)
    assert t.context == a["context"]
    assert t.on_demand == a["on_demand"] == ()
    assert set(a["fenced_existing"]) <= set(a["context"]) | set(a["on_demand"])
    assert not set(a["context"]) & set(a["on_demand"])
    assert set(a["created"]) == set(FENCE_FLOORS[stem]) - {"tickets"}
    assert not set(a["created"]) & (set(a["context"]) | set(a["on_demand"]))
    assert set(a["context"]) <= set(DELIMITER_SAFE)
    assert not set(a["context"]) & set(CLOSURE_SNAPSHOT["excluded_context"])
    assert all(not path.startswith("specs/") for path in a["context"])
    assert a["bytes"] >= a["chars"] > 0
    assert set(FILE_CHARS) == set(FILE_BYTES) == set(DELIMITER_SAFE)
    assert all(FILE_BYTES[path] >= FILE_CHARS[path] > 0 for path in FILE_CHARS)
    # The bound applies at every effort; all operands are permanent fixtures.
    assert a["base_render"] <= render_chars(a) <= HEADROOM_CHARS
    assert set(a["plan"]) <= set(PLAN_CHARS)


def test_payloads_run_preservation_suites_without_fencing_or_embedding_them():
    t = _ticket("soak-run")
    assert t.verification == (
        ("uv", "run", "pytest", "tests/test_daemon_soak.py", "tests/test_daemon_soak_runner.py"),
        ("uv", "run", "pytest", "tests/test_stages.py", "tests/test_merge.py"),
        ("uv", "run", "python", "-m", "eval.daemon_soak", "--out",
         "tickets/soak-run/daemon-soak-report.json"),
    )
    assert not set(PRESERVATION_SUITES) & (set(t.scope_fence) | set(t.context) | set(t.on_demand))
    assert _ticket("phase3-continue-27").verification == (
        ("uv", "run", "pytest", "-q", "tests/test_seeded_phase3_27.py"),
        ("uv", "run", "pytest", "-q"),
    )
