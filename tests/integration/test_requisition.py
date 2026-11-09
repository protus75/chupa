import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from chupa.artifacts import Finding
from chupa.config import load_config
from chupa.driver import Driver
from chupa.gates import lint_gate
from chupa.llm import FakeLLM
from chupa.requisition import RequisitionGate, RequisitionReply, RequisitionVerdict, base_render_chars, review_target, review_ticket
from chupa.specs import RENDER_BOUND_CHARS, REQ_RENDER_HEADROOM, lint_spec, load_spec, render
from chupa.stages import StageContext, implement_inputs, implement_stage
from chupa.tickets import TicketInvalid

SPECS = Path(__file__).resolve().parents[2] / "chupa" / "specs"
TICKET = """---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
none

## Context
- context.txt

## Goal / Why
Create one thing.

## Scope in / Scope out
In: thing. Out: the rest.

## Scope fence
- thing.py

## Acceptance criteria
1. `thing.py` exists, checked by `test -f thing.py`.

## Verification
```
test -f thing.py
```

## Definition of rejected
Needs an outside file.

## Time budget
- expected: 10m
- stuck: 20m
"""


def setup(tmp_path: Path, responses: list) -> tuple[Path, Driver, FakeLLM]:
    (tmp_path / "context.txt").write_text("context")
    (tmp_path / "config.yaml").write_text("""schema_version: 1
state_dir: .state
providers:
  - name: fake
    kind: cli
    package: test-cli
    auth: FAKE_KEY
    models_by_tier: {low: m, medium: m, high: m, max: m}
    limits: {concurrency: 1, est_cost_per_call_usd: 0.5}
routing:
  - {tier: high, surface: review, candidates: [{provider: fake}]}
review: {}
merge: {}
engine_plane_safety_inventory: [context.txt]
""")
    llm = FakeLLM(responses)

    async def never(seconds: float) -> None:
        await asyncio.Event().wait()

    driver = Driver.from_config(load_config(None, cwd=tmp_path), llm=llm, env={"FAKE_KEY": "secret"}, clock=lambda: datetime(2026, 10, 6, tzinfo=UTC), sleep=never)
    return tmp_path, driver, llm


def run(driver: Driver, repo: Path, text: str = TICKET, stem: str = "one-thing", coverage_map: Path | None = None) -> RequisitionVerdict:
    return asyncio.run(
        review_ticket(driver, repo=repo, stem=stem, text=text, specs_dir=SPECS, coverage_map=coverage_map, tier="high", stem_slot="s", run_seq=0, attempt=1, call_seq=1, expected_budget="surface")
    )


def reply(verdict: str, findings: list | None = None) -> str:
    return json.dumps({"verdict": verdict, "summary": "reviewed", "findings": findings or []})


FINDING = {"code": "scope", "message": "missing file", "paved_road": "add it to the fence"}


def test_spec_loads_and_names_finding_keys():
    source = (SPECS / "requisition_review.md").read_text()
    assert lint_spec(source) == []
    spec = load_spec(source)
    assert spec.meta.llm_surface == "requisition_review"
    assert spec.inputs == ("ticket", "context", "render", "coverage_dependents", "prior_review", "retry_findings")
    assert all(key in source for key in ("`code`", "`message`", "`paved_road`"))
    assert "in the fence or cleared in the summary" in source
    assert "the fence must hold a `tests/unit` file" in source
    assert "An unaccounted file is a `snag` finding naming it" in source
    # A stale-path rule must exempt paths created by the ticket or written only as outputs.
    for phrase in (
        "does not exist at the review commit",
        "does not say the ticket creates",
        "a path the ticket creates is not a hit",
        "a path that is only an output of a command is not a hit",
    ):
        assert phrase in source
    assert "Two statements anywhere in the ticket cannot both hold, for example a declared signature and a call to it, or a named fixture and the result a criterion expects from it." in source
    assert "Report every finding in this one reply; never stop at the first." in source
    # The changed-text-only rule must not apply after a schema-invalid review.
    assert "A prior review reporting an invalid requisition review reply clears nothing" in source
    assert "The first character of your reply is `{` and the last is `}`" in source
    assert "re-emit the same verdict as bare JSON" in source


@pytest.mark.parametrize("kind", [None, "authoring_error"])
def test_a_unit_requires_spec_gap_kind(kind):
    with pytest.raises(ValueError, match="unit is non-null only for kind spec_gap"):
        Finding(**{**FINDING, "kind": kind, "unit": "19.P3.governing"})


