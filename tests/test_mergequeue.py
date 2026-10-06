"""Direct tests of the dormant Phase 3 merge admission queue."""

import ast
import asyncio
import dataclasses
from pathlib import Path

import pytest

from chupa.mergequeue import MergeQueue, RED_STREAK_K, TreeHashMismatch, UnresolvedConflict
from tests.test_merge import merged_events, repo, reviewed
from tests.test_stages import STEM, agent, git, verdict


ROOT = Path(__file__).resolve().parents[1]


def import_closure(root: Path, overrides: dict[str, str] | None = None) -> set[str]:
    """Follow both package import idioms from the production CLI root."""
    overrides = overrides or {}
    pending = ["chupa.__main__"]
    seen = set()
    while pending:
        module = pending.pop()
        if module in seen:
            continue
        seen.add(module)
        path = root / (module.replace(".", "/") + ".py")
        if not path.is_file() and module not in overrides:
            continue
        tree = ast.parse(overrides.get(module, path.read_text()))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                pending.extend(a.name for a in node.names if a.name.startswith("chupa."))
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.module.startswith("chupa."):
                    pending.append(node.module)
                elif node.module == "chupa":
                    pending.extend(f"chupa.{a.name}" for a in node.names)
    return seen


def test_queue_is_dormant_in_transitive_production_import_closure():
    assert "chupa.mergequeue" not in import_closure(ROOT)
    main = (ROOT / "chupa" / "__main__.py").read_text()
    assert "chupa.mergequeue" in import_closure(ROOT, {"chupa.__main__": main + "\nimport chupa.mergequeue\n"})
    assert "chupa.mergequeue" in import_closure(ROOT, {"chupa.__main__": main + "\nfrom chupa import mergequeue\n"})
    merge = (ROOT / "chupa" / "merge.py").read_text()
    assert "chupa.merge" in import_closure(ROOT)
    assert "chupa.mergequeue" in import_closure(ROOT, {"chupa.merge": merge + "\nfrom chupa import mergequeue\n"})


def run(coro):
    return asyncio.run(coro)


def assert_refusal_clean(ctx, before):
    wt = ctx.worktree(STEM)
    assert git(wt, "rev-parse", "HEAD").strip() == before
    assert git(wt, "status", "--porcelain") == ""
    assert git(wt, "rev-parse", "--git-path", "rebase-merge").strip()
    assert not (wt / git(wt, "rev-parse", "--git-path", "rebase-merge").strip()).exists()
    assert not (wt / git(wt, "rev-parse", "--git-path", "rebase-apply").strip()).exists()
    assert not merged_events(ctx)


def conflict(ctx):
    wt = ctx.worktree(STEM)
    before = git(wt, "rev-parse", "HEAD").strip()
    (ctx.repo / "chupa" / "thing.py").write_text("main\n")
    git(ctx.repo, "commit", "-am", "main changes thing")
    return before


def test_undeclared_conflict_returns_typed_handoff_and_aborts(repo):
    ctx, ticket, attempt = reviewed(repo, [agent({"chupa/thing.py": "branch ok\n"}), verdict()])
    before = conflict(ctx)
    result = run(MergeQueue(ctx).admit(ticket, attempt=attempt))
    assert result.outcome == "unresolved_conflict"
    assert result.handoff == UnresolvedConflict(STEM, ("chupa/thing.py",))
    assert_refusal_clean(ctx, before)
    assert any(e.body.get("kind") == "merge_conflict_facts" and e.body["rung"] == "rework"
               for e in ctx.driver.journal.read())


def test_declared_union_selects_mechanical_rung_and_checks_rebased_tree(repo):
    cfg = repo / "config.yaml"
    cfg.write_text(cfg.read_text().replace("merge: {}", "merge:\n  strategies:\n"
                                     "    - {paths: [chupa/thing.py], strategy: union}"))
    git(repo, "commit", "-am", "declare append-only merge strategy")
    ctx, ticket, attempt = reviewed(repo, [agent({"chupa/thing.py": "branch ok\n"}), verdict()])
    conflict(ctx)
    result = run(MergeQueue(ctx).admit(ticket, attempt=attempt))
    assert result.outcome == "ok", result.findings
    assert (repo / "chupa" / "thing.py").read_text() == "main\nbranch ok\n"
    assert any(e.body.get("kind") == "merge_conflict_facts" and e.body["rung"] == "mechanical"
               and e.body["strategy_hits"] == ["chupa/thing.py"] for e in ctx.driver.journal.read())


def test_declared_non_append_only_path_refuses_mechanical_rung_and_hands_off(repo):
    cfg = repo / "config.yaml"
    cfg.write_text(cfg.read_text().replace("merge: {}", "merge:\n  strategies:\n"
                                     "    - {paths: [chupa/thing.py], strategy: union}"))
    (repo / "chupa" / "thing.py").write_text("base\n")
    git(repo, "commit", "-am", "base content and strategy")
    ctx, ticket, attempt = reviewed(repo, [agent({"chupa/thing.py": "branch ok\n"}), verdict()])
    before = conflict(ctx)
    result = run(MergeQueue(ctx).admit(ticket, attempt=attempt))
    assert result.outcome == "unresolved_conflict"
    assert result.handoff == UnresolvedConflict(STEM, ("chupa/thing.py",))
    assert_refusal_clean(ctx, before)


