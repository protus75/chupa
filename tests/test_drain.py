"""The `drain` scaffold verb (CHUPA_PLAN.md sections 9, 11.2, 18, 19.P1) against a temp checkout.

The stage-dispatch seam is scripted per stem; everything else -- lockfile, reconcile, intake, the tickets-dir
re-scan, the journal cap fold, the ceilings -- is the production path.
"""

import asyncio
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from chupa.__main__ import main
from chupa.drain import CEILING, HALT_SIGNAL, RETRY_CAP, cap_draws
from chupa.git import Git
from chupa.journal import EventType, Journal
from chupa.lockfile import Lockfile, LockHeld
from chupa.seams import LocalFileSystem, SubprocessExec
from chupa.tickets import intake
from tests.test_cli import CONFIG, ENV, PLAN, git_out, ticket, write

START = datetime(2026, 1, 1, tzinfo=UTC)


class Clock:
    """A fake clock a test (or a scripted stage) can advance."""

    def __init__(self) -> None:
        self.now = START

    def __call__(self) -> datetime:
        return self.now


class Script:
    """Scripted stage seam: each stem's terminals in order (default `merged`), plus per-stem side effects."""

    def __init__(self, outcomes: dict[str, list[str]] | None = None, hooks: dict | None = None) -> None:
        self.outcomes = {stem: list(seq) for stem, seq in (outcomes or {}).items()}
        self.hooks = hooks or {}
        self.calls: list[str] = []
        self.lock_held: list[bool] = []

    def __call__(self, checkout):
        async def dispatch(t):
            self.calls.append(t.stem)
            contender = Lockfile(checkout.config.state_dir, instance_id="contender", clock=checkout.clock)
            try:
                contender.acquire()
            except LockHeld:
                self.lock_held.append(True)
            else:
                contender.release()
                self.lock_held.append(False)
            if hook := self.hooks.get(t.stem):
                hook(checkout)
            seq = self.outcomes.get(t.stem, [])
            terminal = seq.pop(0) if seq else "merged"
            checkout.journal.append(EventType.STATE_TRANSITION, {"to": terminal, "stage": "review"}
                                    if terminal != "merged" else {"to": terminal}, ticket=t.stem)
            return terminal

        return dispatch


def make_root(tmp_path: Path, caps: str = "") -> Path:
    root = tmp_path / "repo"
    (root / "chupa").mkdir(parents=True)
    (root / "chupa" / "thing.py").write_text("")
    (root / "CHUPA_PLAN.md").write_text(PLAN)
    (root / "config.yaml").write_text(CONFIG + caps)
    (root / ".gitignore").write_text(".chupa/\n")
    git_out(root, "init", "-b", "main")
    git_out(root, "add", ".")
    git_out(root, "commit", "-m", "base")
    return root


@pytest.fixture
def root(tmp_path: Path) -> Path:
    return make_root(tmp_path)


def drain(root: Path, script: Script, clock: Clock | None = None) -> int:
    return main(["drain"], cwd=root, env=ENV, clock=clock or Clock(), pipeline=script)


def journal(root: Path) -> Journal:
    return Journal(root / ".chupa" / "state", Clock())


def confirmed(depends: str = "none", priority: str = "P2") -> str:
    """A ticket as the ticket-plane lane commits it: frontmatter already stamped, no intake needed."""
    return ticket(depends).replace("---\npriority: P2", f"---\nstate: confirmed\nsource: human\npriority: {priority}",
                                   1)


def commit_ticket(root: Path, stem: str, text: str) -> None:
    """A ticket-plane commit straight to main (a seeding ticket's output): no intake, no authoring event."""
    write(root, stem, text)
    git_out(root, "add", f"tickets/{stem}/ticket.md")
    git_out(root, "commit", "-m", f"chupa({stem}): ticket", "--only", "--", f"tickets/{stem}/ticket.md")


def intake_at(root: Path, stem: str, at: datetime) -> None:
    """Hand-author and intake one stem with the journal clock at `at` (its authoring-commit event)."""
    write(root, stem, ticket())
    clock = Clock()
    clock.now = at
    g = Git(SubprocessExec(), env=ENV, timeout=30.0)
    asyncio.run(intake(root, g, Journal(root / ".chupa" / "state", clock), LocalFileSystem()))


def retry_draws(root: Path, stem: str) -> int:
    return cap_draws(journal(root).read(), stem, RETRY_CAP)


def tos(root: Path, stem: str) -> list[str]:
    return [e.body["to"] for e in journal(root).read() if e.type == EventType.STATE_TRANSITION and e.ticket == stem]


# --- ordering -----------------------------------------------------------------------------------


def test_a_depends_edge_runs_parent_first(root, capsys):
    write(root, "aaa-child", ticket(depends="- zzz-parent"))
    write(root, "zzz-parent", ticket())
    script = Script()
    assert drain(root, script) == 0
    assert script.calls == ["zzz-parent", "aaa-child"]
    assert script.lock_held == [True, True]  # the one lock-holding process dispatches every ticket
    assert "aaa-child" in capsys.readouterr().out


