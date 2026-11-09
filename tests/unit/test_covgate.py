import pytest

from chupa.covgate import evaluate, parse_gate, percentages


def entry(covered, total):
    return {"summary": {"covered_lines": covered, "num_statements": total}, "missing_lines": []}


def test_weighted_and_empty():
    report = {"meta": {"format": 3}, "files": {"repository": entry(1, 1), "other": entry(0, 9)}}
    assert percentages(report) == (10.0, {"repository": 100.0, "other": 0.0})
    assert percentages({"meta": {"format": 3}, "files": {}}) == (100.0, {})
    gate = parse_gate("[coverage]\ndefault=0\nrepository=50\n[coverage.files]\nrepository=90")
    failures = evaluate(gate, report)
    assert len(failures) == 1 and failures[0].startswith("repository: 10.00%")


def test_invalid_report():
    with pytest.raises(ValueError):
        percentages({"meta": {"format": 3}, "files": {"bad": entry(2, 1)}})
