import asyncio
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from chupa.__main__ import main
from chupa.git import Git
from chupa.journal import EventType, Journal
from chupa.lockfile import Lockfile, LockHeld
from chupa.runner import Refusal
from chupa.seams import SubprocessExec

ENV = {
    "PATH": "/usr/bin:/bin",
    "HOME": "/nonexistent",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@t",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@t",
}

CONFIG = """schema_version: 1
state_dir: .chupa/state
providers:
  - name: claude
    kind: cli
    package: test-cli
    models_by_tier: {low: m, medium: m, high: m, max: m}
    limits: {concurrency: 1}
routing:
  - {tier: medium, surface: implement, candidates: [{provider: claude}]}
review: {}
merge: {}
engine_plane_safety_inventory: [config.yaml]
"""

PLAN = "# Plan\n\n## 11. Failure spine\n\nSpine.\n"

TICKET = """---
priority: P2
kind: feature
---

## Depends on
{depends}

## Context
- chupa/thing.py

## Goal / Why
`thing()` returns ok.

## Scope in / Scope out
In: thing. Out: the rest.

## Scope fence
- chupa/thing.py

## Acceptance criteria
1. `uv run pytest` exits 0.

## Verification
```
uv run pytest
```

## Definition of rejected
Needs a new dependency.

## Time budget
- expected: 10m
- stuck: 20m
"""


def ticket(depends: str = "none") -> str:
    return TICKET.format(depends=depends)


class Clock:
    def __call__(self) -> datetime:
        return datetime(2026, 1, 1, tzinfo=UTC)


class Stages:
    """Scripted fake for the stage-dispatch seam: records each dispatched ticket and the lock state."""

    def __init__(self, terminal: str = "merged") -> None:
        self.terminal = terminal
        self.calls: list[str] = []
        self.lock_held: list[bool] = []
        self.checkout = None

    def __call__(self, checkout):
        self.checkout = checkout

        async def dispatch(t):
            self.calls.append(t.stem)
            contender = Lockfile(checkout.config.state_dir, instance_id="contender", clock=Clock())
            try:
                contender.acquire()
            except LockHeld:
                self.lock_held.append(True)
            else:
                contender.release()
                self.lock_held.append(False)
            checkout.journal.append(EventType.STATE_TRANSITION, {"to": self.terminal}, ticket=t.stem)
            return self.terminal

        return dispatch


@pytest.fixture
def root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "chupa").mkdir(parents=True)
    (root / "chupa" / "thing.py").write_text("")
    (root / "CHUPA_PLAN.md").write_text(PLAN)
    (root / "config.yaml").write_text(CONFIG)
    (root / ".gitignore").write_text(".chupa/\n")
    g = Git(SubprocessExec(), env=ENV, timeout=30.0)

    async def seed():
        await g.init(root, branch="main")
        await g.add(root, ["chupa", "CHUPA_PLAN.md", "config.yaml", ".gitignore"])
        await g.commit(root, "base")

    asyncio.run(seed())
    return root


def cli(root: Path, *argv: str, stages=None) -> int:
    return main(list(argv), cwd=root, env=ENV, clock=Clock(), pipeline=stages or Stages())


def journal(root: Path) -> Journal:
    return Journal(root / ".chupa" / "state", Clock())


def write(root: Path, stem: str, text: str) -> None:
    path = root / "tickets" / stem / "ticket.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def git_out(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], env=ENV, capture_output=True, text=True,
                          check=True).stdout


# --- new ----------------------------------------------------------------------------------------


def test_new_templates_a_ticket_and_lints_it(root, capsys):
    assert cli(root, "new", "add-thing") == 0
    path = root / "tickets" / "add-thing" / "ticket.md"
    text = path.read_text()
    assert "## Acceptance criteria" in text and "## Verification" in text
    out = capsys.readouterr().out
    assert "tickets/add-thing/ticket.md" in out
    assert "`## Acceptance criteria`" in out  # synchronous lint names what is left to fill
    assert git_out(root, "status", "--porcelain", "--", "tickets").startswith("??")  # authored, not committed
    assert not (root / ".chupa").exists()  # file authorship is outside the lock fence


