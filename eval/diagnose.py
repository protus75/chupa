"""Score the production diagnosis stage over the committed failure corpus."""

import argparse
import asyncio
import hashlib
import json
import os
import sys
from collections import Counter
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, PrivateAttr, ValidationError

from chupa.artifacts import DIAGNOSIS_VERDICTS, DiagnosisReply, DiagnosisVerdictName, Harvest
from chupa.config import Config, load_config
from chupa.driver import Driver
from chupa.git import Git
from chupa.journal import EventType, Journal
from chupa.lockfile import Lockfile
from chupa.llm import AgentEffort, AgentTier
from chupa.providers import ProviderLLM, resolve
from chupa.seams import Clock, LocalFileSystem, SubprocessExec
from chupa.specs import load_spec
from chupa.stages import DiagnosisMaterial, diagnose_stage

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "eval" / "diagnose_fixtures"
SPECS = ROOT / "specs"
REPORT = ROOT / "eval" / "diagnose_report.json"
RUN_USD_CAP = 5.00
RUN_DEADLINE_S = 2400.0
CALL_STUCK_S = 600.0
SIGNAL = "diagnose_eval_start"
Outcome = Literal["agree", "disagree", "invalid_artifact", "timeout", "infra_error",
                  "skipped_cost_cap", "skipped_deadline"]


class _Closed(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)


class Case(_Closed):
    ticket: str
    harvest: Harvest
    run_record: str | None
    expected: DiagnosisVerdictName
    why: str
    _name: str = PrivateAttr(default="")
    _path: Path | None = PrivateAttr(default=None)

    @property
    def name(self) -> str:
        return self._name


class CaseError(Exception):
    pass


def load_cases(root: Path = FIXTURES) -> list[Case]:
    cases = []
    for path in sorted(root.glob("*.json")):
        try:
            case = Case.model_validate_json(path.read_text())
        except (OSError, ValidationError) as exc:
            raise CaseError(f"{path}: invalid case envelope: {exc}; fix its closed JSON fields and Harvest") from None
        object.__setattr__(case, "_name", path.stem)
        object.__setattr__(case, "_path", path)
        cases.append(case)
    if len(cases) != 12:
        raise CaseError(f"{root}: found {len(cases)} cases; add or remove JSON case files to make exactly 12")
    counts = Counter(c.expected for c in cases)
    thin = [v for v in DIAGNOSIS_VERDICTS if counts[v] < 2]
    if thin:
        raise CaseError(f"{root}: verdicts {thin} have fewer than two cases; add cases expecting each verdict")
    return cases


def fixtures_sha(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.glob("*.json")):
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


class CaseResult(_Closed):
    name: str
    expected: DiagnosisVerdictName
    got: DiagnosisVerdictName | None
    outcome: Outcome
    usd: float
    seconds: float
    provider: str | None
    model: str | None


class Agreement(_Closed):
    agree: int
    scored: int
    rate: float | None


class Report(_Closed):
    schema_version: Literal[1]
    complete: bool
    spec_version: str
    tier: AgentTier
    effort: AgentEffort
    usd_cap: float
    usd_spent: float
    fixtures_sha: str
    cases: list[CaseResult]
    agreement: Agreement


def _agreement(rows: Sequence[CaseResult]) -> Agreement:
    agree = sum(r.outcome == "agree" for r in rows)
    scored = sum(r.got is not None for r in rows)
    return Agreement(agree=agree, scored=scored, rate=agree / scored if scored else None)


def _report(rows: list[CaseResult], spec, sha: str) -> Report:
    return Report(schema_version=1, complete=all(r.outcome != "skipped_deadline" for r in rows),
                  spec_version=spec.meta.version, tier=spec.meta.tier, effort=spec.meta.effort,
                  usd_cap=RUN_USD_CAP, usd_spent=sum(r.usd for r in rows), fixtures_sha=sha,
                  cases=rows, agreement=_agreement(rows))


def _write(path: Path, report: Report) -> None:
    LocalFileSystem().write(path, (report.model_dump_json(indent=2) + "\n").encode())


