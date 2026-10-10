"""Closed exit records and real supervised subprocess evidence on disposable hosts."""

import asyncio
import copy
import hashlib
import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from chupa.artifacts import (HOST_LOOP_MEMBERS, HOST_LOOP_EXPECTED, HostLoopReport, ExitReceipt,
                            ReviewBaselineReport)
from chupa.audit import Violation
from chupa.seams import LocalFileSystem, SubprocessExec
from chupa.specs import ENTRY_PARTS, PlanContractError, required_units, resolve_plan_contract, entry_unit_gap
from eval import host_loop
from tests.test_eval_harness import report_fixture, corpus_results
from tests.test_stages import repo

ROOT = Path(__file__).resolve().parents[1]


def loop_report():
    members = [HOST_LOOP_MEMBERS[0]] * 3 + list(HOST_LOOP_MEMBERS[1:])
    return HostLoopReport(schema_version=1, entries=[dict(member=m, producing_run=f"member-{i}/0",
        expected=HOST_LOOP_EXPECTED[m], observed=HOST_LOOP_EXPECTED[m], engine_plane_edits=[],
        auditor=[], green=True) for i, m in enumerate(members)])


def test_exit_receipt_entry_unit(repo):
    plan = (ROOT / "CHUPA_PLAN.md").read_text()
    own = "19.P6.exit-receipt-machinery"
    ids = (own, "19.P6.fixture-host-scaffold", "19.P6.supervised-merge-hold",
           "19.P6.go-grade-machinery", "19.P6.go-grade-run")
    assert required_units(plan, "exit-receipt-machinery", ("19.I", *ids)) == ids
    assert required_units(plan, "phase6-exit", ("19.I", "19.L", "19.P6", own,
                          "19.P6.go-grade-run", "19.P6.go-grade-machinery")) == (
                          own, "19.P6.go-grade-run", "19.P6.go-grade-machinery")
    assert ENTRY_PARTS == ("Owner", "Records", "Observable", "Tests")
    resolved = resolve_plan_contract(plan, (*ids, *ids))
    for uid in ids:
        assert resolved.count(f"### {uid} ") == 1
        assert entry_unit_gap(plan, uid) is None
        unit = resolve_plan_contract(plan, (uid,))
        for part in ENTRY_PARTS:
            for replacement in ("", f"- **{part}:**"):
                broken = re.sub(rf"^- \*\*{part}:\*\*.*$", replacement, unit, flags=re.M)
                assert part in entry_unit_gap(broken, uid)
        for broken in ("", unit + unit):
            assert entry_unit_gap(broken, uid)
            with pytest.raises(PlanContractError):
                resolve_plan_contract(broken, (uid,))
    # Terminal successor facts come from the phase and build laws, before any seed writer.
    phase = resolve_plan_contract(plan, ("19.P6",))
    laws = resolve_plan_contract(plan, ("19.L",))
    assert "phase6-exit: {exit: true, depends: [exit-receipt-machinery]" in phase
    assert "producer the exit's own harness run" in phase
    assert "`phase6-exit` authors no seeds" in laws
    assert "regenerable byte-identical" in laws
    assert "19.P6.phase6-exit" not in required_units(plan, "phase6-exit", ("19.P6",))

    # Enter the production admission check with the terminal successor's citations.
    # Every missing part refuses before grammar, model review, or seed lift can write.
    from types import SimpleNamespace
    from chupa import stages
    from tests.test_merge import context
    ctx = context(repo, [])
    data = ("## Plan contract\n" + "".join(f"- {u}\n" for u in ids)).encode()
    async def admission():
        for uid in ids:
            unit = resolve_plan_contract(plan, (uid,))
            for part in ENTRY_PARTS:
                broken = re.sub(rf"^- \*\*{part}:\*\*.*$", "", unit, flags=re.M)
                verdict = await stages._review_one(ctx, SimpleNamespace(stem="continuation"),
                    "phase6-exit", "tickets/phase6-exit/ticket.md", data, "blob", None,
                    plan.replace(unit, broken), ctx.worktree("continuation"), None,
                    siblings=set(), attempt=0, call_seq=1)
                assert verdict.verdict == "snag" and verdict.mechanical == "entry unit gap"
                assert any(f.kind == "spec_gap" and f.unit == uid and part in f.message
                           for f in verdict.findings)
        assert ctx.driver.llm.requests == []
        assert not (repo / "tickets/phase6-exit").exists()
        assert ctx.driver.journal.read() == []
    asyncio.run(admission())


