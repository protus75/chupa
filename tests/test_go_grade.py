"""GO-grade entry contract, closed reports and operator-only verdict production."""

import asyncio
from dataclasses import asdict

import pytest
from pydantic import ValidationError

from chupa.artifacts import ReviewBaselineReport
from chupa.seams import LocalFileSystem
from eval import harness
from tests.test_eval_harness import corpus_results, report_fixture


def test_record_go_requires_complete_floors_identity_and_operator_judgment(tmp_path):
    report, cfg, journal = report_fixture(tmp_path)
    out = tmp_path / "operator-report.json"
    fs = LocalFileSystem()

    def record(candidate=report, config=cfg, approve=True):
        return harness.record_go(candidate, config=config, journal=journal, out=out, fs=fs, approve_author_graph=approve)

    assert report.scores.catch_rate == 0.85 and report.scores.clean_false_snag == 0.15
    candidates = [
        report_fixture(tmp_path, corpus_results(49, 20, 49, 0))[0],
        report_fixture(tmp_path, corpus_results(60, 14, 60, 0))[0],
        report_fixture(tmp_path, graph=False)[0],
        report_fixture(tmp_path, corpus_results(catches=50))[0],
        report_fixture(tmp_path, corpus_results(false_snags=4))[0],
    ]
    for candidate in candidates:
        before = journal.read()
        with pytest.raises(harness.FixtureError):
            record(candidate)
        assert journal.read() == before and not out.exists()
    for surface in ("review", "author"):
        raw = report.model_dump()
        raw["verdict_signal"]["body"]["identity"][surface]["rows"]["low"]["model"] = "drifted"
        drift = ReviewBaselineReport.model_validate(raw)
        before = journal.read()
        with pytest.raises(harness.FixtureError, match="drifted"):
            record(drift)
        assert journal.read() == before and not out.exists()
    raw = report.model_dump()
    raw["verdict_signal"]["body"]["identity"]["author"]["spec_major"] += 1
    before = journal.read()
    with pytest.raises(harness.FixtureError, match="drifted"):
        record(ReviewBaselineReport.model_validate(raw))
    with pytest.raises(harness.FixtureError, match="judgment"):
        record(approve=False)
    # Revalidation defeats unvalidated model_copy updates before any append/write.
    with pytest.raises(ValidationError):
        record(report.model_copy(update={"complete": False}))
    assert journal.read() == before and not out.exists()
    measured = tmp_path / "measured.json"
    harness.write_report(measured, report, fs=fs)
    files = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    with pytest.raises(harness.FixtureError, match="judgment"):
        asyncio.run(harness._run(cfg, {}, lambda: None, out=out, go_report=measured))
    assert files == {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    recorded = record()
    assert recorded.verdict_signal.body.verdict == "GO"
    assert recorded.verdict_signal.model_dump() == asdict(journal.read()[-1])
    assert recorded.verdict_signal.body.identity.model_dump() == harness.baseline_identity(cfg)
    assert ReviewBaselineReport.model_validate_json(out.read_bytes()) == recorded


def test_review_baseline_report_closed_schema(tmp_path):
    report, _, _ = report_fixture(tmp_path)
    assert set(report.model_dump()) == {"schema_version", "complete", "cap_usd", "spent_usd", "results", "scores", "author_graph", "verdict_signal"}
    mutations = [
        lambda r: r.update(extra=True),
        lambda r: r.update(schema_version=2),
        lambda r: r.update(schema_version=True),
        lambda r: r.update(spent_usd=float("inf")),
        lambda r: r.update(spent_usd=-1.0),
        lambda r: r["results"].append(r["results"][0]),
        lambda r: r["results"][0].update(outcome="unknown"),
        lambda r: r["results"][0].update(verdict="lgtm"),
        lambda r: r["results"][0].update(verdict=None),
        lambda r: r["results"][0]["expected"].update(extra=True),
        lambda r: r["scores"].update(planted=1),
        lambda r: r["scores"].update(extra=True),
        lambda r: r["verdict_signal"].update(type="effect_completion"),
        lambda r: r["verdict_signal"].update(v=True),
        lambda r: r["verdict_signal"].update(ts="yesterday"),
        lambda r: r["verdict_signal"]["body"].update(extra=True),
        lambda r: r["verdict_signal"]["body"]["scores"].update(catch_rate=1.0),
        lambda r: r["verdict_signal"]["body"]["identity"].update(extra=True),
        lambda r: r["verdict_signal"]["body"]["identity"]["review"]["rows"].pop("low"),
        lambda r: r["verdict_signal"]["body"]["fixture_authors"][0].update(provider="invented"),
        lambda r: r["author_graph"]["tickets"][0].update(extra=True),
    ]
    for mutate in mutations:
        raw = report.model_dump()
        mutate(raw)
        with pytest.raises(ValidationError):
            ReviewBaselineReport.model_validate(raw)
    partial, _, _ = report_fixture(tmp_path, corpus_results(18, 4, 18, 0))
    raw = partial.model_dump()
    raw["verdict_signal"]["body"]["verdict"] = "GO"
    with pytest.raises(ValidationError, match="GO"):
        ReviewBaselineReport.model_validate(raw)
