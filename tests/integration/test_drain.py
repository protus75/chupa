"""The `drain` scaffold verb (CHUPA_PLAN.md sections 9, 11.2, 18, 19.P1) against a temp checkout.

The stage-dispatch seam is scripted per stem; everything else -- lockfile, reconcile, intake, the tickets-dir
re-scan, the journal cap fold, the ceilings -- is the production path.
"""

import asyncio
import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from chupa.__main__ import build_control, main
from chupa.box import Box
from chupa.caps import draws
from chupa.drain import CEILING, HALT_SIGNAL
from chupa.git import Git
from chupa.journal import EventType, Journal
from chupa.lockfile import Lockfile, LockHeld
from chupa.seams import LocalFileSystem, SubprocessExec
from chupa.tickets import intake
from tests.integration.test_cli import CONFIG, ENV, PLAN, git_out, ticket, with_retro_driver, write
from tests.integration.test_git import commit_lock
from tests.integration.test_merge import repo as admission_repo
from tests.integration.test_stages import adopt_conduct
from tests.integration.test_terminal import repo as rework_repo


def test_bootstrap_never_supervised_holds(admission_repo, monkeypatch):
    from tests.integration.test_merge import test_bootstrap_pipeline_keeps_inline_admission

    test_bootstrap_pipeline_keeps_inline_admission(admission_repo, monkeypatch, "drain")


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
            contender = Lockfile(checkout.config.state_dir, verb="drain", instance_id="contender", clock=checkout.clock)
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
            checkout.journal.append(EventType.STATE_TRANSITION, {"to": terminal, "stage": "review"} if terminal != "merged" else {"to": terminal}, ticket=t.stem)
            return terminal

        return with_retro_driver(checkout, dispatch)


def make_root(tmp_path: Path, caps: str = "") -> Path:
    root = tmp_path / "repo"
    (root / "chupa").mkdir(parents=True)
    (root / "chupa" / "thing.py").write_text("")
    (root / "CHUPA_PLAN.md").write_text(PLAN)
    (root / "config.yaml").write_text(CONFIG + caps)
    (root / ".gitignore").write_text(".chupa/\n")
    adopt_conduct(root)
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
    return ticket(depends).replace("---\npriority: P2", f"---\nstate: confirmed\nsource: human\npriority: {priority}", 1)


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
    g = Git(SubprocessExec(), env=ENV, timeout=30.0, commit_lock=commit_lock(root / ".chupa/state"))
    asyncio.run(intake(root, g, Journal(root / ".chupa" / "state", clock), LocalFileSystem()))


def retry_draws(root: Path, stem: str) -> int:
    return draws(journal(root).read(), stem, "retry")


def tos(root: Path, stem: str) -> list[str]:
    return [e.body["to"] for e in journal(root).read() if e.type == EventType.STATE_TRANSITION and e.ticket == stem]


def test_already_satisfied_settles_without_diagnosis(rework_repo):
    from chupa import runner
    from chupa.llm import FakeLLM
    from chupa.status import reject_queue
    from tests.integration.test_stages import STEM, agent
    from tests.integration.test_terminal import author, clock

    repo = rework_repo
    (repo / "chupa/thing.py").write_text("ok base\n")
    git = Git(SubprocessExec(), env=ENV, timeout=30, commit_lock=commit_lock(repo / ".chupa/state"))

    async def green_base():
        await git.add(repo, ["chupa/thing.py"])
        await git.commit(repo, "green base", only=["chupa/thing.py"])

    asyncio.run(green_base())
    author(repo)
    llm = FakeLLM([agent({}, outcome="already_satisfied")])
    writers = []

    def bind(checkout):
        writer = runner.bind(checkout, llm)
        writers.append(writer)
        return writer

    assert main(["drain"], cwd=repo, env=ENV, clock=clock, pipeline=bind) == 0
    assert [r.surface for r in llm.requests] == ["implement"]
    events = Journal(repo / ".chupa/state", clock).read()
    history = [e for e in events if e.ticket == STEM]
    assert [e.body for e in history if e.type == EventType.STATE_TRANSITION][-1] == {"to": "already_satisfied", "stage": "check", "reason": "already_satisfied"}
    assert not any(e.type == EventType.CAP_CONSUMED for e in history)
    assert not any("routed" in e.body or "dispatch" in e.body for e in history)
    assert not any(e.body.get("signal") in {"diagnosis", "reject_arrival"} for e in history)
    assert not (repo / f"tickets/{STEM}/attempts/0/harvest.json").exists()
    assert reject_queue(events) == {}
    assert not writers[0].ctx.worktree(STEM).exists()


def test_requisition_park_reports_full_reason_under_park_line(root, capsys):
    from chupa import runner
    from chupa.llm import FakeLLM
    from tests.integration.test_rework import SNAG, requisition

    commit_ticket(root, "review-park", confirmed())
    artifact = root / "tickets/review-park/review.md"
    artifact.write_text("existing detail")
    llm = FakeLLM([requisition("snag")])
    assert main(["drain"], cwd=root, env=ENV, clock=Clock(), pipeline=lambda c: runner.bind(c, llm)) == 0
    output = capsys.readouterr().out
    terminal = [e.body for e in journal(root).read() if e.type == EventType.STATE_TRANSITION and e.ticket == "review-park"][-1]
    reason = terminal["reason"]
    assert SNAG.message in reason  # A different or empty review result cannot satisfy the report check.
    assert "parked:\n- review-park: premise_failed at requisition;" in output
    assert f"\n  - {reason}\n  - tickets/review-park/review.md" in output  # Preserve the journal text before ticket-plane paths.
    assert [r.surface for r in llm.requests] == ["requisition_review"]


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


@pytest.mark.parametrize("red_priority, expected", [("P1", ["red", "fresh"]), ("P2", ["fresh", "red"])])
def test_reoffer_and_fresh_share_priority_age_order(root, red_priority, expected):
    intake_at(root, "red", START)
    commit_ticket(root, "red", confirmed(priority=red_priority))
    commit_ticket(root, "fresh", confirmed(priority="P1"))
    journal(root).append(EventType.STATE_TRANSITION, {"to": "gate_failed"}, ticket="red")
    script = Script()
    assert drain(root, script) == 0
    assert script.calls == expected
    assert retry_draws(root, "red") == 1


# --- park, re-offer, and the journal-derived retry budget -------------------------------------------


def test_a_red_independent_ticket_parks_and_the_next_still_runs(tmp_path, capsys):
    root = make_root(tmp_path, "caps: {retry: 1}\n")
    write(root, "aaa-red", ticket())
    write(root, "bbb-green", ticket())

    def findings(checkout):
        (checkout.repo / "tickets" / "aaa-red" / "review.md").write_text("reject: thing() is wrong\n")

    script = Script({"aaa-red": ["gate_failed", "gate_failed"]}, {"aaa-red": findings})
    assert drain(root, script) == 0  # quiescence with a parked red still exits zero
    # The older red re-offer spends its retry before the younger ticket runs.
    assert script.calls == ["aaa-red", "aaa-red", "bbb-green"]
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
    for _ in range(3):  # the shipped default retry cap
        j.append(EventType.CAP_CONSUMED, {"cap": "retry", "ticket_sha": "x"}, ticket="spent")
    script = Script()
    assert drain(root, script) == 0
    assert script.calls == []
    assert "spent: gate_failed at check; retry cap spent (3/3)" in capsys.readouterr().out


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
    root = make_root(tmp_path, "caps: {retry: 3, diagnosis: 6}\n")
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


def test_drain_merges_without_scanning_the_box(root, monkeypatch):
    box = Box(root / ".chupa" / "state" / "box", LocalFileSystem())
    id, _ = box.enqueue(message_class="suggestion", origin="test", summary="pending observation")
    write(root, "work", ticket())
    requests = []
    monkeypatch.setattr("chupa.triage.triage_pass", lambda *args: requests.append(args))
    from chupa.daemon import storm_producer

    def arrival(checkout):
        producer = storm_producer(root=box.root, fs=box.fs, journal=checkout.journal, clock=checkout.clock)
        producer.enqueue(message_class="suggestion", origin="test", summary="pending observation", occurrence_id="drain-observation")

    script = Script(hooks={"work": arrival})
    assert drain(root, script) == 0
    assert script.calls == ["work"]
    assert requests == []
    assert box.get(id).status == "pending"
    assert box.get(id).verdict is box.get(id).resolution is None
    assert any(e.body.get("kind") == "storm_occurrence" for e in journal(root).read())
    assert not any(e.type == EventType.SIGNAL and e.body.get("signal") == "triage_pass" for e in journal(root).read())


