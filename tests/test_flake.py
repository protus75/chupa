"""Injected detection, durable record custody, and calibrated production dormancy."""

import asyncio
from dataclasses import replace
from types import SimpleNamespace

import pytest

from chupa import __main__ as cli, daemon
from chupa.box import Box, Message, signature
from chupa.config import Caps
from chupa.flake import Flake, FlakeError, RerunEvidence
from chupa.journal import EventType, Journal
from chupa.seams import LocalFileSystem
from tests.test_cli import Clock, ENV, Stages, root, ticket, write
from tests.test_daemon_composition import CoreRig, assert_startup_pause_wiring


def evidence(test_id="tests/test_12.py::test_34"):
    return RerunEvidence(test_id, "fail", "pass", True, True, True)


@pytest.fixture
def rig(tmp_path):
    journal = Journal(tmp_path / "state", Clock())
    box = Box(tmp_path / "box", LocalFileSystem())
    escalations = []
    flake = daemon.flake_detection(journal=journal, box=box,
                                  config=SimpleNamespace(caps=Caps()), escalate=escalations.append)
    return SimpleNamespace(journal=journal, box=box, flake=flake, escalations=escalations)


def detect(rig, test_id="tests/test_12.py::test_34", reason="assert 12 /tmp/a.py"):
    return rig.flake.detect(test_id=test_id, evidence=evidence(test_id),
                            summary="Named test failed then passed on bare rerun", reason=reason)


def release(rig, identity, fix="fix-flake"):
    rig.journal.append(EventType.SIGNAL, {
        "kind": "flake_released", "test_id": identity.test_id, "signature": identity.signature,
        "box_id": identity.box_id, "fix_stem": fix,
    }, ticket=None, key=f"flake-release/{identity.box_id}/{fix}")


@pytest.mark.asyncio
async def test_flake_construction_is_idle(monkeypatch):
    def forbid(*args, **kwargs):
        raise AssertionError("construction performed an effect")

    journal = SimpleNamespace(read=forbid, append=forbid)
    box = SimpleNamespace(enqueue=forbid, get=forbid)
    tasks = asyncio.all_tasks()
    monkeypatch.setattr(asyncio, "create_task", forbid)
    flake = daemon.flake_detection(journal=journal, box=box,
                                  config=SimpleNamespace(caps=Caps()), escalate=forbid)
    assert flake.journal is journal and flake.box is box and flake.cap == 5
    assert asyncio.all_tasks() == tasks


@pytest.mark.parametrize("change", [
    {"first_result": "pass"}, {"rerun_result": "fail"}, {"same_workspace": False},
    {"unchanged_code": False}, {"bare_rerun": False}, {"test_id": ""},
    {"test_id": "whole command"}, {"bare_rerun": 1},
])
def test_detection_requires_named_bare_rerun_evidence(rig, monkeypatch, change):
    def forbid(*args, **kwargs):
        raise AssertionError("invalid evidence reached state")

    with monkeypatch.context() as probe:
        probe.setattr(rig.box, "enqueue", forbid)
        probe.setattr(rig.journal, "read", forbid)
        probe.setattr(rig.journal, "append", forbid)
        with pytest.raises(FlakeError, match="provide one named test"):
            rig.flake.detect(test_id=evidence().test_id, evidence=replace(evidence(), **change),
                             summary="fail then pass", reason="failure")
        for kwargs in ({"test_id": " "}, {"summary": " "}, {"reason": ""}):
            args = dict(test_id=evidence().test_id, evidence=evidence(), summary="fail then pass", reason="failure")
            args.update(kwargs)
            with pytest.raises(FlakeError, match="provide one named test"):
                rig.flake.detect(**args)
    assert detect(rig).tests == {evidence().test_id}


def test_flake_report_uses_box_identity(rig):
    first = detect(rig)
    assert detect(rig, reason="assert 99 /other/path.py") == first
    message, = rig.box.messages()
    assert message.signature == signature("failure_report", evidence().test_id, "check", "gate_failed",
                                          reason="assert 12 /tmp/a.py")
    assert message.origin == evidence().test_id
    assert (message.message_class, message.stage, message.outcome, message.status) == (
        "failure_report", "check", "gate_failed", "pending")
    assert message.verdict is message.resolution is message.bug_origin is message.has_repro is None
    assert set(message.model_dump()) == set(Message.model_fields)
    assert first.active[message.id].signature == message.signature
    other = "tests/test_99.py::test_34"
    assert detect(rig, other).tests == {other, evidence().test_id}
    assert len(rig.box.messages()) == 2


