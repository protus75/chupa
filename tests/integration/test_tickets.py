import asyncio
import re
from datetime import UTC, datetime
from pathlib import Path

import pytest

from chupa.git import Git
from chupa.journal import EventType, Journal
from chupa.seams import LocalFileSystem, SubprocessExec
from chupa.tickets import (
    INTAKE_SIGNAL,
    IntakeRefused,
    TicketInvalid,
    depends_cycle,
    intake,
    template,
    validate_ticket,
)

ENV = {
    "PATH": "/usr/bin:/bin",
    "HOME": "/nonexistent",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@t",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@t",
}

FRONT = "---\npriority: P2\nkind: feature\n---\n"

BODY = """
## Depends on
none

## Context
- chupa/thing.py

## Goal / Why
`chupa thing` prints ok. Operators need it.

## Scope in / Scope out
In: the verb. Out: everything else.

## Scope fence
- chupa/thing.py
- tests/test_thing.py

## Acceptance criteria
1. `uv run pytest tests/test_thing.py` exits 0.
2. `chupa/thing.py` exposes `thing()`.

## Verification
```
uv run pytest tests/test_thing.py
```

## Definition of rejected
The verb needs a new dependency.

## Time budget
- expected: 20m
- stuck: 40m
"""

VALID = FRONT + BODY


def run(coro):
    return asyncio.run(coro)


class Clock:
    def __call__(self) -> datetime:
        return datetime(2026, 1, 1, tzinfo=UTC)


@pytest.fixture
def repo(tmp_path: Path):
    g = Git(SubprocessExec(), env=ENV, timeout=30.0)
    root = tmp_path / "repo"
    (root / "chupa").mkdir(parents=True)
    (root / "specs").mkdir()
    (root / "chupa" / "thing.py").write_text("")
    (root / "specs" / "review.md").write_text("spec\n")

    async def seed():
        await g.init(root, branch="main")
        await g.add(root, ["chupa", "specs"])
        await g.commit(root, "base")

    run(seed())
    return root, g, Journal(tmp_path / "state", Clock())


def write(root: Path, stem: str, text: str) -> Path:
    path = root / "tickets" / stem / "ticket.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def do_intake(root, g, journal):
    return run(intake(root, g, journal, LocalFileSystem()))


def complete(text: str) -> str:
    """The frontmatter intake would stamp onto a new human stem."""
    return text if "source:" in text else text.replace("---\npriority", "---\nstate: confirmed\nsource: human\npriority")


def refusal(root, text, stem="t-one"):
    write(root, stem, text)
    text = complete(text)
    with pytest.raises(TicketInvalid) as e:
        validate_ticket(stem, text, root)
    return e.value.findings


def messages(findings) -> str:
    return "\n".join(f"{f.message} || {f.paved_road}" for f in findings)


# --- the four named behaviors ----------------------------------------------------------------


def test_valid_ticket_validates_and_commits(repo):
    root, g, journal = repo
    path = write(root, "t-one", VALID)
    ticket = validate_ticket("t-one", VALID.replace("---\npriority", "---\nstate: draft\nsource: human\npriority"), root)
    assert ticket.verification == (("uv", "run", "pytest", "tests/test_thing.py"),)
    assert (ticket.expected_minutes, ticket.stuck_minutes) == (20, 40)
    assert ticket.frontmatter.agent_tier == ticket.frontmatter.agent_effort == "medium"

    result = do_intake(root, g, journal)

    assert result.committed == ("t-one",) and not result.refused
    assert run(g.status_porcelain(root)) == ""
    text = path.read_text()
    assert "source: human" in text and "state: confirmed" in text and text.endswith(BODY)
    subject = run(g._run(root, "log", "-1", "--format=%s%n%b")).strip()
    assert subject == "chupa(t-one): ticket"
    sha = run(g.rev_parse(root, "HEAD"))
    [event] = [e for e in journal.read() if e.type == EventType.SIGNAL]
    assert event.ticket == "t-one"
    assert event.body == {"signal": INTAKE_SIGNAL, "source": "human", "state": "confirmed", "new": True, "commit": sha}


