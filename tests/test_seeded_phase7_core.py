
"""Phase 7 core authoring snapshots; plan and render operands stay historical.

Implement emits three uncommitted seed files. Check owns per-seed review and
the single ticket-plane lift; this fixture never writes approval records.
"""

import hashlib
import re
from pathlib import Path

import pytest
import yaml

from chupa.tickets import _sections, split_frontmatter, ticket_path

ROOT = Path(__file__).resolve().parents[1]
RENDER_BOUND_CHARS = 400_000
REQ_RENDER_HEADROOM = 0.75
HEADROOM_CHARS = 300_000
RENDER_EFFORT = "max"
BATCH = ("review-spec-readonly", "implement-consumer-read", "phase7-continue")
PAYLOADS = BATCH[:2]
POSITION = 1
UNSEEDED_SUFFIX = (("host-mechanical-check",), ("host-review-surfaces",), ("phase7-exit",))

AUTHORING_HEAD = '7ed35d85e0eaf7b309e5c33c3cc48fb2919e268d'

IDIOM_BLOB = '6784b31785ee00622b30643579c6511bebc3132d'

REQUIRED = {'review-spec-readonly': ('19.P7.review-spec-readonly',),
 'implement-consumer-read': ('19.P7.implement-consumer-read',),
 'phase7-continue': ('19.P7.host-mechanical-check',)}

ENTRY_DEPTH = {'19.P7.review-spec-readonly': {'bytes': 1549,
                                'chars': 1549,
                                'sha256': 'b6cc86d302846e2aef31931262a0170dd129d6de108d4a03781ead37fa3157ba',
                                'resolves': 1,
                                'gap': None,
                                'parts': {'Owner': 132,
                                          'Records': 656,
                                          'Observable': 189,
                                          'Tests': 432},
                                'missing_part_rejected': {'Owner': True,
                                                          'Records': True,
                                                          'Observable': True,
                                                          'Tests': True},
                                'missing_unit_rejected': True,
                                'duplicate_unit_rejected': True,
                                'tests': ('test_specs',
                                          'test_review_spec_read_only',
                                          'test_review_spec_readonly_entry_unit')},
 '19.P7.implement-consumer-read': {'bytes': 1451,
                                   'chars': 1451,
                                   'sha256': '6dbec1e06a3a1a6f688935b338038e84bbdd5e3f2df34f6b22ca3e1ff725bd0c',
                                   'resolves': 1,
                                   'gap': None,
                                   'parts': {'Owner': 126,
                                             'Records': 685,
                                             'Observable': 142,
                                             'Tests': 354},
                                   'missing_part_rejected': {'Owner': True,
                                                             'Records': True,
                                                             'Observable': True,
                                                             'Tests': True},
                                   'missing_unit_rejected': True,
                                   'duplicate_unit_rejected': True,
                                   'tests': ('test_specs',
                                             'test_implement_spec_consumer_read',
                                             'test_implement_consumer_read_entry_unit')},
 '19.P7.host-mechanical-check': {'bytes': 2559,
                                 'chars': 2559,
                                 'sha256': 'e3ca41fdb7a083060afc160a3c5b890c9c4175a061c87c059819155e0dfc10c6',
                                 'resolves': 1,
                                 'gap': None,
                                 'parts': {'Owner': 516,
                                           'Records': 976,
                                           'Observable': 396,
                                           'Tests': 525},
                                 'missing_part_rejected': {'Owner': True,
                                                           'Records': True,
                                                           'Observable': True,
                                                           'Tests': True},
                                 'missing_unit_rejected': True,
                                 'duplicate_unit_rejected': True,
                                 'tests': ('test_host_mechanical',
                                           'test_triggered_entries_run_at_check',
                                           'test_untriggered_entry_never_runs',
                                           'test_hard_failure_fails_check',
                                           'test_soft_failure_reported_and_passes',
                                           'test_gate_bypass_demotes_entry',
                                           'test_base_red_entry_is_preexisting',
                                           'test_structured_findings_and_crash_fail_closed',
                                           'test_inline_merge_reruns_triggered_hard_entries',
                                           'test_host_mechanical_entry_unit',
                                           'test_stages',
                                           'test_merge')}}