def test_an_uncommitted_ticket_file_is_not_eligible(root):
    write(root, "seeder", ticket())

    def author_only(checkout):
        write(checkout.repo, "loose", "invalid ticket")  # lint refuses this file

    script = Script(hooks={"seeder": author_only})
    assert drain(root, script) == 0
    assert script.calls == ["seeder"]
    assert "?? tickets/loose/" in git_out(root, "status", "--porcelain")


def test_drain_intakes_ticket_written_mid_drain(root):
    write(root, "seeder", ticket())

    def author(checkout):
        write(checkout.repo, "new-ticket", confirmed())
        assert "?? tickets/new-ticket/" in git_out(root, "status", "--porcelain")  # intake must not run inside dispatch

    script = Script(hooks={"seeder": author})
    assert drain(root, script) == 0
    assert script.calls == ["seeder", "new-ticket"]  # a startup-only intake misses the new ticket
    assert "chupa(new-ticket): ticket" in git_out(root, "log", "--format=%s")
    events = journal(root).read()
    terminal = next(i for i, e in enumerate(events) if e.ticket == "seeder" and e.body.get("to") == "merged")
    intake_event = next(i for i, e in enumerate(events) if e.ticket == "new-ticket" and e.body.get("signal") == "ticket_intake")
    assert terminal < intake_event  # intake during dispatch would precede the terminal


def test_drain_mid_drain_intake_refusal_exits_2(root):
    write(root, "aaa-first", ticket())
    write(root, "bbb-second", ticket())

    def stage_stray(checkout):
        (checkout.repo / "chupa/stray.py").write_text("stray\n")
        git_out(checkout.repo, "add", "chupa/stray.py")

    script = Script(hooks={"aaa-first": stage_stray})
    assert drain(root, script) == 2  # ignoring intake refusal would continue
    assert script.calls == ["aaa-first"]  # the second ticket must not run
    lock = Lockfile(root / ".chupa/state", verb="drain", instance_id="probe", clock=Clock())
    lock.acquire()  # refusal must release the lock
    lock.release()


def test_drain_honors_priority_edit_mid_drain(root):
    commit_ticket(root, "aaa-first", confirmed(priority="P0"))
    commit_ticket(root, "bbb-second", confirmed(priority="P1"))
    commit_ticket(root, "ccc-third", confirmed(priority="P2"))

    def promote(checkout):
        path = checkout.repo / "tickets/ccc-third/ticket.md"
        path.write_text(path.read_text().replace("priority: P2", "priority: P0"))

    script = Script(hooks={"aaa-first": promote})
    assert drain(root, script) == 0
    assert script.calls == ["aaa-first", "ccc-third", "bbb-second"]  # stale priority selects second first


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
    halts = [e.body for e in journal(root).read() if e.type == EventType.SIGNAL and e.body.get("signal") == HALT_SIGNAL]
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


def test_drain_report_omits_invalid_settled_and_rejected_tickets(root, capsys):
    invalid = confirmed().replace("- chupa/thing.py", "- chupa/missing.py", 1)
    for stem in ("merged", "rejected", "unsettled"):
        commit_ticket(root, stem, invalid)
    j = journal(root)
    j.append(EventType.STATE_TRANSITION, {"to": "merged"}, ticket="merged")
    j.append(EventType.STATE_TRANSITION, {"to": "rejected"}, ticket="rejected")

    script = Script()
    assert drain(root, script) == 0
    assert script.calls == []
    block = capsys.readouterr().out.split("invalid committed tickets:\n", 1)[1].split("\n\n", 1)[0]
    assert "unsettled:" in block
    assert "merged:" not in block and "rejected:" not in block


def test_drain_scan_skips_finished_tickets(root, capsys, monkeypatch):
    from chupa import drain as drain_module

    for stem in ("merged", "rejected", "unsettled"):
        commit_ticket(root, stem, "unparseable")
    j = journal(root)
    j.append(EventType.STATE_TRANSITION, {"to": "merged"}, ticket="merged")
    j.append(EventType.STATE_TRANSITION, {"to": "rejected"}, ticket="rejected")
    parsed = []
    original = drain_module.parse_ticket

    def record(stem, *args, **kwargs):
        parsed.append(stem)
        return original(stem, *args, **kwargs)

    monkeypatch.setattr(drain_module, "parse_ticket", record)
    assert drain(root, Script()) == 0
    block = capsys.readouterr().out.split("invalid committed tickets:\n", 1)[1].split("\n\n", 1)[0]
    assert "unsettled:" in block
    assert "merged:" not in block and "rejected:" not in block
    assert set(parsed) == {"unsettled"}


def test_lock_contention_stops_the_drain_with_exit_2(root):
    write(root, "add-thing", ticket())
    holder = Lockfile(root / ".chupa" / "state", verb="drain", instance_id="other", clock=Clock())
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


# --- spec-gap hold (section 11.4) ---------------------------------------------------------------


def mechanical_first(monkeypatch, stem, *, workspace=True):
    from chupa import runner, stages
    from chupa.artifacts import Cost, Finding, StageResult

    original = runner.run_stages
    called = []

    async def first(ctx, ticket):
        if ticket.stem == stem and not called:
            called.append(ticket.stem)
            if workspace:
                await stages.prepare_worktree(ctx, ticket.stem)
            return stages.StagesRun(
                attempt=0,
                results={
                    "implement": StageResult(
                        outcome="premise_failed", artifact=None, cost=Cost(), findings=[Finding(code="render_over_bound", message="too large", paved_road="shrink or split and rerun drain")]
                    )
                },
            )
        return await original(ctx, ticket)

    monkeypatch.setattr(runner, "run_stages", first)
    return called


@pytest.mark.parametrize("mechanical", [False, True])
def test_rework_update_reenters_on_fresh_content(rework_repo, monkeypatch, mechanical):
    import json

    from chupa import runner
    from chupa.caps import consume
    from chupa.llm import FakeLLM
    from tests.integration.test_drain_reentry import NoChild
    from tests.integration.test_rework import order, requisition
    from tests.integration.test_stages import ENV, SNAG, STEM, agent, verdict
    from tests.integration.test_terminal import author, clock

    repo = rework_repo
    author(repo)
    consume(Journal(repo / ".chupa/state", clock), STEM, "infra", "prior")
    fresh = []

    def update(req):
        text = (repo / f"tickets/{STEM}/ticket.md").read_text().strip()
        revised = text.replace("holds the word ok", "holds ok after reviewed narrowing")
        fresh.append(revised)
        return order("update", [(STEM, revised)])

    if mechanical:
        mechanical_first(monkeypatch, STEM)
        script = []
    else:
        script = [agent({"chupa/thing.py": "ok\n"}), verdict("snag", [SNAG]), json.dumps({"verdict": "split", "lessons": ["Narrow the work."]})]
    llm = FakeLLM([*script, update, requisition(), agent({"chupa/thing.py": "ok\n"}), verdict()])
    assert main(["drain"], cwd=repo, env=ENV, clock=clock, pipeline=lambda c: runner.bind(c, llm), reexec=NoChild()) == 0
    events = Journal(repo / ".chupa/state", clock).read()
    history = [e for e in events if e.ticket == STEM]
    terminals = [e for e in history if e.type == EventType.STATE_TRANSITION and e.body.get("to") != "running"]
    producing = terminals[0].body
    assert producing == (
        {"to": "premise_failed", "stage": "implement", "reason": "render_over_bound"} if mechanical else {"to": "gate_failed", "stage": "review", "reason": "logic", "dispatch": "retry"}
    )
    rendered = [r for r in llm.requests if r.surface == "implement"][-1].rendered
    assert "holds ok after reviewed narrowing" in rendered and "holds the word ok" not in rendered.split("## Prior attempts", 1)[0]
    assert git_out(repo, "show", f"HEAD:tickets/{STEM}/ticket.md") == fresh[0]
    assert draws(events, STEM, "retry") == (0 if mechanical else 1)
    assert draws(events, STEM, "infra") == 1
    assert draws(events, STEM, "diagnosis") == (0 if mechanical else 1)
    if not mechanical:
        draw = next(e for e in history if e.type == EventType.CAP_CONSUMED and e.body["cap"] == "retry")
        assert draw.body == {"cap": "retry", "ticket_sha": git_out(repo, "rev-parse", f"HEAD:tickets/{STEM}/ticket.md").strip()}
        runs = [e for e in history if e.body.get("to") == "running"]
        assert history.index(terminals[0]) < history.index(draw) < history.index(runs[1])


