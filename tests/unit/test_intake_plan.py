import asyncio
from pathlib import Path
from types import SimpleNamespace

import pytest

from chupa import tickets
from chupa.journal import EventType


class Lock:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


class FakeGit:
    _commit_lock = Lock()

    def __init__(self, entries, evidence):
        self.entries = entries
        self.evidence = evidence
        self.commits = []

    async def status_porcelain(self, repo):
        return "".join(f"{status} {path}\n" for status, path in self.entries)

    async def _run(self, repo, *args):
        stem = args[-1].split("/")[1]
        return "\0".join(self.evidence[stem])

    async def _commit(self, repo, message, *, only):
        self.commits.append((message, only))
        return "commit-sha"


class Journal:
    def __init__(self):
        self.events = []

    def read(self):
        return []

    def append(self, *args, **kwargs):
        self.events.append((args, kwargs))


class FS:
    def write(self, path, content):
        path.write_bytes(content)


def setup_plan(tmp_path, monkeypatch):
    entries = [("??", "tickets/good/ticket.md"), (" M", "tickets/bad/ticket.md"), (" M", "tickets/done/ticket.md"), ("A ", "tickets/good/evidence/log")]
    evidence = {"good": ["tickets/good/evidence/log"], "bad": [], "done": []}
    for stem in evidence:
        path = tmp_path / tickets.ticket_path(stem)
        path.parent.mkdir(parents=True)
        path.write_text("---\nstate: draft\npriority: P1\nkind: chore\n---\nbody\n")
    log = tmp_path / evidence["good"][0]
    log.parent.mkdir()
    log.write_text("evidence")
    finding = tickets._f("bad lint", "repair")
    calls = []

    def validate(stem, text, repo, *, _settled=False):
        calls.append((stem, _settled))
        return SimpleNamespace(stem=stem, frontmatter=SimpleNamespace(source="human", state="confirmed"))

    def lint(ticket, repo):
        assert ticket.stem != "done"
        return [finding] if ticket.stem == "bad" else []

    def check_evidence(ticket, repo, *, paths):
        assert ticket.stem != "done"
        assert list(paths) == evidence[ticket.stem]
        return []

    monkeypatch.setattr(tickets, "validate_ticket", validate)
    monkeypatch.setattr(tickets, "lint_findings", lint)
    monkeypatch.setattr(tickets, "evidence_findings", check_evidence)
    monkeypatch.setattr("chupa.status.last_states", lambda events: {"done": "merged"})
    return entries, evidence, finding, calls


def test_plan_decisions(tmp_path, monkeypatch):
    entries, evidence, finding, calls = setup_plan(tmp_path, monkeypatch)
    assert tickets._intake_stray(tmp_path, entries, evidence) == []
    assert tickets._intake_stray(tmp_path, entries + [("M ", "outside.py"), ("D ", evidence["good"][0])], evidence) == ["outside.py", evidence["good"][0]]
    original, stamped, good = tickets._intake_plan_stem(tmp_path, "good", True, evidence["good"], None)
    assert "state: draft" in original
    assert "state: confirmed" in stamped and "source: human" in stamped
    assert good.stem == "good"
    assert tickets._intake_plan_stem(tmp_path, "bad", False, [], None)[2] == [finding]
    assert tickets._intake_plan_stem(tmp_path, "done", False, [], "merged")[2].stem == "done"
    assert calls == [("good", False), ("bad", False), ("done", True)]
    assert (tmp_path / tickets.ticket_path("good")).read_text() == original


def test_intake_applies_plan_and_refuses_stray(tmp_path, monkeypatch):
    entries, evidence, finding, _ = setup_plan(tmp_path, monkeypatch)
    decisions = {stem: tickets._intake_plan_stem(tmp_path, stem, stem == "good", paths, "merged" if stem == "done" else None) for stem, paths in evidence.items()}
    git, journal = FakeGit(entries, evidence), Journal()
    result = asyncio.run(tickets.intake(tmp_path, git, journal, FS(), stems=None))
    assert result.committed == ("done", "good")
    assert result.refused == {"bad": decisions["bad"][2]} == {"bad": [finding]}
    assert (tmp_path / tickets.ticket_path("good")).read_text() == decisions["good"][1]
    assert git.commits == [("chupa(done): ticket", [tickets.ticket_path("done")]), ("chupa(good): ticket", [tickets.ticket_path("good"), *evidence["good"]])]
    assert journal.events[1] == ((EventType.SIGNAL, {"signal": tickets.INTAKE_SIGNAL, "source": "human", "state": "confirmed", "new": True, "commit": "commit-sha"}), {"ticket": "good"})
    stray_entries = entries + [("M ", "outside.py")]
    stray = tickets._intake_stray(tmp_path, stray_entries, evidence)
    git = FakeGit(stray_entries, evidence)
    with pytest.raises(tickets.IntakeRefused) as exc:
        asyncio.run(tickets.intake(tmp_path, git, Journal(), FS(), stems={"good"}))
    assert exc.value.finding.message == f"staged changes outside pending ticket files: {', '.join(stray)}"
    assert not git.commits
