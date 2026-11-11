import asyncio
import multiprocessing
from pathlib import Path

import pytest

from chupa.__main__ import main
from chupa.git import Git
from chupa.journal import EventType
from chupa.lockfile import Lockfile
from chupa.seams import SubprocessExec
from tests.integration.test_cli import ENV, Clock, journal, root, ticket, write
from tests.integration.test_git import commit_lock


def lint(root, *stems):
    def forbidden(checkout):
        pytest.fail("lint constructed the pipeline")

    return main(["lint", *stems], cwd=root, env=ENV, clock=Clock(), pipeline=forbidden)


def git(root, *argv):
    return asyncio.run(Git(SubprocessExec(), env=ENV, timeout=30, commit_lock=commit_lock(root / ".chupa/state"))._run(root, *argv))


def snapshot(root):
    return {p.relative_to(root): (p.read_bytes(), p.stat().st_mtime_ns) for p in root.rglob("*") if p.is_file()}


def test_lint_all_valid(root, capsys):
    # New human work may omit source and state: intake stamps them in memory.
    write(root, "first", ticket())
    write(root, "second", ticket("- first"))
    before = snapshot(root)
    assert lint(root) == 0
    assert capsys.readouterr().out == "lint: 2/2 tickets valid\n"
    assert not (root / ".chupa").exists()
    assert snapshot(root) == before


def test_lint_reports_findings_and_exits_1(root, capsys):
    write(root, "broken", "no frontmatter\n")
    write(root, "valid", ticket())
    assert lint(root) == 1
    lines = capsys.readouterr().out.splitlines()
    assert lines[0].startswith("tickets/broken/ticket.md: ticket.md has no frontmatter (")
    assert lines[0].endswith(")")
    assert lines[-1] == "lint: 1/2 tickets valid"


def test_lint_yaml_finding_is_one_line(root, capsys):
    write(root, "broken", "---\npriority: [\n---\n")
    assert lint(root) == 1
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 2
    assert lines[0].startswith("tickets/broken/ticket.md: frontmatter is not valid YAML:")
    assert lines[0].endswith("(fix the YAML between the `---` fences)")


@pytest.mark.parametrize("claim", ["source: seed", "source: box:suggestion", "state: merged", "state: rejected"])
@pytest.mark.parametrize("staged", [False, True])
def test_lint_applies_new_stem_claims(root, capsys, claim, staged):
    write(root, "claimed", ticket().replace("priority: P2", f"priority: P2\n{claim}"))
    if staged:
        git(root, "add", "--", "tickets/claimed/ticket.md")
    before = snapshot(root)
    assert lint(root, "claimed") == 1
    out = capsys.readouterr().out
    assert "new stem" in out and claim in out
    assert snapshot(root) == before


def test_lint_keeps_committed_claims(root, capsys):
    text = ticket().replace("priority: P2", "priority: P2\nsource: box:suggestion\nstate: draft")
    write(root, "established", text)
    git(root, "add", "--", "tickets/established/ticket.md")
    git(root, "commit", "-m", "established ticket")
    assert lint(root) == 0
    write(root, "established", text.replace("P2", "P1"))
    assert lint(root) == 0
    assert capsys.readouterr().out == "lint: 1/1 tickets valid\n" * 2


def test_lint_flags_bug_without_evidence(root, capsys):
    text = ticket().replace("kind: feature", "kind: bug")
    text += "\n## Regression\n```\nuv run python tests/repro.py\n```\n- carries: tests/repro.py\n"
    write(root, "fix-thing", text)
    assert lint(root) == 1
    assert "no evidence file" in capsys.readouterr().out
    evidence = root / "tickets/fix-thing/evidence/output.txt"
    evidence.parent.mkdir()
    evidence.write_text("observed failure\n")
    (root / ".gitignore").write_text(".chupa/\noutput.txt\n")
    assert lint(root) == 1
    assert "must not be gitignored" in capsys.readouterr().out
    (root / ".gitignore").write_text(".chupa/\n")
    evidence.unlink()
    evidence.symlink_to(root / "chupa/thing.py")
    assert lint(root) == 1
    evidence.unlink()
    evidence.write_text("observed failure\n")
    assert lint(root) == 0