def test_detection_signal_and_quarantine(rig, monkeypatch):
    append = rig.journal.append
    order = []
    enqueue = rig.box.enqueue

    def publish(**kwargs):
        assert not rig.flake.quarantine().tests
        result = enqueue(**kwargs)
        order.append("report")
        return result

    def durable(*args, **kwargs):
        assert len(rig.box.messages()) == 1
        assert not rig.flake.quarantine().tests
        order.append("append")
        result = append(*args, **kwargs)
        order.append("durable")
        return result

    monkeypatch.setattr(rig.box, "enqueue", publish)
    monkeypatch.setattr(rig.journal, "append", durable)
    projection = detect(rig)
    order.append("visible")
    assert order == ["report", "append", "durable", "visible"]
    event, = rig.journal.read()
    message, = rig.box.messages()
    assert event.type == EventType.SIGNAL and event.ticket is None
    assert event.key == f"flake/{message.id}"
    assert event.body == dict(kind="flake_detected", test_id=message.origin,
                             signature=message.signature, box_id=message.id)
    assert projection.tests == {message.origin}
    assert set(projection.active) == {message.id}


def test_detection_replay_and_conflicting_identity(rig, monkeypatch):
    projection = detect(rig)
    assert detect(rig) == projection and len(rig.journal.read()) == 1
    identity, = projection.active.values()
    release(rig, identity)
    assert not detect(rig).tests and len(rig.journal.read()) == 2
    original = rig.box.get
    monkeypatch.setattr(rig.box, "get", lambda id: original(id).model_copy(update={"signature": "a" * 64}))
    with pytest.raises(FlakeError, match="repair the evidence"):
        detect(rig)
    assert len(rig.journal.read()) == 2
    rig.journal.append(EventType.SIGNAL, {
        "kind": "flake_detected", "test_id": "other", "signature": identity.signature,
        "box_id": identity.box_id,
    }, key=f"flake/{identity.box_id}")
    with pytest.raises(FlakeError, match="conflicting detection identity"):
        rig.flake.quarantine()


def test_quarantine_reconstructs_across_segments(rig):
    first = detect(rig)
    identity, = first.active.values()
    (rig.journal.dir / "000002-20260102.jsonl").touch()
    second = detect(rig, reason="a different failure")
    assert len(second.active) == 2 and second.tests == {identity.test_id}
    release(rig, identity)
    rig.journal.append(EventType.SIGNAL, {"kind": "unrelated"}, ticket="a-ticket")
    restart = Flake(journal=Journal(rig.journal.dir.parent, Clock()), box=rig.box,
                    cap=5, escalate=rig.escalations.append)
    assert len(restart.quarantine().active) == 1
    assert restart.quarantine().tests == {identity.test_id}
    remaining, = restart.quarantine().active.values()
    release(rig, remaining)
    assert not restart.quarantine().tests
    # Historical duplicate detections cannot resurrect a released report.
    original = rig.journal.read()[0]
    rig.journal.append(original.type, original.body, key=original.key)
    assert not restart.quarantine().tests
    assert len(list(rig.journal.read_segments())) == 2


@pytest.mark.parametrize("change", [
    {"kind": "unknown"}, {"test_id": " "}, {"signature": "A" * 64},
    {"signature": 123}, {"box_id": ""}, {"extra": "field"},
])
def test_projection_refuses_malformed_records(rig, change):
    body = dict(kind="flake_detected", test_id="test", signature="a" * 64, box_id="box")
    body.update(change)
    rig.journal.append(EventType.SIGNAL, body, key="flake/box")
    with pytest.raises(FlakeError, match="repair the flake evidence"):
        rig.flake.quarantine()


@pytest.mark.parametrize("fault", ["ticket", "key", "type", "unmatched", "release_identity", "fix"])
def test_projection_refuses_bad_envelopes_and_releases(rig, fault):
    identity, = detect(rig).active.values()
    body = dict(kind="flake_released", test_id=identity.test_id, signature=identity.signature,
                box_id=identity.box_id, fix_stem="fix")
    envelope = dict(ticket=None, key=f"flake-release/{identity.box_id}/fix")
    type_ = EventType.SIGNAL
    if fault == "ticket":
        envelope["ticket"] = "ticket"
    elif fault == "key":
        envelope["key"] = "wrong"
    elif fault == "type":
        type_ = EventType.EFFECT_COMPLETION
    elif fault == "unmatched":
        body["box_id"] = "unknown"
        envelope["key"] = "flake-release/unknown/fix"
    elif fault == "release_identity":
        body["test_id"] = "other"
    else:
        body["fix_stem"] = " "
    rig.journal.append(type_, body, **envelope)
    with pytest.raises(FlakeError, match="repair the flake evidence"):
        rig.flake.quarantine()


def test_quarantine_cap_boundary(rig):
    rig.flake.cap = 2
    assert detect(rig, "one").tests == {"one"}
    assert detect(rig, "two").tests == {"one", "two"}
    projection = detect(rig, "one", reason="different failure")
    assert len(projection.active) == 3 and projection.tests == {"one", "two"}
    before = rig.journal.read()
    assert detect(rig, "three") == projection
    assert rig.journal.read() == before and len(rig.box.messages()) == 4
    assert rig.box.messages()[-1].origin == "three"
    assert len(rig.escalations) == 1
    assert "quarantine-cap crossed" in rig.escalations[0]
    assert "fix and release existing quarantines" in rig.escalations[0]
    detect(rig, "three")
    assert len(rig.box.messages()) == 4 and rig.journal.read() == before
    for identity in list(projection.active.values()):
        if identity.test_id == "one":
            release(rig, identity)
    admitted = detect(rig, "three")
    assert admitted.tests == {"two", "three"} and len(rig.box.messages()) == 4


