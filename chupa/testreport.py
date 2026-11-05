"""Pytest per-test results and their strict reader."""

import json
from pathlib import Path

from chupa.seams import LocalFileSystem


class ResultsInvalid(ValueError):
    """A results document does not match the supported schema."""


_results: dict[str, str] = {}


def pytest_addoption(parser):
    parser.addoption("--chupa-results", metavar="PATH", default=None)


def pytest_configure(config):
    _results.clear()


def pytest_runtest_logreport(report):
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
        data = {"schema_version": 1, "tests": _results}
        LocalFileSystem().write(Path(path), json.dumps(data, sort_keys=True).encode("utf-8"))


def read_results(text: str) -> dict[str, str]:
    try:
        data = json.loads(text)
    except (ValueError, TypeError) as exc:
        raise ResultsInvalid(f"invalid JSON: {exc}") from exc
    if not isinstance(data, dict) or set(data) != {"schema_version", "tests"}:
        raise ResultsInvalid("expected only schema_version and tests keys")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ResultsInvalid("schema_version must be integer 1")
    tests = data["tests"]
    if not isinstance(tests, dict):
        raise ResultsInvalid("tests must be an object")
    for nodeid, outcome in tests.items():
        if not isinstance(nodeid, str) or not nodeid.strip():
            raise ResultsInvalid("test node ID must be a nonblank string")
        if not isinstance(outcome, str) or outcome not in {"passed", "failed", "skipped"}:
            raise ResultsInvalid(f"invalid outcome for {nodeid!r}: {outcome!r}")
    return tests
