"""Drive the CLI's continuous graph with disposable repositories and injected time."""

import asyncio
import json

import pytest

from chupa import daemon, runner, stages
from chupa.audit import audit_journal
from chupa.control import publish_request
from chupa.journal import EventType
from chupa.lockfile import Lockfile
from chupa.merge import Admission
from chupa.mergequeue import CONFLICT_FACTS, RED_STREAK, TREE_MISMATCH, MergeQueue, TreeMismatch
from tests.integration.serve_rig import (
    UpgradeChild,
    admission_config,
    admission_graph,
    admission_ticket,
    enable_upgrade,
    finish,
    graph,
    request,
    retro_scenario,
    script,
    start_admission,
    terminals,
    trip,
    until,
    write,
)
from tests.integration.test_cli import ENV, root
from tests.integration.test_scheduler import text, turn


@pytest.mark.asyncio
@pytest.mark.parametrize("ending", ["ok", "noop", "implement", "check", "review"])
async def test_serve_routes_settled_run_to_composed_queue_once(root, monkeypatch, ending):
    changes = {} if ending == "noop" else {"chupa/other.py" if ending == "check" else "chupa/thing.py": "ok\n"}
    rig = await admission_graph(root, monkeypatch, {"work": changes}, endings={"work": ending})
    admission_ticket(root, "work")
    offers, results = [], []
    entered, release = asyncio.Event(), asyncio.Event()
    offer, admit = MergeQueue.offer, MergeQueue._admit

    def offered(queue, ticket, *, attempt):
        writer = rig.owner.writers[ticket.stem]
        assert queue is writer.queue is rig.owner.queue
        assert queue.ctx is writer.ctx and queue.control is rig.owner.control
        assert queue.ctx.driver.journal is queue.control.inbox.journal is rig.journal
        offers.append((ticket, attempt))
        offer(queue, ticket, attempt=attempt)

    async def admitted(queue, ticket, attempt):
        entered.set()
        await release.wait()
        result = await admit(queue, ticket, attempt)
        results.append(result)
        return result

    monkeypatch.setattr(MergeQueue, "offer", offered)
    monkeypatch.setattr(MergeQueue, "_admit", admitted)
    run = await start_admission(rig, monkeypatch)
    try:
        if ending == "ok":
            await until(rig, entered.is_set)
            assert len(offers) == 1 and offers[0][1] == 0
            assert not terminals(rig, "work") and rig.returns == []
            assert rig.owner.core.admission.active.stem == "work"
            assert not rig.owner.core.admission.task.done()
            release.set()
        await until(rig, lambda: rig.returns)
        [terminal] = terminals(rig, "work")
        if ending == "ok":
            assert rig.returns == [("work", "merged")] and isinstance(results[-1].artifact, Admission)
            assert terminal.body["commit"] == results[-1].artifact.commit
            assert await rig.checkout.git.rev_parse(root, "main") == results[-1].artifact.commit
        else:
            assert offers == [] and not any(r == "merged" for _, r in rig.returns)
            assert terminal.body["to"] == ("already_satisfied" if ending == "noop" else "premise_failed" if ending == "implement" else "gate_failed")
    finally:
        release.set()
        await finish(rig, run)