def test_new_refuses_an_existing_stem(root, capsys):
    write(root, "add-thing", "keep me\n")
    assert cli(root, "new", "add-thing") == 2
    assert (root / "tickets" / "add-thing" / "ticket.md").read_text() == "keep me\n"
    assert "already exists" in capsys.readouterr().err


def test_new_refuses_a_bad_stem(root, capsys):
    assert cli(root, "new", "Bad_Stem") == 2
    assert not (root / "tickets").exists()
    assert "kebab-case" in capsys.readouterr().err


# --- status -------------------------------------------------------------------------------------


def test_status_on_an_empty_journal(root, capsys):
    assert cli(root, "status") == 0
    out = capsys.readouterr().out
    for heading in ("merged", "in flight", "blocked", "intake", "spend"):
        assert heading in out
    assert not (root / ".chupa").exists()  # write-free: no journal, no lockfile


def test_status_projects_the_journal(root, capsys):
    j = journal(root)
    j.append(EventType.STATE_TRANSITION, {"to": "running"}, ticket="a")
    j.append(EventType.STATE_TRANSITION, {"to": "merged"}, ticket="a")
    j.append(EventType.STATE_TRANSITION, {"to": "running"}, ticket="b")
    j.append(EventType.STATE_TRANSITION, {"to": "running"}, ticket="c")
    j.append(EventType.STATE_TRANSITION, {"to": "gate_failed"}, ticket="c")
    j.append(EventType.EFFECT_COMPLETION, {"result": {}, "cost": {"usd": 0.25}}, ticket="b", key="llm/b/0/x/1/1")
    j.append(EventType.EFFECT_COMPLETION, {"result": {}, "cost": {"usd": 0.5}}, ticket="c", key="llm/c/0/x/1/1")
    j.append(EventType.SIGNAL, {"signal": "ticket_intake", "source": "human", "state": "confirmed", "new": True,
                                "commit": "abc123"}, ticket="d")
    before = sorted(p.read_bytes() for p in (root / ".chupa").rglob("*") if p.is_file())

    assert cli(root, "status") == 0
    out = capsys.readouterr().out
    section = dict(block.split("\n", 1) for block in out.strip().split("\n\n"))
    assert "a" in section["merged:"] and "b" not in section["merged:"]
    assert "b" in section["in flight:"]
    assert "c: gate_failed" in section["blocked:"]
    assert "d: source: human" in section["intake:"]
    assert "$0.75" in section["spend:"]
    assert sorted(p.read_bytes() for p in (root / ".chupa").rglob("*") if p.is_file()) == before


def test_status_is_deterministic(root, capsys):
    j = journal(root)
    for stem in ("z", "a", "m"):
        j.append(EventType.STATE_TRANSITION, {"to": "merged"}, ticket=stem)
    cli(root, "status")
    first = capsys.readouterr().out
    cli(root, "status")
    assert capsys.readouterr().out == first
    assert first.index("- a") < first.index("- m") < first.index("- z")


# --- run ----------------------------------------------------------------------------------------


def test_run_dispatches_the_locked_validated_stem_to_the_stage_seam(root):
    write(root, "add-thing", ticket())
    stages = Stages()
    assert cli(root, "run", "add-thing", stages=stages) == 0
    assert stages.calls == ["add-thing"]
    assert stages.lock_held == [True]  # the one process holding the lock is the one dispatching
    assert git_out(root, "status", "--porcelain") == ""  # intake committed the ticket before dispatch
    assert "chupa(add-thing): ticket" in git_out(root, "log", "--format=%s")
    events = [(e.type, e.ticket, e.body.get("to")) for e in journal(root).read()]
    assert (EventType.STATE_TRANSITION, "add-thing", "running") in events
    assert events.index((EventType.STATE_TRANSITION, "add-thing", "running")) < events.index(
        (EventType.STATE_TRANSITION, "add-thing", "merged"))
    Lockfile(root / ".chupa" / "state", instance_id="after", clock=Clock()).acquire()  # released on exit


