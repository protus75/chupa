"""Continuation 08: fixed authoring snapshots for two boundaries and their successor.

Authoring rg across chupa/, eval/ and tests/ covered pause/resume, ControlInbox,
control_inbox, ControlProjection, publish_request, DaemonAdmission, snapshot_dispatch,
daemon_core, build_daemon_core, drain, public allowlists and old absence values.
The optional checkpoint preserves existing caller shapes. The sole earned addition
is the control-inbox dormancy fixture, below. Preservation suites stay outside Context.
No live file sizes or plan-unit lengths participate in the historical render proof.
"""

import hashlib
from pathlib import Path

import pytest

from chupa.config import load_config
from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent

PAYLOADS = ('dispatch-pause-boundary', 'pause-resume-activation')

BATCH = ('dispatch-pause-boundary', 'pause-resume-activation', 'phase3-continue-09')

EDGES = {'dispatch-pause-boundary': ('phase3-continue-08',),
 'pause-resume-activation': ('phase3-continue-08', 'dispatch-pause-boundary'),
 'phase3-continue-09': ('dispatch-pause-boundary', 'pause-resume-activation')}

FENCE_FLOORS = {'dispatch-pause-boundary': ('chupa/daemon.py',
                             'chupa/drain.py',
                             'tests/test_daemon_pause.py',
                             'tests/test_drain.py'),
 'pause-resume-activation': ('chupa/daemon.py',
                             'chupa/control.py',
                             'chupa/drain.py',
                             'chupa/__main__.py',
                             'tests/test_daemon_pause.py',
                             'tests/test_control_cli.py',
                             'tests/test_daemon_composition.py'),
 'phase3-continue-09': ('tickets', 'tests/test_seeded_phase3_09.py')}

FENCE_ADDITIONS = {'dispatch-pause-boundary': {},
 'pause-resume-activation': {'tests/test_control.py': 'ACTIVATION: test_control_inbox_is_dormant '
                                                      'pins production absence and run/drain '
                                                      'no-consumption; migrate only that assertion '
                                                      'to test_control_inbox_is_active.'},
 'phase3-continue-09': {}}

AUTHORING_HEAD = 'a695f669770e0ed5098847f3c56ca298e24c9ee1'

MERGED_IDIOM = 'tests/test_seeded_phase3_core.py'

MERGED_IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

AUTHORED_STATE = {'dispatch-pause-boundary': 'confirmed',
 'pause-resume-activation': 'confirmed',
 'phase3-continue-09': 'confirmed'}

APPROVED_SEED_SHA256 = '1eb19034973e4f595a53dd26702ecc4e05d67acbcb850475cf9637fca2d33d35'

HEADROOM_CHARS = 300000

IMPLEMENT_SPEC_CHARS = 4316

RENDER_OVERHEAD = 2000

PLAN_CHARS = {'19.I': 1811,
 '19.P3.dispatch-pause-boundary': 6074,
 '20': 4367,
 '19.P3.pause-resume-activation': 9293,
 '19.L': 19167,
 '19.P3': 16053,
 '13': 19104,
 '19.P3.admission-holds-activation': 8124,
 '19.P3.kill-signal-journal': 5337,
 '19.P3.kill-executor-abort': 5396,
 '6': 36580}

FILE_CHARS = {'chupa/daemon.py': 11004,
 'chupa/drain.py': 21939,
 'chupa/control.py': 6968,
 'tests/test_drain.py': 31876,
 'chupa/__main__.py': 6815,
 'tests/test_daemon_composition.py': 55815,
 'tests/test_control.py': 18540,
 'chupa/seams.py': 5551,
 'chupa/lockfile.py': 3273,
 'tests/test_seeded_phase3_core.py': 5425}

DELIMITER_FREE_AT_AUTHORING = ('chupa/daemon.py',
 'chupa/drain.py',
 'chupa/control.py',
 'tests/test_drain.py',
 'chupa/__main__.py',
 'tests/test_daemon_composition.py',
 'tests/test_control.py',
 'chupa/seams.py',
 'chupa/lockfile.py',
 'tests/test_seeded_phase3_core.py')

