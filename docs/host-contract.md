# Host contract

The installed engine owns process; the host owns project content, tickets and
configuration. See the [host run guide](host-running.md) for invocation and operation.
This document describes the merged configuration and interfaces.
Report intake and cutover below are pending Phase 6 consumer contracts, not an
activation instruction. Foreign process-state adoption is excluded.

## Copyable configuration

Copy this YAML to `config.yaml` at the host checkout root and edit the models,
paths, package and checks for your host. `--config <path>` selects another file;
otherwise the invocation cwd selects `config.yaml`. The loader uses PyYAML
`safe_load`, refuses unknown fields and validates strict types (paths accept
strings). These check commands and merge strategies are host choices, not engine
presets. Loading this example does not run its commands or contact a provider.

```yaml host-example
schema_version: 1
state_dir: .chupa
providers:
  - name: codex
    kind: cli
    package: '@openai/codex' # pnpm package used by provider preflight
    # auth: OPENAI_API_KEY # environment-variable NAME; omit for ambient CLI login
    models_by_tier: {low: host-model, medium: host-model, high: host-model, max: host-model}
    limits: {concurrency: 1, est_cost_per_call_usd: 0.25}
routing:
  - {tier: medium, surface: review, candidates: [{provider: codex}]}
  - {tier: medium, surface: implement, candidates: [{provider: codex, model: host-model}]}
review:
  autofix: # matching changed files are appended to each argv
    - {code: host-fix, argv: [uv, run, ruff, format], files: ["*.py"]}
  mechanical: # argv lists, never shell commands; choose your host's checks
    - {code: host-test, argv: [uv, run, pytest, -q], trigger: always, severity: hard}
    - {code: host-style, argv: [uv, run, ruff, check], trigger: [src/], severity: soft}
  surfaces: [] # host review surfaces are not supported yet
  trigger_map: {src/: [scope_fence]} # engine gate codes only; host entries use their own triggers
  gate_severity: {scope_fence: hard} # merge overrides; engine defaults are all hard
merge:
  safety_checks: [host-test] # each code must resolve to exactly one hard mechanical entry
  strategies: # choose paths suitable for your host
    - {paths: [uv.lock], strategy: regenerate, argv: [uv, lock]}
    - {paths: [CHANGELOG.md], strategy: union}
engine_plane_safety_inventory: [config.yaml, chupa/specs/, chupa/gates.py]
# worktree_root: .chupa/worktrees
# report_inbox: reports
# notify: [notify-send, chupa]
# context_files: [docs/architecture.md]
```

## VS Code extension

The `vscode-chupa` extension activates in a workspace containing `tickets/` and uses the first such folder. Set the resource-scoped `chupa.command` array to the host invocation, for example `["scripts/chupa"]`; its default is `["uv", "run", "python", "-m", "chupa"]`. The extension calls `snapshot` for its read-only view and watches the returned state directory. `chupa watch [--once]` provides the same host observation as text. Both verbs work while the engine holds its lock.

## Python host test setup

Merge this block into the example configuration, replacing the package placeholder in the
unit command with your Python package name.

```yaml python-host
review:
  autofix:
    - {code: ruff-fix, argv: [uv, run, ruff, check, --fix, --exit-zero], files: ["*.py"]}
    - {code: ruff-format, argv: [uv, run, ruff, format], files: ["*.py"]}
  mechanical:
    - code: unit
      argv: [uv, run, python, -m, chupa, covgate, --, python, -m, pytest, tests/unit, -p, chupa.testguard, -p, chupa.testreport, --chupa-results, .chupa/results/unit.json, --cov=<package>, --cov-branch, --cov-context=test, --cov-report=json:coverage.json, -n, auto]
      trigger: always
      severity: hard
      results: .chupa/results/unit.json
      coverage: coverage.json
    - code: integration
      argv: [uv, run, python, -m, pytest, tests/integration, -p, chupa.testreport, --chupa-results, .chupa/results/integration.json, -n, auto]
      trigger: always
      severity: hard
      results: .chupa/results/integration.json
    - {code: lint, argv: [uv, run, ruff, check, .], trigger: always, severity: hard}
    - {code: format, argv: [uv, run, ruff, format, --check, .], trigger: always, severity: hard}
merge:
  safety_checks: [unit]
engine_plane_safety_inventory: [config.yaml, test-gate.toml]
```

Create `test-gate.toml` at the host root:

```toml test-gate
[coverage]
default = 90
# [coverage.packages]
# "src/example" = 95
# [coverage.files]
# "src/example/core.py" = 100

[unit]
budget_seconds = 60
```

Add dev dependencies `chupa`, `pytest`, `pytest-cov`, `pytest-xdist`, and `ruff`.
In `pyproject.toml`, set `[tool.coverage.run]` `core = "ctrace"` and
`[tool.coverage.json]` `show_contexts = true`: Python 3.14's default `sysmon` core drops
per-test contexts. Gitignore `coverage.json` and `.chupa/`.

Covgate runs unit tests and then gates their coverage; its base rerun measures the base's own
coverage. Whole-repo `lint` and `format` also fail at the merge base when main drifts, and
Check files that as `base_red` for a fix ticket. Listing `test-gate.toml` in the safety
inventory sends a ticket that would lower a threshold to a human.

## Complete field inventory

Each row names a model and every accepted field. `required` means no shipped
default; `unset` means omit the key, never write null. Nested blocks retain their
own defaults when partially supplied. Config defaults shown as objects are the
entire default block. This inventory follows `chupa/config.py`.

```yaml config-fields
Config:
  required: [schema_version, state_dir, providers, routing, review, merge, engine_plane_safety_inventory]
  defaults:
    worktree_root: unset
    routing_default_tier: medium
    scheduler: {max_unmerged: 2}
    caps: {diagnosis: 3, retry: 3, premise_bounce: 1, infra: 3, attempts: 5, quarantine: 5, poison: 2}
    circuit_breaker: {k: 3, cooldown_minutes: 10}
    drain: {max_runtime_hours: 12, max_ticket_minutes: 90}
    retro: {enabled: true, every_merges: 25, every_days: 7, spike_count: 5}
    box_policy: {failure_report: confirmed, retro_finding: confirmed, override_report: draft, suggestion: draft, bug_report_self_diagnosed: confirmed, bug_report_player_repro: confirmed, bug_report_player_no_repro: draft}
    notify: unset
    report_inbox: unset
    context_files: []
    ask_notes: unset
Provider:
  required: [name, kind, models_by_tier, limits]
  defaults: {auth: unset, package: unset}
ModelsByTier:
  required: [low, medium, high, max]
  defaults: {}
Limits:
  required: [concurrency]
  defaults: {est_cost_per_call_usd: unset, quota_window_minutes: 60}
Route:
  required: [tier, surface, candidates]
  defaults: {}
Candidate:
  required: [provider]
  defaults: {model: unset}
Review:
  required: []
  defaults: {coverage_map: unset, autofix: [], mechanical: [], surfaces: [], trigger_map: {}, gate_severity: {}}
CoverageMap:
  required: [argv, report]
  defaults: {}
  report: non-blank worktree-relative path without ..
AutofixCommand:
  required: [code, argv, files]
  defaults: {}
MechanicalCheck:
  required: [code, argv, trigger, severity]
  defaults: {results: unset, coverage: unset}
ReviewSurface:
  required: [name, trigger, rules_doc, severity]
  defaults: {}
Merge:
  required: []
  defaults: {safety_checks: [], strategies: []}
RegenerateStrategy:
  required: [paths, strategy, argv]
  defaults: {}
UnionStrategy:
  required: [paths, strategy]
  defaults: {}
Scheduler:
  required: []
  defaults: {max_unmerged: 2}
Caps:
  required: []
  defaults: {diagnosis: 3, retry: 3, premise_bounce: 1, infra: 3, attempts: 5, quarantine: 5, poison: 2}
CircuitBreaker:
  required: []
  defaults: {k: 3, cooldown_minutes: 10}
Drain:
  required: []
  defaults: {max_runtime_hours: 12, max_ticket_minutes: 90}
Retro:
  required: []
  defaults: {enabled: true, every_merges: 25, every_days: 7, spike_count: 5}
```

```yaml config-values
tier: [low, medium, high, max]
severity: [hard, soft]
kind: [api, cli]
trigger: [always, path-prefix-list]
strategy: [regenerate, union]
start_state: [draft, confirmed]
box_row: [failure_report, retro_finding, override_report, suggestion, bug_report_self_diagnosed, bug_report_player_repro, bug_report_player_no_repro]
```

