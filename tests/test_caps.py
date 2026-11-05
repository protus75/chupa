"""Failure-spine cap fold, terminal draws, and parked-stem eligibility."""

import pytest

from chupa import runner
from chupa.__main__ import main
from chupa.artifacts import Cost, Finding, StageResult
from chupa.caps import CAPS, capability, consume, draws, failed_attempts, remaining, spent, spent_reason
from chupa.config import Caps
from chupa.journal import EventType, Journal
from chupa.llm import FakeLLM
from chupa.stages import StagesRun
from chupa.status import reject_queue
from chupa.tickets import validate_ticket
from tests.test_cli import git_out
from tests.test_daemon_composition import production_writer
from tests.test_drain import Clock, Script, commit_ticket, confirmed, drain, journal, make_root
from tests.test_mergequeue import ctx as admission_context
from tests.test_mergequeue import ready
from tests.test_terminal import ENV, STEM, author, clock, diagnosis_reply, repo


def test_attempts_cap_counts_every_failed_terminal(tmp_path):
    j = Journal(tmp_path, clock)
    config = Caps()
    for body in [
        {"to": "running"},
        {"to": "infra_error", "reason": "provider_drought"},
        {"to": "budget_exceeded"},
        {"to": "abandoned"},
        {"to": "merged"},
        {"to": "already_satisfied"},
        {"to": "rejected"},
        {"to": "invalid_artifact"},
    ]:
        j.append(EventType.STATE_TRANSITION, body, ticket="red")
    j.append(EventType.STATE_TRANSITION, {"to": "gate_failed"}, ticket="other")
    assert failed_attempts(j.read(), "red") == 0
    for i, outcome in enumerate(["gate_failed", "premise_failed", "infra_error", "timeout", "gate_failed"]):
        assert spent(config, iter(j.read()), "red") is None
        if i == 4:
            assert spent(config, iter(j.read()), "red", pending={"to": outcome}) == "attempts"
            assert failed_attempts(j.read(), "red") == 4
        j.append(EventType.STATE_TRANSITION, {"to": outcome}, ticket="red")
        assert failed_attempts(j.read(), "red") == i + 1
    assert spent(config, j.read(), "red") == "attempts"
    assert spent_reason("attempts") == "attempts cap spent"
    assert not any(e.type == EventType.CAP_CONSUMED for e in j.read())
    j.append(EventType.SIGNAL, {"signal": "reject_verdict", "verdict": "keep", "actor": "machine"}, ticket="red")
    assert spent(config, j.read(), "red") == "attempts"
    j.append(EventType.SIGNAL, {"signal": "reject_verdict", "verdict": "keep", "actor": "operator"}, ticket="red")
    assert failed_attempts(j.read(), "red") == 0
    assert spent(config, j.read(), "red") is None
    with pytest.raises(ValueError, match="DECLARED_CAPS"):
        consume(j, "red", "attempts", "sha")


@pytest.mark.parametrize("outcome", ["gate_failed", "premise_failed", "infra_error", "timeout"])
def test_attempts_cap_routes_to_reject_queue(repo, monkeypatch, capsys, outcome):
    author(repo)
    j = Journal(repo / ".chupa/state", clock)
    for prior in ["gate_failed", "premise_failed", "infra_error", "timeout"]:
        j.append(EventType.STATE_TRANSITION, {"to": prior}, ticket=STEM)

    async def stage_seam(ctx, ticket):
        return StagesRun(
            attempt=4,
            results={
                "implement": StageResult(
                    outcome=outcome, artifact=None, cost=Cost(), findings=[Finding(code="premise", kind="spec_gap", unit="19.P3.example", message="still failing", paved_road="repair the ticket")]
                )
            },
        )

    monkeypatch.setattr(runner, "run_stages", stage_seam)
    llm = FakeLLM([])
    assert main(["drain"], cwd=repo, env=ENV, clock=clock, pipeline=lambda c: runner.bind(c, llm)) == 0
    events = j.read()
    assert llm.requests == []
    assert failed_attempts(events, STEM) == 5
    assert reject_queue(events)[STEM] == {"to": outcome, "stage": "implement", "reason": "attempts cap spent", "dispatch": "reject_queue", "routed": "reject_queue"}
    assert not any(e.type == EventType.CAP_CONSUMED and e.body["cap"] != "retry" for e in events)
    assert "attempts cap spent (5/5)" in capsys.readouterr().out