def test_host_loop_closed_schema():
    valid = loop_report().model_dump()
    HostLoopReport.model_validate(valid)
    invalid = [{**valid, "unknown": True}, {**valid, "schema_version": True}]
    for mutate in (lambda rows: rows.reverse(),
                   lambda rows: rows[1].update(producing_run=rows[0]["producing_run"]),
                   lambda rows: rows[0].update(observed="unproven"),
                   lambda rows: rows[0].update(green=False),
                   lambda rows: rows[0].update(auditor=["red"]),
                   lambda rows: rows[0].update(engine_plane_edits=["config.yaml"]),
                   lambda rows: rows[0].update(extra=True),
                   lambda rows: rows[0].update(expected="invented", observed="invented"),
                   lambda rows: rows[0].update(producing_run="invalid/negative"),
                   lambda rows: rows.pop(0)):
        data = copy.deepcopy(valid)
        mutate(data["entries"])
        invalid.append(data)
    for data in invalid:
        with pytest.raises(ValidationError):
            HostLoopReport.model_validate(data)
    red = copy.deepcopy(valid)
    red["entries"][0].update(observed="missing", green=False)
    assert not HostLoopReport.model_validate(red).entries[0].green


class RecordingExec(SubprocessExec):
    def __init__(self):
        self.calls, self.spawned, self.killed = [], [], []

    async def run(self, argv, **kwargs):
        self.calls.append((list(argv), kwargs))
        if argv[1:3] == ["-m", "chupa"]:
            callback = kwargs["on_spawn"]
            def spawn(pid):
                self.spawned.append(pid)
                callback(pid)
            kwargs["on_spawn"] = spawn
        return await super().run(argv, **kwargs)

    def kill_group(self, pgid):
        self.killed.append(pgid)
        super().kill_group(pgid)


@pytest.fixture(scope="module")
def production(tmp_path_factory):
    root = tmp_path_factory.mktemp("host-loop")
    exec_ = RecordingExec()
    members = []
    async def exercise():
        for name in host_loop.scaffold.SCENARIOS:
            loop = host_loop.FixtureLoop(root / name, name, exec_=exec_, fs=LocalFileSystem(),
                clock=lambda: datetime.now(UTC), sleep=asyncio.sleep, notifications=None, timeout=30)
            try:
                await loop.initialize()
                await loop.exercise()
            finally:
                await loop.stop()
            members.append(loop)
        return HostLoopReport(schema_version=1, entries=[await m.observe() for m in members])
    report = asyncio.run(exercise())
    return report, members, exec_


def test_host_loop_drives_supervised_fixture_serve(production, tmp_path):
    report, members, exec_ = production
    assert [e.producing_run for e in report.entries[:3]] == [f"{n}/0" for n in ("merge-add", "merge-bonus", "merge-floor")]
    assert all(e.green and not e.engine_plane_edits for e in report.entries)
    serve_calls = [argv for argv, _ in exec_.calls if argv[1:3] == ["-m", "chupa"]]
    assert len(serve_calls) == 5 and all(argv[-1] == "serve" for argv in serve_calls)
    assert exec_.spawned == exec_.killed
    for member in members:
        assert member.task.done()
        assert json.loads((member.root / ".chupa/state/control/active.json").read_bytes()) is None
        costs = [e.body["cost"]["usd"] for e in member.journal.read()
                 if e.type == "effect_completion" and (e.key or "").startswith("llm/")]
        assert costs and all(c == 0 for c in costs)
        assert len(member.requests) >= 2
    async def failure(timeout):
        loop = host_loop.FixtureLoop(tmp_path / str(timeout), "merge-add", exec_=exec_, fs=LocalFileSystem(),
            clock=lambda: datetime.now(UTC), sleep=asyncio.sleep, notifications=None, timeout=timeout)
        try:
            await loop.initialize()
            await loop.start()
            if timeout < 1:
                await loop.until(lambda: False)
            else:
                raise RuntimeError("injected member failure")
        finally:
            await loop.stop()
            assert loop.task.done()
            assert loop.pgid in exec_.killed
    for timeout, error in ((0.3, host_loop.LoopRefused), (30, RuntimeError)):
        with pytest.raises(error):
            asyncio.run(failure(timeout))