def test_bad_schema_ticket_is_refused_with_paved_road(repo):
    root, g, journal = repo
    bad = VALID.replace("priority: P2", "priority: urgent\ntags: [ui]")
    path = write(root, "t-bad", bad)

    result = do_intake(root, g, journal)

    assert result.committed == ()
    findings = result.refused["t-bad"]
    assert {f.code for f in findings} == {"ticket_schema"}
    text = messages(findings)
    assert "priority" in text and "tags" in text
    assert all(f.paved_road.strip() for f in findings)
    assert "frontmatter carries only state, source, priority, kind" in findings[0].paved_road
    assert path.read_text() == bad  # untouched, uncommitted
    assert run(g.status_porcelain(root)).startswith("?? tickets/")
    assert journal.read() == []


# --- the rest of the section 13 grammar ------------------------------------------------------


@pytest.mark.parametrize("stuck", [19, 20, 21])
def test_time_budget_stuck_must_exceed_expected(repo, stuck):
    root, _, _ = repo
    text = complete(VALID.replace("- stuck: 40m", f"- stuck: {stuck}m"))
    if stuck <= 20:
        [finding] = refusal(root, text)
        assert finding.code == "ticket_schema"
        assert finding.path == "tickets/t-one/ticket.md"
        assert "Time budget" in finding.message
        assert f"stuck: {stuck}m" in finding.message
        assert "expected: 20m" in finding.message
        assert finding.paved_road == "set stuck greater than expected (the stage deadline is the stuck budget)"
    else:
        ticket = validate_ticket("t-one", text, root)
        assert (ticket.expected_minutes, ticket.stuck_minutes) == (20, stuck)


@pytest.mark.parametrize(
    ("old", "new", "needle"),
    [
        ("- chupa/thing.py\n\n## Goal", "- chupa/specs/review.md\n\n## Goal", "prompt spec"),
        ("- chupa/thing.py\n\n## Goal", "- chupa/later.py\n\n## Goal", "does not exist"),
        ("- chupa/thing.py\n\n## Goal", "- ../etc/passwd\n\n## Goal", "repo-relative"),
        ("## Depends on\nnone", "## Depends on\n- ghost", "does not resolve"),
        ("## Depends on\nnone", "## Depends on\n- t-one", "self-edge"),
        ("## Definition of rejected\nThe verb needs a new dependency.\n", "", "Definition of rejected"),
        ("## Goal / Why", "## Notes\nhi\n\n## Goal / Why", "unknown body section"),
        ("- expected: 20m\n- stuck: 40m", "- expected: 20 minutes\n- stuck: 40m", "Time budget"),
        ("uv run pytest tests/test_thing.py\n", "uv run pytest 'unterminated\n", "argv-parseable"),
        ("```\nuv run pytest tests/test_thing.py\n```", "`uv run pytest`", "fenced command block"),
        ("exits 0.", "exits 0 and the code is cleaner.", "unmeasurable"),
        ("2. `chupa/thing.py` exposes `thing()`.", "2. The thing works.", "names no check"),
        ("kind: feature", "kind: bug", "no `## Regression`"),
        ("## Time budget", "## Regression\n```\npytest\n```\n- carries: tests/\n\n## Time budget", "non-bug"),
        ("## Time budget", "## Exit-read window\n- nonsense\n\n## Time budget", "unknown body section"),
        ("kind: feature", "kind: feature\ngate_bypass: [{code: vibes, reason: x}]", "gate_bypass"),
    ],
)
def test_grammar_refusals(repo, old, new, needle):
    root, _, _ = repo
    assert old in VALID
    findings = refusal(root, VALID.replace(old, new))
    assert needle in messages(findings)
    assert all(f.code == "ticket_schema" and f.paved_road for f in findings)


def test_bug_ticket_with_regression_validates(repo):
    root, _, _ = repo
    text = VALID.replace("kind: feature", "kind: bug\nstate: draft\nsource: human").replace(
        "## Time budget", "## Regression\n```\nuv run pytest tests/test_thing.py\n```\n- carries: tests/\n\n## Time budget"
    )
    write(root, "t-one", text)
    ticket = validate_ticket("t-one", text, root)
    assert ticket.frontmatter.kind == "bug"
    assert ticket.regression == ("uv", "run", "pytest", "tests/test_thing.py")
    assert ticket.carries == ("tests/",)