PLAN_SIZES = {'19.I': {'bytes': 1811,
          'chars': 1811,
          'sha256': 'cfc0b1be4cfe88be240b6ae604660bd9d27a660cebbd7cad73ceca448091553c'},
 '19.P7.review-spec-readonly': {'bytes': 1549,
                                'chars': 1549,
                                'sha256': 'b6cc86d302846e2aef31931262a0170dd129d6de108d4a03781ead37fa3157ba'},
 '8': {'bytes': 8712,
       'chars': 8712,
       'sha256': '7024a6dc821bad113cc141046646426ee3c397bc3f877f27bbf2dae6b5e53ae1'},
 '19.P7.implement-consumer-read': {'bytes': 1451,
                                   'chars': 1451,
                                   'sha256': '6dbec1e06a3a1a6f688935b338038e84bbdd5e3f2df34f6b22ca3e1ff725bd0c'},
 '19.L': {'bytes': 21595,
          'chars': 21595,
          'sha256': '56b9fc424b7de80dceb1f925f4d18efcb28ba66769444f40708022c96ace614f'},
 '19.P7': {'bytes': 3478,
           'chars': 3478,
           'sha256': '1716018aceacc08bf5287671df7a42fd8183ded68db06b7d46a43998c1b242d9'},
 '13': {'bytes': 19840,
        'chars': 19840,
        'sha256': '62498fb56d1b5fae322306359b35345a8c0beae1f40c670c7fb5d5722b0a649f'},
 '19.P7.host-mechanical-check': {'bytes': 2559,
                                 'chars': 2559,
                                 'sha256': 'e3ca41fdb7a083060afc160a3c5b890c9c4175a061c87c059819155e0dfc10c6'},
 '7': {'bytes': 8173,
       'chars': 8173,
       'sha256': '5946c32455a2d8859111c4b56e2674de365f2e60da9eeb1b98776ba3c4f6e2c7'}}

FILE_SIZES = {'chupa/specs.py': {'bytes': 23574,
                    'chars': 23574,
                    'sha256': 'e5e90b4a6582e8c843109239627e4c793d6e424593576ad9ee84817b84f29260'},
 'tests/test_specs.py': {'bytes': 16525,
                         'chars': 16525,
                         'sha256': '1af6a74e5f04849e80a723169b8062c23a1fe4c3b26af3694d42bde0e02b9cab'},
 'tests/test_stages.py': {'bytes': 40602,
                          'chars': 40602,
                          'sha256': '1e0538db5fad683491a28ec8b20475cdd416124daf28dfefeb4ac58a8c1182ea'},
 'specs/review.md': {'bytes': 3633,
                     'chars': 3633,
                     'sha256': '53f50ff48cfee1adf1deb3fb1d22b8757488273c39a2660d5cc156d6e7eeb116'},
 'specs/implement.md': {'bytes': 5306,
                        'chars': 5306,
                        'sha256': 'f5d3ba603570a56f661a24d7a52d7e4543c0d003a82e36d664f5ef73f3599ddb'},
 'tests/test_seeded_phase6_01.py': {'bytes': 57492,
                                    'chars': 57492,
                                    'sha256': '735465971d2bb73e92e29e7b25ed9d6690b400268fa95044c786dab85befaabe'}}

DELIMITER_FREE_CONTEXT = {'chupa/specs.py': True,
 'tests/test_specs.py': True,
 'tests/test_stages.py': True,
 'specs/review.md': False,
 'specs/implement.md': False,
 'tests/test_seeded_phase6_01.py': True}

IMPLEMENT_BODY_CHARS = 5185

MAX_SEEDS_PER_ADMISSION = 3

DRAIN_MAX_TICKET_MINUTES = 180

SCAN_PATTERN = ('specs/(review|implement)\\.md|implement 1\\.4|review\\.spec_version|\\(\\(\\"implement\\", '
 '\\"1\\.4\\"|Verification.*would not '
 'pass|SPEC_SECTIONS|SPEC_MAX_LINES|spec_version.*1\\.0|version.*1\\.4')

