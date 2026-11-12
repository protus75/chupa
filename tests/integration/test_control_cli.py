"""Real CLI lock routing and identity-bound durable requests."""

import json
from dataclasses import asdict
from types import SimpleNamespace

import pytest

from chupa import __main__ as entry
from chupa import control
from chupa.journal import Journal
from chupa.lockfile import Lockfile, LockHeld
from chupa.seams import LocalFileSystem
from tests.integration.test_cli import ENV, Clock, Stages, root, ticket, write


@pytest.mark.parametrize("dirless", ["draft", "Reject"])
def test_confirm_held_without_writer_lock(tmp_path, monkeypatch, capsys, dirless):
    import asyncio

    from chupa import runner
    from chupa.journal import EventType
    from chupa.tickets import stamp
    from tests.integration.test_mergequeue import admission_control, commit, ready
    from tests.integration.test_mergequeue import ctx as context_fixture

    ctx = context_fixture.__wrapped__(tmp_path)

    async def exercise():
        if dirless in ("draft", "Reject"):
            ticket = await ready(ctx)
            path = ctx.repo / f"tickets/{ticket.stem}/ticket.md"
            if dirless == "Reject":
                ctx.driver.journal.append(EventType.STATE_TRANSITION, {"to": "running"}, ticket=ticket.stem)
                ctx.driver.journal.append(EventType.STATE_TRANSITION, {"to": "gate_failed", "routed": "reject_queue"}, ticket=ticket.stem)
                assert await asyncio.to_thread(entry.main, ["confirm", ticket.stem], cwd=ctx.repo, env=ctx.env, clock=ctx.driver.clock, terminal=(lambda: True, lambda _: "y")) == 0
                assert await asyncio.to_thread(entry.main, ["confirm", ticket.stem], cwd=ctx.repo, env=ctx.env, clock=ctx.driver.clock, terminal=(lambda: True, lambda _: "y")) == 2
                assert [e.body["verdict"] for e in ctx.driver.journal.read() if e.body.get("signal") == "reject_verdict"] == ["keep"]
                return
            ctx.fs.write(path, stamp(path.read_text(), "state", "draft").encode())
            await commit(ctx, ctx.repo, [f"tickets/{ticket.stem}/ticket.md"])
            ctx.driver.journal.append(EventType.SIGNAL, {"signal": "ticket_intake", "state": "draft"}, ticket=ticket.stem)
            consumer = admission_control(ctx, known=lambda stem: (ctx.repo / f"tickets/{stem}/ticket.md").is_file())
            checkout = runner.Checkout(ctx.repo, ctx.config, ctx.env, ctx.exec_, ctx.git, ctx.driver.journal, ctx.fs, ctx.driver.clock, ctx.driver.sleep)
            owner = entry.build_serve(checkout)
            lock = Lockfile(ctx.config.state_dir, verb="drain", instance_id="live", clock=ctx.driver.clock)
            lock.acquire()
            control.write_active(ctx.config.state_dir, consumer.projection, ctx.fs, hold_id=None)
            try:
                assert await asyncio.to_thread(entry.main, ["confirm", ticket.stem], cwd=ctx.repo, env=ctx.env, clock=ctx.driver.clock, terminal=(lambda: True, lambda _: "y")) == 0
                consumer.inbox.consume()

                await consumer.inbox.settle_admissions(owner.apply_verdict)
                events = ctx.driver.journal.read()
                await consumer.inbox.settle_admissions(owner.apply_verdict)
                assert ctx.driver.journal.read() == events
                assert "state: confirmed" in path.read_text()
                assert sum(e.body.get("signal") == "draft_confirmed" for e in events) == 1
            finally:
                lock.release()
            return

    asyncio.run(exercise())


def invoke(root, verb):
    def forbidden(_):
        pytest.fail("control constructed a pipeline")

    return entry.main([verb], cwd=root, env=ENV, clock=Clock(), pipeline=forbidden)


def acquire(root):
    lock = Lockfile(root / ".chupa/state", verb="drain", instance_id="diagnostic-not-lifecycle", clock=Clock())
    lock.acquire()
    return lock