@pytest.mark.parametrize("prefix", ["tests/", "tests/regress_x.py", "fixture/data.json", "nested/test/data.json"])
def test_bug_carries_test_prefix_validates(repo, prefix):
    root, _, _ = repo
    text = complete(bug_text().replace("- carries: tests/", f"- carries: {prefix}"))
    assert validate_ticket("t-bug", text, root).carries == (prefix,)


def test_bug_carries_implementation_prefix_is_refused(repo):
    root, _, _ = repo
    prefix = "vscode-chupa/media/graph.js"
    text = bug_text().replace("- carries: tests/", f"- carries: {prefix}")
    [finding] = refusal(root, text, stem="t-bug")
    assert prefix in finding.message
    assert "tests/" in finding.paved_road


@pytest.mark.parametrize(
    "regression",
    [
        "```\n```\n- carries: tests/",
        "```\ntrue\nfalse\n```\n- carries: tests/",
        "```\ntrue\n```",
        "```\ntrue\n```\n- carries: ../tests",
        "```\ntrue\n```\n- carries: /tests",
        '```\n""\n```\n- carries: tests/',
    ],
)
def test_regression_grammar_is_closed(repo, regression):
    root, _, _ = repo
    text = complete(VALID.replace("kind: feature", "kind: bug").replace("## Time budget", f"## Regression\n{regression}\n\n## Time budget"))
    assert "Regression" in messages(refusal(root, text))


def test_on_demand_must_be_fenced_existing_and_not_context(repo):
    root, _, _ = repo
    base = VALID.replace("## Goal / Why", "## On-demand\n- {}\n\n## Goal / Why")
    (root / "chupa" / "big.py").write_text("")
    assert "not covered" in messages(refusal(root, base.format("chupa/big.py")))
    fenced = base.replace("- tests/test_thing.py", "- tests/test_thing.py\n- chupa/big.py")
    assert "also in `## Context`" in messages(refusal(root, fenced.format("chupa/thing.py")))
    ok = fenced.format("chupa/big.py").replace("---\npriority", "---\nstate: draft\nsource: human\npriority")
    write(root, "t-one", ok)
    assert validate_ticket("t-one", ok, root).on_demand == ("chupa/big.py",)


def test_reserved_and_malformed_stems_are_refused(repo):
    root, _, _ = repo
    assert "reserved" in messages(refusal(root, VALID, stem="retro"))
    assert "kebab-case" in messages(refusal(root, VALID, stem="Bad_Stem"))


def test_dependency_cycle_is_refused(repo):
    root, g, journal = repo
    write(root, "t-a", VALID)
    assert do_intake(root, g, journal).committed == ("t-a",)
    # t-b depends on t-a, then t-a is edited to depend on t-b: the edit closes a cycle.
    write(root, "t-b", VALID.replace("## Depends on\nnone", "## Depends on\n- t-a"))
    assert do_intake(root, g, journal).committed == ("t-b",)
    a = (root / "tickets" / "t-a" / "ticket.md").read_text().replace("## Depends on\nnone", "## Depends on\n- t-b")
    write(root, "t-a", a)
    result = do_intake(root, g, journal)
    assert "cycle: t-a -> t-b -> t-a" in messages(result.refused["t-a"])
    assert depends_cycle("x", {"x": ["y"], "y": ["z"]}) is None


# --- intake source stamp ---------------------------------------------------------------------


def test_new_stem_claiming_a_machine_source_is_refused(repo):
    root, g, journal = repo
    for source in ("seed", "box:bug_report"):
        write(root, "t-one", VALID.replace("---\npriority", f"---\nsource: {source}\npriority"))
        [f] = do_intake(root, g, journal).refused["t-one"]
        assert "only the machine writes" in f.message and "intake stamps `source: human`" in f.paved_road


def test_new_stem_authored_rejected_is_refused(repo):
    root, g, journal = repo
    write(root, "t-one", VALID.replace("---\npriority", "---\nstate: rejected\npriority"))
    assert "state: rejected" in messages(do_intake(root, g, journal).refused["t-one"])


def test_established_seed_keeps_its_source_across_an_edit(repo):
    root, g, journal = repo
    seed = VALID.replace("---\npriority", "---\nstate: confirmed\nsource: seed\npriority")
    write(root, "t-seed", seed)
    run(g.add(root, ["tickets/t-seed/ticket.md"]))
    run(g.commit(root, "conductor seed"))
    edited = seed.replace("Out: everything else.", "Out: everything else, still.")
    path = write(root, "t-seed", edited)

    result = do_intake(root, g, journal)

    assert result.committed == ("t-seed",)
    assert path.read_text() == edited  # never restamped human
    [event] = journal.read()
    assert event.body["source"] == "seed" and event.body["new"] is False