AUTHORED = {'dispatch-pause-boundary': {'chars': 9337,
                             'plan': ('19.I', '19.P3.dispatch-pause-boundary', '20'),
                             'context': ('chupa/daemon.py',
                                         'chupa/drain.py',
                                         'chupa/control.py',
                                         'tests/test_drain.py'),
                             'on_demand': (),
                             'fenced_existing': ('chupa/daemon.py',
                                                 'chupa/drain.py',
                                                 'tests/test_drain.py'),
                             'created': ('tests/test_daemon_pause.py',),
                             'measured_render': 97727},
 'pause-resume-activation': {'chars': 14943,
                             'plan': ('19.I', '19.P3.pause-resume-activation', '20'),
                             'context': ('chupa/daemon.py',
                                         'chupa/control.py',
                                         'chupa/drain.py',
                                         'chupa/__main__.py',
                                         'tests/test_daemon_composition.py',
                                         'tests/test_control.py',
                                         'chupa/seams.py',
                                         'chupa/lockfile.py'),
                             'on_demand': (),
                             'fenced_existing': ('chupa/daemon.py',
                                                 'chupa/control.py',
                                                 'chupa/drain.py',
                                                 'chupa/__main__.py',
                                                 'tests/test_daemon_composition.py',
                                                 'tests/test_control.py'),
                             'created': ('tests/test_daemon_pause.py', 'tests/test_control_cli.py'),
                             'measured_render': 164780},
 'phase3-continue-09': {'chars': 27607,
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P3',
                                 '13',
                                 '20',
                                 '19.P3.admission-holds-activation',
                                 '19.P3.kill-signal-journal',
                                 '19.P3.kill-executor-abort',
                                 '6'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fenced_existing': (),
                        'created': ('tickets', 'tests/test_seeded_phase3_09.py'),
                        'measured_render': 153269}}

OWN_ENTRY_SHA256 = {'dispatch-pause-boundary': '80d05b5f62a957eba027a0b79e92f18397abfc8be877664b2c56893b9f7e8d74',
 'pause-resume-activation': '347fd54abc3e6ee90e08596806cb86467ccebce5cb0cd0fc8ce58161c71ee628'}

NEXT_ENTRY_SHA256 = {'admission-holds-activation': 'cd07574503044f1cd1e89010a42a41087ca14926678df432974814b4244dff1b',
 'kill-signal-journal': '016e237e308a72535b7191936032f9fbf0c3da7b51818056a3046c860677f106',
 'kill-executor-abort': 'bb6a9c45541b8018cfee67e3dde7360a814b2c0d8ed7e8865f73ba4fa869dfe8'}

OBLIGATIONS = {'dispatch-pause-boundary': ('test_pause_checkpoint_precedes_dispatch_and_snapshot',
                             'test_pause_does_not_preempt_active_dispatch',
                             'test_only_matching_resume_releases_pause',
                             'test_checkpoint_failure_and_cancellation_leave_no_dispatch',
                             'test_dispatch_pause_boundary_is_dormant',
                             'test_pause_precedes_fresh_offer_accounting',
                             'test_pause_precedes_retry_cap_draw',
                             'test_pause_precedes_machine_keep',
                             'test_pause_release_rechecks_eligibility_and_budget',
                             'test_pause_checkpoint_failure_spends_no_retry',
                             'test_pause_preserves_free_premise_and_spec_gap_reoffers'),
 'pause-resume-activation': ('test_live_pause_resume_publish_without_journal_write',
                             'test_resume_requires_current_pause_identity',
                             'test_pause_resume_apply_directly_under_lock',
                             'test_control_routing_lock_and_restart_races',
                             'test_production_composes_one_pause_consumer',
                             'test_live_drain_pause_blocks_all_offer_accounting',
                             'test_live_drain_resume_rechecks_selection_and_caps',
                             'test_control_lifecycle_cleanup_on_exit_and_handoff',
                             'test_dispatch_pause_boundary_is_dormant',
                             'test_dispatch_pause_boundary_is_active',
                             'test_control_inbox_is_dormant',
                             'test_control_inbox_is_active')}

