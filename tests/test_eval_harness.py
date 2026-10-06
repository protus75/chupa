"""Review-baseline harness (CHUPA_PLAN.md 19.P1), offline: scripted fake LLM, temp journal."""

import asyncio
import json
import textwrap
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from chupa.artifacts import ReviewVerdict
from chupa.config import load_config
from chupa.driver import Driver
from chupa.journal import EventType, Journal
from chupa.llm import FakeLLM
from chupa.specs import lint_spec
from eval import harness
from eval.harness import Expected, Fixture, FixtureError, Scored

ROOT = Path(__file__).resolve().parent.parent

CONFIG = textwrap.dedent(
    """\
    schema_version: 1
    state_dir: state
    providers:
      - name: claude
        kind: cli
        models_by_tier: {low: c-low, medium: c-med, high: c-high, max: c-max}
        limits: {concurrency: 1}
      - name: codex
        kind: cli
        models_by_tier: {low: x-low, medium: x-med, high: x-high, max: x-max}
        limits: {concurrency: 1, est_cost_per_call_usd: 1.0}
    routing:
    """
) + "".join(
    f"  - {{tier: {t}, surface: implement, candidates: [{{provider: codex}}]}}\n"
    f"  - {{tier: {t}, surface: author, candidates: [{{provider: claude}}]}}\n"
    f"  - {{tier: {t}, surface: review, candidates: [{{provider: claude, model: c-max}}]}}\n"
    for t in ("low", "medium", "high", "max")
) + "review: {}\nmerge: {}\nengine_plane_safety_inventory: []\n"

CODEX = {"provider": "codex", "model": "x-high", "tier": "high"}
NOW = datetime(2026, 10, 5, tzinfo=UTC)


def config(tmp_path: Path):
    (tmp_path / "config.yaml").write_text(CONFIG)
    return load_config(None, cwd=tmp_path)


def fixture(name: str, cls: str, author=CODEX) -> Fixture:
    clean = cls == "none"
    exp = Expected.model_validate({"expected_verdict": "approve" if clean else "snag", "defect_class": cls,
                                   "defect": "" if clean else f"{name} is wrong", "author": author})
    return Fixture(name, f"ticket {name}", f"diff --git a/{name}.py b/{name}.py\n+x = 1\n", exp)


def reply(verdict: str, code: str = "logic") -> str:
    findings = [] if verdict == "approve" else [
        {"code": code, "path": "a.py", "line": 1, "message": "m", "paved_road": "p"}]
    return json.dumps({"verdict": verdict, "summary": "s", "findings": findings})


async def _no_sleep(_: float) -> None:
    await asyncio.Event().wait()


def run(tmp_path: Path, fixtures: list[Fixture], script: list):
    cfg = config(tmp_path)
    llm = FakeLLM(script)
    driver = Driver.from_config(cfg, llm=llm, env={}, clock=lambda: NOW, sleep=_no_sleep)
    journal = Journal(cfg.state_dir, lambda: NOW)
    body = asyncio.run(harness.run_baseline(config=cfg, driver=driver, journal=journal, fixtures=fixtures,
                                            specs_dir=ROOT / "specs", workspace=tmp_path))
    return body, journal, llm


def test_review_spec_lints_clean():
    assert lint_spec((ROOT / "specs" / "review.md").read_text()) == []


def test_committed_fixture_set_meets_the_spike_floor_and_differs_from_review():
    fixtures = harness.load_fixtures()
    planted = [f for f in fixtures if f.expected.defect_class != "none"]
    assert 15 <= len(planted) <= 20 and len(fixtures) - len(planted) >= 3
    assert {f.expected.defect_class for f in planted} == set(harness.DEFECT_CLASSES)
    cfg = load_config(None, cwd=ROOT)
    harness.refuse_same_author({f.expected.author for f in fixtures}, harness.baseline_identity(cfg), "high")