def test_declared_regenerator_selects_mechanical_rung(repo):
    cfg = repo / "config.yaml"
    cfg.write_text(cfg.read_text().replace("merge: {}", "merge:\n  strategies:\n"
                                     "    - {paths: [chupa/thing.py], strategy: regenerate,"
                                     " argv: [sed, -i, s/branch/regen/, chupa/thing.py]}"))
    git(repo, "commit", "-am", "declare generator")
    ctx, ticket, attempt = reviewed(repo, [agent({"chupa/thing.py": "branch ok\n"}), verdict()])
    ticket = dataclasses.replace(ticket, scope_fence=("chupa/other.py",))
    conflict(ctx)
    result = run(MergeQueue(ctx).admit(ticket, attempt=attempt))
    assert result.outcome == "ok", result.findings
    assert (repo / "chupa" / "thing.py").read_text() == "regen ok\n"


def test_both_resolution_rungs_refuse_a_nonconflict_rebase_error(repo):
    ctx, ticket, attempt = reviewed(repo, [agent({"chupa/thing.py": "ok\n"}), verdict()])
    before = git(ctx.worktree(STEM), "rev-parse", "HEAD").strip()
    (repo / "chupa" / "other.py").write_text("moved\n")
    git(repo, "commit", "-am", "main moves")
    ctx.git._env = {**ctx.git._env, "GIT_COMMITTER_NAME": ""}
    result = run(MergeQueue(ctx).admit(ticket, attempt=attempt))
    assert result.outcome == "gate_failed" and result.handoff is None
    assert_refusal_clean(ctx, before)


def test_post_rebase_scope_regate_refuses_and_restores_branch(repo):
    ctx, ticket, attempt = reviewed(repo, [agent({"chupa/thing.py": "ok\n"}), verdict()])
    before = git(ctx.worktree(STEM), "rev-parse", "HEAD").strip()
    ticket = dataclasses.replace(ticket, scope_fence=("chupa/other.py",))
    (repo / "chupa" / "other.py").write_text("moved\n")
    git(repo, "commit", "-am", "main moves")
    result = run(MergeQueue(ctx).admit(ticket, attempt=attempt))
    assert result.outcome == "gate_failed"
    assert any(f.code == "scope_fence" for f in result.findings)
    assert_refusal_clean(ctx, before)


def test_integration_verification_is_red_on_rebased_worktree_and_restores_head(repo):
    ctx, ticket, attempt = reviewed(repo, [agent({"chupa/thing.py": "ok\n"}), verdict()])
    ticket = dataclasses.replace(ticket, verification=(("grep", "-q", "main-marker", "chupa/other.py"),))
    before = git(ctx.worktree(STEM), "rev-parse", "HEAD").strip()
    (repo / "chupa" / "other.py").write_text("main-marker\n")
    git(repo, "commit", "-am", "main moves")
    # The command passes only in the rebased tree; the queue must admit it.
    result = run(MergeQueue(ctx).admit(ticket, attempt=attempt))
    assert result.outcome == "ok", result.findings
    assert result.artifact.reviewed_sha == before


def test_integration_red_counts_distinct_stems_and_pauses_at_three(repo):
    ctx, ticket, attempt = reviewed(repo, [agent({"chupa/thing.py": "ok\n"}), verdict()])
    ticket = dataclasses.replace(ticket, verification=(("grep", "-q", "missing", "chupa/thing.py"),))
    before = git(ctx.worktree(STEM), "rev-parse", "HEAD").strip()
    queue = MergeQueue(ctx)
    for _ in range(2):
        result = run(queue.admit(ticket, attempt=attempt))
        assert result.outcome == "gate_failed"
        assert_refusal_clean(ctx, before)
    assert queue._red == [STEM] and not queue.paused

    for name in ("second-ticket", "third-ticket"):
        source = repo / "tickets" / STEM
        target = repo / "tickets" / name
        target.mkdir()
        (target / "ticket.md").write_text((source / "ticket.md").read_text())
        git(repo, "add", f"tickets/{name}/ticket.md")
        git(repo, "commit", "-m", f"chupa({name}): ticket")
        wt = ctx.worktree(name)
        run(ctx.git.worktree_add(repo, wt, name, "main"))
        (wt / "chupa" / "thing.py").write_text("ok\n")
        git(wt, "commit", "-am", "work")
        head = git(wt, "rev-parse", "HEAD").strip()
        (target / "run.md").write_text((source / "run.md").read_text())
        (target / "review.md").write_text((source / "review.md").read_text().replace(before, head))
        git(repo, "add", f"tickets/{name}/run.md", f"tickets/{name}/review.md")
        git(repo, "commit", "-m", f"chupa({name}): run record and review")
        result = run(queue.admit(dataclasses.replace(ticket, stem=name), attempt=attempt))
        assert result.outcome == "gate_failed"
        assert git(wt, "rev-parse", "HEAD").strip() == head
        assert git(wt, "status", "--porcelain") == ""
        if name == "second-ticket":
            assert not queue.paused
    assert RED_STREAK_K == 3 and queue.paused
    assert run(queue.admit(ticket, attempt=attempt)).outcome == "paused"


def test_tree_hash_mismatch_escalates_without_merged_transition(repo, monkeypatch):
    ctx, ticket, attempt = reviewed(repo, [agent({"chupa/thing.py": "ok\n"}), verdict()])
    original = ctx.git.rev_parse

    async def wrong_tree(path, rev):
        value = await original(path, rev)
        return "0" * 40 if path == repo and rev == "HEAD^{tree}" else value

    monkeypatch.setattr(ctx.git, "rev_parse", wrong_tree)
    queue = MergeQueue(ctx)
    with pytest.raises(TreeHashMismatch):
        run(queue.admit(ticket, attempt=attempt))
    assert queue.paused
    assert not merged_events(ctx)
    assert any(e.body.get("kind") == "merge_tree_hash_mismatch" for e in ctx.driver.journal.read())
