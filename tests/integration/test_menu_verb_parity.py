"""The emitted table and real verb inputs agree on the same files and journal."""

import asyncio
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock

import pytest

from chupa import __main__ as entry
from chupa import observe, runner, status, tickets
from chupa.box import Box, Resolution
from chupa.config import load_config
from chupa.git import Git
from chupa.journal import EventType, Journal
from chupa.lockfile import Lockfile
from chupa.seams import LocalFileSystem, SubprocessExec
from tests.integration.test_cli import ENV
from tests.integration.test_drain import Clock, confirmed, make_root
from tests.integration.test_git import commit_lock


@pytest.fixture
def world(tmp_path):
    root = make_root(tmp_path)
    state = root / ".chupa/state"
    git = Git(SubprocessExec(), env=ENV, timeout=30, commit_lock=commit_lock(state))
    journal = Journal(state, Clock())
    fs = LocalFileSystem()
    checkout = NS(repo=root, git=git, journal=journal, fs=fs, config=load_config(None, cwd=root), clock=Clock(), env=ENV, sleep=None)
    ctx = observe.Context(root, state, root / "config.yaml", SubprocessExec(), git, ENV)

    def write(stem, text, *, commit=True, stage=False):
        path = root / tickets.ticket_path(stem)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        if commit:
            asyncio.run(git.commit(root, "ticket " + stem, only=[tickets.ticket_path(stem)]))
        elif stage:
            asyncio.run(git.add(root, [tickets.ticket_path(stem)]))
        return path

    def transition(stem, state, **body):
        journal.append(EventType.STATE_TRANSITION, {"to": state, **body}, ticket=stem)

    return NS(root=root, state=state, git=git, journal=journal, fs=fs, ctx=ctx, checkout=checkout, write=write, transition=transition)


def validation(w, stem, text):
    try:
        return tickets.validate_ticket(stem, text, w.root)
    except tickets.TicketInvalid as exc:
        return exc.findings


def verb_inputs(w, stem, row, live):
    """Compute the inputs as verbs do, independently of snapshot's input builder."""
    history = w.journal.read()
    path = w.root / tickets.ticket_path(stem)
    entries = tickets._porcelain(asyncio.run(w.git.status_porcelain(w.root, "--untracked-files=all")))
    pending, evidence, stray = asyncio.run(tickets.intake_pending(w.root, w.git, entries))
    plan = tickets._intake_plan_stem(w.root, stem, pending[stem], evidence[stem], status.last_states(history).get(stem)) if stem in pending else None
    pending_flag = asyncio.run(runner.ticket_pending(w.git, w.root, stem))
    disk = validation(w, stem, plan[1] if plan else path.read_text())
    main = validation(w, stem, plan[1] if plan else asyncio.run(w.git._run(w.root, "show", f"main:{tickets.ticket_path(stem)}")))
    from chupa.reconcile import orphans

    common = dict(
        stem=stem,
        events=history,
        file_exists=path.is_file(),
        intake_decision=plan[2] if plan else None,
        stray=stray,
        pending=pending_flag,
        draft=observe.frontmatter(path).get("state") == "draft",
        interrupted=set() if live else set(orphans(history)),
        lock_holder=object() if live else None,
        section=row["section"],
    )
    return {
        key: dict(
            common,
            ticket=main
            if key == "chupaReview"
            else validation(w, stem, path.read_text())
            if key == "chupaPriority"
            else validation(w, stem, tickets.order(path.read_text(), priority=None, runs_before=[]))
            if key == "chupaRunsBefore"
            else disk,
        )
        for key, spec in observe.MENU.items()
        if spec.kind == "ticket"
    }


