import asyncio

from chupa.__main__ import main
from chupa.llm import FakeLLM
from chupa.tickets import validate_ticket
from tests.test_author import _box, _failure, _routes, _run, requisition_reply
from tests.test_cli import ENV, git_out
from tests.test_drain import Clock, commit_ticket, confirmed, journal, make_root
from tests.test_mergequeue import ctx
from tests.test_rework import invoke, order, requisition
from tests.test_triage import author_reply, reply


def no_plan(tmp_path):
    root = make_root(tmp_path)
    (root / "CHUPA_PLAN.md").unlink()
    git_out(root, "add", "-u", "CHUPA_PLAN.md")
    git_out(root, "commit", "-m", "remove plan")
    return root


def test_author_without_plan(tmp_path, monkeypatch):
    root = no_plan(tmp_path)
    _routes(root)
    box = _box(root)
    message = _failure(box)
    llm = FakeLLM([reply("author"), author_reply("repair-thing"), requisition_reply("approve")])
    assert _run(root, monkeypatch, llm) == 0
    assert box.get(message).resolution.link == "repair-thing"
    assert any(r.surface == "requisition_review" for r in llm.requests)


def test_rework_without_plan(ctx):
    async def scenario():
        (ctx.repo / "CHUPA_PLAN.md").unlink()
        await ctx.git._run(ctx.repo, "add", "-u", "CHUPA_PLAN.md")
        await ctx.git.commit(ctx.repo, "remove plan")
        text = confirmed()
        ctx.fs.write(ctx.repo / "tickets/original/ticket.md", text.encode())
        await ctx.git.add(ctx.repo, ["tickets/original/ticket.md"])
        await ctx.git.commit(ctx.repo, "ticket")
        ticket = validate_ticket("original", text, ctx.repo)
        revised = text.replace("`thing()` returns ok.", "`thing()` returns revised ok.")
        result, requests = await invoke(ctx, ticket, text, [order("update", [("original", revised)]), requisition()])
        assert result.outcome == "ok"
        assert [r.surface for r in requests] == ["rework", "requisition_review"]
    asyncio.run(scenario())


def test_kill_without_plan_files_dead_dependency(tmp_path):
    root = no_plan(tmp_path)
    commit_ticket(root, "parent", confirmed())
    commit_ticket(root, "child", confirmed(depends="- parent"))
    assert main(["reject", "parent"], cwd=root, env=ENV, clock=Clock()) == 0
    assert any(e.ticket == "child" and e.body.get("signal") == "dead_dependency" for e in journal(root).read())
    assert "failure_report" in next((root / ".chupa/state/box").glob("*.json")).read_text()


def test_seed_review_without_plan(ctx):
    from chupa.stages import _review_seeds
    from tests.test_mergequeue import ready

    async def scenario():
        (ctx.repo / "CHUPA_PLAN.md").unlink()
        await ctx.git._run(ctx.repo, "add", "-u", "CHUPA_PLAN.md")
        await ctx.git.commit(ctx.repo, "remove plan")
        ticket = await ready(ctx, fence=("tickets",))
        candidate = confirmed().replace("source: human", "source: seed")
        ctx.fs.write(ctx.worktree(ticket.stem) / "tickets/new-seed/ticket.md", candidate.encode())
        reviews, _ = await _review_seeds(ctx, ticket, attempt=0, own=set(), prior={})
        assert len(reviews) == 1 and reviews[0].mechanical == "ticket lint failed"
    asyncio.run(scenario())
