"""Drain admits reports after ticket intake on each loop."""

from types import SimpleNamespace

import pytest

from chupa import drain, triage


@pytest.mark.asyncio
async def test_loop_intakes_reports_after_tickets(monkeypatch):
    calls = []
    checkout = SimpleNamespace(repo=object(), git=object(), fs=object(), journal=SimpleNamespace(read=lambda: []), control=SimpleNamespace(projection=SimpleNamespace(stop_requested=False)))

    async def intake(repo, git, journal, fs, *, stems):
        calls.append(("tickets", repo, git, journal, fs, stems))

    monkeypatch.setattr(drain, "intake", intake)
    monkeypatch.setattr(triage, "report_intake", lambda c: calls.append(("reports", c)))
    run = drain._Drain.__new__(drain._Drain)
    run.c, run.dispatch, run.before_dispatch = checkout, object(), None
    run.report, run.retro, run.provider_deadlines, run.storm_waiting = object(), None, [], False
    run._stopping = lambda: False
    run._offer_material = lambda: None

    async def scan():
        return SimpleNamespace(tickets={})

    run._scan = scan
    run._select = lambda *args: (None, False)
    run._settle = lambda *args: None
    assert await run.run() is run.report
    assert calls == [("tickets", checkout.repo, checkout.git, checkout.journal, checkout.fs, None), ("reports", checkout)]