def discovery(root, life="restart-unique", hold=None):
    control.write_active(root / ".chupa/state", control.ControlProjection(life, hold), LocalFileSystem(), hold_id=hold)


def requests(root):
    return [json.loads(p.read_bytes()) for p in sorted((root / ".chupa/state/control/inbox").glob("*.json"))]


def test_live_pause_resume_publish_without_journal_write(root, monkeypatch, capsys):
    lock = acquire(root)
    ids = iter(["pause-exact", "resume-exact"])
    monkeypatch.setattr(entry, "uuid4", lambda: SimpleNamespace(hex=next(ids)))

    def forbidden(*args, **kwargs):
        pytest.fail("publisher wrote the journal or took the writer role")

    monkeypatch.setattr(Journal, "append", forbidden)
    monkeypatch.setattr(entry, "build_control", forbidden)
    monkeypatch.setattr(Lockfile, "release", forbidden)
    try:
        discovery(root, "life-exact")
        assert invoke(root, "pause") == 0
        assert capsys.readouterr().out == "pause submitted: pause-exact\n"
        discovery(root, "life-exact", "pause-exact")
        assert invoke(root, "resume") == 0
        assert capsys.readouterr().out == "resume submitted: resume-exact\n"
        assert requests(root) == [asdict(control.ControlRequest("pause-exact", "life-exact", "pause", None)), asdict(control.ControlRequest("resume-exact", "life-exact", "resume", "pause-exact"))]
        assert not (root / ".chupa/state/journal").exists()
        contender = Lockfile(lock.state_dir, verb="drain", instance_id="contender", clock=Clock())
        with pytest.raises(LockHeld):
            contender.acquire()
    finally:
        monkeypatch.undo()
        lock.release()


@pytest.mark.parametrize(
    "raw",
    [
        None,
        b"null\n",
        b"{",
        b"{}",
        b"[]",
        b'{"lifecycle_id":"","hold_id":"hold"}',
        b'{"lifecycle_id":1,"hold_id":null}',
        b'{"lifecycle_id":"life","hold_id":""}',
        b'{"lifecycle_id":"life","hold_id":true}',
        b'{"lifecycle_id":"life","hold_id":null,"extra":1}',
        b'{"lifecycle_id":"life","lifecycle_id":"other","hold_id":null}',
        b'{"lifecycle_id":"life","hold_id":null}',
    ],
)
def test_resume_requires_current_pause_identity(root, raw, capsys):
    lock = acquire(root)
    try:
        if raw is not None:
            LocalFileSystem().write(lock.state_dir / "control/active.json", raw)
        assert invoke(root, "resume") == 2
        err = capsys.readouterr().err
        assert "current control identity" in err and "submit a new request" in err
        assert requests(root) == []
        if raw != b'{"lifecycle_id":"life","hold_id":null}':
            assert "retry after the running engine publishes" in err
            assert invoke(root, "pause") == 2
            assert requests(root) == []
    finally:
        lock.release()