def test_rework_split_successors_release_original_dependents(root):
    commit_ticket(root, "original", confirmed())
    commit_ticket(root, "dependent", confirmed(depends="- original", priority="P0"))

    def split(checkout):
        for stem, deps in [("piece-one", "none"), ("piece-two", "none"), ("leaf-a", "none"), ("leaf-b", "none")]:
            commit_ticket(root, stem, confirmed(deps))
        for stem, successors in [("original", ["piece-one", "piece-two"]), ("piece-one", ["leaf-a", "leaf-b"])]:
            checkout.journal.append(EventType.SIGNAL, {"signal": "supersedes", "successors": successors}, ticket=stem)
        checkout.journal.append(EventType.STATE_TRANSITION, {"to": "rejected"}, ticket="piece-one")

    script = Script({"original": ["rejected"], "leaf-a": ["already_satisfied"], "leaf-b": ["gate_failed", "already_satisfied"]}, {"original": split})
    assert drain(root, script) == 0
    assert script.calls == ["original", "leaf-a", "leaf-b", "leaf-b", "piece-two", "dependent"]
    assert retry_draws(root, "original") == 0 and retry_draws(root, "leaf-b") == 1
    assert "piece-one" not in script.calls and script.calls.count("original") == 1


@pytest.mark.parametrize("mechanical", [False, True])
def test_rework_split_preserves_dispatch_terminal_invariant(rework_repo, monkeypatch, mechanical):
    import json

    from chupa import runner
    from chupa.llm import FakeLLM
    from tests.integration.test_rework import order, requisition, successors
    from tests.integration.test_stages import ENV, SNAG, STEM, agent, verdict
    from tests.integration.test_terminal import author, clock

    repo = rework_repo
    (repo / "chupa/thing.py").write_text("ok base\n")
    git_out(repo, "add", "chupa/thing.py")
    git_out(repo, "commit", "-m", "green base")
    author(repo)
    author(repo, stem="dependent", depends=f"- {STEM}")

    def split(req):
        return order("split", successors((repo / f"tickets/{STEM}/ticket.md").read_text().strip()))

    if mechanical:
        mechanical_first(monkeypatch, STEM)
        first = []
    else:
        first = [agent({"chupa/thing.py": "ok\n"}), verdict("snag", [SNAG]), json.dumps({"verdict": "split", "lessons": ["Split the work."]})]
    llm = FakeLLM([*first, split, requisition(), requisition(), agent({}, outcome="already_satisfied"), agent({}, outcome="already_satisfied"), agent({}, outcome="already_satisfied")])
    returns, held = [], []

    def bind(checkout):
        writer = runner.bind(checkout, llm)

        async def dispatch(ticket):
            value = await writer(ticket)
            returns.append((ticket.stem, value))
            contender = Lockfile(checkout.config.state_dir, verb="drain", instance_id="contender", clock=clock)
            with pytest.raises(LockHeld):
                contender.acquire()
            held.append(ticket.stem)
            assert not writer.ctx.worktree(ticket.stem).exists()
            return value

        return dispatch

    assert main(["drain"], cwd=repo, env=ENV, clock=clock, pipeline=bind) == 0
    assert returns == [(STEM, "rejected"), ("piece-one", "already_satisfied"), ("piece-two", "already_satisfied"), ("dependent", "already_satisfied")]
    events = Journal(repo / ".chupa/state", clock).read()
    history = [e for e in events if e.ticket == STEM]
    producing = next(e for e in history if e.body.get("to") == ("premise_failed" if mechanical else "gate_failed"))
    assert producing.body == ({"to": "premise_failed", "stage": "implement", "reason": "render_over_bound"} if mechanical else {"to": "gate_failed", "stage": "review", "reason": "logic"})
    mapping = next(e for e in history if e.body.get("signal") == "supersedes")
    retirement = next(e for e in history if e.body == {"to": "rejected"})
    assert history.index(mapping) < history.index(producing) < history.index(retirement)
    assert history[-1] == retirement and draws(events, STEM, "retry") == 0
    assert held == [s for s, _ in returns]
    # The unchanged seam still rejects a producing return after a later retirement.
    from chupa.config import load_config
    from chupa.drain import _Drain
    from chupa.tickets import validate_ticket

    checkout = runner.Checkout(
        repo,
        load_config(None, cwd=repo),
        ENV,
        SubprocessExec(),
        Git(SubprocessExec(), env=ENV, timeout=30, commit_lock=commit_lock(repo / ".chupa/state")),
        Journal(repo / ".chupa/state", clock),
        LocalFileSystem(),
        clock,
    )
    candidate = validate_ticket("dependent", (repo / "tickets/dependent/ticket.md").read_text(), repo)

    async def mismatch(ticket):
        checkout.journal.append(EventType.STATE_TRANSITION, {"to": "rejected"}, ticket=ticket.stem)
        return "gate_failed"

    with pytest.raises(ValueError, match="but journaled 'rejected'"):
        asyncio.run(_Drain(checkout, mismatch, frozenset())._run_one(candidate, False, "blob"))


@pytest.mark.parametrize("action", ["split", "update", "escalate", "exhausted", "refusal", "publication", "missing"])
def test_render_over_bound_dispatches_rework_without_diagnosis(rework_repo, monkeypatch, action):
    import json

    from chupa import daemon, runner
    from chupa.llm import FakeLLM
    from chupa.status import reject_queue
    from tests.integration.test_rework import order, requisition, successors
    from tests.integration.test_stages import ENV, STEM, agent, verdict
    from tests.integration.test_terminal import author, clock

    repo = rework_repo
    author(repo)
    if action == "exhausted":
        path = repo / f"tickets/{STEM}/ticket.md"
        path.write_text(path.read_text().replace("kind: feature", "kind: feature\nagent_tier: max\nagent_effort: max"))
        from tests.approval import approve

        approve(repo, STEM, clock)
    mechanical_first(monkeypatch, STEM, workspace=action != "missing")
    calls = []
    apply = daemon.apply_rework

    async def observed(*args, **kwargs):
        calls.append(kwargs)
        return await apply(*args, **kwargs)

    monkeypatch.setattr(daemon, "apply_rework", observed)

    def reply(req):
        text = (repo / f"tickets/{STEM}/ticket.md").read_text().strip()
        if action in {"split", "publication"}:
            return order("split", successors(text))
        if action == "update":
            return order("update", [(STEM, text.replace("holds the word ok", "holds ok after shrinking"))])
        return order("escalate") if action != "refusal" else order("update", [(STEM, "invalid")])

    if action == "publication":
        commit = Git.commit

        async def failed(self, root, message, **kwargs):
            if message.endswith(": rework"):
                raise RuntimeError("publication failed")
            return await commit(self, root, message, **kwargs)

        monkeypatch.setattr(Git, "commit", failed)
    script = [] if action == "missing" else [reply]
    if action in {"split", "publication"}:
        script += [requisition(), requisition()]
    if action == "update":
        script += [requisition(), agent({"chupa/thing.py": "ok\n"}), verdict()]
    if action == "split":
        (repo / "chupa/thing.py").write_text("ok base\n")
        git_out(repo, "add", "chupa/thing.py")
        git_out(repo, "commit", "-m", "green base")
        script += [agent({}, outcome="already_satisfied"), agent({}, outcome="already_satisfied")]
    llm = FakeLLM(script)
    returned = []

    def bind(checkout):
        writer = runner.bind(checkout, llm)
        writer.ctx.driver.retry_cap = 0

        async def dispatch(ticket):
            value = await writer(ticket)
            returned.append((ticket.stem, value))
            return value

        return dispatch

    from tests.integration.test_drain_reentry import NoChild

    assert main(["drain"], cwd=repo, env=ENV, clock=clock, pipeline=bind, reexec=NoChild()) == 0
    events = Journal(repo / ".chupa/state", clock).read()
    original = [e for e in events if e.ticket == STEM]
    producing = next(e for e in original if e.body.get("to") == "premise_failed")
    assert producing.body == {"to": "premise_failed", "stage": "implement", "reason": "render_over_bound"}
    assert len(calls) == 1 and calls[0]["attempt"] == 0
    assert not any(e.type == EventType.CAP_CONSUMED for e in original)
    assert not any(e.body.get("signal") in {"diagnosis", "reject_arrival"} for e in original)
    assert STEM not in reject_queue(events)
    assert returned[0] == (STEM, "rejected" if action == "split" else "premise_failed")
    if action == "split":
        assert original[-1].body == {"to": "rejected"}
        assert original.index(producing) < len(original) - 1
    elif action == "update":
        assert [s for s, _ in returned] == [STEM, STEM]
        assert [r.surface for r in llm.requests] == ["rework", "requisition_review", "implement", "review"]
    else:
        assert original[-1] == producing and not any(e.body.get("signal") == "supersedes" for e in original)
        assert [s for s, _ in returned] == [STEM]
        if action == "missing":
            assert llm.requests == []
        if action in {"escalate", "exhausted", "refusal", "publication"}:
            harvest = json.loads((repo / f"tickets/{STEM}/attempts/0/harvest.json").read_text())
            assert all(f["paved_road"] for f in harvest["findings"]) and len(harvest["findings"]) >= 2


