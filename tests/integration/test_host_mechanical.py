"""Host checks through production Check and inline admission."""

import asyncio

import pytest

from chupa import merge, stages
from chupa.box import BOX_DIR, Box
from chupa.seams import ExecutableNotFound
from tests.integration.test_mergequeue import approve, commit, ctx, host, ready, scripted
from tests.integration.test_stages import SECRET


async def checked(ctx, ticket):
    slip = stages.PackingSlip(produced_by_spec_version=1, produced_at_sha="head", stem=ticket.stem, branch=ticket.stem, outcome="ok", summary="work", run_record="run.md")
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
        ctx.fs.write(ctx.repo / "chupa/other.py", b"main moved\n")
        await commit(ctx, ctx.repo, ["chupa/other.py"])
        ctx.config.review.mechanical = [host("red"), host("soft", severity="soft"), host("skip", trigger=["other"])]
        calls = scripted(ctx, monkeypatch, [(1, "red", "")])
        before = await ctx.git.rev_parse(ctx.repo, "main")
        result = await merge.merge(ctx, ticket, attempt=0)
        assert result.outcome == "gate_failed" and [c[0][1] for c in calls] == ["red"]
        assert await ctx.git.rev_parse(ctx.repo, "main") == before
        assert (ctx.config.state_dir / f"spools/{ticket.stem}/0/merge/host-01.txt").exists()

    asyncio.run(run())


@pytest.mark.parametrize("stale", [False, True])
def test_inline_merge_skips_unchanged_code(ctx, monkeypatch, stale):
    async def run():
        ticket = await ready(ctx, verification=(("host", "verify"),))
        if stale:
            await approve(ctx, ticket, sha="older")
        ctx.config.review.mechanical = [host("check")]
        calls = scripted(ctx, monkeypatch, [])
        result = await merge.merge(ctx, ticket, attempt=0)
        assert not calls
        assert result.outcome == ("gate_failed" if stale else "ok")
        if stale:
            assert any(f.code == "correctness_review" for f in result.findings)
        assert not list((ctx.config.state_dir / f"spools/{ticket.stem}/0/merge").glob("*"))

    asyncio.run(run())


def test_autofix_config_loading(ctx, tmp_path):
    import yaml

    from chupa.config import ConfigError, load_config

    raw = yaml.safe_load((ctx.repo / "config.yaml").read_text())
    raw["review"]["autofix"] = [{"code": "fix", "argv": ["fix"], "files": ["*.py"]}]
    path = tmp_path / "config.yaml"

    def load():
        path.write_text(yaml.safe_dump(raw))
        return load_config(path, cwd=tmp_path)

    raw["review"]["mechanical"] = [{"code": "tests", "argv": ["pytest"], "trigger": "always", "severity": "hard", "results": "results.json"}]
    assert load().review.mechanical[0].results == "results.json"
    assert load().review.autofix[0].argv == ["fix"]
    for entry in ({"code": "fix", "argv": [], "files": ["*.py"]}, {"code": "fix", "argv": ["fix"], "files": ["*.py"], "extra": 1}):
        raw["review"]["autofix"] = [entry]
        with pytest.raises(ConfigError):
            load()

    for entry in ({"code": "fix", "argv": ["fix"]}, {"code": "fix", "argv": ["fix"], "files": []}):
        raw["review"]["autofix"] = [entry]
        with pytest.raises(ConfigError) as exc:
            load()
        assert exc.value.key == "review.autofix.0.files"


