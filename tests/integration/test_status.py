"""Status surfaces confirmed policy classes using write-free queue and journal reads."""

import asyncio
import re
from dataclasses import FrozenInstanceError

import pytest

from chupa import __main__ as cli
from chupa import runner
from chupa.__main__ import _status, main
from chupa.box import Box, Resolution
from chupa.daemon import storm_producer
from chupa.git import Git
from chupa.journal import EventType, Journal
from chupa.llm import FakeLLM, LLMResult
from chupa.lockfile import Lockfile
from chupa.retro import Retro, RetroArtifact, measurements, production_evidence, project_window, render_report
from chupa.seams import LocalFileSystem, SubprocessExec
from chupa.specs import load_spec
from chupa.status import project, reject_queue, render
from tests.integration.test_cli import ENV
from tests.integration.test_drain import Clock, make_root
from tests.integration.test_git import commit_lock
from tests.integration.test_retro import completed, merged, rig
from tests.integration.test_retro_box import PROPOSAL
from tests.integration.test_scorecard import invoice, review, rows


def test_settled_stem_never_awaits_verdict(tmp_path):
    journal = Journal(tmp_path, Clock())
    for terminal in ("already_satisfied", "merged"):
        journal.append(EventType.STATE_TRANSITION, {"to": "gate_failed", "routed": "reject_queue"}, ticket=terminal)
        journal.append(EventType.STATE_TRANSITION, {"to": terminal, "stage": "check", "reason": terminal, "dispatch": "reject_queue", "routed": "reject_queue"}, ticket=terminal)
        assert reject_queue(journal.read()) == {}
        journal.append(EventType.SIGNAL, {"signal": "reject_arrival"}, ticket=terminal)
        assert reject_queue(journal.read()) == {}
    assert project(journal.read()).reject == ()


def test_status_surfaces_confirmed_class_tombstones(tmp_path, monkeypatch, capsys):
    root = make_root(tmp_path)
    clock = Clock()
    journal = Journal(root / ".chupa/state", clock)
    fs = LocalFileSystem()
    box = storm_producer(root=root / ".chupa/state/box", fs=fs, journal=journal, clock=clock)
    ids = []
    for cls in ("failure_report", "retro_finding", "suggestion"):
        evidence = {**PROPOSAL, "retro_report_key": "retro/1"} if cls == "retro_finding" else {}
        id, _ = box.enqueue(message_class=cls, origin=cls, summary="observed concern", occurrence_id=cls, **evidence)
        box.resolve(id, Resolution(kind="tombstone", link=f"tombstone-{id}"))
        ids.append(id)
    before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}

    def forbidden(*args, **kwargs):
        raise AssertionError("status tried to write")

    monkeypatch.setattr(LocalFileSystem, "write", forbidden)
    monkeypatch.setattr(Journal, "append", forbidden)
    git = Git(SubprocessExec(), env=ENV, timeout=30, commit_lock=commit_lock(root / ".chupa/state"))
    provenance = {"head": asyncio.run(git.rev_parse(root, "HEAD")), "spec_version": load_spec((runner.SPECS_DIR / "retro.md").read_text()).meta.version, "at": clock().isoformat()}
    status = project(journal.read(), box=box, provenance=provenance)
    assert status.tombstones == tuple((m.id, m.message_class, 0) for m in box.messages()[:2])
    output = render(status)
    assert all(id in output for id in ids)  # The box includes classes excluded from confirmed tombstones.
    assert main(["status"], cwd=root, env=ENV, clock=clock) == 0
    assert capsys.readouterr().out == output
    assert {p: p.read_bytes() for p in root.rglob("*") if p.is_file()} == before
    monkeypatch.undo()
    for n in range(3):
        box.record_rereport(ids[0], occurrence_id=f"fresh/{n}")
    before = journal.read()
    current = project(before, box=Box(box.root, fs))
    assert current.tombstones == ((ids[1], "retro_finding", 0),)
    assert current.reopens == ({"kind": "tombstone_auto_reopened", "box_id": ids[0], "signature": box.get(ids[0]).signature, "reports": 3},)
    assert ids[0] in render(current) and journal.read() == before


