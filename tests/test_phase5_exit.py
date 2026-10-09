"""Phase 5 reads committed production evidence; disposable compositions prove its writers.

The dispatch head freezes this exit's history so later retros do not replace its evidence.
No test supplies, refreshes or commits the receipt consumed by the exit read.
"""

import asyncio
from copy import deepcopy
from datetime import datetime
from functools import lru_cache
import json
import math
import os
from pathlib import Path
import re

import pytest
import yaml

from chupa.git import Git
from chupa.journal import EVENT_VERSIONS, Event
from chupa.retro import RetroArtifact
from chupa.seams import SubprocessExec
from chupa.specs import load_spec
from chupa.stages import Invoice, read_review
from chupa.tickets import _bullets, _sections, split_frontmatter, ticket_path

ROOT = Path(__file__).resolve().parents[1]
EXIT_HEAD = "8447c72d45c5c14c7bddc1b24778ff8e68f72808"
PAYLOADS = ("retro-drain-invoker", "retro-box-activation", "scorecard-reporting",
            "status-projection", "baseline-binding-reader", "retro-doctor-cli")


@lru_cache
def _git(*argv):
    return asyncio.run(Git(SubprocessExec(), env=os.environ, timeout=30)._run(ROOT, *argv))


def _committed(path, head=EXIT_HEAD):
    return _git("show", f"{head}:{path}")


def _dependencies(stem):
    text = _committed(ticket_path(stem))
    frontmatter, _ = split_frontmatter(text)
    assert yaml.safe_load(frontmatter)["state"] != "rejected", (
        f"premise_failed: {stem} needs a merged same-goal successor and rewired dependencies")
    sections, errors = _sections(text, ticket_path(stem))
    assert not errors
    if sections["Depends on"].strip() in {"none", "- none"}:
        return ()
    edges, errors = _bullets(sections["Depends on"], "Depends on", ticket_path(stem))
    assert not errors
    return tuple(edges)


def test_phase5_exit_dependency_coverage():
    registry = yaml.safe_load(re.search(r"^# BEGIN_REGISTRY_P5\n(.*?)^# END_REGISTRY_P5$",
        _committed("CHUPA_PLAN.md"), re.M | re.S)[1])
    assert tuple(s for a in registry["admissions"][:-1] for s in a) == PAYLOADS
    assert _dependencies("phase5-exit") == ("phase5-continue-05",)
    reached, pending = set(), ["phase5-continue-05"]
    while pending:
        stem = pending.pop()
        if stem in reached:
            continue
        reached.add(stem)
        pending.extend(_dependencies(stem))
    assert set(PAYLOADS) <= reached, f"premise_failed: Phase 5 coverage {set(PAYLOADS) - reached}"
    for stem in PAYLOADS:
        assert set(registry["seeds"][stem].get("depends", ())) <= set(_dependencies(stem)), stem
    # Dispatch establishes settlement; this extra read is only the bare squash trailer.
    trailers = _git("log", EXIT_HEAD, "--format=%(trailers:key=chupa-ticket,valueonly)").split()
    assert set(PAYLOADS) <= set(trailers)


def _receipt():
    paths = _git("ls-tree", "-r", "--name-only", EXIT_HEAD, "--", "tickets/retro").splitlines()
    receipts = [p for p in paths if re.fullmatch(r"tickets/retro/[0-9]{6}\.md", p)]
    assert receipts, ("premise_failed: tickets/retro/<seq>.md absent; machinery retro-drain-invoker + "
                      "scorecard-reporting, producer forced pre-exit retro")
    path = max(receipts)
    text = _committed(path)
    assert text.startswith("# Retro receipt\n\n```json\n")
    record = json.loads(text.split("```json\n", 1)[1].split("\n```", 1)[0])
    return path, text, record


def _number(value, *, nonnegative=True):
    assert type(value) in (int, float) and math.isfinite(value), "malformed numeric accounting"
    assert not nonnegative or value >= 0, "negative accounting"


def _count(value):
    assert type(value) is int and value >= 0, "malformed integer accounting"


def _time(value):
    moment = datetime.fromisoformat(value)
    assert moment.tzinfo is not None
    return moment