def test_host_loop_report_regression_and_escape(production):
    report, members, _ = production
    bug, escape = members[-2:]
    assert report.entries[-2].member == "report_to_regression_bug_loop"
    assert bug.before_replay == (1, {"final_state": {"score": 0}, "defect": True})
    assert bug.after_replay == (0, {"final_state": {"score": 3}, "defect": False})
    assert (bug.root / "tickets/regression/evidence/report.json").is_file()
    assert "kind: bug" in (bug.root / "tickets/regression/ticket.md").read_text()
    assert report.entries[-1].producing_run == "escape/0"
    attribution, = [e.body["result"] for e in escape.journal.read()
        if e.type == "effect_completion" and (e.key or "").startswith("escape-attribution/")]
    assert attribution["bug_ticket"] == "regression"
    assert attribution["matches"][0]["ticket"] == "escape"
    assert "review" in attribution["matches"][0]["surfaces"]


def test_host_loop_requires_member_auditor_green(production, monkeypatch):
    _, members, _ = production
    member = members[0]
    with monkeypatch.context() as patch:
        patch.setattr(host_loop, "audit_journal", lambda j: [Violation("one_terminal_per_run", None, "red")])
        with pytest.raises(host_loop.LoopRefused, match="auditor findings"):
            asyncio.run(member.observe())
    with monkeypatch.context() as patch:
        read = member.journal.read
        patch.setattr(member.journal, "read", lambda: [e for e in read() if e.key != "ticket-plane/merge-add/0/checks"])
        with pytest.raises(host_loop.LoopRefused, match="missing unique production evidence"):
            asyncio.run(member.observe())


def test_exit_receipt_closed_schema_and_baseline_identity(tmp_path):
    loop = host_loop.canonical(loop_report())
    report, _, _ = report_fixture(tmp_path)
    for verdict in ("NO_GO", "GO"):
        raw = report.model_dump()
        raw["verdict_signal"]["body"]["verdict"] = verdict
        baseline = ReviewBaselineReport.model_validate(raw)
        receipt = host_loop.regenerate(loop, host_loop.canonical(baseline))
        assert receipt.verdict_signal == baseline.verdict_signal
        assert set(receipt.reads.model_dump().values()) == {"pass"}
    (tmp_path / "partial").mkdir()
    partial, _, _ = report_fixture(tmp_path / "partial", corpus_results(18, 4, 18, 0), graph=False)
    receipt = host_loop.regenerate(loop, host_loop.canonical(partial))
    assert receipt.verdict_signal == partial.verdict_signal
    assert receipt.verdict_signal.body.verdict == "NO_GO"
    raw = partial.model_dump()
    raw["verdict_signal"]["body"]["verdict"] = "GO"
    with pytest.raises(ValidationError, match="GO requires complete"):
        host_loop.regenerate(loop, json.dumps(raw).encode())
    raw = receipt.model_dump()
    for read in raw["reads"]:
        failed = copy.deepcopy(raw)
        failed["reads"][read] = "fail"
        assert ExitReceipt.model_validate(failed).reads.model_dump()[read] == "fail"
        failed["reads"][read] = "unknown"
        with pytest.raises(ValidationError):
            ExitReceipt.model_validate(failed)
    for field in ("host_loop_digest", "baseline_report_digest"):
        for value in ("a" * 63, "A" * 64, "z" * 64):
            with pytest.raises(ValidationError):
                ExitReceipt.model_validate({**raw, field: value})
    for invalid in ({**raw, "unknown": 1}, {**raw, "schema_version": True},
                    {**raw, "reads": {**raw["reads"], "unknown": "pass"}}):
        with pytest.raises(ValidationError):
            ExitReceipt.model_validate(invalid)
    altered = report.model_dump()
    altered["verdict_signal"]["body"]["identity"]["review"]["rows"].pop("low")
    with pytest.raises(ValidationError):
        host_loop.regenerate(loop, json.dumps(altered).encode())
    for member in HOST_LOOP_MEMBERS:
        red = loop_report().model_dump()
        next(e for e in red["entries"] if e["member"] == member).update(green=False, observed="failed")
        receipt = host_loop.regenerate(json.dumps(red).encode(), host_loop.canonical(partial))
        assert receipt.reads.model_dump()[member] == "fail"


