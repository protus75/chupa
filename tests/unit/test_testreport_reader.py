import json

import pytest

from chupa.testreport import ResultsInvalid, read_results


def test_valid_results():
    data = {"schema_version": 2, "tests": {"test_a": "failed", "test_b": "skipped"}, "seconds": {"test_a": 0.0, "test_b": 1.5}}
    result = read_results(json.dumps(data))
    assert result.tests == data["tests"]
    assert result.seconds == data["seconds"]


@pytest.mark.parametrize(
    "data",
    [
        {"schema_version": 2, "tests": {"test_a": "passed"}},
        {"schema_version": 2, "tests": {"test_a": "passed"}, "seconds": {"test_b": 1.0}},
        {"schema_version": 2, "tests": {"test_a": "passed"}, "seconds": []},
        *[{"schema_version": 2, "tests": {"test_a": "passed"}, "seconds": {"test_a": value}} for value in (-1.0, float("nan"), float("inf"), True, 1)],
        {"schema_version": 3, "tests": {"test_a": "passed"}, "seconds": {"test_a": 1.0}},
        {"schema_version": 1, "tests": {"test_a": "passed"}, "seconds": {"test_a": 1.0}},
        {"schema_version": 1, "tests": {"test_a": "passed"}},
        {"schema_version": 1, "tests": []},
        {"schema_version": 1, "tests": {" ": "passed"}},
        {"schema_version": 1, "tests": {"test_a": "error"}},
        [],
    ],
)
def test_invalid_results(data):
    with pytest.raises(ResultsInvalid):
        read_results(json.dumps(data))


def test_invalid_json():
    with pytest.raises(ResultsInvalid):
        read_results("{")
