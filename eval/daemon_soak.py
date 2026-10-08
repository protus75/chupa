"""Deterministic production soak and canonical report writer (19.P3.daemon-soak-runner)."""

import argparse
import asyncio
import json
import os
import sys
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

import yaml

from chupa import runner, serve
from chupa.artifacts import (DAEMON_SOAK_MEMBERS, DAEMON_SOAK_SPEC_VERSION,
                            DaemonSoakEntry, DaemonSoakReport, Harvest)
from chupa.audit import audit_journal
from chupa.config import load_config
from chupa.git import Git
from chupa.journal import EventType, Journal, TERMINAL_STATES
from chupa.llm import FakeLLM, HANG
from chupa.mergequeue import CONFLICT_FACTS, ConflictHandoff
from chupa.reconcile import RECOVERY_ALERT
from chupa.seams import FileSystem, LocalFileSystem, SubprocessExec
from chupa.stages import Invoice, read_review


def write_report(path: Path, report: DaemonSoakReport, fs: FileSystem) -> None:
    # Revalidate nested lists and values that model_construct/model_copy can bypass.
    validated = DaemonSoakReport.model_validate(report.model_dump())
    if any(not entry.green for entry in validated.entries):
        raise ValueError("refusing a red daemon soak report; resolve observations and auditor violations first")
    fs.write(path, (validated.model_dump_json(indent=2) + "\n").encode("utf-8"))


class SoakRefused(Exception):
    def __init__(self, member: str, detail: str):
        super().__init__(f"{member}: {detail}; repair this member's production behavior/evidence "
                         "and rerun uv run python -m eval.daemon_soak --out <path>")


async def _turn() -> None:
    future = asyncio.get_running_loop().create_future()
    asyncio.get_running_loop().call_soon(future.set_result, None)
    await future


class _Time:
    def __init__(self):
        self.start = self.now = datetime(2026, 1, 1, tzinfo=UTC)
        self.waits = []
        self.steps = []
        self.sleeps = []

    def __call__(self):
        return self.now

    async def sleep(self, seconds):
        future = asyncio.get_running_loop().create_future()
        self.sleeps.append(seconds)
        self.waits.append((self.now + timedelta(seconds=seconds), future))
        try:
            await future
        finally:
            self.waits = [(d, f) for d, f in self.waits if f is not future]

    def advance(self, seconds):
        self.now += timedelta(seconds=seconds)
        self.steps.append(seconds)
        for deadline, future in self.waits:
            if deadline <= self.now and not future.done():
                future.set_result(None)


class _FS(LocalFileSystem):
    def __init__(self, clock):
        self.clock = clock
        self.heartbeats = []

    def write(self, path, data):
        super().write(path, data)
        if path.name == "heartbeat":
            self.heartbeats.append(self.clock())


class _Exec:
    """Real Git and Verification; the provider and remote transport are scripted seams."""

    def __init__(self, member):
        self.member = member
        self.real = SubprocessExec()
        self.calls = []
        self.removals = []

    async def run(self, argv, *, cwd, env, timeout, stdin_path=None, on_spawn=None):
        argv = list(argv)
        if argv[0] == "git" and argv[3:4] == ["rebase"] and argv[-1] == "main":
            self.member.admission_heads[cwd.name] = await self.member.git.rev_parse(self.member.root, "main")
        if argv[0] == "claude":
            if stdin_path is None:
                raise AssertionError("soak provider requires a captured triage prompt")
            prompt = stdin_path.read_text()
            if "<<chupa-data:begin message>>" not in prompt:
                raise AssertionError("soak transport accepts only triage, never host work")
            reply = json.dumps(dict(verdict="decision", link=None, summary="Observed synthetic fault",
                rationale="Retain the disposable fixture evidence", evidence=["production fault record"],
                reopen_after_days=1))
            result = (0, json.dumps(dict(type="result", subtype="success", is_error=False,
                                         result=reply, total_cost_usd=0.0)) + "\n", "")
        elif argv[0] == "git" or argv[0] == sys.executable:
            if argv[0] == "git" and argv[3:6] == ["worktree", "remove", "--force"]:
                self.removals.append((Path(argv[6]).name, tuple(self.member.journal.read())))
            if argv[0] == "git" and argv[3:4] == ["push"]:
                result = (0, "disposable checkpoint transport accepted\n", "")
            else:
                result = await self.real.run(argv, cwd=cwd, env=env, timeout=timeout,
                    stdin_path=stdin_path, on_spawn=on_spawn)
        else:
            raise AssertionError(f"unconfigured soak executable: {argv[0]}")
        self.calls.append((argv, cwd, result))
        if argv == self.member.command and cwd.name == "semantic" and result[0] != 0:
            head = await self.member.git.rev_parse(self.member.root, "main")
            main = await self.member.verify(self.member.root)
            self.member.refusals.append((head, main, (cwd / "a.txt").read_bytes(),
                                         (cwd / "b.txt").read_bytes()))
        if argv[0] == "git" and argv[3:5] == ["commit", "-m"] and "\nchupa-ticket: " in argv[5]:
            stem = argv[5].split("\nchupa-ticket: ")[1].splitlines()[0]
            self.member.main_checks.append((stem, await self.member.verify(self.member.root)))
        return result

    def kill_group(self, pgid):
        self.real.kill_group(pgid)