def test_approve_and_effect_key(tmp_path):
    repo, driver, llm = setup(tmp_path, [reply("approve")])
    verdict = run(driver, repo)
    assert verdict.verdict == "approve" and verdict.findings == []
    assert verdict.mechanical is None
    assert len(llm.requests) == 1
    assert llm.requests[0].surface == "requisition_review"
    assert any(e.key == "llm/s/0/requisition_review/1/1" for e in driver.journal.read())


def test_snag_and_invalid_reply(tmp_path):
    repo, driver, llm = setup(tmp_path, [reply("snag", [FINDING])] + [reply("wrong")] * 10)
    assert run(driver, repo).findings[0].paved_road == "add it to the fence"
    # A new call identity avoids replaying the first completion.
    invalid = asyncio.run(
        review_ticket(driver, repo=repo, stem="one-thing", text=TICKET, specs_dir=SPECS, coverage_map=None, tier="high", stem_slot="s", run_seq=0, attempt=1, call_seq=2, expected_budget="surface")
    )
    assert invalid.verdict == "snag" and invalid.mechanical == "invalid reply"
    assert invalid.calls == 1 + driver.retry_cap
    assert len(llm.requests) == 2 + driver.retry_cap
    with pytest.raises(Exception):
        RequisitionReply.model_validate_json(reply("approve", [FINDING]))


def test_invalid_reply_is_reprompted_then_accepted(tmp_path):
    valid = reply("snag", [FINDING])
    repo, driver, llm = setup(tmp_path, [f"Here is the review:\n```json\n{valid}\n```", valid])
    verdict = run(driver, repo)
    assert verdict.verdict == "snag" and verdict.mechanical is None
    assert verdict.findings[0].message == "missing file"
    assert verdict.calls == 2 and len(llm.requests) == 2
    assert "Invalid JSON" in llm.requests[1].rendered
    assert "only the JSON object" in llm.requests[1].rendered
    keys = [e.key for e in driver.journal.read() if e.type == "effect_completion" and e.key and "/requisition_review/" in e.key]
    assert keys == ["llm/s/0/requisition_review/1/1", "llm/s/0/requisition_review/1/2"]


def test_invalid_ticket_and_reserved_stem_spend_no_call(tmp_path):
    repo, driver, llm = setup(tmp_path, [])
    with pytest.raises(TicketInvalid):
        run(driver, repo, TICKET.replace("priority: P2", "priority: PX"))
    with pytest.raises(TicketInvalid):
        run(driver, repo, stem="retro")
    assert llm.requests == []


def test_over_headroom_spends_no_call(tmp_path):
    repo, driver, llm = setup(tmp_path, [])
    (repo / "context.txt").write_text("x" * (int(REQ_RENDER_HEADROOM * RENDER_BOUND_CHARS) + 1_000))
    verdict = run(driver, repo)
    assert verdict.verdict == "snag"
    assert verdict.mechanical == "render over headroom"
    assert verdict.findings[0].code == "render_feasibility"
    assert verdict.calls == 0 and llm.requests == []


def test_render_over_max_bound_is_still_headroom_snag(tmp_path):
    repo, driver, llm = setup(tmp_path, [])
    (repo / "context.txt").write_text("x" * (RENDER_BOUND_CHARS + 1_000))
    verdict = run(driver, repo)
    assert verdict.verdict == "snag"
    assert verdict.findings[0].code == "render_feasibility"
    assert verdict.render_chars > RENDER_BOUND_CHARS
    assert llm.requests == []


def test_provider_error_is_mechanical_snag(tmp_path):
    repo, driver, llm = setup(tmp_path, [RuntimeError("provider unavailable")])
    verdict = run(driver, repo)
    assert verdict.verdict == "snag" and verdict.mechanical == "provider error"
    assert "provider unavailable" in verdict.findings[0].message
    assert len(llm.requests) == 1


def test_implement_reads_context_from_its_worktree(tmp_path):
    repo, driver, _ = setup(tmp_path, [])
    path = repo / "tickets" / "one-thing" / "ticket.md"
    path.parent.mkdir(parents=True)
    path.write_text(TICKET)
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    (worktree / "context.txt").write_text("worktree context")
    ticket = review_target(repo, "one-thing", TICKET)
    ctx = StageContext(repo=repo, config=load_config(None, cwd=repo), env={}, exec_=None, git=None, fs=None, driver=driver, specs_dir=SPECS)
    stage, _ = implement_stage(ctx, ticket, worktree)
    prompt = stage.render(ticket, [])
    assert "worktree context" in prompt
    assert "### context.txt\ncontext\n" not in prompt


