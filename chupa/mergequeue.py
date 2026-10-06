"""Dormant serial merge admission (CHUPA_PLAN.md sections 9, 10; 19.P3).

The daemon activation owns composition. Nothing in the production import closure imports this module.
"""

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from chupa.artifacts import Finding
from chupa.config import RegenerateStrategy, UnionStrategy
from chupa.gates import run_gates
from chupa.git import GitError
from chupa.journal import EventType
from chupa.merge import Admission, Candidate, MERGE_GATES, MERGE_SPEC_VERSION, SeedOnMain, squash_message
from chupa.providers import child_env
from chupa.seams import ExecutableNotFound
from chupa.stages import (
    CHECK_GATES, MAIN, Evidence, StageContext, check_severity, gather_evidence,
)
from chupa.tickets import TICKETS_DIR, Ticket, ticket_path

RED_STREAK_K = 3


@dataclass(frozen=True)
class UnresolvedConflict:
    stem: str
    paths: tuple[str, ...]


@dataclass(frozen=True)
class MechanicalResolution:
    paths: tuple[str, ...]
    strategy_hits: tuple[str, ...]


@dataclass(frozen=True)
class RebaseFailure:
    paths: tuple[str, ...]


@dataclass(frozen=True)
class QueueResult:
    outcome: Literal["ok", "gate_failed", "unresolved_conflict", "paused"]
    artifact: Admission | None = None
    findings: tuple[Finding, ...] = ()
    handoff: UnresolvedConflict | None = None


class TreeHashMismatch(RuntimeError):
    """Main moved to a tree other than the tree that passed integration."""


