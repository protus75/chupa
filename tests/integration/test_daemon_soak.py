"""Closed report and ordinary checks custody (CHUPA_PLAN.md 19.P3.daemon-soak).

All observations here are synthetic construction values in disposable repositories,
never the phase exit artifact.
"""

import json
from copy import deepcopy

import pytest
from pydantic import ValidationError

from chupa.artifacts import ARTIFACT_SCHEMA_VERSION, Artifact
from chupa.git import Git
from chupa.seams import SubprocessExec
from tests.harness.daemon_soak import DAEMON_SOAK_MEMBERS, DAEMON_SOAK_SPEC_VERSION, DaemonSoakEntry, DaemonSoakReport
from tests.integration.test_cli import ENV, root

MEMBERS = (
    "worker_killed_mid_run",
    "conflict_resolution_rungs",
    "semantic_conflict_integration_red",
)
PAIRS = (
    ("abandoned_alerted_then_merged", "alert"),
    ("mechanical_and_rework_main_green", "resolved"),
    ("integration_red_main_green", "refused"),
)


async def report(root):
    git = Git(SubprocessExec(), env=ENV, timeout=30.0)
    return DaemonSoakReport(
        produced_by_spec_version=DAEMON_SOAK_SPEC_VERSION,
        produced_at_sha=await git.rev_parse(root, "HEAD"),
        entries=[
            DaemonSoakEntry(
                member=member,
                planted_fault="synthetic fault • construction only",
                expected=expected,
                observed=expected,
                disposition=disposition,
                producing_run=f"synthetic-{index}/0",
                auditor=[],
                green=True,
            )
            for index, (member, (expected, disposition)) in enumerate(zip(MEMBERS, PAIRS))
        ],
    )


def rejects(payload):
    with pytest.raises(ValidationError):
        DaemonSoakReport.model_validate(payload)
    with pytest.raises(ValidationError):
        DaemonSoakReport.model_validate_json(json.dumps(payload))


@pytest.mark.asyncio
async def test_daemon_soak_schema_is_closed(root):
    valid = await report(root)
    data = valid.model_dump()
    assert DAEMON_SOAK_SPEC_VERSION == 1
    assert DAEMON_SOAK_MEMBERS == MEMBERS
    assert isinstance(valid, Artifact)
    assert set(DaemonSoakReport.model_fields) == {
        "artifact_schema_version",
        "produced_by_spec_version",
        "produced_at_sha",
        "entries",
    }
    assert set(DaemonSoakEntry.model_fields) == {
        "member",
        "planted_fault",
        "expected",
        "observed",
        "disposition",
        "producing_run",
        "auditor",
        "green",
    }
    assert DaemonSoakReport.model_validate_json(valid.model_dump_json()) == valid
    for key in ("produced_by_spec_version", "produced_at_sha", "entries"):
        missing = deepcopy(data)
        del missing[key]
        rejects(missing)
    for key in data["entries"][0]:
        missing = deepcopy(data)
        del missing["entries"][0][key]
        rejects(missing)
    rejects(data | {"runner": "unearned"})
    extra = deepcopy(data)
    extra["entries"][0]["group"] = "unearned"
    rejects(extra)

    for entries in ([], data["entries"][:-1], data["entries"][1:], data["entries"] * 2, list(reversed(data["entries"])), [data["entries"][0], data["entries"][0], data["entries"][2]]):
        rejects(data | {"entries": entries})
    for field, values in {
        "member": ["unknown", " worker_killed_mid_run", 1],
        "planted_fault": ["", " \t\n", 1, None],
        "expected": ["", " \t\n", 1, None],
        "observed": ["", " \t\n", 1, None],
        "disposition": ["unknown", " alert", 1],
        "producing_run": [
            "",
            "synthetic",
            "synthetic/-1",
            "synthetic/1.0",
            "synthetic/+1",
            "synthetic/١",
            "synthetic/0/1",
            "Upper/0",
            "under_score/0",
            "a/0",
            "-bad/0",
            "a" * 65 + "/0",
            "retro/0",
            "synthetic/0\n",
            1,
        ],
        "auditor": ["violation", [""], [" \t\n"], [1], None],
        "green": [1, 0, "true", "false", None],
    }.items():
        for value in values:
            invalid = deepcopy(data)
            invalid["entries"][0][field] = value
            rejects(invalid)
    for field, values in {
        "artifact_schema_version": [-1, ARTIFACT_SCHEMA_VERSION + 1, True, "1", 1.0],
        "produced_by_spec_version": [True, "1", 1.0],
        "produced_at_sha": ["", " \t\n", 1, None],
        "entries": [None, {}, "entries"],
    }.items():
        for value in values:
            rejects(data | {field: value})
    for version in range(ARTIFACT_SCHEMA_VERSION + 1):
        assert DaemonSoakReport.model_validate(data | {"artifact_schema_version": version})
    without_version = data.copy()
    del without_version["artifact_schema_version"]
    assert DaemonSoakReport.model_validate(without_version).artifact_schema_version == ARTIFACT_SCHEMA_VERSION
    for identity in ("12-valid/0", "synthetic/123", "a" * 64 + "/0"):
        assert DaemonSoakEntry.model_validate(data["entries"][0] | {"producing_run": identity})
    with pytest.raises(ValidationError):
        DaemonSoakReport.model_validate(data | {"entries": tuple(valid.entries)})
    with pytest.raises(ValidationError):
        DaemonSoakEntry.model_validate(data["entries"][0] | {"auditor": ()})


@pytest.mark.asyncio
async def test_daemon_soak_green_matches_observation_and_auditor(root):
    valid = await report(root)
    for entry, pair in zip(valid.entries, PAIRS):
        assert (entry.expected, entry.disposition) == pair
        data = entry.model_dump()
        for other_expected, other_disposition in PAIRS:
            if other_expected != entry.expected:
                for changes in (
                    {"expected": other_expected, "observed": other_expected},
                    {"disposition": other_disposition},
                    {"expected": other_expected, "observed": other_expected, "disposition": other_disposition},
                ):
                    with pytest.raises(ValidationError):
                        DaemonSoakEntry.model_validate(data | changes)
        for observed in (entry.expected, "unexpected_observation"):
            for auditor in ([], ["one_terminal_per_run: synthetic: duplicate terminal"]):
                green = observed == entry.expected and not auditor
                changed = data | {"observed": observed, "auditor": auditor, "green": green}
                red_or_green = DaemonSoakEntry.model_validate(changed)
                assert red_or_green.observed == observed and red_or_green.auditor == auditor
                assert red_or_green.green is green
                with pytest.raises(ValidationError):
                    DaemonSoakEntry.model_validate(changed | {"green": not green})
                with pytest.raises(ValidationError):
                    DaemonSoakEntry.model_validate_json(json.dumps(changed | {"green": not green}))
