"""Host checks through production Check and inline admission."""
import asyncio

import pytest

from chupa import merge, stages
from chupa.box import BOX_DIR, Box
from chupa.seams import ExecutableNotFound
from tests.test_mergequeue import ctx, host, ready, scripted
from tests.test_stages import SECRET


async def checked(ctx, ticket):
    slip = stages.PackingSlip(produced_by_spec_version=1, produced_at_sha="head", stem=ticket.stem,
                              branch=ticket.stem, outcome="ok", summary="work", run_record="run.md")
    return await stages.check(ctx, ticket, slip, attempt=0)


def test_triggered_entries_run_at_check(ctx, monkeypatch):
    async def run():
        ticket = await ready(ctx)
        ctx.config.review.mechanical = [host("always"), host("path", trigger=["chupa"])]
        calls = scripted(ctx, monkeypatch, [(0, "", "")] * 2)
        result = await checked(ctx, ticket)
        assert result.outcome == "ok" and [c[0][1] for c in calls] == ["always", "path"]
        assert [r.code for r in result.artifact.reports[-2:]] == ["always", "path"]
        assert (ctx.config.state_dir / f"spools/{ticket.stem}/0/check/host-02.txt").exists()
    asyncio.run(run())


def test_untriggered_entry_never_runs(ctx, monkeypatch):
    async def run():
        ticket = await ready(ctx, changes={"chupa/xy.py": "ok"}, fence=("chupa/xy.py",))
        ctx.config.review.mechanical = [host("skip", trigger=["chupa/x"])]
        calls = scripted(ctx, monkeypatch, [])
        result = await checked(ctx, ticket)
        assert result.outcome == "ok" and not calls
        assert "skip" not in [r.code for r in result.artifact.reports]
        assert not list((ctx.config.state_dir / f"spools/{ticket.stem}/0").rglob("host-*"))
    asyncio.run(run())


@pytest.mark.parametrize("severity", ["hard", "soft"])
def test_failure(ctx, monkeypatch, severity):
    async def run():
        ticket = await ready(ctx)
        ctx.config.review.mechanical = [host("bad", severity=severity)]
        scripted(ctx, monkeypatch, [(1, "bad", ""), (0, "", "")])
        result = await checked(ctx, ticket)
        assert result.outcome == ("gate_failed" if severity == "hard" else "ok")
        assert result.artifact.reports[-1].verdict == "fail" and result.findings[-1].code == "bad"
    asyncio.run(run())


def test_hard_failure_fails_check(ctx, monkeypatch):
    test_failure(ctx, monkeypatch, "hard")


def test_soft_failure_reported_and_passes(ctx, monkeypatch):
    test_failure(ctx, monkeypatch, "soft")


def test_base_red_entry_is_preexisting(ctx, monkeypatch):
    async def run():
        ticket = await ready(ctx, changes={"chupa/other.py": "outside"})
        ctx.config.review.mechanical = [host("base-red")]
        scripted(ctx, monkeypatch, [(1, "red", ""), (1, "red", "")])
        result = await checked(ctx, ticket)
        assert result.outcome == "gate_failed"
        report = result.artifact.reports[-1]
        assert report.verdict == "pass" and not report.findings
        assert [f.code for f in stages._prior_findings(ctx, ticket.stem, "check")] == ["scope_fence"]
        assert Box(ctx.config.state_dir / BOX_DIR, ctx.fs).messages()[0].outcome == "base_red"
    asyncio.run(run())


@pytest.mark.parametrize("failure", [TimeoutError(), ExecutableNotFound("host")])
def test_timeout_and_missing_executable_fail_closed(ctx, monkeypatch, failure):
    async def run():
        ticket = await ready(ctx)
        ctx.config.review.mechanical = [host("bad", argv=["host", SECRET])]
        calls = scripted(ctx, monkeypatch, [failure, (0, "", "")])
        result = await checked(ctx, ticket)
        assert result.outcome == "gate_failed" and "FAKE_KEY" not in calls[0][1]["env"]
        assert SECRET not in result.findings[-1].message
        assert SECRET not in (ctx.config.state_dir / f"spools/{ticket.stem}/0/check/host-01.txt").read_text()
    asyncio.run(run())


def test_inline_merge_reruns_triggered_hard_entries(ctx, monkeypatch):
    async def run():
        ticket = await ready(ctx)
        ctx.config.review.mechanical = [host("red"), host("soft", severity="soft"), host("skip", trigger=["other"])]
        calls = scripted(ctx, monkeypatch, [(1, "red", "")])
        before = await ctx.git.rev_parse(ctx.repo, "main")
        result = await merge.merge(ctx, ticket, attempt=0)
        assert result.outcome == "gate_failed" and [c[0][1] for c in calls] == ["red"]
        assert await ctx.git.rev_parse(ctx.repo, "main") == before
        assert (ctx.config.state_dir / f"spools/{ticket.stem}/0/merge/host-01.txt").exists()
    asyncio.run(run())
