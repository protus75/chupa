import json

import pytest

from chupa.__main__ import main
from chupa.covgate import GateInvalid, evaluate, parse_gate


def report(**files):
    return {"meta": {"format": 3}, "files": files}


def file(covered, total, branches=None, missing=None):
    summary = {"covered_lines": covered, "num_statements": total}
    if branches is not None:
        summary.update(covered_branches=branches[0], num_branches=branches[1])
    return {"summary": summary, "missing_lines": missing or []}


def test_precedence_and_longest_package():
    gate = parse_gate('[coverage]\ndefault=90\nrepository=0\n[coverage.packages]\npkg=80\n"pkg/sub"=70\n[coverage.files]\n"pkg/hard.py"=50')
    # Wrong package/default precedence would reject hard, easy, or nested respectively.
    assert evaluate(gate, report(**{'pkg/hard.py': file(6, 10), 'pkg/easy.py': file(85, 100), 'pkg/sub/x.py': file(75, 100), 'pkg/full.py': file(100, 100)})) == []


def test_aggregates_are_weighted():
    gate = parse_gate('[coverage]\ndefault=0\nrepository=50\n[coverage.packages]\npkg=50\n[coverage.files]\n"pkg/b.py"=0')
    lines = evaluate(gate, report(**{'pkg/a.py': file(10, 10), 'pkg/b.py': file(0, 90)}))
    # Best-file and unweighted means would both pass at 50%.
    assert len(lines) == 2
    assert lines[0].startswith('repository: 10.00% below 50% (coverage.repository)')
    assert lines[1].startswith('pkg: 10.00% below 50% (coverage.packages.pkg)')


def test_branches_and_boundary():
    gate = parse_gate('[coverage]\ndefault=70\nrepository=0\n[coverage.packages]\npkg=50')
    lines = evaluate(gate, report(**{'pkg2/a.py': file(3, 4, (1, 2), [4])}))
    # Lines-only yields 75%; prefix matching wrongly applies pkg's 50%.
    assert len(lines) == 1
    assert 'pkg2/a.py: 66.67% below 70% (coverage.default)' in lines[0]
    assert 'missing lines: [4]' in lines[0]
    assert lines[0].endswith("add unit tests that execute the missing lines. Lowering a threshold in the gate file is a human ticket's decision.")


@pytest.mark.parametrize('covered,total,minimum', [(8999, 10000, 90), (99999, 100000, 100)])
def test_unrounded_comparison(covered, total, minimum):
    gate = parse_gate(f'[coverage]\ndefault={minimum}\nrepository=0')
    # Rounding before comparison would make each file pass.
    assert len(evaluate(gate, report(**{'a.py': file(covered, total)}))) == 1


def test_absent_branches_and_empty_totals():
    gate = parse_gate('[coverage]\ndefault=75\nrepository=0\n[coverage.packages]\npkg=100')
    # Missing branch keys must count as zero; empty totals must be 100, not 0.
    assert evaluate(gate, report(**{'other.py': file(3, 4), 'pkg/empty.py': file(0, 0)})) == []
    assert evaluate(parse_gate('[coverage]\ndefault=100'), report(**{'empty.py': file(0, 0)})) == []


@pytest.mark.parametrize('text,key', [
    ('[coverage]\ndefault=90\nminimum=90', 'coverage.minimum'),
    ('[coverage]\nrepository=90', 'coverage.default'),
    ('[coverage]\ndefault=101', 'coverage.default'),
    ('[coverage]\ndefault=90\n[unit]\nbudget_seconds=0', 'unit.budget_seconds'),
    ('[coverage]\ndefault=true', 'coverage.default'),
    ('[coverage]\ndefault=90\n[unit]\nextra=1', 'unit.extra'),
])
def test_invalid_gate_names_key(text, key):
    # Ignoring an invalid key or silently substituting a default must refuse.
    with pytest.raises(GateInvalid) as exc:
        parse_gate(text)
    assert exc.value.key == key
    assert key in str(exc.value)


def test_budget_default_and_explicit():
    # Distinguish the default from an ignored explicit budget.
    assert parse_gate('[coverage]\ndefault=90').budget_seconds == 60
    assert parse_gate('[coverage]\ndefault=90\n[unit]\nbudget_seconds=17').budget_seconds == 17


def test_cli_without_config(tmp_path, capsys):
    gate = tmp_path / 'thresholds.toml'
    output = tmp_path / 'result.json'
    gate.write_text('[coverage]\ndefault=101')
    args = ['covgate', '--gate', gate.name, '--report', output.name]
    assert main(args, cwd=tmp_path) == 2
    assert 'coverage.default' in capsys.readouterr().err
    gate.write_text('[coverage]\ndefault=80\nrepository=0')
    assert main(args, cwd=tmp_path) == 2
    assert 'result.json' in capsys.readouterr().err
    output.write_text(json.dumps(report(**{'a.py': file(6, 10, missing=[2, 7])})))
    assert main(args, cwd=tmp_path) == 1
    out = capsys.readouterr().out
    assert 'a.py' in out and '[2, 7]' in out
    output.write_text(json.dumps(report(**{'a.py': file(9, 10)})))
    assert main(args, cwd=tmp_path) == 0
    assert capsys.readouterr().out == ''
    output.write_text('{bad')
    assert main(args, cwd=tmp_path) == 2
    assert 'generate a coverage.py' in capsys.readouterr().err