VERIFICATION = {'dispatch-pause-boundary': ('uv',
                             'run',
                             'pytest',
                             'tests/test_daemon_pause.py',
                             'tests/test_drain.py',
                             'tests/test_daemon_admission.py',
                             'tests/test_daemon_config.py',
                             'tests/test_control.py',
                             'tests/test_daemon_composition.py'),
 'pause-resume-activation': ('uv',
                             'run',
                             'pytest',
                             'tests/test_daemon_pause.py',
                             'tests/test_control_cli.py',
                             'tests/test_daemon_composition.py',
                             'tests/test_control.py',
                             'tests/test_drain.py',
                             'tests/test_cli.py',
                             'tests/test_daemon_admission.py',
                             'tests/test_daemon_config.py'),
 'phase3-continue-09': ('uv', 'run', 'pytest', '-q', 'tests/test_seeded_phase3_09.py')}

PRESERVATION = {'dispatch-pause-boundary': ('tests/test_daemon_admission.py',
                             'tests/test_daemon_config.py',
                             'tests/test_control.py',
                             'tests/test_daemon_composition.py'),
 'pause-resume-activation': ('tests/test_drain.py',
                             'tests/test_cli.py',
                             'tests/test_daemon_admission.py',
                             'tests/test_daemon_config.py')}

CLOSURE_CALLERS = {'DaemonAdmission': ('chupa/daemon.py',
                     'tests/test_daemon_admission.py',
                     'tests/test_daemon_config.py'),
 'daemon_core': ('chupa/__main__.py',),
 'build_daemon_core': ('tests/test_daemon_composition.py', 'tests/test_control.py'),
 'control_inbox': ('tests/test_control.py',),
 'compose_pipeline_next_admission': ('chupa/runner.py',
                                     'eval/shakeout/bench.py',
                                     'tests/test_merge.py',
                                     'tests/test_daemon_composition.py')}


def render_chars(a, extra=()):
    # Conservative header/separator allowance, identical bound at maximum effort.
    return (IMPLEMENT_SPEC_CHARS + a["chars"] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[pid] for pid in a["plan"])
            + sum(FILE_CHARS[path] for path in (*a["context"], *extra)))


def _ticket(stem):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT, siblings=BATCH)


def _entry_digest(text):
    return hashlib.sha256(text.strip().encode()).hexdigest()


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert BATCH == ("dispatch-pause-boundary", "pause-resume-activation", "phase3-continue-09")
    assert PAYLOADS == BATCH[:2]
    assert len(set(BATCH)) == 3 <= load_config(None, cwd=ROOT).seeding.max_seeds_per_admission
    assert set(EDGES) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(AUTHORED) == set(BATCH)