# --- dormant dispatch pause checkpoint ----------------------------------------------------------


def pause_checkout(root):
    from chupa.config import load_config
    from chupa.runner import Checkout

    process = SubprocessExec()
    checkout = Checkout(root, load_config(None, cwd=root), ENV, process, Git(process, env=ENV, timeout=30, commit_lock=commit_lock(root / ".chupa/state")), journal(root), LocalFileSystem(), Clock())
    return replace(checkout, control=build_control(checkout))


class Pause:
    def __init__(self, at=2):
        self.at = at
        self.calls = 0
        self.entered, self.release = asyncio.Event(), asyncio.Event()

    async def __call__(self):
        self.calls += 1
        if self.calls == self.at:
            self.entered.set()
            await self.release.wait()


async def paused_drain(root, script, checkpoint):
    from chupa.drain import drain as run_drain
    from tests.integration.test_drain_reentry import NoChild

    checkout = pause_checkout(root)
    return await run_drain(checkout, script(checkout), reexec=NoChild(), before_dispatch=checkpoint)


def prior_failure(root, *, terminal="gate_failed", extra=None):
    blob = git_out(root, "rev-parse", "HEAD:tickets/work/ticket.md").strip()
    j = journal(root)
    j.append(EventType.STATE_TRANSITION, {"to": "running", "ticket_sha": blob}, ticket="work")
    j.append(EventType.STATE_TRANSITION, {"to": terminal, **(extra or {})}, ticket="work")
    return blob


def offer_events(root):
    return [e for e in journal(root).read() if e.type in {EventType.CAP_CONSUMED, EventType.STATE_TRANSITION} or e.body.get("signal") == "reject_verdict"]


@pytest.mark.asyncio
async def test_pause_precedes_fresh_offer_accounting(root):
    commit_ticket(root, "work", confirmed())
    pause, script = Pause(), Script()
    task = asyncio.create_task(paused_drain(root, script, pause))
    await pause.entered.wait()
    assert offer_events(root) == [] and script.calls == []
    pause.release.set()
    assert (await task).merged == ["work"]
    blob = git_out(root, "rev-parse", "HEAD:tickets/work/ticket.md").strip()
    events = offer_events(root)
    assert [e.body for e in events] == [{"to": "running", "ticket_sha": blob}, {"to": "merged"}]
    assert all(e.ticket == "work" and e.key is None for e in events)
    assert script.lock_held == [True] and retry_draws(root, "work") == 0


@pytest.mark.asyncio
async def test_pause_precedes_retry_cap_draw(root):
    commit_ticket(root, "work", confirmed())
    rung = {"tier": "high", "effort": "max"}
    blob = prior_failure(root, extra={"rung": rung})
    before = offer_events(root)
    pause, script = Pause(), Script()
    task = asyncio.create_task(paused_drain(root, script, pause))
    await pause.entered.wait()
    assert offer_events(root) == before and script.calls == []
    pause.release.set()
    assert (await task).merged == ["work"]
    draw, running, terminal = offer_events(root)[len(before) :]
    assert draw.type == EventType.CAP_CONSUMED
    assert draw.ticket == "work" and draw.key is None
    assert draw.body == {"cap": "retry", "ticket_sha": blob, "rung": rung}
    assert running.body == {"to": "running", "ticket_sha": blob}
    assert running.ticket == "work" and running.key is None and terminal.body == {"to": "merged"}
    assert retry_draws(root, "work") == 1


@pytest.mark.asyncio
async def test_pause_precedes_machine_keep(root):
    commit_ticket(root, "work", confirmed())
    blob = prior_failure(root)
    journal(root).append(EventType.SIGNAL, {"signal": "reject_arrival"}, ticket="work")
    pause, script = Pause(), Script()
    before = offer_events(root)
    task = asyncio.create_task(paused_drain(root, script, pause))
    await pause.entered.wait()
    assert offer_events(root) == before and script.calls == []
    pause.release.set()
    assert (await task).merged == ["work"]
    keep, draw, running, terminal = offer_events(root)[len(before) :]
    assert keep.type == EventType.SIGNAL and keep.ticket == "work" and keep.key is None
    assert keep.body == {"signal": "reject_verdict", "verdict": "keep", "actor": "machine"}
    assert draw.body == {"cap": "retry", "ticket_sha": blob}
    assert running.body == {"to": "running", "ticket_sha": blob} and terminal.body == {"to": "merged"}
    assert retry_draws(root, "work") == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("change", ["settled", "budget", "depends", "priority", "content"])
async def test_pause_release_rechecks_eligibility_and_budget(root, change):
    commit_ticket(root, "work", confirmed(priority="P1"))
    if change == "budget":
        prior_failure(root)
    if change == "priority":
        commit_ticket(root, "other", confirmed(priority="P2"))
    pause, script = Pause(), Script()
    task = asyncio.create_task(paused_drain(root, script, pause))
    await pause.entered.wait()
    assert script.calls == []
    if change == "settled":
        journal(root).append(EventType.STATE_TRANSITION, {"to": "already_satisfied"}, ticket="work")
    elif change == "budget":
        for _ in range(6):
            journal(root).append(EventType.CAP_CONSUMED, {"cap": "retry", "ticket_sha": "prior"}, ticket="work")
    elif change == "depends":
        commit_ticket(root, "work", confirmed(depends="- missing"))
    elif change == "priority":
        commit_ticket(root, "other", confirmed(priority="P0"))
    else:
        commit_ticket(root, "work", confirmed().replace("`thing()` returns ok.", "`thing()` returns revised ok."))
    pause.release.set()
    await task
    assert script.calls == (["other", "work"] if change == "priority" else ["work"] if change == "content" else [])
    if change in {"settled", "budget", "depends"}:
        assert not any(e.body.get("to") == "running" for e in offer_events(root)[2 if change == "budget" else 0 :])
    if change == "content":
        [running] = [e for e in offer_events(root) if e.body.get("to") == "running"]
        assert running.body["ticket_sha"] == git_out(root, "rev-parse", "HEAD:tickets/work/ticket.md").strip()
    if change == "budget":
        assert retry_draws(root, "work") == 6


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel", [False, True])
async def test_pause_checkpoint_failure_spends_no_retry(root, cancel):
    commit_ticket(root, "work", confirmed())
    prior_failure(root)
    before = journal(root).read()
    pause, script = Pause(), Script()

    async def checkpoint():
        await pause()
        if pause.calls == pause.at:
            raise ValueError("checkpoint failed")

    task = asyncio.create_task(paused_drain(root, script, checkpoint))
    await pause.entered.wait()
    if cancel:
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    else:
        pause.release.set()
        with pytest.raises(ValueError, match="checkpoint failed"):
            await task
    assert script.calls == [] and journal(root).read() == before and retry_draws(root, "work") == 0
    lock = Lockfile(root / ".chupa/state", verb="drain", instance_id="after-cleanup", clock=Clock())
    lock.acquire()
    lock.release()
    assert (await paused_drain(root, script, None)).merged == ["work"]
    assert retry_draws(root, "work") == 1


@pytest.mark.asyncio
async def test_pause_preserves_free_premise_reoffer(root):
    commit_ticket(root, "work", confirmed())
    prior_failure(root, terminal="premise_failed")
    commit_ticket(root, "work", confirmed().replace("`thing()` returns ok.", "`thing()` returns revised ok."))
    before = offer_events(root)
    pause, script = Pause(), Script()
    task = asyncio.create_task(paused_drain(root, script, pause))
    await pause.entered.wait()
    assert offer_events(root) == before and script.calls == []
    pause.release.set()
    assert (await task).merged == ["work"]
    assert retry_draws(root, "work") == 0
    running, terminal = offer_events(root)[len(before) :]
    assert running.body == {"to": "running", "ticket_sha": git_out(root, "rev-parse", "HEAD:tickets/work/ticket.md").strip()}
    assert terminal.body == {"to": "merged"}


