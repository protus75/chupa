"""Continuation 07: fixed authoring measurements never follow live plan/tree sizes.

Closure grep across chupa/, eval/ and tests/ covered DaemonTasks, control identities,
publish, FileSystem runtime assertions, public allowlists, negative/dormancy fixtures,
Watcher.run, MergeQueue.process and triage_pass. Dormant construction changes no
existing signatures or production absence assertions. The sole earned addition is
Effects' runtime protocol fake (path and reason below). The production composition
harness remains an unchanged preservation suite, never fenced or embedded.
"""

import hashlib
from pathlib import Path

import pytest

from chupa.config import load_config
from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent

PAYLOADS = ('background-consumers', 'control-inbox')

BATCH = ('background-consumers', 'control-inbox', 'phase3-continue-08')

EDGES = {'background-consumers': ('phase3-continue-07',),
 'control-inbox': ('phase3-continue-07', 'background-consumers'),
 'phase3-continue-08': ('background-consumers', 'control-inbox')}

FENCE_FLOORS = {'background-consumers': ('chupa/daemon.py', 'tests/test_daemon_tasks.py'),
 'control-inbox': ('chupa/control.py',
                   'chupa/daemon.py',
                   'chupa/seams.py',
                   'tests/test_control.py'),
 'phase3-continue-08': ('tickets', 'tests/test_seeded_phase3_08.py')}

FENCE_ADDITIONS = {'background-consumers': {},
 'control-inbox': {'tests/test_effects.py': 'CONTRADICTED TESTS/CALLER CLOSURE: '
                                            'test_fakes_satisfy_seam_protocols pins '
                                            'isinstance(FakeFS(), FileSystem); publish extends '
                                            'that runtime protocol, so FakeFS must implement it '
                                            'while write/replace and Effects invariants remain '
                                            'unchanged.'},
 'phase3-continue-08': {}}

AUTHORING_HEAD = 'e970e6ef9d0ede947c932fff2a3b1c7adf255b3a'

MERGED_IDIOM = 'tests/test_seeded_phase3_core.py'

MERGED_IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

AUTHORED_STATE = {stem: "confirmed" for stem in BATCH}

HEADROOM_CHARS = 300_000  # section 8: 400,000 x 0.75 at every effort, including max

IMPLEMENT_SPEC_CHARS = 4316

RENDER_OVERHEAD = 2000

PLAN_CHARS = {'19.I': 1811,
 '19.P3.background-consumers': 5751,
 '19.P3.control-inbox': 8797,
 '20': 4367,
 '19.L': 19167,
 '19.P3': 16053,
 '13': 19104,
 '19.P3.dispatch-pause-boundary': 6074,
 '19.P3.pause-resume-activation': 7703,
 '19.P3.admission-holds-activation': 8124}

FILE_CHARS = {'chupa/daemon.py': 8906,
 'chupa/watcher.py': 2799,
 'chupa/mergequeue.py': 15499,
 'chupa/triage.py': 9510,
 'chupa/seams.py': 4322,
 'chupa/journal.py': 8656,
 'tests/test_effects.py': 6258,
 'tests/test_seeded_phase3_core.py': 5425}

DELIMITER_FREE_AT_AUTHORING = frozenset(FILE_CHARS)

AUTHORED = {'background-consumers': {'chars': 8144,
                          'plan': ('19.I', '19.P3.background-consumers'),
                          'context': ('chupa/daemon.py',
                                      'chupa/watcher.py',
                                      'chupa/mergequeue.py',
                                      'chupa/triage.py'),
                          'on_demand': (),
                          'fenced_existing': ('chupa/daemon.py',),
                          'created': ('tests/test_daemon_tasks.py',),
                          'measured_render': 56772},
 'control-inbox': {'chars': 11592,
                   'plan': ('19.I', '19.P3.control-inbox', '20'),
                   'context': ('chupa/daemon.py',
                               'chupa/seams.py',
                               'chupa/journal.py',
                               'tests/test_effects.py'),
                   'on_demand': (),
                   'fenced_existing': ('chupa/daemon.py',
                                       'chupa/seams.py',
                                       'tests/test_effects.py'),
                   'created': ('chupa/control.py', 'tests/test_control.py'),
                   'measured_render': 59062},
 'phase3-continue-08': {'chars': 30488,
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P3',
                                 '13',
                                 '20',
                                 '19.P3.dispatch-pause-boundary',
                                 '19.P3.pause-resume-activation',
                                 '19.P3.admission-holds-activation'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fenced_existing': (),
                        'created': ('tickets', 'tests/test_seeded_phase3_08.py'),
                        'measured_render': 122614}}

