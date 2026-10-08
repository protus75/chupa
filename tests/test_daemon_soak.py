"""Closed report and ordinary checks custody (CHUPA_PLAN.md 19.P3.daemon-soak).

All observations here are synthetic construction values in disposable repositories,
never the phase exit artifact.
"""

import importlib
import json
from copy import deepcopy
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from chupa import serve, stages
from chupa.artifacts import (
    ARTIFACT_SCHEMA_VERSION,
    DAEMON_SOAK_MEMBERS,
    DAEMON_SOAK_REPORT,
    DAEMON_SOAK_SPEC_VERSION,
    Artifact,
    DaemonSoakEntry,
    DaemonSoakReport,
)
from chupa.git import Git
from chupa.journal import EventType, Journal
from chupa.seams import LocalFileSystem, SubprocessExec
from chupa.tickets import validate_ticket
from eval import daemon_soak
from tests.test_cli import ENV, root
from tests.test_merge import context
from tests.test_restart_timers import repository
from tests.test_stages import CONFIG, STEM, TICKET

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
        entries=[DaemonSoakEntry(
            member=member, planted_fault="synthetic fault • construction only",
            expected=expected, observed=expected, disposition=disposition,
            producing_run=f"synthetic-{index}/0", auditor=[], green=True,
        ) for index, (member, (expected, disposition)) in enumerate(zip(MEMBERS, PAIRS))],
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
    assert DAEMON_SOAK_REPORT == "daemon-soak-report.json"
    assert DAEMON_SOAK_SPEC_VERSION == 1
    assert DAEMON_SOAK_MEMBERS == MEMBERS
    assert isinstance(valid, Artifact)
    assert set(DaemonSoakReport.model_fields) == {
        "artifact_schema_version", "produced_by_spec_version", "produced_at_sha", "entries",
    }
    assert set(DaemonSoakEntry.model_fields) == {
        "member", "planted_fault", "expected", "observed", "disposition", "producing_run", "auditor", "green",
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

    for entries in ([], data["entries"][:-1], data["entries"][1:],
                    data["entries"] * 2, list(reversed(data["entries"])),
                    [data["entries"][0], data["entries"][0], data["entries"][2]]):
        rejects(data | {"entries": entries})
    for field, values in {
        "member": ["unknown", " worker_killed_mid_run", 1],
        "planted_fault": ["", " \t\n", 1, None],
        "expected": ["", " \t\n", 1, None],
        "observed": ["", " \t\n", 1, None],
        "disposition": ["unknown", " alert", 1],
        "producing_run": ["", "synthetic", "synthetic/-1", "synthetic/1.0", "synthetic/+1",
                          "synthetic/١", "synthetic/0/1", "Upper/0", "under_score/0", "a/0",
                          "-bad/0", "a" * 65 + "/0", "retro/0", "synthetic/0\n", 1],
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
                for changes in ({"expected": other_expected, "observed": other_expected},
                                {"disposition": other_disposition},
                                {"expected": other_expected, "observed": other_expected,
                                 "disposition": other_disposition}):
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


class RecordingFS:
    def __init__(self):
        self.calls = []

    def write(self, path, data):
        self.calls.append((path, data))
        LocalFileSystem().write(path, data)

    def publish(self, path, data):
        pytest.fail("report writer must use FileSystem.write")

    def replace(self, src, dst):
        pytest.fail("report writer must use FileSystem.write")


@pytest.mark.asyncio
async def test_daemon_soak_writer_validates_before_write(root, monkeypatch):
    valid = await report(root)
    git = Git(SubprocessExec(), env=ENV, timeout=30.0)
    head, status = await git.rev_parse(root, "HEAD"), await git.status_porcelain(root)
    journal = Journal(root / ".chupa/state", lambda: datetime(2026, 10, 5, tzinfo=UTC))
    before = journal.read()
    fs = RecordingFS()
    path = root / ".chupa/construction" / DAEMON_SOAK_REPORT
    LocalFileSystem().write(path, b"keep existing bytes\n")
    expected = (json.dumps(valid.model_dump(), indent=2, ensure_ascii=False) + "\n").encode("utf-8")

    def forbidden(*args, **kwargs):
        pytest.fail("report writer must not mutate Git or Journal")

    with monkeypatch.context() as patch:
        patch.setattr(Git, "_call", forbidden)
        patch.setattr(Journal, "append", forbidden)
        invalid = [valid.model_copy(update={"produced_at_sha": ""}),
                   DaemonSoakReport.model_construct(**(valid.model_dump() | {"entries": []})),
                   valid.model_copy(update={"entries": list(reversed(valid.entries))})]
        for index, entry in enumerate(valid.entries):
            for changes in ({"observed": "unexpected", "green": False},
                            {"auditor": ["violation"], "green": False},
                            {"observed": "unexpected"}, {"auditor": ["violation"]},
                            {"green": 1}, {"expected": "invented"}):
                entries = list(valid.entries)
                entries[index] = entry.model_copy(update=changes)
                invalid.append(valid.model_copy(update={"entries": entries}))
        mutated = valid.model_copy(deep=True)
        mutated.entries.pop()
        invalid.append(mutated)
        for candidate in invalid:
            for destination in (path, path.parent / "absent" / DAEMON_SOAK_REPORT):
                with pytest.raises(ValueError):
                    daemon_soak.write_report(destination, candidate, fs)
                assert fs.calls == []
                assert path.read_bytes() == b"keep existing bytes\n"
                assert not (path.parent / "absent").exists()
        daemon_soak.write_report(path, valid, fs)
        assert fs.calls == [(path, expected)]
        assert path.read_bytes() == expected
    assert await git.rev_parse(root, "HEAD") == head
    assert await git.status_porcelain(root) == status
    assert journal.read() == before


@pytest.mark.asyncio
@pytest.mark.parametrize("case", ["green", "invalid", "false-green", "stale", "missing", "equal-copy", "startup"])
async def test_daemon_soak_uses_registered_checks_lift(root, monkeypatch, case):
    assert stages.KNOWN_ARTIFACTS[DAEMON_SOAK_REPORT] is DaemonSoakReport
    if case == "startup":
        rig = await repository(root, monkeypatch)

        def forbidden(*args, **kwargs):
            pytest.fail("machinery import/startup must not produce a soak report or prepare host work")

        with monkeypatch.context() as patch:
            patch.setattr(rig.fs, "write", lambda path, data: (
                forbidden() if path.name == DAEMON_SOAK_REPORT else LocalFileSystem().write(path, data)))
            importlib.reload(daemon_soak)
            patch.setattr(daemon_soak, "write_report", forbidden)
            assert await serve.serve(rig.checkout, plan="# Plan\n", read=lambda stem: None,
                stems=lambda: (), prepare=forbidden,
                signals=lambda stop: (stop(), lambda: None)[1]) == 0
        assert not list(root.rglob(DAEMON_SOAK_REPORT))
        assert not any(path.endswith("/" + DAEMON_SOAK_REPORT)
                       for path in await rig.checkout.git.ls_files(root))
        return

    fs = LocalFileSystem()
    fs.write(root / "config.yaml", CONFIG.encode())
    ctx = context(root, [])
    rel = f"tickets/{STEM}/{DAEMON_SOAK_REPORT}"
    raw = TICKET.format(bypass="").replace("grep -q ok chupa/thing.py\nenv", f"soak-fixture --out={rel}")
    fs.write(root / f"tickets/{STEM}/ticket.md", raw.encode())
    await ctx.git.add(root, ["config.yaml", f"tickets/{STEM}/ticket.md"])
    await ctx.git.commit(root, "synthetic report-lane fixture")
    inherited = await report(root)
    if case == "equal-copy":
        daemon_soak.write_report(root / rel, inherited, fs)
        await ctx.git.add(root, [rel])
        await ctx.git.commit(root, "inherited synthetic construction report")
    await stages.prepare_worktree(ctx, STEM)
    worktree = ctx.worktree(STEM)
    ticket = validate_ticket(STEM, raw, root)
    source = await report(worktree)
    outbox = worktree / rel
    daemon_soak.write_report(outbox, source, fs)
    nested_stale = outbox.parent / "nested" / DAEMON_SOAK_REPORT
    if case == "stale":
        fs.write(nested_stale, b'{"invalid": true}')
    await stages.lift_outbox(ctx, STEM, "run-record", attempt=0)
    await stages.lift_outbox(ctx, STEM, "review", attempt=0)
    assert outbox.is_file()
    if case != "equal-copy":
        assert not (root / rel).exists()
    record = "".join(f"## {name}\n\n{'ok' if name == 'Outcome' else 'none'}\n\n"
                     for name in stages.RUN_RECORD_SECTIONS)
    fs.write(root / f"tickets/{STEM}/run.md", record.encode())
    original_exec = ctx.exec_.run
    verified = []

    async def execute(argv, **kwargs):
        if argv[0] != "soak-fixture":
            return await original_exec(argv, **kwargs)
        assert kwargs["cwd"] == worktree
        assert not outbox.exists()  # Implement/inherited bytes are purged before Verification.
        assert not nested_stale.exists()
        verified.append(list(argv))
        if case == "green":
            daemon_soak.write_report(outbox, source, fs)
        elif case in {"invalid", "false-green"}:
            data = source.model_dump()
            if case == "invalid":
                data["entries"].reverse()
            else:
                data["entries"][0]["observed"] = "unexpected"
            fs.write(outbox, json.dumps(data).encode())
        elif case == "equal-copy":
            fs.write(outbox, (root / rel).read_bytes())
        return 0, "", ""

    monkeypatch.setattr(ctx.exec_, "run", execute)
    slip = stages.PackingSlip(produced_by_spec_version=1, produced_at_sha=source.produced_at_sha,
        stem=STEM, branch=STEM, outcome="ok", summary="construction fixture",
        run_record=f"tickets/{STEM}/run.md")
    head = await ctx.git.rev_parse(root, "HEAD")
    result = await stages.check(ctx, ticket, slip, attempt=0)
    assert verified == [["soak-fixture", f"--out={rel}"]]
    completions = [e for e in ctx.driver.journal.read() if e.type == EventType.EFFECT_COMPLETION]
    checks = [e for e in completions if e.key == f"ticket-plane/{STEM}/0/checks"]
    if case == "green":
        assert result.outcome == "ok" and result.artifact.passed
        assert len(checks) == 1
        lifted = checks[0].body["result"]
        assert lifted["kind"] == "checks"
        assert lifted["paths"] == [f"tickets/{STEM}/checks.json", rel]
        committed = await ctx.git._run(root, "show", f"{lifted['commit']}:{rel}")
        assert DaemonSoakReport.model_validate_json(committed) == source
        assert (root / rel).read_bytes() == (source.model_dump_json(indent=2) + "\n").encode("utf-8")
        assert not outbox.exists()
        assert all(rel not in e.body["result"].get("paths", []) for e in completions if e is not checks[0])
    else:
        assert result.outcome == "gate_failed" and not result.artifact.passed
        assert result.findings and all(f.code == "verification" and f.paved_road for f in result.findings)
        if case in {"invalid", "false-green"}:
            assert checks == []
            assert await ctx.git.rev_parse(root, "HEAD") == head
            assert not (root / f"tickets/{STEM}/checks.json").exists()
            assert not (root / rel).exists()
        else:
            assert all(rel not in e.body["result"].get("paths", []) for e in completions)
    assert await ctx.git.diff_names(root, "main", STEM) == []
    assert not (root / "tickets/soak-run" / DAEMON_SOAK_REPORT).exists()
    await ctx.git.worktree_remove(root, worktree)