# Explicit outcomes distinguish shared wrong admissions from correct table wiring.
@pytest.mark.parametrize(
    "case,run,review,order,lint",
    [
        ("draft", False, True, True, True),
        ("new", True, True, True, True),
        ("staged-new", True, True, True, True),
        ("dirty", True, True, True, True),
        ("pending-lint", False, False, True, True),
        ("depends-cycle", False, False, False, True),
        ("runs-before-cycle", False, False, False, True),
        ("stray-clean", False, True, True, True),
        ("stray-row-file", False, False, True, True),
        ("staged-evidence", True, True, True, True),
        ("settled-missing-evidence", False, False, False, False),
        ("queued", True, True, True, True),
        ("blocked", False, True, True, True),
        ("content-parked", True, True, True, True),
        ("reject", True, True, True, True),
        ("running", True, True, False, True),
        ("interrupted", True, True, True, True),
        ("merged", False, False, False, False),
        ("invalid", False, False, False, True),
    ],
)
def test_menu_matches_verbs(world, capsys, case, run, review, order, lint):
    w = world
    text = confirmed()
    if case in {"draft", "new", "staged-new"}:
        text = text.replace("state: confirmed", "state: draft")
    if case == "blocked":
        w.write("peer", confirmed())
        text = confirmed("- peer")
    if case == "depends-cycle":
        # The peer exists before validation; both grammar parses succeed but the graph closes.
        w.write("peer", confirmed("- item"))
        text = confirmed("- peer")
    if case == "runs-before-cycle":
        w.write("peer", confirmed() + "\n## Runs before\n- item\n")
        w.transition("peer", "merged")
        text = confirmed("- peer") + "\n## Runs before\n- peer\n"
    if case == "invalid":
        text = "not a ticket"
    if case == "settled-missing-evidence":
        text = text.replace("kind: feature", "kind: bug") + "\n## Regression\n```\npython tests/repro.py\n```\n- carries: tests/repro.py\n"
        text = text.replace("- chupa/thing.py\n\n## Acceptance", "- chupa/thing.py\n- tests/repro.py\n\n## Acceptance")
        (w.root / "tests").mkdir()
        (w.root / "tests/repro.py").write_text("pass\n")
    path = w.write("item", text, commit=case not in {"new", "staged-new"}, stage=case == "staged-new")
    if case in {"dirty", "pending-lint", "staged-evidence", "settled-missing-evidence"}:
        path.write_text(text.replace("returns ok", "returns the changed value"))
    if case == "pending-lint":
        path.write_text(path.read_text().replace("- chupa/thing.py\n\n## Acceptance", "- chupa/thing.py\n- chupa/status.py\n\n## Acceptance"))
        # A valid grammar with a unit-coverage fence finding, rather than invalid text.
        (w.root / "chupa/status.py").write_text("")
        (w.root / "test-gate.toml").write_text('[coverage]\ndefault = 90\n[coverage.files]\n"chupa/status.py" = 90\n')
    if case in {"stray-clean", "stray-row-file"}:
        (w.root / "outside.py").write_text("staged\n")
        asyncio.run(w.git.add(w.root, ["outside.py"]))
        if case == "stray-row-file":
            path.with_name("untracked.txt").write_text("pending row\n")
    if case == "staged-evidence":
        evidence = path.parent / "evidence/log"
        evidence.parent.mkdir()
        evidence.write_text("regular staged evidence\n")
        asyncio.run(w.git.add(w.root, [str(evidence.relative_to(w.root))]))
    if case == "settled-missing-evidence":
        plan = tickets._intake_plan_stem(w.root, "item", False, [], "already_satisfied")
        assert not isinstance(plan[2], list)  # Intake exempts settled evidence, while Run must not.
        assert any("no evidence file" in f.message for f in validation(w, "item", path.read_text()))
    if case == "content-parked":
        blob = asyncio.run(w.git.rev_parse(w.root, "HEAD:tickets/item/ticket.md"))
        w.transition("item", "running", ticket_sha=blob)
        w.transition("item", "premise_failed", stage="requisition")
    if case == "reject":
        w.transition("item", "gate_failed", routed="reject_queue")
    if case in {"running", "interrupted", "merged", "settled-missing-evidence"}:
        w.transition("item", "already_satisfied" if case == "settled-missing-evidence" else "running" if case == "interrupted" else case)
    box = Box(w.state / "box", w.fs)
    pending, _ = box.enqueue(message_class="suggestion", origin="operator", summary="Pending")
    resolved, _ = box.enqueue(message_class="suggestion", origin="operator", summary="Resolved")
    box.resolve(resolved, Resolution(kind="ticket", link="item"))
    live = case == "running"
    lock = Lockfile(w.state, verb="drain", instance_id="test", clock=Clock())
    if live:
        lock.acquire()
    try:
        snap = observe.snapshot(w.ctx)
        row = next(r for r in snap["rows"] if r["stem"] == "item")
        assert set(row["menu"]) == {k for k, spec in observe.MENU.items() if spec.kind == "ticket"}
        assert {key for key, spec in observe.MENU.items() if spec.extension_only} == {"chupaAskDiagnose", "chupaAskReview", "chupaAskDrafts"}
        inputs = verb_inputs(w, "item", row, live)
        for key, spec in observe.MENU.items():
            if not spec.extension_only:
                assert callable(spec.admission), key  # A new verb key cannot omit admission.
            if spec.kind == "ticket" and not spec.extension_only:
                admitted = spec.admission(**{name: inputs[key][name] for name in spec.inputs}).outcome == "admit"
                assert (row["menu"][key] in {"on", "locked"}) == admitted, (case, key)
        for key, expected in (("chupaRun", run), ("chupaReview", review), ("chupaPriority", order), ("chupaRunsBefore", order or case == "runs-before-cycle"), ("chupaLint", lint)):
            assert (row["menu"][key] != "off") == expected, (case, key)
        if live:
            assert row["menu"]["chupaRun"] == "locked"
            assert row["menu"]["chupaReview"] == "on"  # Running rows remain reviewable.
        for row in snap["box"]:
            assert set(row["menu"]) == {k for k, spec in observe.MENU.items() if spec.kind == "box"}
            for key, value in row["menu"].items():
                decision = observe.MENU[key].admission(row["id"], box.messages())
                assert value == ("locked" if live else "on") if decision.outcome == "admit" else value == "off"
        assert next(r for r in snap["box"] if r["id"] == resolved)["menu"]["chupaDismiss"] == "off"
    finally:
        if live:
            lock.release()
    assert entry.main(["dismiss", resolved], cwd=w.root, env=ENV, clock=Clock()) == 0
    assert f"{resolved}: already resolved -> item" in capsys.readouterr().out