def test_a_child_whose_parent_merges_mid_invocation_runs_in_the_same_invocation(root):
    # The child outranks its parent: only the mid-invocation merge can make it eligible.
    commit_ticket(root, "parent", confirmed(priority="P3"))
    commit_ticket(root, "child", confirmed(depends="- parent", priority="P0"))
    commit_ticket(root, "other", confirmed(priority="P1"))
    script = Script()
    assert drain(root, script) == 0
    assert script.calls == ["other", "parent", "child"]


def test_equal_priority_dispatches_older_authoring_event_first_and_no_event_last(root):
    # Stem order alone would give aaa-none, aaa-new, zzz-old: the age term must override it.
    intake_at(root, "zzz-old", START)
    intake_at(root, "aaa-new", START + timedelta(hours=1))
    commit_ticket(root, "aaa-none", confirmed())
    script = Script()
    assert drain(root, script) == 0
    assert script.calls == ["zzz-old", "aaa-new", "aaa-none"]


def test_priority_outranks_age(root):
    intake_at(root, "old-p3", START)
    commit_ticket(root, "new-p0", confirmed(priority="P0"))
    script = Script()
    assert drain(root, script) == 0
    assert script.calls == ["new-p0", "old-p3"]


# --- park, re-offer, and the journal-derived retry budget -------------------------------------------


def test_a_red_independent_ticket_parks_and_the_next_still_runs(tmp_path, capsys):
    root = make_root(tmp_path, "caps: {retry: 1}\n")
    write(root, "aaa-red", ticket())
    write(root, "bbb-green", ticket())

    def findings(checkout):
        (checkout.repo / "tickets" / "aaa-red" / "review.md").write_text("reject: thing() is wrong\n")

    script = Script({"aaa-red": ["gate_failed", "gate_failed"]}, {"aaa-red": findings})
    assert drain(root, script) == 0  # quiescence with a parked red still exits zero
    # Eligible work runs ahead of the re-offer; the one retry unit is then spent.
    assert script.calls == ["aaa-red", "bbb-green", "aaa-red"]
    out = capsys.readouterr().out
    parked = out.split("parked:\n", 1)[1].split("\n\n", 1)[0]
    assert "aaa-red: gate_failed at review; retry cap spent (1/1)" in parked
    assert "tickets/aaa-red/review.md" in parked  # the red is reported with where its findings live
    assert "bbb-green" not in parked


def test_red_then_green_on_its_reoffer_merges_and_unblocks_its_dependent_in_one_invocation(root):
    write(root, "flaky", ticket())
    write(root, "dependent", ticket(depends="- flaky"))
    write(root, "bystander", ticket())
    script = Script({"flaky": ["gate_failed", "merged"]})
    assert drain(root, script) == 0
    assert script.calls == ["bystander", "flaky", "flaky", "dependent"]
    assert retry_draws(root, "flaky") == 1
    assert tos(root, "flaky")[-1] == "merged" and tos(root, "dependent")[-1] == "merged"
    draw = next(e for e in journal(root).read() if e.type == EventType.CAP_CONSUMED)
    blob = git_out(root, "rev-parse", "HEAD:tickets/flaky/ticket.md").strip()
    assert draw.ticket == "flaky" and draw.body == {"cap": "retry", "ticket_sha": blob}
    # The draw precedes the re-offer's run.
    events = [(e.type, e.body.get("to")) for e in journal(root).read() if e.ticket == "flaky"]
    assert events.index((EventType.CAP_CONSUMED, None)) == events.index((EventType.STATE_TRANSITION, "running"), 2) - 1


def test_a_spent_retry_cap_stays_parked_and_is_never_reoffered(root, capsys):
    commit_ticket(root, "spent", confirmed())
    j = journal(root)
    j.append(EventType.STATE_TRANSITION, {"to": "running"}, ticket="spent")
    j.append(EventType.STATE_TRANSITION, {"to": "gate_failed", "stage": "check"}, ticket="spent")
    for _ in range(6):  # the shipped default retry cap
        j.append(EventType.CAP_CONSUMED, {"cap": "retry", "ticket_sha": "x"}, ticket="spent")
    script = Script()
    assert drain(root, script) == 0
    assert script.calls == []
    assert "spent: gate_failed at check; retry cap spent (6/6)" in capsys.readouterr().out


def test_a_retry_unit_drawn_in_one_invocation_stays_spent_in_the_next(tmp_path, capsys):
    root = make_root(tmp_path, "caps: {retry: 2}\n")
    write(root, "red", ticket())
    script = Script({"red": ["gate_failed"] * 3})
    assert drain(root, script) == 0
    assert script.calls == ["red"] * 3  # the first attempt plus both retry units
    assert retry_draws(root, "red") == 2
    capsys.readouterr()

    again = Script()
    assert drain(root, again) == 0
    assert again.calls == []  # budget re-derived from the journal: nothing carried in memory refills it
    assert "retry cap spent (2/2)" in capsys.readouterr().out