def test_review_render_over_bound_is_mechanical_snag(tmp_path, monkeypatch):
    repo, driver, llm = setup(tmp_path, [])
    import chupa.requisition as requisition
    import chupa.specs as specs

    # The base Implement render fits the bound; the review render, which embeds it, does not.
    base = base_render_chars(repo, review_target(repo, "one-thing", TICKET), TICKET, SPECS)
    monkeypatch.setattr(specs, "RENDER_BOUND_CHARS", base + 1)
    monkeypatch.setattr(requisition, "RENDER_BOUND_CHARS", 2 * base)
    verdict = run(driver, repo)
    assert verdict.verdict == "snag" and verdict.mechanical == "review render over bound"
    assert verdict.findings[0].code == "requisition_review"
    assert llm.requests == []


def test_base_render_matches_implement_and_gate(tmp_path):
    repo, driver, _ = setup(tmp_path, [reply("approve")])
    ticket = review_target(repo, "one-thing", TICKET)
    spec = load_spec((SPECS / "implement.md").read_text())
    production = render(spec, {**implement_inputs(repo, TICKET, ticket, ()), "retry_findings": "none"})
    assert base_render_chars(repo, ticket, TICKET, SPECS) == len(production)
    approved = run(driver, repo)
    snag = approved.model_copy(update={"verdict": "snag", "findings": [Finding(**FINDING)]})
    gate = RequisitionGate()
    assert lint_gate(gate, [approved, snag], repo) == []
    assert gate.check(snag, repo).findings == snag.findings


def test_coverage_dependents_in_prompt(tmp_path):
    repo, driver, llm = setup(tmp_path, [reply("approve")])
    map_path = repo / "map.json"
    map_path.write_text(
        json.dumps(
            {
                "files": {
                    "thing.py": ["tests/outside.py", "tests/in_fence/test_inside.py"],
                    "other.py": ["tests/unrelated.py"],
                }
            }
        )
    )
    ticket = TICKET.replace("- thing.py\n\n## Acceptance", "- thing.py\n- tests/in_fence\n\n## Acceptance")
    assert run(driver, repo, text=ticket, coverage_map=map_path).verdict == "approve"
    prompt = llm.requests[0].rendered
    block = prompt.split("<<chupa-data:begin coverage_dependents>>")[1].split("<<chupa-data:end coverage_dependents>>")[0]
    assert block.strip() == "tests/outside.py: runs thing.py"


@pytest.mark.parametrize("contents", [None, "not json", '{"files": []}'])
def test_invalid_coverage_map_snags_before_model(tmp_path, contents):
    repo, driver, llm = setup(tmp_path, [])
    map_path = repo / "map.json"
    if contents is not None:
        map_path.write_text(contents)
    verdict = run(driver, repo, coverage_map=map_path)
    assert verdict.verdict == "snag"
    assert verdict.findings[0].code == "coverage_map"
    assert verdict.findings[0].paved_road == "run ./dev.py covmap"
    assert verdict.calls == 0 and llm.requests == []


def test_no_coverage_map_renders_notice(tmp_path):
    repo, driver, llm = setup(tmp_path, [reply("approve")])
    assert run(driver, repo).verdict == "approve"
    block = llm.requests[0].rendered.split("<<chupa-data:begin coverage_dependents>>")[1].split("<<chupa-data:end coverage_dependents>>")[0]
    assert block.strip() == "no coverage map configured"


def test_context_section_renders_only_the_section(tmp_path):
    repo, _, _ = setup(tmp_path, [])
    (repo / "m.py").write_text("class B:\n    @mark\n    def run(self):\n        return 7\n\n    def other(self):\n        return 8\n")
    (repo / "d.md").write_text("# One\none\n## Two\ntwo\n### Two-a\nchild\n## Three\nthree\n")
    text = TICKET.replace("- context.txt", "- m.py::B.run\n- d.md#Two")
    ticket = review_target(repo, "one-thing", text)
    context = implement_inputs(repo, text, ticket, ())["context"]
    assert context == "### m.py::B.run\n    @mark\n    def run(self):\n        return 7\n\n\n### d.md#Two\n## Two\ntwo\n### Two-a\nchild\n"  # excludes siblings and retains decorator and subheading