_EXPECTED = (
    ("abandoned_alerted_then_merged", "alert"),
    ("mechanical_and_rework_main_green", "resolved"),
    ("integration_red_main_green", "refused"),
)
_FAULTS = (
    "Interrupt the first Implement worker with unfinished work in its checkout",
    "Append-only mechanical conflict and an undeclared conflict requiring reviewed Rework",
    "Candidate and moved main each set one input; their rebased sum fails Verification",
)
_CHECK = "from pathlib import Path\nassert int(Path('a.txt').read_text()) + int(Path('b.txt').read_text()) <= 1\n"


class _Member:
    """Fixture delivery and observations around the CLI's existing production composition."""

    def __init__(self, root: Path, name: str):
        self.root, self.name = root, name
        self.time = _Time()
        self.fs = _FS(self.time)
        self.journal = Journal(root / ".chupa/state", self.time)
        self.exec = _Exec(self)
        self.env = {"PATH": os.defpath, "HOME": "/nonexistent", "GIT_CONFIG_NOSYSTEM": "1",
                    "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_AUTHOR_NAME": "soak",
                    "GIT_AUTHOR_EMAIL": "soak@example.invalid", "GIT_COMMITTER_NAME": "soak",
                    "GIT_COMMITTER_EMAIL": "soak@example.invalid",
                    "GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z",
                    "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z"}
        self.git = Git(self.exec, env=self.env, timeout=30)
        self.command = [sys.executable, "verify.py"]
        self.owner = self.task = None
        self.lifetimes = []
        self.models = []
        self.changes = {}
        self.moves = {}
        self.hang = False
        self.entered = asyncio.Event()
        self.handoffs = []
        self.inputs = []
        self.cycles = []
        self.sweeps = []
        self.checkpoints = []
        self.interrupted = None
        self.admission_heads = {}
        self.refusals = []
        self.main_checks = []

    async def initialize(self):
        self.root.mkdir(parents=True)
        config = dict(schema_version=1, state_dir=".chupa/state", worktree_root=".chupa/worktrees",
            providers=[dict(name="claude", kind="cli", package="test-cli",
                models_by_tier=dict.fromkeys(("low", "medium", "high", "max"), "script"),
                limits=dict(concurrency=1, est_cost_per_call_usd=0.0))],
            routing=[dict(tier="medium", surface=s, candidates=[dict(provider="claude")])
                     for s in ("implement", "review")],
            review=dict(mechanical=[
                dict(code="structure", argv=[sys.executable, "verify-safety.py"], trigger="always", severity="hard"),
                dict(code="inputs", argv=self.command, trigger="always", severity="hard")]),
            merge=dict(safety_checks=["structure"], strategies=[dict(paths=["union.txt"], strategy="union")]),
            engine_plane_safety_inventory=["config.yaml"], drain=dict(max_runtime_hours=48))
        files = {"config.yaml": yaml.safe_dump(config), ".gitignore": ".chupa/\n",
                 "CHUPA_PLAN.md": "# Disposable soak plan\n", "verify.py": _CHECK,
                 "verify-safety.py": "from pathlib import Path\nassert all(int(Path(p).read_text()) in (0, 1) for p in ('a.txt', 'b.txt'))\n",
                 "a.txt": "0\n", "b.txt": "0\n", "union.txt": "base\n", "conflict.txt": "base\n"}
        for path, data in files.items():
            self.fs.write(self.root / path, data.encode())
        await self.git.init(self.root, branch="main")
        await self.git.add(self.root, list(files))
        await self.git.commit(self.root, "synthetic soak baseline")
        config = load_config(None, cwd=self.root)
        self.checkout = runner.Checkout(self.root, config, self.env, self.exec, self.git,
                                       self.journal, self.fs, self.time, self.time.sleep)

    def ticket(self, stem, paths, *, corrected=False):
        return ("---\nstate: confirmed\nsource: human\npriority: P2\nkind: feature\n---\n\n"
            "## Depends on\nnone\n\n## Context\n- verify.py\n\n## Goal / Why\n"
            + ("Resolve against current main.\n" if corrected else "Exercise synthetic production work.\n")
            + "\n## Scope in / Scope out\nIn: declared fixture paths. Out: live host work.\n\n"
            "## Scope fence\n" + "".join(f"- {p}\n" for p in paths)
            + f"\n## Acceptance criteria\n1. `{sys.executable} verify.py` exits 0.\n\n## Verification\n```\n"
            + f"{sys.executable} verify.py\n```\n\n## Definition of rejected\nNeeds live work.\n\n"
            "## Time budget\n- expected: 1m\n- stuck: 20m\n")

    def publish(self, stem, changes):
        self.changes[stem] = changes
        self.fs.write(self.root / f"tickets/{stem}/ticket.md", self.ticket(stem, changes).encode())

    async def verify(self, path):
        return await self.exec.run(self.command, cwd=path, env=self.env, timeout=30)

    async def prepare(self, local):
        member = self

        class Model(FakeLLM):
            async def call(self, req):
                stem = req.ticket
                if req.surface == "implement":
                    if member.hang:
                        member.fs.write(req.worktree / "unfinished.txt", b"interrupted fixture work\n")
                        member.entered.set()
                        self.script.append(HANG)
                    else:
                        changes = member.changes[stem]
                        for path, data in changes.items():
                            member.fs.write(req.worktree / path, data.encode())
                        await member.git.add(req.worktree, list(changes))
                        await member.git.commit(req.worktree, "scripted fixture implementation")
                        self.script.append(json.dumps(dict(outcome="ok", summary="Implemented fixture",
                            surprises="none", second_problems=[], dead_ends="none",
                            predicted_vs_actual="bounded fixture", findings=[])))
                elif req.surface == "review":
                    if stem in member.moves:
                        candidate = local.config.worktree_root / stem
                        before = await member.verify(candidate)
                        for path, data in member.moves.pop(stem).items():
                            member.fs.write(member.root / path, data.encode())
                            await member.git.add(member.root, [path])
                        await member.git.commit(member.root, "plant moved-main fault")
                        main = await member.verify(member.root)
                        member.inputs.append((stem, before, main, await member.git.rev_parse(member.root, "main")))
                    self.script.append(json.dumps(dict(verdict="approve", summary="Scripted fresh review", findings=[])))
                elif req.surface == "rework":
                    raw = req.rendered.split("<<chupa-data:begin conflict>>\n", 1)[1].split(
                        "\n<<chupa-data:end conflict>>", 1)[0]
                    handoff = ConflictHandoff.model_validate_json(raw)
                    queue = member.owner.queue
                    member.handoffs.append((handoff, queue.active, queue._slot.locked()))
                    member.changes[stem] = {"conflict.txt": "base\nmain\ncorrected\n"}
                    self.script.append(json.dumps(dict(action="update", tickets=[dict(stem=stem,
                        ticket=member.ticket(stem, ["conflict.txt"], corrected=True))])))
                elif req.surface == "requisition_review":
                    self.script.append(json.dumps(dict(verdict="approve", summary="Buildable fixture", findings=[])))
                elif req.surface == "diagnose":
                    self.script.append(json.dumps(dict(verdict="abandon-human", lessons=["Inspect fixture refusal"])))
                else:
                    raise AssertionError(f"unexpected soak surface {req.surface}")
                return await super().call(req)

        model = Model([])
        self.models.append(model)
        return runner.bind(local, model)

    async def until(self, predicate):
        for n in range(100000):
            if predicate():
                return
            if self.task is not None and self.task.done():
                raise SoakRefused(self.name, f"serve stopped early ({self.task.result()})")
            if n % 20 == 0:
                self.time.advance(serve.SERVE_POLL_S)
            await _turn()
        raise SoakRefused(self.name, "production graph did not reach its scripted boundary")

    async def start(self):
        def signals(stop):
            self.owner = stop.__self__
            self.lifetimes.append(self.owner)
            restart = self.owner.core.restart
            reconcile = restart._reconcile
            async def reconciled():
                result = await reconcile()
                self.sweeps.append((self.time(), tuple(result)))
                return result
            restart._reconcile = reconciled
            return lambda: None
        self.task = asyncio.create_task(serve.serve(self.checkout, plan="# Disposable soak plan\n",
                                                  prepare=self.prepare, signals=signals))
        await self.until(lambda: self.owner is not None and self.owner.ready.is_set())
        checkpoint = self.owner.checkpoint
        poll = checkpoint.poll
        async def polled():
            result = await poll()
            self.checkpoints.append(self.time())
            return result
        checkpoint.poll = polled

    async def stop(self):
        if self.task is None:
            return
        if self.owner is not None:
            self.owner.stop()
        else:
            self.task.cancel()
        cleanup = asyncio.gather(self.task, return_exceptions=True)
        await _cleanup(cleanup)
        result = cleanup.result()[0]
        self.task = None
        if isinstance(result, BaseException) and not isinstance(result, asyncio.CancelledError):
            raise result
        if result not in (0, None) and not isinstance(result, asyncio.CancelledError):
            raise SoakRefused(self.name, f"serve cleanup exited {result}")

    def terminals(self, stem):
        return [e for e in self.journal.read() if e.ticket == stem
                and e.type == EventType.STATE_TRANSITION and e.body.get("to") in TERMINAL_STATES]

    async def settled(self, stem, count=1):
        await self.until(lambda: len(self.terminals(stem)) >= count and
                         self.owner.core.admission.active is None and self.owner.mutating is None)

    async def file_fault(self, stem, sequence, suffix, outcome, summary):
        async with self.owner.mutations():
            self.owner.box.enqueue(message_class="failure_report", origin=stem, stage="merge",
                outcome=outcome, summary=summary, occurrence_id=f"{stem}/{sequence}/{suffix}")
        await self.until(lambda: not self.owner.box.pending() and self.owner.mutating is None)

    def facts(self, stem):
        return [e for e in self.journal.read() if e.ticket == stem and e.body.get("kind") == CONFLICT_FACTS]

    def harvest(self, stem, sequence):
        return Harvest.model_validate_json((self.root / f"tickets/{stem}/attempts/{sequence}/harvest.json").read_bytes())

    async def exercise(self):
        await self.start()
        if self.name == DAEMON_SOAK_MEMBERS[0]:
            self.hang = True
            self.publish("worker", {"worker.txt": "completed\n"})
            await self.until(self.entered.is_set)
            self.interrupted = (tuple(self.journal.read()),
                (self.checkout.config.worktree_root / "worker/unfinished.txt").read_bytes())
            await self.stop()
            self.journal.close()
            self.journal = Journal(self.checkout.config.state_dir, self.time)
            from dataclasses import replace
            self.checkout = replace(self.checkout, journal=self.journal)
            self.hang = False
            self.owner = None
            await self.start()
            await self.settled("worker", 2)
        elif self.name == DAEMON_SOAK_MEMBERS[1]:
            self.moves["mechanical"] = {"union.txt": "base\nmain\n"}
            self.publish("mechanical", {"union.txt": "base\nbranch\n"})
            await self.settled("mechanical")
            await self.file_fault("mechanical", 0, "mechanical-conflict", "ok",
                                  json.dumps(self.facts("mechanical")[-1].body, sort_keys=True))
            self.moves["unresolved"] = {"conflict.txt": "base\nmain\n"}
            self.publish("unresolved", {"conflict.txt": "base\nbranch\n"})
            await self.settled("unresolved", 2)
            harvest = self.harvest("unresolved", 0)
            summary = json.dumps(self.facts("unresolved")[0].body, sort_keys=True) + "; " + "; ".join(
                f.message for f in harvest.findings) + "; " + harvest.terminal + "; " + self.handoffs[0][0].model_dump_json()
            await self.file_fault("unresolved", 0, "unresolved-conflict", "gate_failed", summary)
        else:
            self.moves["semantic"] = {"b.txt": "1\n"}
            self.publish("semantic", {"a.txt": "1\n"})
            await self.settled("semantic")
            harvest = self.harvest("semantic", 0)
            spool = self.checkout.config.state_dir / "spools/semantic/0/merge-integration/verify-01.txt"
            await self.file_fault("semantic", 0, "semantic-integration-red", "gate_failed",
                                  spool.read_text() + "; " + harvest.terminal + "; " +
                                  "; ".join(f.message for f in harvest.findings))
        await self.recurring()

    async def recurring(self):
        # Each jump is followed by round trips and actual idle maintenance, before the next jump.
        for _ in range(5):
            self.time.advance(6 * 3600)
            owner = self.owner
            previous = tuple(r.answered for r in owner.responses)
            beats = len(self.fs.heartbeats)
            sweeps, checkpoints = len(self.sweeps), len(self.checkpoints)
            await self.until(lambda: all(r.answered > old and r.responsive()
                for r, old in zip(owner.responses, previous)) and len(self.fs.heartbeats) > beats
                and len(self.sweeps) > sweeps and len(self.checkpoints) > checkpoints
                and owner.mutating is None and not owner.core.admission._slot.locked())
            self.cycles.append((self.time(), tuple(r.responsive() for r in owner.responses)))
        await self.until(lambda: any(e.type == EventType.EFFECT_COMPLETION and
                                    e.key == "checkpoint-push/0" for e in self.journal.read()))


