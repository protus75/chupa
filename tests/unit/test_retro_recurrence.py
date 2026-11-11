import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from chupa.box import Box, Message, RereportJournal, Resolution, Verdict
from chupa.journal import Event, EventType
from chupa.retro import Retro, RetroArtifact, prior_findings, validate_recurrences
from tests.unit.test_retro_proposal import BASE, SPEC


class MemoryJournal:
    def __init__(self):
        self.events = []

    def read(self):
        return list(self.events)

    def append(self, type_, body, *, key=None, ticket=None):
        event = Event(1, type_, "2026-01-01T00:00:00+00:00", ticket, key, body)
        self.events.append(event)
        return event


def message(**changes):
    return Message.model_validate(BASE | SPEC | changes)


def setup_box(initial):
    journal = MemoryJournal()
    state = {"message": initial}

    def write(path, data):
        state["message"] = Message.model_validate_json(data)

    box = Box(Path("/box"), SimpleNamespace(write=write), rereport=RereportJournal(journal))
    box.messages = lambda: [state["message"]]
    box.get = lambda id: state["message"]
    return box, journal, state


def test_prior_findings_projection():
    messages = [
        message(id="merged", status="resolved", resolution=Resolution(kind="ticket", link="done")),
        message(id="running", status="resolved", resolution=Resolution(kind="ticket", link="live")),
        message(id="tomb", status="resolved", resolution=Resolution(kind="tombstone", link="old")),
        message(id="pending"),
    ]
    journal = MemoryJournal()
    journal.append(EventType.STATE_TRANSITION, {"to": "running"}, ticket="done")
    journal.append(EventType.STATE_TRANSITION, {"to": "merged"}, ticket="done")
    journal.append(EventType.STATE_TRANSITION, {"to": "running"}, ticket="live")
    rows = prior_findings(messages, journal.read())
    assert rows == [
        {
            "id": m.id,
            "fixed_failure": m.fixed_failure,
            "status": m.status,
            "resolution_kind": m.resolution.kind if m.resolution else None,
            "resolution_link": m.resolution.link if m.resolution else None,
            "fix_merged": m.id == "merged",
        }
        for m in messages
    ]


@pytest.mark.asyncio
async def test_unknown_recurrence_is_retry_finding():
    artifact = RetroArtifact.model_validate({"proposals": [SPEC | {"recurs": "missing"}]})
    result = await validate_recurrences(artifact, [{"id": "existing"}])
    assert result.verdict == "fail"
    assert [f.code for f in result.findings] == ["retro_recurs"]


def test_fresh_recurrences_and_reopen():
    box, journal, state = setup_box(message())
    for occurrence, count in [("a", 1), ("a", 1), ("b", 2)]:
        box.record_recurrence(state["message"], occurrence)
        assert state["message"].recurrences == count
    resolved = message(status="resolved", resolution=Resolution(kind="ticket", link="done"), verdict=Verdict(verdict="author", produced_by_spec_version="1", rationale="fix"))
    box, journal, state = setup_box(resolved)
    box.record_recurrence(resolved, "fresh", reopen=True)
    assert (state["message"].status, state["message"].reopen, state["message"].resolution, state["message"].verdict, state["message"].recurrences) == ("pending", True, None, None, 1)


@pytest.mark.parametrize("counted", [False, True])
@pytest.mark.parametrize("reopened", [False, True])
def test_intent_recovery(counted, reopened):
    initial = message(recurrences=4 if counted else 3, reopen=reopened and counted)
    box, journal, state = setup_box(initial)
    journal.append(EventType.EFFECT_INTENT, {"recurrences": 4, "reopened": reopened}, key="retro-recurrence/box-1/crash")
    box.record_recurrence(initial, "crash")
    assert state["message"].recurrences == 4
    completions = [e for e in journal.read() if e.type == EventType.EFFECT_COMPLETION]
    assert len(completions) == 1 and completions[0].body["result"] == {"recurrences": 4, "reopened": reopened}


@pytest.mark.asyncio
@pytest.mark.parametrize("state_name", ["pending", "merged", "running"])
async def test_emit_recurrence(monkeypatch, state_name):
    from chupa import daemon

    initial = message() if state_name == "pending" else message(status="resolved", resolution=Resolution(kind="ticket", link="fix"))
    box, journal, state = setup_box(initial)
    if state_name != "pending":
        journal.append(EventType.STATE_TRANSITION, {"to": state_name}, ticket="fix")
    calls = []
    box.enqueue = lambda **kwargs: calls.append(kwargs)
    monkeypatch.setattr(daemon, "storm_producer", lambda **kwargs: box)

    async def show(*args):
        return "# Retro receipt\n\n```json\n" + json.dumps({"proposals": [SPEC | {"recurs": initial.id}]}) + "\n```"

    checkout = SimpleNamespace(repo=Path("/repo"), git=SimpleNamespace(_run=show), config=SimpleNamespace(state_dir=Path("/state")), fs=None, journal=journal, clock=None)
    hook = Retro(checkout, None)
    for n in [1, 2, 3] if state_name == "running" else [1, 1]:
        event = Event(1, EventType.EFFECT_COMPLETION, "", None, f"retro/{n}", {"result": {"commit": "abc"}})
        await hook.emit_proposals(f"retro/{n}", event)
    assert calls == []
    assert state["message"].recurrences == (3 if state_name == "running" else 1)
    if state_name == "merged":
        assert (state["message"].status, state["message"].reopen, state["message"].resolution) == ("pending", True, None)
    if state_name == "running":
        assert (state["message"].status, state["message"].reports) == ("resolved", 0)