def test_staged_change_outside_ticket_files_refuses_intake(repo):
    root, g, journal = repo
    (root / "chupa" / "thing.py").write_text("x = 1\n")
    run(g.add(root, ["chupa/thing.py"]))
    write(root, "t-one", VALID)
    with pytest.raises(IntakeRefused) as e:
        do_intake(root, g, journal)
    assert "chupa/thing.py" in e.value.finding.message and e.value.finding.paved_road
    assert journal.read() == []


def test_staged_refused_ticket_is_in_no_intake_commit(repo):
    root, g, journal = repo
    write(root, "a-bad", VALID.replace("priority: P2", "priority: urgent"))
    run(g.add(root, ["tickets/a-bad/ticket.md"]))
    write(root, "b-good", VALID)

    result = do_intake(root, g, journal)

    assert "a-bad" in result.refused and result.committed == ("b-good",)
    show = run(g._run(root, "show", "--name-only", "--format=", "HEAD"))
    assert show.split() == ["tickets/b-good/ticket.md"]


def test_nothing_pending_is_a_no_op(repo):
    root, g, journal = repo
    result = do_intake(root, g, journal)
    assert result.committed == () and not result.refused


# --- bug evidence at intake ------------------------------------------------------------------


def bug_text():
    return VALID.replace("kind: feature", "kind: bug").replace("## Time budget", "## Regression\n```\nuv run pytest tests/test_thing.py\n```\n- carries: tests/\n\n## Time budget")


def evidence_file(root, stem="t-bug", name="failure.txt"):
    path = root / "tickets" / stem / "evidence" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("observed failure\n")
    return path


@pytest.mark.parametrize("changed", [False, True])
def test_bug_without_evidence_refused_at_intake(repo, changed):
    root, g, journal = repo
    path = write(root, "t-bug", complete(bug_text()) if changed else bug_text())
    if changed:
        run(g.add(root, ["tickets/t-bug/ticket.md"]))
        run(g.commit(root, "existing bug"))
        path.write_text(path.read_text().replace("Operators need it.", "Operators still need it."))
    original = path.read_bytes()
    head = run(g.rev_parse(root, "HEAD"))
    result = do_intake(root, g, journal)
    assert result.committed == ()
    [finding] = result.refused["t-bug"]
    assert "add the observed failure" in finding.paved_road
    assert "tickets/t-bug/evidence" in finding.paved_road
    assert run(g.rev_parse(root, "HEAD")) == head
    assert path.read_bytes() == original
    assert journal.read() == []


@pytest.mark.parametrize("changed", [False, True])
def test_bug_evidence_committed_with_ticket(repo, changed):
    root, g, journal = repo
    path = write(root, "t-bug", bug_text())
    evidence = evidence_file(root, name="nested/failure.txt")
    if changed:
        assert do_intake(root, g, journal).committed == ("t-bug",)
        path.write_text(path.read_text().replace("Operators need it.", "Operators still need it."))
        evidence.write_text("another observed failure\n")
    head = run(g.rev_parse(root, "HEAD"))
    run(g.add(root, [str(evidence.relative_to(root))]))
    result = do_intake(root, g, journal)
    assert result.committed == ("t-bug",) and not result.refused
    assert run(g._run(root, "rev-list", "--count", f"{head}..HEAD")).strip() == "1"
    assert set(run(g._run(root, "show", "--name-only", "--format=", "HEAD")).splitlines()) == {"tickets/t-bug/ticket.md", "tickets/t-bug/evidence/nested/failure.txt"}
    assert run(g.status_porcelain(root)) == ""


def test_feature_needs_no_evidence(repo):
    root, g, journal = repo
    write(root, "t-feature", VALID)
    result = do_intake(root, g, journal)
    assert result.committed == ("t-feature",) and not result.refused