def test_status_current_window_scorecard(tmp_path):
    c, writer, _, _ = rig(tmp_path)
    asyncio.run(invoice(c, writer, "old"))
    old_cost = LLMResult(text='{"verdict":"approve","summary":"ok","findings":[]}', usd=2, input_tokens=None, output_tokens=3, provider="fake", model="fake")
    asyncio.run(review(c, writer, "old", "approve", cost=old_cost))
    merged(c.journal, "old")
    c.journal.append(EventType.EFFECT_INTENT, {}, key="retro/1")
    initial = asyncio.run(_status(c))
    assert initial.scorecard.boundary == "initial" and initial.scorecard.spend_usd == 2
    assert rows(initial.scorecard)["scope_fence"].catches == 1
    completed(c.journal, 1)
    for n in range(25):
        inv = asyncio.run(invoice(c, writer, f"current-{n}", bypass=True))
        assert inv.passed and "scope_fence" in inv.bypassed
        if n == 23:
            assert not rows(asyncio.run(_status(c)).scorecard)["scope_fence"].prune_candidate
    completion = next(e for e in reversed(c.journal.read()) if e.type == EventType.EFFECT_COMPLETION and (e.key or "").endswith("/checks"))
    c.journal.append(completion.type, completion.body, ticket=completion.ticket, key=completion.key)
    c.journal.append(EventType.EFFECT_INTENT, {}, ticket="unfinished", key="ticket-plane/unfinished/0/checks")
    c.fs.write(c.repo / "tickets/current-24/checks.json", b"mutable bytes are not evidence")
    asyncio.run(review(c, writer, "current-24", "snag"))
    cost = LLMResult(text='{"verdict":"approve","summary":"ok","findings":[]}', usd=1.25, input_tokens=11, output_tokens=None, provider="fake", model="fake")
    asyncio.run(review(c, writer, "current-24", "approve", attempt=1, cost=cost))
    head = asyncio.run(c.git.rev_parse(c.repo, "HEAD"))
    merged(c.journal, "current-24", head)
    merged(c.journal, "current-24", head)
    c.journal.append(EventType.SIGNAL, {"signal": "rework_order", "attempt": 1}, ticket="current-24")
    writer.queue._facts("current-24", set(), set(), red=["red.py"])
    c.journal.append(EventType.STATE_TRANSITION, {"to": "gate_failed", "reason": "diff_budget"}, ticket="failed")
    c.journal.append(EventType.EFFECT_INTENT, {}, key="retro/2")
    status = asyncio.run(_status(c))
    card = status.scorecard
    assert card.boundary == "retro/1" and card.merged_ticket_count == 1
    assert status.spend_usd == 3.25 and card.spend_usd == 1.25
    assert card.tokens["input"] == {"known": 11, "unknown_calls": 26}
    assert card.tokens["output"] == {"known": 0, "unknown_calls": 27}
    assert card.signal_counts == {"override": 1, "rework": 1, "gate-failure": 1, "integration-red": 1, "reject": 0, "premise-failed": 0, "infra-error": 0, "flake": 0, "escape": 0}
    assert card.gate_failure_count == 1
    result = rows(card)
    assert list(result) == sorted(result) and "unfinished" not in result
    assert result["scope_fence"].evaluated_tickets == result["scope_fence"].bypass_count == 25
    assert result["scope_fence"].prune_candidate and result["scope_fence"].catch_rate == 0
    assert result["review"].catches == 1 and result["review"].catch_rate == 1
    assert result["diff_budget"].catches == 1
    assert all(row.escapes == row.escape_rate == 0 for row in card.surfaces)
    window = project_window(c.journal.read())
    evidence = asyncio.run(production_evidence(window, c))
    retro_text = render_report(window, evidence, dict(status.provenance), [], RetroArtifact(proposals=[]))
    assert render(status).split("## Surface scorecard\n")[1] == retro_text.split("## Surface scorecard\n\n")[1]
    with pytest.raises(FrozenInstanceError):
        status.scorecard = initial.scorecard
    with pytest.raises(TypeError):
        status.provenance["head"] = "changed"
    completed(c.journal, 2)
    c.journal.append(EventType.EFFECT_INTENT, {}, key="retro/3")
    empty = asyncio.run(_status(c)).scorecard
    assert empty.boundary == "retro/2" and empty.surfaces == ()
    assert empty.merged_ticket_count == empty.spend_usd == empty.gate_failure_count == 0
    assert all(value == {"known": 0, "unknown_calls": 0} for value in empty.tokens.values())
    assert all(value == 0 for value in empty.signal_counts.values())
    assert render(project([])).endswith("| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |\n")


