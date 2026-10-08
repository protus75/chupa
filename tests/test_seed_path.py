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
from chupa.artifacts import Finding
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


@pytest.mark.parametrize("section", ["Context", "On-demand"])
def test_seed_context_must_exist_on_main(repo, section):
    own = repo / "tickets" / STEM / "ticket.md"
    own.write_text(own.read_text().replace("- tickets\n", "- tickets\n- tests/new_idiom.py\n"))
    git(repo, "add", str(own.relative_to(repo)))
    git(repo, "commit", "-m", "allow the seeding branch to create an idiom")
    text = seed_text("alpha-seed")
    if section == "On-demand":
        text = text.replace("## Goal / Why", "## On-demand\n- tests/new_idiom.py\n\n## Goal / Why")
        text = text.replace("## Scope fence\n", "## Scope fence\n- tests/new_idiom.py\n")
    else:
        text = text.replace("## Context\n", "## Context\n- tests/new_idiom.py\n")

    def implement(req: LLMRequest) -> str:
        assert req.worktree is not None
        path = req.worktree / "tests/new_idiom.py"
        path.parent.mkdir(parents=True)
        path.write_text("# Branch-only idiom.\n")
        git(req.worktree, "add", "tests/new_idiom.py")
        git(req.worktree, "commit", "-m", "create branch-only idiom")
        return write_seeds({"alpha-seed": text})(req)

    def respond(req: LLMRequest) -> str:
        return diagnosis_reply() if req.surface == "diagnose" else requisition("approve")

    outcome, ctx, llm = run(repo, [implement, respond, verdict(), diagnosis_reply()])

    assert outcome == "gate_failed"
    assert terminal_body(ctx)["stage"] == "check"
    [seed] = invoice(repo).seeds
    assert (seed.verdict, seed.mechanical) == ("snag", "ticket lint failed")
    assert any("tests/new_idiom.py" in f.message for f in seed.findings)
    assert [r.surface for r in llm.requests] == ["implement", "diagnose"]
    assert not (repo / "tests/new_idiom.py").exists()
    assert not intake_events(ctx)


def test_seed_review_renders_context_from_main(repo):
    (repo / "chupa/thing.py").write_text("ok main context\n")
    git(repo, "add", "chupa/thing.py")
    git(repo, "commit", "-m", "provide main context")
    outcome, _, llm = run(repo, [write_seeds({"alpha-seed": seed_text("alpha-seed")},
                                          code="ok branch context\n"),
                               requisition("approve"), verdict()])

    assert outcome == "merged"
    [request] = [r for r in llm.requests if r.surface == "requisition_review"]
    assert "ok main context" in request.rendered
    assert "ok branch context" not in request.rendered


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


def verdict_events(ctx: StageContext) -> list:
    return [e for e in ctx.driver.journal.read()
            if e.type == EventType.SIGNAL and e.body.get("signal") == "requisition_verdict"]


def test_retry_keeps_the_approved_seed_and_re_reviews_only_the_snag_with_its_prior(repo):
    alpha, beta = seed_text("alpha-seed"), seed_text("beta-seed")
    snag = {"code": "scope", "message": "missing test", "paved_road": "add a test", "kind": "authoring_error"}
    first, ctx, _ = run(repo, [write_seeds({"alpha-seed": alpha, "beta-seed": beta}), requisition("approve"),
                               requisition("snag", [snag]), diagnosis_reply()])
    assert first == "gate_failed"
    assert [(e.ticket, e.body["verdict"], e.body["seeding"]) for e in verdict_events(ctx)] == [
        ("alpha-seed", "approve", STEM), ("beta-seed", "snag", STEM)]
    assert verdict_events(ctx)[1].body["findings"] == [snag]

    fixed = beta.replace("holds the word ok for beta-seed.", "holds the word ok for beta-seed, tested.")

    def retry(req: LLMRequest) -> str:
        assert "## Approved seeds (keep verbatim)" in req.rendered and "tickets/alpha-seed/ticket.md" in req.rendered
        assert (req.worktree / "tickets/alpha-seed/ticket.md").read_text() == alpha  # restored, never re-authored
        return write_seeds({"beta-seed": fixed})(req)

    second, ctx, llm = run(repo, [retry, requisition("approve"), verdict()])
    assert second == "merged"
    [review] = [r for r in llm.requests if r.surface == "requisition_review"]  # alpha is not re-reviewed
    assert "Verdict: snag" in review.rendered and "missing test" in review.rendered
    assert "+" in review.rendered and "tested." in review.rendered  # the diff from the judged text
    assert (repo / "tickets/alpha-seed/ticket.md").read_text() == alpha
    assert (repo / "tickets/beta-seed/ticket.md").read_text() == fixed