@pytest.mark.asyncio
async def test_drain_uses_supplied_control(root, monkeypatch):
    from chupa import __main__ as cli
    from chupa.drain import drain as run_drain
    from chupa.runner import Refusal
    from tests.integration.test_drain_reentry import NoChild

    checkout = pause_checkout(root)
    consumer = checkout.control
    trace = []

    def forbidden(*args, **kwargs):
        pytest.fail("drain constructed a fallback consumer")

    monkeypatch.setattr(cli, "build_control", forbidden)
    acquire, release = Lockfile.acquire, Lockfile.release

    def acquired(lock):
        acquire(lock)
        trace.append("lock")

    def released(lock):
        assert trace[-1] == "retire"
        trace.append("unlock")
        release(lock)

    monkeypatch.setattr(Lockfile, "acquire", acquired)
    monkeypatch.setattr(Lockfile, "release", released)
    for name in ("publish", "checkpoint", "retire"):
        original = getattr(consumer, name)
        if name == "checkpoint":

            async def checked(_original=original):
                assert trace[0] == "lock" and "unlock" not in trace
                trace.append("consume")
                await _original()

            monkeypatch.setattr(consumer, name, checked)
        else:

            def called(_original=original, _name=name):
                assert trace[0] == "lock" and "unlock" not in trace
                _original()
                trace.append(_name)

            monkeypatch.setattr(consumer, name, called)
    assert (await run_drain(checkout, Script()(checkout), reexec=NoChild())).merged == []
    assert trace[:2] == ["lock", "publish"] and "consume" in trace
    assert trace[-2:] == ["retire", "unlock"]
    assert (checkout.config.state_dir / "control/active.json").read_bytes() == b"null\n"
    trace.clear()
    with pytest.raises(Refusal, match="build_control.*Checkout.control"):
        await run_drain(replace(checkout, control=None), Script()(checkout), reexec=NoChild())
    assert trace == []


def test_retro_hook_is_default_off(root):
    from chupa.drain import _Drain
    from chupa.drain import drain as run_drain
    from tests.integration.test_drain_reentry import NoChild

    commit_ticket(root, "work", confirmed())
    checkout = pause_checkout(root)
    script = Script()
    dispatch = script(checkout)
    assert _Drain(checkout, dispatch, frozenset()).retro is None
    assert asyncio.run(run_drain(checkout, dispatch, reexec=NoChild())).merged == ["work"]
    assert not list((root / "tickets/retro").glob("*.md"))
    assert not any((e.key or "").startswith("llm/retro/") for e in checkout.journal.read())


def test_due_retro_waits_for_retry_and_precedes_next_ticket(root):
    from chupa.drain import drain as run_drain
    from chupa.retro import measurements, project_window, select_trigger
    from tests.integration.test_drain_reentry import NoChild

    commit_ticket(root, "aa", confirmed(priority="P0"))
    commit_ticket(root, "bb", confirmed(priority="P1"))
    checkout = pause_checkout(root)
    for n in range(4):
        checkout.journal.append(EventType.STATE_TRANSITION, {"to": "gate_failed"}, ticket=f"prior-{n}")
    trace = []
    script = Script({"aa": ["gate_failed", "merged"]}, {"aa": lambda _: trace.append("aa"), "bb": lambda _: trace.append("bb")})
    dispatch = script(checkout)

    class Retro:
        async def __call__(self, *, forced=False):
            window = project_window(checkout.journal.read())
            if trigger := select_trigger(window, measurements(window), checkout.clock(), checkout.config.retro, forced=forced):
                trace.append(f"retro:{trigger}")
                checkout.journal.append(EventType.EFFECT_COMPLETION, {"result": {}}, key="retro/1")

        async def abort_current(self):
            pass

    dispatch._retro = Retro()
    report = asyncio.run(run_drain(checkout, dispatch, reexec=NoChild()))
    assert report.merged == ["aa", "bb"]
    assert trace == ["aa", "aa", "retro:gate-failure", "bb"]


@pytest.mark.asyncio
async def test_selected_retro_remains_killable_through_existing_control(root):
    from chupa import runner
    from chupa.control import ControlRequest, publish_request
    from chupa.drain import drain as run_drain
    from chupa.llm import HANG, FakeLLM
    from chupa.retro import Retro
    from tests.integration.test_daemon_admission import turn
    from tests.integration.test_drain_reentry import NoChild

    commit_ticket(root, "work", confirmed())
    ticks = asyncio.Queue()

    async def sleep(seconds):
        if seconds == 0.1:
            await ticks.get()
        else:
            await asyncio.Event().wait()

    for n in range(25):
        journal(root).append(EventType.STATE_TRANSITION, {"to": "merged"}, ticket=f"prior-{n}")
    checkout = replace(pause_checkout(root), sleep=sleep, control=None)
    checkout = replace(checkout, control=build_control(checkout))
    llm = FakeLLM([HANG])
    writer = runner.bind(checkout, llm)

    async def dispatch(ticket):
        checkout.journal.append(EventType.STATE_TRANSITION, {"to": "merged"}, ticket=ticket.stem)
        return "merged"

    dispatch.stages = writer.stages
    dispatch.abort_current = writer.abort_current
    dispatch._retro = Retro(checkout, dispatch)
    async with asyncio.timeout(5):
        task = asyncio.create_task(run_drain(checkout, dispatch, reexec=NoChild()))
        while not llm.requests:
            await turn()
        assert llm.requests[0].surface == "retro"
        publish_request(checkout.config.state_dir, ControlRequest("stop-retro", checkout.control.inbox.lifecycle_id, "kill", None), checkout.fs)
        ticks.put_nowait(None)
        report = await task
    assert report.killed and report.exit_code == 1 and llm.aborted == 1
    assert not list((root / "tickets/retro").glob("*.md"))
    assert not any(e.body.get("kind") == "retro_failed" for e in checkout.journal.read())


@pytest.mark.parametrize("scenario", ["not-due", "selected-failure", "due", "self-upgrade"])
def test_drain_retro_runs_only_when_due(tmp_path, monkeypatch, scenario):
    _exercise_retro_drain(tmp_path, monkeypatch, scenario)


def test_phase_exit_stem_gets_no_forced_retro(tmp_path, monkeypatch):
    _exercise_retro_drain(tmp_path, monkeypatch, "phase")