CLOSURE_SCAN = {'chupa': {'bytes': 904,
           'chars': 904,
           'sha256': '8151fe8ac4a77f97c31beb9e0138e994701c8931bca71c9022a7c1eabc604049',
           'matched_lines': 10,
           'matches': ['chupa/specs.py:30:SPEC_SECTIONS = ("Role", "Task", "Inputs", "Output '
                       'format", "On-failure")',
                       'chupa/specs.py:31:SPEC_MAX_LINES = 200',
                       'chupa/specs.py:146:    max_lines: int = SPEC_MAX_LINES,',
                       'chupa/specs.py:157:    max_lines: int = SPEC_MAX_LINES,',
                       'chupa/specs.py:197:    if headings != SPEC_SECTIONS:',
                       'chupa/specs.py:199:                      f"use exactly the sections '
                       '{list(SPEC_SECTIONS)}, in that order, each once"))',
                       "chupa/artifacts.py:281:# specs/review.md's closed finding codes: `ticket` "
                       'is the rma code, the rest are snag codes.',
                       'chupa/artifacts.py:286:    """The review surface\'s model-facing reply '
                       '(specs/review.md); the stage stamps provenance around it."""',
                       'chupa/stages.py:78:    """The implement surface\'s model-facing reply '
                       '(specs/implement.md); the stage stamps provenance."""',
                       'chupa/stages.py:1349:    """specs/review.md wired UNCHANGED: the same spec '
                       'and inputs the review baseline measured."""']},
 'eval': {'bytes': 305,
          'chars': 305,
          'sha256': '9f270232d2dbe08059a15edd76cd09cc654eabc235a233cb6290a8d577882b7b',
          'matched_lines': 3,
          'matches': ['eval/diagnose_report.json:4:  "spec_version": "1.0",',
                      'eval/harness.py:3:`run` drives specs/review.md over the fixtures with a '
                      'shared USD 5 cap and journals one NO_GO signal.',
                      'eval/harness.py:501:    run = sub.add_parser("run", help="score '
                      'specs/review.md over eval/fixtures and journal the verdict signal")']},
 'tests': {'bytes': 2351,
           'chars': 2351,
           'sha256': '1b83453281ecb165fcf1eae1670ffdc328d2305581dd5db00e82a9d7f8b753dd',
           'matched_lines': 20,
           'matches': ['tests/test_author.py:262:                       "overcorrection_risk": '
                       '"useful inputs", "proposed_spec_paths": ["specs/review.md"]}, '
                       '"confirmed"),',
                       'tests/test_author.py:373:    box.record_verdict(message_id, '
                       'Verdict(verdict="author", produced_by_spec_version="1.0", '
                       'rationale="broken"))',
                       'tests/test_retro.py:61:    report = render_report(initial, facts, {"head": '
                       '"actual-head", "spec_version": "1.0"}, [],',
                       'tests/test_retro.py:63:    assert report == render_report(initial, facts, '
                       '{"head": "actual-head", "spec_version": "1.0"}, [],',
                       'tests/test_retro.py:291:                "proposed_spec_paths": '
                       '["specs/review.md"]}',
                       'tests/test_eval_harness.py:195:            "exercised": {"surface": '
                       '"review", "tier": "high", "effort": "high", "spec_version": "1.0"},',
                       'tests/test_triage.py:124:    assert '
                       'box.get(ids[2]).verdict.produced_by_spec_version == "1.0"',
                       'tests/test_triage.py:310:        box.record_verdict(id, '
                       'Verdict(verdict="author", produced_by_spec_version="1.0", rationale="new '
                       'evidence"))',
                       'tests/test_daemon_soak.py:120:        "produced_by_spec_version": [True, '
                       '"1", 1.0],',
                       'tests/test_box.py:192:    box.record_verdict(id, '
                       'Verdict(verdict="tombstone", produced_by_spec_version="1.0", '
                       'rationale="prior match"))',
                       'tests/test_tickets.py:244:        ("- chupa/thing.py\\n\\n## Plan", "- '
                       'specs/review.md\\n\\n## Plan", "prompt spec"),',
                       'tests/test_mergequeue.py:65:                             '
                       'spec_version="1.0", provider="fake", model="fake")',
                       'tests/test_closed_sets.py:160:    assert specs.SPEC_MAX_LINES == 200',
                       "tests/test_closed_sets.py:161:    assert specs.SPEC_SECTIONS == ('Role', "
                       "'Task', 'Inputs', 'Output format', 'On-failure')",
                       'tests/test_retro_box.py:29:            "proposed_spec_paths": '
                       '["specs/review.md", "specs/author.md"]}',
                       'tests/test_retro_box.py:53:    authored["ticket"] = '
                       'authored["ticket"].replace("`chupa/thing.py`", '
                       '"`specs/review.md`").replace(',
                       'tests/test_retro_box.py:55:    authored["ticket"] = '
                       'authored["ticket"].replace("uv run pytest", "test -f specs/review.md")',
                       'tests/test_stages.py:353:    assert isinstance(review, ApprovedInvoice) '
                       'and review.reviewed_sha == head and review.spec_version == "1.0"',
                       'tests/test_stages.py:362:    assert "## Outcome\\n\\nok\\n" in run_md and '
                       '"- provider: fake\\n- model: fake\\n- spec: implement 1.4" in run_md',
                       'tests/test_specs.py:166:    for name, version in (("implement", "1.4"), '
                       '("requisition_review", "2.2")):']}}

