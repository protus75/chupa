"""Merge admission against a temp repo (CHUPA_PLAN.md sections 7, 9, 10; 19.P1)."""

import asyncio
import dataclasses
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from chupa.config import load_config
from chupa.box import BOX_DIR, Box
from chupa.driver import Driver
from chupa.git import Git
from chupa.journal import EventType
from chupa.llm import FakeLLM
from chupa.merge import Admission, AdmissionBoundary, Candidate, PostRebaseGate, merge
from chupa.mergequeue import CONFLICT_FACTS, MergeQueue
from chupa import runner
from chupa.seams import LocalFileSystem, SubprocessExec
from chupa.stages import StageContext, run_stages
from chupa.tickets import validate_ticket
from tests.test_seed_path import (context as seed_context, repo as seed_repo, requisition, seed_text,
                                  ticket as seeding_ticket, write_seeds)
from tests.test_stages import ENV, SNAG, SPECS, STEM, agent, author, git, verdict

GOAL = "`thing.py` holds the word ok."


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "chupa").mkdir(parents=True)
    (root / "chupa" / "thing.py").write_text("")
    (root / "chupa" / "other.py").write_text("")
    (root / "CHUPA_PLAN.md").write_text("# Plan\n")
    (root / "config.yaml").write_text((Path(__file__).parent / "test_stages.py").read_text()
                                      .split('CONFIG = """')[1].split('"""')[0])
    (root / ".gitignore").write_text(".chupa/\n")
    git(root, "init", "-b", "main")
    git(root, "add", ".")
    git(root, "commit", "-m", "base")
    return root


def context(repo: Path, script: list) -> StageContext:
    config = load_config(None, cwd=repo)
    clock = lambda: datetime(2026, 10, 5, tzinfo=UTC)  # noqa: E731

    async def never(seconds: float) -> None:
        await asyncio.Event().wait()

    exec_ = SubprocessExec()
    driver = Driver.from_config(config, llm=FakeLLM(script), env=ENV, clock=clock, sleep=never)
    return StageContext(repo=repo, config=config, env=ENV, exec_=exec_, git=Git(exec_, env=ENV, timeout=30.0),
                        fs=LocalFileSystem(), driver=driver, specs_dir=SPECS)


def reviewed(repo: Path, script: list, *, approve: bool = True, authored: bool = False):
    """Author the ticket and run Implement -> Check -> Review; return what merge needs."""
    if not authored:
        author(repo)
    ctx = context(repo, script)
    ticket = validate_ticket(STEM, (repo / "tickets" / STEM / "ticket.md").read_text(), repo)
    run = asyncio.run(run_stages(ctx, ticket))
    assert run.last == ("review", run.results["review"])
    assert (run.results["review"].outcome == "ok") is approve
    return ctx, ticket, run.attempt


def admit(ctx, ticket, attempt):
    return asyncio.run(merge(ctx, ticket, attempt=attempt))


def merged_events(ctx):
    return [e for e in ctx.driver.journal.read()
            if e.type == EventType.STATE_TRANSITION and e.body.get("to") == "merged"]


def refused_untouched(ctx, result, main_before: str, code: str) -> None:
    assert result.outcome == "gate_failed" and result.artifact is None
    assert code in [f.code for f in result.findings]
    assert git(ctx.repo, "rev-parse", "main").strip() == main_before  # main never moved
    assert git(ctx.repo, "rev-parse", "--verify", STEM)  # branch left in place
    assert ctx.worktree(STEM).is_dir()
    assert not merged_events(ctx)


def test_a_passing_ticket_squash_merges_with_trailers_and_journals_merged(repo):
    ctx, ticket, attempt = reviewed(repo, [agent({"chupa/thing.py": "ok\n"}), verdict()])
    head = git(repo, "rev-parse", STEM).strip()

    result = admit(ctx, ticket, attempt)

    assert result.outcome == "ok", result.findings
    admission = result.artifact
    assert isinstance(admission, Admission) and admission.reviewed_sha == head
    assert git(repo, "rev-parse", "main").strip() == admission.commit
    message = git(repo, "log", "-1", "--format=%B", "main")
    assert message.splitlines()[0] == f"chupa({STEM}): {GOAL}"
    trailers = git(repo, "log", "-1", "--format=%(trailers:only,unfold)", "main").split("\n")
    assert f"chupa-ticket: {STEM}" in trailers and f"chupa-reviewed-sha: {head}" in trailers
    # One commit per ticket, code only: the ticket plane rode its own lane.
    assert git(repo, "show", "--name-only", "--format=", "main").split() == ["chupa/thing.py"]
    assert (repo / "chupa" / "thing.py").read_text() == "ok\n"

    [event] = merged_events(ctx)
    assert event.ticket == STEM and event.body == {"to": "merged", "commit": admission.commit, "reviewed_sha": head}
    assert not ctx.worktree(STEM).exists()
    assert git(repo, "branch", "--list", STEM) == ""
    assert git(repo, "status", "--porcelain") == ""