def _exercise_retro_drain(tmp_path, monkeypatch, scenario):
    from chupa import __main__ as cli
    from chupa import runner
    from chupa.retro import Retro
    from tests.integration.test_drain_reentry import NoChild
    from tests.integration.test_providers import claude_ok

    root = make_root(tmp_path)
    if scenario == "self-upgrade":
        from chupa import drain as drain_mod

        monkeypatch.setattr(drain_mod, "ENGINE", root.resolve())
    config = (root / "config.yaml").read_text().replace("review: {}", "  - {tier: medium, surface: retro, candidates: [{provider: claude}]}\nreview: {}")
    (root / "config.yaml").write_text(config)
    git_out(root, "add", "config.yaml")
    git_out(root, "commit", "-m", "retro route")
    commit_ticket(root, "feature", confirmed(priority="P0"))
    if scenario == "phase":
        commit_ticket(root, "phase5-exit", confirmed(depends="- feature"))
    clock = Clock()
    if scenario in {"due", "selected-failure", "self-upgrade"}:
        for n in range(25):
            journal(root).append(EventType.STATE_TRANSITION, {"to": "merged"}, ticket=f"prior-{n}")
    invocations, dispatches, contexts, prompts = [], [], [], []
    original_hook = Retro.__call__

    async def hook(self, *, forced=False):
        invocations.append((forced, list(dispatches)))
        contender = Lockfile(self.checkout.config.state_dir, verb="drain", instance_id="retro-contender", clock=clock)
        with pytest.raises(LockHeld):
            contender.acquire()
        return await original_hook(self, forced=forced)

    monkeypatch.setattr(Retro, "__call__", hook)

    class Process(SubprocessExec):
        async def run(self, argv, **kwargs):
            if argv[0] == "git":
                return await super().run(argv, **kwargs)
            if argv[1:] == ["--version"]:
                return 0, "1.2.3", ""
            if argv[0] == "pnpm":
                return 0, "1.2.3", ""
            assert argv[0] == "claude"
            prompt = kwargs["stdin_path"].read_text()
            if prompt == "Reply with the single word ok.":
                return 0, claude_ok("ok"), ""
            prompts.append((list(dispatches), prompt))
            assert "current retro window" in prompt
            if scenario == "selected-failure":
                return 1, "", "scripted retro outage"
            out = claude_ok('{"proposals": []}')
            if kwargs.get("on_spawn"):
                kwargs["on_spawn"](123)
            if kwargs.get("on_stdout_line"):
                for line in out.splitlines(keepends=True):
                    kwargs["on_stdout_line"](line)
            return 0, out, ""

    monkeypatch.setattr(cli, "SubprocessExec", Process)

    async def drive(ctx, ticket, **kwargs):
        dispatches.append(ticket.stem)
        contexts.append(ctx)
        path = "chupa/thing.py" if scenario == "self-upgrade" else f"work/{ticket.stem}.py"
        ctx.fs.write(root / path, b"ok\n")
        await ctx.git.add(root, [path])
        await ctx.git.commit(root, "admitted " + ticket.stem, only=[path])
        terminal = "merged"
        body = {"to": terminal, "commit": await ctx.git.rev_parse(root, "HEAD")}
        ctx.driver.journal.append(EventType.STATE_TRANSITION, body, ticket=ticket.stem)
        return terminal

    monkeypatch.setattr(runner, "drive", drive)
    prepared = runner.prepare_pipeline
    owners = []

    async def prepare(checkout):
        writer = await prepared(checkout)
        assert writer.stages.driver.llm.session is checkout.control.providers
        owners.append(writer.stages.driver)
        return writer

    monkeypatch.setattr(runner, "prepare_pipeline", prepare)
    seen = []
    run_driver = __import__("chupa.driver", fromlist=["Driver"]).Driver.run

    async def recorded(self, stage, *args, **kwargs):
        if stage.surface == "retro":
            assert self in owners and kwargs["ticket"] is None and kwargs["scope_fence"] == ()
            assert kwargs["workspace"] == root
            seen.append(self)
        return await run_driver(self, stage, *args, **kwargs)

    monkeypatch.setattr("chupa.driver.Driver.run", recorded)

    monkeypatch.setattr("chupa.__main__._engine_signals", lambda cb: lambda: None)

    class Child:
        spawns = 0

        async def run(self, argv, **kwargs):
            self.spawns += 1
            assert journal(root).read()[-1].body.get("signal") == "drain_handoff"
            contender = Lockfile(root / ".chupa/state", verb="drain", instance_id="child", clock=clock)
            contender.acquire()
            contender.release()
            code = await asyncio.to_thread(main, argv[7:], cwd=root, env=ENV, clock=clock, pipeline=runner.pipeline, reexec=self)
            return code, "", ""

    child = Child()
    assert main(["drain"], cwd=root, env=ENV, clock=clock, pipeline=runner.pipeline, reexec=child if scenario == "self-upgrade" else NoChild()) == 0
    assert child.spawns == (1 if scenario == "self-upgrade" else 0)
    assert invocations[0] == (False, [])
    if scenario in {"not-due", "phase"}:
        assert dispatches == (["feature", "phase5-exit"] if scenario == "phase" else ["feature"])
        assert seen == prompts == []
        assert not list((root / "tickets/retro").glob("*.md"))
    elif scenario == "selected-failure":
        assert dispatches == ["feature"] and len(seen) == 2
        assert [order for order, _ in prompts] == [[], ["feature"]]
        failures = [e for e in journal(root).read() if e.body.get("kind") == "retro_failed"]
        assert len(failures) == 2
    else:
        assert dispatches == ["feature"] and len(seen) == len(prompts) == 1
        assert prompts[0][0] == []
        assert list((root / "tickets/retro").glob("*.md"))


def machine_keeps(root, stem="held"):
    return [e for e in journal(root).read() if e.ticket == stem and e.body == {"signal": "reject_verdict", "verdict": "keep", "actor": "machine"}]


def test_diff_budget_failure_holds_until_ticket_changes(root, capsys):
    from chupa.drain import _Drain

    commit_ticket(root, "work", confirmed())
    calls = []

    def pipeline(checkout):
        async def dispatch(ticket):
            calls.append(ticket.stem)
            body = {"to": "gate_failed", "reason": "verification,diff_budget", "routed": "reject_queue"} if len(calls) == 1 else {"to": "merged"}
            checkout.journal.append(EventType.STATE_TRANSITION, body, ticket=ticket.stem)
            return body["to"]

        return with_retro_driver(checkout, dispatch)

    assert main(["drain"], cwd=root, env=ENV, clock=Clock(), pipeline=pipeline) == 0
    assert calls == ["work"]
    assert not machine_keeps(root, "work")
    assert "diff budget" in capsys.readouterr().out
    checkout = pause_checkout(root)
    run = _Drain(checkout, pipeline(checkout), frozenset())
    run.last_dispatched = "work"
    assert asyncio.run(run._between_tickets())
    checkout.journal.append(EventType.STATE_TRANSITION, {"to": "gate_failed", "reason": "diff_budget"}, ticket="work")
    assert asyncio.run(run._between_tickets())  # An unrouted budget failure also ends the retry cycle.
    commit_ticket(root, "work", confirmed().replace("returns ok.", "returns revised ok."))
    assert not asyncio.run(run._between_tickets())
    assert main(["drain"], cwd=root, env=ENV, clock=Clock(), pipeline=pipeline) == 0
    assert calls == ["work", "work"]


def test_other_gate_failure_is_still_reoffered(root):
    commit_ticket(root, "work", confirmed())
    calls = []

    def pipeline(checkout):
        async def dispatch(ticket):
            calls.append(ticket.stem)
            body = {"to": "gate_failed", "reason": "verification"} if len(calls) == 1 else {"to": "merged"}
            checkout.journal.append(EventType.STATE_TRANSITION, body, ticket=ticket.stem)
            return body["to"]

        return with_retro_driver(checkout, dispatch)

    assert main(["drain"], cwd=root, env=ENV, clock=Clock(), pipeline=pipeline) == 0
    assert calls == ["work", "work"]


def test_diff_budget_spent_cap_reports_cap_road(tmp_path, capsys):
    root = make_root(tmp_path, "caps: {attempts: 1}\n")
    commit_ticket(root, "work", confirmed())
    prior_failure(root, extra={"reason": "diff_budget", "routed": "reject_queue"})
    script = Script()
    assert drain(root, script) == 0
    output = capsys.readouterr().out
    assert script.calls == []
    assert "attempts cap spent" in output
    assert "split or shrink the ticket under the diff budget" not in output


def test_non_plan_bound_premise_reoffer_after_ticket_edit_draws_no_retry(root):
    commit_ticket(root, "work", confirmed())
    prior_failure(root, terminal="premise_failed", extra={"routed": "reject_queue"})
    commit_ticket(root, "work", confirmed().replace("returns ok.", "returns revised ok."))
    script = Script()
    assert drain(root, script) == 0 and script.calls == ["work"]
    assert len(machine_keeps(root, "work")) == 1 and retry_draws(root, "work") == 0


async def _edit_after_implement(ctx, ticket, *, committed):
    rel = f"tickets/{ticket.stem}/ticket.md"
    path = ctx.repo / rel
    ctx.fs.write(path, path.read_text().replace("holds the word ok", "holds ok after operator revision").encode())
    if committed:
        await ctx.git.add(ctx.repo, [rel])
        await ctx.git.commit(ctx.repo, "edit ticket", only=[rel])


