"""Retro measurement aggregation without filesystem or process access."""

import asyncio
from types import SimpleNamespace

from chupa.config import Retro
from chupa.gates import GateReport
from chupa.gates import TestCoverage as Coverage
from chupa.gates import TestTiming as Timing
from chupa.journal import Event, EventType
from chupa.retro import production_evidence, project_window
from chupa.stages import Invoice


def invoice(stem, seconds, percent):
    report = GateReport(
        code="unit", verdict="pass", timing=Timing(seconds=seconds + 1, passed=3, failed=1, skipped=2, slow={"tests/a.py::t": seconds}), coverage=Coverage(percent=percent + 3, files={"a.py": percent})
    )
    return Invoice(produced_by_spec_version=1, produced_at_sha="sha", stem=stem, passed=True, changed_files=[], inserted_lines=0, bypassed=[], reports=[report])


def evidence(invoices, settings=Retro()):
    events = [Event(1, EventType.EFFECT_COMPLETION, "2026-01-01T00:00:00+00:00", item.stem, f"ticket-plane/{item.stem}/0/checks", {"result": {"commit": item.stem}}) for item in invoices]

    class Git:
        async def _run(self, repo, *args):
            return next(item.model_dump_json() for item in invoices if args[-1].startswith(item.stem + ":"))

    checkout = SimpleNamespace(config=SimpleNamespace(retro=settings), git=Git(), repo="unused")
    return asyncio.run(production_evidence(project_window(events), checkout))


def test_measurements_aggregate_in_memory():
    result = evidence([invoice("first", 5.0, 60.0), invoice("second", 2.0, 80.0)])
    assert result["tests"] == {
        "unit": {
            "runs": [{"ticket": "first", "seconds": 6.0, "passed": 3, "failed": 1, "skipped": 2}, {"ticket": "second", "seconds": 3.0, "passed": 3, "failed": 1, "skipped": 2}],
            "slow": {"tests/a.py::t": {"max_seconds": 5.0, "runs": 2}},
        }
    }
    assert result["coverage"] == {"unit": {"percent": 83.0, "files": {"a.py": {"latest": 80.0, "min": 60.0, "runs": 2}}}}


def test_measurements_switches_off():
    result = evidence([invoice("first", 5.0, 60.0)], Retro(test_timing=False, coverage=False))
    assert "tests" not in result and "coverage" not in result


def test_measurements_skip_invoice_without_data():
    empty = invoice("empty", 4.0, 40.0).model_copy(update={"reports": [GateReport(code="other", verdict="pass")]})
    result = evidence([empty, invoice("first", 5.0, 60.0)])
    assert set(result["tests"]) == {"unit"} and set(result["coverage"]) == {"unit"}


def test_retro_default_switches():
    assert Retro().test_timing is True and Retro().coverage is True