@pytest.mark.asyncio
@pytest.mark.parametrize("delivery", ["drive", "consume_result"])
async def test_attempts_cap_skips_conflict_rework(admission_context, monkeypatch, delivery):
    from chupa.mergequeue import ConflictHandoff

    _, writer = production_writer(admission_context, [])
    ctx = writer.ctx
    ticket = await ready(ctx)
    for _ in range(4):
        ctx.driver.journal.append(EventType.STATE_TRANSITION, {"to": "gate_failed"}, ticket=ticket.stem)
    handoff = ConflictHandoff(stem=ticket.stem, reviewed_sha="reviewed", conflicted_paths=[], findings=[Finding(code="post_rebase_regate", message="conflict", paved_road="fresh review")])
    if delivery == "drive":

        async def stages(ctx, ticket):
            return StagesRun(attempt=4, results={"review": StageResult(outcome="ok", artifact=None, findings=[], cost=Cost())})

        async def admission(ticket, *, attempt):
            return handoff

        monkeypatch.setattr(runner, "run_stages", stages)
        assert await runner.drive(ctx, ticket, admission=admission, consume_handoff=writer.consume_handoff) == "gate_failed"
    else:
        await writer.consume_result(ticket, handoff, attempt=4)
    events = ctx.driver.journal.read()
    assert failed_attempts(events, ticket.stem) == 5
    assert reject_queue(events)[ticket.stem]["reason"] == "attempts cap spent"
    assert ctx.driver.llm.requests == []


@pytest.mark.asyncio
@pytest.mark.parametrize("action", ["split", "update", "escalate"])
async def test_attempts_cap_preserves_published_rework(admission_context, action):
    from chupa.daemon import apply_rework
    from tests.test_rework import order, requisition, successors

    _, writer = production_writer(admission_context, [])
    ctx = writer.ctx
    ticket = await ready(ctx)
    for _ in range(4):
        ctx.driver.journal.append(EventType.STATE_TRANSITION, {"to": "gate_failed"}, ticket=ticket.stem)
    text = (ctx.repo / f"tickets/{ticket.stem}/ticket.md").read_text()
    proposals = successors(text.strip()) if action == "split" else [(ticket.stem, text.strip().replace("holds the word ok", "holds ok after narrowing"))] if action == "update" else []
    ctx.driver.llm = FakeLLM([order(action, proposals), *[requisition() for _ in proposals]])
    reworked = await apply_rework(ctx, ticket, [], attempt=4)
    assert reworked.outcome == "ok"
    result = await runner.failure_terminal(ctx, ticket, outcome="gate_failed", stage="merge", findings=[], attempt=4, reworked=reworked, rework_requested=True)
    events = ctx.driver.journal.read()
    assert failed_attempts(events, ticket.stem) == 5
    if action == "split":
        assert result == "rejected" and ticket.stem not in reject_queue(events)
        assert "state: rejected" in (ctx.repo / f"tickets/{ticket.stem}/ticket.md").read_text()
    else:
        assert result == "gate_failed"
        assert reject_queue(events)[ticket.stem] == {"to": "gate_failed", "stage": "merge", "reason": "attempts cap spent", "dispatch": "reject_queue", "routed": "reject_queue"}
    for stem, proposal in proposals:
        assert await ctx.git._run(ctx.repo, "show", f"HEAD:tickets/{stem}/ticket.md") == proposal


def test_fold_counts_only_named_cap_and_stem_across_ticket_revisions(tmp_path):
    j = Journal(tmp_path, clock)
    for body, stem in [
        ({"cap": "infra", "ticket_sha": "first"}, "red"),
        ({"cap": "infra", "ticket_sha": "second"}, "red"),
        ({"cap": "infra"}, "red"),
        ({"cap": "retry", "ticket_sha": "second"}, "red"),
        ({"cap": "infra", "ticket_sha": "second"}, "other"),
    ]:
        j.append(EventType.CAP_CONSUMED, body, ticket=stem)
    j.append(EventType.STATE_TRANSITION, {"to": "infra_error"}, ticket="red")
    events = j.read()
    config = Caps(infra=4, retry=2)
    assert CAPS == ("diagnosis", "retry", "infra", "premise_bounce")
    assert draws(events, "red", "infra") == 3
    assert draws(events, "red", "retry") == 1
    assert draws(events, "other", "infra") == 1
    assert remaining(config, events, "red", "infra") == 1
    assert spent(config, events, "red") is None
    j.append(EventType.CAP_CONSUMED, {"cap": "diagnosis"}, ticket="red")
    assert spent(Caps(diagnosis=1, retry=1, infra=3), j.read(), "red") == "diagnosis"
    assert spent_reason("infra") == "infra cap spent"


def test_invalid_cap_refuses_all_accounting_and_writer(tmp_path):
    j = Journal(tmp_path, clock)
    for operation in (
        lambda: draws(j.read(), "red", "unknown"),
        lambda: remaining(Caps(), j.read(), "red", "unknown"),
        lambda: consume(j, "red", "unknown", "sha"),
    ):
        with pytest.raises(ValueError, match="CAPS"):
            operation()
    assert j.read() == []
    consume(j, "red", "infra", "sha")
    (event,) = j.read()
    assert event.type == EventType.CAP_CONSUMED
    assert event.ticket == "red" and event.body == {"cap": "infra", "ticket_sha": "sha"}


