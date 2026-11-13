"""Non-accepted control decisions are projected in journal order."""

from types import SimpleNamespace

from chupa.journal import EventType
from chupa.status import project, render


def event(request, verb, decision, reason, **extra):
    return SimpleNamespace(
        type=EventType.SIGNAL,
        ticket=None,
        key=None,
        ts="2026-01-01T00:00:00+00:00",
        body={"kind": "control_decision", "request_id": request, "verb": verb, "decision": decision, "reason": reason, **extra},
    )


def test_nonaccepted_decisions_and_render():
    status = project(
        [
            event("z-request", "confirm", "stale", "hold changed", stem="draft"),
            event("a-request", None, "rejected", "invalid request"),
        ]
    )
    assert status.verdict_decisions == (("z-request", "confirm", "draft", "stale", "hold changed"), ("a-request", "", "", "rejected", "invalid request"))
    block = render(status).split("Verdict decisions:\n", 1)[1].split("\n\n", 1)[0]
    assert block.splitlines() == ["- z-request: confirm draft: stale -- hold changed", "- a-request:  : rejected -- invalid request"]
    assert "None" not in block


def test_accepted_decision_is_not_shown():
    status = project([event("accepted-request", "reject", "accepted", "applied", stem="draft")])
    assert status.verdict_decisions == ()
    assert "Verdict decisions:" not in render(status)