OBLIGATIONS = {'background-consumers': ('test_construction_is_idle',
                          'test_run_owns_three_concurrent_consumers',
                          'test_consumer_failure_cancels_and_awaits_siblings',
                          'test_run_cancellation_awaits_all_cleanup',
                          'test_watcher_debounce_tasks_do_not_outlive_owner',
                          'test_overlapping_run_is_refused_until_cleanup_finishes',
                          'test_merge_results_remain_consumer_owned',
                          'test_background_consumers_are_dormant'),
 'control-inbox': ('test_request_shape_and_identity_fail_closed',
                   'test_publication_is_durable_and_never_overwrites',
                   'test_publication_crash_points',
                   'test_publisher_never_writes_journal',
                   'test_decision_precedes_application',
                   'test_request_is_decided_once',
                   'test_decision_crash_reconstructs_projection',
                   'test_lifecycle_identity_never_retargets',
                   'test_resume_matches_only_its_hold',
                   'test_latest_accepted_pause_resume_wins',
                   'test_control_inbox_is_dormant')}

OWN_ENTRY_SHA256 = {'background-consumers': '8580c326a2856692e10df8c63b81cb7d0bc019fc8e076931e2ac32ad7d5396eb',
 'control-inbox': 'e42ec09d1f6e0550629eb8d15f7e6f5ebbbc71609bb793745db9efe0e2f21f84'}

NEXT_ENTRY_SHA256 = {'dispatch-pause-boundary': '80d05b5f62a957eba027a0b79e92f18397abfc8be877664b2c56893b9f7e8d74',
 'pause-resume-activation': '8b7586b4a25b5c410304ca2f40201863e96a27d1dbf773945ec8a663a644077f',
 'admission-holds-activation': 'cd07574503044f1cd1e89010a42a41087ca14926678df432974814b4244dff1b'}

VERIFICATION = {'background-consumers': ('uv',
                          'run',
                          'pytest',
                          'tests/test_daemon_tasks.py',
                          'tests/test_daemon_composition.py',
                          'tests/test_scheduler.py',
                          'tests/test_mergequeue.py',
                          'tests/test_triage.py',
                          'tests/test_cli.py',
                          'tests/test_drain.py'),
 'control-inbox': ('uv',
                   'run',
                   'pytest',
                   'tests/test_control.py',
                   'tests/test_cli.py',
                   'tests/test_drain.py',
                   'tests/test_daemon_composition.py',
                   'tests/test_effects.py'),
 'phase3-continue-08': ('uv', 'run', 'pytest', '-q', 'tests/test_seeded_phase3_08.py')}

PRESERVATION = {'background-consumers': ('tests/test_daemon_composition.py',
                          'tests/test_scheduler.py',
                          'tests/test_mergequeue.py',
                          'tests/test_triage.py',
                          'tests/test_cli.py',
                          'tests/test_drain.py'),
 'control-inbox': ('tests/test_cli.py', 'tests/test_drain.py', 'tests/test_daemon_composition.py')}



def render_chars(a, extra=()):
    return (IMPLEMENT_SPEC_CHARS + a["chars"] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[pid] for pid in a["plan"])
            + sum(FILE_CHARS[p] for p in (*a["context"], *extra)))


def _ticket(stem):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT, siblings=BATCH)


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert BATCH == ("background-consumers", "control-inbox", "phase3-continue-08")
    assert PAYLOADS == BATCH[:2]
    assert len(set(BATCH)) == 3 <= load_config(None, cwd=ROOT).seeding.max_seeds_per_admission
    assert set(EDGES) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(AUTHORED) == set(BATCH)