def test_retry_rung_is_rejected_on_other_caps_and_operator_keep_resets_it(repo):
    author(repo)
    ticket = validate_ticket(STEM, (repo / "tickets" / STEM / "ticket.md").read_text(), repo)
    j = Journal(repo / ".chupa" / "state", clock)
    rung = {"tier": "high", "effort": "max"}
    with pytest.raises(ValueError, match="retry"):
        consume(j, STEM, "infra", "sha", rung=rung)
    assert capability(ticket, j.read()) == ("medium", "medium")
    consume(j, STEM, "retry", "sha", rung=rung)
    assert capability(ticket, j.read()) == ("high", "max")
    j.append(EventType.SIGNAL, {"signal": "reject_verdict", "verdict": "keep", "actor": "machine"}, ticket=STEM)
    assert capability(ticket, j.read()) == ("high", "max")
    j.append(EventType.SIGNAL, {"signal": "reject_verdict", "verdict": "keep", "actor": "operator"}, ticket=STEM)
    assert capability(ticket, j.read()) == ("medium", "medium")
    consume(j, STEM, "retry", "sha", rung={"tier": "medium", "effort": "high"})
    assert capability(ticket, j.read()) == ("medium", "high")


def test_crashing_implement_draws_infra_immediately_before_terminal(repo):
    author(repo)
    llm = FakeLLM([RuntimeError("provider crashed"), diagnosis_reply()])
    assert main(["run", STEM], cwd=repo, env=ENV, clock=clock, pipeline=lambda c: runner.bind(c, llm)) == runner.EXIT_TICKET
    assert [request.surface for request in llm.requests if request.surface != "diagnose"] == ["implement"]
    events = [e for e in Journal(repo / ".chupa" / "state", clock).read() if e.ticket == STEM]
    terminal = next(i for i, e in enumerate(events) if e.type == EventType.STATE_TRANSITION and e.body.get("to") == "infra_error")
    sha = git_out(repo, "rev-parse", f"HEAD:tickets/{STEM}/ticket.md").strip()
    infra = next(i for i, e in enumerate(events) if e.type == EventType.CAP_CONSUMED and e.body["cap"] == "infra")
    assert infra < terminal
    assert events[infra].body == {"cap": "infra", "ticket_sha": sha}
    assert all(
        (e.type == EventType.CAP_CONSUMED and e.body["cap"] == "diagnosis")
        or (e.type == EventType.SIGNAL and e.body.get("signal") == "diagnosis")
        or (e.key is not None and ("/diagnose/" in e.key or e.key.endswith("/diagnosis")))
        for e in events[infra + 1 : terminal]
    )
    assert draws(events, STEM, "infra") == 1


@pytest.mark.parametrize("outcome,expected_draws", [("timeout", 1), ("gate_failed", 0)])
def test_other_terminals_draw_only_when_infra(repo, monkeypatch, outcome, expected_draws):
    author(repo)

    async def stage_seam(ctx, ticket):
        return StagesRun(attempt=0, results={"implement": StageResult(outcome=outcome, artifact=None, findings=[], cost=Cost())})

    monkeypatch.setattr(runner, "run_stages", stage_seam)
    assert main(["run", STEM], cwd=repo, env=ENV, clock=clock, pipeline=lambda c: runner.bind(c, FakeLLM([]))) == runner.EXIT_TICKET
    events = [e for e in Journal(repo / ".chupa" / "state", clock).read() if e.ticket == STEM]
    assert events[-1].body == {"to": outcome, "stage": "implement", "reason": outcome, "dispatch": "reject_queue", "routed": "reject_queue"}
    assert draws(events, STEM, "infra") == expected_draws
    if expected_draws:
        sha = git_out(repo, "rev-parse", f"HEAD:tickets/{STEM}/ticket.md").strip()
        assert next(e.body for e in events if e.type == EventType.CAP_CONSUMED) == {"cap": "infra", "ticket_sha": sha}


@pytest.mark.parametrize("cap", ["infra", "diagnosis"])
def test_spent_cap_parks_even_with_retry_remaining(tmp_path, capsys, cap):
    retry_limit = 1 if cap == "diagnosis" else 3
    root = make_root(tmp_path, f"caps: {{{cap}: 2, retry: {retry_limit}}}\n")
    commit_ticket(root, "red", confirmed())
    j = journal(root)
    j.append(EventType.STATE_TRANSITION, {"to": "gate_failed", "stage": "check"}, ticket="red")
    for sha in ("old", "new"):
        consume(j, "red", cap, sha)
    script = Script()
    assert drain(root, script, Clock()) == 0
    assert script.calls == []
    assert f"red: gate_failed at check; {cap} cap spent (2/2)" in capsys.readouterr().out
    assert draws(j.read(), "red", "retry") == 0
