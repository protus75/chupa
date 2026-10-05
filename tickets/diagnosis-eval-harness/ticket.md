---
state: confirmed
source: seed
priority: P2
kind: feature
agent_tier: high
agent_effort: medium
---

## Depends on
- spine-diagnosis

## Context
- eval/harness.py
- tests/test_eval_harness.py
- chupa/llm.py
- chupa/artifacts.py

## Plan contract
- 19.L
- 19.P2
- section 11

## Goal / Why
`eval/diagnose.py` scores the PRODUCTION diagnosis call (`diagnose_stage` in `chupa/stages.py` with `specs/diagnose.md`, from `spine-diagnosis`) over a committed 12-case fixture corpus under `eval/diagnose_fixtures/`. It writes the agreement report `eval/diagnose_report.json` under a flat per-run USD cap and a hard run deadline. Under the fake LLM every case's expected verdict is proven reachable, and the budget and deadline enforcement are pinned by tests against the report the harness writes. This ticket spends nothing: the real-model run is the next seed (`diagnosis-eval-run`), which only executes this harness.

Why: the diagnosis verdict drives the ladder and the Reject queue, yet nothing measures whether a real model's verdicts agree with a human's on known cases (19.P2 Emits). A harness that cannot prove its own scoring, budget, and kill paths under the fake would make the paid run unreviewable. Splitting harness from spend keeps the paid run a no-code execution of reviewed, merged machinery.

Owners: `eval/diagnose.py` owns the case envelope schema, corpus loading, scoring, the report schema and its writer, the cost cap, the deadline, and the `run` and `verify` subcommands. It imports the verdict vocabulary (`DIAGNOSIS_VERDICTS`), `Harvest`, `DiagnosisMaterial`, and `diagnose_stage` from `chupa/artifacts.py` and `chupa/stages.py`, and never copies them. `eval/harness.py` (the review baseline) is the idiom: its lock, Driver, and ProviderLLM composition. It is a read-only reference and stays unchanged.