@pytest.mark.parametrize("verb", ["pause", "resume"])
@pytest.mark.parametrize("stale", [False, True])
def test_pause_resume_apply_directly_under_lock(root, monkeypatch, capsys, verb, stale):
    state = root / ".chupa/state"
    if stale:
        discovery(root, "old-life", "old-hold")
        control.publish_request(state, control.ControlRequest("old-pause", "old-life", "pause", None), LocalFileSystem())

    def contents():
        return {p.relative_to(state): p.read_bytes() for p in state.rglob("*") if p.is_file() and p.name != "chupa.lock"}

    before = contents()
    trace = []
    original_acquire, original_release = Lockfile.acquire, Lockfile.release

    def acquired(self):
        original_acquire(self)
        trace.append("acquire")

    def released(self):
        assert self.held
        trace.append("release")
        original_release(self)

    def forbidden(*args, **kwargs):
        pytest.fail("idle control allocated identity, constructed consumer or changed a record")

    with monkeypatch.context() as patch:
        patch.setattr(Lockfile, "acquire", acquired)
        patch.setattr(Lockfile, "release", released)
        patch.setattr(entry, "uuid4", forbidden)
        patch.setattr(entry, "build_control", forbidden)
        patch.setattr(control, "read_active", forbidden)
        patch.setattr(control, "publish_request", forbidden)
        patch.setattr(control, "write_active", forbidden)
        patch.setattr(Journal, "append", forbidden)
        assert invoke(root, verb) == 0
    assert capsys.readouterr().out == f"nothing running to {verb}\n"
    assert trace == ["acquire", "release"] and contents() == before
    lock = acquire(root)
    lock.release()
    write(root, "work", ticket())
    stages = Stages()
    lifecycles = []
    original = entry.build_control

    def build(checkout):
        consumer = original(checkout)
        lifecycles.append(consumer.projection.lifecycle_id)
        return consumer

    monkeypatch.setattr(entry, "build_control", build)
    assert entry.main(["drain"], cwd=root, env=ENV, clock=Clock(), pipeline=stages) == 0
    assert stages.calls == ["work"] and stages.lock_held == [True]
    assert len(lifecycles) == 1 and lifecycles[0] != "old-life"
    assert (state / "control/active.json").read_bytes() == b"null\n"
    if stale:
        [decision] = [e.body for e in stages.checkout.journal.read() if e.body.get("kind") == control.CONTROL_DECISION]
        assert decision["decision"] == "stale" and decision["lifecycle_id"] == "old-life"


def test_control_routing_lock_and_restart_races(root, monkeypatch, capsys):
    original = Lockfile.acquire
    next_owner = Lockfile(root / ".chupa/state", verb="drain", instance_id="next-owner", clock=Clock())
    replacement = Lockfile(root / ".chupa/state", verb="drain", instance_id="replacement", clock=Clock())

    # No preflight discovery check: an engine wins the CLI's actual lock acquisition.
    def race(self):
        if self is not replacement and not replacement.held:
            original(replacement)
        return original(self)

    monkeypatch.setattr(Lockfile, "acquire", race)
    try:
        assert invoke(root, "pause") == 2
        assert "retry after" in capsys.readouterr().err and requests(root) == []
        discovery(root, "old-life", "old-hold")
        publish = control.publish_request

        def replace_before_publication(state, request, fs):
            replacement.release()
            original(next_owner)
            discovery(root, "new-life")
            publish(state, request, fs)

        monkeypatch.setattr(control, "publish_request", replace_before_publication)
        assert invoke(root, "resume") == 0
        [request] = requests(root)
        assert request["lifecycle_id"] == "old-life" and request["hold_id"] == "old-hold"
        from tests.integration.test_control import Rig

        new = Rig(replacement.state_dir, lifecycle="new-life")
        new.inbox.consume()
        assert new.decisions()[0]["decision"] == "stale" and new.projection.pause_id is None
        assert requests(root) == [request]
        control.write_active(replacement.state_dir, None, LocalFileSystem(), hold_id=None)
        assert invoke(root, "pause") == 2
        assert len(requests(root)) == 1
    finally:
        if replacement.held:
            replacement.release()
        if next_owner.held:
            next_owner.release()


@pytest.mark.parametrize("binding", ["identity", "durability", "idle-lock"])
def test_cli_observables_detect_removed_bindings(root, monkeypatch, binding):
    if binding == "idle-lock":
        trace = []
        original = Lockfile.acquire

        def traced_acquire(lock):
            trace.append("lock")
            original(lock)

        monkeypatch.setattr(Lockfile, "acquire", traced_acquire)

        async def bypass(checkout, verb):
            return 0

        monkeypatch.setattr(entry, "_control", bypass)
        assert invoke(root, "pause") == 0
        with pytest.raises(AssertionError):
            assert trace == ["lock"]
        return
    lock = acquire(root)
    try:
        discovery(root, "target-life", "exact-hold")
        original = control.publish_request

        def broken(state, request, fs):
            if binding == "identity":
                original(state, control.ControlRequest(request.request_id, "wrong-life", "resume", "wrong-hold"), fs)

        monkeypatch.setattr(control, "publish_request", broken)
        assert invoke(root, "resume") == 0
        with pytest.raises(AssertionError):
            values = requests(root)
            assert len(values) == 1
            assert values[0]["lifecycle_id"] == "target-life" and values[0]["hold_id"] == "exact-hold"
    finally:
        lock.release()


