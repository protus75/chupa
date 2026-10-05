---
state: confirmed
source: seed
priority: P2
kind: feature
agent_tier: medium
agent_effort: medium
---

## Depends on
- invariant-auditor

## Context
- chupa/artifacts.py
- chupa/runner.py
- tests/test_stages.py
- tests/test_drain.py

## On-demand
- chupa/stages.py

## Plan contract
- 19.L
- 19.P2
- section 10
- section 15

## Goal / Why
The shakeout battery has its report lane: the closed `shakeout-report.json` schema, its registration as a KNOWN artifact that ONLY the Check-stage lift may carry to main, the canonical writer, the fake-driven bench, and the group runner with the double gate. Every later battery group adds members to this runner, and its own Check run machine-produces the cumulative report into its OUTBOX.

Why: the Phase 2 exit reads "battery green including every named member" from a committed report (19.P2 exit reads). A report a model could hand-write, or that one deliverable both registers and commits, is the false-green shape 19.L's EXIT-READ CLOSURE and CUSTODY rules refuse. This deliverable is the MACHINERY (schema, registration, writer, runner). The group runs are the PRODUCERS, strictly after it merges.

Owners (19.P2 NAMES, 19.L EXIT-READ CLOSURE): `chupa/artifacts.py` owns the schema. `chupa/stages.py` / `tests/test_stages.py` own the KNOWN registration and the ONE stage-terminal lift path. `eval/shakeout/bench.py` owns the public bench and its `configure` seam (19.P2 BENCH SEAM). `eval/shakeout/run.py` owns the member registry, the runner, the double gate, and the canonical writer. `tests/test_shakeout.py` is the battery suite. `chupa/audit.py` is called, never changed.

## Scope in / Scope out
- In: `chupa/artifacts.py`:
  - `SHAKEOUT_REPORT = "shakeout-report.json"`.
  - `ShakeoutEntry`, closed: `member` (snake-case id), `group`, `planted_fault`, `expected`, `observed` (each non-blank), `producing_run` (`<bench stem>/<run seq>`), `auditor` (list of violation lines), `green` (bool). A validator refuses `green` unless `observed == expected` and `auditor` is empty, and refuses `green: false` when both hold.
  - `ShakeoutReport(Artifact)`: `entries`, with member ids unique.
- In: `chupa/stages.py`:
  - `KNOWN_ARTIFACTS: Mapping[str, type[BaseModel]] = {SHAKEOUT_REPORT: ShakeoutReport}`.
  - `lift_outbox` validates every outbox file whose basename is registered BEFORE anything is written, and raises `ArtifactInvalid(path, error)` on a schema failure. A registered artifact is lifted ONLY by the Check-stage lift (kind `checks`). Every other lift leaves it out.
  - `check` deletes registered artifacts from the outbox BEFORE running Verification, so a stale or agent-written copy never lifts. An `ArtifactInvalid` at its lift makes the Check `gate_failed` with one finding code `verification` (paved road: produce the report only through `eval.shakeout.run`).
  - REPORT REQUIRED (19.P2): when a `## Verification` command names `tickets/<stem>/<registered name>`, the Check fails `gate_failed` with finding code `verification` unless that artifact is in the outbox after Verification, regardless of any per-command attribution (paved road: make the named runner exit 0 so it writes the report).
- In: `eval/shakeout/bench.py`: `Bench`, the fake-driven production composition (section 15 rung 4). It holds a disposable git repo under a given root with a minimal config and `.gitignore`d state dir, the production journal, an injectable advancing clock, the real process seam and git adapter, the filesystem seam, a child environment mapping, a report sink capturing the drain report, and a scripted model seam: a FakeLLM by default, or any `LLM` the member passes at construction (a production `ProviderLLM` over a scripted process seam included).
  - It exposes `add_ticket(stem, text)`, `script(items)`, `drain() -> Report`, `journal`, and `segments()`, all running the production `runner.bind` pipeline and `drain.drain`.
  - `Bench.configure(parsed_config)` rebuilds the production runner, drain, redactor, log, and pipeline factory around a replacement config whose `state_dir` resolves to the existing bench state dir, preserving the repo, journal, clock, process, filesystem, git adapter, environment, report sink, and scripted-model seams. Members select fixtures only through it and never assign private bench fields.
