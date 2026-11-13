import asyncio
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock

import pytest

from chupa import __main__ as entry
from chupa import observe, runner, status, triage
from chupa.box import UnknownBoxId
from chupa.journal import EventType
from chupa.tickets import TicketInvalid, validate_ticket

SNAPSHOT_INPUTS = observe.ticket_menu_inputs


def event(state):
    return NS(type=EventType.STATE_TRANSITION, ticket="item", body={"to": state}, key=None)


def test_stem_admissions():
    assert status.order_admission("item", [], False, None).message == "tickets/item/ticket.md does not exist"
    assert status.order_admission("item", [event("merged")], True, None).outcome == "refuse"
    running = [event("running")]
    assert status.order_admission("item", running, True, None).outcome == "admit"
    assert status.order_admission("item", running, True, object()).outcome == "refuse"
    with pytest.raises(TicketInvalid):
        validate_ticket("item", "not a ticket", Path("/repo"))
    assert status.order_admission("item", [], True, None).outcome == "admit"
    assert status.lint_admission("item", [], False).outcome == "refuse"
    assert status.lint_admission("item", [event("rejected")], True).outcome == "noop"
    assert status.lint_admission("item", [], True).outcome == "admit"


def test_box_admissions():
    pending = NS(id="one", resolution=None)
    resolved = NS(id="two", resolution=NS(link="ticket-2"))
    for admit in (status.triage_admission, status.dismiss_admission):
        assert admit("missing", [pending]).message == "unknown box id missing"
        assert admit("one", [pending, resolved]).outcome == "admit"
        assert admit("two", [pending, resolved]).message == "two: already resolved -> ticket-2"


def test_order_refusal(monkeypatch):
    monkeypatch.setattr(Path, "is_file", lambda self: False)
    checkout = NS(repo=Path("/repo"))
    with pytest.raises(runner.Refusal, match="tickets/item/ticket.md does not exist"):
        entry._order(checkout, "item", "P1", None)


def test_box_verbs(monkeypatch):
    resolved = NS(id="two", resolution=NS(link="ticket-2"))

    class Box:
        def __init__(self, *args, **kwargs):
            pass

        def messages(self):
            return [resolved]

        def get(self, id):
            return resolved

    monkeypatch.setattr(triage, "Box", Box)
    monkeypatch.setattr(triage.Driver, "from_config", lambda *args, **kwargs: NS())
    checkout = NS(config=NS(state_dir=Path("/state")), fs=None, journal=NS(read=lambda: []), env={}, clock=None, sleep=None)
    for call in (triage.triage_pass(checkout, None, ["missing"]), triage.dismiss(checkout, ["missing"])):
        with pytest.raises(UnknownBoxId, match="unknown box id missing"):
            asyncio.run(call)
    assert asyncio.run(triage.dismiss(checkout, ["two"])) == ["two: already resolved -> ticket-2"]


def test_lint_refusal_and_skip(monkeypatch, capsys):
    monkeypatch.setattr(Path, "iterdir", lambda self: iter([]))
    monkeypatch.setattr(Path, "resolve", lambda self: self)
    monkeypatch.setattr(Path, "is_file", lambda self: self.parent.name == "settled")
    git = NS(git_common_dir=AsyncMock(return_value=Path("/repo/.git")), status_porcelain=AsyncMock(return_value=""))
    checkout = NS(repo=Path("/repo"), config=NS(state_dir=Path("/state")), journal=NS(read=lambda: [NS(type=EventType.STATE_TRANSITION, ticket="settled", body={"to": "merged"})]), git=git)
    assert asyncio.run(entry._lint(checkout, ["missing", "settled"])) == 2
    output = capsys.readouterr().out
    assert "tickets/missing/ticket.md: no ticket file" in output
    assert "lint: 0/1 tickets valid" in output


def fake_snapshot_inputs(ctx, history, stems, holder, interrupted):
    """Supply porcelain, claimed text, main text and validation to partial projection fixtures."""
    from dataclasses import replace
    from unittest.mock import patch

    from chupa.tickets import _f

    parsed, invalid = observe.load_tickets(ctx, set())
    dirty, new = observe.uncommitted_tickets(ctx)
    decisions = {**parsed, **{stem: [_f(why, "repair")] for stem, why in invalid.items()}}
    listing = "".join(f"{'??' if stem in new else ' M'} tickets/{stem}/ticket.md\n" for stem in dirty)
    git = NS(status_porcelain=AsyncMock(return_value=listing), _run=AsyncMock(return_value="main text"))

    def validation(stem, text, repo, **kwargs):
        decision = decisions.get(stem)
        if isinstance(decision, list):
            raise TicketInvalid(decision)
        return decision

    with (
        patch.object(Path, "is_file", lambda p: p.parent.name in decisions),
        patch.object(Path, "read_text", lambda *a, **kw: "disk text"),
        patch.object(observe, "_graph", return_value={}),
        patch.object(observe, "validate_ticket", validation),
        patch.object(observe, "_intake_plan_stem", lambda repo, stem, *a, **kw: ("disk text", "claimed text", decisions[stem])),
        patch.object(observe, "frontmatter", return_value={}),
    ):
        inputs, _, _ = SNAPSHOT_INPUTS(replace(ctx, git=git), history, stems, holder, interrupted)
    return inputs, dirty, new