def test_resume_publishes_selected_hold_identity(root, monkeypatch, capsys):
    lock = acquire(root)
    ids = iter(["first-resume", "second-resume"])
    monkeypatch.setattr(entry, "uuid4", lambda: SimpleNamespace(hex=next(ids)))
    try:
        # Selection is explicit: a dispatch pause projection must not replace the supplied admission id.
        control.write_active(lock.state_dir, control.ControlProjection("life", "pause"), LocalFileSystem(), hold_id="admission-exact")
        assert invoke(root, "resume") == 0
        assert requests(root) == [asdict(control.ControlRequest("first-resume", "life", "resume", "admission-exact"))]
        assert invoke(root, "resume") == 0
        assert len(requests(root)) == 2
        assert all(r["hold_id"] == "admission-exact" for r in requests(root))
        discovery(root, "life")
        assert invoke(root, "resume") == 2
        assert "no current hold identity" in capsys.readouterr().err
        assert len(requests(root)) == 2
    finally:
        lock.release()


def test_stop_refuses_when_idle_and_publishes_when_live(root, capsys):
    assert invoke(root, "stop") == 2
    assert "nothing running to stop" in capsys.readouterr().err
    lock = acquire(root)
    try:
        discovery(root, "stop-life")
        assert invoke(root, "stop") == 0
        [request] = requests(root)
        assert request["verb"] == "stop" and request["lifecycle_id"] == "stop-life" and request["hold_id"] is None
    finally:
        lock.release()


@pytest.mark.parametrize("kind", ["keep", "reject-queue", "reject-draft"])
def test_live_verdict_recovery_and_refusal(tmp_path, monkeypatch, capsys, kind):
    import asyncio

    from chupa import runner
    from chupa.journal import EventType
    from chupa.status import project, render
    from chupa.tickets import stamp
    from tests.integration.test_mergequeue import admission_control, commit, ready
    from tests.integration.test_mergequeue import ctx as context_fixture

    ctx = context_fixture.__wrapped__(tmp_path)

    async def exercise():
        ticket = await ready(ctx)
        stem = ticket.stem
        path = ctx.repo / f"tickets/{stem}/ticket.md"
        if kind == "reject-draft":
            ctx.fs.write(path, stamp(path.read_text(), "state", "draft").encode())
            await commit(ctx, ctx.repo, [f"tickets/{stem}/ticket.md"])
        else:
            ctx.driver.journal.append(EventType.STATE_TRANSITION, {"to": "gate_failed", "routed": "reject_queue"}, ticket=stem)
        child = ctx.repo / "tickets/child/ticket.md"
        ctx.fs.write(child, path.read_text().replace("state: draft", "state: confirmed").replace("## Depends on\nnone", f"## Depends on\n- {stem}").encode())
        await commit(ctx, ctx.repo, ["tickets/child/ticket.md"])
        checkout = runner.Checkout(ctx.repo, ctx.config, ctx.env, ctx.exec_, ctx.git, ctx.driver.journal, ctx.fs, ctx.driver.clock, ctx.driver.sleep)
        owner = entry.build_serve(checkout)
        inbox = admission_control(ctx, known=lambda name: (ctx.repo / f"tickets/{name}/ticket.md").is_file() or any(e.ticket == name for e in ctx.driver.journal.read())).inbox
        lock = Lockfile(ctx.config.state_dir, verb="drain", instance_id="live", clock=ctx.driver.clock)
        lock.acquire()
        control.write_active(ctx.config.state_dir, control.ControlProjection(inbox.lifecycle_id), ctx.fs, hold_id=None)
        verb = "confirm" if kind == "keep" else "reject"
        try:
            assert await asyncio.to_thread(entry.main, [verb, stem], cwd=ctx.repo, env=ctx.env, clock=ctx.driver.clock, terminal=(lambda: True, lambda _: "y")) == 0
            assert f"{verb} submitted:" in capsys.readouterr().out
            inbox.consume()
            original = owner.apply_verdict

            async def crash_after(stem, verb, key, actor):
                await original(stem, verb, key, actor)
                raise RuntimeError("crash after mutation")

            with pytest.raises(RuntimeError, match="crash after mutation"):
                await inbox.settle_admissions(crash_after)
            await inbox.settle_admissions(entry.build_serve(checkout).apply_verdict)
            await inbox.settle_admissions(owner.apply_verdict)
            events = ctx.driver.journal.read()
            verdicts = [e.body for e in events if e.ticket == stem and e.body.get("signal") == "reject_verdict"]
            if kind == "keep":
                assert len(verdicts) == 1 and verdicts[0]["verdict"] == "keep" and verdicts[0]["actor"] == "operator"
                assert await asyncio.to_thread(entry.main, [verb, stem], cwd=ctx.repo, env=ctx.env, clock=ctx.driver.clock, terminal=(lambda: True, lambda _: "y")) == 0
                inbox.consume()
                await inbox.settle_admissions(owner.apply_verdict)
                events = ctx.driver.journal.read()
                assert "already kept at this ticket content" in render(project(events))
                assert len([e for e in events if e.ticket == stem and e.body.get("signal") == "reject_verdict"]) == 1
            else:
                assert len(verdicts) == 1 and verdicts[0]["verdict"] == "kill"
                assert sum(e.ticket == stem and e.type == EventType.STATE_TRANSITION and e.body.get("to") == "rejected" for e in events) == 1
                assert "state: rejected" in await ctx.git._run(ctx.repo, "show", f"HEAD:tickets/{stem}/ticket.md")
                assert (await ctx.git._run(ctx.repo, "log", "-1", "--format=%s")).strip() == f"chupa({stem}): rejected"
                assert sum(e.ticket == "child" and e.body.get("signal") == "dead_dependency" and e.body.get("dead") == stem for e in events) == 1
                assert len(list((ctx.config.state_dir / "box").glob("*.json"))) == 1
        finally:
            lock.release()

    asyncio.run(exercise())