`schema_version` must be the integer 1, not a boolean or string. `kind: api`
is currently refused: use `cli`; Implement requires a CLI even when API support
eventually ships. Every CLI requires a nonempty `package` despite its unset model
default. Shipped runtime adapters are `claude` and `codex`; the loader accepts
other names but provider setup refuses names without an adapter. `auth` names an
environment variable, never a literal secret. Codex reports no cost and requires
`est_cost_per_call_usd` at adapter setup; Claude can report actual cost. Estimates
are nonnegative, count fields are integers at least 1, and retry must not exceed
diagnosis. Providers, routing, route candidates, argv and strategy paths are
nonempty lists where declared. Notify requires a nonblank executable and
NUL-free strings.

Candidates name declared providers and are ordered primary-until-pressure;
absent `model` selects `models_by_tier[tier]`. Non-review surfaces fall back to
the review routing row. Surface names and host check codes are strings; engine
gate overrides use engine codes. `trigger` is `always` or a path-prefix list.
Config load refuses a declared `review.surfaces` entry; remove the entries because
host review surfaces are not supported yet.
Regenerate requires argv; union accepts no argv and only resolves append-only
conflicts. A conflict path must match exactly one strategy, and regenerated
paths must be outside the ticket fence; otherwise resolve through Rework with a
new approval.

Set `ask_notes` to add host guidance to `prompt` operator prompts; it is appended as a quoted `host_notes` data block.

Relative `state_dir`, explicit `worktree_root` and `report_inbox` resolve against
the selected config file's parent; absolute paths remain absolute. Absent
worktree_root becomes `<state_dir>/worktrees`. `context_files` and `rules_doc`
remain Path values as written at load time; use host-relative content paths.
An absent `box_policy` row takes its table default. Every explicit null,
including nested values and list items, is refused with its dotted key: omit
the key for a default or supply a value. Unknown keys require correcting the
selected config rather than silently accepting a future schema.

## Version migration

Newer versions refuse with a road to upgrade chupa; older versions name
`chupa migrate-config`. The only prior schema is explicit integer version 0;
missing version is a missing-required-key refusal, never inferred as 0.
`chupa migrate-config` selects the same config path, changes only the version
scalar from 0 to 1, and keeps all other bytes (comments, BOM and line endings).
It validates the full candidate with the real loader before any write, writes
the original bytes to adjacent `config.yaml.bak` (selected filename plus `.bak`),
then performs one atomic config replacement through the filesystem seam.
An existing backup is replaced. Current version is a validated byte-identical
no-op with no backup write. Missing file, missing/non-integer/negative version,
newer version, duplicate or aliased version-0 scalars, invalid YAML or invalid
candidate refuse without writes. Create/select the file, supply the explicit
integer, repair the named key and retry migrate-config, or upgrade for a newer
schema. Every future version bump must ship its migration step.

## Managed conduct and ticket ownership

Engine-owned `<!-- chupa:core begin -->` and `<!-- chupa:core end -->` lines
delimit the managed conduct block; the remainder is project-owned content.
The block carries only process rules that hold for every host; codebase rules belong in the project-owned remainder.
Engine process wins over host content. Do not hand-edit the core: `chupa core`
inserts or refreshes it, then commit the routed files. Routed candidates select
CLAUDE.md for provider name `claude`, AGENTS.md otherwise, deduplicated;
unrouted provider declarations do not select files.
First adoption with zero marker-like text inserts the block before every
original byte. Refresh preserves prefix and suffix bytes without decoding them.
Partial, duplicate, reversed, inline or stray marker text refuses; repair to
exactly one complete begin line followed by one complete end line, retain
project content outside it and escape stray marker text, then retry core.
Refresh inspects the entire selection before writing any file. Core drift
requires `chupa core`; uncommitted routed bytes must be committed or restored.
Project remainder rules attempting to override engine process refuse: move
them to the engine template or rewrite as project-content rules.

Ticket frontmatter policy is additive-only, but today's parser is closed;
there is no frontmatter schema migration mechanism. This is the full accepted
list from `chupa/tickets.py::Frontmatter`:

```yaml ticket-fields
required: [state, source, priority, kind]
defaults: {agent_tier: medium, agent_effort: medium, gate_bypass: []}
```

State is `draft | confirmed | rejected | merged`; priority `P0 | P1 | P2 | P3`;
kind `bug | feature | chore`; tier and effort `low | medium | high | max`.
Source is `human`, historical `seed` or `box:<class>` matching `box:[a-z][a-z0-9_]*`.
Each gate_bypass has only nonblank `code` (an engine gate code) and `reason`.
Put ordering in Depends on and priority, not extra metadata. New human intake
stamps source human and confirms; machine sources belong to engine authoring.