def test_scored_run_journals_one_no_go_signal_with_the_baselined_identity(tmp_path):
    fixtures = [fixture("caught", "logic"), fixture("missed", "scope_escape"), fixture("rma", "hidden_info_leak"),
                fixture("ok", "none"), fixture("noisy", "none")]
    body, journal, llm = run(tmp_path, fixtures, [reply("snag"), reply("approve"), reply("rma", "ticket"),
                                                  reply("approve"), reply("snag")])
    signals = [e for e in journal.read() if e.type == EventType.SIGNAL]
    assert [e.body for e in signals] == [body]
    assert body["signal"] == "review_baseline" and body["verdict"] == "NO_GO"
    review, author = body["identity"]["review"], body["identity"]["author"]
    assert review["spec_major"] == 1 and author["spec_major"] == 1
    assert review["rows"] == {t: {"provider": "claude", "model": "c-max"} for t in ("low", "medium", "high", "max")}
    assert author["rows"]["low"] == {"provider": "claude", "model": "c-low"}
    assert body["fixture_authors"] == [CODEX]
    s = body["scores"]
    assert (s["catch_rate"], s["known_bad_false_approve"], s["clean_false_snag"]) == (0.6667, 0.3333, 0.5)
    assert s["missed"] == ["missed"] and s["false_snagged"] == ["noisy"] and s["unscored"] == []
    assert s["by_class"]["scope_escape"] == {"planted": 1, "caught": 0}
    # Every call is the review surface at the spec's tier, with the fixture as data.
    assert {(r.surface, r.tier) for r in llm.requests} == {("review", "high")}
    assert "ticket caught" in llm.requests[0].rendered


def test_schema_invalid_reply_is_reprompted_with_the_finding(tmp_path):
    body, _, llm = run(tmp_path, [fixture("a", "logic")], ['{"verdict": "approve", "summary": "s",'
                                                           ' "findings": [{"code": "logic", "message": "m",'
                                                           ' "paved_road": "p"}]}', reply("snag")])
    assert body["scores"]["catch_rate"] == 1.0
    assert "approve carries an empty findings list" in llm.requests[1].rendered


def test_infra_failure_is_unscored_never_caught(tmp_path):
    body, _, _ = run(tmp_path, [fixture("a", "logic")], [RuntimeError("cli died")])
    s = body["scores"]
    assert s["catch_rate"] == 0.0 and s["known_bad_false_approve"] == 0.0
    assert s["unscored"] == [{"fixture": "a", "outcome": "infra_error"}]


def test_fixtures_authored_by_the_review_identity_are_refused(tmp_path):
    same = {"provider": "claude", "model": "c-max", "tier": "low"}
    with pytest.raises(FixtureError, match="different"):
        run(tmp_path, [fixture("a", "logic", author=same)], [])


def test_score_counts_rma_as_a_catch_and_ignores_unscored_in_rates():
    exp = fixture("x", "logic").expected
    s = harness.score([Scored("a", exp, "ok", "rma"), Scored("b", exp, "timeout", None)])
    assert s["catch_rate"] == 0.5 and s["known_bad_false_approve"] == 0.0 and s["clean_false_snag"] is None


@pytest.mark.parametrize("raw", [
    {"verdict": "approve", "summary": "s", "findings": [{"code": "logic", "message": "m", "paved_road": "p"}]},
    {"verdict": "snag", "summary": "s", "findings": []},
    {"verdict": "snag", "summary": "s", "findings": [{"code": "ticket", "message": "m", "paved_road": "p"}]},
    {"verdict": "rma", "summary": "s", "findings": [{"code": "logic", "message": "m", "paved_road": "p"}]},
    {"verdict": "lgtm", "summary": "s", "findings": []},
])
def test_review_verdict_refuses_findings_that_do_not_match_the_verdict(raw):
    with pytest.raises(ValidationError):
        ReviewVerdict.model_validate_json(json.dumps(raw))


@pytest.mark.parametrize("raw", [
    {"expected_verdict": "approve", "defect_class": "logic", "defect": "x", "author": CODEX},
    {"expected_verdict": "snag", "defect_class": "none", "defect": "", "author": CODEX},
    {"expected_verdict": "snag", "defect_class": "logic", "defect": "", "author": CODEX},
    {"expected_verdict": "snag", "defect_class": "style", "defect": "x", "author": CODEX},
])
def test_expected_refuses_an_inconsistent_fixture(raw):
    with pytest.raises(ValidationError):
        Expected.model_validate(raw)


def test_authored_fixture_hinting_at_its_defect_is_refused():
    a = harness.Authored(ticket="t", diff="diff --git a/x b/x\n+# off-by-one bug here\n", defect="d")
    assert any("hints" in p for p in harness.check_authored(a, "logic"))
    clean = harness.Authored(ticket="t", diff="diff --git a/x b/x\n+x = 1\n", defect="")
    assert harness.check_authored(clean, "none") == []