@pytest.mark.asyncio
async def test_serve_admission_rebases_regates_and_retires(root, monkeypatch):
    endings = {"work": "review"}

    async def moved(rig, ctx, ticket, attempt):
        if ticket.stem == "work":
            rig.pinned = await ctx.git.rev_parse(root, ticket.stem)
            assert "D tickets/" in await ctx.git.status_porcelain(ctx.worktree(ticket.stem))
            rig.fs.write(root / "chupa/other.py", b"moved\n")
            await ctx.git.add(root, ["chupa/other.py"])
            await ctx.git.commit(root, "main moves after approval")

    rig = await admission_graph(root, monkeypatch, {"work": {"chupa/thing.py": "ok\n"}, "dependent": {"chupa/dependent.py": "ok\n"}}, endings=endings, settled=moved)
    # The tracked ticket-plane copies come from a real failed producing run, never a ready fixture.
    admission_ticket(root, "work")
    first = await start_admission(rig, monkeypatch)
    await until(rig, lambda: rig.returns == [("work", "gate_failed")])
    await finish(rig, first)
    await runner.verdict("work", rig.checkout, kill=False)
    endings.clear()
    config = root / "config.yaml"
    config.write_text(
        config.read_text().replace("review: {}", "review: {mechanical: [{code: host, argv: ['true'], trigger: always, severity: hard}]}").replace("merge: {}", "merge: {safety_checks: [host]}")
    )
    admission_ticket(root, "dependent", paths=("chupa/dependent.py",), depends="- work")
    trace, trees = [], []
    for name in ("gather_safety_evidence", "gather_evidence"):
        original = getattr(stages, name)

        async def evidence(ctx, ticket, *args, _name=name, _original=original, **kwargs):
            if ticket.stem == "work" and rig.owner.queue.active == "work":
                trace.append(_name)
                assert (ctx.worktree(ticket.stem) / "chupa/other.py").read_text() == "moved\n"
            return await _original(ctx, ticket, *args, **kwargs)

        monkeypatch.setattr(stages, name, evidence)
    original = rig.checkout.git.rev_parse

    async def rev_parse(path, ref):
        sha = await original(path, ref)
        if ref.endswith("^{tree}"):
            trees.append((ref, sha))
        return sha

    monkeypatch.setattr(rig.checkout.git, "rev_parse", rev_parse)
    run = await start_admission(rig, monkeypatch)
    try:
        await until(rig, lambda: ("dependent", "merged") in rig.returns)
        assert rig.returns == [("work", "gate_failed"), ("work", "merged"), ("dependent", "merged")]
        assert trace == ["gather_safety_evidence", "gather_evidence", "gather_safety_evidence"]
        assert trees[:2] == [("HEAD^{tree}", trees[0][1]), ("main^{tree}", trees[0][1])]
        [merged] = [e for e in terminals(rig, "work") if e.body.get("to") == "merged"]
        assert merged.body == {"to": "merged", "commit": merged.body["commit"], "reviewed_sha": rig.pinned}
        assert merged.key is None
        message = await rig.checkout.git._run(root, "log", "-1", "--format=%B", merged.body["commit"])
        assert message.startswith("chupa(work): `thing.py` holds the word ok.")
        assert "chupa-ticket: work" in message and f"chupa-reviewed-sha: {rig.pinned}" in message
        [effect] = [e for e in rig.journal.read() if e.key == "merge/work/1" and e.type == EventType.EFFECT_COMPLETION]
        assert effect.body == {"result": {"commit": merged.body["commit"]}}
        assert not rig.checkout.config.worktree_root.joinpath("work").exists()
        assert not (await rig.checkout.git._run(root, "branch", "--list", "work")).strip()
        spools = rig.checkout.config.state_dir / "spools/work/1"
        for path in ("merge-integration/verify-01.txt", "merge-safety/host-01.txt", "merge-integration/host-01.txt"):
            assert "exit 0" in (spools / path).read_text()
        assert [r.surface for llm in rig.models for r in llm.requests].count("review") == 3
    finally:
        await finish(rig, run)