REGISTRY_ROW = ("\n### 19.P3 Phase 3\n\n```yaml\n# BEGIN_REGISTRY_P3\nphase: 3\nadmissions:\n  - [gamma-seed]\n"
                "seeds:\n  gamma-seed: {fence: [chupa/thing.py]}\n# END_REGISTRY_P3\n```\n")


def add_registry_row(repo: Path) -> None:
    (repo / "CHUPA_PLAN.md").write_text((repo / "CHUPA_PLAN.md").read_text() + REGISTRY_ROW)
    (repo / "tests").mkdir(exist_ok=True)
    (repo / "tests/test_plan_lint.py").write_text("")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "registry row without an entry unit")


def terminal_body(ctx: StageContext) -> dict:
    return next(e.body for e in reversed(ctx.driver.journal.read())
                if e.type == EventType.STATE_TRANSITION and e.ticket == STEM)


def test_row_seed_without_its_entry_unit_files_a_hardening_ticket_and_holds(repo):
    add_registry_row(repo)
    outcome, ctx, llm = run(repo, [write_seeds({"gamma-seed": seed_text("gamma-seed")})])

    assert outcome == "gate_failed"
    [seed] = invoice(repo).seeds
    assert (seed.verdict, seed.mechanical) == ("snag", "entry unit gap")
    assert seed.findings[0].unit == "19.P3.gamma-seed"
    assert seed.findings[0].kind == "spec_gap" and "19.P3.gamma-seed is missing" in seed.findings[0].message
    assert [r.surface for r in llm.requests] == ["implement"]  # no review call, no diagnosis
    hardening = validate_ticket("plan-gap-1",
                                (repo / "tickets/plan-gap-1/ticket.md").read_text(), repo)
    assert hardening.scope_fence == ("CHUPA_PLAN.md#19.P3.gamma-seed",)
    assert hardening.frontmatter.priority == ticket(repo).frontmatter.priority
    assert (hardening.frontmatter.agent_tier, hardening.frontmatter.agent_effort) == ("medium", "medium")
    assert hardening.frontmatter.source == "seed" and "seeded_by" not in str(ctx.driver.journal.read())
    assert terminal_body(ctx) == {"to": "gate_failed", "stage": "check", "reason": "spec_gap",
                                  "dispatch": "spec_gap_hold", "round": 1,
                                  "plan_units": {"19.P3.gamma-seed": "absent"}}
    events = ctx.driver.journal.read()
    [record] = [e for e in events if e.body.get("signal") == "hardening_round"]
    assert record.ticket == "plan-gap-1"
    assert record.body == {"signal": "hardening_round", "round": 1,
        "units": {"19.P3.gamma-seed": "absent"}, "filed_by": STEM,
        "gaps": [{"unit": "19.P3.gamma-seed", "message": seed.findings[0].message}]}
    assert not any(e.body.get("signal") == "spec_gap_hold" for e in events)
    completion = next(e for e in events if e.key == "ticket-plane/hardening/1"
                      and e.type == EventType.EFFECT_COMPLETION)
    assert events.index(completion) < events.index(record)
    sha = git(repo, "rev-parse", f"HEAD:tickets/{STEM}/ticket.md").strip()
    assert [e.body for e in ctx.driver.journal.read() if e.type == EventType.CAP_CONSUMED] == [
        {"cap": "hardening", "ticket_sha": sha}]


def test_spent_hardening_cap_routes_the_stem_to_the_reject_queue(repo):
    from chupa.caps import consume
    from chupa.runner import hold_on_hardening
    add_registry_row(repo)
    ctx, _ = context(repo, [])
    for _ in range(ctx.config.caps.hardening):
        consume(ctx.driver.journal, STEM, "hardening", "earlier-ticket-blob")
    history = ctx.driver.journal.read()
    asyncio.run(hold_on_hardening(ctx, ticket(repo), {"19.P3.gamma-seed": ["still missing"]}, attempt=0))
    assert terminal_body(ctx) == {"to": "gate_failed", "stage": "check", "reason": "hardening cap spent",
                                  "dispatch": "reject_queue", "routed": "reject_queue",
                                  "plan_units": {"19.P3.gamma-seed": "absent"}}
    assert not list((repo / "tickets").glob("plan-gap-*"))
    assert ctx.driver.journal.read()[len(history):] == [ctx.driver.journal.read()[-1]]