def test_exit_receipt_regenerates_from_committed_bytes(tmp_path, monkeypatch):
    from chupa.git import Git
    (tmp_path / "baseline").mkdir()
    report, _, _ = report_fixture(tmp_path / "baseline")
    root = tmp_path / "committed"
    root.mkdir()
    loop_bytes = json.dumps(loop_report().model_dump(), separators=(",", ":")).encode() + b"\n\n"
    baseline_bytes = host_loop.canonical(report)
    (root / "host-loop-report.json").write_bytes(loop_bytes)
    (root / "review-baseline-report.json").write_bytes(baseline_bytes)
    env = {"PATH": "/usr/bin:/bin", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    git = Git(SubprocessExec(), env=env, timeout=10)
    async def committed():
        await git.init(root, branch="main")
        await git.add(root, ["host-loop-report.json", "review-baseline-report.json"])
        await git.commit(root, "disposable input reports")
        return [await host_loop.committed_bytes(git, root, root / name)
                for name in ("host-loop-report.json", "review-baseline-report.json")]
    inputs = asyncio.run(committed())
    assert inputs == [loop_bytes, baseline_bytes]
    assert not (root / ".chupa").exists()
    monkeypatch.setattr(JournalForbidden, "read", lambda *a: pytest.fail("live state read"))
    monkeypatch.setattr(host_loop.Journal, "read", JournalForbidden.read)
    first = root / "first.json"
    second = root / "second.json"
    receipt = host_loop.write_receipt(first, *inputs, fs=LocalFileSystem())
    host_loop.write_receipt(second, *inputs, fs=LocalFileSystem())
    assert first.read_bytes() == second.read_bytes()
    assert receipt.host_loop_digest == hashlib.sha256(loop_bytes).hexdigest()
    assert receipt.baseline_report_digest == hashlib.sha256(baseline_bytes).hexdigest()
    assert receipt.verdict_signal == report.verdict_signal
    (root / "host-loop-report.json").write_bytes(loop_bytes + b" ")
    with pytest.raises(host_loop.LoopRefused, match="committed bytes"):
        asyncio.run(host_loop.committed_bytes(git, root, root / "host-loop-report.json"))
    # Invalid committed baseline bytes refuse before any live fixture process or output write.
    (root / "review-baseline-report.json").write_bytes(b"{}")
    async def commit_invalid():
        await git.add(root, ["review-baseline-report.json"])
        await git.commit(root, "invalid disposable baseline")
    asyncio.run(commit_invalid())
    monkeypatch.chdir(root)
    monkeypatch.setattr(host_loop, "produce", lambda *a, **kw: pytest.fail("invalid baseline spawned work"))
    assert asyncio.run(host_loop._main(["--out", "unwritten-loop.json", "--receipt", "unwritten-receipt.json",
                                       "--baseline", "review-baseline-report.json"])) == 1
    assert not (root / "unwritten-loop.json").exists()
    assert not (root / "unwritten-receipt.json").exists()


class JournalForbidden:
    def read(self):
        pytest.fail("live state access")
