"""Offline contract tests for the production diagnosis eval."""

import asyncio
import json
import textwrap
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from chupa.artifacts import DIAGNOSIS_VERDICTS, Harvest
from chupa.config import load_config
from chupa.driver import Driver
from chupa.journal import Journal
from chupa.llm import FakeLLM, HANG, LLMResult
from chupa.specs import load_spec
from chupa.stages import DiagnosisMaterial, diagnose_stage
from eval import diagnose

ROOT = Path(__file__).resolve().parent.parent
CONFIG = textwrap.dedent("""\
schema_version: 1
state_dir: state
providers:
  - name: codex
    kind: cli
    models_by_tier: {low: fake, medium: fake, high: fake, max: fake}
    limits: {concurrency: 1, est_cost_per_call_usd: 1.0}
routing:
  - {tier: high, surface: diagnose, candidates: [{provider: codex}]}
review: {}
merge: {}
engine_plane_safety_inventory: []
""")


def cases():
    return diagnose.load_cases()


def answer(verdict, usd=0.0):
    return LLMResult(text=json.dumps({"verdict": verdict, "lessons": ["Follow the evidence."]}),
                     input_tokens=1, output_tokens=1, provider="fake", model="fake", usd=usd)


def setup(tmp_path, script, *, clock=None, sleep=None):
    (tmp_path / "config.yaml").write_text(CONFIG)
    config = load_config(None, cwd=tmp_path)
    llm = FakeLLM(script)
    now = datetime(2026, 10, 5, tzinfo=UTC)
    clock = clock or (lambda: now)

    async def never(_):
        await asyncio.Event().wait()

    driver = Driver.from_config(config, llm=llm, env={}, clock=clock, sleep=sleep or never)
    return config, driver, Journal(config.state_dir, clock), llm, tmp_path / "report.json", clock


def execute(setup_result, corpus=None):
    config, driver, journal, _, path, clock = setup_result
    return asyncio.run(diagnose.run_eval(config=config, driver=driver, journal=journal,
                                         cases=corpus or cases(), clock=clock, report_path=path))


def disk(path):
    return diagnose.Report.model_validate_json(path.read_text())


def test_committed_corpus_and_closed_envelope(tmp_path):
    corpus = cases()
    assert len(corpus) == 12
    assert [c.name for c in corpus] == sorted(c.name for c in corpus)
    assert all(isinstance(c.harvest, Harvest) for c in corpus)
    assert all(sum(c.expected == v for c in corpus) >= 2 for v in DIAGNOSIS_VERDICTS)
    for path in diagnose.FIXTURES.glob("*.json"):
        (tmp_path / path.name).write_bytes(path.read_bytes())
    path = next(tmp_path.glob("*.json"))
    raw = json.loads(path.read_text())
    raw["unknown"] = 1
    path.write_text(json.dumps(raw))
    with pytest.raises(diagnose.CaseError, match=path.name):
        diagnose.load_cases(tmp_path)
    raw.pop("unknown")
    raw["expected"] = "invented"
    path.write_text(json.dumps(raw))
    with pytest.raises(diagnose.CaseError, match=path.name):
        diagnose.load_cases(tmp_path)
    path.unlink()
    with pytest.raises(diagnose.CaseError, match="exactly 12"):
        diagnose.load_cases(tmp_path)


def test_reachability_uses_production_render_and_writes_valid_report(tmp_path):
    corpus = cases()
    state = setup(tmp_path, [answer(c.expected) for c in corpus])
    execute(state, corpus)
    report = disk(state[4])
    assert report.complete and report.agreement.rate == 1.0
    assert report.agreement.agree == report.agreement.scored == 12
    assert [r.outcome for r in report.cases] == ["agree"] * 12
    assert diagnose.verify(state[4], corpus) == []
    spec = load_spec((ROOT / "specs" / "diagnose.md").read_text())
    for case, req in zip(corpus, state[3].requests, strict=True):
        material = DiagnosisMaterial(ticket=case.ticket, terminal=case.harvest.terminal,
                                     stage=case.harvest.stage, harvest=case.harvest, run_record=case.run_record)
        assert req.surface == "diagnose"
        assert req.rendered == diagnose_stage(spec, material).render(material, [])


def deadline_report(tmp_path):
    corpus = cases()
    base = datetime(2026, 10, 5, tzinfo=UTC)
    now = [base]
    holder = {}

    async def sleep(seconds):
        await asyncio.sleep(0)
        if len(holder["llm"].requests) == 2:
            now[0] += timedelta(seconds=seconds)
            return
        await asyncio.Event().wait()

    def first(_):
        now[0] += timedelta(seconds=2000)
        return answer(corpus[0].expected, 0.25)

    state = setup(tmp_path, [first, HANG],
                  clock=lambda: now[0], sleep=sleep)
    holder["llm"] = state[3]
    execute(state, corpus)
    return state, corpus


def test_deadline_kills_second_call_and_records_all_later_cases(tmp_path):
    state, _ = deadline_report(tmp_path)
    report = disk(state[4])
    assert state[3].aborted == 1
    assert len(state[3].requests) == 2
    assert report.cases[1].outcome == "timeout"
    assert [r.outcome for r in report.cases[2:]] == ["skipped_deadline"] * 10
    assert not report.complete


def test_precall_cost_cap_records_every_skip(tmp_path):
    corpus = cases()
    state = setup(tmp_path, [answer(c.expected, 2.0) for c in corpus])
    execute(state, corpus)
    report = disk(state[4])
    assert len(state[3].requests) == 2
    assert report.usd_spent == 4.0 and report.usd_cap == diagnose.RUN_USD_CAP
    assert [r.outcome for r in report.cases[2:]] == ["skipped_cost_cap"] * 10


def test_resume_only_deadline_skips_and_refuses_changed_corpus(tmp_path):
    state, corpus = deadline_report(tmp_path)
    first = disk(state[4])
    resumed = setup(tmp_path, [answer(c.expected) for c in corpus[2:]])
    execute(resumed, corpus)
    report = disk(resumed[4])
    assert len(resumed[3].requests) == 10
    assert report.complete and report.usd_spent == first.usd_spent
    assert report.cases[1].outcome == "timeout"
    changed = report.model_dump()
    changed["fixtures_sha"] = "wrong"
    state[4].write_text(json.dumps(changed))
    with pytest.raises(diagnose.CaseError, match="delete eval/diagnose_report.json to start over"):
        execute(resumed, corpus)


@pytest.mark.parametrize("field,change,fragment", [
    ("complete", False, "complete"),
    ("cases", "missing", "cases"),
    ("usd_spent", 6.0, "usd_spent"),
    ("agreement", "wrong", "agreement"),
])
def test_verify_names_each_broken_check(tmp_path, field, change, fragment):
    corpus = cases()
    state = setup(tmp_path, [answer(c.expected) for c in corpus])
    execute(state, corpus)
    raw = json.loads(state[4].read_text())
    if change == "missing":
        raw[field].pop()
    elif change == "wrong":
        raw[field]["agree"] = 0
    else:
        raw[field] = change
    state[4].write_text(json.dumps(raw))
    assert any(fragment in failure for failure in diagnose.verify(state[4], corpus))
