# Gemini provider and graphics ticket kind: refactor plan

Add Google's Gemini CLI as a fourth provider beside `claude`, `codex`, and `qwen` (Ollama), and add a `graphics` ticket kind for UI, webpage, image, and flowchart work, with the authoring rules, checks, and review it needs.

## Status

Draft plan. Nothing in it is in effect and no ticket is authored. Written 2026-11-13 at commit `c7f8d6c1`.

## Part A: Gemini CLI provider

### Current state

- `ADAPTERS` in `chupa/providers.py` ships `claude`, `codex`, and `qwen`. A provider named `gemini` is refused at setup: `no shipped cli adapter`.
- `QwenAdapter` subclasses `ClaudeAdapter` because Qwen Code emits Claude's stream format. Qwen Code is a fork of Gemini CLI, but Gemini CLI's own `stream-json` is a different format, so Gemini cannot reuse `ClaudeAdapter.parse`.
- `chupa/watchdog.py` reads two event shapes: Claude's (`assistant` `tool_use` blocks, which qwen shares) and Codex's (`item.*`). It has no Gemini branch.
- `chupa/observe.py` `live_call` labels claude, codex, and qwen processes only.

### Config: no schema change

`Provider` in `chupa/config.py` already carries every field Gemini needs:

| Field | Gemini value |
|---|---|
| `kind` | `cli` |
| `package` | `@google/gemini-cli` (the preflight's latest-release check works unchanged) |
| `auth` | unset for a Google OAuth login (ambient, like claude and codex), or `GEMINI_API_KEY` for a key. `child_env` already passes a key only to its own provider. |
| `base_url` | unset (refused, since `uses_base_url` stays false) |
| `models_by_tier` | `OPERATOR-SETS-THIS` until the operator picks models; the placeholder refusal already covers this |
| `limits.est_cost_per_call_usd` | required: the stream reports tokens, never USD |

Config support is therefore a setup guide plus a routing example. Routing Gemini in this repo's `config.yaml` stays an operator edit after setup, as it was for qwen.

Example declaration for the guide:

```yaml
- name: gemini
  kind: cli
  package: "@google/gemini-cli"
  models_by_tier: {low: OPERATOR-SETS-THIS, medium: OPERATOR-SETS-THIS, high: OPERATOR-SETS-THIS, max: OPERATOR-SETS-THIS}
  limits: {concurrency: 1, est_cost_per_call_usd: 0.50}
```

Out of scope: Vertex AI auth, which needs several env vars (`GOOGLE_API_KEY`, `GOOGLE_GENAI_USE_VERTEXAI`, project, location) while `auth` names one.

### Target design

- **`GeminiAdapter(CliAdapter)`** with its own `argv` and `parse`:
  - argv: `gemini -m <model> --output-format stream-json` plus the write grant; the prompt arrives on stdin, as for every adapter.
  - parse: read the `stream-json` events (`init`, `message`, `tool_use`, `tool_result`, `error`, `result`). The terminal `result` event carries the outcome and token stats. Raise `ValueError` when there is no successful `result`.
  - `reports_cost = False`, `AUTH_MARKERS`, and a `LOGIN_ROAD` naming `chupa/docs/host-gemini.md` and `chupa drain`.
- **Write grant, fail closed.** Ship two settings files in the package and select one per call through `GEMINI_CLI_SYSTEM_SETTINGS_PATH`, the same mechanism `qwen-settings.json` uses through `QWEN_CODE_SYSTEM_SETTINGS_PATH`:
  - `gemini-readonly.json`: a `tools.core` allowlist of the read tools only (read file, glob, search, list directory), matching Claude's `--tools Read Grep Glob LS`.
  - `gemini-write.json`: full tools, with `--approval-mode yolo` on the argv.
  - Both set `context.fileName` to `AGENTS.md`.
  - System settings are the top-precedence layer, so nothing in `~/.gemini/settings.json` or a workspace `.gemini/settings.json` can widen the grant or move the conduct file. The operator never edits a file in their home directory.
- **Conduct file.** Gemini reads `AGENTS.md`, the curated subset for non-Claude CLIs. `routed_conduct_paths` already selects `AGENTS.md` for any provider not named `claude` or `qwen`, so no code change; add a test.
- **Failure classes.** Extend `FAILURE_MARKERS` with Gemini's quota and rate wording (for example `RESOURCE_EXHAUSTED`, `quota exceeded`, 429). It is a shared allowlist, so the additions must not misclassify claude or codex output; the existing classifier tests cover that.
- **Watchdog.** A third branch in `chupa/watchdog.py` for Gemini's `tool_use` and `tool_result` ids and `result` stats, so stall detection and token metering work.
- **Live view.** A `live_call` branch for the pnpm shim's `node .../@google/gemini-cli/...` process, labelled `gemini <model>`.
- **Guide.** New `chupa/docs/host-gemini.md`: what it is, install (`pnpm add -g @google/gemini-cli@latest`), log in or export `GEMINI_API_KEY`, declare it, `chupa probe gemini`, route it, limits (free-tier rate limits, `quota_window_minutes`). The `docs` verb lists it as a fifth guide.

### Prerequisite: hand test

The qwen ticket was decidable because a hand test with an empty `HOME` established its facts before authoring (rule: read before write). Gemini needs the same. Capture the output as the ticket's evidence. Establish:

1. The exact `result` event shape for success and failure, and where the reply text and token counts live.
2. The exit code of a failed turn, and whether a failure can exit 0 (codex does).
3. Whether a `tools.core` allowlist in the system settings file actually blocks writes and shell under headless mode, or whether `--approval-mode plan` (or default approval) is the read-only mode.
4. That `context.fileName` from the system settings file loads `AGENTS.md` from the working directory.
5. The auth-failure and quota wording on stderr or in `error` events.
6. The process argv the pnpm shim produces, for `live_call`.

No argv or parse in this plan is final until that test runs.

### Fence (ticket `gemini-provider`)

- `chupa/providers.py`
- `chupa/gemini-readonly.json` (new)
- `chupa/gemini-write.json` (new)
- `chupa/watchdog.py`
- `chupa/observe.py`
- `chupa/__main__.py` (docs verb tuple)
- `chupa/docs/host-gemini.md` (new)
- `chupa/docs/host-contract.md` (shipped adapter list, no-cost rule, conduct-file sentence)
- `docs/how-chupa-works.md` §8.1
- `README.md` (only if it lists the CLIs)
- `tests/unit/test_gemini_adapter.py` (new)
- `tests/unit/test_live_call.py`
- `tests/unit/test_docs_verb.py`
- `tests/integration/test_cli.py`
- `tests/integration/test_closed_sets.py` (`ADAPTERS`)
- the watchdog's unit test file

## Part B: `graphics` ticket kind

### Current state

- `kind` is the closed set `feature | bug | chore` (`chupa/tickets.py:59`). It is repeated in:
  - `chupa/__main__.py`: `--kind` choices and the kind check at line 771;
  - `chupa/stats.py:108`;
  - `chupa/author.py:245` (skeletons embedded in the Author prompt);
  - `tests/integration/test_closed_sets.py:342`;
  - the `CORE_TEMPLATE` rule text in `chupa/hostfiles.py` (`chupa new <stem> --kind feature|bug|chore`), and through `chupa core` the managed blocks in `CLAUDE.md` and `AGENTS.md`.
- `bug` is the precedent for a kind with its own machinery: an extra section (`## Regression`), a stdout protocol (`regression_result`), committed evidence files, and a Check rule that runs the command at head and at base.
- `## Context` accepts only UTF-8 text, so mockups and reference images have no place in a ticket today.
- Review is text-only: it sees `git diff main...<stem>`, where an image is `Binary files differ`. Nothing renders the output or looks at it.
- `host-authoring.md` requires every criterion to be "a check someone can run or a path someone can read, never a judgment word". Visual work has criteria that only an image can decide.
- `review.mechanical` already accepts a file-glob `trigger`, so a host can run a Markdown or Mermaid check on changed `*.md` and `*.mmd` files today.

### Scope of "graphics"

In: output rendered from code the agent writes: HTML/CSS pages, UI components, SVG, Mermaid or Graphviz flowcharts, and matplotlib-style charts.

Out (v1): AI-generated raster images. No routed CLI generates images headlessly in a way Check can verify. See decision 1.

### Target design

#### B1. Grammar and authoring (`graphics-kind`)

- `kind` gains `graphics`, with its own template.
- New section `## Render`, required on `graphics` and refused on every other kind, like `## Regression`:

  ````
  ## Render
  ```
  uv run python tests/render/home.py
  ```
  - artifact: .chupa/renders/home.png
  - reference: tickets/<stem>/reference/home-mock.png
  - carries: tests/render
  ````

  - The command produces the artifacts. It must name a path under a `carries:` prefix, which must be fenced.
  - `artifact:` names each output file the command writes. Artifacts live under a gitignored render directory and are never committed.
  - `reference:` names optional mockups or baselines, committed under `tickets/<stem>/reference/`.
- `chupa new <stem> --kind graphics [--reference FILE...]` copies the reference files the way `--evidence` copies bug evidence. Intake commits them with the ticket.
- Acceptance criteria come in two forms:
  - Mechanical criteria, checked by tests as today: text present, DOM selector exists, image dimensions, the Mermaid source parses, a contrast ratio.
  - Visual criteria, written `- visual: <artifact>: <observable>`. The observable is something you can see and answer yes or no: an element, a label, a position relative to another element, a colour token. Example: `- visual: home.png: the Save button sits right of Cancel, both on one row`. Never "looks clean" or "modern".
  - Lint enforces the structure (each `visual:` criterion names a declared artifact, and a graphics ticket has at least one mechanical criterion). The LLM requisition review checks that each one can be decided from the image alone. A lint rule cannot judge that, and a denylist of judgment words breaks the fail-closed rule.
- `chupa/docs/host-authoring.md` gains a **Graphics tickets** section, beside **Bug tickets**, covering:
  - the render command and its protocol;
  - artifacts and references;
  - the two criterion forms;
  - preferring a mechanical criterion wherever a test can decide it;
  - the Markdown and flowchart checks hosts declare in config (below).

#### B2. Check (`graphics-render-check`)

- Check runs the render command at the branch head. It prints exactly one JSON object, `{"render_result": "ok", "artifacts": [...]}`, and exits 0. Like `regression_result`, any other stdout, extra keys, or a disagreeing exit code is refused. `{"render_result": "error"}` means a missing prerequisite and never counts as success.
- The engine checks that the listed artifacts are exactly the declared ones, each exists, is non-empty, and has content matching its extension (PNG header, SVG/XML root, HTML).
- The artifacts are copied into the attempt directory (`tickets/<stem>/attempts/...`) so the visual reviewer and the operator can open them.
- The host owns the renderer: a Playwright screenshot script, `mmdc` for Mermaid, `dot` for Graphviz. The engine runs only the command, which keeps it pure Python with no browser dependency.
- Markdown and flowchart checking needs no engine change. A host declares it in `config.yaml`, for example:

  ```yaml
  - {code: mermaid, argv: [npx, mmdc, --validate], trigger: ["*.md", "*.mmd"], severity: hard}
  - {code: markdownlint, argv: [npx, markdownlint-cli2], trigger: ["*.md"], severity: soft}
  ```

  The guide documents this. Validate the exact argv when the guide is written.

#### B3. Visual review (`visual-review-surface`)

- New spec `chupa/specs/review_visual.md` and surface `review_visual`. It runs after the correctness review, on `graphics` tickets only, and is read-only.
- Inputs: the ticket, the artifact paths from B2, the reference paths, and the diff. The reviewer opens images with its read tool (Claude's Read and Gemini's file reader both take images).
- Output: one verdict per `visual:` criterion (`pass` or `fail`) with the observation that decided it, plus an overall `approve` / `snag` / `rma`, matching `review.md`. A gate refuses a reply that skips a criterion or names one not in the ticket.
- Routing needs no config change: `resolve()` falls back from an unrouted surface to the `review` row (`chupa/providers.py:104`). A host may add `{tier: ..., surface: review_visual, candidates: [{provider: gemini}]}`, which makes Gemini a second set of eyes alongside Claude's correctness review.

#### B4. Spec updates

- `chupa/specs/implement.md`: a graphics block. Run the render command, open your own artifacts, and compare them with the references and the visual criteria before committing. Never commit artifacts.
- `chupa/specs/requisition_review.md`: a graphics block. Each `visual:` criterion can be decided from the named artifact alone. Snag a criterion that needs taste or a reading of intent.
- `chupa/specs/author.md`: no text change. It embeds the skeletons, which gain `graphics` through `author.py`.
- Every bumped spec takes the next minor version above its version on main, and its test pin is fenced.

### Where each rule lives

| Rule | Home |
|---|---|
| What a graphics ticket contains and how criteria are written | `chupa/docs/host-authoring.md` (the one authoring source) |
| Ticket format (`## Render`, bullets, kind) | `chupa/tickets.py` |
| How the implementer and reviewers behave | `chupa/specs/implement.md`, `review_visual.md`, `requisition_review.md` |
| The `--kind` list in agent conduct | `CORE_TEMPLATE` in `chupa/hostfiles.py`, rendered by `chupa core` |
| Repo-only rules | none needed; `CLAUDE.md` and `AGENTS.md` outside the managed block are unchanged |

## Ticket breakdown

Future tickets. None are authored yet. Each is written with `chupa new`, then `chupa lint` until clean, then `chupa review` until approved.

| Order | Stem | Kind | Depends on | Notes |
|---|---|---|---|---|
| A0 | (hand test) | n/a | | Produces evidence for A1; not a ticket |
| A1 | `gemini-provider` | feature | none | Fence listed in Part A |
| B1 | `graphics-kind` | feature | none | Grammar, template, `--reference`, lint, kind lists, `CORE_TEMPLATE`, authoring guide, requisition spec |
| B2 | `graphics-render-check` | feature | `graphics-kind` | Render protocol and artifact checks at Check; implement spec block |
| B3 | `visual-review-surface` | feature | `graphics-render-check` | `review_visual` spec, stage, and gate |

Part A and Part B are independent. Within B each ticket needs the previous one's merged code, so `Depends on` is correct there. A1 is useful to B3 only as an optional routing target.

Fence notes for B1:

- `chupa/tickets.py`
- `chupa/__main__.py`
- `chupa/stats.py`
- `chupa/author.py`
- `chupa/hostfiles.py`
- `chupa/docs/host-authoring.md`
- `chupa/specs/requisition_review.md` and its version pin test
- `dev.py` (`new --reference`)
- `docs/how-chupa-works.md` §2
- `tests/integration/test_closed_sets.py`
- `tests/integration/test_tickets.py`
- `tests/integration/test_author.py`
- CLI tests for `new`

Grep `tests/` and `docs/` for `feature|bug|chore` and the kind tuple before authoring, and fence every hit that asserts the set.

## Deferred decisions

1. **Raster image generation.** Include AI-generated images, or only code-rendered output? Recommendation: code-rendered only for v1.
2. **Routing by ticket kind.** A text-only implementer (qwen3-coder) cannot look at its renders. Options:
   - add an optional `kinds:` filter to `Route`. This is a schema change: older engines refuse the key as unknown.
   - route `implement` to a multimodal CLI.

   Recommendation: defer the filter until a graphics run fails for this reason.
3. **Human sign-off.** Should a graphics ticket hold for operator approval before merge? Repo rule: a hold ships with its release verb, so this adds scope to B3. Recommendation: the visual review decides, and only an undecidable criterion parks the ticket for the operator.
4. **Pixel baselines.** A perceptual-diff gate against committed baselines (threshold-based) would make some visual criteria mechanical. Recommendation: leave it out of v1. Hosts that want it write it as a test in the render command.

## Sources

- Gemini CLI headless mode and `stream-json` events: https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/headless.md
- Gemini CLI settings, `context.fileName`, `GEMINI_CLI_SYSTEM_SETTINGS_PATH`, precedence: https://geminicli.com/docs/cli/configuration
- System settings for enterprise control: https://geminicli.com/docs/cli/enterprise
