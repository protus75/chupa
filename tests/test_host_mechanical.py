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


def test_autofix_config_loading(ctx, tmp_path):
    import yaml
    from chupa.config import ConfigError, load_config

    raw = yaml.safe_load((ctx.repo / "config.yaml").read_text())
    raw["review"]["autofix"] = [{"code": "fix", "argv": ["fix"]}]
    path = tmp_path / "config.yaml"
    def load():
        path.write_text(yaml.safe_dump(raw))
        return load_config(path, cwd=tmp_path)
    assert load().review.autofix[0].argv == ["fix"]
    for entry in ({"code": "fix", "argv": []}, {"code": "fix", "argv": ["fix"], "extra": 1}):
        raw["review"]["autofix"] = [entry]
        with pytest.raises(ConfigError):
            load()


def test_autofix_commits_selected_files_and_evaluates_head(ctx, monkeypatch):
    from chupa.config import AutofixCommand
    from tests.test_mergequeue import commit

    async def run():
        ticket = await ready(ctx, changes={"chupa/thing.py": "before\n", "tickets/extra.txt": "ticket\n"},
                             fence=("chupa/thing.py", "tickets"))
        root = ctx.worktree(ticket.stem)
        (root / "chupa/other.py").unlink()
        await commit(ctx, root, ["chupa/other.py"], "delete")
        ctx.config.review.autofix = [AutofixCommand(code="fix", argv=["host", "fix"])]
        original = ctx.exec_.run
        calls = []
        async def execute(argv, **kw):
            if argv[0] == "host":
                calls.append(argv)
                (root / "chupa/thing.py").write_text("fixed\n")
                return 0, "", ""
            return await original(argv, **kw)
        monkeypatch.setattr(ctx.exec_, "run", execute)
        monkeypatch.setattr(stages, "_review_seeds", lambda *a, **kw: asyncio.sleep(0, result=([], [])))
        result = await checked(ctx, ticket)
        head = await ctx.git.rev_parse(ctx.repo, ticket.stem)
        assert calls == [["host", "fix", "chupa/thing.py"]]
        assert result.artifact.produced_at_sha == head
        assert "chupa/thing.py" in await ctx.git.diff_names(ctx.repo, "main", ticket.stem)
        assert (await ctx.git._run(root, "log", "-1", "--format=%s")).strip() == f"chupa({ticket.stem}): autofix"
        assert (await ctx.git._run(root, "show", "--format=", "--name-only", "HEAD")).strip() == "chupa/thing.py"
        assert result.artifact.reports[0].verdict == "pass"
    asyncio.run(run())


def test_autofix_no_change_and_already_satisfied(ctx, monkeypatch):
    from chupa.config import AutofixCommand
    async def run():
        ticket = await ready(ctx)
        root = ctx.worktree(ticket.stem)
        head = await ctx.git.rev_parse(ctx.repo, ticket.stem)
        (root / "chupa/thing.py").write_text("uncommitted\n")
        ctx.config.review.autofix = [AutofixCommand(code="fix", argv=["host", "fix"])]
        calls = scripted(ctx, monkeypatch, [(0, "", "")])
        await checked(ctx, ticket)
        assert len(calls) == 1 and await ctx.git.rev_parse(ctx.repo, ticket.stem) == head
        assert (root / "chupa/thing.py").read_text() == "uncommitted\n"
        slip = stages.PackingSlip(produced_by_spec_version=1, produced_at_sha=head, stem=ticket.stem,
                                  branch=ticket.stem, outcome="already_satisfied", summary="done", run_record="run.md")
        await stages.check(ctx, ticket, slip, attempt=1)
        assert len(calls) == 1
    asyncio.run(run())


def test_autofix_failure_restores_and_blocks_seeds(ctx, monkeypatch):
    from chupa.config import AutofixCommand
    from tests.test_mergequeue import commit
    async def run():
        ticket = await ready(ctx, fence=("chupa/thing.py", "tickets"))
        root = ctx.worktree(ticket.stem)
        path = root / "chupa/thing.py"
        path.chmod(0o755)
        await commit(ctx, root, ["chupa/thing.py"], "executable")
        head = await ctx.git.rev_parse(ctx.repo, ticket.stem)
        ctx.config.review.autofix = [AutofixCommand(code="bad", argv=["host", "bad"]),
                                     AutofixCommand(code="later", argv=["host", "later"])]
        original = ctx.exec_.run
        calls = []
        async def execute(argv, **kw):
            if argv[0] == "host":
                calls.append(argv)
                path.write_text("broken")
                path.chmod(0o644)
                return 1, "", "failed"
            return await original(argv, **kw)
        async def seeds(*args, **kwargs):
            pytest.fail("seed review ran")
        monkeypatch.setattr(ctx.exec_, "run", execute)
        monkeypatch.setattr(stages, "_review_seeds", seeds)
        result = await checked(ctx, ticket)
        assert result.outcome == "gate_failed" and any(f.code == "bad" for f in result.findings)
        assert len(calls) == 1 and await ctx.git.rev_parse(ctx.repo, ticket.stem) == head
        assert "chupa/thing.py" not in await ctx.git.status_porcelain(root)
        assert path.stat().st_mode & 0o111
    asyncio.run(run())


def test_autofix_skips_when_no_files(ctx, monkeypatch):
    from chupa.config import AutofixCommand
    from tests.test_mergequeue import commit
    async def run():
        ticket = await ready(ctx)
        root = ctx.worktree(ticket.stem)
        (root / "chupa/thing.py").unlink()
        await commit(ctx, root, ["chupa/thing.py"], "delete")
        ctx.config.review.autofix = [AutofixCommand(code="fix", argv=["host", "fix"])]
        calls = scripted(ctx, monkeypatch, [])
        await checked(ctx, ticket)
        assert not calls
    asyncio.run(run())
