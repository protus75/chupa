"""Production seeding path: Check reviews each new ticket and lifts only an approved batch."""

import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from chupa.config import load_config
from chupa.driver import Driver
from chupa.git import Git
from chupa.journal import EventType
from chupa.llm import FakeLLM, LLMRequest
from chupa.providers import resolve
from chupa.runner import drive
from chupa.seams import LocalFileSystem, SubprocessExec
from chupa.stages import Invoice, StageContext
from chupa.tickets import validate_ticket
from tests.test_stages import CONFIG, ENV, STEM, TICKET, git, implement_reply, verdict
from tests.test_terminal import diagnosis_reply


def seed_text(stem: str, *, state: str = "confirmed", source: str = "seed",
              tier: str = "medium") -> str:
    return (TICKET.format(bypass="")
            .replace("state: confirmed", f"state: {state}")
            .replace("source: human", f"source: {source}\nagent_tier: {tier}")
            .replace("## Goal / Why", "## Plan contract\n- 19.L\n- 19.P2\n\n## Goal / Why")
            .replace("`thing.py` holds the word ok.", f"`thing.py` holds the word ok for {stem}.")
            .replace("env\n```", "test -f chupa/thing.py\n```"))


def seeding_text() -> str:
    return seed_text(STEM).replace("- chupa/thing.py\n\n## Acceptance criteria",
                                   "- chupa/thing.py\n- tickets\n\n## Acceptance criteria")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "chupa").mkdir(parents=True)
    (root / "chupa/thing.py").write_text("")
    (root / "CHUPA_PLAN.md").write_text("### 19.L Build laws\nSeed law.\n\n### 19.P2 Phase 2\nPhase law.\n")
    routes = """  - {tier: high, surface: review, candidates: [{provider: fake}]}
  - {tier: high, surface: requisition_review, candidates: [{provider: fake, model: high-seed}]}
"""
    (root / "config.yaml").write_text(CONFIG.replace("review: {}", routes + "review: {}"))
    (root / ".gitignore").write_text(".chupa/\n")
    for existing in ("existing-a", "existing-b"):
        path = root / "tickets" / existing / "ticket.md"
        path.parent.mkdir(parents=True)
        path.write_text(TICKET.format(bypass=""))
    own = root / "tickets" / STEM / "ticket.md"
    own.parent.mkdir(parents=True)
    own.write_text(seeding_text())
    git(root, "init", "-b", "main")
    git(root, "add", ".")
    git(root, "commit", "-m", "base with existing tickets")
    return root


def context(repo: Path, script: list) -> tuple[StageContext, FakeLLM]:
    config = load_config(None, cwd=repo)
    llm = FakeLLM(script)

    async def never(seconds: float) -> None:
        await asyncio.Event().wait()

    exec_ = SubprocessExec()
    driver = Driver.from_config(config, llm=llm, env=ENV,
                                clock=lambda: datetime(2026, 10, 6, tzinfo=UTC), sleep=never)
    ctx = StageContext(repo=repo, config=config, env=ENV, exec_=exec_,
                       git=Git(exec_, env=ENV, timeout=30.0), fs=LocalFileSystem(), driver=driver,
                       specs_dir=Path(__file__).resolve().parent.parent / "specs")
    return ctx, llm


def ticket(repo: Path):
    return validate_ticket(STEM, (repo / "tickets" / STEM / "ticket.md").read_text(), repo)


def write_seeds(seeds: dict[str, str], *, code: str = "ok\n"):
    def act(req: LLMRequest) -> str:
        assert req.surface == "implement" and req.worktree is not None
        (req.worktree / "chupa/thing.py").write_text(code)
        git(req.worktree, "add", "chupa/thing.py")
        git(req.worktree, "commit", "-m", "work")
        for stem, text in seeds.items():
            path = req.worktree / "tickets" / stem / "ticket.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        return implement_reply()

    return act


def requisition(verdict_name: str, findings: list | None = None) -> str:
    return json.dumps({"verdict": verdict_name, "summary": "reviewed seed", "findings": findings or []})


def run(repo: Path, script: list):
    ctx, llm = context(repo, script)
    result = asyncio.run(drive(ctx, ticket(repo)))
    return result, ctx, llm


def invoice(repo: Path) -> Invoice:
    return Invoice.model_validate_json((repo / "tickets" / STEM / "checks.json").read_text())


def intake_events(ctx: StageContext):
    return [e for e in ctx.driver.journal.read()
            if e.type == EventType.SIGNAL and e.body.get("signal") == "ticket_intake"
            and e.body.get("seeded_by") == STEM]


def test_two_approved_seeds_have_one_ticket_plane_commit_and_individual_reviews(repo):
    seeds = {"alpha-seed": seed_text("alpha-seed", tier="high"),
             "beta-seed": seed_text("beta-seed")}
    outcome, ctx, llm = run(repo, [write_seeds(seeds), requisition("approve"),
                                   requisition("approve"), verdict()])

    assert outcome == "merged"
    subjects = git(repo, "log", "--format=%s", "main").splitlines()
    assert subjects.count(f"chupa({STEM}): seeds") == 1
    assert sorted(git(repo, "show", "--name-only", "--format=", "main~2").split()) == [
        "tickets/alpha-seed/ticket.md", "tickets/beta-seed/ticket.md"]
    assert [(e.ticket, e.body) for e in intake_events(ctx)] == [
        (stem, {"signal": "ticket_intake", "source": "seed", "state": "confirmed", "new": True,
                "commit": git(repo, "rev-parse", "main~2").strip(), "seeded_by": STEM})
        for stem in seeds]
    assert [(s.stem, s.verdict, s.ticket_sha) for s in invoice(repo).seeds] == [
        (stem, "approve", git(repo, "rev-parse", f"main:tickets/{stem}/ticket.md").strip())
        for stem in seeds]
    requests = [r for r in llm.requests if r.surface == "requisition_review"]
    assert len(requests) == 2
    assert "alpha-seed" in requests[0].rendered and "beta-seed" not in requests[0].rendered
    assert "beta-seed" in requests[1].rendered and "alpha-seed" not in requests[1].rendered
    assert requests[0].tier == "high" and resolve(ctx.config, requests[0].tier,
                                                   "requisition_review").model == "high-seed"
    keys = [e.key for e in ctx.driver.journal.read() if e.type == EventType.EFFECT_COMPLETION]
    assert [k for k in keys if k and "/requisition_review/" in k] == [
        f"llm/{STEM}/0/requisition_review/0/1", f"llm/{STEM}/0/requisition_review/0/2"]