SPEC_BASELINES = {'review': {'version': '1.0', 'placeholders': ('ticket', 'diff', 'retry_findings')},
 'implement': {'version': '1.4',
               'placeholders': ('ticket', 'plan_contract', 'context', 'retry_findings')}}

AUTHORED = {'review-spec-readonly': {'bytes': 2577,
                          'chars': 2577,
                          'sha256': '82a49613086fe7f2e6fc0550f41c8e995b7e5b5aa2a44b81e0a5b3f72fa21db6',
                          'plan': ('19.I', '19.P7.review-spec-readonly', '8'),
                          'citations': ('19.I', '19.P7.review-spec-readonly', 'section 8'),
                          'context': ('chupa/specs.py',
                                      'tests/test_specs.py',
                                      'tests/test_stages.py'),
                          'on_demand': (),
                          'fence': ('specs/review.md',
                                    'tests/test_specs.py',
                                    'tests/test_stages.py'),
                          'existing_fence': ('specs/review.md',
                                             'tests/test_specs.py',
                                             'tests/test_stages.py'),
                          'embedded_fence': ('tests/test_specs.py', 'tests/test_stages.py'),
                          'prompt_sources': ('specs/review.md',),
                          'created': (),
                          'depends': ('phase7-core',),
                          'expected': 30,
                          'stuck': 60,
                          'actual_render': 100552,
                          'render_effort': 'max',
                          'render_overhead': 17,
                          'grammar_valid': True,
                          'grammar_rejections': {'invalid_state': True,
                                                 'invalid_source': True,
                                                 'missing_role_citation': True}},
 'implement-consumer-read': {'bytes': 2814,
                             'chars': 2814,
                             'sha256': '294292c72c9c4297d8f05307557a93258ed88650b686f0366e304fed74cb0daa',
                             'plan': ('19.I', '19.P7.implement-consumer-read', '8'),
                             'citations': ('19.I', '19.P7.implement-consumer-read', 'section 8'),
                             'context': ('chupa/specs.py',
                                         'tests/test_specs.py',
                                         'tests/test_stages.py'),
                             'on_demand': (),
                             'fence': ('specs/implement.md',
                                       'tests/test_specs.py',
                                       'tests/test_stages.py'),
                             'existing_fence': ('specs/implement.md',
                                                'tests/test_specs.py',
                                                'tests/test_stages.py'),
                             'embedded_fence': ('tests/test_specs.py', 'tests/test_stages.py'),
                             'prompt_sources': ('specs/implement.md',),
                             'created': (),
                             'depends': ('phase7-core',),
                             'expected': 30,
                             'stuck': 60,
                             'actual_render': 100691,
                             'render_effort': 'max',
                             'render_overhead': 17,
                             'grammar_valid': True,
                             'grammar_rejections': {'invalid_state': True,
                                                    'invalid_source': True,
                                                    'missing_role_citation': True}},
 'phase7-continue': {'bytes': 5689,
                     'chars': 5689,
                     'sha256': 'b5d676377cfd839e6a7b05e559f712b92d95494afdb54148297296880d3977e1',
                     'plan': ('19.L',
                              '19.I',
                              '19.P7',
                              '13',
                              '19.P7.host-mechanical-check',
                              '7',
                              '8'),
                     'citations': ('19.L',
                                   '19.I',
                                   '19.P7',
                                   'section 13',
                                   '19.P7.host-mechanical-check',
                                   'section 7',
                                   'section 8'),
                     'context': ('tests/test_seeded_phase6_01.py',),
                     'on_demand': (),
                     'fence': ('tickets', 'tests/test_seeded_phase7_01.py'),
                     'existing_fence': (),
                     'embedded_fence': (),
                     'prompt_sources': (),
                     'created': ('tickets', 'tests/test_seeded_phase7_01.py'),
                     'depends': ('review-spec-readonly', 'implement-consumer-read'),
                     'expected': 60,
                     'stuck': 90,
                     'actual_render': 134514,
                     'render_effort': 'max',
                     'render_overhead': -20,
                     'grammar_valid': True,
                     'grammar_rejections': {'invalid_state': True,
                                            'invalid_source': True,
                                            'missing_role_citation': True}}}

