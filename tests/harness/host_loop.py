"""Supervised disposable host evidence."""

import asyncio
import json
import sys
from datetime import timedelta
from pathlib import Path
from typing import Literal

from pydantic import field_validator, model_validator

from chupa.artifacts import NonBlank, _check_integer_version, _check_producing_run, _Strict
from chupa.audit import audit_journal
from chupa.box import Box
from chupa.config import load_config
from chupa.control import AdmissionRequest, ControlRequest, decisions, publish_request, read_active
from chupa.git import Git
from chupa.journal import TERMINAL_STATES, EventType, Journal
from chupa.stages import Invoice, read_review
from hosts.fixture import scaffold
from tests.integration.test_git import commit_lock

ROOT = Path(__file__).resolve().parents[2]
ROAD = "repair the producing machinery and rerun the harness through Check"


HOST_LOOP_MEMBERS = ("machine_ticket_merge", "report_to_regression_bug_loop", "escape_attribution")
HOST_LOOP_EXPECTED = dict(zip(HOST_LOOP_MEMBERS, ("machine_ticket_merged", "report_replayed_regression_bug_merged", "escape_attributed_by_squash_trailers")))


class HostLoopEntry(_Strict):
    member: Literal["machine_ticket_merge", "report_to_regression_bug_loop", "escape_attribution"]
    producing_run: NonBlank
    expected: NonBlank
    observed: NonBlank
    engine_plane_edits: list[NonBlank]
    auditor: list[NonBlank]
    green: bool

    @model_validator(mode="after")
    def _consistent(self):
        _check_producing_run(self.producing_run)
        if self.expected != HOST_LOOP_EXPECTED[self.member]:
            raise ValueError("use the member's fixed expected observation")
        if self.green != (self.observed == self.expected and not self.engine_plane_edits and not self.auditor):
            raise ValueError("green requires matching observation, no engine edits and no auditor findings")
        return self


class HostLoopReport(_Strict):
    schema_version: Literal[1]
    entries: list[HostLoopEntry]

    @field_validator("schema_version", mode="before")
    @classmethod
    def _integer_version(cls, value):
        return _check_integer_version(value, "schema_version must be integer 1")

    @model_validator(mode="after")
    def _ordered(self):
        merges = self.entries[:-2]
        if (
            len(merges) < 3
            or any(e.member != HOST_LOOP_MEMBERS[0] for e in merges)
            or tuple(e.member for e in self.entries[-2:]) != HOST_LOOP_MEMBERS[1:]
            or len({e.producing_run for e in merges}) != len(merges)
        ):
            raise ValueError("use three distinct merge runs followed by regression and escape members")
        return self


class LoopRefused(ValueError):
    def __init__(self, member, detail):
        read = HOST_LOOP_MEMBERS[1] if member == "regression" else HOST_LOOP_MEMBERS[2] if member == "escape" else HOST_LOOP_MEMBERS[0] if member.startswith("merge-") else member
        super().__init__(f"{read} ({member}): {detail}; {ROAD}")


