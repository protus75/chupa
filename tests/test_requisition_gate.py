"""Dispatch reviews committed ticket content before creating an implementation workspace."""
import asyncio
import json

from chupa import runner
from chupa.caps import draws
from chupa.journal import EventType
from chupa.llm import FakeLLM
from chupa.scheduler import Scheduler
from chupa.status import reject_queue
from chupa.tickets import validate_ticket
from tests.approval import approve
from tests.test_cli import ENV, git_out
from tests.test_drain import Clock, commit_ticket, confirmed, journal, make_root, pause_checkout
from tests.test_stages import implement_reply


def reply(verdict, code=None):
    findings = [] if code is None else [{"code": code, "message": "missing required file", "paved_road": "add the file", "kind": "authoring_error"}]
    return json.dumps({"verdict": verdict, "summary": "reviewed", "findings": findings})


def setup(tmp_path, script):
    root = make_root(tmp_path)
    commit_ticket(root, "gate", confirmed())
    checkout = pause_checkout(root)
    llm = FakeLLM(script)
    writer = runner.bind(checkout, llm)
    return root, checkout, llm, writer


async def dispatch(root, checkout, writer):
    text = (root / 'tickets/gate/ticket.md').read_text()
    sha = await checkout.git.rev_parse(root, 'HEAD:tickets/gate/ticket.md')
    checkout.journal.append(EventType.STATE_TRANSITION, {'to': 'running', 'ticket_sha': sha}, ticket='gate')
    return await writer(validate_ticket('gate', text, root))


def test_unreviewed_ticket_is_reviewed_once_then_runs(tmp_path):
    root, checkout, llm, writer = setup(tmp_path, [reply('approve'), implement_reply('premise_failed', [{'code': 'premise', 'message': 'cannot build', 'paved_road': 'repair'}])])
    asyncio.run(dispatch(root, checkout, writer))
    assert [r.surface for r in llm.requests] == ['requisition_review', 'implement']


def test_approved_content_runs_without_review(tmp_path):
    root, checkout, llm, writer = setup(tmp_path, [implement_reply('premise_failed', [{'code': 'premise', 'message': 'cannot build', 'paved_road': 'repair'}])])
    approve(root, 'gate', checkout.clock)
    asyncio.run(dispatch(root, checkout, writer))
    assert [r.surface for r in llm.requests] == ['implement']


def test_snag_parks_before_implement(tmp_path):
    from chupa.drain import parked_blob
    root, checkout, llm, writer = setup(tmp_path, [reply('snag', 'missing_file')])
    assert asyncio.run(dispatch(root, checkout, writer)) == 'premise_failed'
    events = checkout.journal.read()
    terminal = [e.body for e in events if e.type == EventType.STATE_TRANSITION][-1]
    assert terminal['stage'] == 'requisition' and 'missing required file' in terminal['reason']
    assert 'dispatch' not in terminal and 'routed' not in terminal
    assert [r.surface for r in llm.requests] == ['requisition_review']
    assert not writer.ctx.worktree('gate').exists() and not reject_queue(events)
    assert all(draws(events, 'gate', cap) == 0 for cap in ('retry', 'diagnosis', 'premise_bounce'))
    sha = git_out(root, 'rev-parse', 'HEAD:tickets/gate/ticket.md').strip()
    assert parked_blob(events, 'gate') == sha
    from chupa.__main__ import main
    assert main(['drain'], cwd=root, env=ENV, clock=checkout.clock, pipeline=lambda c: runner.bind(c, llm)) == 0
    assert [r.surface for r in llm.requests] == ['requisition_review']


def test_render_feasibility_snag_proceeds_to_implement(tmp_path):
    root, checkout, llm, writer = setup(tmp_path, [reply('snag', 'render_feasibility'), implement_reply('premise_failed', [{'code': 'premise', 'message': 'cannot build', 'paved_road': 'repair'}])])
    asyncio.run(dispatch(root, checkout, writer))
    assert [r.surface for r in llm.requests] == ['requisition_review', 'implement']


def test_edit_releases_and_reviews_the_new_content(tmp_path):
    from chupa.drain import parked_blob
    root, checkout, llm, writer = setup(tmp_path, [reply('snag', 'missing_file'), reply('approve'), implement_reply('premise_failed', [{'code': 'premise', 'message': 'cannot build', 'paved_road': 'repair'}])])
    assert asyncio.run(dispatch(root, checkout, writer)) == 'premise_failed'
    path = root / 'tickets/gate/ticket.md'
    path.write_text(path.read_text().replace('## Goal / Why', '## Goal / Why\nEdited content.'))
    git_out(root, 'add', str(path.relative_to(root)))
    git_out(root, 'commit', '-m', 'edit ticket')
    sha = git_out(root, 'rev-parse', 'HEAD:tickets/gate/ticket.md').strip()
    assert parked_blob(checkout.journal.read(), 'gate') != sha
    from chupa.__main__ import main
    assert main(['drain'], cwd=root, env=ENV, clock=checkout.clock, pipeline=lambda c: runner.bind(c, llm)) == 0
    assert [r.surface for r in llm.requests] == ['requisition_review', 'requisition_review', 'implement']
    verdicts = [e.body['ticket_sha'] for e in checkout.journal.read() if e.body.get('signal') == 'requisition_verdict']
    assert len(verdicts) == 2 and verdicts[0] != sha and verdicts[1] == sha


def test_serve_holds_a_parked_ticket(tmp_path):
    root, checkout, llm, writer = setup(tmp_path, [reply('snag', 'missing_file')])
    asyncio.run(dispatch(root, checkout, writer))
    calls = []
    async def exercise():
        async def sha(stem):
            return await checkout.git.rev_parse(root, f'HEAD:tickets/{stem}/ticket.md')
        async def run(ticket):
            calls.append(ticket.stem)
        scheduler = Scheduler(checkout.journal, run, ticket_sha=sha, quarantined=set, drought_parked=set, completed_unmerged=lambda: 0, max_unmerged=1)
        scheduler.update(validate_ticket('gate', (root / 'tickets/gate/ticket.md').read_text(), root))
        assert await scheduler.dispatch_next() is None
        path = root / 'tickets/gate/ticket.md'
        path.write_text(path.read_text().replace('## Goal / Why', '## Goal / Why\nEdited content.'))
        git_out(root, 'add', 'tickets/gate/ticket.md')
        git_out(root, 'commit', '-m', 'edit ticket')
        assert (await scheduler.dispatch_next()).stem == 'gate'
    asyncio.run(exercise())
    assert calls == ['gate']