def test_live_confirm_old_draft_and_unknown_stem(tmp_path):
    import asyncio

    from chupa import runner
    from chupa.journal import EventType
    from chupa.tickets import stamp
    from tests.integration.test_mergequeue import admission_control, commit, ready
    from tests.integration.test_mergequeue import ctx as context_fixture

    ctx = context_fixture.__wrapped__(tmp_path)

    async def exercise():
        ticket = await ready(ctx)
        stem = ticket.stem
        path = ctx.repo / f"tickets/{stem}/ticket.md"
        ctx.fs.write(path, stamp(path.read_text(), "state", "draft").encode())
        await commit(ctx, ctx.repo, [f"tickets/{stem}/ticket.md"])
        checkout = runner.Checkout(ctx.repo, ctx.config, ctx.env, ctx.exec_, ctx.git, ctx.driver.journal, ctx.fs, ctx.driver.clock, ctx.driver.sleep)
        await runner.verdict(stem, checkout, kill=False)
        ctx.driver.journal.append(EventType.STATE_TRANSITION, {"to": "gate_failed", "routed": "reject_queue"}, ticket=stem)
        owner = entry.build_serve(checkout)
        inbox = admission_control(ctx, known=lambda name: (ctx.repo / f"tickets/{name}/ticket.md").is_file() or any(e.ticket == name for e in ctx.driver.journal.read())).inbox
        for identity, name in (("first", stem), ("missing", "missing"), ("known", "known")):
            if name == "known":
                ctx.driver.journal.append(EventType.STATE_TRANSITION, {"to": "gate_failed"}, ticket=name)
            control.publish_request(ctx.config.state_dir, control.AdmissionRequest(identity, inbox.lifecycle_id, "confirm", name, None, "operator"), ctx.fs)
        inbox.consume()
        key = f"ticket-plane/{stem}/confirm/first"
        ctx.driver.journal.append(EventType.EFFECT_INTENT, {}, ticket=stem, key=key)
        await inbox.settle_admissions(owner.apply_verdict)
        events = ctx.driver.journal.read()
        decisions = {e.body["request_id"]: e.body for e in events if e.body.get("kind") == control.CONTROL_DECISION}
        assert decisions["missing"]["decision"] == "stale" and "name a journaled stem" in decisions["missing"]["reason"]
        assert decisions["known"]["decision"] == "accepted"
        [refusal] = [e.body["result"]["refusal"] for e in events if e.type == EventType.EFFECT_COMPLETION and e.key == "ticket-plane/known/confirm/known"]
        assert "neither a draft nor in the Reject queue" in refusal
        assert sum(e.ticket == stem and e.body.get("signal") == "draft_confirmed" for e in events) == 1
        assert sum(e.ticket == stem and e.body.get("signal") == "reject_verdict" and e.body.get("verdict") == "keep" for e in events) == 1

    asyncio.run(exercise())