def dispatch_ticket(state="confirmed", depends=()):
    return NS(stem="item", frontmatter=NS(state=state, priority="P1", source="human"), depends=depends, runs_before=(), sections={})


@pytest.mark.parametrize("verb", ["run", "review"])
def test_run_review_admission(verb):
    from chupa.tickets import _f

    admit = getattr(status, verb + "_admission")
    good = dispatch_ticket()
    finding = _f("specific lint failure", "repair that field")
    assert admit("item", [], True, good, good).outcome == "admit"  # Successful claimed pending text is accepted.
    assert admit("item", [], True, good).outcome == "admit"  # A clean committed ticket needs no intake decision.
    kwargs = {"pending": True} if verb == "review" else {}
    refused = admit("item", [], True, good, [finding], **kwargs)
    assert refused.outcome == "refuse" and "failed intake: " in refused.message
    assert "specific lint failure" in refused.message  # Rules out reporting disk validation instead of intake.
    invalid = admit("item", [], True, [finding])
    assert invalid.outcome == "refuse" and "is invalid: " in invalid.message
    assert admit("item", [], False, None).outcome == "refuse"
    stray = admit("item", [], True, good, stray=["staged.py"], **kwargs)
    assert stray.message == "staged changes outside pending ticket files: staged.py"
    if verb == "review":
        assert admit("item", [], True, good, stray=["staged.py"], pending=False).outcome == "admit"
        assert admit("item", [event("running")], True, good).outcome == "admit"
        assert admit("item", [event("already_satisfied")], True, good).message == "item is settled or rejected"
    else:
        assert admit("item", [], True, dispatch_ticket("draft")).message == "item is `state: draft`, not confirmed"
        assert admit("item", [event("merged")], True, good).message == "item is already merged"
        assert admit("item", [], True, dispatch_ticket(depends=("other",))).message == "item depends on unmerged other"
        settled = [NS(type=EventType.STATE_TRANSITION, ticket="other", body={"to": "already_satisfied"})]
        assert admit("item", settled, True, dispatch_ticket(depends=("other",))).outcome == "admit"


@pytest.mark.parametrize("verb", ["run", "review"])
@pytest.mark.parametrize("failure", ["intake", "invalid", "missing", "settled"])
def test_dispatch_verbs_use_admission_refusals(monkeypatch, verb, failure):
    from chupa import tickets

    finding = tickets._f("specific failure", "specific repair")
    events = [event("merged")] if failure == "settled" else []
    result = NS(refused={"item": [finding]} if failure == "intake" else {})
    monkeypatch.setattr(runner, "intake", AsyncMock(return_value=result))
    monkeypatch.setattr(tickets, "intake", AsyncMock(return_value=result))
    monkeypatch.setattr(runner, "ticket_pending", AsyncMock(return_value=True))
    monkeypatch.setattr(Path, "is_file", lambda p: failure != "missing")
    monkeypatch.setattr(Path, "read_text", lambda *a: "disk text")
    good = dispatch_ticket()

    def validate(*args):
        if failure == "invalid":
            raise TicketInvalid([finding])
        return good

    monkeypatch.setattr(runner, "validate_ticket", validate)
    monkeypatch.setattr(entry, "validate_ticket", validate)
    checkout = NS(repo=Path("/fake"), git=NS(_run=AsyncMock(return_value="main text")), journal=NS(read=lambda: events), fs=None)
    expected = getattr(status, verb + "_admission")(
        "item", events, failure != "missing", [finding] if failure == "invalid" else good, [finding] if failure == "intake" else None, **({"pending": True} if verb == "review" else {})
    )
    assert expected.outcome == "refuse"  # A fixture that accidentally admits would hide delegation drift.
    with pytest.raises(runner.Refusal) as exc:
        asyncio.run(runner._admit("item", checkout) if verb == "run" else entry._review(checkout, "item"))
    assert str(exc.value) == f"{expected.message} -- {expected.paved_road}"


