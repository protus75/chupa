"""Deterministic capability and Reject routing through the production drain."""

import json

import pytest

from chupa import runner
from chupa.__main__ import main
from chupa.caps import consume, draws, next_rung, remaining
from chupa.config import load_config
from chupa.journal import EventType, Journal
from chupa.llm import FakeLLM
from tests.test_drain_reentry import NoChild
from tests.test_stages import ENV, SNAG, STEM, agent, git, verdict
from tests.test_terminal import author, clock, repo  # noqa: F401 -- fixture


ROUTING = """schema_version: 1
state_dir: .chupa/state
providers:
  - name: fake
    kind: cli
    auth: FAKE_KEY
    models_by_tier: {low: A, medium: A, high: B, max: B}
    limits: {concurrency: 1, est_cost_per_call_usd: 0.5}
routing:
  - {tier: low, surface: implement, candidates: [{provider: fake}]}
  - {tier: medium, surface: implement, candidates: [{provider: fake}]}
  - {tier: high, surface: implement, candidates: [{provider: fake}]}
  - {tier: max, surface: implement, candidates: [{provider: fake}]}
  - {tier: low, surface: review, candidates: [{provider: fake}]}
  - {tier: medium, surface: review, candidates: [{provider: fake}]}
  - {tier: high, surface: review, candidates: [{provider: fake}]}
  - {tier: max, surface: review, candidates: [{provider: fake}]}
review: {}
merge: {}
engine_plane_safety_inventory: [config.yaml]
"""


def diagnosis(verdict_: str) -> str:
    return json.dumps({"verdict": verdict_, "lessons": ["Apply the review finding."]})


def events(repo):
    return [e for e in Journal(repo / ".chupa" / "state", clock).read() if e.ticket == STEM]


def terminals(repo):
    return [e.body for e in events(repo) if e.type == EventType.STATE_TRANSITION
            and e.body.get("to") == "gate_failed"]


def run_drain(repo, script):
    llm = FakeLLM(script)
    code = main(["drain"], cwd=repo, env=ENV, clock=clock,
                pipeline=lambda c: runner.bind(c, llm), reexec=NoChild())
    assert code == 0
    return llm


def test_next_rung_skips_same_model_and_missing_routes(repo):
    (repo / "config.yaml").write_text(ROUTING)
    config = load_config(None, cwd=repo)
    assert next_rung(config, "low", "medium") == {"tier": "high", "effort": "medium"}
    assert next_rung(config, "high", "medium") == {"tier": "high", "effort": "high"}
    assert next_rung(config, "high", "max") is None
    (repo / "config.yaml").write_text(ROUTING.replace(
        "  - {tier: medium, surface: implement, candidates: [{provider: fake}]}\n", "").replace(
        "  - {tier: medium, surface: review, candidates: [{provider: fake}]}\n", ""))
    assert next_rung(load_config(None, cwd=repo), "low", "medium") == {"tier": "high", "effort": "medium"}


def test_escalation_rung_reaches_next_implement_without_editing_ticket(repo):
    (repo / "config.yaml").write_text(ROUTING)
    author(repo)
    path = repo / "tickets" / STEM / "ticket.md"
    before = path.read_bytes()
    llm = run_drain(repo, [agent({"chupa/thing.py": "ok\n"}), verdict("snag", [SNAG]), diagnosis("escalate"),
                           agent({"chupa/thing.py": "ok\n"}), verdict()])
    first, = terminals(repo)
    assert first == {"to": "gate_failed", "stage": "review", "reason": "logic", "dispatch": "escalate",
                     "rung": {"tier": "high", "effort": "medium"}}
    retry, = [e.body for e in events(repo) if e.type == EventType.CAP_CONSUMED and e.body["cap"] == "retry"]
    assert retry["rung"] == first["rung"]
    implements = [r for r in llm.requests if r.surface == "implement"]
    assert [(r.tier, r.effort) for r in implements] == [("medium", "medium"), ("high", "medium")]
    reviews = [r for r in llm.requests if r.surface == "review"]
    assert [(r.tier, r.effort) for r in reviews] == [("medium", "medium"), ("high", "medium")]
    assert path.read_bytes() == before


@pytest.mark.parametrize("verdict_", ["reject", "abandon-human", "split"])
def test_reject_verdicts_auto_keep_once_and_draw_down(repo, verdict_):
    author(repo)
    run_drain(repo, [agent({"chupa/thing.py": "ok\n"}), verdict("snag", [SNAG]), diagnosis(verdict_),
                     agent({"chupa/thing.py": "ok\n"}), verdict()])
    assert terminals(repo)[0] == {"to": "gate_failed", "stage": "review", "reason": "logic",
                                   "dispatch": "reject_queue", "routed": "reject_queue"}
    keeps = [e for e in events(repo) if e.type == EventType.SIGNAL
             and e.body.get("signal") == "reject_verdict"]
    assert [e.body for e in keeps] == [{"signal": "reject_verdict", "verdict": "keep", "actor": "machine"}]
    assert draws(events(repo), STEM, "retry") == 1
    assert remaining(load_config(None, cwd=repo).caps, events(repo), STEM, "retry") == 5