def test_the_budget_fold_counts_only_retry_named_draws(tmp_path):
    root = make_root(tmp_path, "caps: {retry: 3}\n")
    commit_ticket(root, "red", confirmed())
    j = journal(root)
    j.append(EventType.STATE_TRANSITION, {"to": "gate_failed", "stage": "review"}, ticket="red")
    for _ in range(2):
        j.append(EventType.CAP_CONSUMED, {"cap": "retry", "ticket_sha": "old"}, ticket="red")
    for _ in range(5):  # other caps in the vocabulary never perturb the retry budget
        j.append(EventType.CAP_CONSUMED, {"cap": "diagnosis", "ticket_sha": "old"}, ticket="red")
    j.append(EventType.CAP_CONSUMED, {"cap": "retry", "ticket_sha": "old"}, ticket="someone-else")
    script = Script({"red": ["gate_failed"]})
    assert drain(root, script) == 0
    assert script.calls == ["red"]  # exactly the one unit 3 - 2 leaves
    assert retry_draws(root, "red") == 3


# --- true quiescence: the tickets-dir re-scan ----------------------------------------------------------


def test_a_ticket_committed_during_the_invocation_runs_in_the_same_invocation(root):
    write(root, "seeder", ticket())

    def seed(checkout):
        commit_ticket(checkout.repo, "seeded", confirmed())

    script = Script(hooks={"seeder": seed})
    assert drain(root, script) == 0
    assert script.calls == ["seeder", "seeded"]


def test_an_uncommitted_ticket_file_is_not_eligible(root):
    write(root, "seeder", ticket())

    def author_only(checkout):
        write(checkout.repo, "loose", confirmed())  # authored, never committed to the ticket plane

    script = Script(hooks={"seeder": author_only})
    assert drain(root, script) == 0
    assert script.calls == ["seeder"]


# --- the safety envelope ----------------------------------------------------------------------------


def test_the_runtime_ceiling_stops_the_next_dispatch_and_exits_1(root, capsys):
    write(root, "aaa-first", ticket())
    write(root, "bbb-second", ticket())
    clock = Clock()

    def overrun(checkout):
        clock.now = START + timedelta(hours=13)  # past the shipped 12h, mid-stage

    script = Script(hooks={"aaa-first": overrun})
    assert drain(root, script, clock) == 1
    assert script.calls == ["aaa-first"]
    assert tos(root, "aaa-first") == ["running", "merged"]  # the in-flight stage reached its terminal
    assert tos(root, "bbb-second") == []
    out = capsys.readouterr().out
    assert CEILING in out and "HALTED" in out and "quiescent:" not in out
    assert "uv run python -m chupa drain" in out
    assert "bbb-second" in out.split("eligible, not admitted:\n", 1)[1].split("\n\n", 1)[0]
    halts = [e.body for e in journal(root).read() if e.type == EventType.SIGNAL
             and e.body.get("signal") == HALT_SIGNAL]
    assert halts == [{"signal": HALT_SIGNAL, "ceiling": CEILING, "hours": 12, "merged": ["aaa-first"]}]


def test_a_stuck_budget_over_the_per_ticket_ceiling_parks_at_dispatch(root, capsys):
    write(root, "too-long", ticket().replace("- stuck: 20m", "- stuck: 200m"))
    write(root, "fits", ticket())
    script = Script()
    assert drain(root, script) == 0
    assert script.calls == ["fits"]
    assert tos(root, "too-long") == []
    out = capsys.readouterr().out
    assert "too-long: `## Time budget` stuck 200m exceeds drain.max_ticket_minutes (90m)" in out
    assert "lower `- stuck:`" in out


# --- fail closed and exit codes ---------------------------------------------------------------------


def test_an_empty_queue_reports_and_exits_zero(root, capsys):
    script = Script()
    assert drain(root, script) == 0
    assert script.calls == []
    assert "nothing eligible" in capsys.readouterr().out


def test_a_depends_cycle_is_refused_with_a_paved_road(root, capsys):
    write(root, "aaa", confirmed(depends="- bbb"))
    write(root, "bbb", confirmed(depends="- aaa"))
    git_out(root, "add", "tickets")
    git_out(root, "commit", "-m", "cycle")
    script = Script()
    assert drain(root, script) == 2
    assert script.calls == []
    err = capsys.readouterr().err
    assert "cycle" in err and "drop the edge" in err


def test_drafts_never_run_and_are_listed(root, capsys):
    commit_ticket(root, "rough", confirmed().replace("state: confirmed", "state: draft"))
    script = Script()
    assert drain(root, script) == 0
    assert script.calls == []
    assert "rough" in capsys.readouterr().out.split("drafts awaiting confirm:\n", 1)[1]


def test_lock_contention_stops_the_drain_with_exit_2(root):
    write(root, "add-thing", ticket())
    holder = Lockfile(root / ".chupa" / "state", instance_id="other", clock=Clock())
    holder.acquire()
    try:
        script = Script()
        assert drain(root, script) == 2
    finally:
        holder.release()
    assert script.calls == []


def test_drain_reconciles_on_entry(root):
    write(root, "add-thing", ticket())
    journal(root).append(EventType.STATE_TRANSITION, {"to": "running"}, ticket="dead-run")
    assert drain(root, Script()) == 0
    assert tos(root, "dead-run") == ["running", "abandoned"]