def _ancestor(older, newer):
    assert re.fullmatch(r"[0-9a-f]{40}", older), "fixture provenance"
    assert _git("merge-base", older, newer).strip() == older, "stale or foreign provenance"


def _table(text):
    block = text.split("## Surface scorecard\n", 1)[1]
    lines = [line for line in block.splitlines() if line.startswith("|")]
    assert lines[:2] == [
        "| Surface | Evaluated tickets | Catches | Escapes | Bypass count | Catch rate | Escape rate | Prune candidate |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |"]
    rows = {}
    for line in lines[2:]:
        columns = [v.strip() for v in line.strip("|").split("|")]
        assert len(columns) == 8
        surface = columns[0]
        assert surface not in rows, "duplicate surface"
        counts = tuple(int(v) for v in columns[1:5])
        assert all(v >= 0 for v in counts)
        rates = tuple(float(v) for v in columns[5:7])
        assert all(math.isfinite(v) and 0 <= v <= 1 for v in rates)
        assert columns[7] in {"true", "false"}
        rows[surface] = (*counts, *rates, columns[7] == "true")
    assert rows, "missing production surfaces"
    return rows


def _validate_receipt(path, text, record):
    assert set(record) == {"window_boundary", "window_start", "window_final_event", "provenance",
        "measurements", "calibration_divergence", "tombstone_digest", "tombstone_reopens", "proposals"}
    boundary = record["window_boundary"]
    assert boundary == "initial" or re.fullmatch(r"retro/[1-9][0-9]*", boundary)
    sequence = int(Path(path).stem)
    assert sequence == (1 if boundary == "initial" else int(boundary.split("/")[1]) + 1)
    start = _time(record["window_start"])
    final = Event(**record["window_final_event"])
    assert final.type in EVENT_VERSIONS and final.v == EVENT_VERSIONS[final.type]
    assert final.ticket is None or isinstance(final.ticket, str)
    assert final.key is None or isinstance(final.key, str)
    assert isinstance(final.body, dict)
    assert start <= _time(final.ts)
    provenance = record["provenance"]
    assert set(provenance) == {"head", "spec_version", "at"}
    head = provenance["head"]
    _ancestor(head, EXIT_HEAD)
    # The final seeder merge precedes the forced dispatch hook as well as the last payload.
    for stem in ("retro-doctor-cli", "phase5-continue-05"):
        feature = _git("log", EXIT_HEAD, "--format=%H", "--fixed-strings",
            f"--grep=chupa-ticket: {stem}").splitlines()
        assert len(feature) == 1
        _ancestor(feature[0], head)
    producer = _git("log", EXIT_HEAD, "-1", "--format=%H", "--", path).strip()
    assert _git("rev-parse", f"{producer}^").strip() == head, "receipt not produced at its recorded HEAD"
    assert _git("show", "-s", "--format=%s", producer).strip() == f"chupa: retro {sequence:06d}"
    assert provenance["spec_version"] == load_spec(_committed("specs/retro.md", head)).meta.version
    assert _time(provenance["at"]) >= _time(final.ts)
    RetroArtifact.model_validate({"proposals": record["proposals"]})
    assert isinstance(record["tombstone_digest"], list) and isinstance(record["tombstone_reopens"], list)

    measured = record["measurements"]
    assert set(measured) == {"merges", "merged_count", "usd", "input_tokens", "output_tokens",
                              "spikes", "elapsed_seconds", "check_observations"}
    _number(measured["usd"])
    for direction in ("input", "output"):
        tokens = measured[f"{direction}_tokens"]
        assert set(tokens) == {"known", "unknown_calls"}
        for value in tokens.values():
            _count(value)
    assert set(measured["spikes"]) == {"override", "rework", "gate-failure", "integration-red"}
    for value in measured["spikes"].values():
        _count(value)
    _count(measured["merged_count"])
    assert measured["merged_count"] == len(measured["merges"]) > 0
    stems = set(_git("ls-tree", "-r", "--name-only", head, "--", "tickets").splitlines())
    references = []
    for row in measured["merges"]:
        assert set(row) == {"ticket", "commit", "identity"}
        stem, commit = row["ticket"], row["commit"]
        assert ticket_path(stem) in stems, "fabricated merge stem"
        assert len(row["identity"]) == 2 and row["identity"][0] == stem
        _count(row["identity"][1])
        if commit is not None:
            _ancestor(commit, head)
            assert _git("show", "-s", "--format=%(trailers:key=chupa-ticket,valueonly)", commit).strip() == stem
        references.append((stem, commit))
    assert len(set(references)) == len(references)
    if final.type == "state_transition" and final.body.get("to") == "merged":
        assert (final.ticket, final.body["commit"]) in references
    assert record["calibration_divergence"] == measured["elapsed_seconds"]
    assert len(measured["elapsed_seconds"]) == len(references)
    for row, reference in zip(measured["elapsed_seconds"], references, strict=True):
        assert set(row) == {"ticket", "commit", "actual_seconds", "predicted_seconds", "divergence_seconds"}
        assert (row["ticket"], row["commit"]) == reference
        expected = (re.search(r"^- expected: (\d+)m$",
                    _committed(ticket_path(row["ticket"]), row["commit"]), re.M)
                    if row["commit"] is not None else None)
        assert row["predicted_seconds"] == (int(expected[1]) * 60 if expected else None)
        for key in ("actual_seconds", "predicted_seconds", "divergence_seconds"):
            if row[key] is not None:
                _number(row[key], nonnegative=key != "divergence_seconds")
        difference = (row["actual_seconds"] - row["predicted_seconds"]
                      if row["actual_seconds"] is not None and row["predicted_seconds"] is not None else None)
        assert row["divergence_seconds"] == difference

    # Runtime operands come from the receipt. Match whole observation batches to actual
    # committed invoices, including earlier attempts, rather than a live ignored journal.
    observations = measured["check_observations"]
    assert observations, "no production Check observations"
    remaining = list(observations)
    while remaining:
        stem = remaining[0][0]
        assert ticket_path(stem) in stems, "fabricated Check stem"
        commits = _git("log", head, "--format=%H", "--", f"tickets/{stem}/checks.json").splitlines()
        matched = False
        for commit in commits:
            invoice = Invoice.model_validate_json(_committed(f"tickets/{stem}/checks.json", commit))
            assert invoice.stem == stem
            batch = [[stem, r.code, r.verdict, r.code in invoice.bypassed] for r in invoice.reports]
            if batch and remaining[:len(batch)] == batch:
                del remaining[:len(batch)]
                matched = True
                break
        assert matched, "Check observations do not derive from committed production invoices"
    for row in observations:
        assert len(row) == 4 and row[2] in {"pass", "fail"} and type(row[3]) is bool
    rows = _table(text)
    observed_surfaces = {row[1] for row in observations}
    assert observed_surfaces <= set(rows)
    assert set(rows) <= observed_surfaces | {"review"}, "fabricated scorecard surface"
    for surface, row in rows.items():
        evaluated, catches, escapes, bypasses, catch_rate, escape_rate, prune = row
        assert escapes == 0 and escape_rate == 0, "Phase 5 escape column is not zero"
        assert catches <= evaluated and catch_rate == pytest.approx(catches / evaluated if evaluated else 0, abs=.00005)
        assert prune == (evaluated >= 25 and catches == 0)
        if surface != "review":
            observed = [o for o in observations if o[1] == surface]
            assert evaluated == len({o[0] for o in observed})
            assert bypasses == sum(o[3] for o in observed)
            failed = {o[0] for o in observed if o[2] == "fail" and not o[3]}
            assert catches <= len(failed), "catch has no failing production Check observation"
        else:
            assert bypasses == 0
            for stem, _ in references:
                review = read_review(_committed(f"tickets/{stem}/review.md", head))
                assert review.stem == stem
            assert evaluated >= len({stem for stem, _ in references})
    return record