@pytest.mark.asyncio
@pytest.mark.parametrize("case", ["red-streak", "tree-mismatch", "exception", "cancel", "kill"])
async def test_serve_admission_holds_and_cleanup(root, monkeypatch, case):
    if case == "red-streak":
        changes = {stem: {f"chupa/{stem}.py": "red\n" if stem != "green" else "ok\n"} for stem in ("one", "two", "three", "green")}

        async def moved(rig, ctx, ticket, attempt):
            if ticket.stem != "green":
                rig.fs.write(root / "chupa/integration-marker", b"moved\n")
                await ctx.git.add(root, ["chupa/integration-marker"])
                await ctx.git.commit(root, "move main after check")

        rig = await admission_graph(root, monkeypatch, changes, settled=moved)
        admission_config(
            root,
            command=[
                "python3",
                "-c",
                "from pathlib import Path; import sys; sys.exit(int(Path('chupa/integration-marker').exists() and any(p.read_text().startswith('red') for p in Path('chupa').glob('*.py'))))",
            ],
        )
        from chupa import caps

        for stem in ("one", "two", "three"):
            for _ in range(rig.checkout.config.caps.retry):
                caps.consume(rig.journal, stem, "retry", "seed")
        for stem, priority in zip(changes, ("P0", "P1", "P2", "P3"), strict=True):
            admission_ticket(root, stem, paths=(f"chupa/{stem}.py",), priority=priority)
        offers, empty = [], asyncio.Event()
        offer, process = MergeQueue.offer, MergeQueue.process

        def offered(queue, ticket, **kwargs):
            offers.append((queue, ticket.stem, kwargs["attempt"]))
            offer(queue, ticket, **kwargs)

        async def processed(queue):
            if "green" in queue.pending and not empty.is_set():
                assert not any(e.body.get("to") == "merged" for e in terminals(rig, "green"))
                assert ("green", "merged") not in rig.returns
                empty.set()
                return []
            result = await process(queue)
            marker = root / "chupa/integration-marker"
            if marker.exists():
                marker.unlink()
                await rig.checkout.git.add(root, ["chupa/integration-marker"])
                await rig.checkout.git.commit(root, "reset integration marker")
            return result

        monkeypatch.setattr(MergeQueue, "offer", offered)
        monkeypatch.setattr(MergeQueue, "process", processed)
        run = await start_admission(rig, monkeypatch)
        try:
            await until(rig, lambda: ("three", "gate_failed") in rig.returns)
            queue = rig.owner.queue
            identity = queue.hold_id
            assert queue.paused and queue.red_stems == ["one", "two", "three"]
            assert "green" in rig.owner.core.scheduler.pending and not terminals(rig, "green")
            assert [stem for _, stem, _ in offers] == ["one", "two", "three"]
            assert len({id(q) for q, _, _ in offers}) == 1
            [event] = [e for e in rig.journal.read() if e.body.get("kind") == RED_STREAK]
            assert event.ticket == "three" and event.key is None and event.type == EventType.SIGNAL
            assert event.body == {"kind": RED_STREAK, "stems": ["one", "two", "three"], "limit": 3, "hold_id": identity}
            request(rig, "resume", "wrong-hold", hold="wrong")
            request(rig, "resume", "wrong-life", hold=identity, lifecycle="retired")
            request(rig, "pause", "operator-pause")
            await until(rig, lambda: rig.owner.control.projection.pause_id == "operator-pause")
            assert queue.paused and not terminals(rig, "green")
            decisions = {e.body["request_id"]: e.body["decision"] for e in rig.journal.read() if e.body.get("kind") == "control_decision"}
            assert decisions == {"wrong-hold": "stale", "wrong-life": "stale", "operator-pause": "accepted"}
            request(rig, "resume", "admission-release", hold=identity)
            await until(rig, lambda: identity in rig.owner.control.projection.released_hold_ids)
            await until(rig, lambda: not queue.paused)
            assert rig.owner.control.projection.pause_id == "operator-pause" and not terminals(rig, "green")
            request(rig, "resume", "pause-release", hold="operator-pause")
            await until(rig, empty.is_set)
            assert ("green", "merged") not in rig.returns and not terminals(rig, "green")
            await until(rig, lambda: ("green", "merged") in rig.returns)
            assert [stem for _, stem, _ in offers] == ["one", "two", "three", "green"]
            assert all(q is queue and attempt == 0 for q, _, attempt in offers)
            assert queue.red_stems == [] and not queue.pending and not queue.paused
            assert (root / "chupa/green.py").read_text() == "ok\n"
            assert all(not (root / f"chupa/{stem}.py").exists() for stem in ("one", "two", "three"))
        finally:
            await finish(rig, run)
        return

    async def settled(rig, ctx, ticket, attempt):
        rig.pinned = await ctx.git.rev_parse(root, ticket.stem)
        if case != "tree-mismatch":
            ctx.fs.write(root / "chupa/generated.txt", b"base\nmain\n")
            await ctx.git.add(root, ["chupa/generated.txt"])
            await ctx.git.commit(root, "main conflicts")
        rig.before = await ctx.git.rev_parse(root, "main")

    changes = {"chupa/thing.py": "ok\n"}
    if case != "tree-mismatch":
        changes["chupa/generated.txt"] = "base\nbranch\n"
    rig = await admission_graph(root, monkeypatch, {"work": changes}, settled=settled)
    if case != "tree-mismatch":
        rig.fs.write(root / "chupa/generated.txt", b"base\n")
        await rig.checkout.git.add(root, ["chupa/generated.txt"])
        await rig.checkout.git.commit(root, "generated base")
    admission_config(root, strategies=[{"paths": ["chupa/generated.txt"], "strategy": "union"}])
    admission_ticket(root, "work", paths=tuple(changes))
    entered, release, cleaning, abort_release = (asyncio.Event() for _ in range(4))
    failures, chronology = [], []
    error = RuntimeError("injected admission failure")
    call = rig.checkout.git._call

    async def called(path, *args, **kwargs):
        if args == ("rebase", "--abort"):
            cleaning.set()
            if case in {"cancel", "kill"}:
                await abort_release.wait()
            chronology.append("abort")
        return await call(path, *args, **kwargs)

    monkeypatch.setattr(rig.checkout.git, "_call", called)
    if case == "tree-mismatch":
        squash = rig.checkout.git.merge_squash

        async def corrupted(path, stem, message):
            # A real staged-tree defect produces a real mismatching commit, not a fake hash or terminal.
            rig.fs.write(path / "chupa/engine-defect.py", b"unexpected staged content\n")
            await rig.checkout.git.add(path, ["chupa/engine-defect.py"])
            return await squash(path, stem, message)

        monkeypatch.setattr(rig.checkout.git, "merge_squash", corrupted)
        admit = MergeQueue._admit

        async def admitted(queue, ticket, attempt):
            try:
                return await admit(queue, ticket, attempt)
            except TreeMismatch:
                entered.set()
                await release.wait()
                raise

        monkeypatch.setattr(MergeQueue, "_admit", admitted)
    else:

        async def resolve(*args):
            entered.set()
            if case == "exception":
                raise error
            await release.wait()
            raise AssertionError("cancel the admission before releasing this resolution barrier")

        monkeypatch.setattr(MergeQueue, "_resolve", resolve)
    run = await start_admission(rig, monkeypatch)
    rig.owner.failure = failures.append
    try:
        await until(rig, entered.is_set)
        queue = rig.owner.queue
        if case == "tree-mismatch":
            identity = queue.hold_id
            [event] = [e for e in rig.journal.read() if e.body.get("kind") == TREE_MISMATCH]
            checked = await rig.checkout.git.rev_parse(rig.checkout.config.worktree_root / "work", "HEAD^{tree}")
            main = await rig.checkout.git.rev_parse(root, "main^{tree}")
            assert checked != main and event.ticket == "work" and event.key is None
            assert event.body == {"kind": TREE_MISMATCH, "checked_tree": checked, "main_tree": main, "hold_id": identity}
            assert queue.paused and queue.active == "work" and not rig.returns
            request(rig, "resume", "wrong", hold="wrong")
            request(rig, "resume", "release", hold=identity)
            await until(rig, lambda: identity in rig.owner.control.projection.released_hold_ids)
            assert queue.paused and queue.active == "work" and not rig.returns
            release.set()
        elif case in {"cancel", "kill"}:
            assert queue._slot.locked() and queue.active == "work" and not terminals(rig, "work")
            if case == "kill":
                request(rig, "kill", "stop")
            else:
                run.cancel()
            await until(rig, cleaning.is_set)
            for _ in range(3):
                run.cancel()
                await turn()
                assert not run.done()
            assert not any(e.body.get("kind") == "kill_applied" for e in rig.journal.read())
            abort_release.set()
        await until(rig, run.done)
        assert await run == (0 if case in {"cancel", "kill"} else 1)
        assert rig.returns == [] and queue.active is None and not queue._slot.locked()
        assert rig.owner.tasks.tasks == () and all(t.done() for t in rig.owner.workers)
        assert all(t.cancelled() or not t._log_traceback for t in rig.owner.workers)
        assert rig.owner.core.admission.task is None and rig.owner.core.admission.active is None
        assert json.loads((rig.checkout.config.state_dir / "control/active.json").read_text()) is None
        workspace = rig.checkout.config.worktree_root / "work"
        assert workspace.exists() and not await rig.checkout.git.conflicted_paths(workspace)
        assert await rig.checkout.git.status_porcelain(workspace) == ""
        assert audit_journal(rig.journal) == []
        if case == "tree-mismatch":
            assert len(terminals(rig, "work")) == 1 and terminals(rig, "work")[0].body["to"] == "merged"
            assert await rig.checkout.git.rev_parse(root, "main") != rig.before
            assert len(failures) == 1 and isinstance(failures[0], TreeMismatch)
        else:
            assert chronology == ["abort"] and not terminals(rig, "work")
            assert await rig.checkout.git.rev_parse(root, "work") == rig.pinned
            assert await rig.checkout.git.rev_parse(root, "main") == rig.before
            assert failures == ([error] if case == "exception" else [])
    finally:
        release.set()
        abort_release.set()
        if not run.done():
            rig.owner.stop()
            await until(rig, run.done)
            await run


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["precheck", "safety", "integration", "host-red"])
async def test_serve_admission_refusal_keeps_main_green(root, monkeypatch, failure):
    command = ["python3", "-c", "from pathlib import Path; import sys; sys.exit(int('red' in Path('chupa/thing.py').read_text() and Path('chupa/other.py').exists()))"]

    async def settled(rig, ctx, ticket, attempt):
        if ticket.stem == "work":
            if failure == "precheck":
                ctx.fs.write(ctx.worktree(ticket.stem) / "tickets/forbidden.md", b"forbidden")
                await ctx.git.add(ctx.worktree(ticket.stem), ["tickets/forbidden.md"])
                await ctx.git.commit(ctx.worktree(ticket.stem), "committed ticket-plane violation")
            if failure == "host-red":
                ctx.fs.write(root / "main-moved.txt", b"main moved\n")
                await ctx.git.add(root, ["main-moved.txt"])
                await ctx.git.commit(root, "main moves")
            rig.before = await ctx.git.rev_parse(root, "main")
        elif ticket.stem == "next":
            ctx.fs.write(root / "main-moved-next.txt", b"main moved before next admission\n")
            await ctx.git.add(root, ["main-moved-next.txt"])
            await ctx.git.commit(root, "main moves before next admission")

    rig = await admission_graph(root, monkeypatch, {"work": {"chupa/thing.py": "ok red\n"}, "main-side": {"chupa/other.py": "moved\n"}, "next": {"chupa/next.py": "ok\n"}}, settled=settled)
    from chupa import caps

    for _ in range(rig.checkout.config.caps.retry):
        caps.consume(rig.journal, "work", "retry", "seed")
    admission_config(root, command=["false"] if failure == "host-red" else command, safety=failure == "safety")
    admission_ticket(root, "work", priority="P0", verification="grep -q absent chupa/thing.py" if failure == "host-red" else "true")
    # Stage selection suspends a genuine producing run while another genuine run moves main.
    hold = trip(rig, stage="review") if failure in {"safety", "integration"} else None
    if hold:
        admission_ticket(root, "main-side", paths=("chupa/other.py",))
    preserved, offers = [], []
    harvest, offer = runner.harvest_failure, MergeQueue.offer
    admit = MergeQueue._admit

    async def admitted(queue, ticket, attempt):
        before = await queue.ctx.git.rev_parse(root, "main")
        result = await admit(queue, ticket, attempt)
        if ticket.stem == "work":
            assert result.outcome == "gate_failed"
            assert await queue.ctx.git.rev_parse(root, "main") == before
            assert queue.ctx.worktree(ticket.stem).exists()
        return result

    monkeypatch.setattr(MergeQueue, "_admit", admitted)

    async def harvested(ctx, ticket, **kwargs):
        if ticket.stem == "work" and kwargs["stage"] == "merge":
            if failure == "precheck":
                assert await ctx.git.rev_parse(root, "main") == rig.before
            assert ctx.worktree(ticket.stem).exists() and await ctx.git.rev_parse(root, ticket.stem)
            assert "red" not in (root / "chupa/thing.py").read_text()
            preserved.append(kwargs)
        await harvest(ctx, ticket, **kwargs)

    def offered(queue, ticket, **kwargs):
        offers.append(ticket.stem)
        offer(queue, ticket, **kwargs)

    monkeypatch.setattr(runner, "harvest_failure", harvested)
    monkeypatch.setattr(MergeQueue, "offer", offered)
    run = await start_admission(rig, monkeypatch)
    try:
        if hold:
            await until(rig, lambda: ("main-side", "merged") in rig.returns)
            candidate = rig.owner.writers["work"].ctx.worktree("work")
            # Both branches passed Check independently; this command also proves the old candidate alone green.
            assert (await rig.exec.run(command, cwd=candidate, env=ENV, timeout=30))[0] == 0
            assert (await rig.exec.run(command, cwd=root, env=ENV, timeout=30))[0] == 0
            request(rig, "resume", "review-release", hold=hold)
        await until(rig, lambda: ("work", "gate_failed") in rig.returns)
        [failure_args] = preserved
        code = "post_rebase_regate" if failure == "precheck" else "combined"
        assert code in {f.code for f in failure_args["findings"]}
        assert all(f.paved_road for f in failure_args["findings"])
        assert ("work" in offers) == (failure != "precheck")
        assert len(terminals(rig, "work")) == 1
        assert (root / "tickets/work/attempts/0/harvest.json").is_file()
        spools = rig.checkout.config.state_dir / "spools/work/0"
        assert (spools / "merge-integration/verify-01.txt").exists() == (failure in {"integration", "host-red"})
        if failure == "host-red":
            # Ticket base-red remains attributable, while an always-hard host failure still refuses.
            assert (spools / "merge-integration/verify-01-base.txt").is_file()
            assert not rig.checkout.config.worktree_root.joinpath(".base/work").exists()
        assert rig.owner.queue.red_stems == (["work"] if failure in {"integration", "host-red"} else [])
        # A fresh producing candidate proceeds; the old refused branch never reaches main.
        admission_config(root)
        admission_ticket(root, "next", paths=("chupa/next.py",))
        await until(rig, lambda: ("next", "merged") in rig.returns)
        assert "red" not in (root / "chupa/thing.py").read_text() and not rig.owner.queue.red_stems
        assert [req.surface for llm in rig.models for req in llm.requests if req.ticket == "work"].count("diagnose") == 0
    finally:
        await finish(rig, run)