def test_exhausted_ladder_routes_and_auto_keeps(repo):
    (repo / "config.yaml").write_text(ROUTING)
    author(repo)
    path = repo / "tickets" / STEM / "ticket.md"
    path.write_text(path.read_text().replace("kind: feature", "kind: feature\nagent_tier: high\nagent_effort: max"))
    run_drain(repo, [agent({"chupa/thing.py": "ok\n"}), verdict("snag", [SNAG]), diagnosis("escalate"),
                     agent({"chupa/thing.py": "ok\n"}), verdict()])
    assert terminals(repo)[0]["dispatch"] == "reject_queue"
    assert terminals(repo)[0]["routed"] == "reject_queue"
    assert sum(e.body.get("actor") == "machine" for e in events(repo) if e.type == EventType.SIGNAL) == 1
    assert draws(events(repo), STEM, "retry") == 1


def test_same_retry_wall_climbs_on_second_terminal(repo):
    (repo / "config.yaml").write_text(ROUTING)
    author(repo)
    run_drain(repo, [agent({"chupa/thing.py": "ok\n"}), verdict("snag", [SNAG]), diagnosis("retry"),
                     agent({"chupa/thing.py": "ok\n"}), verdict("snag", [SNAG]), diagnosis("retry"),
                     agent({"chupa/thing.py": "ok\n"}), verdict()])
    first, second = terminals(repo)
    assert (first["dispatch"], second["dispatch"], second["rung"]) == (
        "retry", "escalate", {"tier": "high", "effort": "medium"})


def test_three_identical_reasons_climb_even_after_different_verdict(repo):
    (repo / "config.yaml").write_text(ROUTING)
    author(repo)
    llm = run_drain(repo, [agent({"chupa/thing.py": "ok\n"}), verdict("snag", [SNAG]), diagnosis("retry"),
                           agent({"chupa/thing.py": "ok\n"}), verdict("snag", [SNAG]), diagnosis("escalate"),
                           agent({"chupa/thing.py": "ok\n"}), verdict("snag", [SNAG]), diagnosis("retry"),
                           agent({"chupa/thing.py": "ok\n"}), verdict()])
    first, second, third = terminals(repo)
    assert [t["reason"] for t in (first, second, third)] == ["logic"] * 3
    assert third["dispatch"] == "escalate"
    assert third["rung"] == {"tier": "high", "effort": "high"}
    assert [(r.tier, r.effort) for r in llm.requests if r.surface == "implement"][-1] == ("high", "high")


def test_same_retry_wall_at_top_routes_to_queue(repo):
    (repo / "config.yaml").write_text(ROUTING)
    author(repo)
    path = repo / "tickets" / STEM / "ticket.md"
    path.write_text(path.read_text().replace("kind: feature", "kind: feature\nagent_tier: high\nagent_effort: max"))
    run_drain(repo, [agent({"chupa/thing.py": "ok\n"}), verdict("snag", [SNAG]), diagnosis("retry"),
                     agent({"chupa/thing.py": "ok\n"}), verdict("snag", [SNAG]), diagnosis("retry"),
                     agent({"chupa/thing.py": "ok\n"}), verdict()])
    first, second = terminals(repo)
    assert first["dispatch"] == "retry"
    assert second["dispatch"] == "reject_queue" and second["routed"] == "reject_queue"
    assert "rung" not in second


def test_operator_confirm_resets_effective_rung(repo):
    (repo / "config.yaml").write_text(ROUTING)
    author(repo)

    def run_one(script):
        llm = FakeLLM(script)
        assert main(["run", STEM], cwd=repo, env=ENV, clock=clock,
                    pipeline=lambda c: runner.bind(c, llm)) == 1
        return llm

    run_one([agent({"chupa/thing.py": "ok\n"}), verdict("snag", [SNAG]), diagnosis("escalate")])
    rung = terminals(repo)[-1]["rung"]
    sha = git(repo, "rev-parse", f"HEAD:tickets/{STEM}/ticket.md").strip()
    consume(Journal(repo / ".chupa" / "state", clock), STEM, "retry", sha, rung=rung)
    second = run_one([agent({"chupa/thing.py": "ok\n"}), verdict("snag", [SNAG]), diagnosis("reject")])
    assert next(r for r in second.requests if r.surface == "implement").tier == "high"
    assert main(["confirm", STEM], cwd=repo, env=ENV, clock=clock) == 0
    third = run_one([agent({"chupa/thing.py": "ok\n"}), verdict("snag", [SNAG]), diagnosis("reject")])
    assert (next(r for r in third.requests if r.surface == "implement").tier,
            next(r for r in third.requests if r.surface == "implement").effort) == ("medium", "medium")