@pytest.mark.parametrize("terminal", ["already_satisfied", "rejected"])
def test_already_satisfied_or_rejected_hardener_never_re_holds_forever(repo, terminal):
    from chupa.drain import awaited_hardening
    from chupa.runner import hold_on_hardening

    add_registry_row(repo)
    ctx, _ = context(repo, [])
    gaps = {"19.P3.gamma-seed": ["still missing"]}

    def hold(attempt):
        asyncio.run(hold_on_hardening(ctx, ticket(repo), gaps, attempt=attempt))

    hold(0)
    assert awaited_hardening(ctx.driver.journal.read(), STEM) == ("plan-gap-1",)
    ctx.driver.journal.append(EventType.STATE_TRANSITION, {"to": terminal}, ticket="plan-gap-1")
    assert awaited_hardening(ctx.driver.journal.read(), STEM) == ()
    hold(1)
    assert (repo / "tickets/plan-gap-2/ticket.md").is_file()
    assert awaited_hardening(ctx.driver.journal.read(), STEM) == ("plan-gap-2",)

    # Awaiting an open round costs the same unit as filing a new one.
    for attempt in range(2, ctx.config.caps.hardening):
        hold(attempt)
    history = ctx.driver.journal.read()
    draws = [e for e in history if e.type == EventType.CAP_CONSUMED and e.ticket == STEM]
    sha = git(repo, "rev-parse", f"HEAD:tickets/{STEM}/ticket.md").strip()
    assert [e.body for e in draws] == [{"cap": "hardening", "ticket_sha": sha}] * ctx.config.caps.hardening
    accounting = [e for e in history if e.ticket == STEM
                  and e.type in {EventType.CAP_CONSUMED, EventType.STATE_TRANSITION}]
    assert [e.type for e in accounting] == [EventType.CAP_CONSUMED, EventType.STATE_TRANSITION] * len(draws)
    assert all(e.body.get("dispatch") == "spec_gap_hold"
               for e in accounting if e.type == EventType.STATE_TRANSITION)

    files = sorted((repo / "tickets").glob("plan-gap-*/ticket.md"))
    hold(ctx.config.caps.hardening)
    assert terminal_body(ctx) == {"to": "gate_failed", "stage": "check", "reason": "hardening cap spent",
                                  "dispatch": "reject_queue", "routed": "reject_queue",
                                  "plan_units": {"19.P3.gamma-seed": "absent"}}
    assert sorted((repo / "tickets").glob("plan-gap-*/ticket.md")) == files
    assert ctx.driver.journal.read()[len(history):] == [ctx.driver.journal.read()[-1]]


def test_premise_mentioning_a_unit_id_in_prose_is_an_ordinary_premise(repo):
    add_registry_row(repo)
    premise = {"code": "premise", "message": "19.P3.gamma-seed contradicts merged behavior",
               "paved_road": "repair the ticket that mentions 19.P3.gamma-seed"}
    outcome, ctx, _ = run(repo, [implement_reply("premise_failed", [premise]), diagnosis_reply()])

    assert outcome == "premise_failed"
    assert terminal_body(ctx).get("dispatch") != "spec_gap_hold"
    assert any(e.body.get("cap") == "premise_bounce" for e in ctx.driver.journal.read())
    assert not any(e.body.get("signal") == "hardening_round" for e in ctx.driver.journal.read())
    assert not list((repo / "tickets").glob("plan-gap-*"))


def cite_gamma(repo: Path) -> None:
    path = repo / "tickets" / STEM / "ticket.md"
    path.write_text(path.read_text().replace("- 19.P2\n", "- 19.P2\n- 19.P3.gamma-seed\n"))
    git(repo, "add", str(path.relative_to(repo)))
    git(repo, "commit", "-m", "cite the governing entry unit")


def complete_gamma(repo: Path) -> None:
    plan = repo / "CHUPA_PLAN.md"
    plan.write_text(plan.read_text() + "\n### 19.P3.gamma-seed Gamma\n\n- **Owner:** o\n- **Records:** r\n"
                    "- **Observable:** b\n- **Tests:** t\n")
    git(repo, "commit", "-am", "complete entry unit")


def test_structured_premise_spec_gap_files_a_round_for_its_unit(repo):
    add_registry_row(repo)
    complete_gamma(repo)
    cite_gamma(repo)
    premise = {"code": "premise", "message": "the governing unit omits a needed fact",
               "paved_road": "state the fact", "kind": "spec_gap", "unit": "19.P3.gamma-seed"}
    outcome, ctx, llm = run(repo, [implement_reply("premise_failed", [premise])])

    assert outcome == "premise_failed"
    [record] = [e for e in ctx.driver.journal.read() if e.body.get("signal") == "hardening_round"]
    assert set(record.body["units"]) == {"19.P3.gamma-seed"}
    assert terminal_body(ctx)["dispatch"] == "spec_gap_hold"
    assert [e.body["cap"] for e in ctx.driver.journal.read() if e.type == EventType.CAP_CONSUMED] == ["hardening"]
    assert [r.surface for r in llm.requests] == ["implement"]