@pytest.mark.asyncio
@pytest.mark.parametrize("resolution", ["mechanical", "handoff"])
async def test_serve_conflict_handoff_runs_after_admission_unwinds(root, monkeypatch, resolution):
    async def settled(rig, ctx, ticket, attempt):
        rig.pinned = await ctx.git.rev_parse(root, ticket.stem)
        ctx.fs.write(root / "chupa/generated.txt", b"base\nmain\n")
        await ctx.git.add(root, ["chupa/generated.txt"])
        await ctx.git.commit(root, "main conflicts after review")
        rig.before = await ctx.git.rev_parse(root, "main")

    rig = await admission_graph(root, monkeypatch, {"work": {"chupa/thing.py": "ok\n", "chupa/generated.txt": "base\nbranch\n"}}, settled=settled)
    rig.fs.write(root / "chupa/generated.txt", b"base\n")
    await rig.checkout.git.add(root, ["chupa/generated.txt"])
    await rig.checkout.git.commit(root, "generated base")
    admission_config(root, safety=True, strategies=[{"paths": ["chupa/generated.txt"], "strategy": "union"}] if resolution == "mechanical" else [])
    admission_ticket(root, "work", paths=("chupa/thing.py", "chupa/generated.txt"), verification="grep -q ok chupa/thing.py")
    chronology, gates = [], []
    call = rig.checkout.git._call

    async def called(path, *args, **kwargs):
        result = await call(path, *args, **kwargs)
        if args == ("rebase", "--abort"):
            chronology.append("abort")
        return result

    monkeypatch.setattr(rig.checkout.git, "_call", called)
    process = MergeQueue.process

    async def processed(queue):
        result = await process(queue)
        if result:
            assert queue.active is None and not queue._slot.locked()
            chronology.append("unwind")
        return result

    monkeypatch.setattr(MergeQueue, "process", processed)
    apply = daemon.apply_rework

    async def reworked(ctx, ticket, findings, **kwargs):
        queue = rig.owner.queue
        handoff = kwargs["handoff"]
        assert queue.active is None and not queue._slot.locked()
        assert chronology == ["abort", "unwind"]
        assert handoff.approval_invalidated and handoff.reviewed_sha == rig.pinned
        assert handoff.conflicted_paths == ["chupa/generated.txt"]
        assert (root / "chupa/generated.txt").read_text() == "base\nmain\n"
        assert await ctx.git.rev_parse(root, ticket.stem) == rig.pinned
        assert not await ctx.git.conflicted_paths(ctx.worktree(ticket.stem))
        assert await ctx.git.status_porcelain(ctx.worktree(ticket.stem)) == ""
        chronology.append("rework")
        return await apply(ctx, ticket, findings, **kwargs)

    monkeypatch.setattr(daemon, "apply_rework", reworked)
    from chupa import merge as merge_owner

    for gate in stages.CHECK_GATES + merge_owner.MERGE_GATES:
        check = gate.check

        def checked(*args, _gate=gate, _check=check):
            if rig.owner.queue is not None and rig.owner.queue.active == "work":
                gates.append(_gate.code)
            return _check(*args)

        monkeypatch.setattr(gate, "check", checked)
    run = await start_admission(rig, monkeypatch)
    try:
        await until(rig, lambda: rig.returns)
        [facts] = [e for e in rig.journal.read() if e.body.get("kind") == CONFLICT_FACTS]
        assert facts.ticket == "work" and facts.key is None and facts.type == EventType.SIGNAL
        assert facts.body == {
            "kind": CONFLICT_FACTS,
            "conflicted_paths": ["chupa/generated.txt"],
            "resolving_rung": "mechanical" if resolution == "mechanical" else "rework",
            "strategy_paths": ["chupa/generated.txt"] if resolution == "mechanical" else [],
            "integration_red_paths": [],
        }
        [terminal] = terminals(rig, "work")
        if resolution == "mechanical":
            assert rig.returns == [("work", "merged")] and chronology == ["unwind"]
            assert (root / "chupa/generated.txt").read_text() == "base\nmain\nbranch\n"
            assert gates == [
                "scope_fence",
                "run_record",
                "ticket_schema",
                "post_rebase_regate",
                "correctness_review",
                "scope_fence",
                "verification",
                "run_record",
                "diff_budget",
                "core_drift",
                "bug_evidence",
                "ticket_schema",
                "post_rebase_regate",
                "correctness_review",
            ]
            for tier in ("safety", "integration"):
                assert "exit 0" in (rig.checkout.config.state_dir / f"spools/work/0/merge-{tier}/host-01.txt").read_text()
            assert terminal.body["reviewed_sha"] == rig.pinned
        else:
            assert rig.returns == [("work", "gate_failed")] and chronology == ["abort", "unwind", "rework"]
            assert terminal.body["stage"] == "merge" and "commit" not in terminal.body
            [req] = [r for llm in rig.models for r in llm.requests if r.surface == "rework"]
            assert '"approval_invalidated":true' in req.rendered
            assert any(e.body.get("signal") == "rework_order" for e in rig.journal.read())
            assert not gates
    finally:
        await finish(rig, run)