def test_autofix_commits_selected_files_and_evaluates_head(ctx, monkeypatch):
    from chupa.config import AutofixCommand
    from tests.integration.test_mergequeue import commit

    async def run():
        ticket = await ready(ctx, changes={"chupa/thing.py": "before\n", "tickets/extra.txt": "ticket\n"}, fence=("chupa/thing.py", "tickets"))
        root = ctx.worktree(ticket.stem)
        (root / "chupa/other.py").unlink()
        await commit(ctx, root, ["chupa/other.py"], "delete")
        ctx.config.review.autofix = [AutofixCommand(code="fix", argv=["host", "fix"], files=["*.py"])]
        original = ctx.exec_.run
        calls = []

        async def execute(argv, **kw):
            if argv[0] == "host":
                calls.append(argv)
                (root / "chupa/thing.py").write_text("fixed\n")
                return 0, "", ""
            return await original(argv, **kw)

        monkeypatch.setattr(ctx.exec_, "run", execute)
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
        ctx.config.review.autofix = [AutofixCommand(code="fix", argv=["host", "fix"], files=["*.py"])]
        calls = scripted(ctx, monkeypatch, [(0, "", "")])
        await checked(ctx, ticket)
        assert len(calls) == 1 and await ctx.git.rev_parse(ctx.repo, ticket.stem) == head
        assert (root / "chupa/thing.py").read_text() == "uncommitted\n"
        slip = stages.PackingSlip(produced_by_spec_version=1, produced_at_sha=head, stem=ticket.stem, branch=ticket.stem, outcome="already_satisfied", summary="done", run_record="run.md")
        await stages.check(ctx, ticket, slip, attempt=1)
        assert len(calls) == 1

    asyncio.run(run())


def test_autofix_failure_restores_and_blocks_check(ctx, monkeypatch):
    from chupa.config import AutofixCommand
    from tests.integration.test_mergequeue import commit

    async def run():
        ticket = await ready(ctx, fence=("chupa/thing.py", "tickets"))
        root = ctx.worktree(ticket.stem)
        path = root / "chupa/thing.py"
        path.chmod(0o755)
        await commit(ctx, root, ["chupa/thing.py"], "executable")
        head = await ctx.git.rev_parse(ctx.repo, ticket.stem)
        ctx.config.review.autofix = [AutofixCommand(code="bad", argv=["host", "bad"], files=["*.py"]), AutofixCommand(code="later", argv=["host", "later"], files=["*.py"])]
        original = ctx.exec_.run
        calls = []

        async def execute(argv, **kw):
            if argv[0] == "host":
                calls.append(argv)
                path.write_text("broken")
                path.chmod(0o644)
                return 1, "", "failed"
            return await original(argv, **kw)

        monkeypatch.setattr(ctx.exec_, "run", execute)
        result = await checked(ctx, ticket)
        assert result.outcome == "gate_failed" and any(f.code == "bad" for f in result.findings)
        assert len(calls) == 1 and await ctx.git.rev_parse(ctx.repo, ticket.stem) == head
        assert "chupa/thing.py" not in await ctx.git.status_porcelain(root)
        assert path.stat().st_mode & 0o111

    asyncio.run(run())


def test_autofix_skips_when_no_files(ctx, monkeypatch):
    from chupa.config import AutofixCommand
    from tests.integration.test_mergequeue import commit

    async def run():
        ticket = await ready(ctx)
        root = ctx.worktree(ticket.stem)
        (root / "chupa/thing.py").unlink()
        await commit(ctx, root, ["chupa/thing.py"], "delete")
        ctx.config.review.autofix = [AutofixCommand(code="fix", argv=["host", "fix"], files=["*.py"])]
        calls = scripted(ctx, monkeypatch, [])
        await checked(ctx, ticket)
        assert not calls

    asyncio.run(run())