def test_lock_only_gates_writer_actions(world):
    w = world
    w.write("ready", confirmed())
    w.write("draft", confirmed().replace("state: confirmed", "state: draft"))
    Box(w.state / "box", w.fs).enqueue(message_class="suggestion", origin="operator", summary="Work")
    lock = Lockfile(w.state, verb="drain", instance_id="test", clock=Clock())
    lock.acquire()
    try:
        snap = observe.snapshot(w.ctx)
        rows = {r["stem"]: r for r in snap["rows"]}
        assert rows["ready"]["menu"]["chupaRun"] == "locked"
        for key in ("chupaReview", "chupaLint", "chupaPriority", "chupaRunsBefore"):
            assert rows["ready"]["menu"][key] == "on", key
        assert {k: rows["draft"]["menu"][k] for k in ("chupaConfirm", "chupaReject")} == {"chupaConfirm": "on", "chupaReject": "on"}
        assert snap["box"][0]["menu"] == {"chupaTriage": "locked", "chupaDismiss": "locked"}
    finally:
        lock.release()


def test_verb_refusals_and_lint_summary(world, capsys):
    w = world
    for verb in ("review", "run", "order"):
        assert entry.main([verb, "missing", *(["--priority", "P1"] if verb == "order" else [])], cwd=w.root, env=ENV, clock=Clock(), pipeline=lambda c: AsyncMock()) == 2
        output = capsys.readouterr()
        assert "tickets/missing/ticket.md does not exist" in output.err
    for verb in ("triage", "dismiss"):
        assert entry.main([verb, "missing"], cwd=w.root, env=ENV, clock=Clock()) == 2
        assert "unknown box id missing" in capsys.readouterr().err
    w.write("done", confirmed())
    w.transition("done", "merged")
    assert entry.main(["lint", "missing", "done"], cwd=w.root, env=ENV, clock=Clock()) == 2
    output = capsys.readouterr().out
    assert "tickets/missing/ticket.md: no ticket file" in output
    assert "lint: 0/1 tickets valid" in output  # A no-op must not add a second total.