def test_phase5_exit_committed_retro():
    _validate_receipt(*_receipt())


@pytest.mark.parametrize("corruption", ["stem", "surface", "fixture", "stale", "spec", "commit",
    "usd", "nan", "tokens", "bool-tokens", "observations", "escape", "catch", "boundary", "final-event"])
def test_phase5_exit_retro_provenance(corruption):
    path, text, original = _receipt()
    record = deepcopy(original)
    measured = record["measurements"]
    if corruption == "stem": measured["merges"][0]["ticket"] = "fixture-invented"
    elif corruption == "surface": text += "| invented | 1 | 0 | 0 | 0 | 0.0000 | 0.0000 | false |\n"
    elif corruption == "fixture": record["provenance"]["head"] = "fixture-head"
    elif corruption == "stale":
        record["provenance"]["head"] = _git("log", EXIT_HEAD, "--format=%H", "--fixed-strings",
            "--grep=chupa-ticket: retro-drain-invoker").splitlines()[0]
    elif corruption == "spec": record["provenance"]["spec_version"] = "0.0"
    elif corruption == "commit": measured["merges"][0]["commit"] = EXIT_HEAD
    elif corruption == "usd": measured["usd"] = "2.00"
    elif corruption == "nan": measured["usd"] = float("nan")
    elif corruption == "tokens": measured["input_tokens"]["unknown_calls"] = 1.5
    elif corruption == "bool-tokens": measured["output_tokens"]["known"] = True
    elif corruption == "observations": measured["check_observations"][0][2] = "fail"
    elif corruption == "escape": text = text.replace("| 0.0000 | false |", "| 0.1000 | false |", 1)
    elif corruption == "catch":
        evaluated = _table(text)["diff_budget"][0]
        text = text.replace(f"| diff_budget | {evaluated} | 0 | 0 | 0 | 0.0000 |",
                            f"| diff_budget | {evaluated} | 1 | 0 | 0 | {1 / evaluated:.4f} |")
    elif corruption == "boundary": record["window_boundary"] = "fixture-window"
    else: record["window_final_event"]["ticket"] = "fixture-invented"
    with pytest.raises(AssertionError):
        _validate_receipt(path, text, record)