@pytest.mark.parametrize("fail", [False, True])
def test_autofix_selection_and_union(ctx, monkeypatch, fail):
    from chupa.config import AutofixCommand

    async def run():
        changes = {"a.py": "python\n", "config.yaml": "yaml\n", ".gitignore": "ignore\n"}
        ticket = await ready(ctx, changes=changes, fence=tuple(changes))
        root = ctx.worktree(ticket.stem)
        head = await ctx.git.rev_parse(ctx.repo, ticket.stem)
        ctx.config.review.autofix = [
            AutofixCommand(code="py", argv=["host", "py"], files=["*.py"]),
            AutofixCommand(code="yaml", argv=["host", "yaml"], files=["*.yaml"]),
        ]
        original = ctx.exec_.run
        calls = []

        async def execute(argv, **kw):
            if argv[0] == "host":
                calls.append(list(argv))
                (root / argv[-1]).write_text("fixed\n")
                return (1 if fail and argv[1] == "yaml" else 0), "", ""
            return await original(argv, **kw)

        monkeypatch.setattr(ctx.exec_, "run", execute)
        result = await checked(ctx, ticket)
        assert calls == [["host", "py", "a.py"], ["host", "yaml", "config.yaml"]]
        if fail:
            assert result.outcome == "gate_failed"
            assert await ctx.git.rev_parse(ctx.repo, ticket.stem) == head
            assert all((root / path).read_text() == data for path, data in changes.items())
        else:
            assert result.outcome == "ok"
            assert (await ctx.git._run(root, "log", "-1", "--format=%s")).strip() == f"chupa({ticket.stem}): autofix"
            assert set((await ctx.git._run(root, "show", "--format=", "--name-only", "HEAD")).split()) == {"a.py", "config.yaml"}

    asyncio.run(run())


def test_autofix_skips_unmatched_files(ctx, monkeypatch):
    from chupa.config import AutofixCommand

    async def run():
        ticket = await ready(ctx, changes={"config.yaml": "changed\n"}, fence=("config.yaml",))
        ctx.config.review.autofix = [AutofixCommand(code="py", argv=["host", "py"], files=["*.py"])]
        calls = scripted(ctx, monkeypatch, [])
        result = await checked(ctx, ticket)
        assert result.outcome == "ok" and not calls

    asyncio.run(run())


def results_script(ctx, monkeypatch, runs):
    import json

    original = ctx.exec_.run
    calls = []

    async def execute(argv, **kw):
        if argv[0] != "host":
            return await original(argv, **kw)
        calls.append(kw["cwd"])
        rc, outcomes = runs.pop(0)
        if outcomes is not None:
            (kw["cwd"] / "results.json").write_text(json.dumps({"schema_version": 1, "tests": outcomes}))
        return rc, "", ""

    monkeypatch.setattr(ctx.exec_, "run", execute)
    return calls


def test_results_detection_and_replay(ctx, monkeypatch):
    async def run():
        test = "tests/test_a.py::test_x"
        ticket = await ready(ctx)
        ctx.config.review.mechanical = [host("tests").model_copy(update={"results": "results.json"})]
        runs = [(1, {test: "failed"}), (0, {test: "passed"})] * 2
        results_script(ctx, monkeypatch, runs)
        for _ in range(2):
            assert (await checked(ctx, ticket)).outcome == "ok"
        assert len([e for e in ctx.driver.journal.read() if e.body.get("kind") == "flake_detected"]) == 1
        assert len(Box(ctx.config.state_dir / BOX_DIR, ctx.fs).messages()) == 1
        assert (ctx.config.state_dir / f"spools/{ticket.stem}/0/check/host-01-rerun.txt").exists()

    asyncio.run(run())


@pytest.mark.parametrize("edited,second,expected", [(True, "passed", "gate_failed"), (False, "failed", "gate_failed")])
def test_results_block_edited_flake_and_real_failure(ctx, monkeypatch, edited, second, expected):
    async def run():
        test = "tests/test_a.py::test_x"
        ticket = await ready(ctx, changes={"tests/test_a.py": "changed"} if edited else None, fence=("tests/test_a.py",) if edited else ("chupa/thing.py",))
        ctx.config.review.mechanical = [host("tests").model_copy(update={"results": "results.json"})]
        results_script(ctx, monkeypatch, [(1, {test: "failed"}), (0 if second == "passed" else 1, {test: second}), (0, {})])
        result = await checked(ctx, ticket)
        assert result.outcome == expected and any(test in f.message for f in result.findings)
        assert not any(e.body.get("kind") == "flake_detected" for e in ctx.driver.journal.read())

    asyncio.run(run())


