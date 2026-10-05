"""Implement -> Check -> Review stage transitions with the scripted fake (CHUPA_PLAN.md sections 4, 5, 19.P1)."""

import asyncio
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest

from chupa.config import load_config
from chupa.driver import Driver
from chupa.git import Git
from chupa.llm import FakeLLM, LLMRequest
from chupa.seams import LocalFileSystem, SubprocessExec
from chupa.stages import (
    DIFF_BUDGET_FILES,
    ApprovedInvoice,
    DiffBudgetGate,
    Evidence,
    Invoice,
    PackingSlip,
    RunRecordGate,
    SnagList,
    StageContext,
    read_review,
    run_stages,
)
from chupa.tickets import TicketInvalid, validate_ticket

SPECS = Path(__file__).resolve().parent.parent / "specs"
SECRET = "sk-test-not-for-children"
ENV = {
    "PATH": "/usr/bin:/bin",
    "HOME": "/nonexistent",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@t",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@t",
    "FAKE_KEY": SECRET,
}

CONFIG = """schema_version: 1
state_dir: .chupa/state
providers:
  - name: fake
    kind: cli
    auth: FAKE_KEY
    models_by_tier: {low: m, medium: m, high: m, max: m}
    limits: {concurrency: 1, est_cost_per_call_usd: 0.5}
routing:
  - {tier: medium, surface: implement, candidates: [{provider: fake}]}
  - {tier: medium, surface: review, candidates: [{provider: fake}]}
review: {}
merge: {}
engine_plane_safety_inventory: [config.yaml]
"""

TICKET = """---
state: confirmed
source: human
priority: P2
kind: feature
{bypass}---

## Depends on
none

## Context
- chupa/thing.py

## Goal / Why
`thing.py` holds the word ok.

## Scope in / Scope out
In: thing. Out: the rest.

## Scope fence
- chupa/thing.py

## Acceptance criteria
1. `grep -q ok chupa/thing.py` exits 0.

## Verification
```
grep -q ok chupa/thing.py
env
```

## Definition of rejected
Needs a new dependency.

## Time budget
- expected: 10m
- stuck: 20m
"""

STEM = "add-thing"


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], env=ENV, capture_output=True, text=True,
                          check=True).stdout


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "chupa").mkdir(parents=True)
    (root / "chupa" / "thing.py").write_text("")
    (root / "CHUPA_PLAN.md").write_text("# Plan\n")
    (root / "config.yaml").write_text(CONFIG)
    (root / ".gitignore").write_text(".chupa/\n")
    git(root, "init", "-b", "main")
    git(root, "add", ".")
    git(root, "commit", "-m", "base")
    return root


def author(repo: Path, bypass: str = "", plan_contract: str = "") -> None:
    path = repo / "tickets" / STEM / "ticket.md"
    path.parent.mkdir(parents=True)
    path.write_text(TICKET.format(bypass=bypass).replace("## Goal / Why", plan_contract + "## Goal / Why"))
    git(repo, "add", "tickets")
    git(repo, "commit", "-m", f"chupa({STEM}): ticket")


def implement_reply(outcome: str = "ok", findings: list | None = None) -> str:
    return "```json\n" + json.dumps({
        "outcome": outcome, "summary": "wrote ok", "surprises": "", "dead_ends": "none",
        "predicted_vs_actual": "10m predicted, 2m actual", "findings": findings or [],
    }) + "\n```"


def agent(files: dict[str, str], outcome: str = "ok"):
    """A scripted implementer: edits the worktree, commits on the branch, replies."""

    def act(req: LLMRequest) -> str:
        assert req.worktree is not None
        for rel, text in files.items():
            (req.worktree / rel).parent.mkdir(parents=True, exist_ok=True)
            (req.worktree / rel).write_text(text)
        if files:
            git(req.worktree, "add", *files)
            git(req.worktree, "commit", "-m", "work")
        return implement_reply(outcome)

    return act


def verdict(v: str = "approve", findings: list | None = None) -> str:
    return json.dumps({"verdict": v, "summary": "looked", "findings": findings or []})


SNAG = {"code": "logic", "path": "chupa/thing.py", "line": 1, "message": "wrong word", "paved_road": "write ok"}


def run(repo: Path, script: list, bypass: str = "", plan_contract: str = ""):
    author(repo, bypass, plan_contract)
    config = load_config(None, cwd=repo)
    llm = FakeLLM(script)
    clock = lambda: datetime(2026, 10, 5, tzinfo=UTC)  # noqa: E731

    async def never(seconds: float) -> None:
        await asyncio.Event().wait()

    exec_ = SubprocessExec()
    driver = Driver.from_config(config, llm=llm, env=ENV, clock=clock, sleep=never)
    ctx = StageContext(repo=repo, config=config, env=ENV, exec_=exec_, git=Git(exec_, env=ENV, timeout=30.0),
                       fs=LocalFileSystem(), driver=driver, specs_dir=SPECS)
    ticket = validate_ticket(STEM, (repo / "tickets" / STEM / "ticket.md").read_text(), repo)
    return asyncio.run(run_stages(ctx, ticket)), llm, config


