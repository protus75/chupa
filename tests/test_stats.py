import json
from datetime import timedelta
from types import SimpleNamespace

from chupa.__main__ import main
from chupa.journal import EventType, Journal
from chupa.stats import project_stats
from tests.test_cli import ENV
from tests.test_drain import Clock, make_root


def test_projection_windows_durations_cycles_and_invoices(tmp_path):
    clock = Clock()
    journal = Journal(tmp_path, clock)
    def emit(minutes, typ, body, stem="one", key=None):
        clock.now += timedelta(minutes=minutes)
        return journal.append(typ, body, ticket=stem, key=key)
    emit(0, EventType.SIGNAL, {"signal": "ticket_intake", "new": True})
    emit(1, EventType.STATE_TRANSITION, {"to": "running"})
    emit(1, EventType.EFFECT_INTENT, {}, key="llm/one/0/implement/0/1")
    emit(3, EventType.EFFECT_COMPLETION, {}, key="llm/one/0/implement/0/1")
    emit(2, EventType.EFFECT_INTENT, {}, key="llm/one/0/review/0/1")
    emit(4, EventType.EFFECT_COMPLETION, {}, key="llm/one/0/review/0/1")
    emit(5, EventType.STATE_TRANSITION, {"to": "merged"})
    emit(1, EventType.STATE_TRANSITION, {"to": "running"}, "two")
    emit(1, EventType.STATE_TRANSITION, {"to": "gate_failed", "stage": "review", "dispatch": "escalate", "rung": {"tier": "high", "effort": "max"}}, "two")
    emit(1, EventType.STATE_TRANSITION, {"to": "running"}, "two")
    emit(1, EventType.STATE_TRANSITION, {"to": "merged"}, "two")
    emit(1, EventType.STATE_TRANSITION, {"to": "running"}, "three")
    emit(1, EventType.STATE_TRANSITION, {"to": "merged"}, "three")
    emit(1, EventType.EFFECT_COMPLETION, {}, key="ticket-plane/one/0/checks")
    emit(1, EventType.EFFECT_COMPLETION, {}, key="ticket-plane/two/0/checks")
    checks = {f"ticket-plane/{stem}/0/checks": SimpleNamespace(verification=[SimpleNamespace(argv=["test", "suite"], seconds=seconds), SimpleNamespace(argv=["old"], seconds=None)]) for stem, seconds in (("one", 60.0), ("two", 180.0))}
    result = project_stats(journal.read(), {"one": "feature", "two": "bug", "three": "bug"}, checks, now=clock(), window="7d")
    assert {k: result["durations"][k]["p50"] for k in ("implement", "check", "review", "merge", "lead_time")} == {"implement": 3, "check": 2, "review": 4, "merge": 5, "lead_time": 16}
    assert result["cycles"]["feature"]["attempts_mean"] == 1
    assert result["cycles"]["bug"]["attempts_mean"] == 1.5
    assert result["cycles"]["all"]["first_pass_yield"] == 2 / 3
    assert result["ladder"] == {"escalations": 1, "stems": 1, "rungs": {"high/max": 1}, "outcomes": {"merged": 1}}
    assert result["verification"] == {"test suite": {"n": 2, "p50": 2, "p90": 2.8, "max": 3}}
    short = project_stats(journal.read(), {}, checks, now=clock(), window="1h")
    assert short["window"]["events"] == len(journal.read())
    clock.now += timedelta(minutes=50)
    short = project_stats(journal.read(), {}, checks, now=clock(), window="1h")
    assert "implement" not in short["durations"]
    assert short["verification"]["test suite"]["n"] == 2
    clock.now += timedelta(minutes=10)
    short = project_stats(journal.read(), {}, checks, now=clock(), window="1h")
    assert short["verification"]["test suite"]["n"] == 1
    ticket_window = project_stats(journal.read(), {}, checks, now=clock(), window="2t")
    assert ticket_window["window"]["start"] == next(e.ts for e in journal.read() if e.ticket == "two" and e.body.get("to") == "merged")


def test_cli_json_refusal_and_no_write(tmp_path, capsys):
    root = make_root(tmp_path)
    clock = Clock()
    journal = Journal(root / ".chupa/state", clock)
    journal.append(EventType.STATE_TRANSITION, {"to": "merged"}, ticket="done")
    before = {p: p.read_bytes() for p in journal.dir.glob("*")}
    assert main(["stats", "--json"], cwd=root, env=ENV, clock=clock) == 0
    assert list(json.loads(capsys.readouterr().out)) == ["window", "throughput", "durations", "verification", "cycles", "ladder", "failures", "holds", "spend"]
    assert {p: p.read_bytes() for p in journal.dir.glob("*")} == before
    assert main(["stats", "--window", "0d"], cwd=root, env=ENV, clock=clock) == 2
    assert capsys.readouterr().err == "chupa stats: bad window 0d -- use <N>h, <N>d, or <N>t\n"