## Checks and injectable seams

`Gate.check(artifact, workspace) -> GateReport` is synchronous; the report has
code, `pass | fail` verdict, findings (default []), autofix_applied (default
false). Failure requires findings with paved roads; code must match the gate.
Severity belongs to the runner, with all engine codes hard at merge unless
`review.gate_severity` overrides them.

Check first runs `review.autofix` entries in order on existing changed files outside `tickets/`
that match the entry's required nonempty `files` allowlist of fnmatch patterns, appending those
paths to its argv. An entry with no matching files is skipped. If their bytes change, it commits them as
`chupa(<stem>): autofix` before Verification and gates. On failure it stops, restores
the listed files to the branch head, records a hard failure and continues Check.

Check runs every triggered `review.mechanical` entry in config order after engine gates.
An always trigger matches every change; a path prefix matches an equal path or a descendant.
Hard failures block Check, soft failures are recorded, and failures also red at the merge
base are filed as pre-existing and excluded from the verdict and retry findings. Inline
merge reruns triggered hard entries on the rebased candidate. Both and
`MergeQueue.host_checks(ticket, *, attempt, safety)` use the same runner for argv
in the candidate worktree with explicit child env and the ticket stuck timeout.
rc 0 passes; nonzero, timeout and missing executable fail with repair roads.
It consumes exit status, not optional structured findings from stdout. Output
is spooled to `check/host-NN.txt`, `merge/host-NN.txt`,
`merge-safety/host-NN.txt` or `merge-integration/host-NN.txt`;
returned tails are redacted and captured output is scrubbed at the spool seam.
Every safety_checks code must resolve to exactly one hard mechanical entry;
invalid designations fail before commands. Integration selects only always/hard
entries. Host surfaces use their own triggers; trigger_map concerns engine gates.

An entry may set `results` to a worktree-relative file written with `-p chupa.testreport
--chupa-results <path>`. Check removes it before each run and reads fresh results. A failed
command with failed tests runs once more; failed-then-passed tests in changed files block as
flaky, while unedited flakes enter quarantine unless its cap is full. Failed tests block unless
quarantined and unedited. A passing quarantined test is released after its report resolves to a
merged fix ticket. Missing or invalid results after a successful run or rerun fail the entry.
An entry with `results` may also declare a worktree-relative `coverage` report. A flaky test is edited if its test file changed or its coverage context appears on a changed line (or a line adjacent to a pure deletion). Generate coverage.py JSON with `pytest-cov --cov-context=test`, `[tool.coverage.json] show_contexts = true`, and `[tool.coverage.run] core = "ctrace"`. When a flaky test needs classification, missing or invalid coverage contexts fail the entry. Merge-time checks continue to use exit status alone.

The minimal seams in `chupa/seams.py` are:

- `Clock = Callable[[], datetime]` and `Sleep = Callable[[float], Awaitable[None]]`:
  timed work races injected sleep to a clock-derived deadline; tests advance
  deadlines without wall-clock waiting.
- `async run(argv, *, cwd, env, timeout, stdin_path=None) -> (rc, out, err)`:
  explicit required env and timeout (None only for the unbounded self-upgrade
  handoff, which inherits stdio and returns empty out/err). Each child uses
  start_new_session; timeout and outer cancellation use the same group kill and
  wait helper. `kill_group(pgid)` is synchronous SIGKILL signal-not-reap; run
  owns reaping. `on_spawn` publishes the pgid, provider call return clears it.
  `on_stdout_line` includes the EOF tail; consumer failure stops delivery but
  drains capture, attaches process_capture and raises after reap. Unwind retains
  timeout/cancellation type. ExecutableNotFound names the missing binary: install
  it or fix child PATH. Prompts are spooled files connected by stdin_path, never
  argv elements. No stdin_path means devnull.
- `write(path, data)` fsyncs a temporary file and atomically replaces the target;
  `replace(src, dst)` atomically replaces; `publish(path, data)` durably publishes
  without overwriting an existing destination.
- `async notify(argv) -> dict[str, str | int]` validates nonempty argv, nonblank
  executable and NUL-free strings; CommandNotifications scrubs output and
  returns rc/stdout/stderr on success. Nonzero, timeout, missing executable or
  OS errors raise NotificationFailed: fix argv/PATH and retry pending evidence.