class FixtureLoop:
    def __init__(self, root, name, *, exec_, fs, clock, sleep, notifications, timeout=60):
        self.root, self.name = root, name
        self.exec, self.fs, self.clock, self.sleep = exec_, fs, clock, sleep
        self.notifications, self.timeout = notifications, timeout
        self.task, self.pgid = None, None
        self.requests = set()
        self.env = {
            "PATH": str(root / "bin") + ":" + str(Path(sys.executable).parent) + ":/usr/bin:/bin",
            "PYTHONPATH": str(ROOT),
            "PYTHONDONTWRITEBYTECODE": "1",
            "CHUPA_FIXTURE_ROOT": str(root),
            "CHUPA_FIXTURE_SCENARIO": name,
            "GIT_AUTHOR_NAME": "Fixture",
            "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
            "GIT_COMMITTER_NAME": "Fixture",
            "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
            "GIT_CONFIG_NOSYSTEM": "1",
        }
        self.git = Git(exec_, env=self.env, timeout=10, commit_lock=commit_lock(root / ".chupa/state"))
        self.journal = Journal(root / ".chupa/state", clock)

    async def initialize(self):
        scaffold.copy_host(self.root)
        self.fs.write(self.root / ".gitignore", b".chupa/\n.fixture-runtime/\ninbox/\n__pycache__/\n")
        # Committed report fixtures remain inputs; runtime intake uses an empty disposable inbox.
        cfg = self.root / "config.yaml"
        self.fs.write(cfg, cfg.read_bytes().replace(b"report_inbox: reports", b"report_inbox: inbox"))
        await self.git.init(self.root, branch="main")
        await self.git.add(self.root, [p.relative_to(self.root).as_posix() for p in self.root.rglob("*") if p.is_file() and not {".git", ".fixture-runtime"}.intersection(p.parts)])
        await self.git.commit(self.root, "fixture defective base")
        self.base = await self.git.rev_parse(self.root, "HEAD")
        cfg = load_config(None, cwd=self.root)
        self.inventory = cfg.engine_plane_safety_inventory

    async def start(self):
        self.task = asyncio.create_task(
            self.exec.run([sys.executable, "-m", "chupa", "serve"], cwd=self.root, env=self.env, timeout=self.timeout + 10, on_spawn=lambda pgid: setattr(self, "pgid", pgid))
        )
        await self.until(lambda: (self.root / ".chupa/state/control/active.json").exists() and json.loads((self.root / ".chupa/state/control/active.json").read_bytes()) is not None)

    def confirm(self):
        state = self.root / ".chupa/state"
        lifecycle, _ = read_active(state, Path.read_bytes)
        candidates = []
        for path in (self.root / "tickets").glob("*/ticket.md"):
            if "state: draft" in path.read_text():
                candidates.append((path.parent.name, None))
        for stem, hold in candidates:
            identity = (stem, hold)
            if identity in self.requests:
                continue
            self.requests.add(identity)
            publish_request(state, AdmissionRequest(f"fixture-{len(self.requests)}", lifecycle, "confirm", stem, hold, "machine"), self.fs)

    async def until(self, predicate, *, confirm=False):
        deadline = self.clock() + timedelta(seconds=self.timeout)
        while not predicate():
            if self.task is not None and self.task.done():
                try:
                    result = self.task.result()
                except Exception as exc:
                    raise LoopRefused(self.name, f"serve failed: {exc}") from exc
                raise LoopRefused(self.name, f"serve exited before member evidence: {result}")
            if self.clock() >= deadline:
                raise LoopRefused(self.name, "bounded wait timed out before required production evidence")
            if confirm:
                self.confirm()
            await self.sleep(0.05)

    def terminal(self, stem):
        return [e for e in self.journal.read() if e.ticket == stem and e.type == EventType.STATE_TRANSITION and e.body.get("to") in TERMINAL_STATES]

    async def merged(self, stem):
        await self.until(lambda: bool(self.terminal(stem)), confirm=True)
        if [e.body["to"] for e in self.terminal(stem)] != ["merged"]:
            raise LoopRefused(self.name, f"{stem} did not merge: {self.terminal(stem)}")
        return self.terminal(stem)[0]

    def suggestion(self):
        Box(self.root / ".chupa/state/box", self.fs).enqueue(
            message_class="suggestion", origin="fixture", summary=scaffold.scenario(self.root, self.name)["responses"]["implement"][0]["summary"], occurrence_id=f"fixture/{self.name}"
        )

    async def report(self, name, *, app_commit=None):
        raw = json.loads((self.root / f"reports/{name}.json").read_bytes())
        if app_commit is not None:
            raw["app_commit"] = app_commit
        self.fs.write(self.root / "inbox/report.json", (json.dumps(raw) + "\n").encode())

    async def replay(self, path):
        rc, out, _ = await self.exec.run([sys.executable, "replay.py", path], cwd=self.root, env=self.env, timeout=10)
        return rc, json.loads(out)

    async def triage_pending(self):
        await self.until(lambda: bool(Box(self.root / ".chupa/state/box", self.fs).pending()))
        await self.stop()
        code, out, err = await self.exec.run([sys.executable, "-m", "chupa", "triage"], cwd=self.root, env=self.env, timeout=self.timeout + 10)
        if code != 0:
            raise LoopRefused(self.name, f"triage exited {code}: {out} {err}")
        self.journal = Journal(self.root / ".chupa/state", self.clock)
        await self.start()

    async def exercise(self):
        await self.start()
        if self.name == "regression":
            await self.report("regression")
            await self.triage_pending()
            await self.until(lambda: (self.root / "tickets/regression/evidence/replay.json").exists())
            self.before_replay = await self.replay("tickets/regression/evidence/replay.json")
            await self.merged("regression")
            self.after_replay = await self.replay("tickets/regression/evidence/replay.json")
        else:
            self.suggestion()
            await self.triage_pending()
            terminal = await self.merged(self.name)
            if self.name == "escape":
                self.escape_replay = await self.replay("evidence/escape.json")
                # The report resolves to a fresh real bug; its attribution reads escape's squash.
                self.fs.write(self.root / ".fixture-runtime/selection", b"regression")
                await self.report("escape", app_commit=terminal.body["commit"])
                await self.triage_pending()
                await self.until(
                    lambda: any((e.key or "").startswith("escape-attribution/") and e.type == EventType.EFFECT_COMPLETION and e.body.get("result", {}).get("matches") for e in self.journal.read())
                )

    async def stop(self):
        if self.task is None:
            return
        try:
            if not self.task.done():
                state = self.root / ".chupa/state"
                try:
                    lifecycle, _ = read_active(state, Path.read_bytes)
                    publish_request(state, ControlRequest(f"fixture-stop-{lifecycle}", lifecycle, "kill", None), self.fs)
                    await asyncio.wait_for(asyncio.shield(self.task), 5)
                except ValueError, TimeoutError:
                    self.task.cancel()
        finally:
            if self.pgid is not None:
                self.exec.kill_group(self.pgid)
            if not self.task.done():
                self.task.cancel()
            result = await asyncio.gather(self.task, return_exceptions=True)
            self.journal.close()
        if isinstance(result[0], tuple) and result[0][0] != 0:
            raise LoopRefused(self.name, f"serve cleanup exited {result[0]}")

    def need(self, condition, detail):
        if not condition:
            raise LoopRefused(self.name, detail)

    async def observe(self):
        events = self.journal.read()
        findings = [f"{v.invariant}: {v.ticket}: {v.detail}" for v in audit_journal(self.journal)]
        self.need(not findings, "member auditor findings: " + "; ".join(findings))
        stem = self.name
        (terminal,) = self.terminal(stem)
        self.need(terminal.body.get("commit") and terminal.body.get("reviewed_sha"), "merged identity missing")

        def completion(key):
            rows = [e.body["result"] for e in events if e.type == EventType.EFFECT_COMPLETION and e.key == key]
            self.need(len(rows) == 1, f"missing unique production evidence {key}")
            return rows[0]

        admission = completion(f"merge/{stem}/0")
        self.need(admission["commit"] == terminal.body["commit"], "merge completion disagrees with terminal")
        checks = completion(f"ticket-plane/{stem}/0/checks")
        invoice = Invoice.model_validate_json(await self.git._run(self.root, "show", f"{checks['commit']}:tickets/{stem}/checks.json"))
        self.need(invoice.passed and invoice.verification and all(v.rc == 0 for v in invoice.verification), "committed Check is not green")
        review_lift = completion(f"ticket-plane/{stem}/0/review")
        review = read_review(await self.git._run(self.root, "show", f"{review_lift['commit']}:tickets/{stem}/review.md"))
        self.need(review.verdict == "approve" and review.reviewed_sha == terminal.body["reviewed_sha"] == invoice.produced_at_sha, "checked/reviewed identity mismatch")
        rows = await self.git.first_parent_squashes(self.root, terminal.body["commit"])
        self.need(len(rows) == 1 and rows[0]["ticket"] == stem and rows[0]["reviewed_sha"] == review.reviewed_sha, "squash trailer evidence missing")
        edits = [p for p in rows[0]["paths"] if any(p == f.rstrip("/") or p.startswith(f.rstrip("/") + "/") for f in self.inventory)]
        self.need(not edits, "engine-plane edits: " + ", ".join(edits))
        accepted = [e.body for e in decisions(events) if e.body["decision"] == "accepted" and e.body.get("stem") == stem and e.body.get("verb") == "confirm"]
        self.need(
            any(b["hold_id"] is None and b["actor"] == "machine" for b in accepted),
            "machine draft confirmation missing",
        )
        self.need(not any(e.body.get("signal") in ("review_baseline", "reject_verdict") for e in events), "fixture recorded GO or re-armed caps")
        member = HOST_LOOP_MEMBERS[0]
        if stem == "regression":
            member = HOST_LOOP_MEMBERS[1]
            self.need(self.before_replay[0] == 1 and self.before_replay[1]["defect"] and self.after_replay[0] == 0 and not self.after_replay[1]["defect"], "replay repair missing")
            (bug,) = [r for r in invoice.reports if r.code == "bug_evidence"]
            self.need(
                bug.verdict == "pass"
                and bug.bug_evidence.head.regression_result == "pass"
                and bug.bug_evidence.base.regression_result == "defect"
                and bug.bug_evidence.overlay_paths == ["fixtures/replay.json", "fixtures/report_regression.py"]
                and bug.bug_evidence.evidence_paths,
                "real regression-gate evidence missing",
            )
            authored = completion("ticket-plane/regression/author")
            carried = await self.git._run(self.root, "show", f"{invoice.produced_at_sha}:fixtures/replay.json")
            custody = await self.git._run(self.root, "show", f"{authored}:tickets/regression/evidence/replay.json")
            self.need(carried == custody, "carried replay differs from authored durable evidence")
            self.need(await self.git._run(self.root, "show", f"{bug.bug_evidence.base_sha}:regression_test.py"), "test absent on defective base")
        elif stem == "escape":
            member = HOST_LOOP_MEMBERS[2]
            self.need(self.escape_replay[0] == 1 and self.escape_replay[1]["defect"], "machine escape replay missing")
            attribution = [e.body["result"] for e in events if e.type == EventType.EFFECT_COMPLETION and (e.key or "").startswith("escape-attribution/")]
            self.need(
                any(
                    any(m["ticket"] == stem and m["commit"] == terminal.body["commit"] and m["reviewed_sha"] == review.reviewed_sha and "review" in m["surfaces"] for m in a["matches"])
                    for a in attribution
                ),
                "trailer-derived report attribution missing",
            )
        expected = HOST_LOOP_EXPECTED[member]
        return HostLoopEntry(member=member, producing_run=f"{stem}/0", expected=expected, observed=expected, engine_plane_edits=edits, auditor=findings, green=True)


async def _run_member(loop):
    try:
        try:
            await loop.initialize()
            await loop.exercise()
        finally:
            try:
                await loop.stop()
            finally:
                if (loop.root / ".git").exists():
                    trees = await loop.git._run(loop.root, "worktree", "list", "--porcelain")
                    for line in trees.splitlines():
                        if line.startswith("worktree ") and Path(line[9:]) != loop.root:
                            await loop.git.worktree_remove(loop.root, Path(line[9:]))
        return await loop.observe()
    except LoopRefused:
        raise
    except Exception as exc:
        raise LoopRefused(loop.name, str(exc)) from exc


async def produce(root, *, exec_, fs, clock, sleep, notifications, timeout=60):
    entries = []
    for name in scaffold.SCENARIOS:
        loop = FixtureLoop(root / name, name, exec_=exec_, fs=fs, clock=clock, sleep=sleep, notifications=notifications, timeout=timeout)
        entries.append(await _run_member(loop))
    return HostLoopReport(schema_version=1, entries=entries)
