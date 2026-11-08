"""Shared rig for integration tests of the continuous serve graph."""

import asyncio
import json
import time
from types import SimpleNamespace

from chupa import __main__ as cli
from chupa import runner, serve, stages
from chupa.artifacts import Cost, StageResult
from chupa.audit import audit_journal
from chupa.control import ControlRequest, publish_request
from chupa.daemon import TicketWriter
from chupa.driver import LlmStage
from chupa.journal import EventType
from chupa.llm import HANG, FakeLLM
from chupa.lockfile import Lockfile
from chupa.mergequeue import RED_STREAK, TREE_MISMATCH
from chupa.seams import LocalFileSystem, SubprocessExec
from chupa.stages import Invoice, PackingSlip
from tests.integration.test_cli import write as write_ticket
from tests.integration.test_restart_timers import repository
from tests.integration.test_scheduler import text, turn
from tests.integration.test_triage import reply


async def until(rig, predicate):
    deadline = time.monotonic() + 60
    n = 0
    while time.monotonic() < deadline:
        if predicate():
            return
        if n % 20 == 0:
            rig.time.advance(serve.SERVE_POLL_S)
        await turn()
        n += 1
    raise AssertionError("production graph did not reach the scripted boundary")


async def graph(root, monkeypatch, **kwargs):
    rig = await repository(root, monkeypatch)
    rig.fs.publish = LocalFileSystem().publish
    rig.exec.reply = reply("declined")
    owner = serve.Serve(
        rig.checkout,
        read=lambda stem: (root / f"tickets/{stem}/ticket.md").read_text() if (root / f"tickets/{stem}/ticket.md").is_file() else None,
        stems=lambda: (p.parent.name for p in (root / "tickets").glob("*/ticket.md")),
        **kwargs,
    )
    rig.owner = owner
    return rig


def write(root, stem, text):
    from tests.approval import approve
    from tests.integration.test_drain import Clock

    write_ticket(root, stem, text)
    approve(root, stem, Clock())


def script(monkeypatch, *, worktree=False, before=None, terminal="already_satisfied"):
    calls, contexts, artifacts = [], {}, {}

    async def implement(ctx, ticket, *, attempt):
        calls.append((ticket.stem, "implement", attempt))
        contexts[ticket.stem] = ctx
        if worktree:
            await stages.prepare_worktree(ctx, ticket.stem)
        if before is not None:
            await before(ctx, ticket, "implement", attempt)
        artifact = PackingSlip(
            produced_by_spec_version=1, produced_at_sha="fixture", stem=ticket.stem, branch=ticket.stem, outcome="ok", summary="scripted", run_record=f"tickets/{ticket.stem}/run.md"
        )
        artifacts[ticket.stem] = artifact
        return StageResult(outcome="ok", artifact=artifact, cost=Cost(), findings=[])

    async def check(ctx, ticket, slip, *, attempt):
        assert slip is artifacts[ticket.stem] and ctx is contexts[ticket.stem]
        calls.append((ticket.stem, "check", attempt))
        if before is not None:
            await before(ctx, ticket, "check", attempt)
        invoice = Invoice(produced_by_spec_version=1, produced_at_sha="fixture", stem=ticket.stem, passed=True, changed_files=[], inserted_lines=0, bypassed=[], reports=[])
        artifacts[ticket.stem] = invoice
        return StageResult(outcome=terminal, artifact=invoice, cost=Cost(), findings=[])

    async def review(ctx, ticket, invoice, *, attempt):
        assert invoice is artifacts[ticket.stem]
        calls.append((ticket.stem, "review", attempt))
        if before is not None:
            await before(ctx, ticket, "review", attempt)
        return StageResult(outcome="budget_exceeded", artifact=None, cost=Cost(), findings=[])

    async def diagnosis(*args, **kwargs):
        return SimpleNamespace(verdict="abandon-human", lessons=[], mechanical=None)

    monkeypatch.setattr(stages, "implement", implement)
    monkeypatch.setattr(stages, "check", check)
    monkeypatch.setattr(stages, "review", review)
    monkeypatch.setattr(runner, "diagnose", diagnosis)
    return calls, contexts, artifacts


def terminals(rig, stem=None):
    return [e for e in rig.journal.read() if e.type == EventType.STATE_TRANSITION and e.body.get("to") != "running" and (stem is None or e.ticket == stem)]