FENCE_FLOORS = {'review-spec-readonly': ('specs/review.md', 'tests/test_specs.py'),
 'implement-consumer-read': ('specs/implement.md', 'tests/test_specs.py'),
 'phase7-continue': ('tickets', 'tests/test_seeded_phase7_01.py')}

FENCE_ADDITIONS = {'review-spec-readonly': ('tests/test_stages.py',),
 'implement-consumer-read': ('tests/test_stages.py',),
 'phase7-continue': ()}

CLOSURE_EVIDENCE = {'review-spec-readonly': {'tests/test_stages.py': '19.L rule 2: tests/test_stages.py:353, '
                                                  'test_implement_check_review_all_ok_with_artifacts_and_provenance '
                                                  'pins review.spec_version == 1.0; the required 1.1 '
                                                  'bump contradicts it.'},
 'implement-consumer-read': {'tests/test_stages.py': '19.L rule 2: tests/test_stages.py:362, '
                                                     'test_implement_check_review_all_ok_with_artifacts_and_provenance '
                                                     'pins the run record to implement 1.4; the '
                                                     'required 1.5 bump contradicts it.'},
 'phase7-continue': {}}

CONTRADICTED_IN_FLOOR = 'tests/test_specs.py:166, test_spec_lint_accepts_the_implement_and_requisition_specs pins implement 1.4.'

RULES_2_TO_5 = {'contradicted_tests': 'tests/test_specs.py:166; tests/test_stages.py:353,362',
 'activation': 'No dormant component is activated by either prompt edit.',
 'owners': 'Existing specs/review.md and specs/implement.md; no new module.',
 'callers': 'No Python signature, public operation or composition wiring changes.'}

COPY_VIOLATIONS = ()

BIRTH_UNTRACKED = ('tickets/implement-consumer-read/ticket.md',
 'tickets/phase7-continue/ticket.md',
 'tickets/review-spec-readonly/ticket.md')

CUSTODY = {'writer': 'Check',
 'approval_record': 'tickets/phase7-core/checks.json',
 'reviews': ('review-spec-readonly', 'implement-consumer-read', 'phase7-continue'),
 'lift': 'one ticket-plane seed lift after all three approvals',
 'implement_commit': ('tests/test_seeded_phase7_core.py',)}


def _ticket(stem):
    # Only ticket identity is live. No current plan, Context or config feeds these proofs.
    text = (ROOT / ticket_path(stem)).read_text()
    front, body = split_frontmatter(text)
    sections, errors = _sections(body, ticket_path(stem))
    assert not errors
    return yaml.safe_load(front), sections


def _bullets(section):
    return tuple(line[2:] for line in section.splitlines() if line.startswith("- "))


def render_chars(stem):
    a = AUTHORED[stem]
    return (IMPLEMENT_BODY_CHARS + a["chars"] + a["render_overhead"]
            + sum(PLAN_SIZES[pid]["chars"] for pid in a["plan"])
            + sum(FILE_SIZES[path]["chars"] for path in a["context"]))