async def _cleanup(cleanup):
    from chupa.daemon import _protected_cleanup
    await _protected_cleanup(cleanup)


def _require(member, condition, detail):
    if not condition:
        raise SoakRefused(member.name, detail)


async def _observe(member: _Member) -> DaemonSoakEntry:
    """Re-read this member's records after all owned lifetimes have finished."""
    m = member
    need = lambda condition, detail: _require(m, condition, detail)
    events = m.journal.read()
    need(m.task is None and all(o.tasks.tasks == () and all(t.done() for t in o.workers)
        and o.core.admission.task is None and not o.core.watcher._waits for o in m.lifetimes),
        "owned lifetime cleanup is incomplete")
    need(json.loads((m.checkout.config.state_dir / "control/active.json").read_text()) is None,
         "control lifetime was not retired")
    need(not m.time.waits, "injected sleepers survived cleanup")
    need(sum(m.time.steps) >= 86400 and len(m.cycles) == 5 and
         all(all(health) for _, health in m.cycles) and len(m.time.sleeps) > 5 and
         all(b - a >= timedelta(hours=6) for (a, _), (b, _) in zip(m.cycles, m.cycles[1:])),
         "missing recurring consumer round trips across 24 hours")
    need(len(m.fs.heartbeats) >= 5 and m.fs.heartbeats[-1] - m.fs.heartbeats[0] >= timedelta(hours=24),
         "heartbeat did not recur across the soak")
    need(len(list(m.journal.read_segments())) >= 2, "journal age rotation missing")
    need(len(m.sweeps) >= 5 and m.sweeps[-1][0] - m.sweeps[0][0] >= timedelta(hours=24),
         "idle orphan sweeping did not recur")
    need(len(m.checkpoints) >= 5 and m.checkpoints[-1] - m.checkpoints[0] >= timedelta(hours=24),
         "checkpoint polling did not recur")
    need(any(e.type == EventType.TIMER_FIRED for e in events), "timer firing missing")
    need(any(e.type == EventType.EFFECT_COMPLETION and e.key == "checkpoint-push/0" for e in events)
         and any(argv[3:4] == ["push"] for argv, _, _ in m.exec.calls), "checkpoint polling missing")
    need(any(e.body.get("signal") == "triage_pass" for e in events) if m.name != DAEMON_SOAK_MEMBERS[0]
         else any(e.body.get("kind") == RECOVERY_ALERT for e in events), "Box/alert consumer evidence missing")
    need((await m.verify(m.root))[0] == 0, "main Verification is red")
    index = DAEMON_SOAK_MEMBERS.index(m.name)
    expected, disposition = _EXPECTED[index]

    def terms(stem):
        return [e for e in events if e.ticket == stem and e.type == EventType.STATE_TRANSITION
                and e.body.get("to") in TERMINAL_STATES]

    def merged(stem, sequence):
        terminal = terms(stem)[sequence]
        need(terminal.body.get("to") == "merged" and terminal.body.get("commit")
             and terminal.body.get("reviewed_sha"), f"{stem}/{sequence} did not merge with pinned approval")
        need(any(e.type == EventType.EFFECT_COMPLETION and e.key == f"merge/{stem}/{sequence}"
                 and e.body.get("result", {}).get("commit") == terminal.body["commit"] for e in events),
             f"{stem}/{sequence} lacks admission completion")
        review = read_review((m.root / f"tickets/{stem}/review.md").read_text())
        need(review.verdict == "approve" and review.reviewed_sha == terminal.body["reviewed_sha"],
             f"{stem}/{sequence} fresh review approval missing")
        need(any(s == stem and result[0] == 0 for s, result in m.main_checks),
             f"{stem} main Verification after merge missing")
        return terminal

    def filing(stem, sequence, suffix, outcome):
        messages = m.owner.box.messages()
        matched = [msg for msg in messages if msg.message_class == "failure_report" and
                   msg.origin == stem and msg.stage == "merge" and msg.outcome == outcome]
        need(len(matched) == 1 and matched[0].summary.strip(), f"{stem} fault Box report missing or contradictory")
        need(any(e.body.get("kind") == "storm_occurrence" and
                 e.body.get("occurrence_id") == f"{stem}/{sequence}/{suffix}" and
                 e.body.get("signature") == matched[0].signature for e in events),
             f"{stem} Box report lacks original fault-run identity")

    def successful_check(stem, sequence):
        key = f"ticket-plane/{stem}/{sequence}/checks"
        rows = [e for e in events if e.type == EventType.EFFECT_COMPLETION and e.key == key]
        need(len(rows) == 1, f"{stem}/{sequence} checks custody missing")
        return rows[0].body["result"]

    runs = ((("worker", 1),), (("mechanical", 0), ("unresolved", 0), ("unresolved", 1)),
            (("semantic", 0),))[index]
    reviews = {}
    for stem, sequence in runs:
        custody = successful_check(stem, sequence)
        invoice = Invoice.model_validate_json(await m.git._run(m.root, "show",
            f"{custody['commit']}:tickets/{stem}/checks.json"))
        need(invoice.stem == stem and invoice.passed and invoice.verification and
             all(v.argv == m.command and v.rc == 0 and not v.base_red for v in invoice.verification),
             f"{stem}/{sequence} committed Check is not independently green")
        rows = [e for e in events if e.type == EventType.EFFECT_COMPLETION and
                e.key == f"ticket-plane/{stem}/{sequence}/review"]
        need(len(rows) == 1, f"{stem}/{sequence} review custody missing")
        review = read_review(await m.git._run(m.root, "show",
            f"{rows[0].body['result']['commit']}:tickets/{stem}/review.md"))
        need(review.stem == stem and review.verdict == "approve" and
             review.reviewed_sha == invoice.produced_at_sha, f"{stem}/{sequence} approval does not pin checked candidate")
        reviews[stem, sequence] = review

    if index == 0:
        need([e.body["to"] for e in terms("worker")] == ["abandoned", "merged"], "worker recovery sequence missing")
        alerts = [e for e in events if e.ticket == "worker" and e.body.get("kind") == RECOVERY_ALERT]
        need(len(alerts) == 1 and alerts[0].body.get("disposition") == "alert" and
             alerts[0].body.get("outcome") == "abandoned" and alerts[0].body.get("run_seq") == 0,
             "worker original-run recovery alert missing")
        need(events.index(terms("worker")[0]) < events.index(alerts[0]) < events.index(terms("worker")[1]),
             "worker recovery alert ordering wrong")
        removed = [history for stem, history in m.exec.removals if stem == "worker"]
        need(removed and alerts[0] in removed[0] and removed[0][-1] == alerts[0], "alert did not precede worktree removal")
        need(m.entered.is_set() and any(model.aborted for model in m.models) and
             any(req.surface == "implement" for model in m.models for req in model.requests),
             "no interrupted running worker")
        need(m.interrupted is not None and m.interrupted[1] and
             any(e.ticket == "worker" and e.body.get("to") == "running" for e in m.interrupted[0]) and
             not any(e.ticket == "worker" and e.body.get("to") in TERMINAL_STATES for e in m.interrupted[0]) and
             any(e.type == EventType.EFFECT_INTENT and e.ticket == "worker" for e in m.interrupted[0]),
             "interrupted worker lacked a started unfinished run")
        need(m.harvest("worker", 0).terminal == "abandoned", "abandoned run harvest missing")
        merged("worker", 1)
        producing = f"worker/{alerts[0].body['run_seq']}"
    elif index == 1:
        need([e.body["to"] for e in terms("mechanical")] == ["merged"] and
             [e.body["to"] for e in terms("unresolved")] == ["gate_failed", "merged"], "conflict terminal sequences missing")
        need(terms("unresolved")[0].body.get("stage") == "merge", "unresolved conflict terminal belongs to another stage")
        for stem, path, rung, hits in (("mechanical", "union.txt", "mechanical", ["union.txt"]),
                                      ("unresolved", "conflict.txt", "rework", [])):
            facts = m.facts(stem)
            need(len(facts) == (1 if stem == "mechanical" else 2) and facts[0].body == dict(kind=CONFLICT_FACTS, conflicted_paths=[path],
                resolving_rung=rung, strategy_paths=hits, integration_red_paths=[]), f"{stem} conflict rung/path evidence wrong")
            need(events.index(facts[0]) < events.index(terms(stem)[0]), f"{stem} conflict facts follow terminal")
        need(m.facts("unresolved")[1].body == dict(kind=CONFLICT_FACTS, conflicted_paths=[],
            resolving_rung="none", strategy_paths=[], integration_red_paths=[]), "corrected candidate did not re-enter ordinary admission")
        need(len(m.handoffs) == 1, "typed Rework handoff missing")
        handoff, active, locked = m.handoffs[0]
        need(handoff.stem == "unresolved" and handoff.conflicted_paths == ["conflict.txt"] and
             handoff.approval_invalidated and active is None and not locked and handoff.findings,
             "Rework ran before admission unwind or reused approval")
        harvest = m.harvest("unresolved", 0)
        need(harvest.terminal == "gate_failed" and harvest.stage == "merge" and
             harvest.findings == handoff.findings, "unresolved production harvest missing")
        need(any(e.ticket == "unresolved" and e.body.get("signal") == "rework_order" and
                 e.body.get("action") == "update" for e in events), "reviewed Rework update missing")
        first, fresh = handoff.reviewed_sha, merged("unresolved", 1).body["reviewed_sha"]
        need(first == reviews["unresolved", 0].reviewed_sha and first != fresh and
             fresh == reviews["unresolved", 1].reviewed_sha, "corrected candidate reused approval")
        merged("mechanical", 0)
        for stem, seq in (("mechanical", 0), ("unresolved", 1)):
            spool = m.checkout.config.state_dir / f"spools/{stem}/{seq}"
            need(all((spool / p).is_file() and "[exit 0]" in (spool / p).read_text()
                for p in ("check/verify-01.txt", "merge-safety/host-01.txt",
                          "merge-integration/verify-01.txt", "merge-integration/host-01.txt")),
                f"{stem} fresh Check/mechanical regating missing")
        filing("mechanical", 0, "mechanical-conflict", "ok")
        filing("unresolved", 0, "unresolved-conflict", "gate_failed")
        need((m.root / "union.txt").read_text() == "base\nmain\nbranch\n" and
             (m.root / "conflict.txt").read_text() == "base\nmain\ncorrected\n", "conflict resolutions missing from main")
        producing = "unresolved/1"
    else:
        need([e.body["to"] for e in terms("semantic")] == ["gate_failed"] and
             terms("semantic")[0].body.get("stage") == "merge", "semantic refusal terminal missing")
        facts = m.facts("semantic")
        need(len(facts) == 1 and facts[0].body == dict(kind=CONFLICT_FACTS, conflicted_paths=[],
            resolving_rung="none", strategy_paths=[], integration_red_paths=["a.txt"]) and
            events.index(facts[0]) < events.index(terms("semantic")[0]), "semantic queue-owned integration facts missing")
        need(len(m.inputs) == 1 and m.inputs[0][0] == "semantic" and
             m.inputs[0][1][0] == m.inputs[0][2][0] == 0, "inputs were not independently green")
        need(m.refusals and all(head == m.admission_heads.get("semantic") and result[0] == 0
             and a == b == b"1\n" for head, result, a, b in m.refusals),
             "semantic refusal did not preserve unchanged green main and the red candidate")
        # Ticket-plane harvest/triage commits may move HEAD; compare the actual input tree at refusal.
        need((m.root / "a.txt").read_text() == "0\n" and (m.root / "b.txt").read_text() == "1\n",
             "semantic candidate changed main")
        need(await m.git._run(m.root, "show", "semantic:a.txt") == "1\n" and
             await m.git._run(m.root, "show", "semantic:b.txt") == "1\n", "refused candidate evidence not retained")
        spool = m.checkout.config.state_dir / "spools/semantic/0/merge-integration/verify-01.txt"
        need(spool.is_file() and "[exit 1]" in spool.read_text() and "AssertionError" in spool.read_text(),
             "real integration Verification red spool missing")
        harvest = m.harvest("semantic", 0)
        need(harvest.stage == "merge" and harvest.terminal == "gate_failed" and
             any(f.code == "verification" for f in harvest.findings), "semantic production harvest missing")
        need(not any(e.key == "merge/semantic/0" for e in events), "refused candidate reached merge")
        filing("semantic", 0, "semantic-integration-red", "gate_failed")
        producing = "semantic/0"
    violations = audit_journal(m.journal)
    lines = [f"{v.invariant}: {v.ticket or '-'}: {v.detail}" for v in violations]
    need(not lines, "auditor violations: " + "; ".join(lines))
    return DaemonSoakEntry(member=m.name, planted_fault=_FAULTS[index], expected=expected,
        observed=expected, disposition=disposition, producing_run=producing, auditor=lines, green=True)