def subjects(repo: Path) -> list[str]:
    return git(repo, "log", "--format=%s", "main").splitlines()[::-1]


def outcomes(result) -> dict[str, str]:
    return {name: r.outcome for name, r in result.results.items()}


# --- transitions --------------------------------------------------------------------------------


def test_implement_renders_numeric_plan_contract_section(repo):
    (repo / "CHUPA_PLAN.md").write_text("# Plan\n\n## 11. Failure spine\n\nSpine prose.\n")
    git(repo, "commit", "-am", "plan section 11")

    result, llm, _ = run(repo, [agent({"chupa/thing.py": "ok\n"}), verdict()],
                         plan_contract="## Plan contract\n- section 11\n\n")

    assert outcomes(result) == {"implement": "ok", "check": "ok", "review": "ok"}
    assert "## 11. Failure spine\n\nSpine prose." in llm.requests[0].rendered


def test_bare_numeric_plan_contract_bullet_is_refused_at_intake(repo):
    (repo / "CHUPA_PLAN.md").write_text("# Plan\n\n## 11. Failure spine\n")
    author(repo, plan_contract="## Plan contract\n- 11\n\n")

    with pytest.raises(TicketInvalid) as e:
        validate_ticket(STEM, (repo / "tickets" / STEM / "ticket.md").read_text(), repo)
    assert any("Plan contract" in finding.message for finding in e.value.findings)


def test_implement_check_review_all_ok_with_artifacts_and_provenance(repo):
    result, llm, config = run(repo, [agent({"chupa/thing.py": "ok\n"}), verdict()])

    assert outcomes(result) == {"implement": "ok", "check": "ok", "review": "ok"}
    head = git(repo, "rev-parse", STEM).strip()
    slip, invoice, review = (r.artifact for r in result.results.values())
    assert isinstance(slip, PackingSlip) and slip.produced_at_sha == head and slip.produced_by_spec_version == 1
    assert isinstance(invoice, Invoice) and invoice.passed and invoice.changed_files == ["chupa/thing.py"]
    assert invoice.produced_at_sha == head
    assert isinstance(review, ApprovedInvoice) and review.reviewed_sha == head and review.spec_version == "1.0"
    assert (review.provider, review.model) == ("fake", "fake")

    # One ticket-plane commit per stage terminal, on main, never on the branch.
    assert subjects(repo)[-3:] == [f"chupa({STEM}): run-record", f"chupa({STEM}): checks", f"chupa({STEM}): review"]
    canonical = repo / "tickets" / STEM
    assert read_review((canonical / "review.md").read_text()) == review
    assert Invoice.model_validate_json((canonical / "checks.json").read_text()) == invoice
    run_md = (canonical / "run.md").read_text()
    assert "## Outcome\n\nok\n" in run_md and "- provider: fake\n- model: fake\n- spec: implement 1.1" in run_md
    assert git(repo, "diff", "--name-only", f"main...{STEM}").split() == ["chupa/thing.py"]
    outbox = config.worktree_root / STEM / "tickets" / STEM
    assert sorted(p.name for p in outbox.iterdir()) == ["ticket.md"]  # lifted and unlinked

    implement_req, review_req = llm.requests
    assert implement_req.surface == "implement" and implement_req.worktree == config.worktree_root / STEM
    assert "### chupa/thing.py" in implement_req.rendered
    assert review_req.surface == "review" and review_req.worktree is None  # read-only surface
    assert "+ok" in review_req.rendered  # the reviewer sees `git diff main...<stem>`


def test_premise_failed_stops_after_implement_with_its_run_record(repo):
    finding = {"code": "premise", "path": None, "line": None, "message": "contradicts X", "paved_road": "drop X"}
    act = lambda req: implement_reply("premise_failed", [finding])  # noqa: E731
    result, llm, _ = run(repo, [act])

    assert outcomes(result) == {"implement": "premise_failed"}
    assert [f.message for f in result.last[1].findings] == ["contradicts X"]
    assert "## Outcome\n\npremise_failed\n" in (repo / "tickets" / STEM / "run.md").read_text()
    assert len(llm.requests) == 1


def test_check_fails_closed_on_an_out_of_fence_edit_and_never_reaches_review(repo):
    result, llm, _ = run(repo, [agent({"chupa/thing.py": "ok\n", "chupa/other.py": "x\n"})])

    assert outcomes(result) == {"implement": "ok", "check": "gate_failed"}
    assert [(f.code, f.path) for f in result.last[1].findings] == [("scope_fence", "chupa/other.py")]
    assert not result.last[1].artifact.passed
    assert json.loads((repo / "tickets" / STEM / "checks.json").read_text())["passed"] is False
    assert len(llm.requests) == 1  # review never called