## Scope in / Scope out
- In: `eval/diagnose_fixtures/<case>.json`, exactly 12 files. Each is ONE closed JSON envelope (19.P2 FIXTURE CORPORA): `ticket` (ticket.md text), `harvest` (validates as `chupa.artifacts.Harvest`), `run_record` (run.md text or null), `expected` (a member of `DIAGNOSIS_VERDICTS`), and `why` (one sentence naming the evidence that forces the verdict). Every verdict is expected by at least two cases. Files are written with `json.dumps(..., indent=2)` so each string stays one line, keeping the corpus plus harness and tests inside the section 7 diff budget. The cases are hand-authored in this diff and describe failures in a generic small Python project, never this repo's own stems.
- In: `eval/diagnose.py` with:
  - `Case`, the closed pydantic envelope model. `load_cases(root)` returns cases sorted by name and refuses with `CaseError` (naming the file and the fix) on an invalid envelope, a count other than 12, or a verdict expected by fewer than two cases.
  - Engine constants `RUN_USD_CAP = 5.00`, `RUN_DEADLINE_S = 2400.0`, `CALL_STUCK_S = 600.0`, and `REPORT = ROOT / "eval" / "diagnose_report.json"`.
  - `Report`, the closed report model: `schema_version` (1), `complete`, `spec_version`, `tier`, `effort`, `usd_cap`, `usd_spent`, `fixtures_sha` (sha256 over each case file's name and bytes in sorted order), `cases`, and `agreement`. Each case entry holds `name`, `expected`, `got` (verdict or null), `outcome` (one of `agree | disagree | invalid_artifact | timeout | infra_error | skipped_cost_cap | skipped_deadline`), `usd`, `seconds`, `provider`, and `model`. `agreement` holds `agree`, `scored` (cases with a schema-valid verdict), and `rate` (`agree / scored`, null when `scored` is 0).
  - `async def run_eval(*, config, driver, journal, cases, clock, specs_dir, report_path, progress)`. It renders every case through `diagnose_stage(spec, DiagnosisMaterial(...))`, with terminal and stage taken from the case's harvest, and calls `driver.run` at the spec's tier and effort. The stem is `diagnose-eval-<case>`. `attempt` is 1 plus the count of prior `diagnose_eval_start` signals, and one such signal is journaled at the start, so every invocation takes fresh effect keys.
  - PRE-CALL COST CAP: before each call, projected spend is `usd_spent` plus the per-call basis. The basis is the larger of the serving row's `limits.est_cost_per_call_usd` (resolved via `resolve(config, tier, "diagnose")`; 0 when undeclared) and the largest `usd` any earlier call in this report charged. When projected spend exceeds `RUN_USD_CAP`, that case and every later unrun case record `skipped_cost_cap` with no call.
  - HARD DEADLINE: each call's stuck budget is `min(CALL_STUCK_S, seconds left until RUN_DEADLINE_S)`, measured on the injected clock, so the driver's stuck-budget kill (`abort_current` first) lands at or before the deadline. A killed call records `timeout`. Once the deadline is reached, every unrun case records `skipped_deadline` with no call.
  - The report is written atomically (temp file plus replace) after EVERY case, so a killed process leaves a valid partial report. `complete` is true exactly when no case is `skipped_deadline`.
  - RESUME: when `report_path` exists with the same `fixtures_sha` and `spec_version`, `run` re-attempts only its `skipped_deadline` cases, carrying `usd_spent` toward the same cap. A mismatch refuses with exit 2, naming "delete eval/diagnose_report.json to start over".
  - `verify(report_path, cases, specs_dir) -> list[str]`, with no model call. It returns the failed checks: the report validates as `Report`; `complete` is true; case names and `expected` values equal the corpus's; `fixtures_sha` and `spec_version` match the current corpus and spec; `usd_cap == RUN_USD_CAP`; `usd_spent` equals the sum of case `usd` and is at most the cap; and `agreement` recomputes from the cases.
  - CLI `uv run python -m eval.diagnose run | verify`. `run` takes the single-writer lock on the config's state dir and composes ProviderLLM plus `Driver.from_config` exactly as `eval/harness.py` does, then prints the agreement. `verify` prints each failed check and exits 1, else exits 0.
- In: `tests/test_diagnose_eval.py` covers every invariant above, against the report file the harness writes.
- Out: running the eval against a real model and committing `eval/diagnose_report.json` (the `diagnosis-eval-run` seed).
- Out: any change to `chupa/**`, `specs/**`, or `eval/harness.py`, the triage-dedup eval (deferred to daemon-era entry), and Rework or Retro evals.

## Scope fence
- eval/diagnose.py
- eval/diagnose_fixtures
- tests/test_diagnose_eval.py

## Acceptance criteria
1. `tests/test_diagnose_eval.py` proves the committed corpus loads through `load_cases`: 12 envelopes, every harvest a valid `Harvest`, every verdict in `DIAGNOSIS_VERDICTS` expected at least twice. An envelope with an unknown key, an off-vocabulary `expected`, or a missing case is refused with `CaseError`.
2. `tests/test_diagnose_eval.py` proves REACHABILITY. A FakeLLM answers each committed case with its expected verdict as a valid `DiagnosisReply`. The written report has 12 `agree` cases, `rate == 1.0`, and `complete` true, and `verify` returns `[]` for it. Every request has surface `diagnose`, and each rendered prompt equals `diagnose_stage(spec, material).render(material, [])` for that case's material.
3. `tests/test_diagnose_eval.py` proves the HARD DEADLINE with an injected clock and sleep. A FakeLLM `HANG` on case 2, with the deadline expiring during that call, gives `llm.aborted == 1`. The report file on disk records case 2 as `timeout` and every later case as `skipped_deadline`, with no request made for them, and `complete` false.
4. `tests/test_diagnose_eval.py` proves the PRE-CALL COST CAP. FakeLLM results charging `usd=2.0` each give exactly 2 requests. The report records `usd_spent == 4.0`, cases 3 to 12 as `skipped_cost_cap`, and `usd_cap == RUN_USD_CAP`.
5. `tests/test_diagnose_eval.py` proves RESUME. Re-running over the criterion 3 deadline report calls only the `skipped_deadline` cases and carries `usd_spent`. A report whose `fixtures_sha` differs refuses, naming the delete road.
6. `tests/test_diagnose_eval.py` proves `verify` names each failed check for a report that is incomplete, is missing a case, has spend over the cap, or has an agreement that does not recompute.
7. The `python -c` command in `## Verification` exits 0: `eval.diagnose.RUN_USD_CAP == 5.0`.
8. `uv run pytest -q` exits 0 with no test removed or skipped, and `tests/test_eval_harness.py` passes unchanged.

## Verification
```
uv run python -c "import eval.diagnose as d; assert d.RUN_USD_CAP == 5.0 and len(d.load_cases(d.ROOT / 'eval' / 'diagnose_fixtures')) == 12"
uv run pytest -q tests/test_diagnose_eval.py
uv run pytest -q tests/test_eval_harness.py tests/test_diagnose.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- The harness renders diagnosis prompts, or defines the verdict vocabulary, anywhere but through the imports from `chupa/stages.py` and `chupa/artifacts.py`.
- A call runs when its projected spend exceeds the cap, or after the deadline.
- A killed or skipped case is dropped from the report rather than recorded.
- Any test or command spends real model money.
- `eval/diagnose_report.json` is committed.
- The diff touches a file outside the fence.

## Time budget
- expected: 75m
- stuck: 150m
