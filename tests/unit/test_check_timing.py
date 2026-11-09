import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest

from chupa import testreport
from chupa.config import ConfigError, MechanicalCheck, _check_references
from chupa.gates import GateReport
from chupa.gates import TestCoverage as Coverage
from chupa.gates import TestTiming as Timing
from chupa.stages import run_host_command


def test_slow_tests():
    assert testreport.slow_tests({"z": 2.0, "b": 3.0, "a": 3.0, "x": 0.9}, 1.0, 2) == {"a": 3.0, "b": 3.0}
    assert list(testreport.slow_tests({"z": 2.0, "b": 3.0, "a": 3.0}, 1.0, 3)) == ["a", "b", "z"]


def test_writer_sums_phases(monkeypatch):
    captured = []
    monkeypatch.setattr(testreport, "LocalFileSystem", lambda: SimpleNamespace(write=lambda path, data: captured.append(data)))
    testreport.pytest_configure(None)
    for duration in (0.5, 1.0, 2.0):
        testreport.pytest_runtest_logreport(SimpleNamespace(nodeid="a", outcome="passed", duration=duration))
    testreport.pytest_sessionfinish(SimpleNamespace(config=SimpleNamespace(getoption=lambda name: "r.json")), 0)
    result = testreport.read_results(captured[0].decode())
    assert result.tests == {"a": "passed"} and result.seconds == {"a": 3.5}


def test_report_dump():
    base = GateReport(code="x", verdict="pass")
    assert base.model_dump_json() == '{"code":"x","verdict":"pass","findings":[],"autofix_applied":false}'
    report = GateReport(code="x", verdict="pass", timing=Timing(seconds=2.0, passed=1, failed=0, skipped=0, slow={"a": 1.5}), coverage=Coverage(percent=80.0, files={"a": 50.0}))
    assert report.model_dump()["timing"]["slow"] == {"a": 1.5}
    assert report.model_dump()["coverage"] == {"percent": 80.0, "files": {"a": 50.0}}


@pytest.mark.parametrize("field,value", [("slow_test_seconds", 2.0), ("slow_test_limit", 2)])
def test_bounds_require_results(field, value):
    entry = MechanicalCheck(code="x", argv=["test"], trigger="always", severity="hard", **{field: value})
    cfg = SimpleNamespace(retro=SimpleNamespace(enabled=False, spikes=SimpleNamespace(kinds=[])), review=SimpleNamespace(mechanical=[entry]))
    with pytest.raises(ConfigError) as exc:
        _check_references(Path("config"), cfg)
    assert exc.value.key == f"review.mechanical.0.{field}"


def test_command_clock():
    now = datetime(2020, 1, 1)
    times = iter([now, now + timedelta(seconds=2.5)])

    async def run(*args, **kwargs):
        return 0, "ok", ""

    ctx = SimpleNamespace(
        driver=SimpleNamespace(clock=lambda: next(times), spool=SimpleNamespace(write=lambda *args: None), redactor=SimpleNamespace(scrub=lambda x: x)),
        exec_=SimpleNamespace(run=run),
        worktree=lambda stem: Path("."),
        env={},
        config=SimpleNamespace(providers=[]),
    )
    result, report = asyncio.run(run_host_command(ctx, SimpleNamespace(stem="x", stuck_minutes=1), 0, ["test"], "x", "log"))
    assert result.seconds == 2.5 and report.verdict == "pass"