def _passing_invoice(stem, suite):
    invoice = Invoice.model_validate_json(_committed(f"tickets/{stem}/checks.json"))
    assert invoice.stem == stem and invoice.passed
    assert "verification" not in invoice.bypassed
    reports = [r for r in invoice.reports if r.code == "verification"]
    assert len(reports) == 1 and reports[0].verdict == "pass" and not reports[0].findings
    commands = [r for r in invoice.verification if r.argv[:3] == ["uv", "run", "pytest"] and suite in r.argv]
    assert commands and all(r.rc == 0 and not r.base_red for r in commands)


def test_phase5_exit_retro_box(tmp_path, monkeypatch):
    from tests.test_retro_box import test_completed_retro_proposals_reach_prompt_spec_merge as proof

    _passing_invoice("retro-box-activation", "tests/test_retro_box.py")
    assert "async def test_completed_retro_proposals_reach_prompt_spec_merge(" in _committed("tests/test_retro_box.py")
    asyncio.run(proof(tmp_path, monkeypatch))


def test_phase5_exit_baseline(tmp_path):
    from chupa.policy import BASELINED_SURFACES, TIERS
    from tests.test_baseline import (test_baseline_states_and_latest_signal as states,
                                    test_baseline_routing_and_spec_drift as drift)

    _passing_invoice("baseline-binding-reader", "tests/test_baseline.py")
    source = _committed("tests/test_baseline.py")
    assert "def test_baseline_states_and_latest_signal(" in source
    assert "def test_baseline_routing_and_spec_drift(" in source
    states(tmp_path)
    for surface in BASELINED_SURFACES:
        for tier in TIERS:
            directory = tmp_path / surface / tier
            directory.mkdir(parents=True)
            drift(directory, surface, tier)


def test_phase5_exit_production_composition(tmp_path, monkeypatch):
    from tests.test_scorecard import test_scorecard_totals_and_rendering as scorecard
    from tests.test_retro import test_receipt_uses_engine_provenance_usage_calibration_and_tombstones as retro
    from tests.test_drain import test_drain_retro_due_quiescence_and_pre_exit as forced

    # These unchanged proofs exercise real Check -> production_evidence -> scorecard ->
    # Retro and the routed drain pre-exit hook, with injected seams in disposable repos.
    for name in ("scorecard", "retro", "forced"):
        directory = tmp_path / name
        directory.mkdir()
        with monkeypatch.context() as patch:
            if name == "scorecard": scorecard(directory, patch)
            elif name == "retro": retro(directory)
            else: forced(directory, patch, "pre-exit")