def test_cited_missing_unit_is_a_spec_gap_not_a_grammar_refusal(repo):
    add_registry_row(repo)
    seed = seed_text("alpha-seed").replace("- 19.P2\n", "- 19.P2\n- 19.P3.gamma-seed\n")
    outcome, ctx, llm = run(repo, [write_seeds({"alpha-seed": seed})])

    assert outcome == "gate_failed"
    [review] = invoice(repo).seeds
    assert (review.verdict, review.mechanical) == ("snag", "entry unit gap")
    [finding] = review.findings
    assert (finding.kind, finding.unit) == ("spec_gap", "19.P3.gamma-seed")
    assert finding.code == "requisition_review"
    assert not any(r.surface == "requisition_review" for r in llm.requests)
    [record] = [e for e in ctx.driver.journal.read() if e.body.get("signal") == "hardening_round"]
    assert record.body["units"] == {"19.P3.gamma-seed": "absent"}


def test_spec_depth_checks_every_own_and_cited_unit_before_grammar(repo):
    add_registry_row(repo)
    plan = repo / "CHUPA_PLAN.md"
    plan.write_text(plan.read_text().replace("seeds:\n  gamma-seed:",
                                            "seeds:\n  alpha-seed: {}\n  gamma-seed:")
                    + "\n### 19.P3.gamma-seed Gamma\n\n- **Owner:** o\n- **Records:** r\n")
    git(repo, "commit", "-am", "own missing unit and thin cited unit")
    seed = seed_text("alpha-seed").replace("- 19.P2\n", "- 19.P2\n- 19.P3.gamma-seed\n")
    outcome, _, llm = run(repo, [write_seeds({"alpha-seed": seed})])
    assert outcome == "gate_failed"
    [review] = invoice(repo).seeds
    assert review.mechanical == "entry unit gap"
    assert [(f.kind, f.unit) for f in review.findings] == [
        ("spec_gap", "19.P3.alpha-seed"), ("spec_gap", "19.P3.gamma-seed")]
    assert "Observable, Tests" in review.findings[1].message
    assert [r.surface for r in llm.requests] == ["implement"]


def test_premise_naming_a_fact_a_complete_entry_unit_omits_files_hardening(repo):
    add_registry_row(repo)
    complete_gamma(repo)
    cite_gamma(repo)
    premise = {"code": "premise", "message": "19.P3.gamma-seed omits which carrier hands the inbox to both factories",
               "paved_road": "state the carrier in the unit", "kind": "spec_gap", "unit": "19.P3.gamma-seed"}
    outcome, ctx, _ = run(repo, [implement_reply("premise_failed", [premise])])
    assert outcome == "premise_failed"
    assert terminal_body(ctx)["dispatch"] == "spec_gap_hold"
    assert "omits which carrier" in (repo / "tickets/plan-gap-1/ticket.md").read_text()
    sha = git(repo, "rev-parse", f"HEAD:tickets/{STEM}/ticket.md").strip()
    assert [e.body for e in ctx.driver.journal.read() if e.type == EventType.CAP_CONSUMED] == [
        {"cap": "hardening", "ticket_sha": sha}]


def test_premise_without_an_entry_unit_gap_keeps_the_ordinary_park(repo):
    premise = {"code": "premise", "message": "criterion 2 contradicts merged behavior", "paved_road": "fix it"}
    outcome, ctx, _ = run(repo, [implement_reply("premise_failed", [premise]), diagnosis_reply()])
    assert outcome == "premise_failed"
    assert terminal_body(ctx).get("dispatch") != "spec_gap_hold"
    assert not list((repo / "tickets").glob("plan-gap-*"))


def test_a_seed_may_depend_on_a_sibling_seed_of_its_own_batch(repo):
    alpha = seed_text("alpha-seed")
    beta = seed_text("beta-seed").replace("## Depends on\nnone", "## Depends on\n- alpha-seed")
    assert "- alpha-seed" in beta
    outcome, _, llm = run(repo, [write_seeds({"alpha-seed": alpha, "beta-seed": beta}), requisition("approve"),
                                 requisition("approve"), verdict()])
    assert outcome == "merged"
    assert (repo / "tickets/beta-seed/ticket.md").read_text() == beta
    assert [r.surface for r in llm.requests].count("requisition_review") == 2