@pytest.mark.parametrize("verb", ["bind", "run", "drain"])
def test_bootstrap_pipeline_keeps_inline_admission(repo, monkeypatch, verb):
    author(repo)
    source = context(repo, [])
    checkout = runner.Checkout(repo, source.config, source.env, source.exec_, source.git,
                               source.driver.journal, source.fs, source.driver.clock, source.driver.sleep)
    from chupa.__main__ import build_control
    checkout = dataclasses.replace(checkout, control=build_control(checkout))
    llm = FakeLLM([agent({"chupa/thing.py": "ok\n"}), verdict()])

    def forbidden(*args, **kwargs):
        pytest.fail("bootstrap dispatch used the composed queue")

    monkeypatch.setattr(MergeQueue, "offer", forbidden)
    monkeypatch.setattr(MergeQueue, "process", forbidden)
    calls = []
    original = runner.merge

    async def inline(ctx, ticket, *, attempt):
        calls.append((ctx, ticket, attempt))
        return await original(ctx, ticket, attempt=attempt)

    monkeypatch.setattr(runner, "merge", inline)
    def pipeline(local):
        dispatch = runner.bind(local, llm)
        dispatch.queue.paused, dispatch.queue.hold_id = True, "daemon-only-hold"
        local.control.hold(dispatch.queue.hold_id)
        return dispatch
    ticket = validate_ticket(STEM, (repo / "tickets" / STEM / "ticket.md").read_text(), repo)
    if verb == "bind":
        assert asyncio.run(pipeline(checkout)(ticket)) == "merged"
    else:
        from chupa.__main__ import main
        from tests.test_drain_reentry import NoChild
        assert main(["run", STEM] if verb == "run" else ["drain"], cwd=repo, env=ENV,
                    clock=checkout.clock, pipeline=pipeline, reexec=NoChild()) == 0
    [(ctx, original_ticket, attempt)] = calls
    assert original_ticket.stem == ticket.stem and attempt == 0
    assert len(merged_events(ctx)) == 1
    assert not any(e.body.get("kind") == CONFLICT_FACTS for e in ctx.driver.journal.read())
    assert (repo / "chupa/thing.py").read_text() == "ok\n" and not ctx.worktree(STEM).exists()


@pytest.mark.parametrize("failure", ["ticket-plane", "missing-checks", "malformed-checks", "missing-approval", "wrong-sha",
                                    "missing-blob", "invalid-blob", "dirty-main"])