def test_status_production_provenance(tmp_path, monkeypatch, capsys):
    c, _, _, _ = rig(tmp_path)
    spec_text = re.sub(r'version: "[^"]+"', 'version: "7.3"', (runner.SPECS_DIR / "retro.md").read_text())
    specs = tmp_path / "specs"
    specs.mkdir()
    (specs / "retro.md").write_text(spec_text)
    monkeypatch.setattr(runner, "SPECS_DIR", specs)
    head = asyncio.run(c.git.rev_parse(c.repo, "HEAD"))
    expected = {"head": head, "spec_version": load_spec(spec_text).meta.version, "at": c.clock().isoformat()}
    assert expected["spec_version"] == "7.3"
    projected = []

    def capture(events, **kwargs):
        assert kwargs["provenance"] == expected
        assert kwargs["window"].evidence == {**measurements(project_window(events)), "check_observations": [], "tests": {}, "coverage": {}}
        result = project(events, **kwargs)
        projected.append(result)
        return result

    monkeypatch.setattr(cli, "project", capture)
    assert main(["status"], cwd=c.repo, env=ENV, clock=c.clock) == 0
    output = capsys.readouterr().out
    assert output == render(projected[0])
    assert dict(projected[0].provenance) == expected
    for key, value in expected.items():
        assert f"- {key}: {value}\n" in output


@pytest.mark.parametrize("populated", [False, True])
def test_status_preserves_sections_and_is_write_free(tmp_path, monkeypatch, capsys, populated):
    from chupa.effects import Effects
    from chupa.providers import ProviderLLM
    from chupa.seams import CommandNotifications

    c, writer, _, _ = rig(tmp_path)
    box = storm_producer(root=c.config.state_dir / "box", fs=c.fs, journal=c.journal, clock=c.clock)
    if populated:
        asyncio.run(invoice(c, writer, "checked"))
        merged(c.journal, "done")
        c.journal.append(EventType.STATE_TRANSITION, {"to": "running"}, ticket="active")
        c.journal.append(EventType.STATE_TRANSITION, {"to": "gate_failed", "stage": "check", "routed": "reject_queue"}, ticket="held")
        c.journal.append(EventType.SIGNAL, {"signal": "ticket_intake", "source": "human", "state": "confirmed", "commit": "123456789abcdef"}, ticket="new")
        c.journal.append(EventType.EFFECT_COMPLETION, {"result": {}, "cost": {"usd": 2}}, key="llm/spend/0/x/1/1")
        id, _ = box.enqueue(message_class="failure_report", origin="test", summary="visible", occurrence_id="original")
        box.resolve(id, Resolution(kind="tombstone", link="retired"))
        reopened, _ = box.enqueue(message_class="failure_report", origin="other", summary="reopened", occurrence_id="other")
        box.resolve(reopened, Resolution(kind="tombstone", link="other"))
        for n in range(3):
            box.record_rereport(reopened, occurrence_id=f"report/{n}")
        legacy = (
            "merged:\n- done\n\nin flight:\n(none)\n\ninterrupted (the engine stopped mid-run; reject it, or start the engine to rerun it):\n- active\n\nblocked:\n- held: gate_failed\n\n"
            "intake:\n- new: source: human, state: confirmed, commit 123456789abc\n\nspend:\n$2.00\n\n"
            "Reject queue:\n- held: gate_failed at check -- confirm held after editing, or reject held\n\n"
            f"Confirmed-class tombstones:\n- {id}: failure_report, 0 re-reports\n\n"
            f"Tombstone reopens:\n- {reopened}: reopened at 3 re-reports\n"
        )
    else:
        legacy = (
            "merged:\n(none)\n\nin flight:\n(none)\n\nblocked:\n(none)\n\nintake:\n(none)\n\n"
            "spend:\n$0.00\n\nReject queue:\n(none)\n\nConfirmed-class tombstones:\n(none)\n\n"
            "Tombstone reopens:\n(none)\n"
        )
    box_block = (
        f"Suggestion Box (1 pending, 1 resolved):\n- {id}: failure_report: tombstone -> retired: visible\n- {reopened}: failure_report: reopened: reopened"
        if populated
        else "Suggestion Box (0 pending, 0 resolved):\n(none)"
    )
    legacy = legacy.replace("Confirmed-class tombstones:", box_block + "\n\nConfirmed-class tombstones:")
    before = {p: p.read_bytes() for p in c.repo.rglob("*") if p.is_file()}

    def forbidden(*args, **kwargs):
        pytest.fail("status invoked a write or active engine seam")

    for name in ("write", "publish", "replace"):
        monkeypatch.setattr(LocalFileSystem, name, forbidden)
    monkeypatch.setattr(Journal, "append", forbidden)
    monkeypatch.setattr(Lockfile, "acquire", forbidden)
    monkeypatch.setattr(Effects, "run", forbidden)
    monkeypatch.setattr(FakeLLM, "call", forbidden)
    monkeypatch.setattr(ProviderLLM, "call", forbidden)
    monkeypatch.setattr(CommandNotifications, "notify", forbidden)
    monkeypatch.setattr(Retro, "__call__", forbidden)
    monkeypatch.setattr(runner, "bind", forbidden)
    for name in ("enqueue", "record_rereport", "record_verdict", "resolve", "recover"):
        monkeypatch.setattr(Box, name, forbidden)
    git_run = Git._run

    async def read_only(git, repo, *args):
        assert args[0] in {"show", "rev-parse"}
        return await git_run(git, repo, *args)

    monkeypatch.setattr(Git, "_run", read_only)
    assert main(["status"], cwd=c.repo, env=ENV, clock=c.clock, pipeline=forbidden) == 0
    first = capsys.readouterr().out
    assert first.split("\n\ncurrent-window scorecard:")[0] + "\n" == legacy
    assert main(["status"], cwd=c.repo, env=ENV, clock=c.clock, pipeline=forbidden) == 0
    assert capsys.readouterr().out == first
    assert {p: p.read_bytes() for p in c.repo.rglob("*") if p.is_file()} == before


