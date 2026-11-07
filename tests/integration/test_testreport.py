import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from chupa.testreport import ResultsInvalid, pytest_sessionfinish, read_results

pytest_plugins = ["pytester"]


@pytest.fixture
def inner_tests(pytester, monkeypatch):
    monkeypatch.setenv("PYTHONPATH", str(Path(__file__).resolve().parents[2]), prepend=os.pathsep)
    pytester.makepyfile(
        test_a="""
        import pytest

        @pytest.fixture
        def broken_teardown():
            yield
            raise RuntimeError("teardown")

        class TestC:
            def test_m(self):
                pass

        def test_fail():
            assert False

        def test_skip():
            pytest.skip("skip")

        def test_teardown(broken_teardown):
            pass
    """
    )
    return pytester


@pytest.mark.parametrize("workers", ["0", "2"])
def test_reports_all_phases_and_nodeids(inner_tests, workers):
    result = inner_tests.runpytest_subprocess("-p", "chupa.testreport", "--chupa-results", "r.json", "-n", workers)
    assert result.ret == 1
    data = json.loads((inner_tests.path / "r.json").read_text())
    assert data == {
        "schema_version": 1,
        "tests": {
            "test_a.py::TestC::test_m": "passed",
            "test_a.py::test_fail": "failed",
            "test_a.py::test_skip": "skipped",
            "test_a.py::test_teardown": "failed",
        },
    }
    assert read_results(json.dumps(data)) == data["tests"]


def test_no_option_writes_no_file(inner_tests):
    result = inner_tests.runpytest_subprocess("-p", "chupa.testreport", "-n", "0")
    result.assert_outcomes(passed=2, failed=1, skipped=1, errors=1)
    assert not (inner_tests.path / "r.json").exists()


def test_worker_does_not_write(tmp_path):
    path = tmp_path / "r.json"
    config = SimpleNamespace(workerinput={}, getoption=lambda name: str(path))
    pytest_sessionfinish(SimpleNamespace(config=config), 0)
    assert not path.exists()


@pytest.mark.parametrize(
    "data",
    [
        {"schema_version": 2, "tests": {}},
        {"schema_version": "1", "tests": {}},
        {"schema_version": True, "tests": {}},
        {"schema_version": 1, "tests": {"test_a": "error"}},
        {"schema_version": 1, "tests": {"  ": "passed"}},
        {"schema_version": 1, "tests": {}, "extra": 1},
        {"schema_version": 1, "tests": []},
    ],
)
def test_invalid_results(data):
    with pytest.raises(ResultsInvalid):
        read_results(json.dumps(data))


def test_invalid_json():
    with pytest.raises(ResultsInvalid):
        read_results("{")