@pytest.mark.parametrize("verb,verdict", [("confirm", "keep"), ("reject", "kill")])
def test_yes_matches_typed_verdict(tmp_path, capsys, verb, verdict):
    import asyncio

    from chupa.journal import EventType
    from tests.integration.test_mergequeue import ctx as context_fixture
    from tests.integration.test_mergequeue import ready

    ctx = context_fixture.__wrapped__(tmp_path)

    def forbidden(_):
        pytest.fail("--yes must not read input")

    async def exercise():
        for stem in ("typed-ticket", "yes-ticket"):
            await ready(ctx, stem=stem)
            ctx.driver.journal.append(EventType.STATE_TRANSITION, {"to": "gate_failed", "routed": "reject_queue"}, ticket=stem)
        assert await asyncio.to_thread(entry.main, [verb, "yes-ticket"], cwd=ctx.repo, env=ctx.env, clock=ctx.driver.clock, terminal=(lambda: False, forbidden)) == 2
        assert "verdict requires an interactive terminal" in capsys.readouterr().err
        assert await asyncio.to_thread(entry.main, [verb, "typed-ticket"], cwd=ctx.repo, env=ctx.env, clock=ctx.driver.clock, terminal=(lambda: True, lambda _: "y")) == 0
        assert await asyncio.to_thread(entry.main, [verb, "yes-ticket", "--yes"], cwd=ctx.repo, env=ctx.env, clock=ctx.driver.clock, terminal=(lambda: False, forbidden)) == 0
        bodies = {e.ticket: e.body for e in ctx.driver.journal.read() if e.body.get("signal") == "reject_verdict"}
        assert bodies["yes-ticket"] == bodies["typed-ticket"]
        assert bodies["yes-ticket"]["verdict"] == verdict
        if verb == "reject":
            assert "state: rejected" in (ctx.repo / "tickets/yes-ticket/ticket.md").read_text()

    asyncio.run(exercise())


def test_retro_publishes_when_live(root, capsys):
    lock = acquire(root)
    try:
        discovery(root, "retro-life", "some-hold")
        assert invoke(root, "retro") == 0
        [request] = requests(root)
        assert request["verb"] == "retro" and request["lifecycle_id"] == "retro-life" and request["hold_id"] is None
        assert f"retro submitted: {request['request_id']}" in capsys.readouterr().out
    finally:
        lock.release()


