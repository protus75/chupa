"""Fault-injection member for reconcile-on-entry recovery."""

import json

from chupa.journal import EventType
from eval.shakeout.bench import Bench
from eval.shakeout.run import Member, Observation
from eval.shakeout.stages import _commit, _ticket


class _EngineDeath(BaseException):
    pass


async def _engine_death_mid_call(bench: Bench) -> Observation:
    stem = "engine-death-mid-call"
    bench.add_ticket(stem, _ticket(stem, "recovered.txt", "test -f recovered.txt"))
    bench.script([
        _EngineDeath("shakeout engine death"),
        lambda req: _commit(req, {"recovered.txt": "ok\n"}),
        json.dumps({"verdict": "approve", "summary": "approved", "findings": []}),
    ])

    try:
        await bench.drain()
    except _EngineDeath:
        pass
    else:
        raise AssertionError("the scripted Implement call did not escape the drain")

    path = bench.config.worktree_root / stem
    events = bench.journal.read()
    dead_intent = next(event.key for event in events
                       if event.type == EventType.EFFECT_INTENT and event.ticket == stem)
    assert path.exists()
    assert not any(event.type == EventType.EFFECT_COMPLETION and event.key == dead_intent for event in events)

    report = await bench.drain()
    events = bench.journal.read()
    terminals = [event.body["to"] for event in events
                 if event.type == EventType.STATE_TRANSITION and event.ticket == stem
                 and event.body.get("to") != "running"]
    fresh_intent = next(event.key for event in events
                        if event.type == EventType.EFFECT_INTENT and event.ticket == stem
                        and event.key != dead_intent)
    harvest = bench.repo / "tickets" / stem / "attempts" / "0" / "harvest.json"

    assert terminals == ["abandoned", "merged"]
    assert harvest.is_file() and json.loads(harvest.read_text())["terminal"] == "abandoned"
    assert fresh_intent != dead_intent and stem in report.merged and not path.exists()
    return Observation("orphan_harvested_and_rerun_with_fresh_key", f"{stem}/1")


MEMBERS = (
    Member("engine_death_mid_call", "recovery", "Implement call raises after recording its effect intent",
           "orphan_harvested_and_rerun_with_fresh_key", _engine_death_mid_call),
)
