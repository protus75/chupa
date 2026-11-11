from pathlib import Path

import pytest

from chupa.tickets import Ticket, TicketInvalid, parse_ticket


def ticket_text(kind="bug", state="confirmed"):
    regression = "\n## Regression\n```\npython test.py\n```\n- carries: tests/\n" if kind == "bug" else ""
    return f"""---
state: {state}
source: human
priority: P1
kind: {kind}
---
## Depends on
none
## Context
- context.txt
## Goal / Why
Fix the observed failure.
## Scope in / Scope out
Only the fix.
## Scope fence
- fix.py
## Acceptance criteria
1. `python test.py` exits 0.
## Verification
```
python test.py
```
## Definition of rejected
The failure persists.
## Time budget
- expected: 10m
- stuck: 20m
{regression}"""


@pytest.fixture
def repo(tmp_path: Path):
    (tmp_path / "context.txt").write_text("context")
    return tmp_path


def test_bug_without_evidence_is_invalid(repo):
    with pytest.raises(TicketInvalid) as exc:
        parse_ticket("example", ticket_text(), repo)
    assert any("has no evidence file" in finding.message for finding in exc.value.findings)


def test_bug_with_evidence_parses(repo):
    evidence = repo / "tickets/example/evidence/out.txt"
    evidence.parent.mkdir(parents=True)
    evidence.write_text("observed failure")
    assert isinstance(parse_ticket("example", ticket_text(), repo), Ticket)


def test_feature_without_evidence_parses(repo):
    assert isinstance(parse_ticket("example", ticket_text("feature"), repo), Ticket)


def test_rejected_bug_without_evidence_parses(repo):
    assert isinstance(parse_ticket("example", ticket_text(state="rejected"), repo), Ticket)