@pytest.mark.parametrize("directory_link", [False, True])
def test_symlink_is_not_evidence(repo, directory_link):
    from chupa.tickets import evidence_findings

    root, g, journal = repo
    write(root, "t-bug", bug_text())
    target = root / "observed.txt"
    target.write_text("observed failure\n")
    directory = root / "tickets/t-bug/evidence"
    if directory_link:
        directory.symlink_to(root, target_is_directory=True)
    else:
        directory.mkdir()
        (directory / "failure.txt").symlink_to(target)
    ticket = validate_ticket("t-bug", complete(bug_text()), root)
    assert len(evidence_findings(ticket, root)) == 1
    assert "t-bug" in do_intake(root, g, journal).refused
    assert journal.read() == []


def test_gitignored_only_evidence_is_refused_untouched(repo):
    root, g, journal = repo
    (root / ".gitignore").write_text("*.log\n")
    run(g.add(root, [".gitignore"]))
    run(g.commit(root, "ignore logs"))
    path = write(root, "t-bug", bug_text())
    evidence = evidence_file(root, name="failure.log")
    original = path.read_bytes(), evidence.read_bytes()
    head = run(g.rev_parse(root, "HEAD"))
    result = do_intake(root, g, journal)
    assert result.committed == ()
    assert "must not be gitignored" in messages(result.refused["t-bug"])
    assert (path.read_bytes(), evidence.read_bytes()) == original
    assert run(g.rev_parse(root, "HEAD")) == head
    assert journal.read() == []


@pytest.mark.parametrize(
    ("front_state", "journal_state"),
    [
        ("merged", None),
        ("rejected", None),
        ("confirmed", "merged"),
        ("confirmed", "already_satisfied"),
        ("confirmed", "rejected"),
    ],
)
def test_settled_bug_is_not_rejudged_for_evidence(repo, front_state, journal_state):
    root, g, journal = repo
    text = complete(bug_text()).replace("state: confirmed", f"state: {front_state}")
    path = write(root, "t-bug", text)
    run(g.add(root, ["tickets/t-bug/ticket.md"]))
    run(g.commit(root, "historical bug without evidence"))
    if journal_state:
        journal.append(EventType.STATE_TRANSITION, {"to": journal_state}, ticket="t-bug")
    path.write_text(text.replace("Operators need it.", "Operators still need it."))
    result = do_intake(root, g, journal)
    assert result.committed == ("t-bug",) and not result.refused


@pytest.mark.parametrize("staged_kind", ["deletion", "symlink"])
def test_staged_uncommittable_evidence_refuses_before_any_commit(repo, staged_kind):
    root, g, journal = repo
    evidence = evidence_file(root)
    if staged_kind == "deletion":
        run(g.add(root, [str(evidence.relative_to(root))]))
        run(g.commit(root, "old evidence"))
        evidence.unlink()
    else:
        evidence.unlink()
        evidence.symlink_to(root / "chupa/thing.py")
    run(g.add(root, [str(evidence.relative_to(root))]))
    write(root, "t-bug", bug_text())
    write(root, "a-good", VALID)
    head = run(g.rev_parse(root, "HEAD"))
    with pytest.raises(IntakeRefused):
        do_intake(root, g, journal)
    assert run(g.rev_parse(root, "HEAD")) == head
    assert journal.read() == []


@pytest.mark.parametrize("kind", ["feature", "bug", "chore"])
def test_template_per_kind(tmp_path, kind):
    text = template(kind)
    assert ("## Regression" in text) == (kind == "bug")
    samples = {
        "none or bullets of existing ticket stems": "none",
        "existing repo-relative read-first path": "src/thing.py",
        "observable outcome and why it matters": "The command prints ok for operators.",
        "what changes and what stays outside this ticket": "In: the command. Out: other commands.",
        "repo-relative writable path prefix": "src/thing.py",
        "measurable outcome naming a check in backticks": "`uv run pytest` exits 0.",
        "argv command that exits 0": "uv run pytest",
        "outcome that rejects the branch": "The command needs a new dependency.",
        "estimated integer minutes": "10",
        "larger deadline in integer minutes": "20",
        "one argv command emitting the regression_result JSON protocol": "uv run python tests/reproduce.py",
        "test or fixture path prefix needed by the command": "tests/reproduce.py",
    }
    filled = re.sub(r"<([^<>]+)>", lambda match: samples[match[1]], text)
    assert "<" not in filled
    (tmp_path / "src").mkdir()
    (tmp_path / "src/thing.py").write_text("")
    ticket = validate_ticket("t-template", filled, tmp_path)
    assert ticket.frontmatter.kind == kind
    assert ticket.context == ("src/thing.py",)
    assert ticket.regression == (("uv", "run", "python", "tests/reproduce.py") if kind == "bug" else ())
    assert ticket.carries == (("tests/reproduce.py",) if kind == "bug" else ())


