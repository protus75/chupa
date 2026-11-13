import asyncio
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from chupa import observe, runner
from chupa.box import Box
from chupa.journal import EventType
from chupa.reconcile import orphans


@pytest.fixture
def world(monkeypatch):
    from tests.unit.test_menu_admission import fake_snapshot_inputs

    monkeypatch.setattr(observe, "ticket_menu_inputs", fake_snapshot_inputs)
    events = []
    files = {}
    commits = []
    live = [False]
    root = Path("/fake")

    def append(kind, body, *, ticket=None, key=None):
        events.append(SimpleNamespace(type=kind, body=body, ticket=ticket, key=key, ts="2026-01-01T00:00:00+00:00"))

    class FS:
        def write(self, path, content):
            files[path] = content.decode()

    async def commit(repo, message, only):
        commits.append((message, list(only), files[root / only[0]]))
        return "commit-sha"

    git = SimpleNamespace(describe=AsyncMock(return_value="id"), rev_parse=AsyncMock(return_value="head-sha"), commit=commit, _run=AsyncMock(return_value=""))
    journal = SimpleNamespace(read=lambda: list(events), append=append)
    checkout = SimpleNamespace(repo=root, config=SimpleNamespace(state_dir=root / "state"), journal=journal, git=git, fs=FS(), clock=None)
    ctx = observe.Context(root, root / "state", root / "config.yaml", None, None, None)
    monkeypatch.setattr(Path, "is_file", lambda p: p in files)
    monkeypatch.setattr(Path, "exists", lambda p: p in files)
    monkeypatch.setattr(Path, "read_text", lambda p, *a, **kw: files[p])
    monkeypatch.setattr(runner, "intake", AsyncMock(return_value=SimpleNamespace(refused={})))
    monkeypatch.setattr(runner, "_dead_dependents", AsyncMock())

    class Lock:
        def __init__(self, *a, **kw):
            pass

        def acquire(self):
            pass

        def release(self):
            pass

    async def reap(c):
        for stem in orphans(c.journal.read()):
            append(EventType.STATE_TRANSITION, {"to": "abandoned"}, ticket=stem)

    monkeypatch.setattr(runner, "Lockfile", Lock)
    monkeypatch.setattr(runner, "reap", reap)
    monkeypatch.setattr(observe, "journal", lambda *a: [dict(type=e.type, body=e.body, ticket=e.ticket, key=e.key, ts=e.ts) for e in events])
    monkeypatch.setattr(
        observe,
        "load_tickets",
        lambda *a: (
            {
                s: SimpleNamespace(stem=s, frontmatter=SimpleNamespace(priority="P1", state="draft" if "state: draft" in text else "confirmed"), depends=(), runs_before=(), sections={})
                for p, text in files.items()
                if (s := p.parent.name) not in {"merged", "rejected"}
            },
            {},
        ),
    )
    monkeypatch.setattr(observe, "frontmatter", lambda path: {"priority": "P1"})
    monkeypatch.setattr(observe, "depends", lambda path: [])
    monkeypatch.setattr(observe, "committed_ticket_shas", lambda ctx: {p.parent.name: "blob" for p in files})
    monkeypatch.setattr(observe, "uncommitted_tickets", lambda ctx: (set(), set()))
    monkeypatch.setattr(observe, "commits", lambda ctx: {})
    monkeypatch.setattr(observe, "lock_holder", lambda *a: object() if live[0] else None)
    monkeypatch.setattr(observe, "lock_display", lambda *a: ("", None))
    monkeypatch.setattr(observe, "running_stems", lambda *a: ["running"] if live[0] else [])
    monkeypatch.setattr(observe, "operator_holds", lambda ctx, history: {"awaiting"} & {e.ticket for e in history})
    monkeypatch.setattr(Box, "messages", lambda self: [])

    def add(stem, state="confirmed"):
        files[root / "tickets" / stem / "ticket.md"] = f"---\nstate: {state}\npriority: P1\n---\n"

    def row(stem):
        return next((r for r in observe.snapshot(ctx)["rows"] if r["stem"] == stem), None)

    return SimpleNamespace(events=events, files=files, commits=commits, live=live, checkout=checkout, append=append, add=add, row=row)


@pytest.mark.parametrize(
    ("stem", "expected"),
    [
        ("draft", ("on", "on")),
        ("queued", ("off", "on")),
        ("parked", ("off", "on")),
        ("awaiting", ("on", "on")),
        ("retry", ("on", "on")),
        ("interrupted", ("off", "on")),
        ("interrupted-queue", ("off", "on")),
        ("merged", ("off", "off")),
        ("running", ("off", "off")),
    ],
)
def test_snapshot_matches_verdict(world, stem, expected):
    w = world
    w.add(stem, "draft" if stem == "draft" else "confirmed")
    if stem == "parked":
        w.append(EventType.STATE_TRANSITION, {"to": "running", "ticket_sha": "blob"}, ticket=stem)
        w.append(EventType.STATE_TRANSITION, {"to": "premise_failed", "stage": "requisition"}, ticket=stem)
    if stem in ("awaiting", "retry", "interrupted-queue"):
        w.append(EventType.STATE_TRANSITION, {"to": "gate_failed", "routed": "reject_queue"}, ticket=stem)
    if stem in ("interrupted", "interrupted-queue", "running"):
        w.append(EventType.STATE_TRANSITION, {"to": "running"}, ticket=stem)
    if stem == "merged":
        w.append(EventType.STATE_TRANSITION, {"to": "merged"}, ticket=stem)
    w.live[0] = stem == "running"
    menu = w.row(stem)["menu"]
    assert (menu["chupaConfirm"], menu["chupaReject"]) == expected
    original = list(w.events)
    for verb, key in [("confirm", "chupaConfirm"), ("reject", "chupaReject")]:
        w.events[:] = original
        if w.live[0]:
            result = asyncio.run(runner.apply_admission(stem, verb, "request-" + verb, "extension", w.checkout))
            allowed = result["refusal"] is None
            assert "is running" in result["refusal"]
        else:
            try:
                asyncio.run(runner.verdict(stem, w.checkout, kill=verb == "reject", extension=True))
                allowed = True
            except runner.Refusal:
                allowed = False
        assert (menu[key] == "on") == allowed


def test_rejected_has_no_row(world):
    world.add("rejected")
    world.append(EventType.STATE_TRANSITION, {"to": "rejected"}, ticket="rejected")
    assert world.row("rejected") is None


def test_reject_commits_and_journals(world):
    world.add("queued")
    assert world.row("queued")["menu"]["chupaReject"] == "on"
    asyncio.run(runner.verdict("queued", world.checkout, kill=True, extension=True))
    assert world.commits == [("chupa(queued): rejected", ["tickets/queued/ticket.md"], "---\nstate: rejected\npriority: P1\n---\n")]
    assert [(e.type, e.body.get("signal"), e.body.get("verdict"), e.body.get("to")) for e in world.events] == [
        (EventType.SIGNAL, "reject_verdict", "kill", None),
        (EventType.STATE_TRANSITION, None, None, "rejected"),
    ]