class MergeQueue:
    def __init__(self, ctx: StageContext) -> None:
        self.ctx = ctx
        self._lock = asyncio.Lock()
        self._red: list[str] = []
        self.paused = False

    def resume(self) -> None:
        self._red.clear()
        self.paused = False

    async def admit(self, ticket: Ticket, *, attempt: int) -> QueueResult:
        async with self._lock:
            if self.paused:
                return QueueResult("paused")
            return await self._admit(ticket, attempt)

    def _facts(self, stem: str, paths: list[str], rung: str, *,
               strategy_hits: list[str] | None = None, integration_red_paths: list[str] | None = None) -> None:
        self.ctx.driver.journal.append(EventType.SIGNAL, {
            "kind": "merge_conflict_facts", "paths": paths, "rung": rung,
            "strategy_hits": strategy_hits or [], "integration_red_paths": integration_red_paths or [],
        }, ticket=stem)

    def _red_ticket(self, stem: str) -> None:
        if stem not in self._red:
            self._red.append(stem)
        if len(self._red) >= RED_STREAK_K:
            self.paused = True
            self.ctx.driver.journal.append(EventType.SIGNAL, {
                "kind": "merge_red_streak_paused", "stems": list(self._red), "threshold": RED_STREAK_K,
            }, ticket=stem)

    async def _candidate(self, ticket: Ticket, reviewed: str, changed: list[str]) -> Candidate:
        ctx, stem = self.ctx, ticket.stem
        seeds = []
        for seed_stem in sorted({e.ticket for e in ctx.driver.journal.read()
                                 if e.type == EventType.SIGNAL and e.ticket is not None
                                 and e.body.get("signal") == "ticket_intake" and e.body.get("seeded_by") == stem}):
            path = ticket_path(seed_stem)
            try:
                sha = await ctx.git.rev_parse(ctx.repo, f"{MAIN}:{path}")
                text = await ctx.git._run(ctx.repo, "show", f"{MAIN}:{path}")
            except GitError:
                sha, text = None, None
            seeds.append(SeedOnMain(stem=seed_stem, ticket_sha=sha, ticket_text=text))
        checks_text = None
        if seeds:
            try:
                checks_text = await ctx.git._run(ctx.repo, "show", f"{MAIN}:{TICKETS_DIR}/{stem}/checks.json")
            except GitError:
                pass
        review = ctx.repo / TICKETS_DIR / stem / "review.md"
        return Candidate(stem=stem, reviewed_sha=reviewed, changed_files=changed,
                         ticket_text=(ctx.repo / ticket_path(stem)).read_text(),
                         review_text=review.read_text() if review.is_file() else None,
                         seeds=seeds, seed_checks_text=checks_text)

    def _strategy(self, path: str) -> RegenerateStrategy | UnionStrategy | None:
        for row in self.ctx.config.merge.strategies:
            if any(path == p or path.startswith(p.rstrip("/") + "/") for p in row.paths):
                return row
        return None

    async def _resolve(self, worktree: Path, path: str,
                       row: RegenerateStrategy | UnionStrategy) -> None:
        git = self.ctx.git
        if isinstance(row, UnionStrategy):
            base = await git._run(worktree, "show", f":1:{path}")
            ours = await git._run(worktree, "show", f":2:{path}")
            theirs = await git._run(worktree, "show", f":3:{path}")
            if not ours.startswith(base) or not theirs.startswith(base):
                raise ValueError(f"{path} is not append-only; union strategy refused")
            merged = base + ours[len(base):]
            for line in theirs[len(base):].splitlines(keepends=True):
                if line not in ours[len(base):].splitlines(keepends=True):
                    merged += line
            self.ctx.fs.write(worktree / path, merged.encode())
        else:
            await git._run(worktree, "checkout", "--theirs", "--", path)
            rc, out, err = await self.ctx.exec_.run(row.argv, cwd=worktree,
                                                    env=child_env(self.ctx.env, self.ctx.config),
                                                    timeout=self.ctx.config.drain.max_ticket_minutes * 60)
            if rc:
                raise ValueError(f"generator for {path} exited {rc}: {(out + err)[-1000:]}")
        await git.add(worktree, [path])

    async def _rebase(self, ticket: Ticket) -> MechanicalResolution | UnresolvedConflict | RebaseFailure:
        ctx, stem = self.ctx, ticket.stem
        worktree = ctx.worktree(stem)
        paths_seen: list[str] = []
        hits: list[str] = []
        error = await ctx.git.rebase_stop_at_conflict(worktree, MAIN)
        while error is not None:
            paths = await ctx.git.conflicted_paths(worktree)
            paths_seen.extend(p for p in paths if p not in paths_seen)
            if not paths:
                await ctx.git._rebase_abort(worktree)
                self._facts(stem, paths_seen, "refused", strategy_hits=hits)
                return RebaseFailure(tuple(paths_seen))
            rows = [(p, self._strategy(p)) for p in paths]
            if any(row is None for _, row in rows):
                await ctx.git._rebase_abort(worktree)
                self._facts(stem, paths_seen, "rework", strategy_hits=hits)
                return UnresolvedConflict(stem, tuple(paths_seen))
            try:
                for path, row in rows:
                    assert row is not None
                    await self._resolve(worktree, path, row)
                    hits.append(path)
                try:
                    await ctx.git.rebase_continue(worktree)
                    error = None
                except GitError as exc:
                    error = exc
            except (GitError, ValueError, ExecutableNotFound):
                remaining = await ctx.git.conflicted_paths(worktree)
                if remaining:
                    paths_seen.extend(p for p in remaining if p not in paths_seen)
                    await ctx.git._rebase_abort(worktree)
                    self._facts(stem, paths_seen, "rework", strategy_hits=hits)
                    return UnresolvedConflict(stem, tuple(paths_seen))
                await ctx.git._rebase_abort(worktree)
                self._facts(stem, paths_seen, "refused", strategy_hits=hits)
                return RebaseFailure(tuple(paths_seen))
        self._facts(stem, paths_seen, "mechanical", strategy_hits=hits)
        return MechanicalResolution(tuple(paths_seen), tuple(hits))

    async def _admit(self, ticket: Ticket, attempt: int) -> QueueResult:
        ctx, stem = self.ctx, ticket.stem
        worktree = ctx.worktree(stem)
        reviewed = await ctx.git.rev_parse(ctx.repo, stem)
        await ctx.git.restore(worktree, [TICKETS_DIR], source=stem)
        resolution = await self._rebase(ticket)
        if isinstance(resolution, UnresolvedConflict):
            await ctx.git._restore_head(worktree, reviewed)
            self._red.clear()
            return QueueResult("unresolved_conflict", handoff=resolution)
        if isinstance(resolution, RebaseFailure):
            await ctx.git._restore_head(worktree, reviewed)
            self._red.clear()
            return QueueResult("gate_failed", findings=(Finding(
                code="post_rebase_regate", message="rebase refused without a resolvable conflict",
                paved_road=f"re-run `run {stem}` from current main"),))
        paths, hits = list(resolution.paths), list(resolution.strategy_hits)
        if await ctx.git.status_porcelain(worktree):
            await ctx.git._restore_head(worktree, reviewed)
            self._red.clear()
            return QueueResult("gate_failed", findings=(Finding(
                code="post_rebase_regate", message="rebased worktree is dirty",
                paved_road=f"re-run `run {stem}` with a generator that leaves a clean worktree"),))

        changed = await ctx.git.diff_names(ctx.repo, MAIN, stem)
        candidate = await self._candidate(ticket, reviewed, changed)
        severity = check_severity(ctx, ticket)
        if candidate.seeds:
            severity["requisition_review"] = "hard"
        allowed_scope = list(ticket.scope_fence) + [p for row in ctx.config.merge.strategies for p in row.paths]
        run_md = ctx.repo / TICKETS_DIR / stem / "run.md"
        early = Evidence(stem=stem, head_sha=await ctx.git.rev_parse(worktree, "HEAD"), claimed="ok",
                         scope_fence=allowed_scope, changed_files=changed,
                         inserted_lines=0, verification=[],
                         run_record=run_md.read_text() if run_md.is_file() else None)
        safety_gates = [g for g in CHECK_GATES if g.code in {"scope_fence", "run_record"}]
        safety = run_gates(safety_gates, early, worktree, severity=severity)
        merge_safety = run_gates(MERGE_GATES, candidate, ctx.repo, severity=severity)
        findings = [f for result in (safety, merge_safety) for report in result.hard_failures
                    for f in report.findings]
        safety_codes = set(ctx.config.merge.safety_checks)
        unknown = safety_codes - {check.code for check in ctx.config.review.mechanical}
        for code in sorted(unknown):
            findings.append(Finding(code=code, message=f"merge safety check {code} is not declared",
                                    paved_road="declare the check under review.mechanical or remove it from"
                                               " merge.safety_checks"))
        for check in ctx.config.review.mechanical:
            if check.code not in ctx.config.merge.safety_checks:
                continue
            try:
                rc, out, err = await ctx.exec_.run(check.argv, cwd=worktree,
                                                    env=child_env(ctx.env, ctx.config),
                                                    timeout=ticket.stuck_minutes * 60)
            except (TimeoutError, ExecutableNotFound) as exc:
                rc, out, err = None, "", str(exc)
            if rc != 0:
                findings.append(Finding(code=check.code, message=f"safety check exited {rc}: {(out + err)[-1000:]}",
                                        paved_road=f"make {' '.join(check.argv)} pass on the rebased worktree"))
        if findings:
            await ctx.git._restore_head(worktree, reviewed)
            self._red.clear()
            return QueueResult("gate_failed", findings=tuple(findings))

        evidence = await gather_evidence(ctx, ticket, "ok", attempt=attempt, stage="merge")
        # Integration is always red when a command is red on the candidate, even if its base is red too.
        evidence = evidence.model_copy(update={"scope_fence": allowed_scope, "verification": [
            r.model_copy(update={"base_red": False}) for r in evidence.verification]})
        integration = run_gates(CHECK_GATES, evidence, worktree, severity=severity)
        findings = [f for report in integration.hard_failures for f in report.findings]
        for check in ctx.config.review.mechanical:
            if check.trigger != "always" or check.severity != "hard":
                continue
            try:
                rc, out, err = await ctx.exec_.run(check.argv, cwd=worktree,
                                                    env=child_env(ctx.env, ctx.config),
                                                    timeout=ticket.stuck_minutes * 60)
            except (TimeoutError, ExecutableNotFound) as exc:
                rc, out, err = None, "", str(exc)
            if rc != 0:
                findings.append(Finding(code=check.code, message=f"integration check exited {rc}: {(out + err)[-1000:]}",
                                        paved_road=f"make {' '.join(check.argv)} pass on the rebased worktree"))
        if findings:
            red_paths = sorted({f.path for f in findings if f.path}) or changed
            self._facts(stem, paths, "integration_red", strategy_hits=hits,
                        integration_red_paths=red_paths)
            self._red_ticket(stem)
            await ctx.git._restore_head(worktree, reviewed)
            return QueueResult("gate_failed", findings=tuple(findings))

        self._red.clear()
        checked_tree = await ctx.git.rev_parse(worktree, "HEAD^{tree}")

        async def squash() -> dict:
            await ctx.git.merge_squash(ctx.repo, stem)
            await ctx.git.commit(ctx.repo, squash_message(ticket, reviewed))
            return {"commit": await ctx.git.rev_parse(ctx.repo, MAIN)}

        commit = (await ctx.driver.effects.run(squash, key=f"merge/{stem}/{attempt}", ticket=stem))["commit"]
        main_tree = await ctx.git.rev_parse(ctx.repo, "HEAD^{tree}")
        if main_tree != checked_tree:
            self.paused = True
            ctx.driver.journal.append(EventType.SIGNAL, {
                "kind": "merge_tree_hash_mismatch", "checked_tree": checked_tree, "main_tree": main_tree,
            }, ticket=stem)
            raise TreeHashMismatch(f"{stem}: main tree {main_tree} differs from checked tree {checked_tree}")
        ctx.driver.journal.append(EventType.STATE_TRANSITION,
                                  {"to": "merged", "commit": commit, "reviewed_sha": reviewed}, ticket=stem)
        await ctx.git.worktree_remove(ctx.repo, worktree)
        await ctx.git.branch_delete(ctx.repo, stem)
        admission = Admission(produced_by_spec_version=MERGE_SPEC_VERSION, produced_at_sha=commit,
                              stem=stem, commit=commit, reviewed_sha=reviewed)
        return QueueResult("ok", artifact=admission)