def test_daemon_prechecks_precede_offer(seed_repo, monkeypatch, failure):
    ctx, ticket, attempt = seed_reviewed(seed_repo)
    async def scenario():
        checks = "tickets/add-thing/checks.json"
        seed = "tickets/alpha-seed/ticket.md"
        code = "requisition_review"
        if failure == "ticket-plane":
            code = "post_rebase_regate"
            path = ctx.worktree(ticket.stem) / "tickets/committed.md"
            ctx.fs.write(path, b"forbidden code-lane ticket\n")
            await ctx.git.add(ctx.worktree(ticket.stem), ["tickets/committed.md"])
            await ctx.git.commit(ctx.worktree(ticket.stem), "code lane violation")
        elif failure == "missing-checks":
            (ctx.repo / checks).unlink()
        elif failure == "malformed-checks":
            ctx.fs.write(ctx.repo / checks, b"invalid")
        elif failure in {"missing-approval", "wrong-sha"}:
            data = json.loads((ctx.repo / checks).read_text())
            if failure == "missing-approval":
                data["seeds"] = []
            else:
                data["seeds"][0]["ticket_sha"] = "wrong"
            ctx.fs.write(ctx.repo / checks, json.dumps(data).encode())
        elif failure == "missing-blob":
            (ctx.repo / seed).unlink()
        elif failure == "invalid-blob":
            ctx.fs.write(ctx.repo / seed, b"invalid")
            data = json.loads((ctx.repo / checks).read_text())
            data["seeds"][0]["ticket_sha"] = (await ctx.git._run(ctx.repo, "hash-object", seed)).strip()
            ctx.fs.write(ctx.repo / checks, json.dumps(data).encode())
        else:
            # A dirty, valid replacement cannot cure committed wrong-SHA custody.
            data = json.loads((ctx.repo / checks).read_text())
            data["seeds"][0]["ticket_sha"] = "wrong"
            valid = (ctx.repo / checks).read_bytes()
            ctx.fs.write(ctx.repo / checks, json.dumps(data).encode())
        if failure != "ticket-plane":
            await ctx.git.add(ctx.repo, [seed, checks])
            await ctx.git.commit(ctx.repo, "precheck refusal fixture")
        if failure == "dirty-main":
            ctx.fs.write(ctx.repo / checks, valid)
        ctx.config.review.gate_severity = {code: "soft"}
        before = await ctx.git.rev_parse(ctx.repo, "main")
        head = await ctx.git.rev_parse(ctx.repo, ticket.stem)
        journal = ctx.driver.journal.read()
        queue = MergeQueue(ctx, escalate=lambda _: None)
        def forbidden(*args, **kwargs):
            pytest.fail("precheck refusal offered, rebased or ran Verification")
        monkeypatch.setattr(queue, "offer", forbidden)
        monkeypatch.setattr(ctx.git, "rebase_stop_at_conflict", forbidden)
        monkeypatch.setattr(ctx.git, "rebase", forbidden)
        monkeypatch.setattr(stages, "gather_evidence", forbidden)
        boundary = AdmissionBoundary(ctx, mode="daemon", queue=queue)
        result = await boundary(ticket, attempt=attempt)
        assert result.outcome == "gate_failed" and result.artifact is None
        assert code in {f.code for f in result.findings}
        assert all(f.paved_road for f in result.findings)
        assert await ctx.git.rev_parse(ctx.repo, "main") == before
        assert await ctx.git.rev_parse(ctx.repo, ticket.stem) == head
        assert ctx.worktree(ticket.stem).exists() and not queue.pending
        assert ctx.driver.journal.read() == journal and not boundary.results
    from chupa import stages
    asyncio.run(scenario())


def test_admission_mode_is_explicit(repo, monkeypatch):
    ctx, ticket, attempt = reviewed(repo, [agent({"chupa/thing.py": "ok\n"}), verdict()])
    queue = MergeQueue(ctx, escalate=lambda _: None)
    def forbidden(*args, **kwargs):
        pytest.fail("construction or inline admission entered daemon queue")
    monkeypatch.setattr(queue, "offer", forbidden)
    monkeypatch.setattr(queue, "process", forbidden)
    before = ctx.driver.journal.read()
    with monkeypatch.context() as idle:
        idle.setattr(ctx.exec_, "run", forbidden)
        idle.setattr(asyncio, "create_task", forbidden)
        boundary = AdmissionBoundary(ctx, queue=queue)
        daemon = AdmissionBoundary(ctx, mode="daemon", queue=queue)
    assert boundary.mode == "inline" and daemon.mode == "daemon"
    assert not boundary.results and not daemon.results and not queue.pending
    assert ctx.driver.journal.read() == before
    for kwargs in ({"mode": "unknown", "queue": queue}, {"mode": "daemon"}):
        with pytest.raises(runner.Refusal, match="supply.*MergeQueue.*serve composition"):
            AdmissionBoundary(ctx, **kwargs)
    queue.paused, queue.hold_id = True, "daemon-hold"
    from chupa.lockfile import Lockfile
    lock = Lockfile(ctx.config.state_dir, instance_id="inline-mode", clock=ctx.driver.clock)
    lock.acquire()
    try:
        assert asyncio.run(boundary(ticket, attempt=attempt)).outcome == "ok"
    finally:
        lock.release()


def test_approval_carries_across_a_clean_rebase_onto_a_moved_main(repo):
    ctx, ticket, attempt = reviewed(repo, [agent({"chupa/thing.py": "ok\n"}), verdict()])
    head = git(repo, "rev-parse", STEM).strip()
    (repo / "chupa" / "other.py").write_text("moved\n")
    git(repo, "commit", "-am", "main moves")

    result = admit(ctx, ticket, attempt)

    assert result.outcome == "ok", result.findings
    assert f"chupa-reviewed-sha: {head}" in git(repo, "log", "-1", "--format=%B", "main")
    assert (repo / "chupa" / "other.py").read_text() == "moved\n"
    assert git(repo, "show", "--name-only", "--format=", "main").split() == ["chupa/thing.py"]