def request(rig, verb, identity, hold=None, lifecycle=None):
    owner = rig.owner
    publish_request(rig.checkout.config.state_dir, ControlRequest(identity, lifecycle or owner.control.projection.lifecycle_id, verb, hold), rig.fs)


def trip(rig, stem="work", stage="check", signature="a"):
    for index in range(6):
        rig.owner.box.enqueue(message_class="failure_report", origin=stem, stage=stage, outcome="gate_failed", summary=signature, occurrence_id=f"{signature}/{index}")
    return [identity for identity, target in rig.owner.storm.held_stages().items() if target == {"emitting_origin": stem, "emitting_stage": stage}][-1]


async def finish(rig, run):
    rig.owner.stop()
    await until(rig, run.done)
    assert await run == 0
    assert rig.owner.tasks.tasks == () and all(task.done() for task in rig.owner.workers)
    assert json.loads((rig.checkout.config.state_dir / "control/active.json").read_text()) is None
    assert audit_journal(rig.journal) == []


async def activated_graph(root, monkeypatch):
    rig = await graph(root, monkeypatch)
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: (rig.checkout.config.state_dir / "heartbeat").exists())
    finally:
        await finish(rig, run)
    return rig


class HeldLLM(FakeLLM):
    def __init__(self):
        super().__init__([HANG])
        self.entered, self.cleaning, self.release = (asyncio.Event() for _ in range(3))

    async def call(self, request):
        self.entered.set()
        try:
            return await super().call(request)
        finally:
            self.cleaning.set()
            await self.release.wait()


async def active_graph(root, monkeypatch, *, signals=None, failure=None):
    llm = HeldLLM()

    async def prepare(local):
        return runner.bind(local, llm)

    rig = await graph(root, monkeypatch, prepare=prepare, signals=signals, failure=failure)

    async def implementing(ctx, ticket, *, attempt):
        await stages.prepare_worktree(ctx, ticket.stem)
        return await ctx.driver.run(
            LlmStage(surface="implement", emits=PackingSlip, gates=[], render=lambda *_: "scripted implement"),
            ticket,
            ticket=ticket.stem,
            attempt=attempt,
            workspace=ctx.worktree(ticket.stem),
            tier="medium",
            effort="medium",
            stuck_budget=1200,
            expected_budget=300.0,
            scope_fence=(),
        )

    monkeypatch.setattr(stages, "implement", implementing)
    write(root, "work", text())
    run = asyncio.create_task(rig.owner.run())
    await until(rig, llm.entered.is_set)
    return rig, llm, run


async def admission_graph(root, monkeypatch, changes, *, endings=None, settled=None):
    """The merged CoreRig, actual CLI serve composition and real stages with scripted model replies."""
    from tests.integration.test_stages import SNAG, implement_reply, verdict

    endings = endings if endings is not None else {}
    models, contexts, returns = [], {}, []

    class Model(FakeLLM):
        async def call(self, req):
            stem = req.ticket
            if req.surface == "implement":
                for path, data in changes.get(stem, {}).items():
                    rig.fs.write(req.worktree / path, data.encode())
                if changes.get(stem):
                    await rig.checkout.git.add(req.worktree, list(changes[stem]))
                    await rig.checkout.git.commit(req.worktree, "scripted implementation")
                failed = endings.get(stem) == "implement"
                value = implement_reply(
                    "premise_failed" if failed else "already_satisfied" if endings.get(stem) == "noop" else "ok",
                    [{"code": "premise", "message": "scripted premise refusal", "paved_road": "revise this ticket"}] if failed else [],
                )
            elif req.surface == "review":
                value = verdict("snag", [SNAG]) if endings.get(stem) == "review" else verdict()
            elif req.surface == "diagnose":
                value = json.dumps({"verdict": "abandon-human", "lessons": ["inspect the admission findings"]})
            elif req.surface == "rework":
                value = json.dumps({"action": "escalate", "tickets": []})
            else:
                raise AssertionError(f"unexpected scripted surface {req.surface}")
            self.script.append(value)
            return await super().call(req)

    async def prepare(local):
        llm = Model([])
        models.append(llm)
        writer = runner.bind(local, llm)
        return writer

    rig = await graph(root, monkeypatch, prepare=prepare)
    rig.prepare, rig.models, rig.contexts, rig.returns = prepare, models, contexts, returns
    rig.fixture_confirm = True
    rig.held_returns = []
    process, scripted = SubprocessExec(), rig.exec.run

    async def execute(argv, **kwargs):
        if argv[0] in {"git", "true", "false", "grep", "python3"}:
            return await process.run(argv, **kwargs)
        return await scripted(argv, **kwargs)

    monkeypatch.setattr(rig.exec, "run", execute)
    review = stages.review

    async def reviewed(ctx, ticket, invoice, *, attempt):
        result = await review(ctx, ticket, invoice, attempt=attempt)
        contexts[ticket.stem] = ctx
        if result.outcome == "ok" and settled is not None:
            await settled(rig, ctx, ticket, attempt)
        return result

    monkeypatch.setattr(stages, "review", reviewed)
    drive = runner.drive

    async def driving(ctx, ticket, **kwargs):
        result = await drive(ctx, ticket, **kwargs)
        (rig.held_returns if result == "running" else returns).append((ticket.stem, result))
        return result

    monkeypatch.setattr(runner, "drive", driving)
    consume = TicketWriter.consume_result

    async def consumed(writer, ticket, result, *, attempt):
        live = (ticket.stem, attempt) in writer.admission.results
        await consume(writer, ticket, result, attempt=attempt)
        if not live:
            terminal = terminals(rig, ticket.stem)[-1].body["to"]
            returns.append((ticket.stem, terminal))

    monkeypatch.setattr(TicketWriter, "consume_result", consumed)
    return rig