async def _run_member(root: Path, name: str) -> DaemonSoakEntry:
    member = _Member(root / name, name)
    try:
        return await _member_lifetime(member)
    except Exception as exc:
        if isinstance(exc, SoakRefused):
            raise
        raise SoakRefused(name, str(exc)) from exc
    finally:
        member.journal.close()


async def _member_lifetime(member: _Member) -> DaemonSoakEntry:
    try:
        await member.initialize()
        await member.exercise()
    finally:
        try:
            await member.stop()
        finally:
            # Synthetic registered worktrees are removed through Git, even on failed/cancelled runs.
            if hasattr(member, "checkout"):
                trees = await member.git._run(member.root, "worktree", "list", "--porcelain")
                for line in trees.splitlines():
                    if line.startswith("worktree "):
                        path = Path(line.removeprefix("worktree "))
                        if path != member.root:
                            await _cleanup(asyncio.create_task(member.git.worktree_remove(member.root, path)))
    return await _observe(member)


async def produce(root: Path) -> DaemonSoakReport:
    git = Git(SubprocessExec(), env=os.environ, timeout=30)
    sha = await git.rev_parse(Path.cwd(), "HEAD")
    entries = [await _run_member(root, name) for name in DAEMON_SOAK_MEMBERS]
    return DaemonSoakReport(produced_by_spec_version=DAEMON_SOAK_SPEC_VERSION,
                          produced_at_sha=sha, entries=entries)


async def _main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m eval.daemon_soak")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        with tempfile.TemporaryDirectory(prefix="chupa-daemon-soak-") as directory:
            report = await produce(Path(directory))
        write_report(args.out, report, LocalFileSystem())
    except (SoakRefused, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


def main(argv=None) -> int:
    return asyncio.run(_main(argv))


if __name__ == "__main__":
    raise SystemExit(main())
