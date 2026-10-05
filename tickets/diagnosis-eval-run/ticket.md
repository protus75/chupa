---
state: confirmed
source: seed
priority: P2
kind: chore
agent_tier: medium
agent_effort: medium
---

## Depends on
- diagnosis-eval-harness

## Context
- config.yaml

## Plan contract
- 19.L
- 19.P2

## Goal / Why
`eval/diagnose_report.json` exists on main: a complete diagnosis real-model eval report, machine-produced by executing the already-merged harness (`uv run python -m eval.diagnose run`) against the configured providers under the harness's flat per-run USD cap (`RUN_USD_CAP`, 5.00). It records the agreement rate between the production diagnosis call's verdicts and the committed corpus's expected verdicts. `uv run python -m eval.diagnose verify` accepts it.

Why: 19.P2 ships the diagnosis eval as two chained deliverables, and this is the spend half. It EXECUTES the merged harness and writes no code, so the paid run is a reviewed, bounded execution of machinery `diagnosis-eval-harness` already proved under the fake LLM: cost cap, hard deadline, resume. The `diagnose` surface routes through `config.yaml`'s `review` row by inheritance, so no config edit is needed.

## Scope in / Scope out
- In: from the worktree root, run `uv run python -m eval.diagnose run` in the FOREGROUND until it returns. The harness writes the report after every case and stops itself at its deadline. If the command ends with `complete` false (some cases `skipped_deadline`), or the process is killed, run the same command again: it resumes only the unfinished cases and carries the spend toward the same cap. Repeat until `complete` is true.
- In: commit exactly `eval/diagnose_report.json` as the harness wrote it.
- Out: editing the report by hand, or deleting and re-running it to obtain a different agreement rate. The recorded rate is the result, whatever it is.
- Out: any change to `eval/diagnose.py`, `eval/diagnose_fixtures/`, `specs/**`, `chupa/**`, tests, or `config.yaml`. If the harness cannot run (a refusal, a defect, a provider setup error), the outcome is `premise_failed` naming the failing command and its output, never a code fix in this diff.

## Scope fence
- eval/diagnose_report.json

## Acceptance criteria
1. `eval/diagnose_report.json` is committed on the branch, and `uv run python -m eval.diagnose verify` exits 0 over it: complete, every committed case present, `fixtures_sha` and `spec_version` current, `usd_spent` at most `RUN_USD_CAP`, and agreement recomputing from the cases.
2. The `python -c` command in `## Verification` exits 0: every case in `eval/diagnose_report.json` that is neither `skipped_cost_cap` nor `skipped_deadline` names a non-null `provider` and `model` other than `fake`, so the report came from a real-model run.
3. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run python -m eval.diagnose verify
uv run python -c "import json; r = json.load(open('eval/diagnose_report.json')); ran = [c for c in r['cases'] if not c['outcome'].startswith('skipped_')]; assert ran and all(c['provider'] and c['model'] and c['provider'] != 'fake' for c in ran)"
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- The report is hand-written or hand-edited rather than produced by the harness.
- Any file other than `eval/diagnose_report.json` changes.
- The run spends past `RUN_USD_CAP`.
- The diff touches a file outside the fence.

## Time budget
- expected: 60m
- stuck: 120m