def test_gate_bypass_demotes_its_code_to_soft(repo):
    bypass = "gate_bypass:\n  - {code: scope_fence, reason: generated sibling}\n"
    result, _, _ = run(repo, [agent({"chupa/thing.py": "ok\n", "chupa/other.py": "x\n"}), verdict()], bypass)

    assert outcomes(result) == {"implement": "ok", "check": "ok", "review": "ok"}
    invoice = result.results["check"].artifact
    assert invoice.bypassed == ["scope_fence"]
    assert [f.code for f in result.results["check"].findings] == ["scope_fence"]  # still reported, soft


def test_red_verification_fails_check(repo):
    result, _, _ = run(repo, [agent({"chupa/thing.py": "nope\n"})])

    assert outcomes(result) == {"implement": "ok", "check": "gate_failed"}
    assert [f.code for f in result.last[1].findings] == ["verification"]
    assert "grep -q ok chupa/thing.py" in result.last[1].findings[0].message


def test_empty_diff_claimed_ok_fails_verification(repo):
    (repo / "chupa" / "thing.py").write_text("ok\n")
    git(repo, "commit", "-am", "green base")
    result, _, _ = run(repo, [agent({})])

    assert outcomes(result) == {"implement": "ok", "check": "gate_failed"}
    assert [f.message for f in result.last[1].findings] == ["the branch carries no committed change"]


def test_already_satisfied_is_proven_by_green_verification_and_skips_review(repo):
    (repo / "chupa" / "thing.py").write_text("ok\n")
    git(repo, "commit", "-am", "already there")
    result, llm, _ = run(repo, [agent({}, outcome="already_satisfied")])

    assert outcomes(result) == {"implement": "ok", "check": "already_satisfied"}
    assert result.results["implement"].artifact.outcome == "already_satisfied"
    assert len(llm.requests) == 1


def test_review_snag_is_gate_failed_with_a_snag_list(repo):
    result, _, _ = run(repo, [agent({"chupa/thing.py": "ok\n"}), verdict("snag", [SNAG])])

    assert outcomes(result) == {"implement": "ok", "check": "ok", "review": "gate_failed"}
    assert [f.message for f in result.last[1].findings] == ["wrong word"]
    pinned = read_review((repo / "tickets" / STEM / "review.md").read_text())
    assert isinstance(pinned, SnagList) and pinned.reviewed_sha == git(repo, "rev-parse", STEM).strip()


def test_invalid_review_reply_is_reprompted_with_its_validation_finding(repo):
    result, llm, _ = run(repo, [agent({"chupa/thing.py": "ok\n"}), verdict("approve", [SNAG]), verdict()])

    assert outcomes(result)["review"] == "ok"
    assert "approve carries an empty findings list" in llm.requests[2].rendered


def test_verification_children_never_inherit_a_provider_key(repo):
    result, _, config = run(repo, [agent({"chupa/thing.py": "ok\n"}), verdict()])

    spool = (config.state_dir / "spools" / STEM / str(result.attempt) / "check" / "verify-02.txt").read_text()
    assert "PATH=/usr/bin:/bin" in spool and "FAKE_KEY" not in spool and SECRET not in spool


def test_a_fresh_run_tears_down_the_prior_worktree_and_branch(repo):
    stale = load_config(None, cwd=repo).worktree_root / STEM
    git(repo, "worktree", "add", "-b", STEM, str(stale), "main")
    (stale / "chupa" / "thing.py").write_text("stale\n")
    git(stale, "commit", "-am", "stale")

    result, _, _ = run(repo, [agent({"chupa/thing.py": "ok\n"}), verdict()])

    assert outcomes(result)["review"] == "ok"
    assert "stale" not in git(repo, "log", "--format=%s", STEM)


# --- gates --------------------------------------------------------------------------------------


def evidence(**kw) -> Evidence:
    base = dict(stem=STEM, head_sha="abc", claimed="ok", scope_fence=["chupa/"], changed_files=["chupa/a.py"],
                inserted_lines=1, verification=[], run_record=None)
    return Evidence(**{**base, **kw})


def test_diff_budget_caps_files_and_inserted_lines(tmp_path):
    gate = DiffBudgetGate()
    assert gate.check(evidence(), tmp_path).verdict == "pass"
    over = evidence(changed_files=[f"chupa/{n}.py" for n in range(DIFF_BUDGET_FILES + 1)])
    assert "split the ticket" in gate.check(over, tmp_path).findings[0].paved_road
    assert gate.check(evidence(inserted_lines=1_501), tmp_path).verdict == "fail"


def test_run_record_gate_requires_every_section_and_a_closed_outcome(tmp_path):
    gate = RunRecordGate()
    assert gate.check(evidence(), tmp_path).findings[0].message == "run.md is missing"
    bad = "## Outcome\n\nshipped\n\n## Dead ends\n\nnone\n"
    messages = [f.message for f in gate.check(evidence(run_record=bad), tmp_path).findings]
    assert len(messages) == 2 and "'shipped' is not an outcome" in messages[1]