def test_box_status_labels_and_summary(tmp_path):
    box = Box(tmp_path / "box", LocalFileSystem())
    ids = [box.enqueue(message_class="suggestion", origin=str(n), summary=text)[0] for n, text in enumerate(["first\nsecret second line", "x" * 200, "third", "fourth"])]
    box.resolve(ids[1], Resolution(kind="ticket", link="repair"))
    box.resolve(ids[2], Resolution(kind="tombstone", link="old"))
    box.resolve(ids[3], Resolution(kind="declined", link="declined-id"))
    block = render(project([], box=box)).split("Suggestion Box (1 pending, 3 resolved):\n")[1].split("\n\n")[0]
    assert block.splitlines() == [
        f"- {ids[0]}: suggestion: pending: first",
        f"- {ids[1]}: suggestion: author -> repair: {'x' * 117}...",
        f"- {ids[2]}: suggestion: tombstone -> old: third",
        f"- {ids[3]}: suggestion: declined: fourth",
    ]  # Order, labels, first line and truncation differ from full or reversed messages.


def test_corrupt_box_does_not_receive_unknown_id_advice(tmp_path, capsys):
    from chupa.box import BoxError

    root = make_root(tmp_path)
    folder = root / ".chupa/state/box"
    folder.mkdir(parents=True)
    (folder / "corrupt.json").write_text("{}")
    with pytest.raises(BoxError, match="invalid box file"):
        main(["status"], cwd=root, env=ENV, clock=Clock())
    assert "name ids that chupa status lists" not in capsys.readouterr().err


def test_stale_verdict_is_visible_in_status_and_snapshot(tmp_path):
    from chupa import observe

    c, _, _, _ = rig(tmp_path)
    body = {
        "kind": "control_decision",
        "request_id": "request-1",
        "lifecycle_id": "life",
        "verb": "confirm",
        "hold_id": "hold",
        "stem": "draft",
        "actor": "human",
        "decision": "stale",
        "reason": "hold changed",
    }
    c.journal.append(EventType.SIGNAL, body)
    output = render(project(c.journal.read()))
    assert "Verdict decisions:\n- request-1: confirm draft: stale -- hold changed\n" in output
    ctx = observe.Context(c.repo, c.config.state_dir, c.repo / "config.yaml", None, c.git, ENV)
    assert observe.snapshot(ctx)["verdictDecisions"] == [{"request_id": "request-1", "verb": "confirm", "stem": "draft", "decision": "stale", "reason": "hold changed"}]