def test_a_rerun_worktree_with_lifted_tracked_copies_is_restored_and_merges(repo):
    # A prior run already lifted run.md / checks.json / review.md to main, so this run's worktree is born
    # tracking them; the new lift unlinks them there, and an un-restored tree would refuse the rebase.
    author(repo)
    for name in ("run.md", "checks.json", "review.md"):
        (repo / "tickets" / STEM / name).write_text("prior run\n")
    git(repo, "add", "tickets")
    git(repo, "commit", "-m", f"chupa({STEM}): prior run")
    ctx, ticket, attempt = reviewed(repo, [agent({"chupa/thing.py": "ok\n"}), verdict()], authored=True)
    assert "D tickets/" in git(ctx.worktree(STEM), "status", "--porcelain")

    result = admit(ctx, ticket, attempt)

    assert result.outcome == "ok", result.findings
    assert git(repo, "show", "--name-only", "--format=", "main").split() == ["chupa/thing.py"]
    assert "prior run" not in (repo / "tickets" / STEM / "review.md").read_text()


def test_a_failing_hard_gate_blocks_admission(repo):
    # Verification goes red on the rebased candidate but stays green on the merge base.
    ctx, ticket, attempt = reviewed(repo, [agent({"chupa/thing.py": "ok\n"}), verdict()])
    ticket = dataclasses.replace(ticket, verification=(("test", "!", "-s", "chupa/thing.py"),))
    (repo / "chupa" / "other.py").write_text("x\n")
    git(repo, "commit", "-am", "main moves")
    before = git(repo, "rev-parse", "main").strip()

    result = admit(ctx, ticket, attempt)

    refused_untouched(ctx, result, before, "verification")


def test_base_red_verification_does_not_refuse_merge_regating(repo):
    ctx, ticket, attempt = reviewed(repo, [agent({"chupa/thing.py": "ok\n"}), verdict()])
    ticket = dataclasses.replace(ticket, verification=(("grep", "-q", "absent", "chupa/thing.py"),))

    result = admit(ctx, ticket, attempt)

    assert result.outcome == "ok", result.findings
    messages = Box(ctx.config.state_dir / BOX_DIR, ctx.fs).messages()
    assert len(messages) == 1 and messages[0].outcome == "base_red"
    assert messages[0].stage == "merge"
    assert not (ctx.config.worktree_root / ".base" / STEM).exists()


def test_an_approval_pinned_to_an_older_head_blocks_admission(repo):
    ctx, ticket, attempt = reviewed(repo, [agent({"chupa/thing.py": "ok\n"}), verdict()])
    (ctx.worktree(STEM) / "chupa" / "thing.py").write_text("ok but changed after review\n")
    git(ctx.worktree(STEM), "commit", "-am", "post-review edit")
    before = git(repo, "rev-parse", "main").strip()

    result = admit(ctx, ticket, attempt)

    refused_untouched(ctx, result, before, "correctness_review")
    assert "the approval pins" in result.findings[0].message


def test_a_snag_verdict_is_no_approval(repo):
    ctx, ticket, attempt = reviewed(repo, [agent({"chupa/thing.py": "ok\n"}), verdict("snag", [SNAG])],
                                    approve=False)
    before = git(repo, "rev-parse", "main").strip()

    result = admit(ctx, ticket, attempt)

    refused_untouched(ctx, result, before, "correctness_review")
    assert "not approve" in result.findings[0].message


def test_a_branch_committing_ticket_plane_files_is_refused_with_the_outbox_road(tmp_path):
    candidate = Candidate(stem=STEM, reviewed_sha="abc", ticket_text="", review_text=None,
                          changed_files=["chupa/thing.py", f"tickets/{STEM}/notes.md"])

    report = PostRebaseGate().check(candidate, tmp_path)

    [finding] = report.findings
    assert report.verdict == "fail" and finding.path == f"tickets/{STEM}/notes.md"
    assert "driver lifts them" in finding.paved_road


def test_a_main_ticket_edit_failing_the_schema_blocks_admission(repo):
    ctx, ticket, attempt = reviewed(repo, [agent({"chupa/thing.py": "ok\n"}), verdict()])
    path = repo / "tickets" / STEM / "ticket.md"
    path.write_text(path.read_text().replace("## Definition of rejected\nNeeds a new dependency.\n\n", ""))
    git(repo, "commit", "-am", "hand edit")
    before = git(repo, "rev-parse", "main").strip()

    result = admit(ctx, ticket, attempt)

    refused_untouched(ctx, result, before, "ticket_schema")


