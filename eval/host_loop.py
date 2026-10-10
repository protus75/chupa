"""Supervised disposable host evidence and canonical Phase 6 receipt writers."""

import argparse
import asyncio
import hashlib
import json
import sys
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

from chupa.artifacts import (HostLoopEntry, HostLoopReport, ExitReceipt, ReviewBaselineReport,
                            HOST_LOOP_MEMBERS, HOST_LOOP_EXPECTED)
from chupa.audit import audit_journal
from chupa.box import Box
from chupa.config import load_config
from chupa.control import AdmissionRequest, ControlRequest, publish_request, read_active, decisions, releases
from chupa.git import Git, GitError
from chupa.journal import Journal, EventType, TERMINAL_STATES
from chupa.mergequeue import held_admissions
from chupa.seams import LocalFileSystem, SubprocessExec
from chupa.stages import Invoice, read_review
from hosts.fixture import scaffold

ROOT = Path(__file__).resolve().parents[1]
ROAD = "repair the producing machinery and rerun the harness through Check"


class LoopRefused(ValueError):
    def __init__(self, member, detail):
        read = (HOST_LOOP_MEMBERS[1] if member == "regression" else
                HOST_LOOP_MEMBERS[2] if member == "escape" else
                HOST_LOOP_MEMBERS[0] if member.startswith("merge-") else member)
        super().__init__(f"{read} ({member}): {detail}; {ROAD}")


def canonical(record):
    return (json.dumps(record.model_dump(mode="json"), indent=2, ensure_ascii=False) + "\n").encode()


def write_report(path, report, *, fs):
    validated = HostLoopReport.model_validate(report.model_dump())
    fs.write(path, canonical(validated))


def regenerate(loop_bytes, baseline_bytes):
    """Only these validated input bytes supply receipt identity and digests."""
    loop = HostLoopReport.model_validate_json(loop_bytes)
    baseline = ReviewBaselineReport.model_validate_json(baseline_bytes)
    reads = {name: "pass" if all(e.green for e in loop.entries if e.member == name) else "fail"
             for name in HOST_LOOP_MEMBERS}
    reads["go_grade_report"] = "pass"
    return ExitReceipt(schema_version=1, reads=reads,
        host_loop_digest=hashlib.sha256(loop_bytes).hexdigest(),
        baseline_report_digest=hashlib.sha256(baseline_bytes).hexdigest(),
        verdict_signal=baseline.verdict_signal)


def write_receipt(path, loop_bytes, baseline_bytes, *, fs):
    receipt = regenerate(loop_bytes, baseline_bytes)
    fs.write(path, canonical(receipt))
    return receipt


async def committed_bytes(git, repo, path):
    rel = path.resolve().relative_to(repo.resolve()).as_posix()
    # cat-file's decoded return is exact for validated UTF-8 JSON, including whitespace.
    data = (await git._run(repo, "show", f"HEAD:{rel}")).encode()
    if path.read_bytes() != data:
        raise LoopRefused("go_grade_report", "input differs from its committed bytes")
    return data


