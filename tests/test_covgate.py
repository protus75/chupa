import json
import os
import sys

import pytest

from chupa.__main__ import main
from chupa.covgate import GateInvalid, evaluate, parse_gate, run_gate


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
    assert evaluate(gate, report(**{"pkg/hard.py": file(6, 10), "pkg/easy.py": file(85, 100), "pkg/sub/x.py": file(75, 100), "pkg/full.py": file(100, 100)})) == []


def test_aggregates_are_weighted():
    gate = parse_gate('[coverage]\ndefault=0\nrepository=50\n[coverage.packages]\npkg=50\n[coverage.files]\n"pkg/b.py"=0')
    lines = evaluate(gate, report(**{"pkg/a.py": file(10, 10), "pkg/b.py": file(0, 90)}))
    # Best-file and unweighted means would both pass at 50%.
    assert len(lines) == 2
    assert lines[0].startswith("repository: 10.00% below 50% (coverage.repository)")
    assert lines[1].startswith("pkg: 10.00% below 50% (coverage.packages.pkg)")


def test_branches_and_boundary():
    gate = parse_gate("[coverage]\ndefault=70\nrepository=0\n[coverage.packages]\npkg=50")
    lines = evaluate(gate, report(**{"pkg2/a.py": file(3, 4, (1, 2), [4])}))
    # Lines-only yields 75%; prefix matching wrongly applies pkg's 50%.
    assert len(lines) == 1
    assert "pkg2/a.py: 66.67% below 70% (coverage.default)" in lines[0]
    assert "missing lines: [4]" in lines[0]
    assert lines[0].endswith("add unit tests that execute the missing lines. Lowering a threshold in the gate file is a human ticket's decision.")


@pytest.mark.parametrize("covered,total,minimum", [(8999, 10000, 90), (99999, 100000, 100)])
def test_unrounded_comparison(covered, total, minimum):
    gate = parse_gate(f"[coverage]\ndefault={minimum}\nrepository=0")
    # Rounding before comparison would make each file pass.
    assert len(evaluate(gate, report(**{"a.py": file(covered, total)}))) == 1


def test_absent_branches_and_empty_totals():
    gate = parse_gate("[coverage]\ndefault=75\nrepository=0\n[coverage.packages]\npkg=100")
    # Missing branch keys must count as zero; empty totals must be 100, not 0.
    assert evaluate(gate, report(**{"other.py": file(3, 4), "pkg/empty.py": file(0, 0)})) == []
    assert evaluate(parse_gate("[coverage]\ndefault=100"), report(**{"empty.py": file(0, 0)})) == []


@pytest.mark.parametrize(
    "text,key",
    [
        ("[coverage]\ndefault=90\nminimum=90", "coverage.minimum"),
        ("[coverage]\nrepository=90", "coverage.default"),
        ("[coverage]\ndefault=101", "coverage.default"),
        ("[coverage]\ndefault=90\n[unit]\nbudget_seconds=0", "unit.budget_seconds"),
        ("[coverage]\ndefault=true", "coverage.default"),
        ("[coverage]\ndefault=90\n[unit]\nextra=1", "unit.extra"),
    ],
)
def test_invalid_gate_names_key(text, key):
    # Ignoring an invalid key or silently substituting a default must refuse.
    with pytest.raises(GateInvalid) as exc:
        parse_gate(text)
    assert exc.value.key == key
    assert key in str(exc.value)


def test_budget_default_and_explicit():
    # Distinguish the default from an ignored explicit budget.
    assert parse_gate("[coverage]\ndefault=90").budget_seconds == 60
    assert parse_gate("[coverage]\ndefault=90\n[unit]\nbudget_seconds=17").budget_seconds == 17


def test_run_gate_evaluates_fresh_report(tmp_path):
    gate = tmp_path / "gate.toml"
    output = tmp_path / "coverage.json"
    gate.write_text("[coverage]\ndefault=80")
    argv = ["unit", "--example"]

    def run_with(covered, rc):
        def run(actual):
            assert actual == argv  # Passing a different command loses the requested runner arguments.
            output.write_text(json.dumps(report(**{"a.py": file(covered, 10)})))
            return rc

        return run

    # An ignored report or an evaluation before the run cannot distinguish these values.
    assert run_gate(argv, gate_path=gate, report_path=output, run=run_with(9, 0)) == 0
    assert run_gate(argv, gate_path=gate, report_path=output, run=run_with(6, 0)) == 1
    # A passing report must not mask either nonzero runner exit.
    assert run_gate(argv, gate_path=gate, report_path=output, run=run_with(9, 1)) == 1
    assert run_gate(argv, gate_path=gate, report_path=output, run=run_with(9, 2)) == 2


def test_run_gate_rejects_stale_report(tmp_path, capsys):
    gate = tmp_path / "test-gate.toml"
    output = tmp_path / "coverage.json"
    gate.write_text("[coverage]\ndefault=80")
    output.write_text(json.dumps(report(**{"a.py": file(9, 10)})))
    # Keeping the old passing report would incorrectly return 0.
    assert run_gate(["unit"], gate_path=gate, report_path=output, run=lambda argv: 0) == 2
    assert "--cov-report=json:" in capsys.readouterr().err


def test_cli_requires_command(tmp_path, capsys):
    (tmp_path / "test-gate.toml").write_text("[coverage]\ndefault=80")
    (tmp_path / "coverage.json").write_text(json.dumps(report(**{"a.py": file(9, 10)})))
    # Report-only mode would accept this passing report.
    assert main(["covgate"], cwd=tmp_path) == 2
    assert "name the unit-test command after --" in capsys.readouterr().err


def test_cli_runs_in_cwd_and_process_group(tmp_path, capsys):
    (tmp_path / "test-gate.toml").write_text("[coverage]\ndefault=80")
    passing = json.dumps(report(**{"a.py": file(9, 10)}))
    script = f"import os; from pathlib import Path; Path('pgid').write_text(str(os.getpgrp())); Path('coverage.json').write_text({passing!r})"
    # The relative report and pgid are written in cwd; a new session has a different pgid.
    assert main(["covgate", "--", sys.executable, "-c", script], cwd=tmp_path) == 0
    assert int((tmp_path / "pgid").read_text()) == os.getpgrp()
    assert main(["covgate", "--", "no-such-binary-xyz"], cwd=tmp_path) == 2
    assert "no-such-binary-xyz not found -- install it or correct the command after --" in capsys.readouterr().err


def test_cli_invalid_inputs(tmp_path, capsys):
    gate = tmp_path / "thresholds.toml"
    args = ["covgate", "--gate", gate.name, "--report", "result.json", "--", sys.executable, "-c"]
    gate.write_text("[coverage]\ndefault=101")
    assert main(args + ["from pathlib import Path; Path('result.json').write_text('{}')"], cwd=tmp_path) == 2
    assert "coverage.default" in capsys.readouterr().err
    gate.write_text("[coverage]\ndefault=80")
    assert main(args + ["pass"], cwd=tmp_path) == 2
    assert "--cov-report=json:" in capsys.readouterr().err
    assert main(args + ["from pathlib import Path; Path('result.json').write_text('{bad')"], cwd=tmp_path) == 2
    assert "generate a coverage.py" in capsys.readouterr().err
