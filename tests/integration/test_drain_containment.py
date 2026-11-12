"""Dispatch exceptions are isolated to their ticket."""

from chupa import caps
from chupa.config import Caps
from chupa.journal import TERMINAL_STATES, EventType
from chupa.status import reject_queue
from tests.integration.test_drain import Script, commit_ticket, confirmed, drain, journal, make_root


class Boom(Script):
    def __init__(self, terminal=False):
        super().__init__()
        self.terminal = terminal

    def __call__(self, checkout):
        def boom(c):
            if self.terminal:
                c.journal.append(EventType.STATE_TRANSITION, {"to": "gate_failed", "stage": "review"}, ticket="aaa-boom")
            raise IsADirectoryError("context directory")

        self.hooks["aaa-boom"] = boom
        return super().__call__(checkout)


def transitions(root, stem):
    return [e.body for e in journal(root).read() if e.type == EventType.STATE_TRANSITION and e.ticket == stem]


def test_dispatch_raises_is_contained(tmp_path):
    root = make_root(tmp_path, "caps: {attempts: 1}\n")
    for stem in ("aaa-boom", "bbb-ok"):
        commit_ticket(root, stem, confirmed())
    script = Boom()
    assert drain(root, script) == 0
    assert transitions(root, "aaa-boom")[-1] == {"to": "infra_error", "stage": "dispatch", "reason": "dispatch_exception", "error": "IsADirectoryError: context directory"}
    assert transitions(root, "bbb-ok")[-1]["to"] == "merged"
    assert script.calls == ["aaa-boom", "bbb-ok"]


def test_dispatch_raises_after_terminal_keeps_one_terminal(tmp_path):
    root = make_root(tmp_path, "caps: {attempts: 1}\n")
    commit_ticket(root, "aaa-boom", confirmed())
    assert drain(root, Boom(terminal=True)) == 0
    bodies = transitions(root, "aaa-boom")
    running = max(i for i, body in enumerate(bodies) if body["to"] == "running")
    assert [body["to"] for body in bodies[running + 1 :] if body["to"] in TERMINAL_STATES] == ["gate_failed"]


def test_dispatch_raises_every_offer_reaches_reject_queue(tmp_path):
    root = make_root(tmp_path, "caps: {attempts: 3}\n")
    commit_ticket(root, "aaa-boom", confirmed())
    script = Boom()
    assert drain(root, script) == 0
    events = journal(root).read()
    assert caps.spent(Caps(attempts=3), events, "aaa-boom") == "attempts"
    assert reject_queue(events)["aaa-boom"]["to"] == "infra_error"
    assert script.calls == ["aaa-boom"] * 3