def test_results_quarantine_release_and_reflake(ctx, monkeypatch):
    from chupa.box import Resolution
    from chupa.daemon import flake_detection, storm_producer
    from chupa.journal import EventType

    async def run():
        test = "tests/test_a.py::test_x"
        ticket = await ready(ctx)
        ctx.config.review.mechanical = [host("tests").model_copy(update={"results": "results.json"})]
        box = storm_producer(root=ctx.config.state_dir / BOX_DIR, fs=ctx.fs, journal=ctx.driver.journal, clock=ctx.driver.clock)
        flake = flake_detection(journal=ctx.driver.journal, box=box, config=ctx.config, escalate=lambda _: None)
        runs = [(1, {test: "failed"}), (0, {test: "passed"}), (1, {test: "failed"}), (1, {test: "failed"}), (0, {test: "passed"}), (0, {test: "passed"}), (1, {test: "failed"}), (0, {test: "passed"})]
        results_script(ctx, monkeypatch, runs)
        assert (await checked(ctx, ticket)).outcome == "ok"
        identity = next(iter(flake.quarantine().active.values()))
        assert (await checked(ctx, ticket)).outcome == "ok"
        box.resolve(identity.box_id, Resolution(kind="ticket", link="fix-x"))
        assert (await checked(ctx, ticket)).outcome == "ok" and test in flake.quarantine().tests
        ctx.driver.journal.append(EventType.STATE_TRANSITION, {"to": "merged"}, ticket="fix-x")
        assert (await checked(ctx, ticket)).outcome == "ok" and test not in flake.quarantine().tests
        assert (await checked(ctx, ticket)).outcome == "ok"
        assert test in flake.quarantine().tests and len(box.messages()) == 2
        assert identity.box_id not in flake.quarantine().active

    asyncio.run(run())


@pytest.mark.parametrize("runs", [[(0, None), (0, {})], [(1, {"a": "failed"}), (0, None), (0, {})], [(1, {"a": "failed"}), (1, {"a": "passed"}), (0, {})]])
def test_results_fail_closed(ctx, monkeypatch, runs):
    async def run():
        ticket = await ready(ctx)
        ctx.config.review.mechanical = [host("tests").model_copy(update={"results": "results.json"})]
        missing = runs[0][1] is None or runs[1][1] is None
        results_script(ctx, monkeypatch, runs)
        result = await checked(ctx, ticket)
        assert result.outcome == "gate_failed"
        if missing:
            assert any("results.json" in f.message for f in result.findings)

    asyncio.run(run())


@pytest.mark.parametrize("edited,cap", [(True, False), (False, True)])
def test_results_edited_quarantine_and_cap(ctx, monkeypatch, edited, cap):
    from chupa.daemon import flake_detection, storm_producer
    from chupa.flake import RerunEvidence

    async def run():
        test = "tests/test_a.py::test_x"
        ticket = await ready(ctx, changes={"tests/test_a.py": "changed"} if edited else None, fence=("tests/test_a.py",) if edited else ("chupa/thing.py",))
        ctx.config.review.mechanical = [host("tests").model_copy(update={"results": "results.json"})]
        ctx.config.caps.quarantine = 1
        box = storm_producer(root=ctx.config.state_dir / BOX_DIR, fs=ctx.fs, journal=ctx.driver.journal, clock=ctx.driver.clock)
        flake = flake_detection(journal=ctx.driver.journal, box=box, config=ctx.config, escalate=lambda _: None)
        existing = "other" if cap else test
        flake.detect(test_id=existing, evidence=RerunEvidence(existing, "fail", "pass", True, True, True), summary="existing", reason="existing", occurrence_id="existing")
        second = "passed" if cap else "failed"
        results_script(ctx, monkeypatch, [(1, {test: "failed"}), (0 if cap else 1, {test: second}), (0, {})])
        result = await checked(ctx, ticket)
        assert result.outcome == "gate_failed" and any(test in f.message for f in result.findings)
        if cap:
            assert any("quarantine-cap crossed" in f.message for f in result.findings)
            assert test not in flake.quarantine().tests

    asyncio.run(run())


