import asyncio
from pathlib import Path

from chupa.git import Git
from chupa.journal import EventType, Journal, run_seq
from chupa.reconcile import reconcile
from chupa.seams import SubprocessExec
from chupa.status import last_states
from tests.test_cli import ENV, Clock, Stages, cli, git_out, journal, root, ticket, write  # noqa: F401

STATE = Path(".chupa") / "state"


def git() -> Git:
    return Git(SubprocessExec(), env=ENV, timeout=30.0)


def orphan_worktree(root: Path, stem: str) -> Path:
    """What an interrupted run leaves: its branch checked out in a worktree under the worktree root."""
    path = root / STATE / "worktrees" / stem
    path.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(git().worktree_add(root, path, stem, "main"))
    (path / "half-done.py").write_text("")  # uncommitted work the dead run never finished
    return path


def reap(root: Path) -> list[str]:
    return asyncio.run(reconcile(journal(root), git(), root, root / STATE / "worktrees"))


def test_running_with_no_terminal_is_reaped_to_abandoned_on_the_next_run(root):
    write(root, "add-thing", ticket())
    journal(root).append(EventType.STATE_TRANSITION, {"to": "running"}, ticket="dead-run")
    path = orphan_worktree(root, "dead-run")
    stages = Stages()
    assert cli(root, "run", "add-thing", stages=stages) == 0
    events = journal(root).read()
    transitions = [(e.ticket, e.body["to"]) for e in events if e.type == EventType.STATE_TRANSITION]
    # Reaped BEFORE the next run's own dispatch.
    assert transitions.index(("dead-run", "abandoned")) < transitions.index(("add-thing", "running"))
    assert last_states(events)["dead-run"] == "abandoned"
    assert run_seq(events, "dead-run") == 1  # the reap is a terminal: a re-run takes a fresh sequence
    assert not path.exists()
    assert str(path) not in git_out(root, "worktree", "list")


def test_an_open_effect_intent_is_an_orphan(root):
    j = journal(root)
    j.append(EventType.EFFECT_INTENT, {}, ticket="dead-run", key="dead-run/1/implement")
    path = orphan_worktree(root, "dead-run")
    assert reap(root) == ["dead-run"]
    assert last_states(j.read()) == {"dead-run": "abandoned"}
    assert not path.exists()


def test_reconcile_is_idempotent(root):
    j = journal(root)
    j.append(EventType.STATE_TRANSITION, {"to": "running"}, ticket="dead-run")
    j.append(EventType.EFFECT_INTENT, {}, ticket="dead-run", key="dead-run/0/implement")
    assert reap(root) == ["dead-run"]
    assert reap(root) == []
    assert run_seq(j.read(), "dead-run") == 1


def test_a_clean_journal_is_a_no_op(root):
    j = journal(root)
    j.append(EventType.STATE_TRANSITION, {"to": "running"}, ticket="done")
    j.append(EventType.EFFECT_INTENT, {}, ticket="done", key="done/0/implement")
    j.append(EventType.EFFECT_COMPLETION, {"result": "ok"}, ticket="done", key="done/0/implement")
    j.append(EventType.STATE_TRANSITION, {"to": "merged"}, ticket="done")
    # A run that crashed mid-effect but still journaled its terminal is history, not an orphan.
    j.append(EventType.STATE_TRANSITION, {"to": "running"}, ticket="red")
    j.append(EventType.EFFECT_INTENT, {}, ticket="red", key="red/0/implement")
    j.append(EventType.STATE_TRANSITION, {"to": "infra_error", "stage": "implement"}, ticket="red")
    left = orphan_worktree(root, "red")  # a non-ok terminal's worktree stays for the operator
    before = j.read()
    assert reap(root) == []
    assert j.read() == before
    assert left.exists()


def test_an_empty_journal_is_a_no_op(root):
    assert reap(root) == []
    assert journal(root).read() == []


def test_reap_without_a_worktree_still_journals_abandoned(root):
    j = journal(root)
    j.append(EventType.STATE_TRANSITION, {"to": "running"}, ticket="dead-run")
    assert reap(root) == ["dead-run"]
    assert last_states(j.read()) == {"dead-run": "abandoned"}


def test_a_reaped_stem_reruns(root):
    write(root, "add-thing", ticket())
    assert cli(root, "run", "add-thing", stages=Stages("gate_failed")) == 1
    Journal(root / STATE, Clock()).append(EventType.STATE_TRANSITION, {"to": "running"}, ticket="add-thing")
    stages = Stages()
    assert cli(root, "run", "add-thing", stages=stages) == 0
    assert stages.calls == ["add-thing"]
    assert last_states(journal(root).read())["add-thing"] == "merged"