@pytest.mark.parametrize("count,invalid_disk", [(1, False), (20, False), (1, True)])
def test_snapshot_reads_one_porcelain_and_shared_graphs(monkeypatch, count, invalid_disk):
    from unittest.mock import Mock

    from chupa import observe, tickets
    from chupa.box import Box

    root = Path("/fake")
    parsed = {f"item-{i}": NS(**{**vars(dispatch_ticket()), "stem": f"item-{i}"}) for i in range(count)}
    files = {root / tickets.ticket_path(stem): "confirmed disk text" for stem in parsed}
    monkeypatch.setattr(Path, "is_file", lambda p: p in files)
    monkeypatch.setattr(Path, "exists", lambda p: p in files)
    monkeypatch.setattr(Path, "read_text", lambda p, **kw: files[p])
    monkeypatch.setattr(Box, "messages", lambda self: [])
    monkeypatch.setattr(observe, "journal", lambda *a: [])
    monkeypatch.setattr(observe, "load_tickets", lambda *a: ({}, {s: "bad disk" for s in parsed}) if invalid_disk else (parsed, {}))
    monkeypatch.setattr(observe, "committed_ticket_shas", lambda *a: {s: "blob" for s in parsed})
    monkeypatch.setattr(observe, "commits", lambda *a: {})
    monkeypatch.setattr(observe, "held", lambda *a: set())
    monkeypatch.setattr(observe, "operator_holds", lambda *a: set())
    monkeypatch.setattr(observe, "running_stems", lambda *a: [])
    monkeypatch.setattr(observe, "lock_holder", lambda *a: None)
    monkeypatch.setattr(observe, "lock_display", lambda *a: ("", None))
    monkeypatch.setattr(observe, "frontmatter", lambda *a: {"state": "confirmed"})
    graphs = Mock(return_value={})
    monkeypatch.setattr(observe, "_graph", graphs)
    monkeypatch.setattr(tickets, "_graph", Mock(side_effect=AssertionError("per-row graph scan")))

    def parse(stem, text, repo):
        if invalid_disk and text == "confirmed disk text":
            raise TicketInvalid([tickets._f("bad disk", "repair disk")])
        return parsed[stem]

    monkeypatch.setattr(tickets, "parse_ticket", parse)
    git = NS(status_porcelain=AsyncMock(return_value=""), _run=AsyncMock(return_value="committed main text"))
    ctx = observe.Context(root, root / "state", root / "config", None, git, None)
    snap = observe.snapshot(ctx)
    assert len(snap["rows"]) == count  # An empty snapshot would trivially avoid per-stem git calls.
    assert all(r["menu"]["chupaRun"] == ("off" if invalid_disk else "on") for r in snap["rows"])
    assert all(r["menu"]["chupaReview"] == "on" for r in snap["rows"])  # Main validation must not reuse load_tickets' invalid disk set.
    git.status_porcelain.assert_awaited_once_with(root, "--untracked-files=all")
    assert graphs.call_args_list == [((root,),), ((root, "Runs before"),)]  # Two section scans, independent of row count.


@pytest.mark.parametrize("settled", [False, True])
def test_intake_and_snapshot_share_pending_plan(monkeypatch, settled):
    from chupa import observe, tickets
    from tests.unit.test_intake_plan import Lock

    root = Path("/fake")
    rel = tickets.ticket_path("item")
    text = "---\nstate: confirmed\nsource: human\npriority: P1\nkind: feature\n---\n"
    files = {root / rel: text, root / "tickets/item/evidence/log": "staged regular evidence"}
    monkeypatch.setattr(Path, "is_file", lambda p: p in files)
    monkeypatch.setattr(Path, "is_symlink", lambda p: False)
    monkeypatch.setattr(Path, "read_text", lambda p, **kw: files[p])
    monkeypatch.setattr(tickets, "_graph", lambda *a: {})
    monkeypatch.setattr(observe, "_graph", lambda *a: {})
    good = dispatch_ticket()
    monkeypatch.setattr(tickets, "parse_ticket", lambda *a: good)
    monkeypatch.setattr(tickets, "_parse_ticket", lambda *a, **kw: good)
    monkeypatch.setattr(tickets, "lint_findings", lambda *a: [])
    monkeypatch.setattr(tickets, "evidence_findings", lambda *a, **kw: [])
    listing = f" M {rel}\nA  tickets/item/evidence/log\n"
    git = NS(_commit_lock=Lock(), status_porcelain=AsyncMock(return_value=listing), _run=AsyncMock(return_value="tickets/item/evidence/log\0"), _commit=AsyncMock(return_value="committed"))
    history = [event("already_satisfied")] if settled else []
    journal = NS(read=lambda: history, append=lambda *a, **kw: None)
    plans = []
    real_plan = tickets._intake_plan_stem

    def plan(*args, **kwargs):
        result = real_plan(*args, **kwargs)
        plans.append(result)
        return result

    monkeypatch.setattr(tickets, "_intake_plan_stem", plan)
    monkeypatch.setattr(observe, "_intake_plan_stem", plan)
    monkeypatch.setattr(observe, "frontmatter", lambda *a: {"state": "confirmed"})
    ctx = observe.Context(root, root / "state", root / "config", None, git, None)
    inputs, dirty, new = observe.ticket_menu_inputs(ctx, history, {"item"}, None, set())
    result = asyncio.run(tickets.intake(root, git, journal, NS(write=lambda *a: pytest.fail("unchanged text must not be written")), stems={"item"}))
    assert plans == [(text, text, good), (text, text, good)]  # Different settled/evidence paths must still use identical decisions.
    assert (dirty, new) == ({"item"}, set())
    assert inputs["item"]["chupaRun"]["intake_decision"] is good
    assert inputs["item"]["chupaRun"]["stray"] == []  # Staged regular evidence cannot be refused as stray.
    assert result.committed == ("item",) and result.refused == {}
    assert git._commit.call_args.kwargs["only"] == [rel, "tickets/item/evidence/log"]