def test_new_bug_creates_no_evidence(repo, capsys):
    from chupa import __main__ as cli

    root, _, _ = repo
    assert cli.main(["new", "t-bug", "--kind", "bug"], cwd=root) == 0
    assert (root / "tickets/t-bug/ticket.md").read_text() == template("bug")
    assert sorted(p.relative_to(root).as_posix() for p in (root / "tickets/t-bug").rglob("*")) == ["tickets/t-bug/ticket.md"]
    assert "add the observed failure" in capsys.readouterr().out


def test_new_prints_bug_evidence_finding(repo, monkeypatch, capsys):
    from chupa import __main__ as cli

    root, _, _ = repo
    monkeypatch.setattr(cli, "template", lambda kind: complete(bug_text()))
    assert cli._new(root, "t-bug", "bug") == 0
    assert "add the observed failure" in capsys.readouterr().out


def test_runs_before_parsing_and_refusals(repo):
    root, _, _ = repo
    write(root, "t-other", VALID)

    def hinted(target):
        return complete(VALID + f"\n## Runs before\n- {target}\n")

    assert validate_ticket("t-one", hinted("t-other"), root).runs_before == ("t-other",)
    for target in ("t-one", "missing", "none"):
        findings = refusal(root, hinted(target))
        assert all("Runs before" in f.message and f.paved_road for f in findings)
    write(root, "t-other", hinted("t-one"))
    findings = refusal(root, hinted("t-other"))
    assert "Runs before" in findings[0].message and "cycle" in findings[0].message
    assert findings[0].paved_road == "drop the edge that inverts the intended order"


def test_plan_contract_section_is_unknown(repo):
    root, _, _ = repo
    text = VALID.replace("## Goal / Why", "## Plan contract\n- section 11\n\n## Goal / Why")
    assert "unknown body section" in messages(refusal(root, text))


def test_context_section_findings(repo):
    root, _, _ = repo
    (root / "m.py").write_text("class B:\n    def run(self):\n        return 7\n")
    (root / "d.md").write_text("## Two\na\n## Two\nb\n")
    for entry in ("m.py::Missing", "m.py#Two", "d.md::B", "d.md#Nope", "d.md#Two", "m.py\n- m.py::B.run"):
        [finding] = refusal(root, VALID.replace("chupa/thing.py\n\n## Goal", entry + "\n\n## Goal"))
        assert finding.paved_road and "Context" in finding.message  # each bad entry is refused with a fix


def test_context_directory_is_refused(repo):
    root, _, _ = repo
    text = complete(VALID.replace("chupa/thing.py\n\n## Goal", "chupa\n\n## Goal"))
    with pytest.raises(TicketInvalid) as exc:
        validate_ticket("t-one", text, root)
    assert any("Context" in finding.message and "file" in finding.message for finding in exc.value.findings)


def test_context_binary_selector_and_fenced_heading(repo):
    root, _, _ = repo
    (root / "image.png").write_bytes(b"\xff")
    [finding] = refusal(root, VALID.replace("chupa/thing.py\n\n## Goal", "image.png#x\n\n## Goal"))
    assert ".md" in finding.message  # extension checked before decoding
    (root / "d.md").write_text("## Two\n```\n# Two\n```\ntext\n## Three\n")
    ticket = validate_ticket("t-one", complete(VALID.replace("chupa/thing.py\n\n## Goal", "d.md#Two\n\n## Goal")), root)
    from chupa.stages import implement_inputs

    assert implement_inputs(root, "", ticket, ())["context"] == "### d.md#Two\n## Two\n```\n# Two\n```\ntext\n"  # fence is not a heading


def test_context_whole_file_unchanged(repo):
    from chupa.stages import implement_inputs

    root, _, _ = repo
    (root / "chupa/thing.py").write_text("first = 1\nsecond = 2\n")
    ticket = validate_ticket("t-one", complete(VALID), root)
    assert implement_inputs(root, "", ticket, ())["context"] == "### chupa/thing.py\nfirst = 1\nsecond = 2\n"  # whole file, not an excerpt