def _mid_run_hold(repo, monkeypatch, *, committed, failed=False):
    from chupa import runner, stages
    from chupa.llm import FakeLLM
    from chupa.status import reject_queue
    from tests.integration.test_stages import STEM, agent, verdict
    from tests.integration.test_terminal import author, clock

    author(repo)
    original = stages.implement

    async def implement(ctx, ticket, *, attempt):
        result = await original(ctx, ticket, attempt=attempt)
        await _edit_after_implement(ctx, ticket, committed=committed)
        return replace(result, outcome="gate_failed") if failed else result

    monkeypatch.setattr(stages, "implement", implement)
    llm = FakeLLM([agent({"chupa/thing.py": "ok\n"})])
    assert main(["drain"], cwd=repo, env=ENV, clock=clock, pipeline=lambda c: runner.bind(c, llm)) == 0
    events = Journal(repo / ".chupa/state", clock).read()
    assert [r.surface for r in llm.requests] == ["implement"]
    assert not any(e.type == EventType.CAP_CONSUMED for e in events)
    assert not any(e.body.get("signal") == "diagnosis" for e in events)
    assert reject_queue(events)[STEM] == {"to": "gate_failed", "stage": "implement" if failed else "check", "reason": "ticket_changed", "dispatch": "reject_queue", "routed": "reject_queue"}
    import json

    harvest = json.loads((repo / f"tickets/{STEM}/attempts/0/harvest.json").read_text())
    (finding,) = harvest["findings"]
    assert finding["code"] == "ticket_changed" and STEM in finding["message"]
    assert finding["paved_road"] == (f"review the change to tickets/{STEM}/ticket.md, then keep (./dev.py confirm {STEM}) or kill (./dev.py reject {STEM})")
    assert not (repo / f"tickets/{STEM}/checks.json").exists()
    # Even a subsequent intake/daemon lifetime must wait for an explicit keep.
    assert main(["drain"], cwd=repo, env=ENV, clock=clock, pipeline=lambda c: runner.bind(c, llm)) == 0
    assert len(llm.requests) == 1
    monkeypatch.setattr(stages, "implement", original)
    assert main(["confirm", STEM], cwd=repo, env=ENV, clock=clock, terminal=(lambda: True, lambda _: "y")) == 0
    from tests.approval import approve

    approve(repo, STEM, clock)
    fresh = FakeLLM([agent({"chupa/thing.py": "ok\n"}), verdict()])
    from tests.integration.test_drain_reentry import NoChild

    assert main(["drain"], cwd=repo, env=ENV, clock=clock, pipeline=lambda c: runner.bind(c, fresh), reexec=NoChild()) == 0
    assert [r.surface for r in fresh.requests] == ["implement", "review"]
    assert STEM not in reject_queue(Journal(repo / ".chupa/state", clock).read())


def test_ticket_edit_mid_run_holds(rework_repo, monkeypatch):
    _mid_run_hold(rework_repo, monkeypatch, committed=True)


def test_uncommitted_ticket_edit_mid_run_holds(rework_repo, monkeypatch):
    _mid_run_hold(rework_repo, monkeypatch, committed=False)


def test_engine_artifacts_do_not_trigger(rework_repo):
    from chupa import runner
    from chupa.llm import FakeLLM
    from tests.integration.test_drain_reentry import NoChild
    from tests.integration.test_stages import STEM, agent, verdict
    from tests.integration.test_terminal import author, clock

    repo = rework_repo
    author(repo)
    llm = FakeLLM([agent({"chupa/thing.py": "ok\n"}), verdict()])
    assert main(["drain"], cwd=repo, env=ENV, clock=clock, pipeline=lambda c: runner.bind(c, llm), reexec=NoChild()) == 0
    events = Journal(repo / ".chupa/state", clock).read()
    assert [r.surface for r in llm.requests] == ["implement", "review"]
    assert [e.body["to"] for e in events if e.type == EventType.STATE_TRANSITION][-1] == "merged"
    lifted = [e.body["result"]["kind"] for e in events if e.type == EventType.EFFECT_COMPLETION and (e.key or "").startswith(f"ticket-plane/{STEM}/")]
    assert "run-record" in lifted and "checks" in lifted


def test_ticket_edit_during_failed_implement_skips_diagnosis(rework_repo, monkeypatch):
    _mid_run_hold(rework_repo, monkeypatch, committed=True, failed=True)


def test_runs_before_failed_ticket_does_not_block_named_ticket(tmp_path):
    root = make_root(tmp_path, "caps: {attempts: 1}\n")
    intake_at(root, "old", START)
    commit_ticket(root, "old", confirmed(priority="P1"))
    commit_ticket(root, "new", confirmed(priority="P2") + "\n## Runs before\n- old\n")
    snapshots = []

    def capture(checkout):
        snapshots.append(json.loads((checkout.config.state_dir / "queue.json").read_text()))

    script = Script({"new": ["gate_failed"]}, hooks={"new": capture})
    assert drain(root, script) == 0
    assert script.calls == ["new", "old"]
    assert snapshots == [{"at": START.isoformat(), "order": ["new", "old"], "runs_before": {"new": ["old"]}}]


def test_historical_spec_gap_hold_terminal_reads_without_release(root):
    from chupa.drain import parked_blob
    from chupa.journal import dispatch_of

    commit_ticket(root, "work", confirmed())
    blob = prior_failure(root, terminal="premise_failed", extra={"dispatch": "spec_gap_hold", "round": 1, "plan_units": {"19.P3.held": "absent"}})
    events = journal(root).read()
    assert dispatch_of(events[-1].body) == "spec_gap_hold"  # Rejecting the old vocabulary must fail.
    assert parked_blob(events, "work") == blob  # Releasing on the historical round must fail.
    script = Script()
    assert drain(root, script) == 0
    assert script.calls == []  # The unchanged ticket must not be dispatched.
    assert parked_blob(events, "work") != "different-ticket-blob"  # A ticket edit releases the park.


@pytest.mark.asyncio
async def test_stop_finishes_current_ticket_and_releases_lock(root):
    from chupa.control import ControlRequest, publish_request
    from chupa.drain import drain as run_drain
    from tests.integration.test_drain_reentry import NoChild

    commit_ticket(root, "aa", confirmed(priority="P0"))
    commit_ticket(root, "bb", confirmed(priority="P1"))
    checkout = pause_checkout(root)
    entered, release = asyncio.Event(), asyncio.Event()
    calls = []

    class Dispatch:
        async def __call__(self, ticket):
            calls.append(ticket.stem)
            entered.set()
            await release.wait()
            checkout.journal.append(EventType.STATE_TRANSITION, {"to": "merged"}, ticket=ticket.stem)
            return "merged"

        async def abort_current(self):
            pytest.fail("stop aborted the running ticket")

    task = asyncio.create_task(run_drain(checkout, Dispatch(), reexec=NoChild()))
    await asyncio.wait_for(entered.wait(), 5)
    publish_request(checkout.config.state_dir, ControlRequest("stop", checkout.control.inbox.lifecycle_id, "stop", None), checkout.fs)
    while not checkout.control.projection.stop_requested:
        await asyncio.sleep(0)
    assert not task.done()
    release.set()
    report = await task
    assert calls == ["aa"] and report.merged == ["aa"]
    assert report.stopped and report.exit_code == 0 and "stopped on request" in report.render()
    lock = Lockfile(checkout.config.state_dir, verb="drain", instance_id="probe", clock=checkout.clock)
    lock.acquire()
    lock.release()


@pytest.mark.asyncio
async def test_stop_survives_self_upgrade_handoff(root, monkeypatch):
    from chupa import drain as drain_mod
    from chupa.control import ControlRequest, publish_request
    from chupa.drain import drain as run_drain
    from tests.integration.test_drain_reentry import NoChild

    monkeypatch.setattr(drain_mod, "ENGINE", root.resolve())
    commit_ticket(root, "aa", confirmed(priority="P0"))
    commit_ticket(root, "bb", confirmed(priority="P1"))
    checkout = pause_checkout(root)
    calls = []

    class Dispatch:
        async def __call__(self, ticket):
            calls.append(ticket.stem)
            publish_request(checkout.config.state_dir, ControlRequest("stop-upgrade", checkout.control.inbox.lifecycle_id, "stop", None), checkout.fs)
            (root / "chupa/thing.py").write_text("upgraded\n")
            await checkout.git.add(root, ["chupa/thing.py"])
            await checkout.git.commit(root, "upgrade")
            commit = await checkout.git.rev_parse(root, "HEAD")
            checkout.journal.append(EventType.STATE_TRANSITION, {"to": "merged", "commit": commit}, ticket=ticket.stem)
            return "merged"

        async def abort_current(self):
            pytest.fail("stop aborted the running ticket")

    class Child:
        async def run(self, argv, **kwargs):
            assert argv[-2:] == ["--stop-lifecycle", checkout.control.inbox.lifecycle_id]
            child = pause_checkout(root)
            report = await run_drain(child, Dispatch(), reexec=NoChild(), stop_lifecycle=argv[-1])
            assert report.stopped and report.exit_code == 0 and report.merged == []
            return report.exit_code, "", ""

    report = await run_drain(checkout, Dispatch(), reexec=Child())
    assert report.handoff == 0 and calls == ["aa"]
    assert any(e.body.get("signal") == "drain_handoff" for e in checkout.journal.read())