def test_phase7_core_exact_admission():
    assert BATCH == ("review-spec-readonly", "implement-consumer-read", "phase7-continue")
    assert len(BATCH) <= MAX_SEEDS_PER_ADMISSION == 3
    assert POSITION == 1
    assert UNSEEDED_SUFFIX == (
        ("host-mechanical-check",), ("host-review-surfaces",), ("phase7-exit",))
    assert BIRTH_UNTRACKED == tuple(ticket_path(s) for s in sorted(BATCH))
    assert set(AUTHORED) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(BATCH)
    later = {s for row in UNSEEDED_SUFFIX for s in row}
    for stem in BATCH:
        fm, sections = _ticket(stem)
        a = AUTHORED[stem]
        assert fm == dict(priority="P1", kind="feature", agent_tier="medium",
                          agent_effort="medium", source="seed", state="confirmed")
        assert a["grammar_valid"]
        assert all(a["grammar_rejections"].values())
        assert _bullets(sections["Depends on"]) == a["depends"]
        assert not later.intersection(a["depends"])
        assert _bullets(sections["Plan contract"]) == a["citations"]
        assert _bullets(sections["Time budget"]) == (
            f'expected: {a["expected"]}m', f'stuck: {a["stuck"]}m')
        assert 0 < a["expected"] < a["stuck"] <= DRAIN_MAX_TICKET_MINUTES
        if stem in PAYLOADS:
            assert a["depends"] == ("phase7-core",)
            assert a["plan"] == ("19.I", "19.P7." + stem, "8")
            assert not {"19.L", "19.P7"} & set(a["plan"])
        else:
            assert a["depends"] == PAYLOADS
            assert a["plan"] == (
                "19.L", "19.I", "19.P7", "13", "19.P7.host-mechanical-check", "7", "8")
            assert a["fence"] == ("tickets", "tests/test_seeded_phase7_01.py")
            assert a["context"] == ("tests/test_seeded_phase6_01.py",)
            scope = sections["Scope in / Scope out"]
            for fact in ("Position 1", "admissions[1:]", "position 2", "admissions[2:]",
                         "host-mechanical-check and phase7-continue-02",
                         "host-review-surfaces", "phase7-exit alone", "no successor",
                         "19.P8", "medium/medium", "high/high", "KNOWN-HARD",
                         "seeding.max_seeds_per_admission", "drain.max_ticket_minutes",
                         "refuse forward edges"):
                assert fact in scope, fact


def test_phase7_core_entry_depth():
    assert REQUIRED == {
        "review-spec-readonly": ("19.P7.review-spec-readonly",),
        "implement-consumer-read": ("19.P7.implement-consumer-read",),
        "phase7-continue": ("19.P7.host-mechanical-check",),
    }
    assert set(ENTRY_DEPTH) == {uid for units in REQUIRED.values() for uid in units}
    for stem, units in REQUIRED.items():
        assert len(units) == len(set(units))
        assert set(units) <= set(AUTHORED[stem]["plan"])
        for uid in units:
            entry = ENTRY_DEPTH[uid]
            assert entry["resolves"] == 1 and entry["gap"] is None
            assert set(entry["parts"]) == {"Owner", "Records", "Observable", "Tests"}
            assert all(n > 0 for n in entry["parts"].values())
            assert entry["missing_part_rejected"] == dict.fromkeys(entry["parts"], True)
            assert entry["missing_unit_rejected"] and entry["duplicate_unit_rejected"]
            assert {k: entry[k] for k in ("bytes", "chars", "sha256")} == PLAN_SIZES[uid]
    assert ENTRY_DEPTH["19.P7.review-spec-readonly"]["tests"] == (
        "test_specs", "test_review_spec_read_only", "test_review_spec_readonly_entry_unit")
    assert ENTRY_DEPTH["19.P7.implement-consumer-read"]["tests"] == (
        "test_specs", "test_implement_spec_consumer_read", "test_implement_consumer_read_entry_unit")
    for stem in PAYLOADS:
        _, sections = _ticket(stem)
        for name in ENTRY_DEPTH["19.P7." + stem]["tests"]:
            assert name in sections["Acceptance criteria"], (stem, name)
    assert not COPY_VIOLATIONS


