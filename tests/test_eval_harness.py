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
        package: test-cli
        models_by_tier: {low: c-low, medium: c-med, high: c-high, max: c-max}
        limits: {concurrency: 1}
      - name: codex
        kind: cli
        package: test-cli
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


def graph_reply():
    problems = json.loads(harness.GRAPH_PROBLEMS.read_text())
    return {"problems": problems, "tickets": [
        {"stem": f"graph-{i}", "problem_id": p["id"], "depends": [f"graph-{i-1}"] if i else [],
         "goal": p["summary"]} for i, p in enumerate(problems)]}


def corpus_results(planted=60, clean=20, catches=51, false_snags=3):
    # Disposable scripted score cases, never written into the measured corpus.
    return [Scored(f"planted-{i}", fixture(f"planted-{i}", harness.DEFECT_CLASSES[i % 4]).expected,
                   "ok", "snag" if i < catches else "approve") for i in range(planted)] + [
        Scored(f"clean-{i}", fixture(f"clean-{i}", "none").expected,
               "ok", "snag" if i < false_snags else "approve") for i in range(clean)]


def report_fixture(tmp_path, results=None, graph=True):
    from chupa.artifacts import AuthorGraph
    cfg = config(tmp_path)
    results = corpus_results() if results is None else results
    body = {"signal": "review_baseline", "verdict": "NO_GO", "identity": harness.baseline_identity(cfg),
            "exercised": {"surface": "review", "tier": "high", "effort": "high", "spec_version": "1.0"},
            "fixture_authors": [CODEX], "scores": harness.score(results)}
    journal = Journal(cfg.state_dir, lambda: NOW)
    event = journal.append(EventType.SIGNAL, body)
    report = harness.make_report(results, AuthorGraph.model_validate(graph_reply()) if graph else None, 2.0, event)
    return report, cfg, journal


def test_go_grade_fixture_floors_and_author_separation(tmp_path):
    assert (harness.MIN_DEFECTS, harness.MIN_CLEAN) == (15, 3)
    assert (harness.GO_MIN_DEFECTS, harness.GO_MIN_CLEAN) == (50, 15)
    fixtures = harness.load_fixtures()
    assert {f.expected.defect_class for f in fixtures} == {*harness.DEFECT_CLASSES, "none"}
    root = tmp_path / "fixtures"
    root.mkdir()
    selected = [f for f in fixtures if f.expected.defect_class != "none"][:15]
    selected += [f for f in fixtures if f.expected.defect_class == "none"][:3]
    for f in selected:
        d = root / f.name
        d.mkdir()
        for name in ("ticket.md", "diff.patch", "expected.json"):
            (d / name).write_bytes((harness.FIXTURES / f.name / name).read_bytes())
    assert len(harness.load_fixtures(root)) == 18
    missing = root / selected[-1].name / "expected.json"
    data = missing.read_bytes()
    missing.write_text('{"extra":true}')
    with pytest.raises(FixtureError, match="re-author"):
        harness.load_fixtures(root)
    missing.write_bytes(data)
    for f in selected[-1:]:
        d = root / f.name
        for p in d.iterdir():
            p.unlink()
        d.rmdir()
    with pytest.raises(FixtureError, match="15 planted and 2 clean"):
        harness.load_fixtures(root)
    clean_dir = root / selected[-1].name
    clean_dir.mkdir()
    for name in ("ticket.md", "diff.patch", "expected.json"):
        (clean_dir / name).write_bytes((harness.FIXTURES / selected[-1].name / name).read_bytes())
    planted_dir = root / selected[0].name
    for p in planted_dir.iterdir():
        p.unlink()
    planted_dir.rmdir()
    with pytest.raises(FixtureError, match="14 planted and 3 clean"):
        harness.load_fixtures(root)
    with pytest.raises(ValidationError):
        Expected.model_validate({"expected_verdict": "approve", "defect_class": "none", "defect": " ", "author": CODEX})
    # A complete graph does not relax either separate GO floor.
    for planted, clean, complete in ((49, 15, False), (50, 14, False), (50, 15, True)):
        report, _, _ = report_fixture(tmp_path, corpus_results(planted, clean, planted, 0))
        assert report.complete is complete
    cfg = config(tmp_path)
    identity = harness.baseline_identity(cfg)
    with pytest.raises(FixtureError, match="different"):
        harness.refuse_same_author([harness.AuthorIdentity(provider="claude", model="c-max", tier="low")], identity, "high")