def admission_ticket(root, stem, *, paths=("chupa/thing.py",), verification="true", depends="none", priority="P2"):
    from tests.integration.test_stages import TICKET

    raw = TICKET.format(bypass="").replace("priority: P2", f"priority: {priority}")
    raw = raw.replace("## Depends on\nnone", f"## Depends on\n{depends}")
    raw = raw.replace("## Scope fence\n- chupa/thing.py", "## Scope fence\n" + "\n".join(f"- {p}" for p in paths))
    raw = raw.replace("grep -q ok chupa/thing.py\nenv", verification)
    write(root, stem, raw)


async def start_admission(rig, monkeypatch):
    build = cli.build_serve

    def built(*args, **kwargs):
        rig.owner = build(*args, **kwargs)
        return rig.owner

    monkeypatch.setattr(cli, "build_serve", built)
    run = asyncio.create_task(serve.serve(rig.checkout, prepare=rig.prepare))
    await until(rig, lambda: rig.owner.ready.is_set())
    return run


def admission_config(root, *, command=None, safety=False, strategies=()):
    import yaml

    path = root / "config.yaml"
    config = yaml.safe_load(path.read_text())
    config["review"] = {"mechanical": [{"code": "combined", "argv": command or ["true"], "trigger": "always", "severity": "hard"}]}
    config["merge"] = {"safety_checks": ["combined"] if safety else [], "strategies": list(strategies)}
    path.write_text(yaml.safe_dump(config))


def notify_command(root, *, enabled=True):
    import sys

    import yaml

    path = root / "config.yaml"
    raw = yaml.safe_load(path.read_text())
    if enabled:
        raw["notify"] = [
            sys.executable,
            "-c",
            "import sys; from pathlib import Path; p=Path('deliveries.jsonl'); p.open('a').write(sys.argv[-1]+'\\n'); sys.exit(1 if Path('notify-fails').exists() else 0)",
        ]
    else:
        raw.pop("notify", None)
    path.write_text(yaml.safe_dump(raw))


def deliveries(root):
    path = root / "deliveries.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def notify_completions(rig):
    return [e for e in rig.journal.read() if e.type == EventType.EFFECT_COMPLETION and e.key.startswith("notify/")]


def escalation_batch(rig, label):
    hold = trip(rig, stem=f"{label}-storm", signature=label)
    # Reuse the real composition and canonical MergeQueue writer, without launching host work.
    queue = rig.owner.queue
    if queue is None:
        queue = runner.bind(rig.owner.checkout, FakeLLM([])).queue
        rig.owner.queue = queue
    queue._hold(f"{label}-red", {"kind": RED_STREAK, "stems": ["one", "two", "three"], "limit": 3})
    red = queue.hold_id
    queue._hold(f"{label}-tree", {"kind": TREE_MISMATCH, "checked_tree": "checked", "main_tree": "main"})
    return hold, red, queue.hold_id