def test_phase7_core_closure():
    assert re.fullmatch(r"[0-9a-f]{40}", AUTHORING_HEAD)
    assert re.fullmatch(r"[0-9a-f]{40}", IDIOM_BLOB)
    assert set(CLOSURE_SCAN) == {"chupa", "eval", "tests"}
    for scan in CLOSURE_SCAN.values():
        assert scan["matched_lines"] == len(scan["matches"]) > 0
        assert re.fullmatch(r"[0-9a-f]{64}", scan["sha256"])
    assert FENCE_ADDITIONS == {
        "review-spec-readonly": ("tests/test_stages.py",),
        "implement-consumer-read": ("tests/test_stages.py",),
        "phase7-continue": (),
    }
    for stem in PAYLOADS:
        reason = CLOSURE_EVIDENCE[stem]["tests/test_stages.py"]
        assert "test_implement_check_review_all_ok_with_artifacts_and_provenance" in reason
        assert ("353" if stem == PAYLOADS[0] else "362") in reason
        assert "tests/test_stages.py" in AUTHORED[stem]["fence"]
        assert set(CLOSURE_EVIDENCE[stem]) == set(FENCE_ADDITIONS[stem])
    # The in-floor spec lint assertion also changes; historical snapshots never do.
    assert "tests/test_specs.py:166" in CONTRADICTED_IN_FLOOR
    assert RULES_2_TO_5 == {
        "contradicted_tests": "tests/test_specs.py:166; tests/test_stages.py:353,362",
        "activation": "No dormant component is activated by either prompt edit.",
        "owners": "Existing specs/review.md and specs/implement.md; no new module.",
        "callers": "No Python signature, public operation or composition wiring changes.",
    }
    for stem, a in AUTHORED.items():
        _, sections = _ticket(stem)
        assert _bullets(sections["Scope fence"]) == a["fence"]
        assert a["fence"] == (*FENCE_FLOORS[stem], *FENCE_ADDITIONS[stem])
        assert _bullets(sections["Context"]) == a["context"]
        assert "On-demand" not in sections and a["on_demand"] == ()
        assert set(a["existing_fence"]) == set(a["embedded_fence"]) | set(a["prompt_sources"])
        assert set(a["embedded_fence"]) <= set(a["context"])
        assert not set(a["created"]).intersection(a["context"])
        assert set(a["fence"]) == set(a["existing_fence"]) | set(a["created"])
        assert all(not p.startswith("specs/") and DELIMITER_FREE_CONTEXT[p] for p in a["context"])
        assert all(p.startswith("specs/") and not DELIMITER_FREE_CONTEXT[p] for p in a["prompt_sources"])
        assert not {"tests/test_seeded_phase7_core.py", "tests/test_seeded_phase7_01.py"}.intersection(a["context"])
    assert SPEC_BASELINES == {
        "review": {"version": "1.0", "placeholders": ("ticket", "diff", "retry_findings")},
        "implement": {"version": "1.4", "placeholders": ("ticket", "plan_contract", "context", "retry_findings")},
    }


def test_phase7_core_maximum_effort_render_from_recorded_operands():
    assert RENDER_EFFORT == "max"
    assert RENDER_BOUND_CHARS == 400_000 and REQ_RENDER_HEADROOM == 0.75
    assert HEADROOM_CHARS == int(RENDER_BOUND_CHARS * REQ_RENDER_HEADROOM)
    assert set(PLAN_SIZES) == {pid for a in AUTHORED.values() for pid in a["plan"]}
    for record in (*FILE_SIZES.values(), *PLAN_SIZES.values()):
        assert record["bytes"] >= record["chars"] > 0
        assert re.fullmatch(r"[0-9a-f]{64}", record["sha256"])
    for stem in BATCH:
        assert 0 < render_chars(stem) == AUTHORED[stem]["actual_render"] <= HEADROOM_CHARS
        assert AUTHORED[stem]["render_effort"] == RENDER_EFFORT


@pytest.mark.parametrize("stem", BATCH)
def test_phase7_core_recorded_ticket_bytes(stem):
    data = (ROOT / ticket_path(stem)).read_bytes()
    a = AUTHORED[stem]
    assert (len(data), len(data.decode()), hashlib.sha256(data).hexdigest()) == (
        a["bytes"], a["chars"], a["sha256"])


def test_phase7_core_check_owns_seed_custody():
    _, sections = _ticket("phase7-continue")
    scope = sections["Scope in / Scope out"]
    for fact in ("uncommitted", "requisition_review", "checks.json",
                 "single ticket-plane seed lift", "approved bytes", "ticket_sha",
                 "re-author only snagged seeds"):
        assert fact in scope, fact
    assert CUSTODY == {
        "writer": "Check",
        "approval_record": "tickets/phase7-core/checks.json",
        "reviews": BATCH,
        "lift": "one ticket-plane seed lift after all three approvals",
        "implement_commit": ("tests/test_seeded_phase7_core.py",),
    }