def test_go_grade_existing_corpus_is_partial_no_go(tmp_path, monkeypatch):
    from chupa.artifacts import ReviewBaselineReport
    before = {p: p.read_bytes() for p in harness.FIXTURES.glob("*/*") if p.is_file()}
    fixtures = harness.load_fixtures()
    cfg = config(tmp_path)
    class ReadyLLM(FakeLLM):
        async def preflight(self):
            return []
    llm = ReadyLLM([reply(f.expected.expected_verdict) for f in fixtures] + [json.dumps(graph_reply())])
    monkeypatch.setattr(harness, "ProviderLLM", lambda *args, **kwargs: llm)
    out = tmp_path / "report.json"
    body = asyncio.run(harness._run(cfg, {"PATH": "/usr/bin:/bin"}, lambda: NOW, out=out))
    report = ReviewBaselineReport.model_validate_json(out.read_bytes())
    assert (report.scores.planted, report.scores.clean) == (18, 4)
    assert not report.complete and body["verdict"] == "NO_GO"
    assert report.author_graph is not None and all(r.verdict for r in report.results)
    assert before == {p: p.read_bytes() for p in before}
    assert not (tmp_path / "tickets").exists()


@pytest.mark.parametrize("mode", ["run", "author"])
def test_eval_preflight_refuses_before_measured_calls(tmp_path, monkeypatch, mode):
    cfg = config(tmp_path)
    class UnreadyLLM(FakeLLM):
        async def preflight(self):
            return ["provider probe failed; repair login and retry"]
    llm = UnreadyLLM([])
    monkeypatch.setattr(harness, "ProviderLLM", lambda *args, **kwargs: llm)
    monkeypatch.setattr(harness, "_clock", lambda: NOW)
    out = tmp_path / "report.json"
    cases = tmp_path / "cases"
    with pytest.raises(FixtureError, match="repair login"):
        if mode == "run":
            asyncio.run(harness._run(cfg, {"PATH": "/usr/bin:/bin"}, lambda: NOW, out=out))
        else:
            asyncio.run(harness.author_fixtures(cfg, provider="codex", tier="high",
                only=["logic-pagination"], force=False, env={"PATH": "/usr/bin:/bin"}, root=cases))
    assert not llm.requests and not out.exists() and not cases.exists()
    assert not any(e.body.get("signal") in {"review_baseline", "author_invoked"}
                   for e in Journal(cfg.state_dir, lambda: NOW).read())


def test_go_grade_fixture_author_identity_comes_from_call(tmp_path, monkeypatch):
    from tests.test_providers import FakeExec, codex_ok, provider_session
    cfg = config(tmp_path)
    monkeypatch.setattr(harness, "_clock", lambda: NOW)
    authored = {"ticket": "scripted ticket", "diff": "diff --git a/a b/a\n+x = 1\n", "defect": "a:1 wrong"}
    process = FakeExec((0, codex_ok(json.dumps(authored)), ""))
    session = provider_session(cfg, clock=lambda: NOW, sleep=_no_sleep)
    root = tmp_path / "disposable-cases"
    asyncio.run(harness._author_fixtures(cfg, provider="codex", tier="high", only=["logic-pagination"],
        force=False, env={}, root=root, session=session, exec_=process))
    expected = Expected.model_validate_json((root / "logic-pagination/expected.json").read_bytes())
    assert expected.author.model_dump() == CODEX
    assert process.calls[0]["argv"][process.calls[0]["argv"].index("-m") + 1] == "x-high"
    events = session.journal.read()
    assert any(e.body.get("signal") == "author_invoked" for e in events)
    completed = [e.body["result"] for e in events if e.type == EventType.EFFECT_COMPLETION
                 and (e.key or "").startswith("llm/")]
    assert [(r["provider"], r["model"]) for r in completed] == [("codex", "x-high")]
    captured = cfg.state_dir / "spools/fixture-logic-pagination/1/author/call-01"
    assert captured.joinpath("output.txt").read_text() == json.dumps(authored)
    assert "fixture" in captured.joinpath("prompt.md").read_text()
    snapshots = {p: p.read_bytes() for p in cfg.state_dir.rglob("*") if p.is_file()}
    with pytest.raises(FixtureError, match="different"):
        # c-max is the actual selected author model at max and the review model.
        asyncio.run(harness._author_fixtures(cfg, provider="claude", tier="max", only=["logic-pagination"],
            force=True, env={}, root=root, session=session, exec_=process))
    assert snapshots == {p: p.read_bytes() for p in snapshots}
    assert len(process.calls) == 1