def test_run_exits_1_on_a_non_ok_terminal(root):
    write(root, "add-thing", ticket())
    assert cli(root, "run", "add-thing", stages=Stages("gate_failed")) == 1
    assert (root / "tickets" / "add-thing" / "ticket.md").is_file()


def test_run_refused_when_the_lockfile_is_already_held(root, capsys):
    write(root, "add-thing", ticket())
    holder = Lockfile(root / ".chupa" / "state", instance_id="other", clock=Clock())
    holder.acquire()
    try:
        stages = Stages()
        assert cli(root, "run", "add-thing", stages=stages) == 2
    finally:
        holder.release()
    assert stages.calls == []
    assert "other" in capsys.readouterr().err  # the holder identity names who to wait for
    assert git_out(root, "status", "--porcelain").startswith("??")  # intake never ran: nothing committed
    assert journal(root).read() == []


def test_run_refuses_an_invalid_ticket(root, capsys):
    write(root, "add-thing", ticket().replace("## Verification", "## Verify"))
    stages = Stages()
    assert cli(root, "run", "add-thing", stages=stages) == 2
    assert stages.calls == []
    assert "ticket_schema" in capsys.readouterr().err
    assert not any(e.type == EventType.STATE_TRANSITION for e in journal(root).read())


def test_run_refuses_a_missing_stem(root, capsys):
    stages = Stages()
    assert cli(root, "run", "no-such", stages=stages) == 2
    assert stages.calls == []
    assert "new no-such" in capsys.readouterr().err


def test_run_refuses_an_unmerged_dependency(root, capsys):
    write(root, "first", ticket())
    write(root, "second", ticket(depends="- first"))
    stages = Stages()
    assert cli(root, "run", "second", stages=stages) == 2
    assert stages.calls == []
    assert "run first" in capsys.readouterr().err
    assert cli(root, "run", "first", stages=stages) == 0
    assert cli(root, "run", "second", stages=stages) == 0
    assert stages.calls == ["first", "second"]


def test_run_refuses_a_merged_ticket(root, capsys):
    write(root, "add-thing", ticket())
    stages = Stages()
    assert cli(root, "run", "add-thing", stages=stages) == 0
    assert cli(root, "run", "add-thing", stages=stages) == 2
    assert stages.calls == ["add-thing"]
    assert "merged" in capsys.readouterr().err


def test_run_refused_before_the_lock_when_the_pipeline_refuses(root, capsys):
    def unbuilt(checkout):
        raise Refusal("pipeline missing", "build it")

    write(root, "add-thing", ticket())
    assert main(["run", "add-thing"], cwd=root, env=ENV, clock=Clock(), pipeline=unbuilt) == 2
    assert "pipeline missing -- build it" in capsys.readouterr().err
    assert journal(root).read() == []


def test_config_error_exits_2(root, capsys):
    (root / "config.yaml").write_text("schema_version: 1\n")
    assert cli(root, "status") == 2
    assert "config.yaml" in capsys.readouterr().err


# --- module entry -------------------------------------------------------------------------------


def test_python_dash_m_chupa_is_the_entry(root):
    env = {**ENV, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    proc = subprocess.run([sys.executable, "-m", "chupa", "status"], cwd=root, env=env, capture_output=True,
                          text=True)
    assert proc.returncode == 0, proc.stderr
    assert "merged:" in proc.stdout
    proc = subprocess.run([sys.executable, "-m", "chupa", "bogus"], cwd=root, env=env, capture_output=True,
                          text=True)
    assert proc.returncode == 2


def test_project_stays_virtual():
    import tomllib

    pyproject = tomllib.loads((Path(__file__).resolve().parents[1] / "pyproject.toml").read_text())
    assert "scripts" not in pyproject["project"]
    assert "build-system" not in pyproject
    assert os.path.isfile(Path(__file__).resolve().parents[1] / "chupa" / "__main__.py")