@pytest.mark.parametrize("crash_signal", ["ticket_intake", "hardening_round"])
def test_reaped_filer_replays_its_round_commit(repo, monkeypatch, crash_signal):
    from chupa.effects import Effects
    from chupa.runner import file_hardening
    add_registry_row(repo)
    ctx, _ = context(repo, [])
    plan = (repo / "CHUPA_PLAN.md").read_text()
    original = ctx.driver.journal.append
    def crash(type, body, **kwargs):
        if body.get("signal") == crash_signal:
            raise RuntimeError("filer died after committing")
        return original(type, body, **kwargs)
    monkeypatch.setattr(ctx.driver.journal, "append", crash)
    with pytest.raises(RuntimeError, match="filer died"):
        asyncio.run(file_hardening(ctx, ticket(repo), {"19.P3.gamma-seed": ["original fact"]}, 1, plan=plan))
    monkeypatch.setattr(ctx.driver.journal, "append", original)
    original(EventType.STATE_TRANSITION, {"to": "abandoned"}, ticket=STEM)
    ctx.driver.effects = Effects(ctx.driver.journal)
    # Recovery may detect different facts; replay must retain the completed filing's data.
    asyncio.run(file_hardening(ctx, ticket(repo), {"19.P3.gamma-seed": ["different fact"]}, 1, plan=plan + "changed"))
    subjects = git(repo, "log", "--format=%s").splitlines()
    assert subjects.count(f"chupa({STEM}): hardening round 1") == 1
    events = ctx.driver.journal.read()
    [record] = [e for e in events if e.body.get("signal") == "hardening_round"]
    assert record.body["gaps"] == [{"unit": "19.P3.gamma-seed", "message": "original fact"}]
    assert len([e for e in events if e.body.get("signal") == "ticket_intake"
                and e.ticket == "plan-gap-1"]) == 1
    assert len([e for e in events if e.type == EventType.EFFECT_COMPLETION
                and e.key == "ticket-plane/hardening/1"]) == 1


def test_round_ticket_covers_all_gaps_with_the_filers_priority_and_deep_capability(repo):
    from dataclasses import replace
    from chupa.runner import hold_on_hardening
    from chupa.specs import unit_sha
    add_registry_row(repo)
    plan_path = repo / "CHUPA_PLAN.md"
    plan = plan_path.read_text() + (
        "\n## 11. Spine\n\n### 11.4 Hardening\n\nRules.\n\n"
        "### 19.P4 Phase 4\n\n```yaml\n# BEGIN_REGISTRY_P4\nphase: 4\n"
        "admissions: [[delta-seed]]\nseeds:\n"
        "  delta-seed: {fence: [chupa/thing.py], deep: true, cite: ['11.4', '19.L']}\n"
        "# END_REGISTRY_P4\n```\n\n### 19.P4.delta-seed Delta\n\n"
        "- **Owner:** o\n- **Records:** r\n- **Observable:** b\n- **Tests:** t\n")
    plan_path.write_text(plan)
    git(repo, "add", "CHUPA_PLAN.md")
    git(repo, "commit", "-m", "second phase and complete deep unit")
    ctx, _ = context(repo, [])
    filer = ticket(repo)
    filer = replace(filer, frontmatter=filer.frontmatter.model_copy(update={"priority": "P0"}))
    gaps = {"19.P3.gamma-seed": ["missing fact", "another fact"], "19.P4.delta-seed": ["needed carrier"]}
    asyncio.run(hold_on_hardening(ctx, filer, gaps, attempt=0))
    text = (repo / "tickets/plan-gap-1/ticket.md").read_text()
    hardener = validate_ticket("plan-gap-1", text, repo)
    assert hardener.frontmatter.priority == "P0"
    assert (hardener.frontmatter.agent_tier, hardener.frontmatter.agent_effort) == ("high", "high")
    assert set(hardener.plan_contract) == {"19.L", "19.P3", "19.P4", "19.P4.delta-seed", "11.4"}
    assert set(hardener.scope_fence) == {"CHUPA_PLAN.md#19.P3.gamma-seed", "CHUPA_PLAN.md#19.P4.delta-seed"}
    assert hardener.verification == (("uv", "run", "pytest", "tests/test_plan_lint.py"),)
    for facts in gaps.values():
        for fact in facts:
            assert f"> {fact}" in hardener.sections["Acceptance criteria"]
    [record] = [e for e in ctx.driver.journal.read() if e.body.get("signal") == "hardening_round"]
    assert record.body["units"] == terminal_body(ctx)["plan_units"] == {
        "19.P3.gamma-seed": "absent", "19.P4.delta-seed": unit_sha(plan, "19.P4.delta-seed")}