@pytest.mark.parametrize("stem", BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    fm = _ticket(stem).frontmatter
    # Later rejection is lifecycle history; confirmed is the authored birth.
    assert AUTHORED_STATE[stem] == "confirmed"
    assert fm.source == "seed" and fm.state in (AUTHORED_STATE[stem], "rejected")
    assert (fm.priority, fm.kind) == ("P1", "feature")
    assert (fm.agent_tier, fm.agent_effort) == ("medium", "medium")
    assert not fm.gate_bypass


@pytest.mark.parametrize("stem", BATCH)
def test_stuck_budget_fits_the_drain_envelope(stem):
    t = _ticket(stem)
    assert 0 < t.expected_minutes < t.stuck_minutes <= load_config(None, cwd=ROOT).drain.max_ticket_minutes


@pytest.mark.parametrize("stem", BATCH)
def test_dependencies_as_authored(stem):
    assert set(_ticket(stem).depends) == set(EDGES[stem])
    assert EDGES["background-consumers"] == ("phase3-continue-07",)
    assert EDGES["control-inbox"] == ("phase3-continue-07", "background-consumers")
    assert EDGES["phase3-continue-08"] == PAYLOADS


@pytest.mark.parametrize("stem", BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    t = _ticket(stem)
    assert set(t.scope_fence) == set(FENCE_FLOORS[stem]) | set(FENCE_ADDITIONS[stem])
    assert all(reason.startswith("CONTRADICTED TESTS/CALLER CLOSURE:")
               for reason in FENCE_ADDITIONS[stem].values())
    if stem in PAYLOADS:
        assert "chupa/__main__.py" not in t.scope_fence
        assert "tests/test_daemon_composition.py" not in t.scope_fence
    if stem == "control-inbox":
        assert set(FENCE_ADDITIONS[stem]) == {"tests/test_effects.py"}
        assert "test_fakes_satisfy_seam_protocols" in t.sections["Scope in / Scope out"]


@pytest.mark.parametrize("stem", PAYLOADS)
def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract(stem):
    t = _ticket(stem)
    expected = ("19.I", f"19.P3.{stem}", *(("20",) if stem == "control-inbox" else ()))
    assert t.plan_contract == AUTHORED[stem]["plan"] == expected
    scope = t.sections["Scope in / Scope out"]
    # Hash the complete carried entry: every owner, exact record and sole writer,
    # observable, crash/cleanup case, named test and full Verification command.
    entry = scope.split("\n\nCALLER CLOSURE:", 1)[0].split("\n\nCONSTRUCTION BOUNDARY:", 1)[0].strip()
    assert hashlib.sha256(entry.encode()).hexdigest() == OWN_ENTRY_SHA256[stem]
    assert all(f"- **{part}:**" in entry for part in ("Owner", "Records", "Observable", "Tests"))
    assert all(name in entry for name in OBLIGATIONS[stem])
    assert len(OBLIGATIONS[stem]) == (8 if stem == "background-consumers" else 11)
    assert "Daemon import absence is no longer evidence" in scope
    assert "calibrate raising" in scope and "deliberate wiring raises" in scope
    assert "CLI run/drain" in scope and "Leave chupa/__main__.py" in scope
    assert "inline admission, accounting, reconciliation, lock lifetime and terminals" in scope


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket("phase3-continue-08")
    assert t.plan_contract == AUTHORED[t.stem]["plan"] == (
        "19.L", "19.I", "19.P3", "13", "20", "19.P3.dispatch-pause-boundary",
        "19.P3.pause-resume-activation", "19.P3.admission-holds-activation",
    )
    assert t.context == (MERGED_IDIOM,) == ("tests/test_seeded_phase3_core.py",)
    assert t.scope_fence == ("tickets", "tests/test_seeded_phase3_08.py")
    assert len(AUTHORING_HEAD) == len(MERGED_IDIOM_BLOB) == 40
    assert MERGED_IDIOM_BLOB == "2feb2512789adbf84d57e9153d77d6a7a06edb8a"
    assert "admissions[8:]" in t.sections["Goal / Why"]
    scope = t.sections["Scope in / Scope out"]
    for stem, digest in NEXT_ENTRY_SHA256.items():
        first = scope.index("- **Owner:**", scope.index("The following complete") if stem != "admission-holds-activation" else scope.index("Carry its complete"))
        if stem == "pause-resume-activation":
            first = scope.index("- **Owner:**", first + 1)
        end = scope.find("\n\n- **Owner:**", first + 1)
        if stem == "pause-resume-activation":
            end = scope.index("\n\nCreate phase3-continue-09", first)
        if stem == "admission-holds-activation":
            end = scope.index("\n\nEach continuation", first)
        assert hashlib.sha256(scope[first:end].strip().encode()).hexdigest() == digest
    for fact in (
        "entry_unit_gap", "resolve_plan_contract", "section 11.4", "premise_failed",
        "BEGIN_REGISTRY_P3", "END_REGISTRY_P3", "admissions[9:]", "admissions[10:]",
        "Author only dispatch-pause-boundary, pause-resume-activation and phase3-continue-09",
        "pause-resume-activation seed explicitly depends on its dispatch-pause-boundary sibling",
        "depending on both dispatch-pause-boundary and pause-resume-activation",
        "The exact phase3-continue-09 Plan contract is 19.L, 19.I, 19.P3, section 13, section 20, "
        "19.P3.admission-holds-activation, 19.P3.kill-signal-journal, 19.P3.kill-executor-abort and section 6",
        "kill pair belongs to 09's citations, never 08's",
        "tests/test_seeded_phase3_09.py", "tests/test_seeded_phase3_core.py",
        "tests/test_control.py under ACTIVATION for test_control_inbox_is_dormant",
        "test_control_inbox_is_active", "19.L closure rules 2-5", "direct callers",
        "300,000-character headroom", "Prompt-specs and delimiter-bearing sources are never Context",
        "Preservation suites stay unchanged in Verification only, neither fenced nor embedded",
        "file sizes, ticket sizes and plan-unit lengths recorded IN that test",
        "terminal phase3-exit as its sole payload with no successor",
        "seeding.max_seeds_per_admission", "Deep rows start high/high; other rows medium/medium",
        "keep previously approved seeds verbatim", "ticket_sha", "chupa(phase3-continue-08): seeds",
        "Commit only this ticket's new test",
    ):
        assert fact in scope, fact
    assert t.verification == (VERIFICATION[t.stem], ("uv", "run", "pytest", "-q"))


@pytest.mark.parametrize("stem", BATCH)
def test_context_closure_and_max_effort_render_use_authoring_snapshots(stem):
    a, t = AUTHORED[stem], _ticket(stem)
    assert t.context == a["context"] and t.on_demand == a["on_demand"] == ()
    assert set(t.scope_fence) == set(a["fenced_existing"]) | set(a["created"])
    assert set(a["fenced_existing"]) <= set(a["context"]) | set(a["on_demand"])
    assert not set(a["created"]) & (set(a["context"]) | set(a["on_demand"]))
    assert not set(a["context"]) & set(a["on_demand"])
    assert set(a["context"]) <= DELIMITER_FREE_AT_AUTHORING
    assert not any(p.startswith("specs/") for p in a["context"])
    assert all(FILE_CHARS[p] > 0 for p in a["context"])
    assert all(PLAN_CHARS[pid] > 0 for pid in a["plan"])
    assert 0 < a["measured_render"] <= render_chars(a) <= HEADROOM_CHARS
    for path in a["on_demand"]:
        assert render_chars(a, (path,)) > HEADROOM_CHARS, path


@pytest.mark.parametrize("stem", PAYLOADS)
def test_payloads_run_preservation_suites_without_fencing_or_embedding_them(stem):
    t = _ticket(stem)
    assert t.verification == (VERIFICATION[stem], ("uv", "run", "pytest", "-q"))
    assert set(PRESERVATION[stem]) <= set(VERIFICATION[stem])
    assert "tests/test_daemon_composition.py" in PRESERVATION[stem]
    assert not set(PRESERVATION[stem]) & (set(t.scope_fence) | set(t.context) | set(t.on_demand))
