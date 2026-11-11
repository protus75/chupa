import pytest
from pydantic import ValidationError

from chupa.box import Message
from chupa.retro import RetroProposal

SPEC = {"fixed_failure": "bad result", "overcorrection_risk": "lost coverage", "proposed_spec_paths": ["specs/review.md"]}
TEST = {"fixed_failure": "slow test", "overcorrection_risk": "lost coverage", "test_issue": "slow", "proposed_paths": ["tests/unit/test_one.py"]}
BASE = {
    "id": "box-1",
    "seq": 1,
    "signature": "a" * 64,
    "message_class": "retro_finding",
    "summary": "slow test",
    "origin": "retro",
    "stage": None,
    "outcome": None,
    "bug_origin": None,
    "has_repro": None,
    "status": "pending",
    "verdict": None,
    "resolution": None,
    "retro_report_key": "retro/1",
}


def test_message_test_proposal_coherent():
    assert Message.model_validate(BASE | TEST).proposed_paths == ["tests/unit/test_one.py"]
    for proposal in (TEST | {"proposed_spec_paths": ["specs/review.md"]}, {"fixed_failure": "x", "overcorrection_risk": "y"}, SPEC | {"test_issue": "slow"}):
        with pytest.raises(ValidationError):
            Message.model_validate(BASE | proposal)
    for extra in ({"test_issue": "slow"}, {"proposed_paths": ["tests/x.py"]}):
        with pytest.raises(ValidationError):
            Message.model_validate(BASE | {"message_class": "suggestion", "retro_report_key": None} | extra)


def test_message_refuses_bad_paths():
    for path in ("/abs", "../x"):
        with pytest.raises(ValidationError):
            Message.model_validate(BASE | TEST | {"proposed_paths": [path]})


def test_message_loads_pre_change_retro_finding():
    message = Message.model_validate(BASE | SPEC)
    assert message.test_issue is None and message.proposed_paths == []


def test_retro_proposal_exactly_one():
    assert RetroProposal.model_validate(SPEC).proposed_spec_paths == ["specs/review.md"]
    assert RetroProposal.model_validate(TEST).test_issue == "slow"
    for proposal in (TEST | {"proposed_spec_paths": ["specs/review.md"]}, {"fixed_failure": "x", "overcorrection_risk": "y"}, TEST | {"test_issue": "unknown"}):
        with pytest.raises(ValidationError):
            RetroProposal.model_validate(proposal)


@pytest.mark.asyncio
async def test_emit_proposals_skips_existing_origin(monkeypatch):
    import hashlib
    import json
    from pathlib import Path
    from types import SimpleNamespace

    from chupa import daemon
    from chupa.journal import Event, EventType
    from chupa.retro import Retro

    other = SPEC | {"fixed_failure": "another failure"}
    pid = hashlib.sha256(json.dumps(SPEC, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()[:16]
    existing = f"retro-proposal/retro/1/{pid}"
    calls = []
    box = SimpleNamespace(messages=lambda: [SimpleNamespace(origin=existing)], enqueue=lambda **kwargs: calls.append(kwargs))
    monkeypatch.setattr(daemon, "storm_producer", lambda **kwargs: box)

    async def show(*args):
        assert args[1:] == ("show", "abc:tickets/retro/000001.md")
        return "# Retro receipt\n\n```json\n" + json.dumps({"proposals": [SPEC, other]}) + "\n```"

    checkout = SimpleNamespace(repo=Path("/repo"), git=SimpleNamespace(_run=show), config=SimpleNamespace(state_dir=Path("/state")), fs=None, journal=None, clock=None)
    event = Event(1, EventType.EFFECT_COMPLETION, "2026-01-01T00:00:00+00:00", None, "retro/1", {"result": {"commit": "abc"}})
    await Retro(checkout, None).emit_proposals("retro/1", event)
    assert len(calls) == 1
    assert calls[0]["fixed_failure"] == "another failure"
    assert calls[0]["origin"] != existing