async def run_eval(*, config: Config, driver: Driver, journal: Journal, cases: Sequence[Case],
                   clock: Clock, specs_dir: Path = SPECS, report_path: Path = REPORT,
                   progress: Callable[[str], None] = lambda _: None) -> Report:
    spec = load_spec((specs_dir / "diagnose.md").read_text())
    sha = fixtures_sha(cases[0]._path.parent if cases and cases[0]._path else FIXTURES)
    prior = None
    if report_path.exists():
        try:
            prior = Report.model_validate_json(report_path.read_text())
        except (OSError, ValidationError):
            raise CaseError(f"{report_path}: invalid report; delete eval/diagnose_report.json to start over") from None
        if prior.fixtures_sha != sha or prior.spec_version != spec.meta.version:
            raise CaseError(f"{report_path}: corpus or spec changed; delete eval/diagnose_report.json to start over")
    rows = {r.name: r for r in prior.cases if r.outcome != "skipped_deadline"} if prior else {}
    attempt = 1 + sum(e.type == EventType.SIGNAL and e.body.get("signal") == SIGNAL for e in journal.read())
    journal.append(EventType.SIGNAL, {"signal": SIGNAL, "attempt": attempt})
    started = clock()
    largest = max((r.usd for r in rows.values()), default=0.0)
    serving = resolve(config, spec.meta.tier, "diagnose")
    estimate = serving.provider.limits.est_cost_per_call_usd or 0.0
    for case in cases:
        if case.name in rows:
            continue
        spent = sum(r.usd for r in rows.values())
        left = RUN_DEADLINE_S - (clock() - started).total_seconds()
        if left <= 0:
            outcome = "skipped_deadline"
        elif spent + max(estimate, largest) > RUN_USD_CAP:
            outcome = "skipped_cost_cap"
        else:
            outcome = None
        if outcome is not None:
            row = CaseResult(name=case.name, expected=case.expected, got=None, outcome=outcome,
                             usd=0.0, seconds=0.0, provider=None, model=None)
        else:
            material = DiagnosisMaterial(ticket=case.ticket, terminal=case.harvest.terminal,
                                         stage=case.harvest.stage, harvest=case.harvest,
                                         run_record=case.run_record)
            result = await driver.run(diagnose_stage(spec, material), material,
                                      ticket=f"diagnose-eval-{case.name}", attempt=attempt, workspace=ROOT,
                                      tier=spec.meta.tier, effort=spec.meta.effort,
                                      stuck_budget=min(CALL_STUCK_S, left), expected_budget='eval', scope_fence=())
            reply = result.artifact
            got = reply.verdict if result.outcome == "ok" and isinstance(reply, DiagnosisReply) else None
            result_outcome = ("agree" if got == case.expected else "disagree") if got else result.outcome
            row = CaseResult(name=case.name, expected=case.expected, got=got, outcome=result_outcome,
                             usd=result.cost.usd, seconds=result.cost.seconds,
                             provider=result.cost.provider, model=result.cost.model)
            largest = max(largest, row.usd)
        rows[case.name] = row
        current = _report([rows[c.name] for c in cases if c.name in rows], spec, sha)
        _write(report_path, current)
        progress(f"{case.name}: {row.outcome}")
    return _report([rows[c.name] for c in cases], spec, sha)


def verify(report_path: Path, cases: Sequence[Case], specs_dir: Path = SPECS) -> list[str]:
    try:
        report = Report.model_validate_json(report_path.read_text())
    except (OSError, ValidationError) as exc:
        return [f"report schema: {exc}"]
    failures = []
    if not report.complete:
        failures.append("complete: report has skipped deadline cases")
    if [(r.name, r.expected) for r in report.cases] != [(c.name, c.expected) for c in cases]:
        failures.append("cases: names or expected verdicts differ from corpus")
    if report.fixtures_sha != fixtures_sha(cases[0]._path.parent if cases and cases[0]._path else FIXTURES):
        failures.append("fixtures_sha: corpus differs")
    if report.spec_version != load_spec((specs_dir / "diagnose.md").read_text()).meta.version:
        failures.append("spec_version: diagnosis spec differs")
    if report.usd_cap != RUN_USD_CAP:
        failures.append("usd_cap: cap differs")
    if report.usd_spent != sum(r.usd for r in report.cases) or report.usd_spent > RUN_USD_CAP:
        failures.append("usd_spent: spend differs from cases or exceeds cap")
    if report.agreement != _agreement(report.cases):
        failures.append("agreement: score does not recompute")
    return failures


def _clock() -> datetime:
    return datetime.now(UTC)


async def _run(config: Config) -> Report:
    env = dict(os.environ)
    exec_ = SubprocessExec()
    instance_id = await Git(exec_, env=env, timeout=30).describe(ROOT)
    lock = Lockfile(config.state_dir, instance_id=instance_id, clock=_clock)
    lock.acquire()
    try:
        llm = ProviderLLM(config, exec_=exec_, fs=LocalFileSystem(), env=env, cwd=ROOT, timeout=CALL_STUCK_S)
        driver = Driver.from_config(config, llm=llm, env=env, clock=_clock, sleep=asyncio.sleep)
        return await run_eval(config=config, driver=driver, journal=driver.journal,
                              cases=load_cases(), clock=_clock, progress=print)
    finally:
        lock.release()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m eval.diagnose")
    parser.add_argument("command", choices=("run", "verify"))
    args = parser.parse_args(argv)
    if args.command == "verify":
        failures = verify(REPORT, load_cases())
        for failure in failures:
            print(failure)
        return int(bool(failures))
    try:
        report = asyncio.run(_run(load_config(None, cwd=ROOT)))
    except CaseError as exc:
        print(exc, file=sys.stderr)
        return 2
    print(report.agreement.model_dump_json())
    return 0


if __name__ == "__main__":
    sys.exit(main())