def test_a_conflicted_rebase_is_aborted_and_refused(repo):
    ctx, ticket, attempt = reviewed(repo, [agent({"chupa/thing.py": "ok\n"}), verdict()])
    head = git(repo, "rev-parse", STEM).strip()
    (repo / "chupa" / "thing.py").write_text("conflict\n")
    git(repo, "commit", "-am", "main conflicts")
    before = git(repo, "rev-parse", "main").strip()

    result = admit(ctx, ticket, attempt)

    refused_untouched(ctx, result, before, "post_rebase_regate")
    assert "re-branches from current main" in result.findings[0].paved_road
    assert git(repo, "rev-parse", STEM).strip() == head  # never left mid-rebase
    assert not (repo / ".git" / "worktrees" / STEM / "rebase-merge").exists()


def seed_reviewed(repo):
    seed = seed_text("alpha-seed")
    ctx, llm = seed_context(repo, [write_seeds({"alpha-seed": seed}), requisition("approve"), verdict()])
    ticket = seeding_ticket(repo)
    run = asyncio.run(run_stages(ctx, ticket))
    assert run.results["review"].outcome == "ok"
    assert [req.surface for req in llm.requests] == ["implement", "requisition_review", "review"]
    return ctx, ticket, run.attempt


def test_merge_safety_refuses_a_seed_whose_committed_blob_changed(seed_repo):
    ctx, ticket, attempt = seed_reviewed(seed_repo)
    path = seed_repo / "tickets/alpha-seed/ticket.md"
    path.write_text(path.read_text() + "\n")
    git(seed_repo, "commit", "-am", "seed text changes after Check")
    before = git(seed_repo, "rev-parse", "main").strip()

    result = admit(ctx, ticket, attempt)

    refused_untouched(ctx, result, before, "requisition_review")
    assert any("no approve verdict pins" in f.message for f in result.findings)


def test_merge_safety_rechecks_seed_lint_even_with_a_matching_approval(seed_repo):
    ctx, ticket, attempt = seed_reviewed(seed_repo)
    path = seed_repo / "tickets/alpha-seed/ticket.md"
    path.write_text(path.read_text().replace("## Definition of rejected\nNeeds a new dependency.\n\n", ""))
    checks_path = seed_repo / "tickets" / STEM / "checks.json"
    checks = json.loads(checks_path.read_text())
    checks["seeds"][0]["ticket_sha"] = git(seed_repo, "hash-object", str(path)).strip()
    checks_path.write_text(json.dumps(checks))
    git(seed_repo, "commit", "-am", "invalid seed and matching approval")
    before = git(seed_repo, "rev-parse", "main").strip()

    result = admit(ctx, ticket, attempt)

    refused_untouched(ctx, result, before, "requisition_review")
    assert any("Definition of rejected" in f.message for f in result.findings)


def test_merge_safety_admits_a_seed_with_matching_recorded_approval(seed_repo):
    ctx, ticket, attempt = seed_reviewed(seed_repo)

    result = admit(ctx, ticket, attempt)

    assert result.outcome == "ok", result.findings
    assert (seed_repo / "tickets/alpha-seed/ticket.md").is_file()
    assert git(seed_repo, "show", "--name-only", "--format=", "main").split() == ["chupa/thing.py"]


def test_merge_safety_reads_committed_seed_and_checks_despite_dirty_main_checkout(seed_repo):
    ctx, ticket, attempt = seed_reviewed(seed_repo)
    (seed_repo / "tickets/alpha-seed/ticket.md").write_text("uncommitted invalid ticket\n")
    (seed_repo / "tickets" / STEM / "checks.json").write_text("uncommitted invalid checks\n")

    result = admit(ctx, ticket, attempt)

    assert result.outcome == "ok", result.findings
    assert git(seed_repo, "show", "main:tickets/alpha-seed/ticket.md") == seed_text("alpha-seed")


def test_pipeline_requires_supplied_control(repo):
    from chupa import merge as owner
    from chupa.__main__ import build_control
    ctx = context(repo, [])
    checkout = runner.Checkout(repo, ctx.config, ctx.env, ctx.exec_, ctx.git,
                               ctx.driver.journal, ctx.fs, ctx.driver.clock, ctx.driver.sleep)
    consumer = build_control(checkout)
    with pytest.raises(TypeError):
        owner.compose_pipeline(ctx, escalate=lambda _: None)
    with pytest.raises(runner.Refusal, match="build_control.*Checkout.control"):
        owner.compose_pipeline(ctx, escalate=lambda _: None, control=None)
    queue = owner.compose_pipeline(ctx, escalate=lambda _: None, control=consumer)
    assert queue.control is consumer and queue.hold_id is None
    assert MergeQueue(ctx, escalate=lambda _: None).control is None
    assert ctx.driver.journal.read() == []