def test_lint_skips_settled_tickets(root, capsys):
    for stem, state in (("merged", "merged"), ("noop", "already_satisfied"), ("rejected", "rejected")):
        write(root, stem, "old invalid grammar\n")
        journal(root).append(EventType.STATE_TRANSITION, {"to": state}, ticket=stem)
    write(root, "active", ticket())
    assert lint(root) == 0
    assert capsys.readouterr().out == "lint: 1/1 tickets valid\n"
    assert lint(root, "merged", "noop", "rejected") == 0
    assert capsys.readouterr().out == "lint: 0/0 tickets valid\n"
    journal(root).append(EventType.STATE_TRANSITION, {"to": "running"}, ticket="merged")
    assert lint(root) == 1
    assert "tickets/merged/ticket.md:" in capsys.readouterr().out


def test_lint_in_worktree_skips_main_settled_tickets(root, capsys):
    write(root, "merged", "old invalid grammar\n")
    write(root, "active", ticket().replace("priority: P2", "state: confirmed\nsource: human\npriority: P2"))
    git(root, "add", "--", "tickets")
    git(root, "commit", "-m", "tickets")
    journal(root).append(EventType.STATE_TRANSITION, {"to": "merged"}, ticket="merged")
    worktree = root.parent / "worktree"
    git(root, "worktree", "add", "--detach", str(worktree))
    before = snapshot(root)
    assert lint(worktree) == 0
    assert capsys.readouterr().out == "lint: 1/1 tickets valid\n"
    assert not (worktree / ".chupa").exists()
    assert snapshot(root) == before


def test_lint_named_stems_and_missing_stem(root, capsys):
    write(root, "valid", ticket())
    write(root, "broken", "invalid\n")
    assert lint(root, "valid") == 0
    assert capsys.readouterr().out == "lint: 1/1 tickets valid\n"
    for missing in ("missing", "../escape", "Bad_Stem", "retro"):
        assert lint(root, "valid", missing) == 2
        out = capsys.readouterr().out
        assert "no ticket file" in out
        assert out.endswith("lint: 1/2 tickets valid\n")
    for invalid in ("Bad_Stem", "retro"):
        write(root, invalid, ticket())
        assert lint(root, invalid) == 1
        assert "stem" in capsys.readouterr().out
    # An escaped existing file must never be read, even when otherwise valid.
    (root / "escape").mkdir()
    (root / "escape/ticket.md").write_text(ticket())
    assert lint(root, "../escape") == 2


def hold_lock(root, connection):
    lock = Lockfile(root / ".chupa/state", instance_id="other-process", clock=Clock())
    lock.acquire()
    try:
        connection.send("locked")
        connection.recv()
    finally:
        lock.release()


def test_lint_is_read_only_and_lock_free(root, capsys):
    write(root, "valid", ticket())
    journal(root).append(EventType.STATE_TRANSITION, {"to": "gate_failed"}, ticket="valid")
    context = multiprocessing.get_context("spawn")
    parent, child = context.Pipe()
    process = context.Process(target=hold_lock, args=(root, child))
    process.start()
    try:
        assert parent.poll(10) and parent.recv() == "locked"
        # Force a stale index stat entry, which a normal git status may refresh.
        (root / "chupa/thing.py").touch()
        before = snapshot(root)
        assert lint(root) == 0
        assert capsys.readouterr().out == "lint: 1/1 tickets valid\n"
        assert snapshot(root) == before
    finally:
        parent.send("release")
        process.join(10)
        if process.is_alive():
            process.terminate()
            process.join()
        parent.close()
        child.close()
    assert process.exitcode == 0


def test_lint_unreadable_tickets_directory(root, monkeypatch, capsys):
    write(root, "valid", ticket())
    original = Path.iterdir

    def unreadable(path):
        if path == root / "tickets":
            raise PermissionError("tickets directory unreadable")
        return original(path)

    monkeypatch.setattr(Path, "iterdir", unreadable)
    assert lint(root) == 2
    out = capsys.readouterr().out
    assert "tickets directory unreadable" in out and "restore" in out


def test_lint_unreadable_ticket(root, capsys):
    write(root, "invalid-encoding", "")
    (root / "tickets/invalid-encoding/ticket.md").write_bytes(b"\xff")
    assert lint(root) == 2
    assert "restore" in capsys.readouterr().out


def test_lint_flags_stuck_over_drain_ceiling(root, capsys):
    write(root, "budget", ticket().replace("- stuck: 20m", "- stuck: 91m"))
    assert lint(root, "budget") == 1
    out = capsys.readouterr().out
    assert "stuck 91m exceeds drain.max_ticket_minutes (90m)" in out
    assert "lower `- stuck:`" in out and "split" in out
    write(root, "budget", ticket().replace("- stuck: 20m", "- stuck: 90m"))
    assert lint(root, "budget") == 0
    assert capsys.readouterr().out == "lint: 1/1 tickets valid\n"
