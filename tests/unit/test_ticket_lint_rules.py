"""Authoring checks against parsed tickets with an in-memory repository."""

from pathlib import Path

import pytest

from chupa import tickets

TEXT = """---
state: confirmed
source: human
priority: P1
kind: bug
---
## Depends on
- none
## Context
- chupa/x.py
## Goal / Why
Reproduce the reported defect.
## Scope in / Scope out
In: x. Out: other modules.
## Scope fence
- chupa/x.py
- tests/regress_x.py
## Acceptance criteria
1. `./dev.py test` exits 0.
## Verification
```
./dev.py test
```
## Regression
```
./dev.py test tests/x.py
```
- carries: tests/regress_x.py
## Definition of rejected
The defect remains.
## Time budget
- expected: 10m
- stuck: 20m
"""


@pytest.fixture
def repo(monkeypatch):
    root = Path("/memory/repo")
    files = {root / "chupa/x.py": "value = 1", root / "tickets/example/evidence/log.txt": "observed defect"}
    monkeypatch.setattr(Path, "is_file", lambda p: p in files)
    monkeypatch.setattr(Path, "exists", lambda p: p in files)
    monkeypatch.setattr(Path, "is_symlink", lambda p: False)
    monkeypatch.setattr(Path, "read_text", lambda p: files[p])
    monkeypatch.setattr(Path, "rglob", lambda p, pattern: iter(f for f in files if f.is_relative_to(p)))
    monkeypatch.setattr(Path, "glob", lambda p, pattern: iter(()))
    return root, files


def test_regression_requires_carried_path_not_runner_denylist(repo):
    root, _ = repo
    # Neither parsing nor merge validation should acquire the authoring restriction.
    for parse in (tickets.parse_ticket, tickets.validate_ticket):
        ticket = parse("example", TEXT, root)
        [finding] = tickets.lint_findings(ticket, root)
        assert "does not name a carried file" in finding.message
        assert "does not speak the regression protocol" in finding.paved_road
    good = TEXT.replace("./dev.py test tests/x.py", "uv run python tests/regress_x.py")
    assert tickets.lint_findings(tickets.parse_ticket("example", good, root), root) == []


def test_carries_must_be_fenced(repo):
    root, _ = repo
    good = TEXT.replace("./dev.py test tests/x.py", "uv run python tests/regress_x.py")
    bad = good.replace("- tests/regress_x.py\n", "")
    [finding] = tickets.lint_findings(tickets.parse_ticket("example", bad, root), root)
    assert "tests/regress_x.py" in finding.message and "outside `## Scope fence`" in finding.message
    assert tickets.lint_findings(tickets.parse_ticket("example", good, root), root) == []


@pytest.mark.parametrize("floor", [0, 12])
def test_positive_file_floor_requires_unit_file(repo, floor):
    root, files = repo
    # Remove the regression explicitly while preserving the remaining required sections.
    text = TEXT.replace("kind: bug", "kind: feature").replace(TEXT[TEXT.index("## Regression") : TEXT.index("## Definition of rejected")], "")
    text = text.replace("- tests/regress_x.py\n", "")
    files[root / "test-gate.toml"] = f'[coverage]\ndefault = 90\n[coverage.files]\n"chupa/x.py" = {floor}\n'
    findings = tickets.lint_findings(tickets.parse_ticket("example", text, root), root)
    assert len(findings) == (1 if floor else 0)
    if floor:
        assert "chupa/x.py" in findings[0].message and "12" in findings[0].message
    with_test = text.replace("- chupa/x.py\n## Acceptance", "- chupa/x.py\n- tests/unit/test_x.py\n## Acceptance")
    assert tickets.lint_findings(tickets.parse_ticket("example", with_test, root), root) == []
    del files[root / "test-gate.toml"]
    assert tickets.lint_findings(tickets.parse_ticket("example", text, root), root) == []


def test_invalid_gate_is_finding(repo):
    root, files = repo
    files[root / "test-gate.toml"] = "[invalid"
    text = TEXT.replace("./dev.py test tests/x.py", "uv run python tests/regress_x.py")
    [finding] = tickets.lint_findings(tickets.parse_ticket("example", text, root), root)
    assert finding.path == "test-gate.toml" and "invalid test-gate.toml" in finding.message


@pytest.mark.parametrize(
    "command,allowed",
    [
        ("python tests/regress_x.py", True),
        ("python ./tests/regress_x.py", True),
        ("python tests/regress_x.py_extra", False),
        ("python tests/regress_x.py/../other.py", False),
    ],
)
def test_command_path_membership(repo, command, allowed):
    root, _ = repo
    text = TEXT.replace("./dev.py test tests/x.py", command)
    # A lexical prefix or unnormalized traversal would admit the wrong reproducer.
    findings = tickets.lint_findings(tickets.parse_ticket("example", text, root), root)
    assert bool(findings) == (not allowed)


def test_lint_verb_prints_carried_file_finding(repo, monkeypatch, capsys):
    import asyncio
    from types import SimpleNamespace

    from chupa import __main__ as cli

    root, files = repo
    files[root / "tickets/example/ticket.md"] = TEXT
    monkeypatch.setattr(Path, "iterdir", lambda p: iter([root / "tickets/example"]))
    monkeypatch.setattr(Path, "resolve", lambda p: p)

    async def common_dir(repo):
        return root / ".git"

    async def status(repo):
        return ""

    async def run(repo, *args):
        return "tickets/example/evidence/log.txt"

    checkout = SimpleNamespace(
        repo=root,
        config=SimpleNamespace(state_dir=root / ".state", drain=SimpleNamespace(max_ticket_minutes=90)),
        git=SimpleNamespace(git_common_dir=common_dir, status_porcelain=status, _run=run),
        journal=SimpleNamespace(read=lambda: []),
    )
    # Wiring lint to validation alone would silently accept this parsed bug ticket.
    assert asyncio.run(cli._lint(checkout, ["example"])) == 1
    assert "does not name a carried file" in capsys.readouterr().out
