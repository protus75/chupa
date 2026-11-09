"""Pytest per-test results and their strict reader."""

import json
import math
from dataclasses import dataclass
from pathlib import Path

from chupa.seams import LocalFileSystem


class ResultsInvalid(ValueError):
    """A results document does not match the supported schema."""


@dataclass(frozen=True)
class Results:
    tests: dict[str, str]
    seconds: dict[str, float]


_results: dict[str, str] = {}
_seconds: dict[str, float] = {}


def pytest_addoption(parser):
    parser.addoption("--chupa-results", metavar="PATH", default=None)


def pytest_configure(config):
    _results.clear()
    _seconds.clear()


def pytest_runtest_logreport(report):
    _seconds[report.nodeid] = _seconds.get(report.nodeid, 0.0) + report.duration
    outcome = report.outcome
    previous = _results.get(report.nodeid, "passed")
    if outcome == "failed" or previous == "failed":
        _results[report.nodeid] = "failed"
    elif outcome == "skipped" or previous == "skipped":
        _results[report.nodeid] = "skipped"
    else:
        _results[report.nodeid] = "passed"


def pytest_sessionfinish(session, exitstatus):
    config = session.config
    path = config.getoption("--chupa-results")
    if path is not None and not hasattr(config, "workerinput"):
        data = {"schema_version": 2, "tests": _results, "seconds": _seconds}
        LocalFileSystem().write(Path(path), json.dumps(data, sort_keys=True).encode("utf-8"))


def read_results(text: str) -> Results:
    try:
        data = json.loads(text)
    except (ValueError, TypeError) as exc:
        raise ResultsInvalid(f"invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ResultsInvalid("results must be an object")
    version = data.get("schema_version")
    if type(version) is not int or version != 2:
        raise ResultsInvalid("schema_version must be integer 2")
    expected = {"schema_version", "tests", "seconds"}
    if set(data) != expected:
        raise ResultsInvalid("unexpected results keys")
    tests = data["tests"]
    if not isinstance(tests, dict):
        raise ResultsInvalid("tests must be an object")
    seconds = data["seconds"]
    if not isinstance(seconds, dict) or seconds.keys() != tests.keys():
        raise ResultsInvalid("seconds keys must match tests keys")
    if any(type(value) is not float or not math.isfinite(value) or value < 0 for value in seconds.values()):
        raise ResultsInvalid("seconds values must be finite nonnegative floats")
    for nodeid, outcome in tests.items():
        if not isinstance(nodeid, str) or not nodeid.strip():
            raise ResultsInvalid("test node ID must be a nonblank string")
        if not isinstance(outcome, str) or outcome not in {"passed", "failed", "skipped"}:
            raise ResultsInvalid(f"invalid outcome for {nodeid!r}: {outcome!r}")
    return Results(tests, seconds)


def slow_tests(seconds: dict[str, float], floor: float, limit: int) -> dict[str, float]:
    return dict(sorted(((node, value) for node, value in seconds.items() if value >= floor), key=lambda item: (-item[1], item[0]))[:limit])