def test_one_snag_blocks_the_batch_but_records_the_other_approval(repo):
    seeds = {"alpha-seed": seed_text("alpha-seed"), "beta-seed": seed_text("beta-seed")}
    snag = {"code": "scope", "path": "tickets/beta-seed/ticket.md", "line": None,
            "message": "missing test", "paved_road": "add a test"}
    outcome, ctx, llm = run(repo, [write_seeds(seeds), requisition("approve"),
                                   requisition("snag", [snag]), diagnosis_reply()])

    assert outcome == "gate_failed"
    assert [(s.stem, s.verdict) for s in invoice(repo).seeds] == [
        ("alpha-seed", "approve"), ("beta-seed", "snag")]
    assert any(r.code == "requisition_review" and r.verdict == "fail" for r in invoice(repo).reports)
    assert not (repo / "tickets/alpha-seed/ticket.md").exists()
    assert not (repo / "tickets/beta-seed/ticket.md").exists()
    assert not intake_events(ctx)
    assert f"chupa({STEM}): seeds" not in git(repo, "log", "--format=%s", "main").splitlines()
    assert [r.surface for r in llm.requests] == ["implement", "requisition_review",
                                                    "requisition_review", "diagnose"]


@pytest.mark.parametrize("change", [{"state": "draft"}, {"source": "human"}])
def test_wrong_seed_frontmatter_fails_without_a_requisition_call(repo, change):
    text = seed_text("alpha-seed", **change)
    outcome, ctx, llm = run(repo, [write_seeds({"alpha-seed": text}), diagnosis_reply()])

    assert outcome == "gate_failed"
    assert [(s.stem, s.verdict, s.mechanical) for s in invoice(repo).seeds] == [
        ("alpha-seed", "snag", "seed frontmatter")]
    assert [r.surface for r in llm.requests] == ["implement", "diagnose"]
    assert not intake_events(ctx)


def test_lint_failure_is_a_recorded_snag_without_a_requisition_call(repo):
    outcome, ctx, llm = run(repo, [write_seeds({"alpha-seed": "not a ticket\n"}), diagnosis_reply()])

    assert outcome == "gate_failed"
    [seed] = invoice(repo).seeds
    assert seed.verdict == "snag" and seed.mechanical == "ticket lint failed"
    assert seed.findings[0].code == "ticket_schema"
    assert [r.surface for r in llm.requests] == ["implement", "diagnose"]
    assert not intake_events(ctx)


def test_identical_own_seed_is_skipped_on_rerun_and_prior_approvals_survive(repo):
    seeds = {"alpha-seed": seed_text("alpha-seed"), "beta-seed": seed_text("beta-seed")}
    first, _, _ = run(repo, [write_seeds(seeds), requisition("approve"), requisition("approve"), verdict()])
    assert first == "merged"

    second, ctx, llm = run(repo, [write_seeds({"alpha-seed": seeds["alpha-seed"]}, code="ok again\n"),
                                  verdict()])

    assert second == "merged"
    assert [r.surface for r in llm.requests] == ["implement", "review"]
    assert [(s.stem, s.verdict) for s in invoice(repo).seeds] == [
        ("alpha-seed", "approve"), ("beta-seed", "approve")]
    assert len(intake_events(ctx)) == 2
    assert git(repo, "log", "--format=%s", "main").splitlines().count(f"chupa({STEM}): seeds") == 1


def test_rewriting_a_foreign_existing_ticket_fails_check(repo):
    foreign = (repo / "tickets/existing-a/ticket.md").read_text() + "\n"
    outcome, ctx, llm = run(repo, [write_seeds({"existing-a": foreign}), diagnosis_reply()])

    assert outcome == "gate_failed"
    assert [r.surface for r in llm.requests] == ["implement", "diagnose"]
    assert invoice(repo).seeds[0].findings[0].code == "requisition_review"
    assert "already exists on main" in invoice(repo).seeds[0].findings[0].message
    assert not intake_events(ctx)


def test_mechanical_failure_preserves_prior_seed_approvals_for_later_merge(repo):
    seeds = {"alpha-seed": seed_text("alpha-seed"), "beta-seed": seed_text("beta-seed")}
    first, _, _ = run(repo, [write_seeds(seeds), requisition("approve"), requisition("approve"), verdict()])
    assert first == "merged"

    second, _, _ = run(repo, [write_seeds({"alpha-seed": seeds["alpha-seed"]}, code="nope\n"),
                              diagnosis_reply()])
    assert second == "gate_failed"
    assert [(s.stem, s.verdict) for s in invoice(repo).seeds] == [
        ("alpha-seed", "approve"), ("beta-seed", "approve")]

    third, ctx, llm = run(repo, [write_seeds({"alpha-seed": seeds["alpha-seed"]}, code="ok third\n"),
                                 verdict()])
    assert third == "merged"
    assert [r.surface for r in llm.requests] == ["implement", "review"]
    assert len(intake_events(ctx)) == 2