@pytest.mark.parametrize("live", [False, True])
def test_extension_repeat_keep(tmp_path, capsys, live):
    import asyncio

    from chupa import runner
    from chupa.journal import EventType
    from chupa.status import project, render
    from tests.integration.test_mergequeue import admission_control, ready
    from tests.integration.test_mergequeue import ctx as context_fixture

    ctx = context_fixture.__wrapped__(tmp_path)

    async def exercise():
        ticket = await ready(ctx)
        stem = ticket.stem
        journal = ctx.driver.journal
        checkout = runner.Checkout(ctx.repo, ctx.config, ctx.env, ctx.exec_, ctx.git, journal, ctx.fs, ctx.driver.clock, ctx.driver.sleep)
        inbox = admission_control(ctx, known=lambda name: name == stem).inbox
        owner = entry.build_serve(checkout)
        lock = Lockfile(ctx.config.state_dir, verb="drain", instance_id="live", clock=ctx.driver.clock)
        if live:
            lock.acquire()
            control.write_active(ctx.config.state_dir, control.ControlProjection(inbox.lifecycle_id), ctx.fs, hold_id=None)

        async def invoke(flag):
            result = await asyncio.to_thread(
                entry.main, ["confirm", stem, flag], cwd=ctx.repo, env=ctx.env, clock=ctx.driver.clock, terminal=(lambda: False, lambda _: pytest.fail("unexpected prompt"))
            )
            output = capsys.readouterr()
            if live:
                assert result == 0 and "confirm submitted:" in output.out
                inbox.consume()
                await inbox.settle_admissions(owner.apply_verdict)
            return result, output

        def keeps():
            return [e.body for e in journal.read() if e.ticket == stem and e.body.get("signal") == "reject_verdict" and e.body.get("verdict") == "keep"]

        try:
            journal.append(EventType.STATE_TRANSITION, {"to": "gate_failed", "routed": "reject_queue"}, ticket=stem)
            assert (await invoke("--yes"))[0] == 0
            assert len(keeps()) == 1
            journal.append(EventType.STATE_TRANSITION, {"to": "gate_failed", "routed": "reject_queue"}, ticket=stem)
            result, output = await invoke("--yes")
            assert result == (0 if live else 2)
            assert "already kept at this ticket content" in (render(project(journal.read())) if live else output.err)
            assert len(keeps()) == 1
            assert (await invoke("--extension"))[0] == 0
            records = keeps()
            assert len(records) == 2
            assert records[0]["ticket_sha"] is not None
            assert records[0] == records[1] and records[1]["actor"] == "operator"
        finally:
            if live:
                lock.release()

    asyncio.run(exercise())


def test_non_engine_holder_refuses_stop_and_confirm(root, capsys):
    lock = Lockfile(root / ".chupa/state", verb="triage", instance_id="other", clock=Clock())
    lock.acquire()
    try:
        discovery(root)
        assert invoke(root, "stop") == 2
        assert "triage" in capsys.readouterr().err
        assert entry.main(["confirm", "candidate", "--yes"], cwd=root, env=ENV, clock=Clock()) == 2
        assert "triage" in capsys.readouterr().err
        assert requests(root) == []
    finally:
        lock.release()


@pytest.mark.parametrize("kind", ["valid", "invalid", "timeout"])
def test_live_confirm_intakes_before_submission(root, monkeypatch, capsys, kind):
    import fcntl
    from datetime import timedelta

    from chupa.lockfile import CommitLock
    from tests.integration.test_cli import git_out
    from tests.integration.test_drain import Clock as AdvancingClock
    from tests.integration.test_drain import commit_ticket, confirmed

    commit_ticket(root, "candidate", confirmed().replace("state: confirmed", "state: draft"))
    path = root / "tickets/candidate/ticket.md"
    path.write_text(path.read_text().replace("## Goal / Why", "## Goal / Why\nChanged.") if kind != "invalid" else path.read_text().replace("## Goal / Why", "## Invalid section"))
    lock = acquire(root)
    discovery(root)
    clock = AdvancingClock()

    async def sleep(seconds):
        clock.now += timedelta(seconds=seconds)

    monkeypatch.setattr(entry, "CommitLock", lambda state, **kwargs: CommitLock(state, clock=clock, sleep=sleep))
    try:
        with (root / ".chupa/state/commit.lock").open("w") as commit_lock:
            if kind == "timeout":
                fcntl.flock(commit_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            result = entry.main(["confirm", "candidate", "--yes"], cwd=root, env=ENV, clock=clock)
        output = capsys.readouterr()
        if kind == "valid":
            assert result == 0 and "confirm submitted:" in output.out
            assert "Changed." in git_out(root, "show", "main:tickets/candidate/ticket.md")
            assert len(requests(root)) == 1
        else:
            assert result == 2 and ("commit.lock" if kind == "timeout" else "failed intake") in output.err
            assert requests(root) == []
    finally:
        lock.release()