- In: `eval/shakeout/run.py`:
  - `Member`, a frozen dataclass: `id`, `group`, `planted_fault`, `expected`, `run: Callable[[Bench], Awaitable[Observation]]`. `Observation`: `observed`, `producing_run`.
  - `GROUPS: tuple[str, ...] = ()`, the closed ordered group list later seeds append to. Each group's members live in `eval/shakeout/<group>.py` as `MEMBERS: tuple[Member, ...]`, loaded by group name.
  - `run_member(member, root) -> ShakeoutEntry`: a fresh `Bench` under `root/<member id>`, the member's run, then `audit(bench.segments())` rendered one line per violation.
  - `produce(group, prior: ShakeoutReport | None, root) -> ShakeoutReport`, the DOUBLE GATE: the prior report must hold every member of every group before `group` in `GROUPS`; each prior entry's member is re-run and must come back green with the same `observed`; then `group`'s own members run and each must be green. Any failure raises `ShakeoutRefused` naming the member, and no report is produced.
  - `write_report(path, report)`, the ONE writer: atomic, through the filesystem seam, `model_dump_json(indent=2)` plus a newline. `produced_by_spec_version` is the engine constant `SHAKEOUT_SPEC_VERSION = 1` and `produced_at_sha` is the checkout's HEAD.
  - `python -m eval.shakeout.run --group <g> [--prior <path>] --out <path>` runs `produce` in a temp root and writes the report only on success. It exits 0 on success, 1 on `ShakeoutRefused`, and 2 on an unknown group.
- Out: every battery member (the group seeds), any `chupa/audit.py` change, run-lane admission (Phase 3), and committing any report from this ticket.

## Scope fence
- chupa/artifacts.py
- chupa/stages.py
- tests/test_stages.py
- eval/shakeout/
- tests/test_shakeout.py

## Acceptance criteria
1. `tests/test_stages.py` proves a Check whose Verification writes a valid `shakeout-report.json` into the outbox lifts it in the `chupa(<stem>): checks` commit, a schema-invalid one makes the Check `gate_failed` and commits neither file, and the implement-terminal lift leaves a registered artifact unlifted.
2. `tests/test_stages.py` proves a report left in the outbox before Check is deleted before Verification runs, so a Verification that writes nothing lifts no report, and that a Check whose Verification names `tickets/<stem>/shakeout-report.json` but leaves no report fails `verification` even when every command is otherwise excused.
3. `tests/test_shakeout.py` registers two test-local members through the runner's group loading and proves `produce` refuses a prior report missing an earlier group's member, refuses when a re-run prior member's `observed` differs, and returns the cumulative report otherwise.
4. `tests/test_shakeout.py` proves a member whose bench journal carries a planted double terminal comes back `green: false` with a `one_terminal_per_run` auditor line, and that `ShakeoutEntry` refuses `green: true` with a non-empty `auditor`.
5. `tests/test_shakeout.py` proves `Bench.configure` keeps the journal, clock, repo, and scripted model while changing a config cap, and that the `python -m eval.shakeout.run --group nope --out x.json` command exits 2.
6. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run pytest -q tests/test_shakeout.py tests/test_stages.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- A registered report can reach main through any lift but the Check-stage lift, or without passing its schema.
- A Check passes when its Verification names a registered report and none is in the outbox.
- A second report writer, or a second lift path, exists.
- `produce` writes a report when any prior or own member is not green.
- The diff touches a file outside the fence.

## Time budget
- expected: 90m
- stuck: 180m