@pytest.mark.parametrize("deletion,covered,expected", [(False, 3, "gate_failed"), (False, 2, "ok"), (False, 9, "ok"), (True, 5, "gate_failed"), (True, 2, "ok")])
def test_coverage_changed_lines(ctx, monkeypatch, deletion, covered, expected):
    import json

    from tests.integration.test_mergequeue import commit

    async def run():
        test = "tests/test_a.py::test_x"
        original_lines = [f"line {i}\n" for i in range(1, 11)]
        ctx.fs.write(ctx.repo / "pkg/m.py", "".join(original_lines).encode())
        await commit(ctx, ctx.repo, ["pkg/m.py"], "base code")
        changed = original_lines.copy()
        if deletion:
            del changed[4]
        else:
            changed[2] = "edited\n"
        ticket = await ready(ctx, changes={"pkg/m.py": "".join(changed)}, fence=("pkg/m.py",))
        ctx.config.review.mechanical = [host("tests").model_copy(update={"results": "results.json", "coverage": "coverage.json"})]
        original = ctx.exec_.run
        calls = 0

        async def execute(argv, **kw):
            nonlocal calls
            if argv[0] != "host":
                return await original(argv, **kw)
            calls += 1
            outcomes = {test: "failed" if calls == 1 else "passed"}
            (kw["cwd"] / "results.json").write_text(json.dumps({"schema_version": 1, "tests": outcomes}))
            (kw["cwd"] / "coverage.json").write_text(json.dumps({"files": {"pkg/m.py": {"contexts": {str(covered): [test + "|run"]}}}}))
            return (1 if calls == 1 else 0), "", ""

        monkeypatch.setattr(ctx.exec_, "run", execute)
        result = await checked(ctx, ticket)
        assert result.outcome == expected
        detected = [e for e in ctx.driver.journal.read() if e.body.get("kind") == "flake_detected"]
        assert bool(detected) == (expected == "ok")
        if expected == "gate_failed":
            assert any(test in f.message for f in result.findings)

    asyncio.run(run())


@pytest.mark.parametrize("coverage,flaky,expected", [(None, True, "gate_failed"), ({"files": {"x": {"contexts": {"1": [""]}}}}, True, "gate_failed"), (None, False, "ok")])
def test_coverage_fail_closed(ctx, monkeypatch, coverage, flaky, expected):
    import json

    async def run():
        test = "tests/test_a.py::test_x"
        ticket = await ready(ctx)
        ctx.config.review.mechanical = [host("tests").model_copy(update={"results": "results.json", "coverage": "coverage.json"})]
        original = ctx.exec_.run
        calls = 0

        async def execute(argv, **kw):
            nonlocal calls
            if argv[0] != "host":
                return await original(argv, **kw)
            calls += 1
            (kw["cwd"] / "results.json").write_text(json.dumps({"schema_version": 1, "tests": {test: "failed" if flaky and calls == 1 else "passed"}}))
            if coverage is not None:
                (kw["cwd"] / "coverage.json").write_text(json.dumps(coverage))
            return (1 if flaky and calls == 1 else 0), "", ""

        monkeypatch.setattr(ctx.exec_, "run", execute)
        result = await checked(ctx, ticket)
        assert result.outcome == expected
        assert not any(e.body.get("kind") == "flake_detected" for e in ctx.driver.journal.read())
        if flaky:
            assert any("coverage.json" in f.message for f in result.findings)

    asyncio.run(run())


def test_coverage_requires_results(ctx, tmp_path):
    import yaml

    from chupa.config import ConfigError, load_config

    raw = yaml.safe_load((ctx.repo / "config.yaml").read_text())
    raw["review"]["mechanical"] = [{"code": "tests", "argv": ["pytest"], "trigger": "always", "severity": "hard", "coverage": "coverage.json"}]
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(raw))
    with pytest.raises(ConfigError) as exc:
        load_config(path, cwd=tmp_path)
    assert exc.value.key == "review.mechanical.0.coverage"