class FixtureLoop:
    def __init__(self, root, name, *, exec_, fs, clock, sleep, notifications, timeout=60):
        self.root, self.name = root, name
        self.exec, self.fs, self.clock, self.sleep = exec_, fs, clock, sleep
        self.notifications, self.timeout = notifications, timeout
        self.task, self.pgid = None, None
        self.requests = set()
        self.env = {"PATH": str(root / "bin") + ":" + str(Path(sys.executable).parent) + ":/usr/bin:/bin",
                    "PYTHONPATH": str(ROOT), "PYTHONDONTWRITEBYTECODE": "1",
                    "CHUPA_FIXTURE_ROOT": str(root), "CHUPA_FIXTURE_SCENARIO": name,
                    "GIT_AUTHOR_NAME": "Fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
                    "GIT_COMMITTER_NAME": "Fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
                    "GIT_CONFIG_NOSYSTEM": "1"}
        self.git = Git(exec_, env=self.env, timeout=10)
        self.journal = Journal(root / ".chupa/state", clock)

    async def initialize(self):
        scaffold.copy_host(self.root)
        self.fs.write(self.root / "CHUPA_PLAN.md", b"# Disposable score host plan\n")
        self.fs.write(self.root / ".gitignore", b".chupa/\n.fixture-runtime/\ninbox/\n__pycache__/\n")
        # Committed report fixtures remain inputs; runtime intake uses an empty disposable inbox.
        cfg = self.root / "config.yaml"
        self.fs.write(cfg, cfg.read_bytes().replace(b"report_inbox: reports", b"report_inbox: inbox"))
        await self.git.init(self.root, branch="main")
        await self.git.add(self.root, [p.relative_to(self.root).as_posix() for p in self.root.rglob("*")
            if p.is_file() and not {".git", ".fixture-runtime"}.intersection(p.parts)])
        await self.git.commit(self.root, "fixture defective base")
        self.base = await self.git.rev_parse(self.root, "HEAD")
        cfg = load_config(None, cwd=self.root)
        self.inventory = cfg.engine_plane_safety_inventory

    async def start(self):
        self.task = asyncio.create_task(self.exec.run([sys.executable, "-m", "chupa", "serve"],
            cwd=self.root, env=self.env, timeout=self.timeout + 10,
            on_spawn=lambda pgid: setattr(self, "pgid", pgid)))
        await self.until(lambda: (self.root / ".chupa/state/control/active.json").exists())

    def confirm(self):
        state = self.root / ".chupa/state"
        lifecycle, _ = read_active(state, Path.read_bytes)
        events = self.journal.read()
        held = held_admissions(events)
        candidates = [(stem, hold) for stem, (hold, _) in held.items()]
        for path in (self.root / "tickets").glob("*/ticket.md"):
            if "state: draft" in path.read_text():
                candidates.append((path.parent.name, None))
        for stem, hold in candidates:
            identity = (stem, hold)
            if identity in self.requests:
                continue
            self.requests.add(identity)
            publish_request(state, AdmissionRequest(f"fixture-{len(self.requests)}", lifecycle,
                "confirm", stem, hold, "machine"), self.fs)

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
        return [e for e in self.journal.read() if e.ticket == stem
                and e.type == EventType.STATE_TRANSITION and e.body.get("to") in TERMINAL_STATES]

    async def merged(self, stem):
        await self.until(lambda: bool(self.terminal(stem)), confirm=True)
        if [e.body["to"] for e in self.terminal(stem)] != ["merged"]:
            raise LoopRefused(self.name, f"{stem} did not merge: {self.terminal(stem)}")
        return self.terminal(stem)[0]

    def suggestion(self):
        Box(self.root / ".chupa/state/box", self.fs).enqueue(message_class="suggestion",
            origin="fixture", summary=scaffold.scenario(self.root, self.name)["responses"]["implement"][0]["summary"],
            occurrence_id=f"fixture/{self.name}")

    async def report(self, name, *, app_commit=None):
        raw = json.loads((self.root / f"reports/{name}.json").read_bytes())
        if app_commit is not None:
            raw["app_commit"] = app_commit
        self.fs.write(self.root / "inbox/report.json", (json.dumps(raw) + "\n").encode())

    async def replay(self, path):
        rc, out, _ = await self.exec.run([sys.executable, "replay.py", path], cwd=self.root,
                                       env=self.env, timeout=10)
        return rc, json.loads(out)

    async def exercise(self):
        await self.start()
        if self.name == "regression":
            await self.report("regression")
            await self.until(lambda: (self.root / "tickets/regression/evidence/replay.json").exists())
            self.before_replay = await self.replay("tickets/regression/evidence/replay.json")
            await self.merged("regression")
            self.after_replay = await self.replay("tickets/regression/evidence/replay.json")
        else:
            self.suggestion()
            terminal = await self.merged(self.name)
            if self.name == "escape":
                self.escape_replay = await self.replay("evidence/escape.json")
                # The report resolves to a fresh real bug; its attribution reads escape's squash.
                self.fs.write(self.root / ".fixture-runtime/selection", b"regression")
                await self.report("escape", app_commit=terminal.body["commit"])
                await self.until(lambda: any((e.key or "").startswith("escape-attribution/")
                    and e.type == EventType.EFFECT_COMPLETION
                    and e.body.get("result", {}).get("matches") for e in self.journal.read()))

    async def stop(self):
        if self.task is None:
            return
        try:
            if not self.task.done():
                state = self.root / ".chupa/state"
                try:
                    lifecycle, _ = read_active(state, Path.read_bytes)
                    publish_request(state, ControlRequest("fixture-stop", lifecycle, "kill", None), self.fs)
                    await asyncio.wait_for(asyncio.shield(self.task), 5)
                except (ValueError, TimeoutError):
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
        terminal, = self.terminal(stem)
        self.need(terminal.body.get("commit") and terminal.body.get("reviewed_sha"), "merged identity missing")
        def completion(key):
            rows = [e.body["result"] for e in events if e.type == EventType.EFFECT_COMPLETION and e.key == key]
            self.need(len(rows) == 1, f"missing unique production evidence {key}")
            return rows[0]
        admission = completion(f"merge/{stem}/0")
        self.need(admission["commit"] == terminal.body["commit"], "merge completion disagrees with terminal")
        checks = completion(f"ticket-plane/{stem}/0/checks")
        invoice = Invoice.model_validate_json(await self.git._run(self.root, "show",
            f"{checks['commit']}:tickets/{stem}/checks.json"))
        self.need(invoice.passed and invoice.verification and all(v.rc == 0 for v in invoice.verification),
                  "committed Check is not green")
        review_lift = completion(f"ticket-plane/{stem}/0/review")
        review = read_review(await self.git._run(self.root, "show",
            f"{review_lift['commit']}:tickets/{stem}/review.md"))
        self.need(review.verdict == "approve" and review.reviewed_sha == terminal.body["reviewed_sha"]
                  == invoice.produced_at_sha, "checked/reviewed identity mismatch")
        rows = await self.git.first_parent_squashes(self.root, terminal.body["commit"])
        self.need(len(rows) == 1 and rows[0]["ticket"] == stem
                  and rows[0]["reviewed_sha"] == review.reviewed_sha, "squash trailer evidence missing")
        edits = [p for p in rows[0]["paths"] if any(p == f.rstrip("/") or p.startswith(f.rstrip("/") + "/")
                 for f in self.inventory)]
        self.need(not edits, "engine-plane edits: " + ", ".join(edits))
        accepted = [e.body for e in decisions(events) if e.body["decision"] == "accepted"
                    and e.body.get("stem") == stem and e.body.get("verb") == "confirm"]
        self.need(any(b["hold_id"] is None and b["actor"] == "machine" for b in accepted)
                  and any(b["hold_id"] is not None and b["actor"] == "machine" for b in accepted),
                  "machine draft and held confirmations missing")
        self.need(any(r["stem"] == stem and r["actor"] == "machine" for r in releases(events).values()),
                  "identity-bound release completion missing")
        self.need(not any(e.body.get("signal") in ("review_baseline", "reject_verdict") for e in events),
                  "fixture recorded GO or re-armed caps")
        member = HOST_LOOP_MEMBERS[0]
        if stem == "regression":
            member = HOST_LOOP_MEMBERS[1]
            self.need(self.before_replay[0] == 1 and self.before_replay[1]["defect"]
                      and self.after_replay[0] == 0 and not self.after_replay[1]["defect"], "replay repair missing")
            bug, = [r for r in invoice.reports if r.code == "bug_evidence"]
            self.need(bug.verdict == "pass" and bug.bug_evidence.head.regression_result == "pass"
                      and bug.bug_evidence.base.regression_result == "defect"
                      and bug.bug_evidence.overlay_paths == ["fixtures/replay.json", "fixtures/report_regression.py"]
                      and bug.bug_evidence.evidence_paths, "real regression-gate evidence missing")
            authored = completion("ticket-plane/regression/author")
            carried = await self.git._run(self.root, "show", f"{invoice.produced_at_sha}:fixtures/replay.json")
            custody = await self.git._run(self.root, "show", f"{authored}:tickets/regression/evidence/replay.json")
            self.need(carried == custody, "carried replay differs from authored durable evidence")
            self.need(await self.git._run(self.root, "show", f"{bug.bug_evidence.base_sha}:regression_test.py"),
                      "test absent on defective base")
        elif stem == "escape":
            member = HOST_LOOP_MEMBERS[2]
            self.need(self.escape_replay[0] == 1 and self.escape_replay[1]["defect"], "machine escape replay missing")
            attribution = [e.body["result"] for e in events if e.type == EventType.EFFECT_COMPLETION
                           and (e.key or "").startswith("escape-attribution/")]
            self.need(any(any(m["ticket"] == stem and m["commit"] == terminal.body["commit"]
                and m["reviewed_sha"] == review.reviewed_sha and "review" in m["surfaces"]
                for m in a["matches"]) for a in attribution), "trailer-derived report attribution missing")
        expected = HOST_LOOP_EXPECTED[member]
        return HostLoopEntry(member=member, producing_run=f"{stem}/0", expected=expected,
                             observed=expected, engine_plane_edits=edits, auditor=findings, green=True)


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
        loop = FixtureLoop(root / name, name, exec_=exec_, fs=fs, clock=clock, sleep=sleep,
                           notifications=notifications, timeout=timeout)
        entries.append(await _run_member(loop))
    return HostLoopReport(schema_version=1, entries=entries)


async def _main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m eval.host_loop")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    args = parser.parse_args(argv)
    fs, exec_ = LocalFileSystem(), SubprocessExec()
    clock = lambda: datetime.now(UTC)
    git = Git(exec_, env={"PATH": "/usr/bin:/bin"}, timeout=10)
    try:
        try:
            baseline_bytes = await committed_bytes(git, Path.cwd(), args.baseline)
            ReviewBaselineReport.model_validate_json(baseline_bytes)
        except (ValueError, OSError, GitError) as exc:
            raise LoopRefused("go_grade_report", str(exc)) from exc
        with tempfile.TemporaryDirectory(prefix="chupa-host-loop-") as directory:
            report = await produce(Path(directory), exec_=exec_, fs=fs, clock=clock,
                                   sleep=asyncio.sleep, notifications=None)
        write_report(args.out, report, fs=fs)
        write_receipt(args.receipt, canonical(report), baseline_bytes, fs=fs)
    except (ValueError, OSError, GitError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


def main(argv=None):
    return asyncio.run(_main(argv))


if __name__ == "__main__":
    raise SystemExit(main())
