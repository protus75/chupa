"""Diagnosis through the production run and drain composition."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from chupa import runner
from chupa.__main__ import main
from chupa.artifacts import Cost, Diagnosis, DiagnosisReply, Finding, StageResult
from chupa.caps import consume, draws
from chupa.config import load_config
from chupa.journal import EventType, Journal
from chupa.llm import FakeLLM
from chupa.providers import ProviderSetupError, resolve
from chupa.specs import data_close, data_open
from chupa.stages import StagesRun
from tests.test_drain_reentry import NoChild
from tests.test_providers import CONFIG as ROUTING_CONFIG
from tests.test_stages import ENV, SNAG, STEM, agent, git, verdict
from tests.test_terminal import author, clock, diagnosis_reply, repo  # noqa: F401 -- fixture


def history(repo: Path):
    return [e for e in Journal(repo / ".chupa" / "state", clock).read() if e.ticket == STEM]


def invoke(repo: Path, script: list, verb: str = "run"):
    llm = FakeLLM(script)
    argv = [verb, STEM] if verb == "run" else [verb]
    code = main(argv, cwd=repo, env=ENV, clock=clock,
                pipeline=lambda c: runner.bind(c, llm), reexec=NoChild())
    return code, llm


def diagnosis(repo: Path) -> Diagnosis:
    return Diagnosis.model_validate_json((repo / "tickets" / STEM / "diagnosis.json").read_text())


@pytest.mark.parametrize("reply", [
    {"verdict": "maybe", "lessons": ["do this"]},
    {"verdict": "retry", "lessons": []},
    {"verdict": "retry", "lessons": ["   "]},
    {"verdict": "retry", "lessons": ["x" * 301]},
    {"verdict": "retry", "lessons": ["x"] * 6},
    {"verdict": "retry", "lessons": ["x"], "extra": "forbidden"},
])
def test_reply_schema_refuses_invalid_shape(reply):
    with pytest.raises(ValidationError):
        DiagnosisReply.model_validate(reply)


def test_routing_inherits_review_at_asked_tier_and_preserves_own_row(tmp_path):
    (tmp_path / "config.yaml").write_text(ROUTING_CONFIG)
    cfg = load_config(None, cwd=tmp_path)
    served = resolve(cfg, "medium", "diagnose")
    assert (served.provider.name, served.model) == ("claude", "c-max")
    with pytest.raises(ProviderSetupError, match="tier 'high', surface 'diagnose'"):
        resolve(cfg, "high", "diagnose")
    (tmp_path / "config.yaml").write_text(ROUTING_CONFIG.replace(
        "- {tier: medium, surface: review,", "- {tier: medium, surface: diagnose, candidates: [{provider: codex}]}\n"
        "  - {tier: medium, surface: review,"))
    own = resolve(load_config(None, cwd=tmp_path), "medium", "diagnose")
    assert (own.provider.name, own.model) == ("codex", "x-med")


def test_review_snag_orders_harvest_draw_effect_signal_and_terminal(repo):
    author(repo)
    lesson = "Read the review finding and change the word to ok."
    code, llm = invoke(repo, [agent({"chupa/thing.py": "ok\n"}), verdict("snag", [SNAG]),
                              diagnosis_reply(lesson)])
    assert code == runner.EXIT_TICKET
    events = history(repo)
    harvest = next(i for i, e in enumerate(events) if e.type == EventType.EFFECT_COMPLETION
                   and e.key == f"ticket-plane/{STEM}/0/harvest")
    draw = next(i for i, e in enumerate(events) if e.type == EventType.CAP_CONSUMED
                and e.body["cap"] == "diagnosis")
    effect = next(i for i, e in enumerate(events) if e.type == EventType.EFFECT_COMPLETION
                  and e.key and "/diagnose/" in e.key)
    signal = next(i for i, e in enumerate(events) if e.type == EventType.SIGNAL
                  and e.body.get("signal") == "diagnosis")
    terminal = next(i for i, e in enumerate(events) if e.type == EventType.STATE_TRANSITION
                    and e.body.get("to") == "gate_failed")
    assert harvest < draw < effect < signal < terminal
    assert events[draw].body == {"cap": "diagnosis", "ticket_sha": git(
        repo, "rev-parse", f"HEAD:tickets/{STEM}/ticket.md").strip()}
    assert events[signal].body == {"signal": "diagnosis", "attempt": 0, "verdict": "retry",
                                   "lessons": [lesson], "mechanical": None}
    assert events[terminal].body == {"to": "gate_failed", "stage": "review"}
    requests = [r for r in llm.requests if r.surface == "diagnose"]
    assert len(requests) == 1 and requests[0].tier == "medium"
    assert SNAG["message"] in requests[0].rendered
    assert (repo / "tickets" / STEM / "ticket.md").read_text() in requests[0].rendered
    record = diagnosis(repo)
    assert (record.stem, record.attempt, record.verdict, record.lessons, record.mechanical) == (
        STEM, 0, "retry", [lesson], None)
    assert f"chupa({STEM}): diagnosis" in git(repo, "log", "--format=%s", "main")


def test_invalid_verdict_reprompts_then_fails_closed_with_one_draw(repo):
    author(repo)
    cap = load_config(None, cwd=repo).caps.retry
    bad = json.dumps({"verdict": "maybe", "lessons": ["try again"]})
    code, llm = invoke(repo, [agent({"chupa/thing.py": "ok\n"}), verdict("snag", [SNAG])]
                       + [bad] * (cap + 1))
    assert code == runner.EXIT_TICKET
    requests = [r for r in llm.requests if r.surface == "diagnose"]
    assert len(requests) == cap + 1
    assert "invalid_artifact" in requests[1].rendered and "maybe" not in requests[1].rendered
    assert draws(history(repo), STEM, "diagnosis") == 1
    record = diagnosis(repo)
    assert record.verdict == "abandon-human" and record.lessons == []
    assert record.mechanical.startswith("no schema-valid verdict")


@pytest.mark.parametrize("outcome,findings,expected", [
    ("gate_failed", [], "workspace gone"),
    ("budget_exceeded", [], None),
    ("premise_failed", [Finding(code="render_over_bound", message="too large", paved_road="shrink")], None),
])
def test_missing_workspace_and_no_call_short_circuits(repo, monkeypatch, outcome, findings, expected):
    author(repo)

    async def stage_seam(ctx, ticket):
        return StagesRun(attempt=0, results={"implement": StageResult(
            outcome=outcome, artifact=None, findings=findings, cost=Cost())})

    monkeypatch.setattr(runner, "run_stages", stage_seam)
    code, llm = invoke(repo, [])
    assert code == runner.EXIT_TICKET and llm.requests == []
    assert draws(history(repo), STEM, "diagnosis") == 0
    signals = [e.body for e in history(repo) if e.type == EventType.SIGNAL and e.body.get("signal") == "diagnosis"]
    assert [s["mechanical"] for s in signals] == ([expected] if expected else [])


@pytest.mark.parametrize("cap,expected", [("diagnosis", "diagnosis cap spent"),
                                          ("infra", "infra cap spent")])
def test_spent_caps_short_circuit_after_infra_draw(repo, cap, expected):
    author(repo)
    # The infra case spends its sole unit on this terminal; the diagnosis case arrives already spent.
    if cap == "infra":
        path = repo / "config.yaml"
        path.write_text(path.read_text() + "\ncaps: {infra: 1}\n")
    else:
        consume(Journal(repo / ".chupa" / "state", clock), STEM, "diagnosis", "old-ticket-sha")
        # Default cap is six, so fill the remaining lineage draws.
        for _ in range(load_config(None, cwd=repo).caps.diagnosis - 1):
            consume(Journal(repo / ".chupa" / "state", clock), STEM, "diagnosis", "old-ticket-sha")
    code, llm = invoke(repo, [RuntimeError("provider failed")])
    assert code == runner.EXIT_TICKET
    assert [r.surface for r in llm.requests if r.surface == "diagnose"] == []
    assert draws(history(repo), STEM, "diagnosis") == (6 if cap == "diagnosis" else 0)
    assert diagnosis(repo).mechanical == expected
    assert next(e.body["mechanical"] for e in history(repo) if e.type == EventType.SIGNAL
                and e.body.get("signal") == "diagnosis") == expected


def test_drain_renders_two_attempts_lessons_and_no_spooled_raw_marker(repo):
    author(repo)
    marker = "PRIVATE_SPOOLED_FIRST_ATTEMPT_MARKER"
    code, llm = invoke(repo, [RuntimeError(marker), diagnosis_reply("Avoid the first dead end."),
                              agent({"chupa/thing.py": "nope\n"}), diagnosis_reply("Write ok in thing.py."),
                              agent({"chupa/thing.py": "ok\n"}), verdict()], verb="drain")
    assert code == 0
    renders = [r.rendered for r in llm.requests if r.surface == "implement"]
    assert len(renders) == 3
    block = renders[2].split(data_open("ticket"), 1)[1].split(data_close("ticket"), 1)[0]
    criteria = block.split("## Acceptance criteria", 1)[1].split("## Verification", 1)[0]
    assert "> Avoid the first dead end." in criteria
    assert "> Write ok in thing.py." in criteria
    assert marker not in renders[1] and marker not in renders[2]


def test_no_lessons_keeps_raw_harvest_reason(repo):
    author(repo)
    marker = "RAW_REASON_WITHOUT_LESSONS"
    cap = load_config(None, cwd=repo).caps.retry
    bad = json.dumps({"verdict": "maybe", "lessons": ["not used"]})
    code, _ = invoke(repo, [RuntimeError(marker)] + [bad] * (cap + 1))
    assert code == runner.EXIT_TICKET and diagnosis(repo).lessons == []
    code, llm = invoke(repo, [agent({"chupa/thing.py": "ok\n"}), verdict()])
    assert code == 0
    render = next(r.rendered for r in llm.requests if r.surface == "implement")
    assert f"> RuntimeError: {marker}" in render
