import asyncio
import json

import pytest

from chupa import __main__ as entry
from chupa.control import ControlRequest, publish_request
from chupa.drain import drain
from chupa.journal import EventType
from tests.integration.test_cli import ENV, ticket
from tests.integration.test_drain import commit_ticket, confirmed, pause_checkout, root
from tests.integration.test_drain_reentry import NoChild


async def until(predicate):
    async def wait():
        while not predicate():
            await asyncio.sleep(0.02)

    await asyncio.wait_for(wait(), 5)


def decisions(checkout, stem):
    return [e.body for e in checkout.journal.read() if e.body.get("kind") == "control_decision" and e.body.get("stem") == stem]


@pytest.mark.asyncio
@pytest.mark.parametrize("verb", ["confirm", "reject"])
async def test_live_admission(root, verb):
    commit_ticket(root, "aa", confirmed(priority="P0"))
    commit_ticket(root, "dd", ticket().replace("---\npriority:", "---\nstate: draft\nsource: human\npriority:", 1))
    checkout = pause_checkout(root)
    entered, release = asyncio.Event(), asyncio.Event()
    calls = []

    class Dispatch:
        async def __call__(self, item):
            calls.append(item.stem)
            if item.stem == "aa":
                entered.set()
                await release.wait()
            checkout.journal.append(EventType.STATE_TRANSITION, {"to": "merged"}, ticket=item.stem)
            return "merged"

        async def abort_current(self):
            pytest.fail("unexpected abort")

    task = asyncio.create_task(drain(checkout, Dispatch(), reexec=NoChild()))
    try:
        await asyncio.wait_for(entered.wait(), 5)
        assert await asyncio.to_thread(entry.main, [verb, "dd", "--extension"], cwd=root, env=ENV, clock=checkout.clock) == 0
        state = "confirmed" if verb == "confirm" else "rejected"
        path = root / "tickets/dd/ticket.md"
        await until(
            lambda: (
                f"state: {state}" in path.read_text()
                and any(e.ticket == "dd" and (e.body.get("signal") == "draft_confirmed" if verb == "confirm" else e.body.get("to") == "rejected") for e in checkout.journal.read())
            )
        )
        assert decisions(checkout, "dd")[-1]["decision"] == "accepted"
        assert calls == ["aa"] and not task.done()
        release.set()
        await asyncio.wait_for(task, 5)
        assert calls == (["aa", "dd"] if verb == "confirm" else ["aa"])
    finally:
        release.set()
        if not task.done():
            task.cancel()
        await asyncio.gather(task, return_exceptions=True)


@pytest.mark.asyncio
async def test_unknown_and_settled(root):
    commit_ticket(root, "aa", confirmed(priority="P0"))
    commit_ticket(root, "done", confirmed())
    checkout = pause_checkout(root)
    checkout.journal.append(EventType.STATE_TRANSITION, {"to": "merged"}, ticket="done")
    original = (root / "tickets/done/ticket.md").read_text()
    entered, release = asyncio.Event(), asyncio.Event()

    class Dispatch:
        async def __call__(self, item):
            entered.set()
            await release.wait()
            checkout.journal.append(EventType.STATE_TRANSITION, {"to": "merged"}, ticket=item.stem)
            return "merged"

        async def abort_current(self):
            pytest.fail("unexpected abort")

    task = asyncio.create_task(drain(checkout, Dispatch(), reexec=NoChild()))
    try:
        await asyncio.wait_for(entered.wait(), 5)
        for stem in ("unknown", "done"):
            assert await asyncio.to_thread(entry.main, ["confirm", stem, "--extension"], cwd=root, env=ENV, clock=checkout.clock) == 0
        log = checkout.config.state_dir / "engine.log"
        await until(lambda: decisions(checkout, "unknown") and decisions(checkout, "done") and "verdict_refused" in log.read_text())
        assert decisions(checkout, "unknown")[-1]["decision"] == "stale"
        assert decisions(checkout, "unknown")[-1]["reason"] == "name a journaled stem or an existing ticket.md"
        assert decisions(checkout, "done")[-1]["decision"] == "accepted"
        assert any(json.loads(line).get("event") == "verdict_refused" and json.loads(line).get("stem") == "done" for line in log.read_text().splitlines())
        assert (root / "tickets/done/ticket.md").read_text() == original
    finally:
        release.set()
        await asyncio.wait_for(task, 5)


@pytest.mark.asyncio
async def test_confirm_during_pause(root):
    commit_ticket(root, "aa", confirmed())
    commit_ticket(root, "dd", ticket().replace("---\npriority:", "---\nstate: draft\nsource: human\npriority:", 1))
    checkout = pause_checkout(root)
    entered, release = asyncio.Event(), asyncio.Event()

    async def before():
        entered.set()
        await release.wait()

    class Dispatch:
        async def __call__(self, item):
            checkout.journal.append(EventType.STATE_TRANSITION, {"to": "merged"}, ticket=item.stem)
            return "merged"

        async def abort_current(self):
            pytest.fail("unexpected abort")

    task = asyncio.create_task(drain(checkout, Dispatch(), reexec=NoChild(), before_dispatch=before))
    try:
        await asyncio.wait_for(entered.wait(), 5)
        publish_request(checkout.config.state_dir, ControlRequest("pause-test", checkout.control.inbox.lifecycle_id, "pause", None), checkout.fs)
        release.set()
        await until(lambda: checkout.control.projection.pause_id == "pause-test")
        assert await asyncio.to_thread(entry.main, ["confirm", "dd", "--extension"], cwd=root, env=ENV, clock=checkout.clock) == 0
        await until(lambda: "state: confirmed" in (root / "tickets/dd/ticket.md").read_text())
        assert decisions(checkout, "dd")[-1]["decision"] == "accepted" and not task.done()
        publish_request(checkout.config.state_dir, ControlRequest("resume-test", checkout.control.inbox.lifecycle_id, "resume", "pause-test"), checkout.fs)
        await asyncio.wait_for(task, 5)
    finally:
        release.set()
        if not task.done():
            task.cancel()
        await asyncio.gather(task, return_exceptions=True)