@pytest.mark.asyncio
async def test_stop_at_paused_checkpoint_admits_nothing(root):
    from chupa.control import ControlRequest, publish_request
    from chupa.drain import drain as run_drain
    from tests.integration.test_drain_reentry import NoChild

    commit_ticket(root, "work", confirmed())
    checkout = pause_checkout(root)
    script = Script()

    async def request_both():
        for identity, verb in (("10-pause", "pause"), ("20-stop", "stop")):
            publish_request(checkout.config.state_dir, ControlRequest(identity, checkout.control.inbox.lifecycle_id, verb, None), checkout.fs)

    report = await run_drain(checkout, script(checkout), reexec=NoChild(), before_dispatch=request_both)
    assert report.stopped and report.exit_code == 0 and script.calls == []
    assert checkout.control.projection.pause_id == "10-pause"


def test_lifecycle_log_precedes_lock_release(root, monkeypatch):
    import os

    release = Lockfile.release
    observed = []

    def released(lock):
        rows = [json.loads(line) for line in (root / ".chupa/state/engine.log").read_text().splitlines()]
        observed.extend(e for e in rows if e["event"] in {"engine_start", "engine_stop"})
        release(lock)

    monkeypatch.setattr(Lockfile, "release", released)
    assert drain(root, Script()) == 0
    assert [(e["event"], e["verb"], e["pid"], e.get("outcome")) for e in observed] == [("engine_start", "drain", os.getpid(), None), ("engine_stop", "drain", os.getpid(), "quiescent")]
    assert all("engine_start" not in str((e.type, e.body)) and "engine_stop" not in str((e.type, e.body)) for e in journal(root).read())


def test_reoffer_rules_and_recording():
    from types import SimpleNamespace

    from chupa.config import Caps
    from chupa.drain import awaiting_operator, record_reoffer, reofferable

    def event(kind, body, stem="work"):
        return SimpleNamespace(type=kind, ticket=stem, body=body)

    limits = Caps(retry=2, attempts=4)
    rung = {"tier": "high", "effort": "max"}
    history = [event(EventType.STATE_TRANSITION, {"to": "gate_failed", "routed": "reject_queue", "rung": rung})]
    spent = history + [event(EventType.CAP_CONSUMED, {"cap": "retry"}) for _ in range(2)]
    changed = [event(EventType.STATE_TRANSITION, {"to": "gate_failed", "routed": "reject_queue", "reason": "verification,ticket_changed"})]
    assert reofferable(history, "work", limits) and not awaiting_operator(history, "work", limits)  # Holding every Reject entry blocks a retry.
    assert awaiting_operator(spent, "work", limits) and not reofferable(spent, "work", limits)  # Ignoring cap draws reoffers spent work.
    assert awaiting_operator(changed, "work", limits) and not reofferable(changed, "work", limits)  # Budget alone cannot release ticket_changed.
    assert not awaiting_operator(spent, "other", limits) and reofferable(spent, "other", limits)  # Another stem's history must not hold this one.

    class JournalFake:
        def __init__(self):
            self.entries = []

        def append(self, kind, body, *, ticket):
            self.entries.append((kind, body, ticket))

    journal_fake = JournalFake()
    record_reoffer(journal_fake, history, "work", "new-sha")
    assert journal_fake.entries == [
        (EventType.SIGNAL, {"signal": "reject_verdict", "verdict": "keep", "actor": "machine"}, "work"),
        (EventType.CAP_CONSUMED, {"cap": "retry", "ticket_sha": "new-sha", "rung": rung}, "work"),
    ]  # The keep precedes the draw, which carries the new SHA and terminal rung.
    journal_fake.entries.clear()
    premise = [event(EventType.STATE_TRANSITION, {"to": "premise_failed", "routed": "reject_queue"})]
    record_reoffer(journal_fake, premise, "work", "new-sha")
    assert journal_fake.entries == [(EventType.SIGNAL, {"signal": "reject_verdict", "verdict": "keep", "actor": "machine"}, "work")]  # A premise reoffer keeps but draws nothing.
    journal_fake.entries.clear()
    drought = [event(EventType.STATE_TRANSITION, {"to": "infra_error", "provider_drought": {"tier": "high"}})]
    record_reoffer(journal_fake, drought, "work", "new-sha")
    assert journal_fake.entries == []  # A drought neither draws retry nor invents a machine keep.


async def requested_retro_scenario(root, *, second=False, stop=False):
    from chupa.control import ControlRequest, publish_request
    from chupa.drain import drain as run_drain
    from tests.integration.test_drain_reentry import NoChild

    commit_ticket(root, "aa", confirmed(priority="P0"))
    if second:
        commit_ticket(root, "bb", confirmed(priority="P1"))
    # Requested retros must work with automatic retros disabled.
    config = root / "config.yaml"
    config.write_text(config.read_text() + "\nretro: {enabled: false}\n")
    checkout = pause_checkout(root)
    trace = []

    class Retro:
        async def __call__(self, *, forced=False):
            if forced:
                assert tos(root, "aa") == ["running", "merged"]  # A mid-ticket call sees no terminal.
                trace.append("forced")

        async def abort_current(self):
            pytest.fail("retro aborted")

    class Dispatch:
        _retro = Retro()

        async def __call__(self, ticket):
            trace.append(ticket.stem)
            if ticket.stem == "aa":
                for identity, verb in [("10-retro", "retro")] + ([("20-stop", "stop")] if stop else []):
                    publish_request(checkout.config.state_dir, ControlRequest(identity, checkout.control.inbox.lifecycle_id, verb, None), checkout.fs)
                checkout.control.inbox.consume()
            checkout.journal.append(EventType.STATE_TRANSITION, {"to": "merged"}, ticket=ticket.stem)
            return "merged"

        async def abort_current(self):
            pytest.fail("ticket aborted")

    report = await run_drain(checkout, Dispatch(), reexec=NoChild())
    return report, trace


@pytest.mark.asyncio
async def test_requested_retro_runs_between_tickets_once(root):
    report, trace = await requested_retro_scenario(root, second=True)
    assert report.merged == ["aa", "bb"]
    assert trace == ["aa", "forced", "bb"]  # Missing, repeated, or late forced calls change the trace.


@pytest.mark.asyncio
async def test_requested_retro_runs_before_quiescent_exit(root):
    report, trace = await requested_retro_scenario(root)
    assert report.merged == ["aa"] and not report.stopped
    assert trace == ["aa", "forced"]  # A quiescent return that drops the request omits forced.


@pytest.mark.asyncio
async def test_requested_retro_skipped_on_stop(root):
    report, trace = await requested_retro_scenario(root, stop=True)
    assert report.stopped and report.merged == ["aa"]
    assert trace == ["aa"]  # Stop takes precedence over the pending retro.


def test_drain_refuses_committed_core_drift_before_dispatch(root, capsys):
    commit_ticket(root, "work", confirmed())
    path = root / "CLAUDE.md"
    path.write_bytes(path.read_bytes().replace(b"## Engine conduct", b"## Old conduct", 1))
    git_out(root, "add", "CLAUDE.md")
    git_out(root, "commit", "-m", "drift conduct")
    script = Script()
    assert drain(root, script) == 2
    assert "CLAUDE.md: chupa core is drifted" in capsys.readouterr().err
    assert script.calls == []
    lock = Lockfile(root / ".chupa/state", verb="drain", instance_id="contender", clock=Clock())
    lock.acquire()
    lock.release()


def test_operator_keep_releases_unchanged_premise_park(root):
    from chupa.status import reject_queue

    commit_ticket(root, "work", confirmed())
    blob = prior_failure(root, terminal="premise_failed", extra={"stage": "implement", "reason": "premise", "dispatch": "reject_queue", "routed": "reject_queue"})
    assert "work" in reject_queue(journal(root).read())  # The failure reached the Reject queue.
    script = Script()
    assert drain(root, script) == 0 and script.calls == []  # An unchanged ticket stays parked without a keep.
    assert main(["confirm", "work", "--yes"], cwd=root, env=ENV, clock=Clock()) == 0
    assert "work" not in reject_queue(journal(root).read())  # Confirm recorded the verdict.
    assert git_out(root, "rev-parse", "HEAD:tickets/work/ticket.md").strip() == blob  # No ticket edit caused release.
    assert drain(root, script) == 0 and script.calls == ["work"]  # The next drain dispatches it.