@pytest.mark.parametrize("stem", BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    fm = _ticket(stem).frontmatter
    # Rejection is later lifecycle history, never a different seed birth.
    assert AUTHORED_STATE[stem] == "confirmed"
    assert fm.source == "seed" and fm.state in (AUTHORED_STATE[stem], "rejected")
    assert (fm.priority, fm.kind, fm.agent_tier, fm.agent_effort) == ("P1", "feature", "medium", "medium")
    assert not fm.gate_bypass


@pytest.mark.parametrize("stem", BATCH)
def test_stuck_budget_fits_the_drain_envelope(stem):
    t = _ticket(stem)
    assert 0 < t.expected_minutes < t.stuck_minutes <= load_config(None, cwd=ROOT).drain.max_ticket_minutes


@pytest.mark.parametrize("stem", BATCH)
def test_dependencies_as_authored(stem):
    assert set(_ticket(stem).depends) == set(EDGES[stem])
    assert EDGES[PAYLOADS[0]] == ("phase3-continue-08",)
    assert EDGES[PAYLOADS[1]] == ("phase3-continue-08", "dispatch-pause-boundary")
    assert EDGES[BATCH[-1]] == PAYLOADS


@pytest.mark.parametrize("stem", BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    t = _ticket(stem)
    assert set(t.scope_fence) == set(FENCE_FLOORS[stem]) | set(FENCE_ADDITIONS[stem])
    assert FENCE_ADDITIONS[PAYLOADS[0]] == FENCE_ADDITIONS[BATCH[-1]] == {}
    assert set(FENCE_ADDITIONS[PAYLOADS[1]]) == {"tests/test_control.py"}
    assert all(reason.startswith("ACTIVATION:") for reason in FENCE_ADDITIONS[stem].values())
    if stem == PAYLOADS[1]:
        scope = t.sections["Scope in / Scope out"]
        assert "test_control_inbox_is_dormant" in scope and "test_control_inbox_is_active" in scope
        assert "19.L ACTIVATION" in scope and "sole addition" in scope
        assert "no mandatory constructor change" in scope
        assert "chupa/runner.py" not in t.scope_fence
    assert CLOSURE_CALLERS["daemon_core"] == ("chupa/__main__.py",)
    assert CLOSURE_CALLERS["control_inbox"] == ("tests/test_control.py",)


@pytest.mark.parametrize("stem", PAYLOADS)
def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract(stem):
    t = _ticket(stem)
    assert t.plan_contract == AUTHORED[stem]["plan"] == ("19.I", f"19.P3.{stem}", "20")
    scope = t.sections["Scope in / Scope out"]
    entry = scope.split("\n\nAUTHORING CLOSURE:", 1)[0].strip()
    # Complete fixed entry digest pins every owner, record shape, writer, observable,
    # named invariant and full Verification, without following a later live plan.
    assert _entry_digest(entry) == OWN_ENTRY_SHA256[stem]
    assert all(f"- **{label}:**" in entry for label in ("Owner", "Records", "Observable", "Tests"))
    assert all(name in entry for name in OBLIGATIONS[stem])
    assert len(OBLIGATIONS[stem]) == (11 if stem == PAYLOADS[0] else 12)
    assert "inline admission, accounting, reconciliation, lock lifetime and terminals" in scope
    assert "kill" in scope and "admission/storm holds" in scope and "serve" in scope
    if stem == PAYLOADS[0]:
        assert "calibrate raising before_dispatch probes" in scope
        assert "ordinary CLI run/drain" in scope and "explicit wiring" in scope
        # Match the previously approved bytes even when the contract is regenerated.
        text = (ROOT / ticket_path(stem)).read_text().replace("state: rejected", "state: confirmed", 1)
        assert hashlib.sha256(text.encode()).hexdigest() == APPROVED_SEED_SHA256
    else:
        for fact in ("nothing running to pause", "nothing running to resume", "b\"null\\n\"",
                     "FileSystem.write", "test_dispatch_pause_boundary_is_active",
                     "test_control_inbox_is_active", "consume()", "recover()", "LockHeld",
                     "deliberate removal or misordering", "injected async wakeup"):
            assert fact in scope, fact


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket(BATCH[-1])
    assert t.plan_contract == AUTHORED[t.stem]["plan"] == (
        "19.L", "19.I", "19.P3", "13", "20", "19.P3.admission-holds-activation",
        "19.P3.kill-signal-journal", "19.P3.kill-executor-abort", "6",
    )
    assert t.context == (MERGED_IDIOM,) == ("tests/test_seeded_phase3_core.py",)
    assert t.scope_fence == ("tickets", "tests/test_seeded_phase3_09.py")
    assert len(AUTHORING_HEAD) == len(MERGED_IDIOM_BLOB) == 40
    assert MERGED_IDIOM_BLOB == "2feb2512789adbf84d57e9153d77d6a7a06edb8a"
    assert "admissions[9:]" in t.sections["Goal / Why"]
    scope = t.sections["Scope in / Scope out"]
    admission = scope.split("Carry this complete admission-holds-activation contract verbatim:\n\n", 1)[1]
    admission = admission.split("\n\nCreate phase3-continue-10", 1)[0]
    kills = scope.split("Carry their complete own entries into phase3-continue-10 as follows:\n\n", 1)[1]
    kills = kills.split("\n\nEach continuation", 1)[0]
    signal, abort = kills.split("\n\n- **Owner:**", 1)
    for stem, carried in (("admission-holds-activation", admission),
                          ("kill-signal-journal", signal), ("kill-executor-abort", "- **Owner:**" + abort)):
        assert _entry_digest(carried) == NEXT_ENTRY_SHA256[stem]
    for fact in (
        "BEGIN_REGISTRY_P3", "END_REGISTRY_P3", "admissions[9:]", "admissions[10:]", "admissions[11:]",
        "entry_unit_gap", "resolve_plan_contract", "section 11.4", "premise_failed",
        "Author only admission-holds-activation and phase3-continue-10",
        "depends on phase3-continue-09 and its registry dependency pause-resume-activation",
        "depending on admission-holds-activation", "19.L closure rules 2-5",
        "every direct caller", "chupa/runner.py", "eval/shakeout/bench.py", "no fallback second inbox",
        "tests/test_seeded_phase3_10.py", "tests/test_seeded_phase3_core.py",
        "never this batch's tests/test_seeded_phase3_09.py",
        "19.P3.kill-worker-stop", "19.P3.kill-failure-suppression",
        "citations belong to phase3-continue-10", "shared inbox", "never acquire admission holds",
        "300,000-character headroom", "Prompt-specs and delimiter-bearing sources are never Context",
        "Preservation suites stay unchanged in Verification only, neither fenced nor embedded",
        "file sizes, ticket sizes and plan-unit lengths recorded IN that test",
        "Record authoring head, merged idiom blob and measurements", "Never migrate historical seeding tests",
        "seeding.max_seeds_per_admission", "Deep rows start high/high; other rows medium/medium",
        "terminal phase3-exit as its sole payload with no successor",
        "keep previously approved seeds verbatim", "ticket_sha", "chupa(phase3-continue-09): seeds",
        "Commit only this ticket's new test",
    ):
        assert fact in scope, fact
    assert ("The exact phase3-continue-10 Plan contract is 19.L, 19.I, 19.P3, section 13, section 20, "
            "19.P3.kill-signal-journal, 19.P3.kill-executor-abort, 19.P3.kill-worker-stop, "
            "19.P3.kill-failure-suppression and section 6") in scope
    for name in (
        "test_named_stems_cover_exactly_this_admission_and_successor",
        "test_seed_passes_intake_lint_with_confirmed_seed_birth", "test_stuck_budget_fits_the_drain_envelope",
        "test_dependencies_as_authored", "test_fence_contains_its_floor_and_only_earned_additions",
        "test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract",
        "test_successor_cites_next_admission_and_embeds_merged_earlier_idiom",
        "test_context_closure_and_max_effort_render_use_authoring_snapshots",
        "test_payloads_run_preservation_suites_without_fencing_or_embedding_them",
    ):
        assert name in scope
    assert t.verification == (VERIFICATION[t.stem], ("uv", "run", "pytest", "-q"))


@pytest.mark.parametrize("stem", BATCH)
def test_context_closure_and_max_effort_render_use_authoring_snapshots(stem):
    a, t = AUTHORED[stem], _ticket(stem)
    assert t.context == a["context"] and t.on_demand == a["on_demand"]
    assert set(t.scope_fence) == set(a["fenced_existing"]) | set(a["created"])
    assert set(a["fenced_existing"]) <= set(a["context"]) | set(a["on_demand"])
    assert not set(a["created"]) & (set(a["context"]) | set(a["on_demand"]))
    assert not set(a["context"]) & set(a["on_demand"])
    assert set(a["context"]) <= set(DELIMITER_FREE_AT_AUTHORING)
    assert not any(p.startswith("specs/") for p in a["context"])
    assert all(FILE_CHARS[p] > 0 for p in a["context"])
    assert all(PLAN_CHARS[pid] > 0 for pid in a["plan"])
    assert 0 < a["measured_render"] <= render_chars(a) <= HEADROOM_CHARS
    for path in a["on_demand"]:
        assert render_chars(a, (path,)) > HEADROOM_CHARS, path
    if stem == PAYLOADS[1]:
        assert {"tests/test_daemon_pause.py", "tests/test_control_cli.py"} == set(a["created"])
        assert "tests/test_control.py" in a["fenced_existing"]


@pytest.mark.parametrize("stem", PAYLOADS)
def test_payloads_run_preservation_suites_without_fencing_or_embedding_them(stem):
    t = _ticket(stem)
    assert t.verification == (VERIFICATION[stem], ("uv", "run", "pytest", "-q"))
    assert set(PRESERVATION[stem]) <= set(VERIFICATION[stem])
    assert not set(PRESERVATION[stem]) & (set(t.scope_fence) | set(t.context) | set(t.on_demand))