Non-LLM children inherit the parent environment minus every configured provider
key; only the serving LLM gets its own key. Active-work, notification and handoff
executors are separate; abort targets the executor that spawned active work.

## Instance custody

ONE instance writes a host repo line. Stable is a PyPI release installed with `uv tool install chupa==<version>`; dev uses its own disposable checkout, worktree root and state dir,
with checkpoint push disabled. Instances share only remotes. Upgrade or roll back by reinstalling the desired version and restarting. A git-checkout engine running `serve`
restarts itself when its `chupa/` tree changes.
`<state_dir>/chupa.lock` uses advisory flock before writes and records instance_id,
pid, host, state_dir and started_at for diagnostics only. Kernel release on
process death governs correctness, never stale-pid adoption. On LockHeld wait
for or stop the holder; never delete the lockfile. Child descriptors do not pin it.
State dir owns journal, box queue, quarantine ledgers, attempt spools, engine
log and heartbeat. Decisions and tombstones are committed under
`tickets/decisions/`, so dedup memory travels with the repo. Config is re-read at
each dispatch cycle: watcher/debounce in daemon, re-parsing in scaffold verbs;
routing, severity and ceiling edits take effect without restart.

## Pending report-inbox contract

The optional report_inbox is a directory for small host JSON reports, consumed
by sequential triage into the same durable Suggestion Box. Version-1 reports
have exactly these fields:

```yaml report-fields
required: [schema_version, origin, summary, app_commit, app_version]
defaults: {implicated_paths: [], evidence: {replay: null, log: null}}
self_diagnosed_required: [game_slug, anomaly_code, location]
origins: [self_diagnosed, player]
replay_max_bytes: 1048576
log_max_bytes: 65536
```

schema_version is integer 1; summary, app_commit/app_version and self-diagnosed
fields are nonblank. Player reports omit game_slug, anomaly_code and location.
Unknown report/evidence keys refuse; version 0 accepts the same shape with only
its version scalar changed. Evidence replay/log are nullable repo-relative
paths (unlike config's null refusal). implicated_paths are repo-relative paths.
Self-diagnosed dedup uses the exact tuple (game_slug, anomaly_code, location,
app_version), preserving digits and path bytes; player text uses sequential
semantic dedup. The producer supplies no signature field.

Replay JSON contains initial_state and an ordered actions list. Read metadata-first:
replay at most 1 MiB, log at most 64 KiB, accepting exact boundaries; recheck
copied bytes. Missing, escaping, non-regular or over-limit files refuse before
message recording. Repair schema/path/evidence and retry; malformed reports
stay unconsumed with diagnostics. Box copies report and bounded evidence into
durable box custody before message recording, never referring back to mutable
inbox evidence. Mark consumed only after durable enqueue or dedup, with a
stable arrival identity on retries. has_repro means a validated replay was
copied. Triage copies custody evidence into the authored ticket's evidence/
directory; report -> replay -> permanent regression fixture. Report text is
untrusted data at every hop: triage writes its own summary, raw text never enters
ticket prose and later prompts see only delimited data. Evidence is quoted,
never executed outside the deterministic replay harness. app_commit attribution
is a later consumer's judgment, not proof of an introducing commit.

## Pending cutover contract

1. Unattended bootstrap self-build continues through Phase 6 under drain's safety
   envelope; serve and drain both merge green candidates without operator confirm.
2. Supervised fixture wiring uses a committed fixture host in a disposable copy,
   scripted CLI and machine-actor confirms against its own subprocess. It proves
   the pre-cutover loop; it does not constitute live-host acceptance.
3. Commit the GO-grade baseline report and Author graph. The baseline scores at
   least 50 planted defects and 15 clean controls, catch rate at least 0.85 and
   false-snag rate at most 0.15. An incomplete/cap-exhausted report is NO_GO;
   commit measured partial evidence and perform a bounded rerun. The operator's
   Author-graph judgment is required even above those mechanical floors.
4. Operator-recorded GO follows that committed baseline and judgment; the report
   embeds its verdict signal's journal identity. GO binds to current resolved
   review/author routing and spec-major identity. GO governs only Author starting
   state. Serve merges green candidates without an operator confirm.
5. NO_GO or no declared host waits at cutover. A declared live host is onboarded
   only after GO and operator judgment; start serve on host work and perform
   live-host acceptance separately. A fixture report cannot substitute for it.

This document adds no report consumer, GO writer or runtime activation.
