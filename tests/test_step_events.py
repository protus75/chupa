import asyncio
import json

from chupa import runner
from chupa.stages import run_stages
from chupa.tickets import validate_ticket
from tests.test_merge import context, repo
from tests.test_stages import STEM, agent, author, verdict


def stage_events(ctx, surface):
    log = ctx.config.state_dir / "engine.log"
    return [e for line in log.read_text().splitlines() if (e := json.loads(line)).get("surface") == surface and e["event"] in ("stage_start", "stage_end")]


def test_check_events_on_scope_violation(repo):
    author(repo)
    ctx = context(repo, [agent({"chupa/thing.py": "ok\n", "chupa/other.py": "outside\n"})])
    ticket = validate_ticket(STEM, (repo / "tickets" / STEM / "ticket.md").read_text(), repo)
    run = asyncio.run(run_stages(ctx, ticket))
    assert run.last[1].outcome == "gate_failed"  # A successful Check would not prove the violation.
    events = stage_events(ctx, "check")
    assert [(e["event"], e.get("outcome"), e["stem"], e["attempt"]) for e in events] == [
        ("stage_start", None, STEM, run.attempt), ("stage_end", "gate_failed", STEM, run.attempt)
    ]  # Missing, reversed, or incorrectly attributed events differ.


def test_merge_events_on_drive(repo):
    author(repo)
    ctx = context(repo, [agent({"chupa/thing.py": "ok\n"}), verdict()])
    ticket = validate_ticket(STEM, (repo / "tickets" / STEM / "ticket.md").read_text(), repo)
    assert asyncio.run(runner.drive(ctx, ticket)) == "merged"  # A stopped run never reaches admission.
    events = stage_events(ctx, "merge")
    assert [(e["event"], e.get("outcome"), e["stem"], e["attempt"]) for e in events] == [
        ("stage_start", None, STEM, 0), ("stage_end", "ok", STEM, 0)
    ]  # Missing, reversed, or incorrectly attributed events differ.
