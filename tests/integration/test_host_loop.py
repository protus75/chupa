"""Closed exit records and real supervised subprocess evidence on disposable hosts."""

import asyncio
import copy
import json
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from chupa.audit import Violation
from chupa.seams import LocalFileSystem, SubprocessExec
from eval import host_loop
from eval.host_loop import HOST_LOOP_EXPECTED, HOST_LOOP_MEMBERS, HostLoopReport


def loop_report():
    members = [HOST_LOOP_MEMBERS[0]] * 3 + list(HOST_LOOP_MEMBERS[1:])
    return HostLoopReport(
        schema_version=1,
        entries=[
            dict(member=m, producing_run=f"member-{i}/0", expected=HOST_LOOP_EXPECTED[m], observed=HOST_LOOP_EXPECTED[m], engine_plane_edits=[], auditor=[], green=True) for i, m in enumerate(members)
        ],
    )


def test_host_loop_closed_schema():
    valid = loop_report().model_dump()
    HostLoopReport.model_validate(valid)
    invalid = [{**valid, "unknown": True}, {**valid, "schema_version": True}]
    for mutate in (
        lambda rows: rows.reverse(),
        lambda rows: rows[1].update(producing_run=rows[0]["producing_run"]),
        lambda rows: rows[0].update(observed="unproven"),
        lambda rows: rows[0].update(green=False),
        lambda rows: rows[0].update(auditor=["red"]),
        lambda rows: rows[0].update(engine_plane_edits=["config.yaml"]),
        lambda rows: rows[0].update(extra=True),
        lambda rows: rows[0].update(expected="invented", observed="invented"),
        lambda rows: rows[0].update(producing_run="invalid/negative"),
        lambda rows: rows.pop(0),
    ):
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
        if argv[1:3] == ["-m", "chupa"] and kwargs.get("on_spawn"):
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
            loop = host_loop.FixtureLoop(root / name, name, exec_=exec_, fs=LocalFileSystem(), clock=lambda: datetime.now(UTC), sleep=asyncio.sleep, notifications=None, timeout=30)
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
    assert [argv[-1] for argv in serve_calls].count("serve") == 11
    assert [argv[-1] for argv in serve_calls].count("triage") == 6
    assert exec_.spawned == exec_.killed
    for member in members:
        assert member.task.done()
        assert json.loads((member.root / ".chupa/state/control/active.json").read_bytes()) is None
        costs = [e.body["cost"]["usd"] for e in member.journal.read() if e.type == "effect_completion" and (e.key or "").startswith("llm/")]
        assert costs and all(c == 0 for c in costs)
        assert any(hold is None for _, hold in member.requests)

    async def failure(timeout):
        loop = host_loop.FixtureLoop(tmp_path / str(timeout), "merge-add", exec_=exec_, fs=LocalFileSystem(), clock=lambda: datetime.now(UTC), sleep=asyncio.sleep, notifications=None, timeout=timeout)
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
    (attribution,) = [e.body["result"] for e in escape.journal.read() if e.type == "effect_completion" and (e.key or "").startswith("escape-attribution/")]
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