@pytest.mark.parametrize("boundary", ["box", "published", "append", "durable", "escalation"])
def test_detection_failures_and_crash_replay(rig, monkeypatch, boundary):
    def fail(*args, **kwargs):
        raise RuntimeError("injected crash")

    if boundary == "escalation":
        rig.flake.cap = 1
        detect(rig, "existing")
    before = rig.journal.read()
    original_enqueue, original_append = rig.box.enqueue, rig.journal.append

    def published(**kwargs):
        original_enqueue(**kwargs)
        fail()

    def durable(*args, **kwargs):
        original_append(*args, **kwargs)
        fail()

    with monkeypatch.context() as probe:
        if boundary in {"box", "published"}:
            probe.setattr(rig.box, "enqueue", fail if boundary == "box" else published)
        elif boundary in {"append", "durable"}:
            probe.setattr(rig.journal, "append", fail if boundary == "append" else durable)
        else:
            probe.setattr(rig.flake, "escalate", fail)
        with pytest.raises(RuntimeError, match="injected crash"):
            detect(rig)
    rig.flake = Flake(journal=Journal(rig.journal.dir.parent, Clock()), box=rig.box,
                      cap=rig.flake.cap, escalate=rig.escalations.append)
    if boundary == "durable":
        assert rig.flake.quarantine().tests == {evidence().test_id}
    else:
        assert rig.journal.read() == before
        assert evidence().test_id not in rig.flake.quarantine().tests
    if boundary == "escalation":
        assert evidence().test_id not in detect(rig).tests
    else:
        assert detect(rig).tests == {evidence().test_id}
        assert len(rig.box.messages()) == 1 and len(rig.journal.read()) == 1
        assert detect(rig).tests == {evidence().test_id}
        assert len(rig.journal.read()) == 1


@pytest.mark.parametrize("verb", ["run", "drain"])
@pytest.mark.parametrize("trip", [None, "construction", "invocation"])
def test_flake_detection_is_dormant(root, tmp_path, monkeypatch, verb, trip):
    dormant = Flake(journal=Journal(root / ".chupa/state", Clock()),
                    box=Box(root / ".chupa/state/box", LocalFileSystem()),
                    cap=5, escalate=lambda message: None)

    def forbid_construct(*args, **kwargs):
        raise AssertionError("production constructed flake hook")

    def forbid_invoke(*args, **kwargs):
        raise AssertionError("production invoked flake detection")

    monkeypatch.setattr(daemon, "flake_detection", forbid_construct)
    monkeypatch.setattr(Flake, "__init__", forbid_construct)
    monkeypatch.setattr(Flake, "detect", forbid_invoke)
    # Calibrate both probes by injecting wiring at real production boundaries.
    control = cli.build_control

    def wired_control(checkout):
        if trip == "construction":
            daemon.flake_detection(journal=checkout.journal, box=dormant.box,
                                   config=checkout.config, escalate=dormant.escalate)
        elif trip == "invocation":
            dormant.detect(test_id=evidence().test_id, evidence=evidence(),
                           summary="Named test failed then passed", reason="assertion failed")
        return control(checkout)

    monkeypatch.setattr(cli, "build_control", wired_control)
    write(root, "work", ticket())
    stages = Stages()

    def exercise_cli():
        assert cli.main([verb, "work"] if verb == "run" else [verb], cwd=root,
                        env=ENV, clock=Clock(), pipeline=stages) == 0
        assert stages.calls == ["work"] and stages.lock_held == [True]
        assert not Box(root / ".chupa/state/box", LocalFileSystem()).messages()
        assert not any(e.body.get("kind") in {"flake_detected", "flake_released"}
                       for e in stages.checkout.journal.read())

    async def exercise_core():
        calls = []

        async def prepare(local):
            async def dispatch(t):
                calls.append(t.stem)
                return "merged"
            return dispatch

        directory = tmp_path / "core"
        directory.mkdir()
        composed = CoreRig(directory, prepare=prepare)
        assert_startup_pause_wiring(composed.core)
        t = await composed.add("work")
        assert await composed.core.admission.dispatch(t) == "merged"
        assert calls == ["work"] and composed.core.restart.ready
        assert composed.journal.read() == []
        assert not Box(directory / "box", LocalFileSystem()).messages()

    if trip:
        with pytest.raises(AssertionError, match="production .* flake"):
            exercise_cli()
        with pytest.raises(AssertionError, match="production .* flake"):
            asyncio.run(exercise_core())
    else:
        exercise_cli()
        asyncio.run(exercise_core())