def test_go_grade_scoring_and_partial_report(tmp_path):
    from chupa.artifacts import ReviewBaselineReport
    results = corpus_results()
    report, _, _ = report_fixture(tmp_path, results)
    assert report.complete and report.scores.catch_rate == 0.85 and report.scores.clean_false_snag == 0.15
    assert len(report.scores.missed) == 9 and len(report.scores.false_snagged) == 3
    results[0] = Scored(results[0].name, results[0].expected, "budget_exceeded", None)
    partial, _, _ = report_fixture(tmp_path, results)
    assert not partial.complete and partial.verdict_signal.body.verdict == "NO_GO"
    assert partial.scores.unscored[0].outcome == "budget_exceeded"
    raw = partial.model_dump()
    raw["scores"]["planted"] += 1
    with pytest.raises(ValidationError, match="scores"):
        ReviewBaselineReport.model_validate(raw)


def test_go_grade_shared_cap_includes_retries_and_author_graph(tmp_path):
    from chupa.artifacts import ReviewBaselineReport
    from chupa.llm import LLMResult
    cfg = config(tmp_path)
    def paid(text, usd):
        return LLMResult(text, None, None, "claude", "c-max", usd)
    fixtures = [fixture("retry", "logic"), fixture("next", "none")]
    llm = FakeLLM([paid("bad json", 1.0), paid(reply("snag"), 1.0),
                   paid(reply("approve"), 1.0), paid("bad graph", 1.0), paid(json.dumps(graph_reply()), 1.0)])
    driver = Driver.from_config(cfg, llm=llm, env={}, clock=lambda: NOW, sleep=_no_sleep)
    out = tmp_path / "report.json"
    asyncio.run(harness.run_baseline(config=cfg, driver=driver, journal=driver.journal,
        fixtures=fixtures, out=out, workspace=tmp_path))
    assert [r.budget_usd for r in llm.requests] == [5.0, 4.0, 3.0, 2.0, 1.0]
    assert [r.surface for r in llm.requests] == ["review"] * 3 + ["author"] * 2
    assert ReviewBaselineReport.model_validate_json(out.read_bytes()).spent_usd == 5.0
    llm = FakeLLM([paid("invalid", 5.0)])
    driver = Driver.from_config(cfg, llm=llm, env={}, clock=lambda: NOW, sleep=_no_sleep)
    asyncio.run(harness.run_baseline(config=cfg, driver=driver, journal=driver.journal,
        fixtures=fixtures, out=out, workspace=tmp_path))
    assert len(llm.requests) == 1 and llm.requests[0].budget_usd == 5.0
    partial = ReviewBaselineReport.model_validate_json(out.read_bytes())
    assert partial.author_graph is None and not partial.complete
    assert [r.outcome for r in partial.results] == ["budget_exceeded"] * 2


def test_go_grade_author_graph_uses_local_prompt(tmp_path):
    from chupa.artifacts import AuthorGraph
    cfg = config(tmp_path)
    graph = graph_reply()
    llm = FakeLLM([json.dumps(graph)])
    driver = Driver.from_config(cfg, llm=llm, env={}, clock=lambda: NOW, sleep=_no_sleep)
    artifact, cost = asyncio.run(harness.run_author_graph(driver, attempt=1, workspace=tmp_path,
        budget_usd=5.0, tier="high", effort="high"))
    assert artifact.model_dump() == graph and cost == 0.0
    [request] = llm.requests
    assert "harness-local graph exercise" in request.rendered and request.surface == "author"
    assert request.worktree is None and "specs/author.md" not in request.rendered
    assert not (tmp_path / "tickets").exists()
    for variant in ("cycle", "missing", "unknown-problem", "invalid-stem", "duplicate"):
        raw = json.loads(json.dumps(graph))
        if variant == "cycle":
            raw["tickets"][0]["depends"] = [raw["tickets"][-1]["stem"]]
        elif variant == "missing":
            raw["tickets"][0]["depends"] = ["absent-ticket"]
        elif variant == "unknown-problem":
            raw["tickets"][0]["problem_id"] = "absent"
        elif variant == "invalid-stem":
            raw["tickets"][0]["stem"] = "INVALID"
        else:
            raw["problems"].append(raw["problems"][0])
        with pytest.raises(ValidationError):
            AuthorGraph.model_validate(raw)