class UpgradeChild:
    def __init__(self, rig):
        self.rig = rig
        self.calls = []

    async def run(self, argv, *, cwd, env, timeout, stdin_path=None):
        lock = Lockfile(self.rig.checkout.config.state_dir, instance_id="probe", clock=self.rig.time)
        lock.acquire()
        lock.release()
        self.calls.append((list(argv), cwd, env, timeout))
        return 7, "", ""


async def enable_upgrade(rig, engine):
    (engine / "chupa/specs").mkdir(parents=True, exist_ok=True)
    (engine / "chupa/specs/base.md").write_text("base")
    await rig.checkout.git.add(engine, ["chupa/specs/base.md"])
    await rig.checkout.git.commit(engine, "engine trees")
    rig.owner.engine = engine
    rig.owner.reexec = UpgradeChild(rig)
    rig.owner.argv = ("--config", "config.yaml", "serve")


async def retro_scenario(root, monkeypatch, mode):
    from chupa import retro

    entered, release, retro_entered, retro_release, checked = (asyncio.Event() for _ in range(5))

    async def settled(rig, ctx, ticket, attempt):
        if ticket.stem == "aa":
            entered.set()
            await release.wait()

    rig = await admission_graph(root, monkeypatch, {"aa": {"docs/a.txt": "a\n"}}, endings={"bb": "noop"}, settled=settled)
    config = root / "config.yaml"
    config.write_text(config.read_text() + f"retro:\n  enabled: {'false' if mode == 'disabled' else 'true'}\n  merges: {{every: 1}}\n")
    admission_ticket(root, "aa", paths=("docs/a.txt",), priority="P0")
    admission_ticket(root, "bb", paths=("docs/b.txt",), priority="P1")
    calls, aborted = [], []

    class FakeRetro:
        def __init__(self, checkout, pipeline):
            self.checkout = checkout
            assert pipeline.stages.driver is not None

        async def __call__(self, *, forced):
            calls.append(forced)
            assert terminals(rig, "aa")[-1].body["to"] == "merged"
            assert not any(e.ticket == "bb" and e.body.get("to") == "running" for e in rig.journal.read())
            assert not any(w.active or w.continuations for w in rig.owner.writers.values())
            retro_entered.set()
            await retro_release.wait()
            if mode == "failed":
                window = retro.project_window(rig.journal.read())
                rig.journal.append(
                    EventType.SIGNAL, {"kind": retro.RETRO_FAILED, "window_boundary": window.boundary, "trigger": "merges", "error_code": "ValueError"}, key=f"retro-failed/{window.boundary}/merges"
                )
            else:
                rig.journal.append(EventType.EFFECT_COMPLETION, {"result": {"commit": "fixture"}}, key="retro/1")

        async def abort_current(self):
            aborted.append(True)
            retro_release.set()

    monkeypatch.setattr(serve, "Retro", FakeRetro)
    check = rig.owner.check_retro

    async def observed_check():
        await check()
        if terminals(rig, "bb"):
            checked.set()

    monkeypatch.setattr(rig.owner, "check_retro", observed_check)
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, entered.is_set)
        if mode in {"requested", "kill"}:
            request(rig, "retro", "retro-request")
            await until(rig, lambda: rig.owner.control.projection.retro_id == "retro-request")
            assert not any(e.ticket == "bb" and e.body.get("to") == "running" for e in rig.journal.read())
        release.set()
        if mode != "disabled":
            await until(rig, retro_entered.is_set)
            assert calls == [mode in {"requested", "kill"}]
            assert not any(e.ticket == "bb" and e.body.get("to") == "running" for e in rig.journal.read())
            if mode == "kill":
                request(rig, "kill", "kill-retro")
                await until(rig, run.done)
                assert await run == 0 and aborted == [True]
                assert any(e.body.get("kind") == "kill_applied" for e in rig.journal.read())
                return
            retro_release.set()
        await until(rig, checked.is_set)
        await until(rig, lambda: rig.owner.upgrade_idle() and rig.owner.retro_task is None)
        for _ in range(5):
            rig.time.advance(serve.SERVE_POLL_S)
            await turn()
        assert [e.body["to"] for e in terminals(rig, "bb")] == ["already_satisfied"]
        assert calls == ([] if mode == "disabled" else [mode == "requested"])
        assert not rig.owner.retro_pending()
    finally:
        release.set()
        retro_release.set()
        if not run.done():
            await finish(rig, run)
