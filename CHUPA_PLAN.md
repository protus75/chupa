# chupa -- implementation plan (seed document)

Status: design plan. This file seeds a NEW, separate repository and is self-contained: every load-bearing rule, contract, and decision is stated here; implementer-owned internal schemas are delegated where marked (sections 6 and 13). Nothing depends on any other document existing. "chupa" is the project name (unique so agents never confuse this system's rules with another project's).

**Two eras -- a reading rule.** Every rule below binds ONE of two systems; conflating them produces wrong builds and wrong reviews.

- BOOTSTRAP era (Phases 0-2): the conductor then the continuous self-hosting drain, the NO-GO resting state; tuned for unattended forward progress under the good-enough bar. Its UNATTENDED conduct is not confined to Phases 0-2 -- it governs chupa building ITSELF and runs holds-exempt through the whole self-hosted build to Phase 6 (section 19), bounded by the section 18 safety envelope, never a per-phase `confirm`; the daemon is a component built and soak-proven in Phase 3, not a supervisor the still-building engine hands itself to.
- DAEMON era (Phase 3+): the continuous daemon machinery, and -- once the operator CUTS OVER to running on HOST work (GO first RECORDED, the daemon started on that work via `chupa serve`) -- the supervised product carrying the full gate set.

The split is contractual -- section 19's bootstrap contract is the authority. Bind every requirement, build decision, and review finding to its era before applying it:

- A product supervision surface never gates chupa's own self-build (through Phase 6). Supervised-merge holds, GO-gated auto-confirm, and the phase-boundary/box draft gate govern HOST work under a recorded GO; the self-build is bounded by the section 18 safety envelope, never a `confirm`. The GO-grade eval's Author-graph check runs from a harness-local author prompt, NOT the production `specs/author.md` (a Phase 2 seed).
- A bootstrap convenience never ships as engine code (section 0).

Why: holding one era to the other era's contract is wrong by construction.

## 0. Cold start (bootstrap this repo from this document)

Given only this file on a Linux box, the steps below stand up the repo and the environment Phase 0 (section 19) builds into. Everything here is a ONE-TIME human bootstrap the operator runs before any agent or daemon exists, distinct from the engine's own runtime, which never shells these bootstrap conveniences (one named exception: the drain's self-upgrade re-exec through `uv run`, D1).

**Prerequisites.** Two are required by the engine at runtime; the BOOTSTRAP CLI -- shipped default `claude`, retargetable per the paragraph below -- is required by the BOOTSTRAP (the conductor shells it per deliverable -- preflight-checked; a nonzero exit halts the run, never a silent skip); the rest are setup-only. Host #1 -- the operator-declared host project Phase 6 onboards (BoardGameUI in this plan's reference environment) -- is a declared setup input, not a binary: declare it here at setup or declare none. EITHER WAY Phase 6 scaffolds the committed fixture host and runs its wiring and exit reads against it (section 19); the declared host bears only on the operator's post-cutover onboarding and acceptance reads, and with none declared live onboarding simply waits at the cutover. `gh` is a convenience for repo creation ONLY -- the engine never shells it (no `gh`, no PRs in the loop; section 18, D8).

The bootstrap CLI is a declared constant at the top of `bootstrap/conductor.py` (shipped default `claude`; any agent CLI with a headless prompt mode satisfies it -- for `codex`, `codex exec` with the prompt on stdin). The conductor shells that one CLI per deliverable through a single adapter row (argv shape, prompt delivery, exit-code read), and deliverable 1 authors the conduct file THAT CLI loads -- CLAUDE.md for `claude`, AGENTS.md for `codex` (section 17's curated-subset rule then runs in the opposite direction) -- so retargeting the bootstrap is a one-constant edit plus that mapping, never a rewrite of this section.

| Tool | Version | Role | Required |
|---|---|---|---|
| Python | 3.14+ (floor; D1) | interpreter the chupa venv pins -- provided by uv, not the system | yes -- runtime |
| git | any recent | every ref/commit op goes through `git.py` (section 10) | yes -- runtime |
| claude | the latest release, installed with `pnpm add -g @anthropic-ai/claude-code@latest`, logged in | the conductor shells `claude -p` per deliverable (build + review contexts); engine runtime touches it only as a configured `cli` provider (section 6) | yes -- bootstrap |
| pnpm | any recent, its global bin dir on PATH | installs and updates every agent CLI globally; the preflight reads each CLI's latest release from it (section 6) | yes -- setup + preflight |
| uv | any recent | creates the venv and installs deps; runtime-shelled ONLY by the drain's self-upgrade re-exec (section 18, D1) | setup + one exception |
| gh | any recent | one-command repo creation below; engine NEVER shells it | no -- convenience |

Runtime deps are deliberately tiny (goal 1): stdlib (`asyncio`, `argparse`, `tomllib`, `json`) plus `PyYAML` (config parse, section 15) and `pydantic` (artifact + journal-body schema validation, section 5). Journal projections are stdlib read-time folds (D3); an analytics engine (DuckDB) is a D10 return at the first projection measured too slow as a fold. Provider SDKs are pulled per the provider layer (section 6), never hardcoded here.

Verify prerequisites, then let uv provide Python (uv fetches a standalone CPython from Astral's python-build-standalone, so the system Python version is irrelevant):

```bash
git --version      || echo "install git (required)"
command -v claude  || echo "install + log in claude (required: the conductor shells it)"
command -v uv      || echo "install uv:  curl -LsSf https://astral.sh/uv/install.sh | sh"
command -v gh      || echo "gh optional -- repo-create convenience only"
uv python install 3.14   # Python comes from uv, not the system
```

Create and seed the repo -- the `python3` block extracts both `bootstrap/conductor.py` and the pointer README from this document, so neither is hand-pasted and CHUPA_PLAN.md stays canonical:

````bash
mkdir -p ~/source/chupa && cd ~/source/chupa
git init -b main
mv ~/Downloads/CHUPA_PLAN.md .            # this document
mkdir -p bootstrap
python3 - <<'PY'
import re
plan = open("CHUPA_PLAN.md").read()
def extract(name):                       # one minimal pattern for every embedded source
    return re.search(r"# BEGIN_%s\n(.*?)\n# END_%s" % (name, name), plan, re.S).group(1)
open("bootstrap/conductor.py", "w").write(extract("CONDUCTOR") + "\n")
open("README.md", "w").write(extract("README") + "\n")
PY
git add README.md CHUPA_PLAN.md bootstrap/conductor.py
git commit -m "Seed: chupa plan + generated README + bootstrap conductor"
````

**Generated files (conductor + README).** The `python3` extractor materializes TWO files from this document's appendix (section 21) with one pattern -- the lines between a `# BEGIN_<NAME>` / `# END_<NAME>` sentinel pair, read straight from CHUPA_PLAN.md (already on disk after the `mv`): `bootstrap/conductor.py` from `# BEGIN_CONDUCTOR` (the phase-playbook driver) and `README.md` from `# BEGIN_README` (a deliberate POINTER -- identity, read-first link to this plan, and the lifecycle run commands (bootstrap, drain, serve) -- never a parallel run-book). README.md is GENERATED, never hand-edited: a README change edits the `# BEGIN_README` block in the appendix and re-runs the same extractor. Keep both sentinel pairs intact; the extractor keys on them.

Publish -- one command with gh, or the git-only path if gh is absent:

```bash
gh repo create chupa --private --source=. --remote=origin --push
```

```bash
# git-only fallback: create an empty PRIVATE repo in the GitHub web UI first, then
git remote add origin git@github.com:<owner>/chupa.git
git push -u origin main
```

Environment + first build. From the seeded repo, create the venv and start Phase 0:

```bash
uv venv --python 3.14
uv pip install pyyaml pydantic   # the non-stdlib runtime deps
```

Phase 0 formalizes these in a `uv`-managed `pyproject.toml` with `requires-python = ">=3.14"`; the manual install above only gets the first session running. Then drive the whole bootstrap -- Phase 0 then Phase 1 -- WITHOUT hand-pasting; `bootstrap/conductor.py` (seeded above) is the automation, and with no `--phase` it runs every conductor-owned phase end to end:

```bash
python3 bootstrap/conductor.py             # default: Phase 0 then Phase 1, end to end
python3 bootstrap/conductor.py --auto      # same, unattended (no verdict pauses)
```

The conductor parses this document's Phase N prompt playbook and runs each deliverable in a FRESH `claude -p` context (a separate scoped context -- the anti-wander property -- carrying a standing preamble with the verify-in-place and file-don't-ask rules), then GATES by the prompt's own stop-condition, layered fail-closed:

- The `claude` call MUST exit zero. Transient nonzero exits are retried with backoff a bounded number of times; a persisting failure (a dead or unauthenticated CLI) halts, never a phantom completion.
- The playbook item's `expects:` files MUST exist on disk (the agent-did-nothing check).
- The conductor re-runs `uv run pytest` itself, never trusting the agent's claim.
- A SECOND fresh context adversarially reviews the uncommitted diff, failing ONLY the good-enough bar's spine-breaking classes (section 19): state corruption, deadlock or permanent stall, secret exposure, false-green verification (tests that mirror the implementation instead of pinning behavior). A blocking finding must be REPRODUCIBLE, must attach to the CURRENT deliverable's diff (never pre-existing code or later-phase scope), and the finding set FREEZES after buying exactly one bounded reimplementation pass -- a reviewer that raises a new blocking objection each pass is the churn failure mode, and its later findings are advisory. Every other finding is appended to `bootstrap/suggestions.md`, never a halt. The same admissibility bounds apply to the pipeline's `correctness_review` REJECT from the day it exists (section 7): a bare unstructurable verdict, a pre-existing-defect complaint, or a scope-expanding demand does not block.
- Gate findings (red suite or spine-class review fail) are fed back up to twice before halting for the operator -- both rounds servicing the FROZEN first-pass blocking set per the freeze law above; a new blocking objection raised on a later pass files to `bootstrap/suggestions.md` instead of halting.

A real-model deliverable (its exit is a recorded verdict, not a green suite -- Phase 1 prompts 2 and 9) runs, commits on journal evidence, then pauses for the operator to read the verdict (`--auto` continues without pausing). A bootstrap run records at most NO-GO -- the GO-grade baseline is a Phase 6 deliverable run immediately before cutover, where GO is first read (section 19) -- leaving daemon-era machine authoring supervised until GO is recorded; the bootstrap drain itself never holds (section 19).

The single cold-start paste above is the ONLY hand-paste; from here the conductor drives every deliverable. It is section-0 bootstrap tooling, never engine code (D1 governs the engine, not these cold-start conveniences), and it retires once the Phase 1 walking skeleton lands and chupa runs its own tickets. Phases 0-1 are built by the conductor, not by chupa itself.

Automation is the default, in three rungs: no `--phase` runs every conductor-owned phase (0 then 1); `--phase N` runs one phase; `--phase N --deliverable K` runs exactly that one deliverable and stops. Coarser rungs run the finer one in order, gating each the same way, and compose through `bootstrap/state.json`. A deliverable that persistently exceeds its fix attempts halts naming that finest rung: the paved road is narrowing or splitting ITS playbook prompt in this document, then re-running exactly that deliverable -- never hand-pasting, never restarting the phase.

**First session (VSCode + Claude Code).** After cold start the repo holds this document, the README, and `bootstrap/conductor.py` -- no engine code. The operator does NOT hand-paste the build (the cold-start paste above is the only one). Why: pasting the whole plan and saying "go" is the wander trap the conductor exists to avoid -- each deliverable gets a fresh, scoped `claude -p` context instead.

- Open the repo (`code ~/source/chupa`); approve permissions once (`/permissions`) to watch in the panel, but the conductor invokes `claude -p` headless, so no panel interaction is required.
- Create the venv and deps (above), then run `python3 bootstrap/conductor.py` (no `--phase` runs Phase 0 then Phase 1 end to end; `--phase 0` runs just Phase 0; `--phase 0 --deliverable K` just that one step). It walks each phase's prompt playbook deliverable by deliverable: a fresh context per prompt, the layered gate above, a commit per green deliverable, a halt on red. Deliverable 1 authors the seed conduct file (CLAUDE.md, section 17; AGENTS.md waits for the first deliverable that routes a non-Claude agent CLI); once CLAUDE.md lands every later `claude -p` auto-loads it.
- The default run continues into Phase 1 (the walking skeleton) after Phase 0; `--phase 1` runs it alone. Two of its deliverables are real-model runs whose exit is a recorded verdict, not a green suite (the catastrophic-NO-GO spike and the first real ticket merge); the conductor runs them, then pauses for the operator to read the verdict before continuing (`--auto` skips the pause; GO itself is not earnable during the bootstrap -- the GO-grade baseline is a Phase 6 deliverable at cutover, section 19). Export the provider key first (see the Phase 1 prereqs below).
- Re-running over existing work is expected, not an error. The gates check outputs, not authorship, so the conductor cannot tell a deliverable it just built from one an earlier lineage already committed; a deliverable whose output is already present is VERIFIED in place (the conductor's standing preamble carries that instruction into every context) and `commit()` no-ops on the clean tree. Progress lives in `bootstrap/state.json`; a re-seed can leave it desynced from the tree (state says done N while the code is further along), which self-heals as the run advances. To restart a phase clean, delete `bootstrap/state.json`.
- The operator role may be a supervising chat session instead of a human at the terminal (section 17, rule set B): it runs the conductor with `--auto`, because the verdict pause waits on a human, and the drain in the background, then repairs each stop under the section 19 recovery order.
- A deliverable that notices an out-of-scope problem appends it to `bootstrap/suggestions.md` (the pre-Phase-2 stand-in for the Suggestion Box, section 11) and moves on -- it never stops to ASK, because a pytest-gated step does not pause and the question would be lost. The stand-in has a consumer: the Phase 2 Suggestion Box deliverable ingests this file as the box's first messages and retires it (section 19).
- The conductor's final Phase 1 deliverables -- the prompt 14-17 handoff, four seed batches -- author Phase 2's tickets (specs only) into a seeded queue, then it retires. After that the loop flips: the operator runs ONE `chupa drain` and chupa builds Phase 2 AND every later phase through its own pipeline -- each phase's last ticket seeds the next as `confirmed` INTO the same running drain, which carries the whole self-build to quiescence with no per-phase re-run (section 19).

**Phase 0 prompt playbook.** These are the conductor's input -- parsed in order from this section by `bootstrap/conductor.py --phase 0`, not hand-pasted. The conductor runs each in a fresh `claude -p` context, re-runs `uv run pytest` as the gate, and commits per deliverable (halting on red). Each assumes CLAUDE.md is loaded (deliverable 1 authors it). Prompt 1 is the seed-files step; 2-11 build Phase 0 to its exit gate (section 19). Keep every block's format intact -- an "N -- Title:" line, then an "expects:" line naming the space-separated files whose on-disk existence the conductor verifies after the run -- EVERY source file the deliverable creates, its production modules as well as its tests, so the check covers every output and no created module is left undeclared and unowned (`-` waives the check for journal-gated deliverables), then one fenced prompt -- because the conductor parses exactly that shape.

1 -- Seed conduct file (CLAUDE.md):
expects: CLAUDE.md

```
Read CHUPA_PLAN.md section 17 plus the design law in sections 2-3. Author the root
CLAUDE.md exactly per section 17: a 3-5 line
identity block (what chupa is, engine plane vs host plane), ONE read-first pointer
to CHUPA_PLAN.md, seed rule sets A and B as terse behavioral rules, hard cap
<= 120 lines. Do NOT author AGENTS.md: every bootstrap context is claude -p,
which loads CLAUDE.md -- the AGENTS.md curated subset is authored per section 17
by whichever deliverable first routes a non-Claude agent CLI. Write
no engine code. Stop when CLAUDE.md exists so I can review.
```

2 -- Project scaffold:
expects: pyproject.toml uv.lock .gitignore chupa/__init__.py tests/test_scaffold.py

```
Set up the project skeleton per CHUPA_PLAN.md (design law sections 2-3, D1 pure
Python, Phase 0 in section 19). Create a uv-managed pyproject.toml with
requires-python = ">=3.14", runtime deps pyyaml and pydantic (the full
section 0 runtime set), dev deps pytest and
pytest-asyncio; a chupa/ package plus tests/ dir; a .gitignore covering .venv/,
__pycache__/, and .chupa/ (the instance state dir: journal, spools, worktrees;
sections 10, 15).
Ship the project's first test (tests/test_scaffold.py) proving the harness:
the chupa package imports, and pyproject.toml parses (tomllib) with
requires-python ">=3.14" and the declared runtime deps -- enough that the suite
is green and every later pytest gate runs on a proven harness.
No other engine logic yet. Commit uv.lock
(this is an app -- pin it for reproducible sync). No kernel logic yet. Verify uv
run pytest is green, then stop.
```

3 -- journal.py (TDD):
expects: chupa/journal.py tests/test_journal.py

```
Implement chupa/journal.py per CHUPA_PLAN.md (D3 and the Phase 0 kernel list in
section 19): segmented append-only JSONL under the host state dir (the
segmented journal/ layout and ordered segment naming, section 6 -- but NO roll
trigger: size/age rotation and its roll test are a Phase 3 seed with the
daemon, rotation's first retention consumer), glob-ordered read across
segments, write-ahead fsync, torn-tail
tolerance (a truncated final line is skipped on read, not fatal), the pinned
`ts` rendering (section 6). TDD: write
tests/test_journal.py first, including one that reads every event back in
order across MULTIPLE pre-seeded segments (glob-ordered read is layout
behavior, not roll behavior), and one that appends a torn final line and
still reads the rest. Pure stdlib only. Stop when uv run pytest is green.
```

4 -- effects.py (once-semantics):
expects: chupa/effects.py tests/test_effects.py

```
Implement chupa/effects.py per CHUPA_PLAN.md (mechanical-sandwich in section 2, the
Phase 0 list in section 19): an effect wrapper that journals intent, executes
once, journals the result, and on replay returns the recorded result instead of
re-executing. Use the injectable seams (clock, process-exec, filesystem) as
Protocols so tests drive fakes. TDD tests/test_effects.py first: once-semantics is completion-keyed per
section 6 -- an effect whose key already has a completed event is not
re-executed on restart (a crash AFTER the completion is journaled does not
double-execute, and replay returns the recorded result). The intent-only
crash window (intent journaled, completion not yet) is closed by Phase-1
reconcile-on-entry (section 11), NOT the Phase-0 primitive, so do not build
intent-suppression into the primitive. Stop when uv run pytest is
green.
```

5 -- git.py:
expects: chupa/git.py chupa/seams.py tests/test_git.py

```
Implement chupa/git.py per CHUPA_PLAN.md section 10 and D1: every git call through
argv lists (no shell, no string assembly), dir-pinned with git -C <dir>. Cover
the ops Phase 1 needs (init, status, rev-parse, add, commit, branch, worktree
add/remove/prune, rebase, merge --squash, and describe --tags --always --dirty
for the section-6 lockfile identity) as thin typed wrappers over the
process-exec seam. Worktree cleanup is worktree remove + prune, never rm -rf. TDD
tests/test_git.py against a fake process-exec seam plus one test against a real
temp repo. Stop when uv run pytest is green.
```

6 -- Lockfile guard:
expects: chupa/lockfile.py tests/test_lockfile.py

```
Implement the single-writer lockfile guard (chupa/lockfile.py) per CHUPA_PLAN.md
(D2, sections 6 and 15): one advisory flock per project checkout carrying
instance identity, acquired before any write, refused if already held, and
RELEASABLE by the holder -- the drain's self-upgrade handoff releases it
before spawning its child (section 18). TDD tests/test_lockfile.py first,
including lock-contention-refused and release-then-reacquire. Stop when uv
run pytest is green.
```

7 -- config loader:
expects: chupa/config.py tests/test_config.py

```
Implement the config loader (chupa/config.py) per CHUPA_PLAN.md section 15: parse
config.yaml at the
checkout root (or --config path) with PyYAML safe_load, validate fail-closed
against the top-level schema in section 15, enforce the schema_version handshake
(refuse a NEWER schema_version, accept equal; refuse an OLDER one with a paved
road naming migrate-config -- migration is explicit per section 15, the verb
itself Phase 6's), and emit precise errors naming the
bad key. TDD tests/test_config.py first: valid config, missing required key, and
newer plus older schema_version
all covered. Stop when uv run pytest is green.
```

8 -- Artifact models + Gate runner:
expects: chupa/artifacts.py chupa/gates.py tests/test_gates.py

```
Implement the Artifact models and StageResult/Outcome types (chupa/artifacts.py),
and the Gate protocol +
runner + gate-lint (chupa/gates.py) per CHUPA_PLAN.md sections 5 and 7 and the
Phase 0 list in
section 19. Gates are a closed protocol; every gate finding ships a paved-road
message, and gate-lint FAILS a gate that lacks one. Prove the machinery with a
gate-lint test over a stub gate (the first real content gate arrives with a
Phase 1 deliverable that earns it). The runner applies hard/soft severity from
review.gate_severity (invariant 3); with no config loaded in Phase 0 it
defaults to the shipped all-hard map (every v1 hard-set code hard at merge,
section 15). TDD tests/test_gates.py first, including
gate-lint rejecting a
paved-road-less gate. Stop when uv run pytest is green.
```

9 -- LLM interface (fake) + stage driver:
expects: chupa/llm.py chupa/driver.py chupa/enginelog.py chupa/redact.py tests/test_driver.py

```
Implement the LLM interface with a scripted fake (chupa/llm.py), and the one
LLM-stage driver (chupa/driver.py)
per CHUPA_PLAN.md section 5 (invariant 2) and section 6. The driver renders the
prompt, writes it to the attempt spool BEFORE the call (a call that raises or
hangs must leave the sent prompt on disk), calls the LLM seam, captures each
attempt to the spool, writes
structured events to the engine log (never the journal), and runs every captured
stream through the redaction seam scrubbing configured secret VALUES before
persisting. Per invariant 2 the driver then validates the emitted artifact and
runs the stage's gates, feeding a hard-gate failure back as an in-stage
re-prompt on the SAME workspace bounded by the retry cap (section 11.1, shipped
default 6 from caps.retry); Phase 0 exercises this loop with the echo stage's
empty gate list. The fake returns scripted responses for deterministic tests. TDD
tests/test_driver.py first, including a secret value that must not appear in any
spooled/logged output. Stop when uv run pytest is green.
```

10 -- spec renderer + spec lint + plan lint:
expects: chupa/specs.py tests/test_specs.py tests/test_plan_lint.py

```
Implement the spec renderer + spec lint (chupa/specs.py) per CHUPA_PLAN.md
section 8. The renderer keeps untrusted host content in
the DATA channel, never the instruction channel; spec lint fails a spec that
folds data into instructions. The renderer also owns the `Plan contract`
resolver (section 13): a ticket's plan ids -- numeric section ids against
CHUPA_PLAN.md's `## N.` headings, subsection ids (`N.k`) against its
`### N.k` headings, and section-19 unit ids (`19.L`, `19.I`, `19.P0`-`19.P6`,
entry units `19.P<n>.<stem>`) against its `### 19.<unit>` headings -- resolve
verbatim,
deduplicated, injected as the sole channel for plan bytes; an unresolvable id,
or section 22, is a fail-closed refusal. It owns the RENDER_BOUND_CHARS and
REQ_RENDER_HEADROOM constants and the delimiter quoting of section 8. TDD the
renderer + lint (tests/test_specs.py), including a lint failure on a spec
that renders injected content outside the data-block form, a `Plan contract`
id that resolves to its section's bytes exactly once when cited twice, a unit
id resolving to exactly its unit, an unknown id refused, and a delimiter-
bearing payload rendered quoted. Then implement PLAN LINT per section 8 in
chupa/specs.py and tests/test_plan_lint.py, run against the real
CHUPA_PLAN.md (heading ids, registry parse/coverage/cite resolution,
entry-unit parts). Stop when uv run pytest is green.
```

11 -- Phase 0 exit gate:
expects: tests/test_echo_stage.py tests/test_fault_injection.py

```
Wire the Phase 0 exit gate per CHUPA_PLAN.md section 19. Build a toy echo stage
(tests/test_echo_stage.py):
consumes a stub artifact, emits one, running end-to-end under
the LLM-stage driver with the fake LLM. Then build the crash-point / fault-
injection harness (tests/test_fault_injection.py) over the state layer (journal +
effects) that induces crashes
at each write point and asserts torn-tail tolerance and effect once-semantics.
Phase 0 is done when the echo stage runs green end-to-end AND the fault harness
passes. Stop when uv run pytest is green.
```

**Phase 1 prompt playbook.** Same conductor as Phase 0 -- `bootstrap/conductor.py --phase 1` parses and runs these in order, gating and committing per deliverable -- with two differences. Phase 1 is FIRST real-model contact (a real provider key enters, key-scoped; see the operator prereqs below), and per the section 19 ordering exception the review-baseline eval runs FIRST, before the walking skeleton, because a NO-GO verdict is cheapest to find before the kernel is wrapped in a pipeline. Prompts 1-2 stand up real-model review and run the catastrophic-NO-GO spike; 3-8 build the walking skeleton; 9 is the exit gate; 10-17 are the handoff, one independently-gated deliverable per subsystem -- reconcile-on-entry (10); the `drain` verb's dispatch loop and park/retry accounting (11); the findings-fed re-entry rendering (12); the self-upgrade re-exec and premise park (13); and the seeded Phase 2 queue as four batches (14 caps+harvest, 15 diagnosis+its eval, 16 box+ladder+triage, 17 Author+requisition_review+battery+auditor+exit seed), the conductor's final acts -- no handoff prompt bundles two independently-testable subsystems into one coding context. Prompts 2 and 9 are the real-model deliverables (exit is a recorded verdict / a merged ticket, not a green suite) -- the conductor runs them, then pauses for the operator to read the verdict before continuing (`--auto` skips the pause). After 17 the queue is seeded and the loop flips: the operator runs ONE `chupa drain` that carries Phase 2 and every later phase to quiescence (section 19), each phase's final ticket seeding the next into the same running drain, and the conductor is retired.

**Phase 1 prerequisites (operator, before `--phase 1`).** Phase 1 adds one runtime dependency section 0 did not need -- a reachable model provider -- since Phase 0 ran the scripted fake. Before running `--phase 1`, and required by prompt 2's live run: pick the provider set and each provider's access `kind` (`api` or `cli` -- they degrade differently, section 6); make each reachable (an `api` SDK pulled into the venv, a `cli` agent binary installed with `pnpm add -g <package>@latest`, on PATH behind its argv wrapper, its pnpm package recorded as the provider's `package`, D1); export the key under the env-var NAME the config provider registry declares in `auth`, never a literal secret in any file (an `api`-keyed provider; a `cli` provider on ambient CLI login declares no `auth` and needs no export -- sections 6, 15); record the chosen per-tier model ids -- each provider's `models_by_tier` values and the strongest-model pin REVIEW takes at every tier -- where prompt 1's authoring agent can read them (a setup note, or a pre-authored `providers:` block in config.yaml that prompt 1 then treats as operator-owned truth), so the authored config carries operator-chosen ids, never agent guesswork; and set each no-usage `cli` provider's `limits.est_cost_per_call_usd` (recommended 1.00 USD for a flat-subscription agent CLI whose stream reports no cost, e.g. codex -- section 6). Pinning the (provider, model) rows for REVIEW and AUTHOR is part of the config.yaml prompt 1 AUTHORS (no earlier deliverable creates the instance config); switching later is a config edit, never a ticket edit. If prompt 1 finds NO operator-provided values (no setup note, no pre-authored `providers:` block), it does not guess and does not halt: it authors every operator-owned value as the literal placeholder `OPERATOR-SETS-THIS` (model ids, `auth` env-var names, `est_cost_per_call_usd`) -- schema-valid, so every offline deliverable builds and tests -- and the provider layer REFUSES a live call whose resolved row still carries a placeholder, a config/setup refusal naming this prerequisite (section 6; fail-closed: a placeholder can never reach a model, and inventing a real-looking value is the guesswork this paragraph bans).

1 -- Provider layer + real LLM adapter (first real-model contact):
expects: chupa/providers.py config.yaml tests/test_providers.py

```
Implement the provider layer (chupa/providers.py) per CHUPA_PLAN.md section 19
(Phase 1) and section 6:
a provider registry, routing parse (validation includes the
implement-requires-cli rule, section 6), and the FIRST routed candidate only, with
key-scoped injection (a surface's key reaches only the call that needs it, never
the wider process). Add a real client implementing the Phase 0 LLM
interface behind the routing. The engine ships one `cli` provider adapter per
agent CLI it can drive -- from the start, `claude` AND `codex` -- over a shared
base that owns the write-grant derivation, the redaction of both sinks, and the
cost floor (the trust boundary, so it lives ONCE, never a copy per adapter).
Each adapter is its own argv contract and event-stream parse: `claude` via
`-p --output-format stream-json` (model via `--model <model>`; effort has no
claude flag, so it is recorded in provenance only; write grant
`--permission-mode bypassPermissions`
for implement, the literal read-tool allowlist `--allowedTools Read Grep Glob LS`
elsewhere; text/usage/cost from the terminal
`result` event); `codex` via `exec --json` (model via `-m <model>`, effort via
`-c model_reasoning_effort=<effort>`; write grant
`--dangerously-bypass-approvals-and-sandbox` for implement, `--sandbox read-only`
+ `approval_policy=never` elsewhere; the prompt on stdin via a trailing `-`; text
from the last `agent_message` item, usage from `turn.completed`, NO cost reported
so the declared flat estimate charges, and a `turn.failed`/`error` event is the
failure signal BECAUSE codex exits 0 even on a failed turn). TDD each adapter's
LIVE contract against a scripted fake subprocess (section 6):
the per-surface write-grant allowlist reaches the invocation, the invocation
runs in the passed worktree, and usage/cost is parsed from the event stream
-- a client that omits the write grant must fail THIS suite, never surface
for the first time at the first real ticket. AUTHOR the instance's config.yaml at the checkout
root IF IT IS ABSENT (no earlier deliverable creates it); config.yaml is
HOST-PLANE (section 15), so an existing one is operator-owned truth this
deliverable READS for its routing and never overwrites: schema_version, state_dir
.chupa/state, the provider registry, and routing rows for the REVIEW, AUTHOR,
and IMPLEMENT surfaces at EVERY tier of the closed low|medium|high|max scale --
route IMPLEMENT to codex and AUTHOR to claude, each naming only its provider and
inheriting models_by_tier[tier] (section 6) so it scales with the ticket's
agent_tier with no per-row model, and REVIEW to claude pinned to its strongest
model at every tier. Routing review to a different provider or model than the
implementer is the PREFERRED diversity setting (section 6), never a hard gate:
the only hard requirement is that review runs in a SEPARATE session from
implement (the driver enforces it), so same-model-different-session is allowed
and the operator may route implement to any model (a config edit). The IMPLEMENT
rows pin a kind: cli
provider (the implement-requires-cli rule fails the config at load otherwise,
section 6). All
four tiers are declared so a seed authored at any agent_tier (section 13)
resolves to a route, never a routing hole that terminals infra_error and PARKS
the drain on an operator config edit -- a stop the bootstrap contract forbids
(section 19); shipped defaults may stand elsewhere. Parse ONLY limits.est_cost_per_call_usd from the limits block
(cost stamping needs it, section 6); the rest of limits is Phase 3's to
parse and enforce. If any routing row pins a non-Claude agent CLI, author
AGENTS.md (the section 17 curated subset) in this same deliverable AND reconcile
CLAUDE.md's note that AGENTS.md now exists (a both-files change, section 17) --
the first non-Claude context must start with conduct rules.
The operator's provider values (models_by_tier, routing pins, cli kinds,
est_cost_per_call_usd) are in bootstrap/operator-setup.md -- operator-owned
truth; author config.yaml from them, never placeholders for values it states.
TDD the registry + routing parse and key-scoping against
fakes (tests/test_providers.py); keep the suite offline -- no real call in uv run
pytest. Stop when uv run
pytest is green.
```

2 -- Review-baseline eval: fixtures + harness (the catastrophic-NO-GO spike):
expects: specs/review.md eval/harness.py eval/fixtures

```
Build the review-baseline eval per CHUPA_PLAN.md `19.P1` (exit reads) -- run
it now, before the walking skeleton. First author specs/review.md (the REVIEW
prompt-spec, section 8) if absent -- the SAME spec prompt 6 later wires
unchanged, so the baseline measures the spec the skeleton will run. Commit
eval/fixtures/<name>/ with 15-20
planted defects spanning logic, hidden-info leak, acceptance mismatch, and scope
escape, PLUS at least 3 clean (defect-free) fixtures whose expected verdict is
approve; each fixture dir holds diff.patch (the planted diff) and expected.json
carrying the expected verdict, the defect-class tag, and the author identity
(provider, model, tier) -- authored via a (provider, model) DIFFERENT from the one routed to
REVIEW (at minimum a different tier), the fixture-author identity recorded in
the baseline signal: same-family fixtures share the reviewer's blind spots and
inflate the catch rate (section 6). Implement eval/harness.py: drive
specs/review.md over each fixture
through the provider layer and score catch rate, known-bad false-approve, and
clean false-snag.
Record the run as a journal signal event carrying the baselined identity -- the
resolved (provider, model) rows serving REVIEW and AUTHOR at every tier the eval
exercised, plus those surfaces' spec-major versions -- and the verdict. The
scored run records NO-GO, the only verdict this spike can support: it is
catastrophic-NO-GO detection -- a reviewer that misses gross planted defects is
cheapest to find now, before the kernel is wrapped in a pipeline -- not GO
grading, which needs the >= 50-fixture set and the operator's Author-graph
judgment and is a Phase 6 deliverable run immediately before cutover, where GO
is first read (section 19; section 13 touchpoint 7). NO-GO is a designed state
(section 12 supervised mode; the bootstrap drain is exempt, section 19), not a
blocker. Do not discard the harness or fixtures -- they are the base the
Phase 6 GO-grade baseline extends. This is a real-model run: stop when the eval
records a verdict.
```

3 -- LLM call as effect:
expects: chupa/llmeffect.py tests/test_llm_effect.py

```
Move the LLM call behind the @effect wrapper per CHUPA_PLAN.md `19.P1`
and the effects contract in section 2: idempotency key ticket+run_seq+surface+
attempt+call_seq -- run_seq derived per section 6 as the count of the stem's
prior terminal events -- a cost-event journaled per call, and replay returning
the recorded result instead of re-calling (the Phase 0 driver called the seam
directly -- this replaces that path). TDD tests/test_llm_effect.py with the
scripted fake: a replay that does NOT re-call,
and exactly one cost-event per call. Stop when uv run pytest is green.
```

4 -- Ticket contract + runner intake:
expects: chupa/tickets.py tests/test_tickets.py

```
Implement the ticket contract and runner intake (chupa/tickets.py) per
CHUPA_PLAN.md section 13 and
`19.P1`. Ticket frontmatter carries only fields the scheduler, a
gate, or the authoring/triage policy reads; ordering lives in depends and
priority, never prose. Runner intake: at invocation, validate pending hand-
authored ticket FILES and ticket-plane-commit them, standing in for the Phase 3
watcher. Intake lint enforces the full section 13 grammar, including the
`Plan contract` section-id form and `Context`'s structural refusal of the
plan file itself. TDD tests/test_tickets.py: a valid ticket validates and
commits; a bad-schema ticket is refused with a paved-road message; a ticket
citing CHUPA_PLAN.md in `Context` is refused naming the `Plan contract` road;
a `Plan contract` bullet with an unresolvable section id is refused. Stop
when uv run pytest is green.
```

5 -- CLI verbs: status, new, run <stem>:
expects: chupa/__main__.py chupa/status.py chupa/runner.py tests/test_cli.py

```
Implement the CLI verbs per CHUPA_PLAN.md section 18 and `19.P1`:
status projects current state from the journal (a projection, never
authoritative); new authors a ticket file; run <stem> drives one ticket through
intake + the single-writer lockfile + the stage-dispatch seam, in the single
process holding the lock -- the stages and merge behind that seam are prompts
6-7's deliverables, so dispatch reaching the seam with the locked, validated
stem IS the tested behavior here (a scripted fake stands in). Expose the
verbs through a `python -m chupa` module entry (chupa/__main__.py); keep the project
virtual (no console script until the release path, section 13 touchpoint 6). TDD
tests/test_cli.py against a temp checkout, including run refused when the
lockfile is already held and run provably dispatching the locked stem to the
stage seam.
Stop when uv run pytest is green.
```

6 -- Stages: Implement / Check / Review:
expects: chupa/stages.py specs/implement.md tests/test_stages.py

```
Build the Implement, Check, and Review stages (chupa/stages.py;
specs/implement.md) per CHUPA_PLAN.md sections 4
and 5 and `19.P1`, as prompt-specs run through the LLM-stage driver,
single worker, full artifacts + provenance per stage. Review WIRES the existing
specs/review.md from prompt 2 UNCHANGED -- a spec-major rewrite here silently
drifts the just-recorded baseline identity (section 19). The live pipeline runs
IMPLEMENT-onward on one hand-authored ticket. Do NOT build the Author stage or
specs/author.md: nothing in Phase 1 executes them -- their machine input, the
triaged Suggestion Box, does not exist until Phase 2 -- so they are a seeded
Phase 2 ticket beside the triage consumer that feeds them (prompts 16-17). TDD
tests/test_stages.py: the stage
transitions with the scripted
fake. Stop when uv run pytest is green.
```

7 -- Merge: hard gate set + single-admission:
expects: chupa/merge.py tests/test_merge.py

```
Implement MERGE (chupa/merge.py) per CHUPA_PLAN.md section 9, section 10, and
`19.P1`:
the v1 hard gate set MINUS the bug gate (kind: bug, the ## Regression grammar,
and the merge-base overlay defer to the Phase 6 report inbox, their first
bug-intake consumer -- sections 7, 19), then a synchronous single-admission
merge -- ticket-plane restore (git restore of tickets/** to main's content,
section 9), rebase
onto main, mechanical hard-set re-run, pinned-approval check, squash + trailers,
and journal the admission's state_transition with body to: merged through the
Journal seam (the promoted envelope field, section 6 -- D3 reconcile and the
prompt 9 gate both key on it).
Both writer lanes (squash-merge to main + ticket-plane commits) run inline in the
one CLI process under the single-writer lockfile; the dedicated serial merge task,
red-streak pause, and tree-hash assert are Phase 3. All git through git.py. TDD
tests/test_merge.py against a temp repo: a passing ticket merges with trailers; a
failing hard gate
blocks admission. Stop when uv run pytest is green.
```

8 -- Non-ok terminal:
expects: tests/test_terminal.py

```
Implement non-ok terminal handling per CHUPA_PLAN.md section 11 and section 19
(Phase 1): a non-ok terminal -- a spent cap or any non-ok terminal state --
journals its state transition and exits 1 (the section 18 exit-code contract:
1 = a ticket outcome, 2 = an engine-plane refusal), leaving the ticket and branch in
place. Retry, diagnosis, and auto-harvest arrive with the Phase 2 spine, so build
none of them here (the reject-findings re-entry RENDERING ships with the
prompt 11-12 drain pair, section 11.2). TDD tests/test_terminal.py: a stage returning non-ok leaves
branch + ticket intact,
journals the transition, and the process exits 1 (an engine-plane refusal exits 2 --
section 18's exit-code contract). Stop when uv run pytest is
green.
```

9 -- Phase 1 exit gate:
expects: -

```
Drive the Phase 1 exit per CHUPA_PLAN.md section 19. Author ONE real ticket and run
it IMPLEMENT-onward to a local merge on main -- single worker, real model,
complete artifacts + provenance events, both writer lanes inline (`run <stem>`,
operator-invoked, is itself the supervised-merge go-ahead, section 12). The
prompt 2 baseline record STANDS as the bootstrap-era record -- do NOT re-run
the harness here: its outcome changes nothing the bootstrap does (the drain
is exempt, section 19), the section 12 policy reads identity at read time so
prompt 6's wired specs already resolve any drift to supervised mode, and the
GO-grade baseline is earned immediately before cutover, where GO is first read
(the Phase 6 deliverable; section 13 touchpoint 7). Phase 1 is done when the real ticket is merged
with complete artifacts and events. After this, chupa consumes its own
tickets -- stop hand-prompting and start authoring tickets.
```

10 -- Reconcile-on-entry (reap orphaned in-flight runs):
expects: chupa/reconcile.py tests/test_reconcile.py

```
Implement reconcile-on-entry per CHUPA_PLAN.md section 11 and `19.P1`:
when a `run`/`drain` scaffold acquires the single-writer lockfile, BEFORE it
dispatches, reap any orphaned in-flight run an interrupted predecessor left -- a
ticket the journal shows `running` with no terminal transition, or an
`effect_intent` with no matching `effect_completion`. The scaffold holds the sole
writer lock and no daemon exists, so such a run is provably dead. Reap is
fail-closed and minimal here: journal an `abandoned` terminal state_transition for
each orphaned ticket (never hand-edit the journal -- APPEND through the Journal
seam) and remove its orphan worktree via git worktree remove + prune through
git.py (never bare rm -rf). This is the foreground form of the Phase 3
restart-reconcile; auto-harvest of the orphan (section 11.2) folds in with the
Phase 2 spine, not here -- build no harvest. TDD tests/test_reconcile.py against a
temp checkout: a journal
with a `running` and no terminal is reconciled to `abandoned` and its worktree
removed on the next `run`/`drain`; a clean journal is a no-op. Stop when uv run
pytest is green.
```

11 -- Drain verb (run the ready queue: dispatch, park, retry accounting):
expects: chupa/drain.py tests/test_drain.py

```
Implement the `drain` verb per CHUPA_PLAN.md section 18 and `19.P1`:
drive every ELIGIBLE ticket -- validated, committed, depends satisfied, not
blocked -- through the same path as `run <stem>`, one at a time in the single
process holding the single-writer lockfile, in `depends`-constrained
(priority, age) order, to QUIESCENCE: a non-ok ticket terminal PARKS that stem and the drain continues;
a merge landed mid-invocation satisfies depends edges in the same invocation;
at quiescence -- nothing eligible and unparked -- each parked stem whose
`retry` cap (section 11.1) still holds budget is RE-OFFERED, one retry unit
drawn per re-offer, each draw journaled as a `cap_consumed` event and
remaining budget derived from the journal at entry (a LIFETIME budget per
stem, never an in-memory counter -- section 11.2), eligible work always
running ahead of re-offers, and
quiescence re-evaluated after every re-offer merge so unblocked dependents run
in the same invocation. After EVERY merge, RE-SCAN the committed tickets dir, so
a ticket authored or confirmed DURING the invocation -- a seeding ticket's
output committed to main via the ticket-plane lane -- becomes eligible in the
SAME invocation (section 18's true quiescence, tickets-dir half ONLY; the
Suggestion-Box re-consume is the Phase 2 box consumer's job, NOT this verb's).
The drain ends when nothing is eligible, unparked, re-offerable, or newly
authored, reporting every still-parked red with its findings. Two config bounds
(section 15, the `drain:` block) stop an unattended drain short of quiescence:
the overall wall-clock ceiling `config.drain.max_runtime_hours` -- on trip,
admit no NEW ticket, let the in-flight one reach its stage terminal, journal the
halt, report progress, and name the continuing `chupa drain` (a runaway
backstop, distinct from a quiescence stop, never a mid-stage kill); and the
per-ticket ceiling `config.drain.max_ticket_minutes` -- a ticket whose authored
`Time budget` stuck exceeds it PARKS at dispatch with a paved road (lower the
budget), never running. The reject-findings re-entry RENDERING is prompt 12's
deliverable, completed BEFORE this drain ever runs a seeded queue (section
11.2's re-entry-ships-with-the-drain law binds the 11-12 pair): leave the
render call as a seam here and build no folding logic. Engine-plane
refusals (lock contention, journal corruption, config/setup refusals) still
stop the drain. Fail closed:
an empty ready set is reported, not an error; a depends cycle is refused with a
paved road; no ticket runs before the tickets it depends on have merged. This is
the foreground precursor to the Phase 3 daemon's dispatch loop --
build no async, no worker pool, no queue persistence. The self-upgrade
re-exec and the premise_failed park are prompt 13's deliverable: leave the
re-exec trigger as a called seam here and build neither. TDD tests/test_drain.py
against a temp checkout:
two tickets with a depends edge run parent-first; two equal-priority stems with
distinct authoring-clock events dispatch older-first, and a stem with no
authoring event sorts after any stem with one (section 9's age term); a red
INDEPENDENT first ticket
parks and the second still runs, the red reported at the end; a ticket red on
its first attempt and green on its re-offer merges in the SAME invocation,
exactly one retry unit drawn, and a dependent blocked only on it runs in that
same invocation; a stem whose retry cap is spent stays parked and
is reported, never re-offered; a retry unit drawn in one invocation is still
spent in the NEXT invocation -- budget re-derived from the journal by counting
retry-NAMED `cap_consumed` events (never all caps, so a later cap in the
vocabulary never perturbs a retry-budget assertion -- section 11.2), never
carried in memory; a child whose
parent merges mid-invocation runs in the same invocation; a ticket committed to
the tickets dir DURING the invocation (a running ticket's ticket-plane commit of
a new `confirmed` stem) runs in the SAME invocation with no re-run; a fake clock
advanced past `max_runtime_hours` stops the NEXT dispatch, names the ceiling in
the report distinct from quiescence, and leaves the in-flight stage
un-interrupted; a ticket whose `Time budget` stuck exceeds `max_ticket_minutes`
parks at dispatch with its paved road and never runs; an empty queue
reports and exits zero, quiescence with parked reds still exits zero, and a
ceiling halt exits 1 (the section 18 exit-code contract). Stop when
uv run pytest is green.
```

12 -- Reject-findings re-entry (findings-fed re-offers):
expects: chupa/drain.py tests/test_drain_reentry.py

```
Complete the `drain` verb's re-entry per CHUPA_PLAN.md section 11.2 and
`19.P1`, behind the render seam prompt 11 left: a stem
re-entering after a non-ok terminal folds the prior terminal's findings
artifacts already durable in its ticket dir (review.md reject findings, a
failing checks.json) into the prior-attempts data section of the next
attempt's render -- rendered fresh each attempt IN CRITERIA-POSITION per
section 11.2, never written into ticket.md -- so no drain is ever
findings-blind (a blind re-run repeats its failure unchanged and parks; this
11-12 pair IS section 11.2's re-entry-ships-with-the-drain law, and no seeded
queue runs before both land). TDD tests/test_drain_reentry.py against a temp
checkout: a re-offer's rendered prompt provably contains the prior attempt's
reject findings, positioned in the same prompt section as the acceptance
criteria; a first attempt's render carries no prior-attempts section. Stop
when uv run pytest is green.
```

13 -- Drain self-upgrade re-exec + premise park:
expects: tests/test_drain_upgrade.py

```
Finish the `drain` verb per CHUPA_PLAN.md section 18 and `19.P1`,
behind the seam prompt 11 left. An admission whose diff touches chupa/** or
specs/** re-execs
the drain through the process-exec seam as `uv run python -m chupa drain` --
ONE form, dependency changes included, D1's named runtime exception -- the parked
set carried in argv, via the section 18 HANDOFF: journal the handoff, close
journal handles, RELEASE the single-writer lock, spawn with timeout=None and
inherited stdio, await, exit with the child's code. A stem whose last
terminal was premise_failed stays parked across invocations until its
ticket-plane ticket.md commit changes (section 18) and is never re-offered.
TDD tests/test_drain_upgrade.py against a temp checkout: a self-upgrading
admission re-execs before the next dispatch (fake the exec seam; assert the
HANDOFF ORDER -- lock released and journal closed BEFORE the spawn -- plus
the uv-run argv form, timeout=None, and that the parked set survives); retry
budget spent before the re-exec is still spent in the child -- journal-derived
per section 11.2, never re-armed by the exec; a premise_failed stem is
skipped by the next invocation
and runs again after a ticket edit lands. Stop when
uv run pytest is green.
```

14 -- Phase 1 -> Phase 2 handoff, batch 1 of 4 (caps + auto-harvest):
expects: tickets

```
As the first of the conductor's four final seeding acts (prompts 14-17 author
the Phase 2 queue in `depends` order; nothing dispatches until the operator
launches `chupa drain` after prompt 17), author the first Phase 2 seeds per
CHUPA_PLAN.md `19.P2` and section 11: one ticket.md per
deliverable, written under tickets/<stem>/ as real specs -- caps FIRST, scoped
to diagnosis and the infra budget (the `retry` cap with its journal-derived
`cap_consumed` accounting already shipped with the Phase 1 drain, as did the
reject-findings re-entry -- section 11.2 -- so every spine ticket runs
findings-fed and retry-bounded; this ticket rebuilds NEITHER; the
`premise_bounce` cap and its DRAW land with the escalation ladder + Reject
queue seeds of prompt 16's batch, beside the confirm/reject release verbs -- a
hold never lands before its release, section 2), then auto-harvest before wipe
(allowlist extraction, attempts/ dirs; harvest EXTENDS the section 11.2
rendering, never a second path). AUTHORING LAW, binding every seed in prompts
14-17 (sections 9, 13, 18, 19): every seed is a real spec written under
tickets/<stem>/; each '## Context' bullet a repo-relative path
that EXISTS (the read-first set), plan prose entering only through `Plan
contract` ids (section 13) -- `19.L`, `19.P2`, and the owning sections the
deliverable needs, never whole section 19 and never a whole-plan path; a
fenced existing file whose embedding breaches the section 8 authoring
headroom listed under '## On-demand' instead of Context; each '## Scope
fence' includes every file the acceptance criteria force AND fences the module
that OWNS each hooked seam (section 9 ownership law); seeds ordered by
`depends`/priority so `chupa drain` runs them in a sound order; `Time budget`
by rule, never feel -- expected sized to the deliverable, stuck = 2x expected
-- and every seed DISPATCHABLE under this instance's drain envelope: a stuck
budget over `config.yaml`'s `drain.max_ticket_minutes` parks at dispatch
(section 18), so size that ceiling to at least the largest seed's stuck --
the shipped default (90) sits below the spine's biggest tickets, the envelope
that admits the seeds ships WITH them (never lowering a ticket's authored
stuck threshold, its real hang bound, to fit a dispatch gate), and RAISING
that one key (upward only) is the ONE sanctioned edit of the operator-owned
config.yaml (prompt 1's never-overwrites rule governs every other key -- the
specific command here wins over the general rule); every seed stamped
`confirmed` at authoring (bootstrap seeds are the build plan, never
suggestions -- nothing waits at a draft gate or on a `confirm` verb the seeded
phase has not built yet); the pre-ladder tier rule of section 19 (HIGH tier
until the ladder merges; known-hard seeds high/high with cited evidence).
Author SPECS only; implement none of the code -- chupa does that when the
human runs `chupa drain`. Do NOT author Phase 3+ tickets: their specs depend
on what Phase 2 builds and learns (D10). Stop when the batch's stems exist
under tickets/ and uv run pytest is green.
```

15 -- Phase 1 -> Phase 2 handoff, batch 2 of 4 (diagnosis + its eval):
expects: tickets

```
Author the second Phase 2 seed batch per CHUPA_PLAN.md `19.P2`
and section 11.3, depends-ordered after prompt 14's stems: the diagnosis call
with `lessons` over the harvested material (the sandwich's one model judgment
-- closed verdict vocabulary, mechanical short-circuits), and the diagnosis
real-model eval as its TWO chained deliverables (section 19): first the
harness + committed fixture set, its expected verdicts proven reachable under
the fake LLM and its budget/timeout enforcement pinned by tests against the
committed report artifact; then the spend ticket that only EXECUTES the
already-merged harness. Prompt 14's AUTHORING LAW binds every seed here (it
restates sections 9, 13, 18, 19 -- read those sections). Author SPECS only;
implement none of the code. Stop when the batch's stems exist under tickets/
and uv run pytest is green.
```

16 -- Phase 1 -> Phase 2 handoff, batch 3 of 4 (Suggestion Box + ladder + triage):
expects: tickets

```
Author the third Phase 2 seed batch per CHUPA_PLAN.md `19.P2` and
sections 11-12, depends-ordered after prompt 15's stems: the Suggestion Box
BEFORE anything that files into it (durable queue, signature dedup, decision
registry, and the harvest wiring that enqueues each run record's second
problems -- the mailbox exists before its first letter; its spec includes
one-time ingestion of bootstrap/suggestions.md, the section 0 stand-in, as the
box's first messages -- ONE suggestion-class message per non-empty line --
that file then retired: deleted in the box deliverable's own reviewed code
diff, its `## Scope fence` naming `bootstrap/suggestions.md` (section 19),
never a ticket-plane commit; the storm-control circuit breaker is a Phase 3
seed beside the daemon's continuous producers, and tombstone auto-reopen +
retro itemization are Phase 5's, with the retro stage that reads them --
section 19), then the escalation ladder ending at the Reject queue WITH its
confirm/reject verdict verbs AND the `premise_bounce` cap and its draw landing
before any hold can fire (a hold never lands before its verdict verbs or its
release -- section 2, enforced by `depends` chaining across these seeds; every
seed that WRITES a marked terminal fences the terminal-write owner
(chupa/runner.py, section 9 ownership law) plus the stage layer whose
outcomes feed it (chupa/stages.py), and the Reject queue itself is a
journal-derived projection that writes no terminal -- section 19; the
pre-daemon default is auto-keep while retry budget remains, section 11.4),
then the box's sequential triage consumer (the machine route from a filed
problem to a ticket change) -- invoked ONLY by the operator verb `chupa
triage` (BOOTSTRAP era): ONE pass over every pending box item -- author,
tombstone, or decision-record each -- then STOP. The bootstrap drain NEVER
scans the box itself: no scan before dispatch, none after a merge (sections
12, 18). A box-authored ticket takes its section 12 table default -- almost
always `draft` -- and the operator who ran `chupa triage` confirms only the
few worth building; there is NO self-build auto-confirm exemption, because a
human is present at every scan and nothing from the box need run unattended.
`chupa/policy.py` resolves box starting-state from the table plus scope
override in BOTH eras with NO drain special-case; the seeds pin
`tests/test_policy.py` (a bootstrap box ticket resolves `draft`) and
`tests/test_drain.py` (a drain does NOT scan the box). PHASE SEEDS are NOT
box-authored -- a phase's final ticket authors the next phase's `ticket.md`
files DIRECTLY as confirmed ticket-plane output (sections 12, 19); the
DAEMON-era continuous box consumer and its GO-gated auto-confirm (sections 9,
12) are a SEPARATE era, built with the daemon, never folded in here. Prompt
14's AUTHORING LAW binds every seed (the box and ladder seeds cap out at stuck
150-180m). Author SPECS only; implement none of the code. Stop when the
batch's stems exist under tickets/ and uv run pytest is green.
```

17 -- Phase 1 -> Phase 2 handoff, batch 4 of 4 (Author + requisition_review + battery + auditor + exit seed):
expects: tickets tests/test_seeded_phase2.py

```
Author the final Phase 2 seed batch per CHUPA_PLAN.md `19.P2`,
depends-ordered after prompt 16's stems: the Author stage + specs/author.md
the triage consumer feeds (deferred from Phase 1, where nothing executes them
-- sections 4-5 and 8); `requisition_review` as its THREE chained deliverables
(section 19: the pure review call + spec + gate registration, then the
Author-path consumer, then the seed-path consumer at the seeding ticket's
Check stage with MERGE-SAFETY enforcement, each fencing the module that OWNS
its seam); then the phase's Emits as seeds of their own -- the invariant
auditor, and the shakeout battery as its per-owning-module chained groups plus
the report-lane deliverable (section 19: machine-produced shakeout-report.json
lifted by the one stage-terminal lift path, double-gate re-confirmation; the
battery's pass condition is that auditor) -- then LAST the Phase 2 exit
ticket, its depends transitively covering EVERY Phase 2 seed: it performs the
`19.P2` exit read and authors Phase 3's seeds in the `19.L` core-first chain
(the `19.P3` registry's core admission plus one phase3-continue seeding ticket), by
DIRECT ticket-plane authoring -- its Implement stage writes Phase 3's
ticket.md files `confirmed`, intake-lint validated AND feasibility-reviewed
(`requisition_review`) at its own Check stage, picked up by the drain's
after-every-merge tickets-dir re-scan (section 18) -- NEVER by filing a
Suggestion Box message (the box carries filed problems, never a known
build-plan ticket), and every later phase boundary seeds the same way. Prompt
14's AUTHORING LAW binds every seed. Author SPECS only; implement none of the
code. Do NOT author Phase 3+ feature tickets beyond that core batch and its `-continue` tail (D10). Add a
test (tests/test_seeded_phase2.py) that every seeded Phase 2 ticket passes
intake lint, that every seed's stuck budget is at or under the configured
`drain.max_ticket_minutes` (section 18), AND that the seeded depends edges
realize the deliverable order stated above (section 13 authoring law) -- the
test NAMES its phase's seed stems explicitly and asserts only over those named
stems, never a `source: seed` pattern-match over the tickets plane (every
later phase's seeds carry the same stamp, so a scan would be reddened by a
later seeding from outside this test's own fence); each seeding ticket ships its own per-BATCH named-stem test FILE the same way -- section 19's bounded-batch seeding puts SEVERAL seeding tickets in one phase (the phase-exit core batch, `<phase>-continue`, and any further continuation), and two writers of one per-phase file are a guaranteed conflict in the serial merge queue's rebase -- while the rung-1 resolution machinery is itself a downstream batch: each batch writes its OWN new test file (its Scope fence, never Context), reading the prior batch's merged file for the idiom. PIN GRAIN is law for every such test: it pins IDENTITY and STRUCTURE -- the named stem set, `depends` edges, `source: seed` and other frontmatter values, grammar validity -- and NEVER byte prose, phrase substrings, or criteria counts, because sanctioned machinery legitimately rewrites what byte pins freeze: the section 13 `reject <stem>` kill stamps `rejected`, Rework update/split rewrites criteria and supersedes stems (sections 4, 11.4), and the section 18 premise-park road releases a stem only through a new `ticket.md` content commit. So a state or existence assert accepts the full lifecycle (a later `rejected` stamp or supersedes-map entry is history, not drift); a live-queue assert (dispatchability, awaiting-terminal) is banned outright -- the test classifies only the CLOSED list of its own batch's stems as historical, and a confirmed later-phase stem mid-run is never required to show a terminal event; the section 19 known-hard tier pin asserts the frontmatter tier values and THAT the citing evidence exists, never its wording; and the section 19 invariant-to-test closure obligates tests of the built rule's BEHAVIOR, never a string-match over the prose that states it. Two further closure rules the batched form forces: (1) PINNED MATERIAL -- a seed test's rendered material is a permanent deterministic fixture (the section 15 replay-corpus law), never live engine bytes: every size, Context/On-demand partition, plan-unit length, and max-effort render it asserts is computed from values RECORDED IN THE TEST at authoring, never re-read from live files, live markers, or the live plan, because a test that reads live state reddens later, historical, and out-of-fence when a fenced module legitimately changes; once its seeds merge, a seeding test is an immutable historical fixture no later ticket fences or migrates; (2) AUTHORED-STATE ONLY -- it asserts the seed's authored content and `confirmed` birth, never byte-identity against lifecycle state: the section 13 terminal `rejected` stamp into an authored seed's `ticket.md` is a sanctioned later transition that must not redden a merged seeding test. Stop when uv run
pytest is green. After this the conductor is retired: the human runs ONE
`chupa drain` that carries Phase 2 and every later phase to quiescence
(section 19), each phase's final ticket seeding the next as `confirmed` into
the same running drain.
```

## 1. What chupa is

A continuously running orchestration engine that authors and runs tickets against host project repos, including itself: it drafts the ticket set for a feature, wires dependencies, runs implement -> check -> review -> merge, harvests failures, and files follow-ups.

The ticket lifecycle is named after a business procurement cycle, with code development activities in place of the business activities:

| Procurement stage    | Dev activity                | Actor      |
|----------------------|-----------------------------|------------|
| Requisition          | Author ticket(s)            | LLM        |
| Fulfill & Ship       | Implement code              | LLM        |
| Invoicing            | Lint / acceptance checks    | script     |
| Inspect & Accept     | Code review                 | LLM        |
| Rework               | Update/split/escalate ticket| LLM        |
| Reject               | Human keep/edit/kill queue  | human      |
| Approve & Pay        | Approval record             | script     |
| Settle Payment       | Merge to local main         | script     |
| Reconcile            | Retrospective + cost ledger | LLM        |

The table is also the operator vocabulary: every operator-facing surface (CLI output, escalation text, README) speaks it or plain English; scheduler jargon stays in the spec and the code.

Design goals, in priority order:

1. Simple and robust over feature-rich; check/feature accretion is the primary failure mode designed against.
2. Automated: human touchpoints are enumerated and small.
3. Continuous queue, not batches, with live re-prioritization.
4. One consistent pattern for every stage, gate, and handoff.
5. Every failure path is designed.

Non-goals for v1: multi-machine execution, a composition/plugin engine, a web UI, GitHub PRs in the loop, deterministic re-execution recovery, fleet management (section 15).

## 2. Design law and anti-goals

Design law -- principles every section below must satisfy:

- **Rule surfaces fail closed.** Allowlists and closed vocabularies, never denylists; a paved road ships inside every prohibition; mechanical enforcement backs prose; exactly one narrow, auditable exception valve per gate.
- **A hold ships with its release.** Any state that suspends a ticket pending an outside verdict or change -- the Reject queue, a premise park, a poison quarantine -- lands WITH OR AFTER its release path -- in the same deliverable, or in a deliverable whose `depends` chain guarantees the release merged first -- and its paved road never names a verb that is not yet built. A hold whose only release is a ticket change may not precede the machinery that machine-produces ticket changes (sections 11, 12). A hold that can strand a ticket with no reachable release is fail-stuck, not fail-closed.
- **Failure recovery is a mechanical sandwich.** Deterministic machinery outside, exactly one model judgment call in the middle, deterministic dispatch out; caps are checked before the model is called. Two distinct retry senses: cross-attempt retry (section 11.4) is a fresh workspace from the top, never resume; the in-stage re-prompt loop (section 5, invariant 2) feeds gate findings back against the SAME workspace, bounded by the retry-like-action cap. When the deterministic layer can tell that asking the model is pointless, it does not ask.
- **The ticket is the contract; the run record is the receipt** (section 13), with predicted-vs-actual divergence as the calibration signal.
- **No dual-path code.** No compat shims, defensive parallel codepaths, or deprecation layers for internal surfaces; rename in place and update every call site in the same change; recovery is git revert.
- **Executed work is fenced by gates, not jailed.** v1 does not sandbox agent subprocesses or ticket-authored commands; on a single-operator personal box they run with the operator's own privileges (section 16). Gates and review are the trust boundary, never the goodwill of executed code.
- **Operator surfaces speak plain language.** Names a human reads or types -- CLI verbs and options, report lines, error text, ticket stems -- use ordinary words, parseable without this plan; plan-internal shorthand (spine, box, plane, quiesce) never reaches an operator surface. Internal vocabulary (journal event types, outcome enums) may stay terse. An existing violator renames via ticket when next touched, per the dual-path law.

Anti-goals -- failure modes this design prevents, each addressed by a numbered decision:

- No consistent pattern between steps for gates and handoffs (-> D4).
- Feature/check accretion that makes automation brittle (-> D10).
- Batch-oriented scheduling fighting a continuous queue (-> D6).
- One author-declared path list overloaded to do both conflict prediction and scope bounding (-> D7).
- A remote code host's PR machinery inside the dev loop (-> D8).
- Shell scripting as orchestration glue (-> D1).
- Metadata accreting to serve subsystems that do not exist yet (-> the anti-bloat law, section 13).

## 3. Core decisions

- **D1 -- Pure Python.** No bash anywhere: no shell scripts, no `shell=True`, no string-assembled commands. External binaries (git, agent CLIs) are exec'd with argument lists through dedicated wrapper modules. One chupa-owned venv, created and populated with `uv` (setup only, with ONE named runtime exception: the bootstrap drain's self-upgrade re-exec runs `uv run python -m chupa drain` through the process-exec seam, section 18), on Python 3.14+ (the pinned floor); startup refuses any other interpreter or a lower Python. Why: a stopped drain waiting for a human to retype the command is the failure the bootstrap contract bans (section 19); 3.14 raised from 3.11 for currency and EOL runway to Oct 2030, above the language features actually used (`tomllib` at 3.11, PEP 604 unions at 3.10).
- **D2 -- Single asyncio daemon.** One process, ONE in-flight ticket run (single-flight dispatch) -- through the entire self-build and the first daemon era. A concurrent worker pool is a post-cutover D10 return earned by measured queue starvation on host work; it multiplies the review surface and the conflict surface faster than any other knob, so it is never a default. No leases, no heartbeat protocols, no distributed locks. Crash recovery is restart + rescan + reconcile against the journal. A single-writer lockfile per project checkout (carrying instance identity) fences the orchestration write surfaces -- ref mutation, commits, the journal, dispatch state -- against a second daemon or a chat session; hand-editing FILES under the tickets dir is OUTSIDE the fence (the human intake path, section 13, safe because only the daemon commits). Reconcile scans from the journal tail; an additive `checkpoint` event shape is RESERVED (not built in v1) so bounding the scan later is a new event type, not a schema rewrite -- it ships per D10 only when a full rescan actually hurts.
- **D3 -- Files + journal are the source of truth.** Tickets and artifacts are markdown/JSON files in the host repo, committed via the serial writer's ticket-plane lane (section 10); every state transition and external action is an event in an append-only JSONL journal. Derived views (status, backlog, ledger, scorecard) are projections, never authoritative; no index builder -- every projection is a stdlib read-time fold over the JSONL (an analytics engine such as DuckDB is a D10 return at the first projection measured too slow as a fold). Crash precedence: for an externally observable effect the WORLD wins (a branch/file/main row that exists is truth) and reconcile re-derives the journal note -- a merged ticket specifically from the squash commit's `chupa-ticket` / `chupa-reviewed-sha` trailers (section 10), the identity a deleted branch no longer carries; the journal is authoritative only for intent and non-observable effects. Durability: artifact and ticket writes are atomic (temp file, fsync, rename); the journal is append-only, one JSON object per line, and every reader tolerates a torn trailing line -- a crash mid-append drops the partial record, no reader aborts.
- **D4 -- One stage contract** (section 5). Stages communicate only through schema-validated artifacts on disk plus the journal. One driver runs every LLM stage. One gate shape. One outcome vocabulary.
- **D5 -- Fail-closed gates only** (section 7).
- **D6 -- Continuous scheduler** (section 9). No waves, no groups, no batch verbs. Ordering comes only from `depends` and `priority`; a file watcher makes priority edits and new tickets take effect at the next dispatch.
- **D7 -- Scope is fenced by a gate; conflicts are resolved at merge** (section 9). No author-time conflict prediction anywhere; the serial merge queue is the one place conflicts are resolved. Scheduling may AVOID manufacturing a conflict only on observed facts, never on estimates -- the overlap law and its dispatch-skip / pre-review-hold checkpoints (section 9).
- **D8 -- GitHub out of the dev loop** (section 10). Local main is the blessed line; merges are local; GitHub is a non-blocking checkpoint sidecar.
- **D9 -- Thin primitives kernel** (section 6). Journal, Effect, Signal, Timer adopted in minimal form; re-execution recovery, hash chains, blob stores, and the composition engine refused.
- **D10 -- Every feature earns its place with an incident.** The only way a gate, check, or subsystem is added is the surprise -> rule -> gate promotion path, with the incident cited in its docstring. Retro reports catch-rates and proposes deleting gates with zero catches over N tickets. Gate count is a managed budget, not a ratchet. The v1 core set is the one seed grant, chosen by design rather than incident; D10 governs every addition beyond it, and retro's prune path applies to the seed set the same as to earned additions.

## 4. Lifecycle and artifacts

Every stage consumes one typed artifact and emits one typed artifact; the procurement documents are the artifacts:

- Requisition consumes a triaged Suggestion Box message (section 12 -- the one machine route into authoring; human intake authors ticket files directly, section 13) and emits the **ticket** (one or more, with a dependency graph).
- Implement emits the **packing slip**: a branch plus a run record.
- Invoicing (mechanical) emits the **invoice**: a structured check report.
- Inspect emits an **approved invoice**, a **snag list** (to Rework), or an **RMA** (to the human Reject queue).
- Rework emits a **rework order**: updated ticket, split tickets, and/or a model-tier escalation (the escalation element is consumed by the section 11.4 ladder's journal-derived rung, never written into ticket frontmatter).
- Approve (mechanical) emits an **approval record** -- an attestation (approver surface identity + reviewed SHA + the spec versions + the resolved gate set: the plain list of gate codes, review-surface names, and severities in effect at approval time), not a cryptographic signature -- pinned to the reviewed commit SHA. The approval record persists in the JOURNAL, as the body of the admission's `state_transition` (its pydantic model, section 13) -- never a ticket-dir file: the section 13 ticket-dir listing is closed, and `review.md`'s pinned verdict is the merge gate's on-disk input.
- Settle (mechanical) merges via the merge queue.
- Reconcile emits **retro findings** into the Suggestion Box.

LLM stages: Author, Implement, Review, Rework, Suggestion-Box triage, Retro. A second engine review surface, `requisition_review`, judges an AUTHORED TICKET rather than a diff -- the feasibility review that runs before a ticket commits confirmed (section 7). Everything else is a script. Judgment goes in LLMs; verdicts go in scripts.

## 5. Kernel contracts

```python
class Stage(Protocol):
    name: StageName          # closed vocab: author|implement|check|review|
                             #   rework|merge|triage|retro
    kind: Literal["mechanical", "llm"]
    consumes: type[Artifact] # pydantic v2 model, schema-validated on read
    emits: EmitSpec          # ONE type, OR an emits_by_verdict map for branch
                             #   stages (review: approved-invoice | snag-list
                             #   | RMA; triage's verdict-keyed set, section 12;
                             #   rework emits ONE composite rework-order type,
                             #   section 4); keys are stage-local verdicts,
                             #   NOT Outcome values; schema-validated on the
                             #   branch taken
    gates: list[GateCode]    # gates that validate the emitted artifact

@dataclass(frozen=True)
class StageResult:
    outcome: Outcome         # ok | already_satisfied | invalid_artifact |
                             #   gate_failed | premise_failed | timeout |
                             #   infra_error | budget_exceeded
    artifact: Artifact | None
    findings: list[Finding]  # {code, path, line, message, paved_road}
    cost: Cost               # tokens, seconds, attempts, plus usd + provider +
                             #   model on LLM calls (usd=0, provider/model=None
                             #   for non-LLM effects); the effect_completion
                             #   event carries the same fields (section 6 ledger)

class Gate(Protocol):
    code: GateCode           # engine-shipped closed vocab (section 7 v1 set):
                             #   ticket_schema | scope_fence | verification |
                             #   run_record | diff_budget | post_rebase_regate |
                             #   bug_evidence | core_drift (both land Phase 6:
                             #   bug_evidence v1-deferred to its first
                             #   consumer, core_drift additive per D10,
                             #   sections 7, 8, 19) | correctness_review |
                             #   requisition_review. Host review surfaces
                             #   register more codes (own gate budget).
                             #   correctness_review at merge = the pinned-
                             #   approval check for the admitted SHA, never a
                             #   re-executed model call (section 9).
    def check(self, artifact, workspace) -> GateReport
    # GateReport: {code, verdict, findings, autofix_applied}; verdict is
    #   the closed pair pass | fail -- hard/soft severity is applied by
    #   the runner from config (invariant 3), never carried in the report
```

Invariants:

1. Stages communicate only through artifacts on disk plus the journal. No side channels, no shared mutable state. Every artifact EXCEPT the ticket (exempt per the versioning policy below) records the spec version and commit SHA that produced it (provenance): base-model fields `produced_by_spec_version` and `produced_at_sha`. `produced_at_sha` is the HOST-repo commit the stage's workspace was at (main for author/triage-time artifacts, the branch HEAD for implement/review-time ones) -- in the self-hosted case that commit legitimately IS an engine-repo SHA; what it never records is the running instance's own release identity.
2. One driver runs every LLM stage: render spec -> call model -> validate artifact schema -> run gates -> on hard failure feed structured findings back and RE-PROMPT the same workspace within caps -> escalate. A schema-INVALID artifact -- including a verdict value outside its closed vocabulary -- is a validation failure that takes this same bounded re-prompt loop (the validation error fed back as the finding) before any terminal, never a full-cycle burn. Before validation the driver strips exactly ONE surrounding markdown code fence (optionally language-tagged) from the final output, because agent CLIs routinely wrap JSON that way; any other malformation takes the re-prompt loop. Stages differ only in spec file, artifact type, and gate list. For Implement, call-model may be an agent-CLI subprocess executing in the ticket worktree behind the LLM seam (`kind: cli`, section 6), granted write access to that worktree because Implement is the one surface that mutates the tree (the grant is per-surface and fail-closed, section 6); a re-prompt is a re-invocation of that subprocess with the structured findings appended.
3. Gate severity (hard/soft) lives in config, not gate code: for engine-shipped codes the `review.gate_severity` map (MERGE context, section 15; shipped default: the v1 hard set of section 7 is hard at merge), and for host-declared mechanical checks the per-entry `severity` field (section 7). Author-context severity is an engine constant (soft) until a configuration actually needs the second dimension -- the per-context map is a D10 return. Soft failure emits a Suggestion Box message and continues; hard failure feeds the retry loop.
4. `premise_failed` is a first-class outcome: Implement may return "the bug does not reproduce / this conflicts with X", routing back to Requisition with feedback instead of grinding out a bad implementation. `already_satisfied` is the complementary first-class short-circuit: an Implement that finds every acceptance criterion ALREADY holds on the base -- proven by running the ticket's own `## Verification` commands green, never by judgment alone -- terminates `already_satisfied`, and the ticket settles as a no-op (journaled `to: merged` with no code diff; regenerated or reseeded work frequently arrives already built, and parking it as a false premise turns recovery into churn).
5. Autofix lints must be idempotent: run twice, assert fixpoint.
6. Branch stages (review, triage) emit one of several artifact types by stage-local verdict via `emits_by_verdict` (rework emits ONE composite rework-order type, section 4). Two named steps sit OUTSIDE the `StageName` vocab on purpose: `diagnose` is a failure-spine substep (section 11.3) and `approve` is a mechanical substep of `merge` (section 4). Model-facing config is keyed by `llm_surface`, a closed vocab (the LLM stage names plus `diagnose` and the engine review surface `requisition_review` of section 7, extended at config load with each host-declared review surface's `name`), used by prompt-spec frontmatter (section 8) and the provider routing table (section 6) -- so the diagnosis call gets a governed, versioned spec and a routing row without becoming a Stage, and a host surface can route to its own provider. A surface with no routing row of its own inherits the `review` row.

Every `Finding` carries a REQUIRED `paved_road` field -- a gate that cannot tell the agent what to do instead does not pass gate-lint; `path` and `line` are OPTIONAL (nullable), since a frontmatter- or schema-level finding has neither.

**Versioning policy** (one rule at every durable boundary): every persisted format that crosses a boundary carries a schema version, every reader refuses-newer and migrates-or-tolerates-older, and evolution is additive-only within a version (a field's meaning is never repurposed). Stamped surfaces: journal events (`v` per event); the base `Artifact` model (one inherited version field, `artifact_schema_version`, carried alongside and distinct from the invariant-1 provenance fields the base model also holds); the host config (`schema_version` handshake, section 15); the report inbox (engine refuses newer, tolerates older); the rendered `chupa:core` block (version + hash stamp); prompt specs (section 8). Ticket frontmatter deliberately carries NO version field -- and the ticket is likewise the ONE stage-emitted artifact exempt from the base-model `artifact_schema_version`/provenance fields (its provenance lives in the journal and the authoring stage's StageResult, so the closed frontmatter list in section 13 stays complete): tickets are ephemeral and flow between instances through git (successive engine versions operating one repo line -- concurrent divergence is excluded by the one-writing-instance rule, section 15), so a version-refusing parser would deadlock mixed-instance operation. Additive-only evolution plus strict closed-vocab authoring lint IS the ticket versioning provision; a breaking ticket-schema change ships by quiescing the queue and letting old tickets drain, never by migrating them. Quiesce = the section 9 kill-switch pause applied to DISPATCH only: stop admitting tickets, let in-flight ones finish and merge, so "drain" is a bounded, observable state. Across concurrent instances a breaking change is coordinated by pausing each instance's dispatch before the schema flip -- a manual v1 operator step.

## 6. Primitives kernel (adopt thin, refuse the rest)

### 6.1 Primitives

The kernel decomposes onto seven durable-execution primitives (the set Temporal, Restate, and DBOS converged on). Verdict per primitive:

| Primitive  | Adopt? | v1 form |
|------------|--------|---------|
| Journal    | yes    | JSONL event log, schema-versioned events. NO hash chain, NO content-addressed blob store (no v1 consumer). |
| Effect     | yes -- biggest win | one wrapper (`@effect(key=...)`) for every external action: git ops, LLM calls, ticket emission, notify, push. Owns journaling, idempotency key, cost capture, once semantics. |
| Signal     | yes -- as convention | human inputs (confirm, reject verdict, kill switch) are journal events. Completes the human-oversight audit trail. |
| Timer      | yes -- tiny module | journaled deadlines re-armed at daemon startup ("retro after M days", checkpoint pushes, stuck thresholds surviving restart). Built in Phase 3 with the daemon, its first consumer (D10). |
| Lease      | mostly no | ONE single-writer lockfile per checkout with instance identity; in-process asyncio locks otherwise. No general subsystem. |
| Step       | already have | it is the Stage protocol + driver. Skip the determinism formalism. |
| Projection | as a rule | derived views never authoritative. Satisfied by stdlib read-time folds over the JSONL. |

Explicitly refused: DBOS-style deterministic re-execution recovery. Why: the discipline tax (all nondeterminism through injected seams) buys nothing over the proven model (retry = fresh worktree from the top, daemon recovery = rescan + reconcile); without re-execution, hash-chaining and Step formalism have no consumer.

### 6.2 Journal

**Journal file layout and rotation.** The journal is a `journal/` directory of append-only JSONL SEGMENTS under the host's config-declared state dir (never a hardcoded path, section 15). One ACTIVE segment is appended and rolls at a size/age threshold (engine constants: 64 MiB or 24 hours, whichever first). The roll trigger ships with its first retention consumer, the Phase 3 daemon (section 19) -- the segmented layout and readers land in Phase 0, and pre-daemon the active segment simply grows. Rolled segments are IMMUTABLE, so the append-only law and torn-tail tolerance apply only to the active segment's tail. Segment names sort in write order (zero-padded sequence + roll date, e.g. `000001-20260804.jsonl`), so `read_json_auto` over a `journal/*.jsonl` glob reconstructs the ordered stream (D3's no-index-builder rule holds). v1 NEVER deletes or compacts a segment; retention/GC is the deferred ARCH block, returning via D10. `Journal.read_segments()` is the ONE parser -- it yields each ordered segment as its own ordered event tuple under the same corruption and active-tail rules -- and `Journal.read()` flattens it, so the auditor's per-segment laws need no filesystem reach-through. Reconcile and status read newest-segment-first; the reserved `checkpoint` event (D2) later bounds that scan to a suffix of segments.

Durability is write-ahead: an effect's intent event is fsync'd BEFORE the effect executes, completion events are fsync'd before anything dispatches on them, and background appends fsync at least every 3 seconds (an engine constant, not config) -- a crash can cost buffered non-load-bearing events but never an intent record, a Timer, a Signal, or a cap-consumption event the system acted on.

Both readers obey ONE law: tolerate exactly a torn FINAL line of the ACTIVE segment; any other malformed line -- mid-segment or in a rolled segment -- is a hard error surfaced as corruption, never skipped. The WRITER's startup dual: truncate a torn final line of the active segment before appending (append-only applies to records, not bytes), so a resumed append never creates a mid-segment malformed line and a roll never seals a torn tail into an immutable segment. (Bootstrap-surfaced hazard, filed to the sink per section 11: the startup dual runs only at startup, so a LIVE writer that tears its own active tail without dying -- a short write under `ENOSPC` -- then rolls that segment before any restart WOULD seal the torn tail into an immutable one. v1 does not guard the live path; repair-before-roll is the earned fix when it first fires.) Every projection reader validates rolled segments strictly and applies tail-tolerance only to the active segment (never a blanket ignore-errors read).

**Journal event envelope.** Every line is one JSON object with a fixed top-level shape -- `v` (event-schema version, per `type`, per the versioning policy above), `type` (a value from the closed `EventType` set below), `ts` (UTC from the clock seam in ONE pinned rendering: RFC 3339 with a `+00:00` offset, exactly an aware-UTC Python `datetime.isoformat()` -- pinned so lexicographic order IS chronological order, and readers, projections, and the bootstrap conductor may compare `ts` as a string), `ticket` (owning ticket stem or null), `key` (the effect idempotency key or null), and `body` (a `type`-specific object) -- so every type-varying field lives in `body`, never at top level. The closed `EventType` set (extended additively per D10, each type carrying its own `v`):

| `type` | emitted |
|--------|---------|
| `effect_intent`     | before an effect executes (write-ahead) |
| `effect_completion` | after it completes, carrying the result |
| `signal`            | a human input lands (confirm, reject, kill) |
| `timer_armed`       | a deadline is scheduled |
| `timer_fired`       | a deadline elapses |
| `cap_consumed`      | a failure-spine or budget cap is spent (section 11) |
| `state_transition`  | a ticket or run changes state |
| `checkpoint`        | RESERVED, not emitted in v1 (D2) -- bounds the reconcile scan later |

An unknown `type` on read is a hard corruption error, never skipped (the fail-closed law). Per-type `body` schemas are implementer-owned pydantic models, validated at the write seam and versioned by each type's `v` -- deliberately not enumerated here (same status as the non-`run.md` artifact bodies, section 13); the ENVELOPE, not the bodies, is the cross-version contract -- with TWO promoted body fields. First: every `state_transition` body carries `to`, the destination state's name from the closed RUN-STATE vocabulary -- `running`, plus the terminal states `merged`, `abandoned`, `rejected`, and each non-`ok` `Outcome` value (section 5) used as a terminal state name -- the vocabulary the section 15 invariant auditor validates against, because D3's world-wins reconcile and the bootstrap conductor's verdict gate both key on it. Second: a terminal `state_transition` that routes its stem to the Reject queue also carries the marker `routed: reject_queue` -- the field the section 9 eligibility fold reads. Everything else in a body stays implementer-owned.

### 6.3 Effects

**Effect contract (the once semantics reconcile depends on).** `@effect(key=...)` -- decorator sugar over the `Effects.run(action, *, key, ticket)` primitive, deferred to its first call site (the Phase 1 LLM call) while Phase 0 ships only the primitive -- is once-per-KEY against the surviving journal: on restart, an effect whose key already appears as a completed event is not re-run. That completed-key check reads the journal directly (D3, no index builder) -- the daemon holds an in-memory set of completed keys, scanned from the journal at startup and appended to as effects complete.

The key DOMAIN is chosen per effect class:
- attempt-EXCLUDING for user-visible side effects that must fire once across retries (notify / page / GitHub push key on ticket+event, so a retried run never double-alerts);
- reviewed-SHA for merge (merging a given approved SHA is idempotent);
- attempt-scoped for re-runnable work (a fresh worktree's git ops key on ticket+attempt, and an LLM call on ticket+surface+attempt+call_seq -- a monotone per-attempt sequence -- so each call records and replays deterministically and a re-prompt takes a fresh key, never a replayed result). A ticketless box-driven LLM surface uses the SAME universal key shape with the surface name in the ticket slot -- triage `llm/triage/<box message seq>/triage/<pass>/<call_seq>`, Author `llm/author/<pass>/author/<box message seq>/<call_seq>`, where `<pass>` counts prior `triage_pass` signals -- and spools under `spools/<surface>/...`, never a surface-specific bypass of the Driver or the LLM effect.

Every per-run key -- the attempt-scoped class and the ticket-plane RUN-artifact commits (run record, checks, review; the intake ticket commit is once per file and stays run-blind) -- additionally carries the RUN SEQUENCE: the count of this stem's prior terminal events (completed terminals and `abandoned` reaps) in the journal, derived at run entry by a read-time fold (D3, no counter file). Same-sequence replay is a WITHIN-PROCESS guard: only a re-entry with no intervening terminal replays, and every cross-process entry path reconciles FIRST (scaffold on-entry, daemon restart-reconcile -- section 11), reaping an interrupted run to `abandoned` -- so crash recovery is always a fresh sequence doing real work, and the cross-run once-guarantees live in the run-BLIND domains below (notify, merge). A run that reached ANY terminal is history: the next entry takes the next sequence, every key is fresh, and the re-run is real work. Keys are never retired and never deleted -- a superseded run's completions are inert journal history, unreachable by construction.

The attempt-excluding class and the reviewed-SHA merge key keep their domains run-BLIND on purpose: an alert fires once per ticket+event across all runs, and merging a given approved SHA is idempotent -- with ONE named exception: the spiral-warning notify key carries the run sequence, because a fresh run's spiral is fresh spend and must re-page (section 9).

Effects also split by OBSERVABILITY for reconcile: an externally observable effect (branch exists, file on disk, row in main) is reconciled by observing the world; a non-observable effect (notify) that crashed between acting and journaling is reconciled conservatively -- re-send beats a missed alert, and the attempt-excluding key prevents a storm. A fresh run's worktree creation is defined as TEARDOWN-AND-CREATE: any worktree and branch a prior run left are removed first (worktree remove + prune + branch delete, through git.py), then created fresh from current main -- so a fresh keyspace can never trip over a dead run's leavings.

Do NOT add a separate idempotency-class enum: the key already encodes the class. The `key=` argument is a callable over the effect's own arguments (`(args) -> str`; a bare string is allowed for a singleton effect), and the arguments it closes over ARE what select the domain above -- an attempt-excluding key omits the attempt number, an attempt-scoped key includes it. Key components join with `/` (the `key=retro/<seq>` convention, section 14): keys persist across restarts and self-upgrades, so the join is pinned, never per-call-site taste.

### 6.4 Single-writer lockfile

**Single-writer lockfile (the Lease row).** One advisory `flock` on the lockfile `<state_dir>/chupa.lock` fences the orchestration write surfaces (ref mutation, commits, journal, dispatch state) against a second daemon or a chat session. `flock` is chosen over an `O_EXCL` pidfile precisely because it needs no liveness protocol (D2 refuses leases and heartbeats): the kernel releases the lock when the holder dies, so a crashed daemon's lock is free at restart with no stale-pid reclaim. The file records the holder identity -- `{instance_id, pid, host, state_dir, started_at}` (instance_id is the installed release tag, or for an untagged dev instance the engine checkout's `git describe --tags --always --dirty`) -- for diagnostics and the "someone else holds it" error, but correctness comes from `flock`, not from reading those fields. In-process asyncio locks serialize tasks within the one daemon; the lockfile is the only cross-process lock.

### 6.5 Logging, spools, and redaction

**Operational logging (the journal is not a debug log).** The journal records intents, effects, signals, timers, caps, and state transitions -- never diagnostic chatter: it is versioned, corruption-strict, and never deleted. Diagnostic capture is two instance-local surfaces under the state dir, neither ever authoritative (no gate or dispatch decision reads them; harvest quotes them as informational material only), plus one shared filter:

- **Engine log.** Daemon diagnostic output -- unexpected exceptions, watcher/debounce noise, reconcile detail -- goes to one line-oriented engine log, size-rotated (shipped default 16 MiB x 4 files; an engine constant, not config). Load-bearing failures are ALSO journaled as events (a watcher parse failure, a harvest error); the engine log is the human-readable detail behind the event, never the record.
- **Attempt spool.** The driver tees each stage attempt's full output -- subprocess stdout/stderr, the agent adapter's JSONL event stream (section 9), check and verification command output -- to a per-attempt spool at `<state_dir>/spools/<stem>/<attempt>/` (`<attempt>` is the RUN SEQUENCE above -- one attempt per run entry, so a run's spool dir and its `attempts/<n>/` harvest dir share the number, section 11.2). Inside it each model call's capture (prompt, output, error) lives at `<surface>/call-<nn>/`, the stage's surface plus its call sequence, so the Implement, Review, and diagnose calls sharing an attempt never overwrite one another's files. The rendered prompt is written to the spool BEFORE the model call executes: a call that raises or hangs must leave on disk exactly what was sent. That spooled prompt file is ALSO the sole prompt-delivery channel: the agent-CLI adapter hands the prompt to the child by connecting THAT FILE as its standard input (section 15's `stdin_path`), and the rendered prompt is NEVER a command-line argument -- a prompt is unbounded while an argv element is capped by the OS argument limit, so a large ticket's prompt on argv aborts the call before the model is reached (the failure a file avoids by construction); argv carries only the fixed flags. The spool is what the section 11 harvest cuts its capped tails from and what spiral detector fixtures are cut from (section 9). Spools are deleted at the run's post-harvest cleanup; a spiral warning or poison quarantine PINS the run's spool (never auto-deleted) until an operator releases it, so fixture material survives the wipe.
- **Redaction seam.** Configured secret VALUES (the env vars named by the provider registry's `auth` fields) are redacted from every captured stream -- journal bodies, engine log, spools, harvested artifacts -- by one shared filter at the write seam that replaces each resolved secret value, matched as a literal substring, with the token `[REDACTED:<NAME>]`, so a subprocess that echoes its environment cannot persist a secret. The filter is wired at CONSTRUCTION time, before the first spool write, into EVERY production writer: the four streams above resolve to a maintained WRITER-SITE checklist (the journal writer, the engine-log writer, the attempt-spool writer, harvest serialization -- one stream may have several writers, and every writer of a listed stream appears here), and a deliverable adding a captured stream or a new writer of an existing stream extends this checklist in the same change; the regression test exercises the CONFIG-to-writer path end to end -- a test that passes the secret in manually proves nothing and is a banned test shape (it satisfies the letter of the Phase-0 prompt-9 secret test, section 0, while the wiring is absent). An effect RESULT is scrubbed exactly once, BEFORE it becomes the effect's return value and its completion record: the executing path and a later replay of the same key return the SAME post-scrub bytes by construction -- the recorded result is the only version that ever exists.

### 6.6 Block catalog and fake LLM

A 16-code block catalog names the orchestration building blocks. It is a NAMING SCHEME and coverage checklist, not a plugin system:

| Code   | Block                                                      | v1?      |
|--------|------------------------------------------------------------|----------|
| AUTH   | ticket authoring (schema + closed vocabularies)            | core     |
| HGATE  | human gate (draft->confirmed, reject verdicts, quarantine release) | core |
| PLAN   | scheduler (gutted to deps + priority dispatch, section 9)  | core     |
| WORK   | workspace-per-ticket + engine-agnostic agent adapter       | core     |
| GATE   | gate-check harness (hard/soft config, check-runner)        | core     |
| SHIP   | merge queue (rebase, re-gate, squash-merge, section 9)     | core     |
| EMIT   | dedup-then-emit shared ticket writer (the Suggestion Box)  | core     |
| THRESH | threshold-then-escalate (caps, budgets, circuit breaker)   | core     |
| WDOG   | watchdog (stuck/spiral detection, external heartbeat)      | core     |
| DIAG   | the single failure-diagnosis step (section 11)             | core     |
| HARV   | harvest-from-artifact on failure (section 11)              | core     |
| JUDGE  | standalone LLM judgment step (verdict + confidence)        | deferred |
| CLUS   | failure-cause clustering (signature normalize + group)     | deferred |
| HOOK   | lifecycle hook registry (isolated terminal side effects)   | deferred |
| STEW   | steward composition (idempotent maintenance chains)        | deferred |
| ARCH   | archive / reconcile GC (terminal-artifact relocation)      | deferred |

Deferred codes return only via D10. The table is a coverage checklist; module naming is the implementer's.

The fake-LLM adapter is a first-class kernel component: the `LLM` interface has a scripted-fake implementation from day one, and journaled effects returning recorded results IS the record/replay mechanism -- replay fixtures fall out of the kernel, keyed by the effect key itself, never a separate fixture id.

### 6.7 LLM interface and routing

**LLM interface (the one seam every model call crosses).** One async method behind the `@effect` wrapper, with a `cli` implementation plus the scripted fake; the `api` implementation is a D10 return built at the first configured `api` provider (section 18), and the interface's `kind` field reserves its place. This is a kernel contract the driver and cost capture both call, so its shape is fixed here, not implementer-owned:

```python
class LLM(Protocol):
    kind: Literal["api", "cli"]
    async def call(self, req: LLMRequest) -> LLMResult: ...
    # abort_current is the synchronous kill seam, deliberately NOT behind
    # @effect (the one-async-method-behind-@effect law above stays true): it
    # returns only after the external writer (the CLI subprocess and its
    # process group) can no longer mutate the worktree. The driver calls it
    # BEFORE harvest and BEFORE recording any timeout terminal -- proven by a
    # test with a cancellation-resistant fake.
    def abort_current(self) -> None: ...

@dataclass(frozen=True)
class LLMRequest:
    surface: LlmSurface      # closed vocab (section 5): selects spec + routing
    rendered: str            # rendered prompt (spec renderer); the agent-CLI
                             #   invocation input for kind: cli
    tier: AgentTier          # low|medium|high|max -> models_by_tier
    effort: AgentEffort      # low|medium|high|max, passed through to the model
    ticket: str | None       # owning ticket stem (keying + provenance)
    worktree: Path | None    # the writable tree; set for a cli Implement run
                             #   only, the one surface granted write (invariant 2)

@dataclass(frozen=True)
class LLMResult:
    text: str                # model / agent output
    input_tokens: int | None # None when a cli stream reports no usage
    output_tokens: int | None
    provider: str            # which provider served (journal + run-record stamp)
    model: str               # which model served
    usd: float               # metered cost, or the cli est_cost_per_call_usd
                             #   fallback (below); feeds effect_completion cost
```

The routing table (below) resolves `(tier, surface)` to the concrete `(provider, model)` BEFORE the call; a resolution landing on a row still carrying the section 0 placeholder value is refused pre-call as a config/setup refusal (the placeholder convention -- never a live call); a `kind: cli` provider fills the token fields from the adapter event stream when present and falls back to `limits.est_cost_per_call_usd` otherwise.

### 6.8 Provider layer

**Provider layer.** The `LLM` interface is multi-provider. Instance config declares a provider registry -- `{name, kind: api | cli, auth (an env-var NAME, never a literal secret), package (a `cli` provider's pnpm package), models-by-tier, limits}` -- plus a routing table mapping each (`agent_tier`, `llm_surface`) to an ORDERED candidate list of (provider, model) pairs. A candidate names a provider and MAY pin an explicit `model`; when it omits one, the provider's `models_by_tier[tier]` supplies it, so `models_by_tier` is the per-provider default and a candidate's `model` is an optional per-route override, never a second independent source (Phase 1's authored config pins a model only where the row demands it -- REVIEW at every tier -- while its implement/author candidates name only a provider and inherit `models_by_tier[tier]` from the start, per the section 0 prompt 1 authoring order). Tickets ask for semantic capacity only (section 13); the routing table is the single place semantics resolve to a concrete provider, so switching providers is a config edit, never a ticket edit. Tier resolution is uniform, and the PREDICATE decides -- the parentheticals are examples, never enumerations: every surface invoked FOR a ticket (implement, review, rework, its diagnose, `requisition_review` of that authored ticket) resolves at that ticket's `agent_tier`; calls no ticket owns (triage, retro, Author) resolve at the config's `routing_default_tier` (section 15; shipped default medium). The journal and run record stamp which provider and model served each attempt. A provider key is injected ONLY into the agent-CLI or API call that needs that specific key; every other child process -- verification commands, checks, evidence replay -- is spawned without that key in its environment and never inherits it. The child base environment is INHERIT-MINUS-SECRETS: every child gets the parent's full environment (an ambient-login CLI needs HOME and PATH) minus every env var any provider's `auth` names, with exactly the serving call's key restored for that one call -- never an allowlist rebuild. **The provider set is a bootstrap INPUT, collected up front and carried through unchanged.** The operator's setup (the Phase 1 prerequisite, section 0), BEFORE the conductor and seeds run, collects EVERY input the build needs -- which providers, each provider's STYLE (`kind: cli` or `kind: api`), its models by tier, and its key. The CONTRACT covers both styles and any provider count the config declares, but v1 SHIPS only the `cli` style: a `cli` provider is a subprocess behind its argv wrapper (D1); the `api` client (an operator-installed venv SDK import, fail-closed if absent -- the api analog of the section 15 seam's unresolvable-`argv[0]`) is a D10 return built, together with its spend ceiling and token buckets (below), at the first configured `api` provider -- until it ships, a config declaring `kind: api` is REFUSED at load with an error naming the unshipped client (fail-closed, never a silent fallback). Neither a CLI binary nor an SDK is ever a chupa runtime dependency in `pyproject.toml`. The specific set is the operator's CHOICE, never hardcoded in a seed -- this repo happens to run two `cli` providers (codex, claude), but a seed builds GENERICALLY over whatever the config declares. Once the conductor and seeds start there are NO human gates of any kind: everything the build needs was gathered at setup, so no seed stops to ask for input, and none adds, removes, re-declares, or switches away from a configured provider. A provider or model change is a `config.yaml` edit BETWEEN runs, never a ticket edit and never mid-run. Phase 4's provider work (routing, failure classification, cooldowns, failover) builds the engine handling over the configured set -- `cli` classified from exit code + stderr, `api` from HTTP status (below) -- adding no provider and no dependency.

### 6.9 Rate limits and spend

- **Rate limiting is deterministic and pre-call.** Per-provider CONCURRENCY caps are enforced by the dispatcher BEFORE the effect executes; a call that would exceed the cap waits or spills to the next candidate instead of burning a provider-side rejection. The wait-vs-spill rule is deterministic: spill when the next candidate can serve the call NOW and the primary's projected wait exceeds 60 seconds (an engine constant, not config); otherwise wait, FIFO. Token buckets (requests/min, tokens/min) are `api`-metering machinery, deferred with the `api` client -- a `cli` provider exposes no enforceable TPM/RPM surface (below). Time spent waiting at a cap is journaled and EXCLUDED from the ticket's time budget and the watchdog's wall-clock regions, so a starved run never reads as stuck.
- **Spend is stamped in v1; spend ENFORCEMENT ships with the `api` client.** Every completion event carries its cost (metered usage when the stream reports it, else the declared `est_cost_per_call_usd` flat estimate) -- the LEDGER is the read-time fold over `effect_completion` cost fields (D3), and reconcile reports it. On a FLAT-SUBSCRIPTION `cli` provider a USD ceiling is meaningless backstop -- marginal per-call cost is ~0 (the CLI reports a NOTIONAL equivalent-API cost, as Claude Code's `total_cost_usd` does, or none, as Codex does) -- so the operative backstops are the provider's own rate/quota limits (`rate_limited` | `quota_exhausted`, below), the concurrency caps, and the circuit breaker, and a flat-subscription instance carries NO USD spend cap by design. The cumulative spend ceiling -- global and per-provider over a rolling window, the pre-call check whose crossing returns `budget_exceeded` (section 5), pauses dispatch, and fires the budget-exceeded escalation (section 13) -- protects real per-token dollars and is deferred WITH the `api` client to the first configured `api` provider; the config-load refusal above keeps that fail-closed (no `api` provider can run unmetered before the ceiling exists). The `budget_exceeded` outcome and escalation stay defined in their vocabularies; their producer ships with the ceiling.

### 6.10 Provider failures, failover, and droughts

- **Provider failures classify into a closed vocabulary:** `rate_limited | quota_exhausted | outage | auth_error | model_error | unclassified`. `rate_limited`: honor retry-after, retry same provider, spill under queue pressure. `quota_exhausted`: mark the provider cooling-down until its window resets (a journaled Timer whose duration is `limits.quota_window_minutes`, section 15 -- a `cli` provider exposes no retry-after, so the window length needs this declared source), fail over for subsequent calls, emit a soft Suggestion Box report. `outage`: per-provider circuit breaker -- K consecutive failures opens the circuit for T minutes (shipped defaults K=3, T=10) -- with failover. `auth_error`: fail over AND alert (a section 13 escalation) -- a dead credential never self-heals, so failover must not silently mask it. `unclassified` -- a `cli` exit matching no known class -- is a first-class member, never a raw `infra_error` loop: it draws from the stem's `infra` budget (section 11.1), counts toward the same circuit breaker, and at budget spent the stem PARKS with a paved road naming the provider and the captured exit/stderr tail, so an unrecognized CLI failure mode is bounded and visible instead of retried blind. Classification is the provider's; the driver owns ONE mapping from a classified exception to a `Finding` (`code` = the failure class, message = the provider error, paved road = the provider's declared login road for `auth_error`) carried in the attempt harvest -- never copied into the terminal reason, which stays code-only -- and an unclassified exception carries no finding.
- **One provider payload per session.** Each lock-held engine session (`drain` or `serve`) composes ONE provider registry/cooldown payload and ONE journal-backed `Timers` lifetime and threads it to every provider-client construction site (implement, review, rework, triage, Author, retro); nothing constructs a second registry. The watchdog and its inner client resolve each call's served identity once from that payload. A classified quota hit arms cooldown and ends that attempt WITHOUT drawing the stem's `infra` cap; later calls skip the cooling candidate in configured order; an all-candidates-cooling route holds until its journaled Timer fires.
- **Failover granularity is the attempt, never mid-run.** An in-flight run is not migrated; if it dies, the normal fresh-workspace retry re-resolves routing and lands on the next healthy candidate.
- **All candidates exhausted for a tier:** a DROUGHT is a ROUTING outcome, never a spine failure -- no call was possible, so nothing is metered. The dispatcher consults breaker/cooldown/quota state BEFORE dispatch; a stem whose resolved route has no available candidate parks COST-FREE, the dispatcher journaling the drought-park event (the journal-derived source of section 9's `not parked (provider drought)` eligibility term): no model call, no cap draw, no diagnosis, no Reject-queue arrival -- the `budget_exceeded` park's exact shape (section 11.3) -- and the stem re-enters eligibility automatically once routing resolves, an open circuit's cooldown expiry included (section 9). A drought DISCOVERED MID-RUN (a stage call refused pre-call because the resolved tier's candidates are all unavailable -- open breaker, cooling quota, exhausted tier) terminals the attempt `infra_error` with the drought reason so the section 11.2 handler still runs (harvest -> journal -> wipe), but that reason draws NO cap, gets NO diagnosis, and is EXEMPT from section 11.4's identical-terminal ladder and Reject routing -- it drought-parks exactly like the pre-dispatch case (capability cannot fix weather; the headless auto-keep must never convert a drought into a spend loop or a terminal rejection of healthy work). What survives for the resumed attempt is section 11.2's harvest -- run record, findings, committed-candidate sha in the prior-attempts render; the unreviewed diff never enters the ticket spec, and failover granularity stays the attempt (this section). Every provider failure from a call that actually RAN (outage, model_error, unclassified, auth_error) still terminals `infra_error` and draws the infra cap per section 11.1 -- a failed call is always metered; only the absence of a callable provider is free, its bound the routing-resolves re-entry gate rather than a cap. A fleet-wide provider drought raises the escalation alert (section 13).

### 6.11 CLI provider contract

- Implementer and reviewer always run in SEPARATE SESSIONS -- distinct stage calls each with their own context, never one session grading its own output. That separation is the HARD requirement, enforced structurally by the one-call-per-stage driver (section 5). Routing the review surface to a DIFFERENT provider or model than implement is a PREFERENCE layered on top -- it reduces shared model-family blind spots -- never a hard gate: the same model in two separate sessions is allowed, and which model serves each surface is the operator's config choice (a config edit, section 15).
- **`kind: api` and `kind: cli` degrade differently.** An `api` provider (once its client ships) exposes per-call token usage and HTTP status: full contract above. A `cli` provider is a subprocess black box: per-provider CONCURRENCY caps and classification from exit code + stderr only, no enforceable TPM/RPM buckets, no retry-after (spill-on-pressure and the circuit breaker still apply). Cost is never unmetered -- Implement typically runs as a `cli` subprocess and is the largest spender: a `cli` provider's completion events carry usage parsed from the adapter event stream when the CLI reports it, and a provider whose stream carries no usage MUST declare `limits.est_cost_per_call_usd`, a conservative flat estimate charged to the ledger per call; declaring neither is a config error (fail-closed). Phase 4's quota-exhaustion exit is exercised over whatever providers the config declares -- a `cli` provider classifies rate-limit/quota from exit code + stderr, an `api` provider from HTTP status. Failover PROOF is fixture-scoped: the failover deliverable's verified runs exercise a multi-candidate FIXTURE registry in which the failing candidate fails over to the next, and the `19.P4` exit read -- "lands the next attempt on the failover candidate" -- is read from THAT verified run's served-identity stamps, never from a provider added to the live config for the occasion. The live config is never the fixture: a SINGLE-candidate live route (a legal operator choice -- the set is the operator's CHOICE, above) never invents, adds, or switches to a provider to satisfy an exit read; its live quota evidence is instead the `quota_exhausted` classification, the armed journaled cooldown Timer (above), and that Timer's journaled `timer_fired` event after the window resets, the served identity remaining the sole configured candidate throughout -- a quota with no remaining candidate parks per the candidates-exhausted rule (above); either style's access (a `cli` binary, an `api` SDK) is operator-installed at setup, never a chupa runtime dependency (section 0).
- **A `kind: cli` call's write grant is per-SURFACE, never per-directory, and fail-closed.** Implement is the one surface that mutates the tree, so its `worktree` is set (above) and the agent-CLI subprocess is invoked as a WRITING surface -- the adapter's write jail OFF, running with the operator's own privileges per section 16. A directory-scoped grant ("write access to exactly the worktree") cannot serve Implement: a worktree's git metadata lives in the parent checkout's `.git`, and a `## Verification` toolchain writes caches outside the workspace root, so a jailed subprocess can neither commit nor verify and terminates `ok` on an EMPTY diff. Every other surface -- Author, Review, each host review surface, and the ticket-less triage/retro calls -- runs the agent CLI READ-ONLY and writes no file (they emit an artifact the driver writes, invariant 1). The grant is a closed allowlist of the tree-writing surfaces, derived by the client build from the request's `surface`, never a global default a subprocess carries: a surface off the allowlist gets read-only, so a new writing surface adds itself deliberately. This is a kernel contract, not an adapter default. Routing validation enforces the same rule fail-closed at config load: a candidate serving the `implement` surface must be `kind: cli` -- an `api` provider returns text, and no apply-patch machinery exists to turn text into worktree edits (a D10 addition if ever earned) -- so a config that routes Implement to `api` is a config error.
- **The reliability knobs are a D10 seam.** Circuit breaker, cooldown Timers, and diversity routing ship in their simplest working form; each tightening waits on a cited incident.
- **Provider preflight.** Before the conductor's first deliverable and before every `chupa drain` dispatches, each configured `cli` provider's installed version (`<binary> --version`) equals its package's latest release (`pnpm view <package> version`), and each routed (provider, model) pair answers one minimal probe call. A stale CLI or a failing probe refuses the run -- exit 2, nothing dispatched, no cap drawn -- naming the provider, the model, and the provider's own message; the paved road is `pnpm add -g <package>@latest`, or a routing fix in `config.yaml`.

Event vocabulary note (deferred, not v1): if external anchoring ever matters, align journal event fields with OpenTelemetry GenAI attributes and the EU AI Act Article 12 logging bar. The AI audit trail (a v1 refusal, section 18) returns as projections over the journal -- trajectory/reward/preference exports, per-merge attestations -- never as ticket frontmatter.

## 7. Gates: fail closed, one valve, earn your way in

### 7.1 Gate shape

Every gate is built to the five-rung shape:

1. Prose explains WHY (the only rung that teaches intent).
2. Never a denylist. Allowlist semantics and closed vocabularies only; unlisted means stop. The Gate base class offers `allowed:`-style helpers, not pattern-ban helpers.
3. Every finding carries its paved road (required field).
4. Mechanical enforcement is the only road to merge: the merge stage is the single writer to main and re-runs the hard gate set itself (mechanical codes; the review surface participates as the pinned approval, section 9). Prose compliance is never load-bearing.
5. Exactly one valve, uniform everywhere: `gate_bypass: [{code, reason}]` in ticket frontmatter, surfaced at the draft->confirmed human gate, visible forever, auto-reported to the Suggestion Box. K bypasses of the same gate code (shipped default K=3 within one retro window) auto-files a rule-defect report (an `override_report` box message, section 12). There are NO env-var bypasses; the config namespace does not contain them.

### 7.2 Hard gate set

v1 hard gate set (each cites its motivating incident; parenthesized stage = whose emitted artifact the code validates): ticket schema + closed vocab (Requisition); ticket feasibility (`requisition_review`; Author and seed authoring, section 13); scope fence (section 9; Check); the ticket's own `## Verification` commands pass (Check; executed like every ticket-authored command, section 16), attributed by BASE DIFF (the attribution machinery ships with the Phase 2 spine beside its filing consumer, the Suggestion Box -- the Phase 1 gate fails on any red, section 19) -- a `## Verification` command that fails on the branch is re-run at the branch's MERGE BASE, and one that ALSO fails there is a PRE-EXISTING base failure: filed as a second problem (section 11.7) and charged to neither the Check nor the retry budget, so a full-suite command never fails a stem for a red it did not introduce. A command green at the base and red on the branch is the branch's own regression and fails the Check; the merge-time INTEGRATION CHECK on a green main (section 9) is the backstop for any command the base excused. Attribution is per COMMAND, never per test -- the engine ships no per-runner output parsing (section 18); run record present + schema-valid (Check); diff budget (Check) -- a mechanical cap on the reviewable diff: changed-file count and inserted-line count against engine constants (shipped: 30 files / 1,500 inserted lines), sized so every rendered review prompt fits the serving provider's context bound (the section 8 render contract is the same law at the prompt seam) -- an over-budget diff terminals `gate_failed` with the paved road "split the ticket (diagnosis verdict `split`, section 11)", so an unreviewably large diff is split at the gate, never dispatched to a review call that cannot hold it (a fixture corpus counts per file, so an eval case is ONE closed envelope file, never a directory of per-field files); post-rebase gate re-run (merge); bug gate (Check) -- a `kind: bug` ticket must carry evidence in its ticket dir and a regression check that failed pre-fix, verified mechanically: the gate runs the ticket's `## Regression` command (section 13) at the branch head, which must PASS, and at the merge base WITH the branch's `carries:` paths overlaid (section 13), which must FAIL -- the overlay exists because the regression test usually arrives WITH the fix, and a bare base run would fail for the vacuous reason that the test file does not exist yet, satisfiable by any new test regardless of the defect (heavier bug machinery -- commit-order enforcement, spec-first ordering, device matrices -- is excluded until earned per D10). The bug gate ships with its first bug-intake consumer, the Phase 6 report inbox (section 19); bootstrap-era merges run the hard set without it. Two engine LLM review surfaces in v1: `correctness_review` (correctness / acceptance-criteria review of an implemented diff, participating at merge as the pinned approval, section 9) and `requisition_review` (the feasibility review of an AUTHORED TICKET before it commits confirmed -- run at AUTHORING for every machine-authored ticket whatever its starting state: a draft-starting box ticket carries the verdict on its draft, and the later human `confirm` flip re-runs nothing -- the semantic complement to the grammar-only `ticket_schema` gate: it judges the ticket BUILDABLE against the shipped engine and the plan it renders, catching a criterion that contradicts merged behavior, a `## Scope fence` missing a file the acceptance criteria force, mutually unsatisfiable criteria, an authored base Implement render over the section 8 bound (RENDER FEASIBILITY, measured mechanically at authoring -- section 19), or -- for a phase-exit/seeding ticket, which is IN SCOPE like any machine-authored ticket -- an exit criterion reading a signal or artifact that no deliverable of its phase emits (the exit-read closure, section 19), verdicts approve | snag | rma mirroring code review -- a snag re-authors within caps, an rma parks for a human, section 13). Always-run vs diff-triggered is a config map from path prefixes to gate codes (`review.trigger_map`, section 15 -- it governs ENGINE-shipped gate codes; host-declared checks and surfaces carry their own per-entry `trigger`). Everything else starts soft and must earn hard status (D10).

### 7.3 Review surfaces

**Host-declared review surfaces.** The engine ships the generic gates above; everything project-specific comes from the HOST's config (data plane), in a `review` section validated fail-closed (unknown codes, shapes, or vocab are config errors, not skips):

- **Mechanical checks:** each entry is `{code, argv command, trigger: always | path-prefixes, severity: hard | soft}`. The engine runs the argv through the check-runner contract (any stack): exit status plus OPTIONAL structured findings JSON on stdout -- a JSON array of section 5 `Finding` objects (`{code, path, line, message, paved_road}`; `paved_road` optional in this one producer, defaulted to the generic road) -- wrapped into the uniform GateReport. A bare nonzero exit with no JSON becomes a single finding whose message is the captured stderr/stdout tail and whose paved_road is generic, so an off-the-shelf linter (ruff, eslint, clippy) drops in without a per-tool adapter. A check that CRASHES fails closed -- routed like a hard failure, never a silent skip.
- **LLM review surfaces:** for CODE the engine ships exactly one (`correctness`; the authored-ticket feasibility surface `requisition_review` of section 7 is the separate authoring-time review, not a diff surface); the host declares additional surfaces as `{name, trigger, rules_doc, severity: hard | soft}`, where `rules_doc` is a host-owned review-rules file the engine's generic review spec renders in as content. Composition is conjunction: each triggered surface runs as its own review call under the one driver (routed by its `llm_surface` name, section 5); a hard surface's snag-list routes to Rework exactly like `correctness`'s; a soft surface's findings go to the Suggestion Box without blocking; and the merge-admissible approval (section 9) exists only when EVERY triggered hard surface has approved the same SHA -- the approval record's resolved surface list (section 4) pins "which surfaces approved", never implicit. New surfaces earn their way in per D10 within the host's own gate budget, and every surface is measured by the section 14 catch/escape scorecard. Every `requisition_review` finding carries a closed `kind`: `spec_gap` (the governing spec omits a fact the work needs) or `authoring_error` (the work contradicts stated spec or merged code, or is malformed); section 11.4 routes by kind.

## 8. Prompt specs

### 8.1 Prompt specs and the render contract

Every LLM stage is defined by a prompt spec file -- one engine-plane file per `llm_surface` at `specs/<surface>.md`: YAML frontmatter (closed vocab: `llm_surface` (section 5), consumes/emits artifact types, model tier, effort, gate list, version) plus fixed prose sections (Role, Task, Inputs, Output format, On-failure -- every spec tells the model what to do when it cannot comply).

- Spec lint validates frontmatter schema, vocab, section presence, size budget (shipped default: 200 lines). Structured feedback with paved roads, bounded AI re-run.
- Rendered-prompt size is a render CONTRACT: the renderer measures every rendered prompt against the serving provider's context bound -- for CLI providers exposing no tokenizer, ONE engine-owned conservative character-count bound, the same at every tier and effort so climbing the ladder never shrinks it -- engine constant `RENDER_BOUND_CHARS` = 400,000, about half the smallest configured model's context window at three characters per token, leaving the other half for the agent's own reads and work; a provider with a smaller window lowers it (stage-local bounds are forbidden) -- and REFUSES an over-bound render as a named stage terminal -- a MECHANICAL PRE-CALL SHORT-CIRCUIT like `budget_exceeded` (section 11.3): ticket-text arithmetic, never implementer failure, so no diagnosis call and no cap draw; the stem parks like `premise_failed` (paved road: shrink the inputs or split the ticket), released only by a ticket-plane content change, and dispatches mechanically to Rework `split` once Rework is live -- never dispatching a prompt for the provider to crash on. The diff budget gate (section 7) keeps review prompts inside this bound by construction; prompt delivery is always the spooled stdin file (section 6), never argv. AUTHORING HEADROOM: an authored ticket's base Implement render must fit `REQ_RENDER_HEADROOM` = 0.75 of that bound (300,000 characters), leaving room for attempt history (`19.L`).
- PLAN LINT keeps this plan renderable as per-ticket seed contracts (Phase 0, `chupa/specs.py`, `tests/test_plan_lint.py`): every `###` heading is a subsection `N.k` inside its own `## N.` section, `19.L`, `19.I`, a phase unit `19.P<n>`, or an entry unit `19.P<n>.<stem>` naming a row of that phase's registry, and each id has exactly one heading; every `BEGIN_REGISTRY_P<n>` block parses as YAML, its `admissions` cover its `seeds` exactly with at most two payloads each, and every seed `cite` resolves (an integer section, a quoted `"N.k"` subsection, or `"19.L"` for a row implementing a `19.L` law); every entry unit carries each SPEC DEPTH part (section 19) as a non-empty labeled bullet. Plan lint sets no size budget: a seed's whole rendered prompt is bounded once, by the authoring render-feasibility check (AUTHORING HEADROOM above, `19.L`). A plan edit failing lint is reworked before it commits.
- Untrusted-origin content never enters a prompt as instructions. Host docs render inside delimited data blocks; player-report text and evidence files render only as quoted data marked untrusted (and only summarized-by-triage text reaches ticket prose, section 12). Spec lint checks that templates wrap injected content in the data-block form -- the data/instruction boundary is a rendering contract, not stage-local vigilance. A data payload that legitimately contains the engine's data-block delimiter -- a Review diff of renderer code, retry findings or a harvested tail quoting it, a test asserting it -- is QUOTED at the ONE rendering boundary before data-block validation: every occurrence becomes the deterministic visible text `[chupa-data:` in the model-visible payload, the durable source staying byte-exact; this is engine-owned rendering, never a stage refusal or a reason to omit the material. A rendered prompt or prompt spec is never injected as a later prompt's input, quoted or otherwise. The change that first lands quoting is bootstrap-safe under the OLD renderer: its diff never spells the raw delimiter (it uses the engine constant and dynamically built fixture values) and leaves existing delimiter-bearing lines byte-identical. Golden tests prove a payload whose runtime value contains the delimiter reaches the model visibly quoted.
- Specs are code: versioned as MAJOR.MINOR (a MAJOR bump is the "spec-major change" that fires the section 13 touchpoint 7 re-baseline trigger), golden-tested (render from fixture inputs, snapshot), and every artifact records the producing spec version.
- Spec changes ship as ordinary tickets through the pipeline (self-hosting). Formal canary/shadow rollout is deferred until a spec change causes harm.

### 8.2 Rule planes

**The two rule planes.** chupa defines ticket structure and control; the target repo defines the what/content of implementation:

- **Engine plane (chupa-owned): HOW work runs.** Ticket schema and closed vocabularies, stage prompt specs, gate discipline, workspace/git rules, the run-record contract. Versioned with the engine, propagated to hosts by bootstrap refresh, never host-edited.
- **Host plane (target-repo-owned): WHAT to build.** Architecture and domain rules, tech stack, design docs, review-rules docs, verification conventions. Never engine-edited. It enters the pipeline AS DATA: rendered into Implement/Review prompts via host-declared context files and review surfaces (section 7), with provenance stamping the engine spec version and the host-doc SHAs in each prompt.

The planes meet in exactly two places: the rendered root AI files (managed `chupa:core` block + project-owned remainder, section 15) and prompt rendering. Conflict rule: the engine plane wins on process, the host plane wins on content -- and "redefines process" is a CLOSED MECHANICAL predicate, never a semantic judgment: the drift lint normalizes the project-owned remainder into paragraphs (Markdown list prefixes stripped, nonblank continuation lines joined -- a rule split across physical lines is ONE paragraph), and a normalized paragraph FAILS the lint exactly when it opens with the subject `chupa` followed by a directive from the closed modal list (must, must not, should, should not, shall, shall not, will, will not, may, may not) or by an imperative from the closed engine-process predicate vocabulary the drift-lint deliverable declares; every other subject and ordinary project rule passes, proven by refusal AND acceptance fixtures (a lint that reddens `The chupa dashboard must use dark mode.` is as broken as one that greens an override). The managed block is fail-closed on its own markers: a duplicated, reordered, or UNTERMINATED `chupa:core` marker -- or stray marker-like text anywhere in the file -- refuses both render and lint (corruption is never green); a routed CLI's file with NO marker and NO marker-like text is FIRST ADOPTION (`19.P6`): the managed block is inserted with every existing byte preserved as project-owned remainder; a missing marker WITH marker-like text present still refuses; repair never erases a project-owned byte, and a second render over a clean file is byte-identical (idempotence, a named test). The renderer manages the conduct file of every CLI the RESOLVED ROUTING names, via section 17's mapping (the `claude` CLI loads CLAUDE.md; any other agent CLI loads AGENTS.md): a routed CLI's file is always rendered, an unrouted CLI's file is never created (an unread copy to drift, section 17) -- never an assumed provider's file. This machinery lands as chained deliverables -- the renderer (carrying the marker and idempotence contract), drift DETECTION (the pure classifier), then gate ACTIVATION -- never one ticket (`19.P6`; it proved unbuildable bundled). Reflexive case (chupa developing chupa): the `chupa:core` render and drift lint run against the TICKET BRANCH's engine version, and the branch's golden snapshot is the authority, so an engine-plane template change ships with its own updated block instead of drift-failing against the running instance's older version. The golden snapshot is REGENERATED by a mechanical render target, never hand-edited: the drift lint compares the committed block against a fresh render of the branch's template, so a snapshot a fresh render does not reproduce fails.

Rule ROUTING is three-way: orchestration-generic -> the engine's core template (propagated by bootstrap refresh); project-specific -> that host's project section; personal machine-wide preference -> the operator's global agent config. Engine rules NEVER go in the personal global config. Why: concurrent instances may run different engine versions, and a global copy of one version's rules would leak into the other's sessions.

## 9. Scheduler, scope fence, merge queue

### 9.1 Continuous dispatch

**Continuous dispatch.** Eligible = `state: confirmed` + all `depends` merged + not quarantined + not parked (provider drought) + not awaiting a Reject-queue verdict -- the last two journal-derived, like quarantine (the Reject fold: a stem awaits a verdict when its latest terminal `state_transition` body carries the Reject-routing marker `routed: reject_queue` -- stamped by the spine when it terminates a stem to the queue, section 11 -- with no later `confirm`/`reject` `signal`; the bootstrap drain's auto-keep journals the same signal with a MACHINE actor stamped on its body, section 11.4 -- either actor's signal resolves the awaiting-verdict hold; only the operator's bounds the cap fold (section 11.2); no new run state exists for this). Drought-parked tickets re-enter eligibility automatically at the next dispatch cycle once routing resolves; the OPERATOR'S Reject-queue `keep` re-enqueues the ticket and re-arms its spent failure-spine caps; the bootstrap drain's auto-keep (section 11.4) re-enqueues only -- it DRAWS DOWN remaining budget and NEVER re-arms a spent cap. Sort by (priority, age) -- the age term is the starvation guard; age = time since the journal event of the stem's first ticket-plane `ticket.md` commit -- and EVERY authoring path emits it: human intake (section 13 touchpoint 1), the Author stage, box triage, and phase seeding all journal the same per-stem authoring-commit event, else the starvation guard is silently dead for machine-authored stems -- journal-derived, D3, never a file mtime, with lexicographic stem order as the final deterministic tiebreak, a stem with no event sorting as `None` (never a synthetic now: no event means no seniority); the deliverable that lands the age term also lands its consumer, demoting the stem-name comparison to the final tiebreak in the eligibility sort, proven by a test with DISTINCT per-stem clocks (an equal-clock test cannot discriminate a working sort from a broken one). A file watcher on the tickets dir re-sorts the pending queue on any edit (live re-prioritization). It DEBOUNCES so a half-written ticket is never scheduled, and parses FAIL-CLOSED: a ticket that does not parse holds its last-known-good sort position (a NEW ticket with no parsed state stays out of the queue), and the parse failure is journaled. No preemption of running work (a P0 takes the next free slot).

### 9.2 Dependency liveness

**Dependency liveness.** A dependency edge can die: its predecessor is killed at the Reject queue or abandoned. Terminal-without-merge is an event the scheduler consumes: the daemon journals a dead-dependency event for every confirmed ticket whose `depends` names the dead stem and emits one `failure_report` per dependent into the Suggestion Box (pre-daemon, the Phase 2 `reject` verb emits exactly these -- the dead-dependency events and per-dependent reports -- INLINE at the kill, the handling shipping with its trigger, section 19; the daemon's continuous scan takes over in Phase 3), so stranded work resurfaces as schedulable revision (re-wire, re-scope, or kill) instead of silting. When Rework splits a ticket, it journals a supersedes map (old stem -> successor stems); the scheduler satisfies a dependency on a superseded stem once ALL successors merge, and the terminal-without-merge scan resolves stems THROUGH that map in both directions -- a dead successor also marks the superseded stem dead, so dependents of the ORIGINAL stem get their dead-dependency events too.

### 9.3 Ordering and scope fence

**Ordering and scope metadata.** One author-declared path list must never do two jobs (conflict prediction and scope bounding). Why: path predictions are guesses that over-serialize the queue and miss real collisions. Two separate mechanisms:

- `depends`: explicit predecessor stems, minimal, the only ordering mechanism.
- `## Scope fence`: the implement stage's WRITE ALLOWLIST. After implement, a mechanical gate checks `git diff --name-only` is a subset of the declared prefixes, and a `CHUPA_PLAN.md#<unit id>` entry admits a plan diff only when every changed line lies inside that unit's heading range; outside edits fail closed, with the `gate_bypass` valve for genuine surprises. AUTHORING law: the fence includes every file the acceptance criteria force -- criteria that compel an out-of-fence edit are an authoring defect, and the correct implement outcome is premise_failed, never a compat shim. The forced set is JUDGED at authoring, never left to run-time discovery: `requisition_review` checks the fence CLOSURE before a ticket commits confirmed -- its prompt directs the reviewer to trace the reference closure of every symbol the scope-in changes (callers and importers, aliases included) and the recorded-value closure of every constant or version it bumps (the artifacts and assertions carrying the old value) -- and rejects a fence omitting any, naming them, so a forced-file gap is caught at authoring time rather than as a runtime premise_failed. The closure is LLM judgment under that review's prompt, never a shipped static analyzer (the engine carries no per-stack reference tooling, section 18); a mechanical closure check is a D10 return at the first fence-gap escape this review misses. Behavioral fan-out that only a run reveals is absorbed at the gate, not by pre-widening: the scope-fence gate auto-admits an out-of-fence edit ONLY when it is confined to a TEST file and a mechanical anti-weakening check passes (no test deleted, skipped, or xfailed; assertion count non-decreasing) with the full suite green -- a TEST file matches the engine-constant patterns (a `tests/` path component, or basename `test_*` / `*_test.*`), and the anti-weakening check is language-aware for PYTHON only, stdlib `ast` over both sides of the diff (the self-host's language; no per-stack tooling accretes, section 18): a file those patterns claim but the parser cannot own FORFEITS auto-admission, fail-closed to the `gate_bypass` valve, never a heuristic pass -- a test edit cannot balloon the shipped surface, and loosening one is separately detectable. Every other out-of-fence edit -- any production file outside the derived closure -- stays fail-closed: a genuine surprise takes the `gate_bypass` valve, and reach with no reference, value, or dependency link to the scope-in is the authoring defect the fence exists to stop. One authored exception is structural, not a defect: a phase-SEEDING ticket (section 19) writes not-yet-authored `ticket.md` files -- the next phase's core batch, or its own phase's `-continue` feature batches -- whose stems are unknowable when its own fence is authored, so its fence is necessarily the whole `tickets` plane -- pre-naming the stems would be speculative seeding (D10). The broad prefix bounds writes to the ticket plane; that a seeding run only CREATES new stems and never rewrites an existing ticket is Review's to confirm, not the fence's. And the whole-plane fence is a WRITE bound ONLY, never review material: `requisition_review`'s material for a seeding ticket is PER AUTHORED SEED -- that seed's own text and Context closure, one render per seed, each under the section 8 bound -- never one union blob over the whole authored set or the plane's history (sections 7, 19).
- Conflicts are RESOLVED at the merge queue, the one place they are real; single-flight dispatch (D2) makes them rare by construction, and the deferred overlap checkpoints (section 18) are the D10 return if a future worker pool starts manufacturing them.

### 9.4 Merge queue

**Merge queue (one serial async task).** The queue admits ready branches in (priority, age) order -- the same sort as dispatch -- and an in-flight admission is never interrupted (a P0 takes the next free slot). Per branch, in order, all BEFORE main moves: RESTORE the branch worktree's ticket plane to main's content (`git restore` of `tickets/**` through git.py -- stage terminals lift-and-unlink ticket-plane artifacts, section 10, so a worktree born from an earlier main carries tracked deletions of the already-lifted copies, and an un-restored tree refuses the rebase) -> rebase onto main -> fast MERGE-SAFETY tier -> full INTEGRATION CHECK -> squash-merge -> delete branch. The MERGE-SAFETY tier is the cheap subset a rebase can invalidate -- rebase-clean, scope fence, run-record present, plus host-designated fast checks (`merge.safety_checks`, section 15) -- run first so an inadmissible candidate is rejected before paying the full run. The INTEGRATION CHECK is the FULL always-run hard set -- every engine-shipped hard gate plus every host mechanical entry with `trigger: always` and `severity: hard` (the host's own test suite belongs in that class; the green-main guarantee is exactly as strong as this set) -- AND the ticket's own `## Verification`, executed against the rebased candidate tree. That tree is content-identical to what the squash-merge will put on main, so checking it pre-admission catches semantic conflicts (green alone, red together) while main stays green by construction: a red candidate is not admitted -- main is untouched, the branch routes back through the failure spine with the integration findings as context (rework with conflict/semantic context, re-review per the risk routing below), and the next branch is admitted immediately. No freeze machinery exists because the failure mode it would manage cannot occur on this path.

### 9.5 Merge-time gate scoping and conflict resolution

Merge-time gate scoping: the re-run set is the MECHANICAL codes only, validating the admission's code diff, not every declared-binary evidence file already on main; integration-shaped checks (the ticket's verification) run against the tree; `correctness_review` participates as the pinned-approval requirement for the admitted SHA, never as a re-executed model call. Auto-admission is additionally GO-COVERED: the review effect's completion stamps the (provider, model) that actually SERVED (section 6), and the queue compares that served identity -- never just the routing config -- to the currently binding GO identity; an approval served off-baseline (a spill or failover landed the review call on an unbaselined candidate, section 6) queues for the operator's `confirm` exactly like supervised merge (section 12), dispatch and other candidates' checks continuing. A green candidate is squash-merged; the pinned review approval carries across a clean rebase (the deliberate, stated exception to approval-SHA strictness -- MERGE-SAFETY plus the INTEGRATION CHECK bound the carry's risk to what mechanical checks can see; the residual, a byte-identical diff whose meaning changed under a moved main, is an accepted risk the section 14 escape attribution measures, and an escape of that shape is the cited incident that would earn re-review-after-rebase per D10). Daemon era only: when no GO baseline currently binds, a green candidate queues for the operator's `confirm` before admission (supervised merge, section 12) while dispatch and review continue -- the bootstrap drain never holds (section 19). The hold itself is a Phase 6 deliverable, built at the first daemon-on-host-work cutover (section 19); through the entire self-build no admission holds, so the Phase 3 soak and every phase-exit seed exercise the merge queue without it, and no self-build seed (Phase 4 provider failover included) may require it. After the merge the queue asserts main's tree hash equals the checked candidate's tree hash; a mismatch is an engine defect and escalates immediately (section 13). One full verification run per admitted ticket is the deliberate serialization cost of a permanently green main. That cost has a stated capacity: admissions per day are bounded by rebase + MERGE-SAFETY + INTEGRATION CHECK wall-clock (a 30-minute suite caps at ~48/day), and the host's always-run hard set must be sized so capacity comfortably exceeds worker throughput. Backpressure is explicit, not emergent: at `scheduler.max_unmerged` completed-but-unmerged branches (section 15; shipped literal default `2` -- v1 has no `workers` key, and the `2 x workers` formula returns WITH the worker pool, section 18) dispatch stops admitting NEW tickets until the merge queue drains. If K consecutive DISTINCT tickets go integration-red (shipped default K=3), that is a systemic signal: merge admissions pause and the red-streak escalation fires (section 13); `resume` re-opens admissions. A conflicted rebase walks a cheapest-first resolution ladder; whatever rung resolves it -- and whenever every rung refuses -- the worktree is NEVER left mid-rebase: a refusal runs `rebase --abort` before it returns (section 10), so the branch the refusal names stays re-runnable:

1. **Mechanical resolution.** git's own merge machinery absorbs non-overlapping edits; on top of it, host-declared per-path strategies (closed vocab: `regenerate: <command>` -- take either side and re-run the generator, for lockfiles and generated fixtures; `union` -- for append-only files). Deterministic and fail-closed: only declared paths get a strategy. Strategy-resolved content is derived output and needs no re-review beyond the post-rebase gates. A generated path has exactly ONE owner: either the ticket's `## Scope fence` (agent regenerates in-branch, the default) or a host-declared merge-time `regenerate:` path -- never both; the scope-fence gate exempts host-declared strategy paths. The same ownership law governs FENCE AUTHORING: a deliverable that hooks, writes, or reads an engine seam fences the module that OWNS that seam -- the run's terminal `state_transition` write and the section 11.2 terminal handler (harvest -> dispatch -> journal -> wipe) are the driver's (`chupa/runner.py`); the stage-terminal OUTBOX lift and stage-evidence gathering are the stage layer's (`chupa/stages.py`), and section 10's "the driver lifts the outbox" means the driver INVOKES that one stage-layer lift path, never a second copy; admission is the merge queue's (`chupa/merge.py`); the eligibility sort is the scheduler's (`chupa/drain.py`); a cap draw is owned by the module that journals its `cap_consumed` event -- never only the module that calls into a seam or the helper that computes for it; `requisition_review` treats an outside-owner hook as a forced-file closure gap and rejects the ticket at authoring. Wherever a deliverable's `expects:` list names a file, the deliverable prose states what that file OWNS and the tests must import and exercise the production module -- a near-empty stub satisfying a file-existence check is the false-green shape this rule exists to refuse. (A rerere replay cache with its custody protocol, and a conflict-only micro-rework mode, are D10 returns at the first chronically re-resolved conflict the conflict facts show -- section 18.)
2. **Full Rework** with conflict context and invalidated approval (re-review) for every conflict the mechanical rung leaves.

Strategy caveat: an auto-resolved path can stay green while silently changing meaning, so retro watches strategy-resolved merges -- a resolution later implicated in an integration-red or a bug ticket revokes that path's strategy declaration.

### 9.6 Cross-ticket overlap

**Cross-ticket overlap: resolved at merge, measured for the future.** Author-time path prediction (fence-vs-fence) stays rejected, and under single-flight dispatch (D2) no second in-flight run exists to overlap. The dispatch-time overlap skip and the pre-review hold -- spend optimizations that only pay off under a concurrent pool -- are DEFERRED with that pool (section 18); their law is recorded here for the return: never act on estimate-vs-estimate; act only when at least one side is an OBSERVED fact. What ships now is the MEASUREMENT: the scope-fence gate already computes `git diff --name-only` per branch, the driver journals each branch's observed changed-file set at implement-terminal, and every merge admission journals its CONFLICT FACTS -- the conflicted file list, the resolving rung (counting strategy hits, because a path that repeatedly needs mechanical resolution is chronically contended even though every merge "succeeded"), and integration-red implicated paths. Those facts are the evidence stream that earns the deferred checkpoints, a dispatch-serialization knob, or a retro-proposed refactor-split back via D10 -- measured contention, never a guess.

### 9.7 Watchdogs

**Watchdogs: liveness and progress are different questions.** Per-stage `asyncio.wait_for` using the ticket's time budget with an expected-to-stuck floor (guard against expected==stuck authoring mistakes); process-group kill for agent subprocesses. A heartbeat answers only "is the run alive?" -- the wasted hours live in busy-but-spinning runs -- so the watchdog also runs SPIRAL detection over the agent adapter's event stream. The adapter CONTRACT requires one JSONL event per tool call from any integrated agent CLI, recorded to the run's attempt spool (section 6). Three time regions per ticket size class: healthy (below expected x 1.5) -- log, do nothing; soft band (expected x 1.5 up to stuck) -- notify on the signal; stuck -- the hard timeout path. v1 ships ONE cheap deterministic signal, no model calls ("declared output file" = any path matching the ticket's `## Scope fence` prefixes):

- **Spend-without-progress:** token/cost burn since the last mutation to a declared output file crosses a threshold -- an ENGINE CONSTANT, never a new config knob: spend since that mutation exceeding 3 x the serving row's per-call cost basis (metered usage, else `limits.est_cost_per_call_usd`, section 6) -- the shape-blind signal that catches a thrasher whatever its thrash looks like (debris accumulation, command repetition, poll loops, or file-diverse spinning alike burn spend without moving a declared output).

Additional signal SHAPES -- throwaway-file accumulation, tool-call repetition, mutation-entropy stall, poll-loop match -- and a degraded-watch mode for a stream-less CLI are D10 returns, each earned by a pinned spiral fixture the shipped signal misses (section 18). The cross-ATTEMPT analog -- the same terminal reason repeating across attempts -- is the failure spine's identical-terminal short-circuit (section 11.4), not a watchdog signal.

The signal tripping in the soft band pushes ONE notification per run (the notify key carries the run sequence, section 6: re-tripping within a run never re-pages, a NEW run's spiral pages again). NO AUTO-KILL: the human decides -- kill (`chupa kill <run>`, SIGKILL of the run's process group, section 16), inject guidance (edit the ticket THEN kill: attempt renders are immutable per invariant 2, so an edit reaches the next attempt's render, never a running one), or let it cook. Every observed spiral becomes a permanent detector fixture (the recorded event stream from the run's pinned attempt spool, section 6, plus the expected verdict), so the signal set is regression-tested against a corpus and each deferred signal shape returns citing the fixture that earned it; an LLM-as-judge signal stays unbuilt until a spiral appears that no cheap pattern can express. The bottom layer is a dumb external heartbeat (systemd timer / cron) checking the daemon's heartbeat file -- touched by the main loop each cycle ONLY while its watched core tasks (workers, merge queue, box consumer, watcher) are live, so a dead or wedged core task stops the touch and the mtime check catches it; unrelated to the reserved journal `checkpoint` event (D2). No LLM in the bottom layer. One kill-switch flag pauses all workers at the next safe checkpoint.

## 10. Git and GitHub

### 10.1 Main line and worktrees

- Local `main` is the blessed line. Branch per ticket in a worktree off one shared `.git`, created at `<worktree_root>/<stem>` under the config-declared `worktree_root` (section 15; shipped default `<state_dir>/worktrees` -- instance-local and gitignored with the state dir; the stem names the worktree dir exactly as it names the branch). The merge queue SQUASH-merges locally and deletes the branch: main history is one commit per ticket (per-ticket bisect granularity, no agent WIP-commit noise); intra-ticket history is disposable, the durable detail lives in the journal and run record. The branch name is the ticket STEM verbatim -- no `ticket/` or other prefix (section 13: the one identity reused as dir name, branch name, and squash trailer). Each squash commit's subject is `chupa(<stem>): <ticket Goal line>` and it records `chupa-ticket: <stem>` and `chupa-reviewed-sha: <sha>` trailers, so reconcile and dependency-eligibility can map an integrated commit back to its ticket and approved SHA after the branch is deleted -- the identity D3's world-wins reconcile needs. No PRs, no `gh`, no PR-state failure modes in the loop.

### 10.2 Admission lanes

- **Two admission lanes, one writer.** The serial merge task is the single writer to main; everything reaching main goes through one of two lanes: (a) squash-merges of reviewed ticket branches -- code; (b) TICKET-PLANE COMMITS -- mechanical, path-fenced to `tickets/**` -- by which stages persist process artifacts directly: authored tickets (Author, box triage, human intake), run records, check reports (`checks.json`), review verdicts, harvest `attempts/` dirs, evidence copies, decision records, retro reports (section 14). Ticket-plane commits need no branch and no review (process record, not code); a ticket-plane commit touching anything outside `tickets/**` is refused, with one named exception: the rendered root AI files of the `chupa:core` bootstrap refresh (section 15), a deterministic drift-linted render the daemon commits mechanically after an engine upgrade. (Seed `ticket.md` files reach main through this ticket-plane lane; their REFUSABLE review point is the seeding ticket's own Check stage, section 19 -- a refused seed never commits, so no code-lane exception exists or is needed for `tickets/**`.) The lane's writer validates what it commits: schema checks for artifacts it knows; evidence files are declared binary data and exempt. Failed-attempt artifacts and the tickets of runs that never merge reach durable history through this lane -- custody never depends on a ticket succeeding. Ticket-plane commits interleave with code admissions in the same serial task, so "single writer to main" stays true. Custody at the worktree seam: the agent's own ticket dir (`tickets/<stem>/`) inside its worktree is its OUTBOX -- run record, `checks.json`, box-message files, evidence -- and the scope-fence gate structurally exempts `tickets/<stem>/**` EXCEPT `ticket.md`, which stays read-only to the agent (the no-self-editing rule, section 11). At every stage terminal the driver lifts the outbox into the canonical tickets dir and commits it via this lane -- ONE ticket-plane commit per stage terminal, subject `chupa(<stem>): <artifact-kind>` (e.g. `run-record`, `review`, `checks`), no trailers (trailers identify the CODE line, not the process record) -- ingesting box-message files into the Suggestion Box. Outbox files are scooped from the worktree FILESYSTEM and never committed to the ticket branch: the branch carries code only, so no rebase ever replays a `tickets/**` commit against the already-lifted copies on main, and a branch that does carry one fails MERGE-SAFETY with the paved road "leave outbox files uncommitted; the driver lifts them". The scope-fence gate reads the branch's committed diff; uncommitted worktree debris is watchdog territory (signal 1), wiped with the worktree. The squash-merge applies the CODE diff only; `tickets/**` never rides the code lane.

### 10.3 Review and GitHub sidecar

- Review happens on the local diff (`git diff main...<stem>`); the verdict is a review artifact pinned to the reviewed SHA, persisted via the ticket-plane lane to `tickets/<stem>/review.md`; the merge gate requires an approval for the SHA it admits (carried across a clean rebase per section 9).
- GitHub is a checkpoint sidecar: a mechanical Effect pushes main (and optionally a mirror) after every K merges (shipped default K=5) or daily. It can never block the loop; push failure is a soft finding to the Suggestion Box, and a FAILED push never marks its trigger window done -- the effect re-fires at the next trigger until a push lands, because an attempt that records itself as done on failure silently ends the offsite copy. The sidecar ships with the Phase 3 daemon and its Timer (section 19): the sole offsite copy of an unattended multi-phase build does not wait for the sidecar phase.

### 10.4 The git wrapper

- All git access goes through one `git.py` wrapper -- argv lists, dir-pinned (`["git", "-C", dir, ...]`), constructed with a REQUIRED keyword-only child `env` (never a `None` default: the process seam consumes a mapping, and section 6's key-injection rule needs every caller to state what a child inherits), executed through the process-exec seam as ASYNC subprocesses so nothing blocks the event loop (D2). The Phase-1 op set -- the ONE canonical enumeration, which prompt 5 (section 0) defers to so the list cannot drift from its consumers -- is `init`, `status --porcelain`, `rev-parse`, `diff --name-only <base>...<stem>` and `diff <base>...<stem>` (the scope-fence gate and Review both read the branch diff -- this section and section 9), `add`, `commit`, `branch`, `worktree add`/`remove`/`prune`, `rebase` with its `rebase --abort` dual (a refused conflicted rebase is ABORTED before the refusal returns, so the worktree sits on its own branch head -- a refusal that leaves a rebase in progress strands the very branch it tells the operator to re-run), `restore` (the merge admission's ticket-plane restore, section 9), `merge --squash`, and `describe --tags --always --dirty` (diagnostics-only: it derives the section-6 lockfile `instance_id` for an untagged dev instance, enumerated here so the D1 all-git-through-`git.py` law holds). The richer merge-queue resolution ops a conflict needs (per-path merge strategies) are Phase 3 (section 9); rerere is a D10 return (section 18). Worktree cleanup uses `git worktree remove` + `prune`, never bare `rm -rf` (orphaned-metadata lesson). An orphan sweeper reconciles worktrees at daemon startup.

## 11. Failure spine

Uniform routing on the outcome envelope; the recovery path is the mechanical sandwich:

### 11.1 Caps

**Caps fire first, before any model call.** Max diagnosis invocations per ticket (shipped default 6); max retry-like actions (shipped default 6, never set above the diagnosis cap); max premise bounces (default 2 -- Author<->Implement round-trips on `premise_failed`, invariant 4); max hardening tickets per entry unit (shipped default 3, section 11.4); max infra terminals (shipped default 6 -- `infra_error` and `timeout` draw this budget, so a crashing review call or a hung subprocess is bounded exactly like a model failure, never an unbounded park-and-retry loop the retry cap cannot see; a provider failure from a call that RAN lands here by construction; a drought -- no callable candidate, pre-dispatch or discovered mid-run -- parks cost-free instead (section 6)). Every non-ok terminal draws from one of these NAMED budgets -- `gate_failed` and in-stage re-prompts from retry, `premise_failed` from premise_bounce, `infra_error`/`timeout` from infra -- so no failure class can loop outside the cap system -- the one exception is the drought-reason `infra_error`, which draws nothing and is bounded by its routing-resolves re-entry gate and the fleet-wide drought escalation (sections 6, 13). Three refusal events map onto the vocabulary explicitly, each a `gate_failed` drawing retry: a review REJECT verdict (the review surface is a gate, invariant 3); a conflicted rebase every live resolution rung refuses (pre-Rework, section 19 -- the abort leaves the branch re-runnable, section 10); and an EMPTY COMMITTED DIFF at the verification gate, unless Implement proved `already_satisfied` (invariant 4) -- the one sanctioned empty-diff settlement. The diagnosis and retry defaults are 6, not 3, because the escalation ladder (section 11.4) draws a cap unit per rung: a hard ticket climbs tier-then-effort AND must still have budget to LAND at the top rung, so a cap that only covered the climb would RMA every hard stem to a human. These spine caps are config-declared (the `caps:` key, section 15) with the shipped defaults above, checked deterministically BEFORE any model call -- never model-decided -- present from the Phase 0-2 failure spine and distinct from the Phase 3 THRESH spend and rate budgets (section 6). The retry cap counts BOTH retry senses (section 2): in-stage re-prompts and cross-attempt retries draw down the one budget, and that bound exists from Phase 0 with the driver. ONE case has no lineage to fold: an AUTHORING-time in-stage re-prompt -- the Author driver's re-prompt on a `requisition_review` snag, run BEFORE any `ticket.md` is committed and so before any stem or lineage exists (section 11.2 assigns the lineage budget at the first ticket-plane commit) -- is bounded by the DRIVER'S LOCAL per-invocation allowance sized from `caps.retry`, never by the journal cap fold (the section 11.2 in-memory ban governs LIFETIME lineage budgets; pre-lineage there is nothing durable to fold), and an exhausted authoring allowance terminates the authoring pass with the cap NAMED; the lineage fold governs the committed stem's in-stage re-prompts and cross-attempt retries from its first ticket-plane commit on. Because each cross-attempt retry rides a FRESH diagnosis (the sandwich's rung order), the retry cap is never set above the diagnosis cap: a retry the diagnosis budget cannot cover is a diagnosis-STARVED re-run -- it repeats a failure with only the raw prior findings and no new steering, at full model spend -- so a stem whose diagnosis budget is spent escalates to the Reject queue rather than drawing another retry. If any cap is spent, terminate to the human Reject queue without invoking the model -- and the recorded reason NAMES the spent cap verbatim ("diagnosis cap spent", "infra cap spent"), never a generic verdict-shape message that sends an operator chasing a phantom model failure. (The Reject queue itself arrives with the Phase 2 spine; in Phase 0-1, before it exists, a spent cap or any non-ok terminal just journals its state transition and exits nonzero, leaving ticket and branch in place -- `19.P1`. The exit contract holds for FAULTS too: nothing reaches the operator as a raw traceback. A fault outside the stage vocabulary still exits as a named, stopped verb -- an unresolvable binary surfaces as the section 15 seam's config/setup refusal, and a key left mid-effect by a dead run (an intent with no completion) is reported with the key and the run that stranded it; the orphan's DISPOSITION is fixed -- restart-reconcile (Phase 3) reaps it to `abandoned` exactly like reconcile-on-entry (section 11.2) -- never a silent retry and never a traceback.)

### 11.2 Auto-harvest and the terminal handler

**Auto-harvest before wipe -- on EVERY non-ok terminal.** The driver's terminal handler order is fixed: harvest -> dispatch -> journal -> wipe worktree, where dispatch is the section 11.3-11.4 recovery (the one diagnosis call and its cap draw, then the deterministic routing decision) and journal writes the run's SINGLE terminal `state_transition` carrying any `routed: reject_queue` marker the routing set (section 6). Dispatch PRECEDES the terminal write for a load-bearing reason: the routing predicate reads the FINAL cap state -- including this recovery's own diagnosis draw -- so the marker rides the terminal it belongs on; a terminal journaled before dispatch cannot carry its own routing. Harvest still precedes both (the diagnosis call reads the harvested material) and the wipe still comes last: no worktree is wiped until after its terminal is journaled, and a crash mid-dispatch leaves a `running` with no terminal -- reconcile's orphan reap, below. The section 9 ownership-law parenthetical states this same order -- the two statements never diverge. Killed, stalled, and timed-out runs route through the same handler; orphan worktrees found at restart are harvested before the sweeper removes them. Before the Phase 3 daemon exists, the same reconcile runs ON-ENTRY: a `run`/`drain` scaffold, holding the sole writer lock, reaps any orphaned in-flight run -- a `running` with no terminal, an `effect_intent` with no completion -- the moment it becomes the writer, journaling an `abandoned` terminal and removing the orphan worktree (Phase 1 reaps bare; Phase 2 folds in this harvest; Phase 3 moves it to daemon startup). The `abandoned` terminal a reap journals is what FREES the stem: keys are run-scoped (section 6), so the next entry takes the next run sequence and a fresh keyspace, and teardown-and-create clears the dead run's worktree and branch. An `abandoned` or non-ok stem therefore stays ELIGIBLE, and its re-run is real work -- never a replay of the recorded failure, never a removed worktree's path handed to a stage. Re-authoring under a fresh stem is DEAD as a recovery path for a LIVE lineage: a rename is never machinery, and no rename or re-author resets caps (the lineage law below). The sanctioned retirement for ANY confirmed lineage that will never merge (obsoleted or superseded seed included) is the section 13 `reject <stem>` kill -- journal-identity resolution, `rejected` stamped, section 9's dead-dependency handling fired (it resolves THROUGH the supersedes map, both directions), caps and history preserved -- never a drain special case keyed to stem names. Distinct and SANCTIONED after that retirement: SUCCESSION -- a FRESH REVIEWED same-goal stem, narrowed or split, on a fresh branch never the rejected candidate's, authored via touchpoint 1 intake (the operator its reviewer, section 13) or a reviewed machine authoring, free to cite the rejected lineage's committed Check and review artifacts (`tickets/<old-stem>/checks.json`, `review.md` -- durable ticket-plane history, section 10) as Context evidence. A retirement WITH a named successor journals the SAME supersedes-map entry a Rework split does (old stem -> successor stems, section 9), so every dependent -- the phase exit's transitive reads included (section 19) -- resolves through the map instead of stranding on a dead edge; only a successor-less kill leaves dependents to the bare dead-dependency events. UNATTENDED AUTHORITY: when an immutable stem parks or terminally rejects SOLELY because a base-reproducible plan, engine, or test defect made its unchanged contract impossible, the recovery chain itself performs the state-only `reject` plus succession once the fix is committed and green -- this pair rides section 19's answer-a-Reject-item touchpoint, never a new authority -- and the SAME root-cause defect sanctions it ONCE: recurrence is an operator boundary, as is every park with any other cause. The cost model is stated, not hidden: under drain's park-on-red run-to-quiescence loop (section 18) and deterministic sort, a persistently red stem is re-attempted findings-fed at real model spend, down to its remaining `retry` cap, while the rest of the queue proceeds. The cap is a LIFETIME budget per stem, never per-invocation: every draw journals a `cap_consumed` event NAMING ITS CAP and recording the `ticket_sha` its run was dispatched against (section 6) -- `ticket_sha` is the git BLOB SHA of the committed `tickets/<stem>/ticket.md` content (hash-object identity, never a commit id: run-record and review ticket-plane commits move every commit id but not the ticket's blob, so only a content edit moves it) -- and each cap's remaining budget is derived at entry by the ONE journal cap fold, which counts the lineage's `cap_consumed` events that name THAT cap -- a fold that ignores the cap name draws every cap down against one budget, a single-cap assumption the next cap in the vocabulary (section 11.1) silently breaks; an in-memory counter is wrong by construction, because it forgets across invocations and across the drain's self-upgrade re-exec. Cap budgets are scoped to the STEM'S LINEAGE, assigned once at the stem's first ticket-plane `ticket.md` commit (intake or authoring, the same event section 9's age term reads) and invariant across every edit and rename: the cap fold counts every `cap_consumed` naming that cap across ALL ticket shas of the lineage, and `ticket_sha` is recorded on each draw for audit and attribution only -- it NEVER selects, clears, or refills a budget. There is no content-edit cap reset: an edit reaches the next attempt's render (an edited ticket is new work for the IMPLEMENTER, not a new budget), and the ONE re-arm is the operator's Reject-queue `keep` (`confirm <stem>`, sections 9 and 13): its journal `signal` also bounds the fold, so draws before the stem's latest OPERATOR-actor keep fall out of the count -- the auto-keep's machine-actor signal (section 11.4) resolves the verdict hold and NEVER bounds the fold, and the double-confirm refusal (section 13 touchpoint 3) keeps that re-arm finite -- and a draw recorded with NO `ticket_sha` counts against the current budget so a journal written before this mechanism never reads as refilled. That lineage-scoped count is the single cap fold, defined in the journal beside the run-state vocabulary it reads (section 6); a cap-spent stem stays parked and reported, never silently re-armed; the drain's provisional-quiescence re-offer fold, on discovering a spent cap, RECORDS the releasable Reject-queue arrival before returning exactly as the run-terminal path does (section 9's marker -- answered by the section 11.4 auto-keep only at remaining budget, by the operator's verdict otherwise), so no lineage is left releaseless, and a cap-spent stop never advertises `drain` as its own release (the section 0 prompt-11 drain text's "stays parked ... never re-offered" governs re-DISPATCH only, never the arrival record). Drain is an operator action until the Phase 3 daemon, and the Phase 2 escalation ladder is what routes a repeat offender onward -- until it lands, the journal-derived cap itself is the bound, never the operator's finger. Harvest is a fail-closed ALLOWLIST extraction (never "everything except the diff"): the run record if written; structured gate findings and the StageResult; the stage's terminal REASON when the outcome carries no findings (for `invalid_artifact`, the schema-validation error string the driver logged); a capped stage-log tail and a capped adapter event-stream tail (both cut from the attempt spool, section 6); `git diff --stat` (names and counts, never content); wall time, cost, attempt number. Every non-ok terminal NAMES where its detail lives -- the `attempts/<n>/` dir once harvest exists, the engine log path before then (Phase 1). The unreviewed code diff never enters the ticket spec. Attempt artifacts land in `tickets/<stem>/attempts/<n>/` (ticket-plane lane, section 10; `<n>` IS the section 6 run sequence -- the same number that keys the run's effects and names its spool dir -- so cross-run re-entries never collide); the renderer for attempt N+1 automatically includes a "Prior attempts (informational, unverified, not reviewed)" section built from them -- BOUNDED, so history never grows a render into the section 8 bound on exactly the lineages with the most history: once an attempt's harvest has a journaled diagnosis `lessons` (section 11.3), every later render carries that attempt's typed lessons and terminal reason (the section 11.4 comparison key), NEVER the raw harvest payload, regardless of that payload's individual size -- cumulative accretion, not any one payload, is what crosses the bound; raw harvests stay durable at `attempts/<n>/` for the operator and the diagnosis call, and only a not-yet-diagnosed attempt's harvest renders raw. -- the ticket file itself is never edited, so acceptance criteria and predictions cannot be clobbered, and nothing depends on a human running a harvest verb. POSITION is part of this contract: the prior terminal's UNRESOLVED findings and their paved roads render as an itemized clear-these-findings block in the SAME prompt position as the acceptance criteria -- criteria-position is what a re-prompted implementer acts on; an appendix is what it skims -- marked attempt-scoped and rendered fresh each attempt, never written into `ticket.md` (findings accreted into criteria harden stale attempt guidance into permanent acceptance and eventually contradict the work). The section has one SENIOR source that predates harvest: the prior run's terminal findings artifacts -- review.md's reject findings, a failing checks.json -- already durable in the canonical ticket dir when the stem re-enters (ticket-plane lane, section 10). The re-entry renderer folds them into this same prior-attempts section, untrusted data like all of it, with no harvest, no diagnosis call, and no new bookkeeping: the run-entry fold that derives the run sequence (section 6) already reads the prior terminal event, so the renderer knows a prior run ended and how. This REJECT-FINDINGS RE-ENTRY ships WITH the Phase 1 drain verb (section 19; realized as the section 0 prompt 11-12 pair, both landing before any seeded queue runs) and depends on run-scoped keys alone, so no drain over a seeded queue is ever findings-blind. Harvest EXTENDS the same rendered section with the material only the dying worktree holds -- one rendering seam, never a second path. Harvest is soft: a harvest error journals a finding and dispatch proceeds. Setup-death short-circuit: a workspace that died before doing anything skips harvest.

### 11.3 Diagnosis

**One diagnosis LLM call.** Context: state, ticket, run record if any, capped log tail, capped diff. One question: what should happen next? Verdict vocabulary is closed (retry | escalate | split | reject | abandon-human); a verdict outside the set is treated FAIL-CLOSED as a mechanical RMA to the Reject queue, never a silent retry. `retry` re-runs at the SAME capability (a fixable oversight the findings now steer); `escalate` says more CAPABILITY would help and hands the knob to the deterministic ladder below -- the model RECOMMENDS escalation, it never picks its own tier or effort. The verdict includes a `lessons` field, journaled and rendered as the harvest's form in every later attempt's prior-attempts section (section 11.2) -- diagnosed raw payloads never re-render; no extra model call. Lessons are bounded to the record: each restates a finding the terminal carries and cites the plan text or merged code that answers it, never naming a record, field, constant, or mechanism neither states; a fact neither states is a `spec_gap` (section 11.4). Synthetic short-circuit: if the workspace is gone, write `abandon-human` mechanically and never ask. `budget_exceeded` is the second mechanical short-circuit: the exhausted ceiling blocks the diagnosis call itself (section 2's pointless-call rule), so the stem parks like a provider drought -- no cap consumed, no Reject routing -- and re-enters eligibility at the first dispatch cycle whose pre-call check clears (window rolled or ceiling raised, section 6). An over-bound render refusal (section 8) is the third mechanical short-circuit: the ticket's text against the bound is arithmetic -- a ticket-text defect, never implementer failure -- so NO diagnosis call, NO cap consumed, and the stem PARKS like `premise_failed` (section 18 -- released only by a ticket-plane content change that shrinks or splits it) until Rework is live, then dispatches mechanically to Rework `split`; section 11.4's pre-Rework fail-closed split-to-Reject routing (and section 19's restatement) governs diagnosis verdicts on IMPLEMENTED attempts only -- a confirmed ticket never terminally rejects at zero attempts over prompt size.

### 11.4 Deterministic dispatch and the capability ladder

**Deterministic dispatch.** A match on the verdict string: `retry` re-runs at the authored capability; `escalate` walks the CAPABILITY LADDER one rung, deterministically and MODEL-FIRST -- raise `agent_tier` to the next tier that resolves a DIFFERENT model (a bump resolving the SAME model, e.g. `high`->`max` where the config shares them, is SKIPPED so no attempt is wasted on a no-op), and once no higher model exists raise `agent_effort` one step toward `max` -- the RUNG is journal-derived, never a ticket edit: each escalate dispatch records its rung on the body of the `cap_consumed` event its retry draw already journals, scoped to the stem's LINEAGE like the caps (folded at entry, section 11.2), dispatch resolves the effective (tier, effort) as authored frontmatter plus the folded rungs, and `ticket.md` is NEVER edited to escalate (an edit changes neither budgets nor rungs; the operator's Reject-queue `keep` is the one event that resets both, with the spent spine caps of section 13 touchpoint 3; frontmatter is the STARTING capability, section 13); Rework may choose split (Rework is a Phase 3 deliverable, landing with the merge queue whose resolution rung 2 it is -- section 19; until it lands, a `split` verdict dispatches fail-closed to the Reject queue like a spent ladder, and in Phase 1, before that queue exists, the stem just terminals non-ok -- never a silent retry); RMA to the Reject queue only when the ladder is EXHAUSTED (top model at `max` effort). Model first because the model is the dominant capability lever and nothing sits above the top one, so max effort on that model is the final rung. The failure-spine caps (section 11.1) are sized to cover the full ladder, so a stem can climb every rung before RMA; a longer model ladder raises the caps to match. Oscillation detection: consecutive snag lists alternating the same findings short-circuit to Reject, and so does a retry that comes back STILL failing the same gate code it was dispatched to clear -- returning to the identical wall is not findings-fed progress at the CURRENT capability, so it climbs the capability ladder above instead of re-running at the same rung; only when the ladder is EXHAUSTED (top model, `max` effort) does the identical wall short-circuit to Reject. The rule generalizes across the WHOLE terminal vocabulary, not just gate codes: K consecutive attempts ending with an identical terminal reason (shipped K=3) -- the same gate code, the same `infra_error` reason string, the same timeout (EXCEPT a drought reason -- open breaker or exhausted tier -- which drought-parks cost-free per section 6, never laddering or Rejecting) -- short-circuit past further same-rung retries (to the ladder while rungs remain, to park/Reject when none do) regardless of remaining budget, because repeating an identical wall is never progress whatever the wall is made of. Only `authoring_error` walls climb the ladder: more capability cannot supply a fact the spec omits. A `spec_gap` finding never retries or escalates, and an Implement `premise_failed` naming an entry unit that is missing or lacks a SPEC DEPTH part is a `spec_gap` of that unit, routed the same way and drawing no `premise_bounce`. When an entry unit governs the ticket (section 19), the engine files a HARDENING ticket and holds the stem on it: stem `harden-<row stem>-<n>` (`n` the unit's hardening round, from 1), `source: seed`, the row's starting tier and effort, engine-composed (no Author call), fenced to `CHUPA_PLAN.md#19.P<n>.<stem>` alone, citing `19.L`, its phase unit, the entry unit, and the row's `cite`, its criteria each gap fact stated in the unit consistent with merged code and plan lint green; it runs the normal Implement, Review, and merge path, and its `run.md` judgment calls record every choice it made. The held stem journals one `spec_gap_hold` signal (`{awaits: <hardening stem>, gaps: [<finding>]}`), is ineligible until that stem merges, and its release re-run draws no `retry` unit; past the hardening cap the next spec gap routes to the Reject queue. Without an entry unit, a `spec_gap` routes as any other gate failure. NON-CONVERGENCE -- K consecutive rejections by one gate that each clear prior findings while raising new ones -- routes as a spec gap, never up the ladder. Pre-daemon default verdict: the bootstrap drain runs headless -- zero human input (section 19), and supervised-merge holds bind the daemon era, never the bootstrap drain (section 12) -- so no hold waits on a human. A Reject-queue arrival whose `retry` cap still holds budget auto-resolves to `keep` (one findings-fed re-entry, one unit drawn -- DRAW-DOWN only: its machine-actor signal never bounds the section 11.2 cap fold and never re-arms a spent cap; re-arm is the operator's manual keep alone, bounded by the double-confirm refusal, section 13 touchpoint 3) inside the same drain; at spent budget the stem reaches a terminal-without-merge and the drain proceeds to the rest of the queue -- never a park for a verdict no headless run can deliver. The caps bound the spend; `confirm` and `reject` are the daemon-era operator surface, present only when an operator is watching, never a stop in the bootstrap drain. A findings-fed retry earns its next attempt only by CLEARING the finding it was handed, never by trading it for a new evasion of the same code -- that distinction is what stops a hard gate from merely relocating the spiral from prose-argument into evasion-invention. Cross-attempt retry is always a fresh worktree (never the in-stage re-prompt loop of section 5); only the branch name and journal history survive.

### 11.5 Flaky handling

**Flaky handling.** A check that fails then passes on a bare re-run (same workspace, no code change -- a third, narrow sense of "retry") is a bug signal, not a pass: auto-file a flake report (signature-deduped) and quarantine-ledger the test so it stops blocking merges while its fix ticket queues. A config cap bounds simultaneously quarantined tests (shipped default 5); crossing it halts further auto-quarantine and escalates (section 13), so environmental flakiness cannot silently gut the gate set. Release is mechanical AND identity-bound: the quarantine ledger entry stores its flake report's (signature-deduped) box message id, and the triage resolution that routes that report to a fix ticket records the minted stem in the message's status field -- the resolution record section 12 already keeps, never a decision-registry record -- so ledger entry -> message -> fix stem resolves mechanically, and it is THAT stem's MERGE whose green re-run lifts the entry: never a stem-name inference, never new ticket frontmatter. `resume` stays the manual override -- an HGATE journal Signal like `confirm` (section 13), materialized by whichever single writer holds the lock (the drain pre-cutover, the daemon after; the request reaches it through section 20's control inbox), the release decision journaled BEFORE the ledger changes. Ledger identity: detection -- called only after one named test fails then passes on the bare re-run -- appends one `signal` keyed `flake/<box_id>` (`{kind: flake_detected, test_id, signature, box_id}`) and folds the test into quarantine; release appends one `signal` keyed `flake-release/<box_id>/<fix_stem>` (`{kind: flake_released, test_id, signature, box_id, fix_stem}`) BEFORE folding it out, only when the box resolution names `fix_stem`, that stem merged, and the test's green re-run is observed; a repeated release appends nothing. Flake handling ships with the Phase 3 merge queue (`19.P3`).

### 11.6 Poison quarantine

**Poison quarantine.** A ticket whose run brings down the daemon or its worker is attributed deterministically: restart-reconcile journals each crash's IN-FLIGHT SET (runs with an intent event and no completion) and every member accrues one strike -- under single-flight dispatch (D2) the set is normally a singleton and attribution is exact; if a concurrent pool ever returns (section 18) the culprit is not singly identifiable, so the whole set is striked, and the escalation prints each crash's set so the human can read the intersection. K strikes (shipped default 2) auto-quarantines: journaled, excluded from eligibility (section 9), escalated (section 13). An innocent striked alongside a culprit exits the same way as the culprit: release is a human verb (`chupa resume --ticket <stem>`, an HGATE decision).

### 11.7 Second problems

**Second problems are filed, never folded in.** When an agent notices an out-of-scope problem mid-run -- an adjacent bug, a pre-existing red test, a refactor itch -- the contract is: leave it alone, record it in the run record, emit a Suggestion Box message so it becomes schedulable work (the scope fence makes the inline fix fail closed anyway). A filed problem costs a fresh, correctly scoped run later -- strictly cheaper than a blurred diff that cannot be bisected, reviewed, or reverted cleanly. A pre-existing failure the agent did not cause routes the same way: verify it reproduces on the base commit, then file it, not fix it (unless the fix is trivially in scope).

## 12. Suggestion Box and decision registry

### 12.1 Queue and producers

One durable queue, one sequential LLM consumer (sequential keeps dedup trivially consistent). On disk the queue is one atomic JSON file per message under `<state_dir>/box/`, named `<seq>-<sig8>.json` (zero-padded enqueue sequence + the first 8 hex chars of the failure signature), message id `box-<seq>-<sig8>` -- the id `run.md`'s `## Second problems filed` cites -- with the triage resolution recorded as a status field inside the file (atomic replace, D3). Message classes: `suggestion | failure_report | override_report | retro_finding | bug_report`; class-specific triage prompting lives INSIDE the single `specs/triage.md` (section 8's one-file-per-surface law): the one spec renders a per-class Task variant keyed by the message class, never a spec file per class.

- **Producers.** A second problem never folds into the diff that found it; harvest enqueues each run record's `second_problems` into the box, so a parked stem's filed fix becomes triageable work -- the machine route to the ticket change that releases a premise park (sections 11, 13).

### 12.2 Consumer scheduling

- **Consumer scheduling is era-split.** BOOTSTRAP era: `drain` NEVER scans the box; the Suggestion Box is a filed-complaint queue consumed ONLY when the operator runs `chupa triage`, which triages every pending item in one pass and stops. Producers still enqueue automatically -- only the CONSUMER is human-triggered -- and the next phase's seeds do NOT route through the box (they are direct `confirmed` ticket-plane files, picked up by the drain's tickets-dir re-scan, section 18). DAEMON era (Phase 3+): the watched continuous consumer (section 9) replaces `chupa triage`, always on, no ordering knob (D10). Separate eras, separately governed -- never read one era's cadence onto the other.

### 12.3 Duplicates and the decision registry

- **Never hard-delete duplicates.** Tombstone with a link to the existing ticket or decision. A registry record is ONE markdown file per decision or tombstone under `tickets/decisions/` (committed via the ticket-plane lane, section 15): YAML frontmatter carrying `id`, `kind: decision | tombstone`, `link` (the ticket or decision it resolves to), and the reopen window as `reopen_after_days: <int>` -- REQUIRED, no shipped default, set by triage per record, measured from the record's ticket-plane commit date -- with rationale and evidence as body. The Decision Registry makes every "decided not to implement" durable and searchable; dedup checks new items against open tickets, merged tickets, AND decisions (semantic match, not string match). Decisions may be re-opened after a time window with new evidence. Tombstone visibility: tombstoning a confirmed-class report -- a box record whose `message_class` resolves to a `confirmed` row in the policy table below (`failure_report`, `retro_finding`, and the confirmed `bug_report` rows), read from the record's EXISTING `message_class`; box records carry NO priority field, so nothing here reads P0/P1 (the table's `(P0/P1)` notes are the AUTHORED ticket's priority, never a field on the record) -- is surfaced in status and itemized at the next retro. K re-reports deduping onto the same tombstoned record (shipped default K=3) auto-reopen it, and the reopen's mechanics are PINNED, because every unstated reading violates a standing law: the INVOKER is the box's own dedup path -- whichever layer collapses a re-report onto the tombstoned record (the enqueue signature match, or triage's semantic match) counts it on that record, and the K-th fires the reopen in the same pass; box code owns its queue records (retro READS tombstones for itemization, it never mutates queue state), idempotent on (tombstone record id, reopen occurrence) -- a threshold crossing reopens once, never once per scan or per retro. The reopen CLEARS the tombstoned message's resolution and returns it to `pending` carrying a reopen marker (the registry record stays -- never hard-deleted, above), so ticket creation stays with the ONE machine-authoring seam -- the box consumer -> triage -> Author path (section 4) -- NEVER a second ticket-writing path in box or retro code; a reopen-marked message is never re-deduped onto the record it just reopened -- triage authors from it, and the ticket it authors starts `draft` UNCONDITIONALLY -- the valve exists to buy a human look, so a reopen never takes an auto-confirm row from the policy table below (GO-absent eras resolve `draft` anyway by that table's own rule; under a standing GO this clause overrides the row). Each reopen journals a `signal` keyed `tombstone-reopen/<box_id>/<reports>` (body `{kind: tombstone_auto_reopened, box_id, signature, reports}`, `reports` the post-increment count) BEFORE the resolution clears, through a journal-backed callback every journal-holding Box constructor receives (one `record_rereport` path serves both dedup layers; a Box built without it counts the re-report but at the K-th refuses `RereportCallbackRequired` without clearing), which status and the next retro's itemization read -- the false-positive escape hatch that makes a wrong dedup kill observable from inside the system (and the valve the deferred section 14 dedup-health proxies would read, section 18).

### 12.4 Admission and pre-lineage spend

- **Admission and pre-lineage spend are fail-closed.** Triage returns `author` only when the message or its class-owned evidence demonstrates a current, materially harmful behavior gap, the change is bounded to one buildable ticket, and the goal names a measurable post-change observation. A plan-wording mismatch, speculative hardening, cleanup, refactor, style preference, or test-only improvement is a decision record, not work, unless tied to reachable incorrect runtime behavior. An `author` verdict receives ONE Author invocation with its bounded local re-prompt allowance for the item's lifetime: if it commits no ticket -- schema or requisition exhaustion, timeout, provider failure, post-author validation or commit failure -- the consumer writes one decision record carrying the failure evidence and resolves the item, and no later scan invokes Author for it again; new evidence returns through the normal decision-reopen path. A recorded `author` verdict whose `produced_by_spec_version` differs from the current `specs/triage.md` version is resolved as a decision record (the stale version and the current one as evidence) with NO model call, so a policy change retires the backlog it supersedes instead of spending Author on it. Requisition-review feedback that Author stores beside a recorded triage verdict is an operator annotation outside the closed `TriageAuthor` artifact: a pass resuming that verdict validates only the artifact's own fields, never failing on the annotation. Because that one invocation is the item's whole allowance, `specs/author.md` requires a mechanical PREFLIGHT before emitting: every list item starts `- `; `Depends on` is `- none` or stem bullets; each acceptance criterion names, in backticks, an exact substring of a `## Verification` command or an observable repository path; a bug's `## Regression` is exactly one fenced command plus one or more `- carries: <path-prefix>` bullets; on a re-prompt, Author repairs every supplied finding while keeping already-valid sections byte-identical.

### 12.5 Storm control

- **Storm control.** Dedup by failure signature at enqueue -- the mechanical layer only (the semantic dedup above runs in the sequential triage consumer, never at enqueue). An ENGINE-produced message's signature is sha256 over (message class, producing stem + stage, terminal outcome or gate code, and the reason string normalized: every token containing a path separator stripped, every digit run stripped, whitespace collapsed to single spaces -- deterministic and order-stable); a bootstrap-ingested suggestion line (section 19), which has no stem, stage, or outcome, signs over (`suggestion`, the fixed origin `bootstrap-ingest`, its normalized line text); a host `bug_report` uses the intake recipe below. Plus a circuit breaker: same signature > K in window T (shipped defaults K=5, T=1 hour) TRIPS. The journaled trip PRECEDES the durable held state (a crash can never expose an unjournaled hold) and carries a trip identity. The hold suppresses the emitting stage at dispatch SELECTION -- the scheduler's seam (section 9), which keeps selecting unrelated work -- over a CLOSED pausable set of pipeline stages, a pause surface of its own, independent of the merge queue's integration-red-streak admission pause and the kill-switch pause (both section 9); a non-pipeline producer (a bootstrap-ingested suggestion, a host `bug_report`) has no emitting stage and files + alerts WITHOUT a pause. The trip is ONE journaled signal -- the section 13 `storm-breaker trip` escalation -- whose body carries the held state and the trip identity, plus ONE enqueued P0 `failure_report`: pause, P0, and alert are that one signal plus that one box message, never three separate durable records. Release is `resume` (section 18) BOUND to that trip identity, consumed exactly once within the current engine lifecycle (the running `drain` or `serve`) -- an earlier request can never release a later trip. Enqueue dedup FEEDS this counter rather than starving it: a dedup hit (an arriving item collapsing onto an existing signature) counts toward the breaker window, so upstream dedup cannot make the breaker unreachable. Ledger identity: each arrival records one `signal` keyed `storm-occurrence/<signature>/<occurrence_id>` (`{kind: storm_occurrence, signature, occurrence_id, emitting_stage, emitting_origin}`, the last two nullable strings; a producer-supplied `occurrence_id` unique per arrival and stable on replay), idempotent on an existing key; the window is the half-open `(now - T, now]` over envelope timestamps across active and rolled segments, tripping when count > K; the trip identity is deterministic over (signature, first live occurrence id, crossing occurrence id). In the BOOTSTRAP drain an offer is a whole ticket, not a selectable stage, so its hold selects the ticket whose stem equals `emitting_origin` -- before retry draws or any other dispatch accounting -- while `emitting_stage` stays diagnostic, and a null or non-ticket origin creates no hold.

### 12.6 Outcomes

- **Outcomes:** a ticket (routed to Requisition), a tombstone, or a decision record. The starting state of a box-authored ticket is set by the policy table below -- config-declared as `box_policy` (section 15), one key per table ROW (the three `bug_report` rows are distinct keys; an ABSENT key or row takes this table's value as its shipped default -- unlike the safety inventory's deliberate no-default -- while an explicit `null` is refused per section 15), so the safety inventory fences it by path -- the single knob controlling how much unsupervised authoring authority the daemon has. The confirmed defaults BIND only while a currently recorded GO baseline stands (section 19; the GO record is a journal `signal` event carrying the baselined identity -- the resolved review/author routing rows and spec-major versions, section 19 -- compared to CURRENT routing at policy-read time); absent, revoked, or identity-drifted GO, every auto-confirm class resolves `draft` in EVERY era -- supervised mode; the bootstrap era, where no GO is ever recorded, resolves `draft` by this same rule (prompt 16's `tests/test_policy.py` pin is that rule's protected instance, not an exemption). The BOOTSTRAP era needs no exemption here: its box is consumed only by the operator's `chupa triage` (a human is present at every scan), so a box-authored ticket takes its table default -- almost always `draft` -- and the operator confirms only the few worth building; nothing from the box auto-confirms or auto-runs while chupa builds itself, and the recovery for a stalled bootstrap build is the operator editing the plan and rerunning, never an in-engine loop off the box. Phase seeds are NOT box-authored -- they are direct `confirmed` ticket-plane files (section 19). The policy table below binds the DAEMON era on host work only:

  | Box item class            | Starting state      |
  |---------------------------|---------------------|
  | `failure_report`          | `confirmed` (P0/P1) |
  | `retro_finding`           | `confirmed`         |
  | `override_report` (aggregated rule defect) | `draft` |
  | `suggestion`              | `draft`             |
  | `bug_report` -- self-diagnosed by the host app | `confirmed` (P0/P1) |
  | `bug_report` -- player-submitted, repro attached | `confirmed` |
  | `bug_report` -- player-submitted, no repro | `draft` |

  **Scope override (applies to every row).** Regardless of class, a box-authored ticket whose `## Scope fence` touches the ENGINE-PLANE SAFETY INVENTORY starts at `draft`, so a human sees any change that could widen the daemon's autonomy or shrink its oversight. The inventory is a closed, config-declared path list covering: gate definitions; prompt specs; closed-vocabulary lists; gate severity/trigger config; this policy table and the auto-confirm classes; host low-risk path declarations (the re-review skip list, section 9); per-path merge strategies (a `regenerate:` argv runs at merge time, section 9); MERGE-SAFETY tier membership; failure-spine caps and the quarantine caps; spend ceilings, windows, and provider routing/limits; and the inventory itself. The inventory has NO shipped default and absence FAILS CLOSED: with no declared inventory the override cannot classify a fence, so every machine-originated ticket starts `draft` until the key is declared. The override binds every MACHINE edit of a ticket, not only box authoring: a Rework-updated or Rework-split ticket whose fence NEWLY touches the inventory reverts to `draft` (split successors inherit the check), and a machine-originated ticket carrying any non-empty `gate_bypass` starts at -- or reverts to -- `draft`: the valve's surfacing point is the draft gate, and a bypass that would never pass that gate does not get to skip it.

  **Supervised merge (the daemon-era half of supervised mode).** Starting state governs who CONFIRMS a ticket; it cannot govern whether an unproven reviewer merges unsupervised -- hand-authored tickets enter `source: human`, conductor-seeded bootstrap tickets are authored `confirmed` outright and stamped `source: seed` (sections 13, 19), and neither waits at the draft gate. So absent, revoked, or identity-drifted GO, the DAEMON's merge queue also holds: a green candidate queues for the operator's `confirm <stem>` instead of auto-admitting, while dispatch, review, and other candidates' checks continue -- a supervision queue, never a stop-the-world. The hold's mechanics are pinned here because each crosses a seam: (1) HELD is an ADMISSION state -- a typed result of the merge lane's admission, recorded after MERGE-SAFETY and the INTEGRATION CHECK pass and before ANY main-tree mutation -- never a new run Outcome or run state (the closed vocabularies of sections 5 and 6 do not grow); a held run records NO terminal until its admission settles, and the drain reads HELD as still-settling, never as ok-without-merged; (2) a held stem is EXCLUDED from dispatch eligibility and its worktree is KEPT -- no terminal fires at hold time, so the section 11.2 terminal handler (harvest -> dispatch -> journal -> wipe) never runs on it and the runner returns control to the drain without a wipe -- so release admits the reviewed artifact, not a rebuild; (3) release is the operator's `confirm <stem>`, sharing touchpoint 3's journal-identity resolution (a dirless stem is still confirmable) but NOT its Reject-queue keep semantics: a held release journals the admission's release event, never the `keep` signal that re-arms spine caps (section 11.2's fold), and the double-confirm refusal does not bind it; when main has advanced past the held candidate's checked sha, the release RE-RUNS rebase and the mechanical merge-time re-run set (section 9), the pinned review approval carrying across a clean rebase exactly as section 9 states -- a frozen continuation is never committed over moved main, and every remaining held candidate re-checks after a release advances main; (4) holds are DURABLE, and this clause AMENDS the orphan definitions of sections 11.2 and 15 in place: the hold is JOURNALED when it is recorded, and a `running` with no terminal whose journal shows a live hold is a HELD admission, not reconcile's orphan -- restart-reconcile preserves the held worktree and reconstructs the admission's authority from the journal and committed ticket artifacts, never from process memory; (5) the deliverable landing the hold fences EVERY seam owner it touches -- the merge lane, the hold-policy read, the `confirm`/`reject` release surfaces, the CLI entry, the stage layer, the drain's eligibility fold, and the runner's worktree lifecycle (section 9's ownership law names one owner PER SEAM; a hold crosses many seams, so its deliverable fences every owner, never one module). `run <stem>` -- one ticket, foreground, operator-invoked -- is itself the go-ahead (section 16: supervision here is an attention guard, not an authentication boundary), and the BOOTSTRAP drain never holds an admission at all (section 19). A currently-binding GO lifts the daemon hold; that is what the number gates. The hold is built in Phase 6 (section 19), its first daemon-on-host-work consumer; the self-build runs under the bootstrap drain and never holds, so no earlier phase builds it and no self-build seed depends on it. One machine actor exists on this surface: the Phase 6 exit harness's scripted confirms against its OWN fixture subprocess (section 19) -- delivered through the section 20 control inbox and journaled as machine-actor supervision evidence, never a cap re-arm; a live host operator surface never has a machine confirmer.

  Why: machine-detected breakage and retro findings derived from measured history auto-confirm (self-repair should not wait on the owner; the tickets still pass review); judgment-shaped items -- rule-defect proposals, new ideas -- park at the draft gate.

### 12.7 Advisory checks

- **Advisory checks cannot become theater.** Soft-gate failures are journaled per check code; a configured unhealthy streak for the same code (shipped default: 5 consecutive failures) escalates into one confirmed repair ticket whose goal is to fix the check or remove it through the normal config-change path. Soft means non-blocking -- never invisible.
- The box consumer is watched by the watchdog layer; its failure alerts via the external heartbeat, not via itself.

### 12.8 Host bug intake

**Host bug intake.** Host applications feed the same box, not a separate queue -- dedup, the decision registry, and the storm breaker are exactly what a bug stream needs. The seam is generic: the host contract declares a REPORT INBOX directory; anything host-side -- app self-diagnosis (unhandled engine exceptions, illegal-move storms, view-leak detections) or a player-facing report composer -- writes a small JSON report file there and chupa ingests it as a `bug_report`. The report schema carries origin (`self_diagnosed | player`), summary, a dedup signature (game slug + anomaly code + location + app version for self-diagnosed; semantic dedup for player text), app commit/version, optional implicated code paths, and evidence file paths.

Evidence is the point of the intake: a record-actions host attaches `initial_state` plus the action log -- a deterministic repro -- plus a capped structured-log excerpt. Triage copies evidence into the authored ticket's `evidence/` dir, and the bug gate (section 7) turns the attached replay into a permanent regression fixture: report -> replay -> regression test. Player-submitted text is UNTRUSTED at every hop: triage treats it as data and writes its own SUMMARY into the authored ticket -- raw report text never enters ticket prose, and reaches later prompts only as delimited untrusted-data blocks (section 8). Evidence files are quoted, never executed outside the deterministic replay harness (section 16).

## 13. Ticket contract and human touchpoints

### 13.1 Ticket file and frontmatter

A ticket is one markdown file: frontmatter a script schedules -- YAML between `---` fences, parsed with PyYAML `safe_load` like every YAML surface (section 15) -- plus a body an agent executes. Frontmatter is the minimum the code consumes: `state` (closed vocab `draft | confirmed | rejected | merged` -- `rejected` stamped at a Reject-queue kill via the ticket-plane lane, and the draft->confirmed flip from a human `confirm` is a journal Signal the daemon materializes the same way; `merged` is recorded at settle by the admission's `to: merged` journal transition, NOT a frontmatter restamp -- the scheduler folds merged stems out of eligibility from that journal record (D3), so a settled ticket's frontmatter rests at the value it was authored with; running state is journal-derived, never frontmatter), `source` (closed vocab `human | seed | box:<class>` -- everything machine-originated routes through the box EXCEPT a phase seed, and `source: human` is what "human-requested work auto-confirms" keys on; `seed` is a phase-boundary deliverable authored directly to the ticket plane -- by the conductor or, once self-hosting, a phase-exit ticket's Implement stage (section 19) -- born `confirmed`, never through the box, asserting the seed entry path so the record never claims a human hand-wrote machine-seeded work), `priority` (`P0..P3`), `kind` (`bug | feature | chore`, set explicitly by the author or box triage, NEVER inferred by any lexical heuristic over prose -- an inference is a rule an agent can argue with; an explicit declaration is not), `agent_tier`, `agent_effort` (both on the closed `low | medium | high | max` scale -- tier keys the `models_by_tier` map, section 15; effort passes through to the routed model; an authored ticket DEFAULTS to `medium`/`medium` -- a starting capability the failure spine's ladder (section 11) can climb from on evidence, never a blanket `high`/`high` that leaves escalation nowhere to go, and an author raises the START only for a ticket it judges known-hard), `gate_bypass`. Nothing else. Frontmatter bloat is structurally prevented by the anti-bloat law: **ticket frontmatter may only contain fields the scheduler, a gate, or the authoring/triage policy reads; audit, calibration, and training data are journal-derived projections, never ticket fields.** Field classes consciously excluded -- context-size hints, engine/model pins, agent profiles, doc-ordering modes, tags, groups, lexical bug heuristics -- enter only via D10.

### 13.2 Body sections

Body sections, each existing to remove one specific way an unsupervised agent goes wrong:

- **Depends on** -- the execution graph. The scheduler reads ONLY this; prose ordering does nothing. The graph is closed over consumption: a ticket whose scope consumes another unmerged ticket's deliverable carries that edge, and when a source spec states a deliverable order, an authored SET's edges must realize it -- an authoring pass that translates prose order into tickets asserts the edges, not just each ticket's lint.
- **Context** -- the read-first files: read-only references, distinct from the scope fence, injected into the implement prompt. The habit encoded is read-before-write.
- **On-demand** (optional) -- fenced EXISTING paths deliberately not embedded because embedding them breaches the authoring headroom (section 8); the implementer reads each from the worktree before editing it.
- **Plan contract** (optional) -- the sole channel for plan prose: a bullet list of plan ids -- a numeric section id (e.g. `section 11`), a subsection id (e.g. `section 11.4`), or a section-19 unit id (`19.L`, `19.I`, `19.P0`-`19.P6`, or an entry unit such as `19.P3.rework-stage`); a subsection or unit resolves to its `###` heading through the next `###` or `##` heading, and a section is never cited with one of its own subsections -- the renderer resolves verbatim, deduplicates, and injects at bounded size; section 22 never resolves. `Context` structurally refuses the plan file itself (grammar below), so a seed citing the plan cites sections or units, never the file.
- **Goal / Why** -- one observable post-merge outcome, plus the judgment fuel for the fork the spec did not anticipate.
- **Scope in / Scope out** -- scope-out fences the tempting adjacent cleanups; what must NOT change is as load-bearing as what must.
- **Scope fence** -- the write allowlist a gate enforces (section 9).
- **Acceptance criteria** -- every item measurable ("exits 0 when...", "is unchanged"); never "improved" or "better".
- **`## Verification`** -- the exact commands the agent runs to check its own work instead of asking a human. This is where autonomy lives; a ticket without it has to phone home.
- **`## Regression`** (present exactly when `kind: bug`) -- the ONE command that reproduces the reported defect, plus `carries:` path prefixes naming the branch-added test/fixture files the command needs; the section 7 bug gate runs it at the branch head (must pass) and at the merge base with the `carries:` paths overlaid from the branch (must fail -- for the defect, not for a missing test).
- **Definition of rejected** -- when to STOP and throw the branch away rather than churn down a dead end.
- **Time budget** -- agent wall-clock anchored (expected + stuck threshold), never human-engineer hours.

### 13.3 Body grammar

Every machine-read body section has a fixed grammar the Requisition gate validates: `Depends on` is a bullet list of stems (or `none`), each stem required to RESOLVE against existing ticket dirs, merged squash trailers, the supersedes map, or, for a machine-authored seed, a sibling seed of its own batch (`19.L`) -- an unresolvable stem fails closed -- and the same gate rejects dependency CYCLES across the authored set plus the existing graph, re-validated on every ticket write (author, rework update or split, human intake): acyclic at every insertion keeps the global graph acyclic; `Context` is one repo-relative path per bullet, each required to exist in the tree the ticket lands in (for a machine-authored seed, main, never its author's worktree) -- EXCEPT the plan file itself AND the engine's prompt-spec files (`specs/*.md`), both of which `Context` structurally refuses as governed engine prose: plan prose enters a prompt only through the `Plan contract` body section, a bullet list of plan ids (a numeric section id such as `section 11`, a subsection id such as `section 11.4`, or a section-19 unit id such as `19.L`, `19.P3`, or `19.P3.rework-stage`) that the renderer resolves verbatim, deduplicates, and injects as the sole channel for plan bytes, refused fail-closed at the grammar gate when an id does not resolve; a prompt-spec's behavior is cited the same way -- the plan section that governs the surface, never the raw `specs/*.md` file, which carries the engine's OWN data-block delimiter and so breaks the section 8 data/instruction rendering contract the moment it is injected as data; a file the ticket itself will CREATE is named in `## Scope fence` and `## Verification` ONLY -- `Context` is read-first EXISTING material, so a future path there is exactly what the existence check refuses, and a review finding demanding one is demanding the refused shape (this is the one placement rule for future paths); and `Plan contract`, optional elsewhere, is REQUIRED on a `source: seed` ticket and MUST cite, by role: a seed implementing a registry row cites `19.I`, its own entry unit, and the ids its row's `cite` names, never its phase unit, nor `19.L` unless its row cites it; a seeding or exit ticket cites `19.L`, `19.I`, its phase unit, and the entry units of the seeds it authors; a hardening ticket (section 11.4) cites `19.L`, its phase unit, the entry unit it hardens, and that row's `cite`; a seed of a phase with no registry cites `19.L` and its phase unit -- never whole section 19, nor sections 0, 21, or 22 -- so the plan bytes that OWN the machinery its row states inject (the section 9 ownership law names the owner): cited sections are the only plan bytes that inject, so a seed citing none renders an implement prompt with zero governing plan text -- a closure gap `requisition_review` rejects at authoring (section 7); `Scope fence` is one path prefix per bullet, or `CHUPA_PLAN.md#<unit id>` confining plan edits to that unit's heading range (a missing entry unit is inserted after its phase's last unit); `On-demand` is one existing repo-relative path per bullet, each also covered by `Scope fence` and absent from `Context`, refused fail-closed otherwise; `Verification` is a fenced command block, one argv-parseable command per line (each tokenized with `shlex.split(posix=True)`, never a shell, D1); `Regression` (present exactly when `kind: bug`, absent otherwise) is ONE argv-parseable command plus one or more `carries: <path-prefix>` lines, each required to match at least one branch-changed file -- the reproducing check the section 7 bug gate executes and the overlay set it applies at the merge base; `Time budget` is an expected/stuck minutes pair written as two bullets, `expected: <int>m` and `stuck: <int>m` (integer minutes); `Exit-read window` (present only on a phase-exit ticket, section 19) is a bullet list of closed-form journal-window declarations (event type + bounding criterion) the renderer resolves and the driver materializes as the exit ticket's consumed artifact (section 19's materialized journal window), refused fail-closed when a declaration does not parse. The same gate enforces the checkable-criteria floor at the grammar level: every acceptance criterion must name at least one `Verification` command or observable artifact that checks it, and banned adjective forms ("improved", "better", "cleaner") fail lint. Whether the commands ACTUALLY prove the criteria is judgment -- Review's duty, measured by the section 14 scorecard. Grammar is likewise necessary, not sufficient: feasibility is `requisition_review`'s duty (section 7). Every MACHINE-authored ticket -- `box:<class>` and `seed` alike -- is judged BUILDABLE against the shipped engine before it commits `confirmed` and becomes eligible; a `snag` re-authors within caps, an `rma` (a plan defect the author cannot fix) parks for a human. A `source: human` intake (touchpoint 1) runs it ADVISORY -- the operator is its reviewer -- so the front door never blocks on a model call.

### 13.4 Layout and run record

Layout: **one directory per ticket** (`tickets/<stem>/` holding `ticket.md`, `run.md`, `review.md`, `checks.json`, `attempts/<n>/`, evidence). Multiple artifacts per ticket are a directory listing, not a naming convention. Stems match `^[a-z0-9][a-z0-9-]{1,63}$` (lowercase kebab-case): the directory name IS the stem, reused verbatim as the branch name and the squash-trailer identity, validated fail-closed by the `ticket_schema` gate. Two reserved sibling dirs are excluded from the stem namespace by that same gate: `tickets/decisions/` (section 15) and `tickets/retro/` (section 14) -- both match the stem regex, so without the exclusion a ticket could shadow them.

The run record is the co-located receipt (surprises, judgment calls, dead ends, outcome, resolved engine/model, predicted-vs-actual divergence). Run records deliberately preserve NEGATIVE information -- what failed first, what was abandoned, what was left alone on purpose. Together with the journal they are the project's queryable memory: Author and triage query them and the decision registry before creating new work.

The `run.md` schema the `run_record` gate validates is a fixed section set: `## Outcome` (closed-vocab terminal state -- the section 5 `Outcome` vocabulary, no separate set, so a merged run's value is `ok`, or `already_satisfied` for a no-op settlement), `## Surprises / judgment calls`, `## Dead ends` (what was abandoned and why), `## Second problems filed` (box message ids, section 11.7), `## Resolved engine/model` (provider + model + spec versions that served), and `## Predicted vs actual` (the calibration divergence). Sections may be empty but must be present; the gate checks presence and the closed `## Outcome` vocab, not prose quality -- that is Review's duty. The other artifact bodies (packing slip, invoice, snag list, RMA, rework order, approval record, retro findings) are implementer-owned pydantic models, schema-validated at the stage seam but deliberately NOT a cross-version persisted contract the way `run.md`, the journal envelope, and config are.

### 13.5 Human touchpoints

Human touchpoints -- the complete list:

1. Idea intake. The front door is a file: hand-author `ticket.md` under `tickets/<stem>/` in the working tree, or template one with `chupa new <stem>`. File authorship is outside the lock fence (D2) by design; the watcher validates it and the daemon commits it via the ticket-plane lane with a fail-closed `source` stamp: a NEW stem commits `source: human` -- intake STAMPS it (an absent `source` is filled in; a new stem CLAIMING a machine source, `seed` or `box:<class>`, is refused with a paved road naming this rule -- only the machine writes those), and the auto-confirm is the intake commit's journal Signal materializing `state: confirmed` exactly like the human `confirm` flip (frontmatter paragraph above); a stem whose committed predecessor carries `source: seed` KEEPS it across an in-place correction (the section 19 recovery-edit path) -- intake never demotes an established seed, because a demotion falsifies the record (claiming a human hand-wrote machine-seeded work) and reddens any seed-integrity check on the next merge. The human never runs git against a checkout the daemon holds. Validation is never silent: `chupa new` lints synchronously, and tickets failing the watcher's parse are a named top-of-output category in `status`. Every intake commit is journaled and itemized in a `status` intake category: `source: human` asserts the ENTRY PATH, not an authenticated identity (section 16), so the operator can always see what claimed to be them.
2. Draft->confirmed on machine-originated tickets (policy table decides which classes need it; `source: human` auto-confirms).
3. The Reject queue (RMA'd tickets: keep / edit / kill; a kill triggers the dead-dependency handling of section 9 for everything that depended on it). Verb mapping is fixed: `confirm <stem>` = keep (re-enqueue, spent spine caps reset, section 9); `reject <stem>` = kill (`rejected` stamped, dead-dependency events fire); edit is not a verb -- the operator edits `ticket.md` (the intake path, touchpoint 1) and then `confirm`s. Both verbs resolve the stem against the JOURNAL identity, never by loading `ticket.md` first: a stem whose ticket dir is gone (regenerated away, section 19) is still confirmable/rejectable, and rejecting a dirless ghost clears its queue entries with a journal-only `rejected` -- a hold must never outlive its release because its file vanished (section 2). And a `confirm` on a stem with NO `ticket.md` change since its previous `confirm` is refused on the second consecutive occurrence, paved road "edit the ticket (or fix the plan and regenerate it) before re-enqueueing" -- an unchanged ticket re-fed to freshly reset caps is an infinite cap refill, not recovery.
4. Escalations -- the ONLY push channel, a closed vocabulary: stuck-past-threshold, spiral-warning (soft band), budget-exceeded, poison-quarantined, quarantine-cap crossed, provider drought, dead credential (`auth_error`), storm-breaker trip, integration-red streak (merge admissions paused), post-merge tree-hash mismatch, box-consumer death (via the external heartbeat), and Reject-queue arrival (a terminated ticket must never die invisibly while its dependents starve). Transport is a config-declared argv notify command run as an Effect through the section 15 notifications seam; unset, escalations land in `status` and the daemon warns at startup that push is off. The transport has ONE owning deliverable: the notify-transport stem named in the `19.P4` list (the transport Effect, its section 6 notify key domains, and the section 15 `notify` config parse), ordered BEFORE its first push consumer, the watchdog soft band (section 9). Until it merges, EVERY escalation here -- Phase 3's storm-breaker trip and red streak included -- lands in `status` only as a journaled signal, and no earlier seed names or invokes a notify consumer. Each escalation names its pull-side exit (`resume`, `reject`, `kill` -- section 18). Three pinned explicitly: a tree-hash mismatch pauses merge admissions like a red streak (`resume` after inspection or revert); drought-parked tickets un-park automatically at the next dispatch cycle once routing resolves (section 9); box-consumer death exits by restarting the daemon -- an operator action, not a verb.
5. Read-only status, pulled on demand: a `status` projection over the journal (merged, in-flight, blocked, spend, box activity, tombstone digest, and from Phase 5 the current-window scorecard), deterministic and write-free -- a later field is ADDED, never replacing or dropping an existing section or its wording -- consumable as a CLI verb, a written file, or a slash command; a dashboard is a possible later skin over the same projection. Never pushed on a schedule.
6. Engine release. Merged engine work reaches a RUNNING stable instance only through the release path: cut a tag, install into the stable venv, drain (the section 5 quiesce), restart. Same loop for the pre-schema-flip pause of section 5. Recurring, deliberate, small.
7. GO-baseline upkeep. Run the committed baseline eval (the GO-grade fixture harness -- the Phase 1 spike's set grown to GO grade in Phase 6, immediately before cutover, where GO gets its first reader -- a mechanical run), read its committed report -- the run-lane execution inside the drain has already committed it and mechanically recorded its verdict signal, at most NO-GO before cutover (section 0) -- and record GO, when the report earns it, via the harness's operator mode (`--record-go` carries your Author-graph judgment, section 19). The real 24-48h `serve` soak on a synthetic or host workload is part of this same operator cutover step -- run supervised, before GO is recorded; the Phase 3 exit's bounded synthetic soak is its drain-executable stand-in (section 19). Recurs after every model, provider, or spec-major routing change (section 19); until re-recorded the system rests in supervised mode -- a safe resting state, not a stall. A retro-shipped spec-MAJOR change (Phase 5) therefore revokes GO on merge by design, so spec-major self-improvements batch naturally ahead of one re-baseline; MINOR spec versions do not revoke. The post-cutover acceptance reads -- K >= 10 machine-authored tickets merged on host #1 and one real host bug loop, counted only from this engine's own journal and provenance stamps (section 6) -- are this same operator step's follow-through after cutover, never a phase-exit criterion (section 19).

Everything else is autonomous. No pipeline's resting state is a manual step.

## 14. Retro (Reconcile)

### 14.1 Triggers and reads

- Triggers: N tickets OR M days (shipped defaults N=25, M=7) OR a signal SPIKE forcing an early retro -- PER KIND, never a summed total: any one of the four signal kinds reaching the shipped default S=5 within the CURRENT retro window (counted from the latest retro-report `effect_completion` boundary below, like every other window count) fires the trigger on its own. Each kind counts exactly ONE journal-derived identity, pinned here because an unpinned operand reads as unspecifiable and silently drops the trigger (the observed loss): override = each USED bypass (a ticket admitted carrying a non-empty `gate_bypass` entry, section 7 -- the RAW uses the valve's K=3 same-code aggregation and the scorecard's bypass count already fold, never the aggregated `override_report` box message); rework = each Rework invocation (one per emitted rework order, section 4); gate-failure = each terminal `state_transition` carrying `to: gate_failed` (the section 6 run-state vocabulary); integration-red = each admission whose journaled conflict facts carry integration-red implicated paths (section 9 -- the individual reds, never the K=3 red-streak escalation, which is a section 13 pause, not this count). All THREE trigger classes ship in v1; none is deferrable, and a build that cannot author the spike trigger has a plan defect to fix, not a trigger to drop.
- Reads the journal/ledger: predicted vs actual cost and time per ticket, gate catch-rates, bypass aggregation, failure clusters. The driver materializes this window projection as the retro stage's consumed artifact -- the one RECURRING stage whose input is the journal itself (invariant 1's "plus the journal"; a phase-exit ticket's materialized exit-read window, section 19, rides the same driver seam); the committed retro report below is its persisted output.
- Dedup-health proxies (near-identical-merged and reversal-rate signals over the box consumer) are a post-host-#1 D10 return (section 18): until an incident earns them, dedup regressions surface through the operator reading retro reports and through the section 12 tombstone auto-reopen valve, which stays -- the observability is the valve, the proxy metrics are the deferrable layer.
- Conflict-hotspot trending across retro windows -- and the retro-proposed serialization stopgap and refactor-split machinery it would drive -- is a post-host-#1 D10 return (section 18). The section 9 conflict facts are journaled from Phase 3 onward, so the return arrives to an evidence stream already waiting; under single-flight dispatch (D2) conflicts are rare enough that a human reading the facts in the retro window is the v1 detector.

### 14.2 Catch and escape instrumentation

- **Per-surface catch and escape instrumentation** -- the data D10 needs to promote or prune LLM review surfaces, not only mechanical gates:
  - A CATCH is a journal-DERIVED increment per (surface, ticket), never a new emitted event: a gate or review surface raised findings -- a `state_transition` carrying `to: gate_failed` (the gate's codes in its recorded reason/findings), or the review surface's snag/rma verdict recorded in its own LLM-call `effect_completion` (keyed ticket+surface+attempt+call_seq, section 6) -- and the same stem subsequently reached `to: merged` with those findings resolved. A finding upheld at a terminal-without-merge outcome (an RMA the human confirms by killing, an abandon) ALSO counts: a surface that reliably stops the worst work must not read as prunable zero-activity. Deterministic gates and LLM review surfaces are counted the SAME way, from these fail-then-pass and upheld-at-terminal records -- NO per-catch event is emitted and no driver or stage grows a catch emitter (the section 6 EventType set carries no catch type; the scorecard below is a read-only projection, D3 and section 13's anti-bloat law), so a catch fold reading any source other than these named durable records is the fixture-only-event false green this rule exists to refuse.
  - An ESCAPE is a defect that passed every surface: a `bug_report` (or later integration-red) attributed back through the squash trailers (section 10) to a merged ticket OR a bounded range of them. Exact introducing-commit identity is a NON-GOAL. Triage narrows the range from the report's app commit/version and implicated paths (section 12), journals it with a confidence note, and the scorecard counts the escape against the surfaces that passed the range's merges. The escape PRODUCER -- triage's bug-to-merged-range attribution and the squash-trailer read op in `git.py` it needs (a trailer-format log read -- the section 10 op enumeration grows per phase, as the Phase 3 resolution ops did; never a section 18 CLI verb) -- ships with the Phase 6 bug intake (section 19), so the scorecard's escape column is Phase-6-live while its other columns are self-build-live from Phase 5.
  - The SURFACE SCORECARD is the journal-derived projection retro reads: per-surface catch rate, escape rate, bypass count. A projection, never ticket frontmatter (anti-bloat law, section 13). Zero catches AND zero escapes over N tickets makes a surface a prune candidate exactly like a gate; escapes clustering on one surface are the cited-incident evidence for tightening it.
  - Run-filed follow-ups surface through backlog hygiene (below): a stale filed item resurfaces for an explicit promote-or-kill decision; an aggregate scheduled-vs-silted rate metric is a D10 return (section 18).

### 14.3 Outputs and the retro report

- Outputs go through the Suggestion Box (dedup + decision registry for free); one single entry point for all work creation.
- **The retro report is the committed receipt.** Each retro also persists ONE report file -- `tickets/retro/<seq>.md`, zero-padded seq so listings sort in order, committed via the ticket-plane lane (`retro/` is a reserved non-stem dir, section 13) -- snapshotting what the human reads and the next retro diffs against: the surface scorecard, spend against the ceilings, calibration divergence, the tombstone digest (section 12), and every proposal with its named fixed-failure/overcorrection pair. The journal stays authoritative -- the report is a re-derivable snapshot (D3), committed so the receipt travels with the repo the way run records do. The report's commit effect (`key=retro/<seq>`) doubles as the WINDOW BOUNDARY: the N-tickets / M-days triggers and every "within one retro window" count (section 7) measure from the latest retro-report `effect_completion` event -- no new event type needed.

### 14.4 Pruning and tuning

- Retro also PRUNES: proposes deleting gates with zero catches over N tickets, compressing rules, retiring unused vocab.
- **Rule tuning guards against overcorrection.** Every retro-proposed rule or gate change must name BOTH the failure it fixes and the overcorrection it risks. Urgency and importance stay on separate axes: the urgent instance is unblocked first, the important cause is captured as its own scheduled ticket, and ordering lives in `depends` and `priority`, never in prose.
- **Backlog hygiene.** Retro resurfaces stale draft tickets for an explicit promote-or-kill decision. STALE is pinned like every other trigger operand here: a draft ticket with no ticket-plane edit across one full retro window (the window boundary above).

## 15. Engine, hosts, and instances

### 15.1 Engine and instances

- **Engine repo + per-project data plane.** The chupa repo contains engine code only; every host project (including chupa itself) keeps its own `tickets/`, config, and state. Rejected alternative: a hub control repo with one central cross-repo queue -- it divorces tickets from the code they change, and one hub bug breaks every project at once.
- **Self-hosting.** chupa runs its own development tickets.
- **Instance isolation.** An instance = one installed release + its own project checkouts, worktree roots, and state dirs. Stable = a tagged release installed in its own venv, never a symlink into a working tree; rollback = reinstall the previous tag. Stable and dev instances share only git remotes. ONE instance writes a given host repo line: the stable instance owns the host's blessed main; dev instances run against their OWN disposable host checkouts with the checkpoint push disabled; validated engine changes reach stable through the release path (tag + install + restart, section 13 touchpoint 6), never by promoting a dev instance's host main. The "tickets flow between instances through git" provision (section 5) is about SUCCESSIVE engine versions operating one repo line, not concurrent mains. Worked layout:

  ```
  ~/bin/chupa               # stable entry point, installed from tag vX.Y.Z
  ~/source/chupa            # stable engine clone (main)
  ~/source/chupa-next       # dev engine clone (feature branches)
  ~/source/<host>          # host clone: daemon writes main, human authors tickets (sec 13)
  ~/orch/<host>-work/      # stable instance: ticket worktrees + state
  ~/orch-dev/<host>/       # dev instance: its OWN separate host checkout
  ~/orch-dev/<host>-work/  # dev instance: ticket worktrees + state
  ```

### 15.2 Host contract

- **Host contract (doc authored in Phase 6, with its machinery and first external reader; until then this section IS the schema's source).** Config schema with `schema_version` handshake (refuse newer; refuse older with a paved road naming `migrate-config` -- and that verb PERFORMS a real migration, never a vacuous no-op: version 0 IS the defined prior schema, a `config.yaml` declaring the explicit integer `schema_version: 0` (an ABSENT `schema_version` stays a missing-required-key refusal at load and under `migrate-config` alike -- fail-closed defaulting, never a migration case), and `migrate-config` carries it to the current schema (the 0->1 step rewrites `schema_version` and keeps every other key byte-for-byte) -- validating the FULL migrated candidate fail-closed before ONE atomic replace via the filesystem seam, a byte-identical no-op on a current-version config, and a no-write refusal naming the cause on everything else (missing file, missing or non-integer `schema_version`, newer, older-than-supported) -- so the loader's refusal and the verb it names agree, and every future `schema_version` bump ships its migration step in the same change); additive-only ticket frontmatter; the check-runner interface; root AI files (CLAUDE.md/AGENTS.md) rendered from engine-owned templates as ONE committed file with a managed `<!-- chupa:core begin/end -->` block plus a project-owned remainder, refreshed by bootstrap, drift-linted, never hand-edited inside the block (the committed form of the two rule planes, section 8); the single-writer lockfile with instance identity; the injectable-seams inventory -- one minimal seam each (a PRNG seam is NOT in it: nothing in the engine draws randomness; it is added with its first consumer, D10): clock (a zero-arg `Clock = Callable[[], datetime]` -- one clock convention kernel-wide, not a `now()` Protocol; plus its blocking companion `Sleep = Callable[[float], Awaitable[None]]` -- every timed wait, the driver's stuck-budget race included, races the active work against an injected sleep to a clock-derived deadline, never a raw `asyncio.wait(timeout=...)`, so a test advances a deadline with zero wall-clock wait), process-exec (`async run(argv, *, cwd, env, timeout, stdin_path=None) -> (rc, out, err)`; every child is spawned in its OWN PROCESS GROUP (`start_new_session`) and every kill the seam performs is a GROUP kill -- an agent CLI spawns tool subprocesses of its own, and killing only the direct child leaves grandchildren writing the worktree; the seam also exposes a SYNCHRONOUS group kill that section 6's `abort_current` returns behind (signal-not-reap: the reap stays with the async spawner -- a SIGKILLed group can no longer mutate the worktree, which is all `abort_current` promises), and BOTH the seam's own timeout branch AND an outer asyncio cancellation unwinding through `run` route through that ONE kill-and-wait helper (section 19's Phase-0 per-stage `wait_for` stuck-budget kill reaches the seam as exactly that cancellation) -- a cancellation that skips the group kill exits with the CLI's grandchildren alive in a worktree the driver believes frozen; the group-kill promises of sections 6, 9, and 16 (`abort_current`'s contract, the watchdog, `chupa kill <run>`) are implementable only at this seam, which exposes `kill_group` plus a spawn-time pgid hook; the run-to-group binding is PUBLISHED at spawn, cleared at call return, consumed at most once by the `serve` kill path, threaded providers -> the LLM effect -> stages -> serve; `kill <run>` is PER-RUN and SIGKILL-on-receipt -- it never stops the daemon (the serve loop keeps running with dispatch and admission state unchanged; `serve` itself stops via the kill switch or an OS signal, section 18) and it is never a fold at dispatch checkpoints, which cannot kill a hung run that yields no checkpoint, while the kill-switch pause stays the distinct graceful path (section 16); a `kill` naming a run whose merge admission is in flight DEFERS: the admission-owned child is never aborted (the admission path holds the single ticket-plane writer lock, sections 6/9), the kill is consumed when the admission unwinds, and the run launches no further child; a kill signal from a prior daemon lifecycle never replays (the control-inbox identity binding, section 20); ONE active-work executor INSTANCE is threaded through the production composition -- `abort_current` (section 6) is meaningful only on the instance that spawned the active child, so no task identity is aliased and no process seam is shared between active work, notification, and the self-upgrade handoff; and under cancellation the abort/spawn composition STILL translates an unresolvable `argv[0]` to the seam's declared error, never an escaping `FileNotFoundError`; `env` is required and explicit at the seam and every wrapper above it; `timeout` is required but accepts None for the one unbounded caller -- the drain's self-upgrade handoff child, which also runs with INHERITED stdio, streamed to the operator, out/err empty in the result (section 18); `stdin_path` is an optional FILE path (default None) the seam OPENS and connects as the child's standard input -- the sole channel for an agent-CLI prompt, because a rendered prompt is UNBOUNDED and a command-line argument is capped by the OS argument limit, so a prompt is NEVER an argv element and reaches the CLI only as this file (the one the driver spools before the call, section 6); the unbounded handoff child passes none; and the seam FAILS CLOSED on an unresolvable `argv[0]` -- it raises its own declared error naming the missing binary, a config/setup refusal, never an escaping `FileNotFoundError` from spawn), filesystem (atomic `write` / `replace`), notifications (`notify(argv)`) -- kept for fake-driven testing even though re-execution recovery is refused; the notify command (section 13); the state-dir contents (journal, box queue, quarantine ledgers, attempt spools, engine log, heartbeat file -- instance-local, while the decision registry and tombstones live in the host repo under `tickets/decisions/`, committed via the ticket-plane lane, so dedup memory travels with the repo); config re-read at each dispatch cycle, so a ceiling, routing, or severity edit takes effect without a restart (the daemon reads it through the same watcher-and-debounce discipline as tickets; the pre-daemon scaffold verbs satisfy the same rule by RE-PARSING `config.yaml` at each dispatch cycle -- same cadence, no watcher); and an optional report-inbox path for host-app bug intake (section 12).

  The host contract is ONE `config.yaml` at the host checkout root -- located via the `--config` flag, else `config.yaml` at the invocation cwd (the checkout root) -- parsed with PyYAML `safe_load` and validated fail-closed against the `schema_version` handshake (additive-only; the full field list, plus a commented EXAMPLE `review`/`merge` block a new host copies and edits, lives in the host-contract doc, authored in Phase 6). Defaulting is fail-closed: a key with a shipped default takes that default only when ABSENT; an explicit `null` is refused with a precise error naming the key, never parsed into a `None` a typed field forbids. Top-level keys:

  ```yaml
  schema_version: 1
  state_dir: <path>                 # journal, box queue, quarantine ledgers, heartbeat
  worktree_root: <path>             # ticket worktrees (section 10); default <state_dir>/worktrees
                                    # (journal segment roll thresholds are engine constants, section 6)
  providers:                        # section 6
    - name: <str>
      kind: api | cli               # api is REFUSED at load until its client ships (section 6)
      auth: <ENV_VAR_NAME>          # env-var NAME, never a literal secret; OMIT for a cli
                                    #   provider using ambient CLI login (a flat subscription)
      models_by_tier: {low: <model>, medium: <model>, high: <model>, max: <model>}
      limits: {concurrency: <int>,  # rpm/tpm buckets defer with the api client (section 18);
               est_cost_per_call_usd: <usd or unset>,  # required iff cli with no usage in stream
                                    #   (section 6; spill wait is an engine constant)
               quota_window_minutes: <int>}  # cooldown Timer length on quota_exhausted
                                    #   (section 6; shipped default 60 -- a cli provider has no retry-after)
  routing:                          # (agent_tier, llm_surface) -> ordered candidates
    - {tier: <str>, surface: <str>, candidates: [{provider: <str>, model: <str>}]}
  routing_default_tier: medium      # tier for calls no ticket owns (triage, retro; section 6)
  review:                           # section 7
    mechanical:
      - {code: <str>, argv: [<str>], trigger: always | [<path-prefix>], severity: hard | soft}
    surfaces:
      - {name: <str>, trigger: always | [<path-prefix>], rules_doc: <path>, severity: hard | soft}
    trigger_map: {<path-prefix>: [<gate-code>]}
      # always-run vs diff-triggered for ENGINE-shipped gate codes only
      # (section 7); mechanical/surfaces entries use their own trigger
    gate_severity:                  # section 5 invariant 3; engine-shipped codes, MERGE context
      <gate-code>: hard | soft
      # shipped default: every v1 hard-set code is hard at merge; author-context
      # severity is an engine constant (soft) until a consumer exists (D10)
  merge:                            # section 9
    safety_checks: [<code>]         # host-designated fast checks in the MERGE-SAFETY tier
    strategies:                     # rung-1 per-path conflict resolution
      - {paths: [<path-prefix>], strategy: regenerate, argv: [<str>]}
      - {paths: [<path-prefix>], strategy: union}
      # (a low_risk_paths re-review skip list defers with micro-rework, section 18)
  scheduler:                        # sections 2 (D2) and 9 -- single-flight dispatch;
    max_unmerged: 2                 # dispatch backpressure: pause new admissions at this many
                                    #   completed-but-unmerged branches
                                    # (a workers key returns with the worker pool, section 18;
                                    #   serialize_paths defers with the overlap checkpoints)
  # (spend ceilings defer with the api client, section 18; cost stamping needs no key)
  caps: {diagnosis: 6, retry: 6, premise_bounce: 2, infra: 6, quarantine: 5, poison: 2}
  seeding: {max_seeds_per_admission: 3}  # section 19 bounded-batch seeding contract
                                    #   (the successor seeder is included in the count)
  circuit_breaker: {k: 3, cooldown_minutes: 10}
  drain:                            # section 18 -- the self-build drain's unattended safety envelope (the daemon has its own THRESH bounds, section 6); replaces the per-phase `confirm` (section 19)
    max_runtime_hours: 12           # overall drain wall-clock ceiling: a runaway backstop, NOT a phase gate -- on trip, halt at a safe checkpoint naming the continuing `chupa drain`
    max_ticket_minutes: 90          # hard ceiling the drain refuses to DISPATCH past: a ticket whose authored `Time budget` stuck exceeds it parks with a paved road, never runs
  engine_plane_safety_inventory: [<path-prefix>]  # section 12
  box_policy:                       # section 12 policy table, one key per ROW:
    # failure_report | retro_finding | override_report | suggestion |
    # bug_report_self_diagnosed | bug_report_player_repro |
    # bug_report_player_no_repro
    # absent key/row: the section 12 table value is the shipped default
    #   (explicit null refused, per the defaulting rule above)
    <policy-row>: draft | confirmed
  notify: <argv or unset>           # section 13 escalations
  report_inbox: <path or unset>     # section 12 host bug intake
  context_files: [<path>]           # host-plane content rendered as data (section 8)
  ```
- **No host-layout hardcoding.** Every path the engine touches comes from the host config. A check that assumes a host's directory layout is a portability bug.

### 15.3 Test-harness ladder

- **Test-harness ladder replaces wall-clock soaks:** (1) invariant auditor over the journal, run continuously against live runs -- a closed set of named invariants folded over the record, each carrying the law it enforces: exactly one terminal transition per run; every `cap_consumed` naming a declared cap; every `effect_intent` in a run that reached THE ok terminal `merged` carrying a matching `effect_completion` -- the pairing invariant fires at `merged` and NOWHERE else: EVERY non-ok terminal (timeout, abandoned, rejected, gate_failed, premise_failed, all of them) is exempt as closed-run history (section 11.2), and a run that reached no terminal is reconcile's orphan, not the auditor's finding; every `to: merged` transition carrying the commit it produced; every state name inside the closed run-state vocabulary (section 6); timestamps non-decreasing within a segment; (2) crash-point + fault injection on the state layer; (3) replay corpus -- every real incident becomes a permanent deterministic fixture, including journals written by older engine versions as the backward-compat check (journaled effects returning recorded results IS replay); (4) fake-agent simulation driving whole pipelines through the injected seams, pass condition = the invariant auditor; (5) shadow mode, deferred. Any phase exit that names a soak uses rung 4's fake-driven production composition with the injected clock advanced across the specified duration and recurring cycles; elapsed wall time is never the evidence. The shakeout battery (synthetic tickets with known outcomes: bad schema, scope escape, premise-false, unfixable lint, review-reject, merge conflict, orchestrator-crash) is the orchestrator's own permanent test suite.

### 15.4 Portability and fleet

- **Portability proof.** After BoardGameUI runs as host #1, a deliberately different-stack second host validates the host contract with contract fixes only, no project-local hacks. A NON-BLOCKING annex to the Phase 6 exit (section 19): v1 DONE does not gate on it, and it may run any time after host #1.
- **Fleet layer last.** A registry + merged status views only; holds no state and makes no decision a per-project instance could make. Deferred.

Rejected alternatives, recorded so they are not re-litigated: provider load balancing (round-robin or least-loaded candidate selection) -- routing stays an ORDERED candidate list, primary-until-pressure with deterministic spill (section 6), because balanced routing makes the serving model nondeterministic per attempt, muddying the GO-baseline identity (section 19), provenance, and failure attribution, for no throughput the spill rule does not already recover; porting or extracting an existing orchestrator codebase (this is a fresh implementation); and sprint mode (one long-lived feature branch per feature set with a heavyweight promotion gate), which trades per-ticket merge risk for concentrated integration risk at promotion -- the serial merge queue + cheap hard gates + post-rebase re-check delivers the same blast containment without a second-class branch discipline.

## 16. Threat model

chupa is a single-operator personal tool: it runs on a LAN box the operator owns, against the operator's own repositories, and does NOT sandbox executed work. Agent subprocesses, `## Verification` commands, mechanical checks, and evidence replay run with the operator's own privileges.

The failure modes are named so they are decisions: wrong or malicious model output (code, tickets, verdicts, verification commands); prompt injection riding data (countered by the section 8 rendering contract, which keeps untrusted content in the data channel, out of the instruction channel); and a bad dependency or repro pulled during a run. What bounds them is not an OS jail but the pipeline: the hard gate set, the correctness review, and the serial merge queue -- nothing reaches main without passing them (sections 7, 9), and mechanical enforcement is load-bearing, never prose. Two consequences of no-sandbox, named at their sharpest points: first, ticket-authored `## Verification` commands execute with operator privileges BEFORE any review exists -- the gate set bounds what MERGES, not what RUNS, and the section 8 rendering contract narrows the injection path into that execution without walling it; second, the intake front door (section 13) trusts a PATH -- any process with operator privileges, including an executing agent, can write a `source: human` ticket that auto-confirms, which is why every intake commit is journaled and itemized in status. `chupa kill <run>` SIGKILLs a run's process group; the kill-switch pause is the graceful path. Provider keys are injected only into the one call that needs them (section 6), and the redaction seam scrubs configured secret VALUES from every captured stream before it persists -- configured provider secrets only: any other credential on disk is exposed to executed work exactly as to any process the operator runs. OS containment is a D10 return if chupa is ever pointed at work the operator does not already trust.

## 17. Seed root agent files (CLAUDE.md / AGENTS.md)

The repo is seeded with a root CLAUDE.md written from this section by Phase 0 deliverable 1 -- the agents that build Phase 0 need standing conduct rules from the first session. AGENTS.md, the curated subset, is authored from this same section by whichever deliverable FIRST routes a non-Claude agent CLI to a writing surface: that CLI's child loads AGENTS.md and never CLAUDE.md, so the moment the config routes one, AGENTS.md is authored and both files are load-bearing -- a rule add/change/remove touches both in the same change. While every routed context is `claude -p`, CLAUDE.md alone is load-bearing and a second conduct file would be an unread copy to drift. The seed files are the v0 of the engine core template (section 8): when bootstrap rendering ships (section 15), this content becomes the first `chupa:core` block and hand-editing inside the managed block stops.

Format contract -- the context-efficiency rules the seed file obeys:

- Opens with a 3-5 line identity block (what chupa is, engine plane vs host plane) and ONE read-first pointer to this plan. The plan is never duplicated into CLAUDE.md: the root file carries only conduct an agent needs in-context every session, and links here for design detail.
- Two rule kinds, maintained differently. Behavioral rules -- ones no gate can check -- keep full but terse text; the prose is the only enforcement. Gate-backed rules compress to one line: rule + author-time actionable + gate code + link. At seed time every rule is behavioral (no gates exist yet); when a rule gains its gate (Phases 0-2), compress it in the same change that lands the gate.
- Hard size budget: target <= 120 lines. A rule earns a line only if violating it is cheap to do and expensive to unwind.
- Every rule carries a one-line why plus its source: a section of this plan at seed time, a cited incident once D10 takes over.
- Regeneration stop check is ROW COVERAGE, not shape: every rule-set-A row and set-B session bullet is a required semantic assertion compared against the existing file; a row the plan changed that the file still contradicts fails the check, even when identity block, pointer, and line cap already pass.

Seed rule set A -- engine conduct, restated from this plan. The root file states only the conduct form; the linked section owns the design detail:

| Conduct rule | From |
|---|---|
| Pure Python: no shell scripts, no `shell=True`, no string-assembled commands; external binaries only via argv wrapper modules; the chupa venv only | D1 |
| Build the simplest thing that satisfies the ticket; no speculative features, gates, config knobs, or metadata -- every addition cites the incident that earned it | goal 1, D10 |
| No dual-path code: no compat shims, deprecation layers, or defensive parallel paths; rename in place, update every call site, recover by revert | section 2 |
| Fail closed: allowlists and closed vocabularies, never denylists; every prohibition and every gate finding ships a paved road | sections 2, 7 |
| A hold ships with its release: the Reject queue, a premise park, or a poison quarantine lands with or after its release path (same deliverable, or `depends`-after it), its paved road never names an unbuilt verb, and a hold whose only release is a ticket change never precedes the machinery that machine-produces ticket changes | sections 2, 11 |
| Files + journal are the source of truth; derived views are projections and never authoritative -- never hand-edit one or cite one as authority | D3 |
| Generated files are render targets, never write targets: README.md and bootstrap/conductor.py extract from this plan's appendix sentinel blocks, CLAUDE.md is authored from section 17 by Phase 0 deliverable 1 (AGENTS.md by the first deliverable that routes a non-Claude agent CLI) -- a change edits this plan and reruns the generator, never the rendered file | section 1 |
| The plan is the seed: a plan defect (gap, bug, wrong spec) is fixed in the plan, then regenerated from it -- rerun the owning deliverable, deleting and regenerating the affected tickets or code so the seed drives the artifact; a ticket or code file is hand-edited ONLY for a defect provably not the plan's OR under the blocking-defect fast path (a defect stopping the drain's forward progress: plan edited and committed FIRST, then the minimal congruent code fix by hand in the same session, regeneration ticket optional -- section 19), and never before the plan's status is determined | sections 1, 19 |
| All git through `git.py` (argv lists, dir-pinned); worktree cleanup via `worktree remove` + `prune`, never bare `rm -rf`; no `gh`, no PRs in the loop | section 10 |
| Second problems are filed (Suggestion Box), never folded into the current diff; a pre-existing failure is verified on the base commit, then filed | section 11 |
| Read before write: no command, claim, or test is written until the artifact that owns that fact has been read | section 13 |
| Ticket frontmatter carries only fields the scheduler, a gate, or the authoring/triage policy reads; execution ordering lives in `depends` and `priority`, never in prose | section 13 |
| Clock, process exec, filesystem, and notifications go through the injectable seams -- never called raw in engine code | section 15 |
| Executed work is fenced by gates and review, not jailed: v1 does not sandbox executed code; never rely on its goodwill, and never pass a provider key to a process that does not need it | section 16 |
| The journal is the record, never a debug log: diagnostics go to the engine log and attempt spools, and configured secret values are redacted from every captured stream at the write seam | section 6 |
| Do not start a phase until the previous phase's exit is met | section 19 |

Seed rule set B -- session conduct for interactive chat in this repo. Proven in host #1's rule file; stated in full so this document stays self-contained (a human-present chat session is the one context the pipeline machinery does not govern):

- **Terse communication.** Lead with the answer; cut hedging, filler, and preamble; short sentences and tight lists.
- **Comments explain why, not what.** Comment only invariants, hazards, and deliberate-looking-wrong choices; match surrounding density.
- **Plan prose is pure spec.** Rules stated tersely; no incident citations, session references, or change history in plan prose -- provenance lives in the Suggestion Box, the journal, and git history; the one exception is section 22, the plan's uncited rationale appendix.
- **Track open threads.** A reply that raises several questions or options owns that list until it is empty; restate unresolved threads every turn; the user engaging on one thread never closes the others.
- **Announce unsolicited dives.** Name any investigation or authoring the user did not request in 1-2 sentences and get a now / after / skip decision before spending the time; the requested task always runs first. (Autonomous pipeline stages are exempt -- they file same-turn via the Suggestion Box.)
- **Supervising session.** A chat session the user directs to run the conductor or drain and repair its stops is an operator under the section 19 recovery order and the same closed touchpoint list. It runs the conductor with `--auto` and the drain as a background process, acting only when the process exits. Recovery-order work at a stop is requested work, never an unsolicited dive. It stops for the user on: a plan edit changing a section 3 decision, a section 18 refusal, a section 20 open decision, or the 19.L bootstrap contract; an expired agent login; a Reject-queue keep or kill (it diagnoses and proposes; a ticket edit following a committed plan fix it applies itself); and a stem stopping again on a cause it already repaired (one repair per cause). Each recovery reports the plan commit, any hand-fix commit, the filed cause ticket, and the continuing command.
- **Instance first, cause captured.** A reported problem yields the minimal unblock first and a separately filed cause ticket in the same session -- the chat form of the section 14 urgency/importance rule.
- **Git session safety.** Respect the single-writer lockfile: a chat session never mutates git state in a checkout whose lock a daemon holds (authoring ticket FILES in the working tree is the sanctioned intake path, section 13, and needs no git). Stage and commit only files authored this session, by explicit path; never a tree-wide destructive verb (`clean`, `reset --hard`, `checkout -- .`) in a shared checkout. Never push or remote-mutate from a chat session unless the user explicitly says push -- pushes are the checkpoint Effect's job (section 10).

AGENTS.md is a curated subset, never a mirror: only load-bearing, expensive-to-violate rules cross over; CLAUDE.md is canonical on conflict; once AGENTS.md exists, a rule add/change/remove touches both files in the same change. Once bootstrap rendering ships, both render from the same engine template and the manual sync duty dissolves into the render step.

Excluded on purpose, for self-consistency with the anti-bloat law and the section 18 refusals: host-plane and product rules from any host repo; metadata taxonomies and their lints; batch/wave scheduling rules; provider or model pins; and any restatement of design this plan already owns.

## 18. Explicitly not building (v1 refusals)

### 18.1 Refusals

Named so they are decisions, not omissions. Each may return only via D10 (a real incident):

- Deterministic re-execution recovery; journal hash-chaining; blob store.
- Composition/plugin engine over the block catalog.
- GitHub PRs, `gh`, PR-state machinery in the loop.
- Author-time conflict-prediction machinery (path-bucket tables) and wave/group batch scheduling; multiple ticket authoring modes.
- Metadata taxonomies and their lints (code annotations, test marks, doc tags, glossary currency), producer-health manifests, semantic history search.
- A shipped generic-check catalog. The engine ships ZERO code checks -- no ruff/eslint/complexity presets, no enable-flags: generic linters are one-line host `review.mechanical` entries (section 7), and the host-contract doc's commented example config (Phase 6, section 15) is where the typical rows live -- documentation to copy, never an engine surface, so the check-runner contract stays the only seam and the engine never accretes per-tool knowledge.
- A sprawling CLI. The CLI stays small (stdlib `argparse`, no click/typer): status, new, confirm, reject, kill, pause, resume, retro, triage, migrate-config, doctor, core (the Phase 6 `chupa:core` bootstrap render + drift lint, sections 8, 15 -- the operator and new-host invocation of the ONE renderer whose post-upgrade refresh the daemon commits mechanically per section 10, one renderer with two invokers, never a second render path; listed here so the section 19 deliverable and this closed vocabulary agree), `serve` -- plus `run <stem>` and `drain`, the self-build's scaffold verbs (drive one ticket, or the whole ready queue, through the pipeline synchronously). `drain` carries the entire self-hosted build to quiescence (Phases 2-6, section 19); it retires when the operator CUTS OVER to the continuous daemon on host work, not at Phase 3 -- the daemon is built and soak-proven WITHIN the self-build, then takes execution over at the operator's explicit promotion: `chupa serve` STARTS that continuous daemon (section 19, Phase 3) on host work -- the long-running foreground process that holds the single-writer lock, emits the heartbeat, and is governed by `kill`/`pause`/`resume`; unlike `drain` it does not stop at quiescence but runs until stopped. `serve` is a DAEMON-ERA verb: the self-build never invokes it ON HOST WORK (the scaffold `drain` carries Phases 2-6; the two exceptions are the Phase 3 soak's in-process synthetic-checkout `serve` composition and the Phase 6 exit harness's bounded synthetic-checkout `serve` subprocess, section 19); the one operator-launched pre-cutover `serve` is touchpoint 7's supervised 24-48h soak, run before GO is recorded, so the first UNSUPERVISED `chupa serve` on host work is the cutover itself, launched only after GO is recorded (section 13 touchpoint 7).
  - `drain` runs every eligible ticket in `depends`-constrained (priority, age) order, one at a time in the single writer process, to QUIESCENCE: a non-ok TICKET terminal PARKS that stem and the drain continues with the next eligible ticket; a merge landed mid-invocation satisfies `depends` edges in the same invocation. Quiescence is TRUE quiescence: after every merge the drain RE-SCANS the committed tickets dir -- shipped WITH the Phase 1 drain verb, needing nothing Phase 1 lacks -- so a ticket authored or confirmed mid-invocation (a seeding ticket's ticket-plane output) becomes eligible in the SAME invocation -- the seed-to-seed continuity the self-build needs (section 19). The bootstrap drain NEVER scans the box: the Suggestion Box is consumed only by the operator's `chupa triage` verb (section 12), and the daemon's continuous box consumer is a Phase 3+ era, not this drain. At quiescence -- nothing eligible and unparked -- each parked stem whose `retry` cap (section 11.1) still holds budget is RE-OFFERED -- in the same `depends`-constrained (priority, age) order as dispatch -- one retry unit drawn per re-offer, so eligible work always runs ahead of re-offers and a red stem never starves the queue; a re-offer renders FINDINGS-FED (section 11.2 -- the re-entry ships with this verb, as the section 0 prompt 11-12 pair), and quiescence is re-evaluated after every re-offer merge, so an unblocked dependent runs in the same invocation; the drain ends when nothing is eligible, unparked, re-offerable, or newly authored, reporting every still-parked red with its findings -- the stop names its continuing command (section 19), never a silent tail. Two config-declared bounds hold an unattended drain in place of an operator's finger (section 15). The overall wall-clock ceiling (`drain.max_runtime_hours`) stops it short of quiescence: on trip the drain admits no new ticket, lets the in-flight one reach its stage terminal, journals the halt, reports progress, and names the continuing `chupa drain` (which reconciles on-entry and resumes) -- a runaway backstop the operator sizes above a normal build, never a routine phase gate, and a re-run after it resumes a bounded safety stop, never the banned release for machine-retryable work (section 19). The per-ticket ceiling (`drain.max_ticket_minutes`) is checked at DISPATCH: a ticket whose authored `Time budget` stuck exceeds it PARKS with a paved road (lower the budget) rather than dispatching, so no single ticket claims an unbounded run before the Phase 4 watchdog enforces the authored threshold. The report also lists any draft tickets awaiting `confirm` (section 12) -- box-triage-authored drafts can exist mid-build; the SEEDS themselves are never draft (authored `confirmed`, section 19). Engine-plane refusals (lock contention, journal corruption, config/setup refusals) still STOP the drain; park is for ticket outcomes only. Exit codes are ONE three-value contract for both scaffold verbs: 0 = quiescence reached (parked reds included -- the report names them and their continuing command); 1 = a non-quiescent stop (`run <stem>`'s ticket at a non-ok terminal, or a drain halted by `max_runtime_hours`); 2 = an engine-plane refusal -- wrappers and the conductor key on the class, never the message text.
  - An admission whose diff touches `chupa/**` or `specs/**` is a SELF-UPGRADE: before the next dispatch the drain re-execs itself through the process-exec seam (section 15) as `uv run python -m chupa drain` -- ONE form, dependency changes included (uv's sync is a no-op when nothing changed); this is D1's one named runtime `uv` exception. It carries the invocation's parked set in argv -- one repeated `--parked <stem>` flag per stem -- so no stage runs stale in-process code against the upgraded checkout. The re-exec is a HANDOFF with a fixed order: the parent journals the handoff, closes its journal handles, RELEASES the single-writer lockfile, then spawns the child through the seam with `timeout=None` and inherited stdio (section 15), awaits it, and exits with the child's exit code -- doing nothing else after the spawn, so the child (which reconciles on-entry and takes the now-free lock like any drain) is the only writer. Each self-upgrading admission nests exactly one such awaiting parent; the chain is bounded by the invocation's self-upgrading admissions and every process in it is idle except the leaf.
  - Both scaffold verbs reconcile ON-ENTRY: on taking the sole writer lock they first reap any orphaned in-flight run an interrupted predecessor left (section 11), so an interrupted `run`/`drain` self-heals on the next invocation. A stem whose last run ended non-ok -- reaped (`abandoned`) or a completed non-ok terminal -- stays ELIGIBLE: keys are run-scoped (section 6), so the re-run takes a fresh keyspace and is real work, never a replay, and its re-entry prompt carries the prior findings (section 11.2). A red stem costs a drain at most its remaining `retry` cap, drawn one unit per re-offer from the one retry budget every retry sense shares (section 11.1); the operator escape begins only where that cap ends. Exception: a stem whose last terminal was `premise_failed` stays parked across invocations until its ticket-plane `ticket.md` commit changes -- the verdict answered the ticket as written, so re-asking it unchanged replays a judgment, not work (section 2's pointless-call rule). That park's paved road is `source`-keyed (section 13): a `source: seed` stem renders the plan, so its false premise is a PLAN defect -- the road names fixing the false assumption in CHUPA_PLAN.md first (section 1), the releasing `ticket.md` change then being the plan-congruent regeneration -- the section 19 recovery-edit path (an in-place correction of the unrun seed after the plan commit), never a code-first edit that precedes the plan's status determination; a `source: human | box:<class>` stem's road names the direct `ticket.md` edit (a box stem's plan-level cause files separately, section 12). The mechanical release is the one rule both share -- the stem's committed `ticket.md` content changes -- so the road differs only in where the fix originates, never in what unparks the stem.
  - `new` templates a ticket file (the intake front door, section 13); `serve` starts the continuous daemon loop on host work (the daemon era, `19.P3`) -- the sole writer for its lifetime, reconciling on-entry like the scaffold verbs, running until `kill` or a signal stops it; `kill` hard-stops a run (section 16); `migrate-config` performs the explicit older-config migration (section 15); `doctor` is a mechanical self-check (venv, git on PATH, config schema, lock, journal readability). `resume` is the pull-side remediation for every push escalation (section 13): un-pause dispatch after a `budget_exceeded` pause (with the ceiling raised or the window rolled past, else the next pre-call check re-pauses), release a quarantined test or ticket, lift a storm-breaker hold (section 12, bound to its trip identity), and re-open merge admissions after an integration-red streak -- no escalated state is a dead end.
  - Invocation: the CLI is a MODULE entry (`chupa/__main__.py`), run during dev and the whole bootstrap as `uv run python -m chupa <verb>` -- the same venv convention as `uv run pytest`. The project stays a VIRTUAL uv project (`package = false`, no build backend) per goal 1 and D10: a packaged `chupa` console script is not built until the release path needs one (section 13 touchpoint 6), at which point a stable release puts bare `chupa` on `$PATH` (`~/bin/chupa`, section 15). Bare `chupa` is never assumed on `$PATH` during the build.
- The AI audit trail layer (trajectories, reward vectors, preference pairs, training exports, attestations) and its frontmatter/table surfaces. Planned to return as projections over the journal (section 6) -- the kernel already captures the raw material (model, spec version, SHA, cost per effect), so nothing is lost by deferring.
- Formal canary/shadow rollout for prompt-spec changes (provenance measurement first).
- Multi-daemon / multi-machine execution and general leases.
- A feature-flag subsystem. Engine behavior knobs are explicit config keys; rollout risk is handled by the stable/dev instance split and tagged releases (a flag framework recreates the dual-path shape section 2 bans, and every flag doubles the shakeout battery's state space). Host-product feature flags are host-plane content: implemented in host code/config by ordinary ticket diffs, never set from ticket frontmatter, with flag-hygiene gates a host may add per D10.
- A web UI.

### 18.2 Deferred behind a named trigger

Deferred behind a NAMED trigger -- D10 returns, distinct from the refusals above and listed so deferred scope cannot silently re-accrete; each returns only when its trigger fires, citing it:

- The `api` provider client, its token buckets (rpm/tpm), and the cumulative USD spend ceiling -> the first configured `kind: api` provider; until they ship together, `kind: api` is refused at config load (section 6).
- The concurrent worker pool -- and with it the dispatch-time overlap skip, the pre-review hold, a `workers` config key, and dispatch serialization by path -> measured queue starvation or measured contention on host work, post-cutover (D2, section 9).
- A rerere replay cache with its custody protocol, conflict-only micro-rework, and a `low_risk_paths` re-review skip list -> the first chronically re-resolved conflict shown by the journaled conflict facts (section 9).
- Spiral-signal shapes beyond spend-without-progress (debris accumulation, command repetition, mutation-entropy stall, poll-loop match) and the degraded-watch mode -> a pinned spiral fixture the shipped signal misses / a configured stream-less CLI (section 9).
- Dedup-health proxy metrics, conflict-hotspot trending, and the scheduled-vs-silted rate -> a post-host-#1 incident each (section 14).
- The triage-dedup real-model eval -> daemon-era entry, beside the GO-grade baseline (section 19).
- A mechanical scope-fence closure analyzer -> the first fence-gap escape `requisition_review` misses (section 9).
- An analytics engine over the journal (DuckDB) -> the first projection measured too slow as a stdlib fold (D3).
- The per-context (author/merge) gate-severity map -> the first gate needing different severities in the two contexts (section 5).
- A PRNG seam -> its first consumer (section 15).

## 19. Implementation phases

Section 19 is split into separately citable units (section 13 `Plan contract` grammar): `19.L` holds the seeding, exit, and operator laws; `19.I` holds the laws every implementing ticket applies; `19.P0`-`19.P6` hold one phase each -- deliverables, settled contracts, exit reads, and, for the self-hosted Phases 3-6, the phase's SEED REGISTRY; and each registry row's ENTRY UNIT `19.P<n>.<stem>` holds that row's full contract. A `source: seed` ticket cites exactly the units section 13 names for its role; it never cites whole section 19, nor sections 0, 21, or 22. Why each law exists lives in section 22, which nothing cites.

### 19.L Build laws

**Phase gating.** Do not start a phase until the previous phase's exit is met, and met is READ, never claimed: a criterion that lives in the journal or git is verified by reading that artifact (D3). Ordering is mechanical: every phase's seeds `depend` on the prior phase's exit ticket, so they cannot dispatch until it merges -- an edge read from git, never an operator's per-phase judgment. One exception: the Phase 1 review-baseline eval runs FIRST within Phase 1, before the walking skeleton; its harness and fixtures are the base the Phase 6 GO-grade baseline grows, nothing thrown away.

**Bootstrap contract.** The self-hosted build runs to done -- the Phase 6 exit receipt exists green -- or to a plain-English stop naming the one command that continues it, never a per-phase re-run; a drain that goes quiescent with a phase's exit reads unperformed has stalled, not finished, and its quiescence report names the parked exit stem and the unmet read. Phases 0-1 run on `bootstrap/conductor.py`; from the Phase 1 handoff ONE continuous `chupa drain` (section 18) carries Phases 2-6, each phase's final ticket seeding the next into the same running drain, whose after-every-merge tickets-dir re-scan makes those seeds eligible in the same invocation. Each launch carries a durable `bootstrap_attempt_id` stamped into `bootstrap/state.json` (the section 21 conductor owns it) and is bounded by the wall-clock ceiling, `MAX_ATTEMPT_CALLS` (section 21), and -- once real-model calls flow through cost events (section 6) -- the spend ceilings those events feed, read as `max_attempt_cost_usd`. The attempt's record is that state file plus the journal entries carrying its id; the legitimate second attempt after repair is the next no-flag invocation, validated against that record.
- Pre-daemon operator touchpoints are a CLOSED list: start a run; scan the Suggestion Box at will (`chupa triage`); answer a Reject item whose retry budget is spent; edit a premise-failed ticket or fix the plan and rerun; re-authenticate an expired agent login. A run that stops for anything else is a P0 defect the run files to the box. At a stop, an outer context's ONLY writes are those touchpoints, in the recovery order below; any other ticket edit, `confirm`, journal write, or motion of main from outside the engine's own lanes is a P0 defect -- the conductor's builder contexts included (a builder never commits to main past its reviewer, and no deliverable context re-enters the conductor).
- GOOD-ENOUGH BAR: bootstrap review -- the conductor's second-context review of a deliverable and, once chupa self-hosts, the pipeline's review of a ticket -- fails work ONLY for state corruption, deadlock or permanent stall, secret exposure, or false-green verification; every other finding is filed to the box (pre-Phase-2, `bootstrap/suggestions.md`) and the work settles.
- ERA SPLIT: bootstrap behavior is tuned for unattended forward progress through Phase 6; no supervision surface (the GO gate, draft gates, supervised merge, section 12) gates the self-build, and every seed is authored `confirmed`. Supervision engages at the operator's explicit cutover to host work, when GO is first RECORDED -- not because the daemon's code was built. The unattended drain's bound is the SAFETY ENVELOPE -- `drain.max_ticket_minutes` and `drain.max_runtime_hours` with section 18's trip behavior -- a runaway backstop, never a phase gate. The bootstrap drain never holds an admission; recovery is git revert.

**Operator recovery order** (a stopped drain). (1) Read the stopped stem's artifacts -- `diagnosis.json`, `review.md`, `attempts/<n>/`, the engine log, the journal -- for the REAL cause, never the status label (a "no schema-valid verdict" park is usually a spent diagnosis cap). (2) DETERMINE the plan's status before editing anything. A plan defect (a gap, contradiction, orphaned behavior, or a value that should be an input) is fixed in the plan and COMMITTED first, then regenerated from: a merged stem cannot re-run (the drain folds it out), so ship a NEW corrective seed; an unrun seed is edited in place and left UNCOMMITTED for the next drain's intake -- its new SHA releases the park and only the park, because caps are LINEAGE-scoped and no edit resets them (section 11.2; the one re-arm is the operator's Reject-queue `keep`, section 13). A defect provably NOT the plan's -- a fence missing a criteria-forced file (grep every reference before a rename-fence), a sound spec the model could not implement -- is a ticket or code fix, never before the plan's status is determined. BLOCKING-DEFECT FAST PATH: a defect stopping the drain's forward progress (an engine bug no ticket routes around, a seam fault below the failure spine) is repaired by committing the plan FIRST, then hand-applying the minimal congruent code fix with its test in the same session, filing a regeneration ticket only if the hand fix is narrower than the plan change. A code-first patch is the violation; a plan-only edit that strands the working fix unapplied is the opposite violation. Never lead with a ticket edit, `confirm`, or `drain`.

**Drain conduct.** No drain is findings-blind: the reject-findings re-entry ships WITH the Phase 1 drain verb (section 11.2). A parked stem with remaining `retry` budget is re-offered findings-fed in the SAME invocation, quiescence is re-evaluated after every re-offer merge, and requeue-on-unblock is tested drain behavior (section 18), never an operator duty. The self-upgrade re-exec -- `uv run python -m chupa drain` through the process-exec seam, D1's one runtime exception -- is automatic, never a stop. A seeded queue never relies on its own recovery machinery: a `depends` edge INTO a recovery-machinery ticket must never block the operator escape (a non-ok stem stays eligible and re-runs on fresh run-scoped keys, sections 6, 11, 18), and a recovery-machinery ticket is sized to pass the active gates with the standing render alone, split before seeding when it cannot.

**Seed buildability -- proven where authored, never discovered where run.** The Requisition gate is GRAMMAR only; every machine-authored ticket, seed and box alike, is judged by `requisition_review` (section 7) before it commits `confirmed`. The bootstrap floor: Phase 2's conductor-authored seeds and `requisition_review`'s own deliverables pass grammar only and fall to the run-time premise park (section 18); from the Phase 2 exit ticket on, every seed is reviewed before it commits. The review reads the engine and tests the ticket names and judges: the fence covers every file the criteria force (section 9's authoring law); no invariant or criterion contradicts merged behavior; the criteria are mutually satisfiable; every invariant the deliverable states or cites has a NAMED test obligation (a stated rule with no named test is a gap -- a green suite that never exercises it is false-green); and RENDER FEASIBILITY -- the authored base Implement render (standing inputs, zero attempt history) measured against the bound times the authoring headroom (section 8). An over-bound render is a `snag` (shrink or split at authoring). A `snag` re-authors within caps; an `rma` -- a genuine plan defect the author cannot fix -- parks for a human. A machine-authored seed's closure is ALSO pinned by mechanical assertions in the seeding ticket's own test file, beside (never replacing) the review -- the seed's own tests, not an engine-shipped analyzer, and the already-earned D10 return of section 9's mechanical closure check:
1. CONTEXT CLOSURE: every fenced EXISTING path is embedded `## Context` or listed in `## On-demand` (section 13); paths the seed creates are in neither. A path is on-demand only when embedding it breaches headroom, and the test records its authoring-time size.
2. CONTRADICTED TESTS: every existing test whose assertions the criteria's behavior flip contradicts is fenced -- at authoring, grep the flipped symbol and the old recorded value across `tests/`. A fence wall on a criteria-forced path is this authoring defect; the correct implement outcome is `premise_failed` (section 9), drawing the premise bounce back through Author (section 11.1).
3. ACTIVATION: an activation seed fences each predecessor construction ticket's dormancy-pinning test files.
4. OWNERS: a deliverable introducing a not-yet-built module states its owner in the seed's prose, sourced from its entry unit; an entry unit silent on an owner is a `spec_gap` (SPEC DEPTH), never an owner invented inline.
5. CALLER CLOSURE: a seed that changes a public signature, constructor arity, or composition-root wiring fences every direct caller an authoring-time grep finds across `chupa/`, `eval/`, and `tests/` (`eval/` harnesses and benches are composition roots); a seed adding a public operation to a module whose public surface an allowlist test pins fences that test; a seed superseding an earlier phase's behavior fences the test that pins the old behavior.
An existing test the seed must keep green but never edits is a PRESERVATION suite: run unchanged in `## Verification`, neither fenced nor Context.

**Seeding chain.** Each phase's FINAL deliverable (its exit ticket) seeds the NEXT phase CORE-FIRST from that phase's registry -- the YAML block in its `19.P<n>` unit, the ONE source every seeding ticket reads and never edits, parsed straight from this plan; it is never copied into a repo file. It authors the registry's `core` admission plus one `<phase>-continue` seeding ticket. Each continuation authors the registry's next admission -- at most `seeding.max_seeds_per_admission` `source: seed` files INCLUDING its successor seeder (config-declared beside `caps:`, section 15; shipped 3) -- plus the next numbered continuation (`<phase>-continue-02`, ...), until the terminal admission carries the phase-exit seed as its SOLE payload with no successor. Each continuation owns only `tickets` plus its own new `tests/test_seeded_phase<n>_<nn>.py`, depends on every payload of the admission before it, and embeds one merged earlier seeding test as its idiom, never the test created in its own admission. Rules:
- GRAIN LAW, both directions: a registry row is ONE ticket owning ONE independently provable contract -- never a multi-boundary bundle, never one deliverable split into a chain of sub-component tickets a single context could own.
- A KNOWN-DEEP row (its contract crosses module seams) rides its admission ALONE and starts `high/high`. The phase-exit seed is plan-named KNOWN-HARD and starts `agent_tier: high, agent_effort: high` (this sentence is its citing evidence). Every other row starts `medium/medium`, except under the pre-ladder tier rule below.
- A batch's seeds depend only on merged work, already-seeded batches, and within-batch stems; a forward dependency on a later batch is refused. Within an admission, list order implies nothing: a seed consuming a sibling's output declares `depends` on it (the registry's `depends`). The chain is finite: each link names its position and carries the shrinking unseeded suffix.
- `requisition_review` at a seeding Check renders ONE target per pass -- each seed against its own text and Context plus committed plan and code, never the accumulated batch -- plus that seed's PRIOR REVIEW: its latest `requisition_verdict` signal in the seeding ticket's lineage (every seed review journals one, carrying `verdict`, `ticket_sha`, and a snag's `findings`) and the diff from the bytes it judged. The review rules each prior finding cleared or standing and raises a new finding only against changed text. An `approve` holds while the seed's bytes match its `ticket_sha`: Check does not re-review it, and a retry keeps it verbatim and re-authors only the snagged seeds.
- A row's fence is a FLOOR: the seeding ticket adds only paths mechanical rules 2-5 find and records each addition in its test. Any other widening, and any renaming, reordering, adding, splitting, or omitting of rows, is a plan edit under the recovery order, never seeding-time invention. A seed realizes exactly the machinery its row states (D10).
- CONTEXT PARTITION: embedded Context is the default; an existing path whose embedding breaches headroom moves to `## On-demand`. A path a sibling seed creates in the SAME admission is never Context; a seed authored after that sibling merges may embed it. Prompt-spec sources and any file carrying the engine data-block delimiter are never Context (section 13).
- SPEC DEPTH: each registry row's full contract lives in its ENTRY UNIT `### 19.P<n>.<stem>` after its phase unit; the registry row stays the one-line index. An entry unit carries, as labeled bullets: **Owner** (each new module), **Records** (every record, signal, body key, frontmatter value, and constant it reads or writes, with exact shape, edge behavior, and its one writer), **Observable** (dormancy or behavioral), and **Tests** (each invariant's named test). A missing or incomplete entry unit is a `spec_gap` the seed path detects mechanically before any review call, and a fact a seed needs that its unit omits is a `spec_gap` its review finds; either hardens the unit through section 11.4, never seeding-time invention. Never seed past the NEXT phase (D10).
- Seeds are written DIRECTLY by the seeding ticket's Implement stage as `confirmed` ticket-plane output, intake-lint validated AND `requisition_review`-checked at its own Check stage -- never through the Suggestion Box, which carries filed problems, never a known build-plan ticket. Seed emission is an ordinary re-runnable Implement pass, never a hook registered to fire after its own merge. DELIVERY: seeds reach main only through the ticket-plane lane (section 10), never the seeding ticket's code branch (that fails MERGE-SAFETY). RE-RUN: a re-run treats the stem's OWN previously lifted seeds (journal-identified) as already emitted, never a collision; foreign stems stay protected. REJECTION: a materialized seed later terminally `reject`ed (section 13) leaves its obligation to a fresh same-goal seed authored by the same pass; section 9's dead-dependency handling surfaces every dependent for re-wiring, the exit's edge included, and the exit read accepts `state: rejected` plus the successor's `to: merged`.
- SEEDING TESTS pin identity and structure over AUTHORING-TIME snapshots (section 0 prompt 17's pin-grain law): stems, edges, frontmatter, fence, Context/on-demand partition, recorded sizes, and the max-effort render computed from sizes and plan-unit lengths recorded IN the test. They never re-read the live tree, live file sizes, or the live plan; once their seeds merge they are immutable historical fixtures that no later ticket fences or migrates.

**Exit tickets.** The exit ticket carries three obligations -- the exit READ, committing any phase report, and authoring the next phase's core -- and splits into a `depends`-chained pair (READ + report, then seeding) whenever one alone strains its context. Every prior-phase stem is a TRANSITIVE `depends`, so its dispatch IS the merged-presence proof (git-read, the squash trailers of section 10); any authored entry-read is at most that bare check, never a `checks.json`/approval provenance cross-check and never a git verb `git.py` does not ship. Every OTHER criterion reads a COMMITTED artifact or a WIRED-AND-SHAPED proof against merged code -- never the live journal (the exit runs on a clean checkout without the gitignored state dir) and never a live occurrence of a misbehavior-conditional emitter (a healthy drain never flakes, storms, or fails a push). Where evidence IS runtime history, the read is over a journal WINDOW the driver materializes into the worktree, declared in the closed-grammar `Exit-read window` section (section 13), keyed to the declaration, never a stem name. Each read names the emitter's REAL durable record by its own constant -- never an invented signal, never a symbol-presence grep, never a journal or report the exit test itself writes. "Read from the journal" in an exit-read list names the emitter's record surface, never the exit ticket's read surface. An unmet criterion returns `premise_failed` naming it. An exit read realized as a merged TEST runs at Check and on merged main, where only committed artifacts and merged code exist; the conductor-performed Phase 0-1 gates run with the live state dir and may read it directly. The exit ticket's acceptance criteria NAME the transitive-dependency coverage and each read, never a `pytest` run blind to them. When seeding is staged, the exit seed lands LAST with its predecessor chain already committed, so `requisition_review` verifies coverage against committed tickets.
- EXIT-READ CLOSURE: every criterion NAMES its emitter deliverable; `requisition_review` rejects an exit read with no emitter among the phase's deliverables. A COMMITTED-REPORT read names two roles: MACHINERY -- the closed schema in `chupa/artifacts.py`, its registration among the lane writer's KNOWN artifacts in `chupa/stages.py`, its canonical writer, AND a runner that constructs the report from member-local production evidence -- and PRODUCER, a run strictly after the machinery merges (a dedicated no-code run-lane seed, later deliverable runs, or the exit's own harness run). One deliverable is never both registrar and committer, and a deliverable never lifts its own report. Each report registers under its OWN name. A report committed by the lock-holding drain through the ticket-plane Git/Effects seam (the retro report, `19.P5`) takes no KNOWN registration: its machinery is the deliverable that wires that commit and its producer the run that commits it.
- RUN-LANE ADMISSION: a no-code producer's deliverable is its schema-validated report in its worktree OUTBOX. Its admission accepts an empty committed diff exactly when the lift names a registered KNOWN artifact under that stem's OUTBOX besides `run.md` -- never unknown output, uncommitted code, or committed `tickets/**` (section 10); merge journals `to: merged` with `commit: null` and retires once.
- CUSTODY: every exit-read artifact or receipt is MACHINE-PRODUCED by its emitting run and reaches main only through the engine's lanes -- no hand-committed copy or out-of-lane refresh, ever; touching one from outside is a P0 defect. A fault-injection report records a member green only from that member's own evidence AND an invariant-auditor-green member journal.
- ENVELOPE: an exit gate is satisfiable inside the safety envelope -- soaks spend injected-clock time, never wall time; live host reads and the real 24-48h soak are operator post-cutover acceptance (section 13 touchpoint 7), never drain-executable criteria.
- TERMINAL: `phase6-exit` authors no seeds; it performs the exit reads and commits `tickets/phase6-exit/exit-receipt.json` (closed schema, `19.P6`) through the OUTBOX lift, regenerable byte-identical from the artifacts it cites.

**Pre-ladder tier rule.** Until the escalation ladder (section 11) merges, the conductor and every code-bearing seed run at the HIGH tier; a plan-named known-hard seed carries `high/high` at START with its citing evidence recorded in the seed and pinned by its seeding test.

### 19.I Implementation laws

**Staged construction -> activation (phase-generic).** Work that flips production behavior lands as a dormant-until-activated chain with a stated evidence contract per stage:
- CONSTRUCTION builds components unreachable from production, proven by a discriminating dormancy observable -- the transitive `chupa.*` import closure rooted at `chupa/__main__.py`, recognizing both `import chupa.x` and `from chupa import x`, which must FAIL once the component becomes reachable (a byte-snapshot or a one-idiom scan is false-green). A construction landing inside an already-reachable module instead states a BEHAVIORAL observable in its row -- no production caller of the new seam, proven by a test over the production composition graph. Its evidence grade is explicitly sub-production: section 9's production-exercise rule is met by exercising the dormant component directly.
- ACTIVATION flips callers under a TRANSITION FENCE: fence, Context, and Verification name every predecessor dormant fixture and every predecessor NEGATIVE assertion the flip invalidates (verb absence, task count, `not hasattr` composition checks -- an absence assertion has no reference edge to the new symbol, so it is named explicitly and migrated in the same commit), plus every config and composition root the flip forces. Acceptance is proven through the REAL production composition: the first activation of a phase lands an in-process production-composition harness constructing the CLI/`serve` object graph without launching host work, and later activations reuse it. A test-only graph is never production evidence.
- A hold lands with or after its release surface (section 2), and a dedicated proof ticket demonstrates a merged ticket registers its successor end to end before anything depends on it.

### 19.P0 Phase 0 -- Kernel + contracts

- *Deliverables:* `journal.py` (segmented append-only JSONL under the host state dir, glob-ordered read, `read_segments()` as the one parser, write-ahead fsync, torn-tail tolerance; the roll TRIGGER ships in Phase 3); `effects.py`; the lockfile guard (release-then-reacquire proven -- the drain's self-upgrade handoff depends on it, section 18); `git.py`; the config loader (`config.yaml` parse, fail-closed validation, the `schema_version` refuse-newer check, the `kind: api` load refusal -- sections 6, 15); Artifact models, StageResult/Outcome (`already_satisfied` included, section 5), Gate protocol + runner + gate-lint (paved road required); the one LLM-stage driver (section 5 invariant 2: the schema-invalid re-prompt loop, the single-fence JSON unwrap, and the stuck-budget kill raced against the injected `Sleep` seam, section 15) with attempt-spool capture, the engine log, and the redaction seam (section 6); spec renderer + spec lint + the rendered-prompt size refusal (section 8) + the `Plan contract` resolver (section 13: section and unit ids resolved verbatim, deduplicated, the sole channel for plan bytes) + PLAN LINT (section 8); the LLM interface with scripted fake.
- *Emits:* the kernel test suite; the crash-point / fault-injection harness on the state layer (section 15).
- *Exit reads (each from the named emitter's artifact):* a toy echo stage -- consumes a stub artifact, emits one -- runs end to end under the driver with the fake LLM (emitter: the driver); kernel tests green, including a journal read back in order across multiple pre-seeded segments (emitter: `journal.py` + suite); plan lint green over this plan (emitter: `chupa/specs.py` + `tests/test_plan_lint.py`); the fault-injection harness proves torn-tail tolerance and effect once-semantics under induced crashes (emitter: the harness).

### 19.P1 Phase 1 -- Walking skeleton

- *Deliverables:* the provider layer -- registry + routing parse and the FIRST candidate only, with key-scoped injection, and BOTH `cli` adapters (`claude`, `codex`) over the shared base owning write-grant derivation, redaction, and the cost floor (section 6; section 0 prompt 1 is the contract). SINGLE-PROVIDER FALLBACK: with only one provider CLI available, route REVIEW to that provider's strongest tier, record the lost review-identity diversity as a standing open decision, and expect to need section 7's review-authority bounds sooner. The review-baseline NO-GO spike FIRST: a committed fixture set of 15-20 planted defects PLUS at least 3 clean (defect-free) fixtures under `eval/fixtures/`, scored by `eval/harness.py` for catch rate, known-bad false-approve, and clean false-snag; fixtures authored by a different (provider, model) -- at minimum a different tier -- from the one serving REVIEW, the fixture-author identity recorded in the baseline signal. The LLM call behind the `@effect` wrapper (section 6 key shapes, cost event, replay; of `limits` only `est_cost_per_call_usd` parses here). Implement -> Check -> Review -> Merge on ONE real hand-authored ticket, single-flight, CLI-invoked (`status`, `new`, and the scaffold `run <stem>`, section 18); both writer lanes inline in the one CLI process holding the single-writer lock. Merge = the v1 hard gate set minus the bug gate (deferred to Phase 6's report inbox) and including the diff budget gate (section 7), scoped per section 9's merge-time law: the re-run set is the MECHANICAL codes only, `correctness_review` participates as the pinned approval, and `requisition_review` never runs at merge; ticket-plane restore before rebase, squash + trailers (section 9). The verification gate runs WITHOUT base-diff attribution (any red `## Verification` command fails the Check; attribution lands with the Phase 2 spine, section 7). The runner validates and ticket-plane-commits pending hand-authored tickets at invocation (the fail-closed `source` stamp of section 13; intake lint enforces the full section 13 grammar including `Plan contract` ids, `On-demand`, and the `Context` plan-file refusal). Reconcile-on-entry (reaping orphaned in-flight runs). The `drain` verb (section 18) with findings-fed re-entry rendered IN CRITERIA-POSITION (section 11.2) and journal-derived `retry` accounting; a non-ok terminal journals its transition and exits 1, leaving ticket and branch in place. The Author stage + `specs/author.md` are a Phase 2 seed. Engine and host stay COLOCATED; the host-contract indirection is first exercised in Phase 6.
- *Emits:* the `review_baseline` NO-GO signal carrying the baselined identity (the resolved (provider, model) rows serving REVIEW and AUTHOR at every tier plus those surfaces' spec-major versions); one merged real ticket with complete artifacts and provenance events; the seeded Phase 2 queue -- the conductor's FINAL act (section 0 prompts 14-17): each seed intake-lint-clean, `confirmed`, dispatchable under the drain envelope (authored stuck budget at or under `drain.max_ticket_minutes`), ordered by `depends`/`priority`.
- *Exit reads:* the real ticket's `to: merged` transition and squash trailers (emitters: the merge lane, the journal); the recorded NO-GO verdict signal (emitter: the spike harness); the Phase 2 seeds present and lint-green on the ticket plane (emitter: the handoff deliverable). The conductor then retires.

### 19.P2 Phase 2 -- Failure spine

The reject-findings re-entry and journal-derived `retry` accounting shipped with the Phase 1 drain, so every deliverable here runs findings-fed and retry-bounded from its first invocation. Phase 2's seeds are authored by the conductor (section 0 prompts 14-17), each citing `19.L` and `19.P2`.
- *Deliverables, in `depends` order:* caps -- scoped to `diagnosis` and the `infra` budget (`premise_bounce` lands with its release below); auto-harvest before wipe (allowlist extraction, `attempts/` dirs; harvest EXTENDS the section 11.2 rendering, never a second path; worktree keys run- and attempt-scoped, section 6); the diagnosis call with `lessons` over harvested material (section 11's rung order); the Suggestion Box BEFORE anything that files into it (durable queue, signature dedup, decision registry; harvest enqueues each run record's second problems once the queue exists; its first messages are the ingested `bootstrap/suggestions.md` entries -- ONE `suggestion`-class message per non-empty line, the line as summary -- that file then DELETED in the box deliverable's own reviewed code diff, its fence naming `bootstrap/suggestions.md`); the escalation ladder ending at the Reject queue WITH `confirm` and `reject` AND the `premise_bounce` cap and its draw, landing before any hold can fire -- every deliverable that WRITES a marked terminal fences the terminal-write owner `chupa/runner.py` plus `chupa/stages.py`; the Reject queue is a journal-derived projection keyed on the `routed: reject_queue` marker riding the run's single terminal `state_transition` -- queue code never writes that terminal, and the verbs' resolutions journal through the same owner; the box's sequential triage consumer (operator verb `chupa triage`, section 12) -- an `author` verdict invokes Author IN the same pass, and until Author merges an `author`-verdict item rests `pending` with a paved road naming that deliverable; the Author stage + `specs/author.md`; `requisition_review` as THREE chained deliverables -- the pure review call + `specs/requisition_review.md` + gate registration with no consumers; its box-path wiring at Author; its seed-path wiring, sited at the seeding ticket's own Check stage with the PRE-ADMISSION seam in `merge.py`/`stages.py` (MERGE-SAFETY) enforcing the same verdict as the last point that can refuse a seeding branch -- never "drain intake"; each consumer fences the module that OWNS its seam.
- *Emits (each its own seeded ticket; the exit transitively depends on all):* the cumulative shakeout battery (fake LLM) as ONE chained deliverable per owning production module (a fixture ticket fences the ONE module whose behavior it pins plus its test file), each member specifying (1) the planted fault, (2) the single discriminating observable a correct engine produces and a faked run cannot, and (3) which artifact carries the human-readable detail -- the harvested finding, never the terminal REASON, which stays a stable code-only value (the section 11.4 comparison key). Each group run plants its faults and MACHINE-PRODUCES its report entries to its worktree OUTBOX, each later group re-confirming every prior group's entries before appending its own (the double gate). Membership: bad schema, scope escape, premise-false, unfixable lint planted BRANCH-ONLY, review-reject -- all reaching correct terminals with zero human input; a review-rejected ticket whose re-entry renders the prior findings IN CRITERIA-POSITION; a timed-out ticket whose second attempt sees the first attempt's dead ends; engine death mid-call reaped/harvested/re-entered findings-fed; a conflicted rebase leaving no half-rebased worktree; an empty committed diff reaching a non-ok terminal; a planted secret reaching no ticket-plane artifact; a premise-failed stem skipped until its ticket changes, then run; agent-CLI auth expiry yielding a classified non-ok naming the re-auth road; unparseable or schema-invalid output exhausting the bounded re-prompt then terminating; a stage past its stuck budget killed by the Phase 0 driver, harvested, and terminated while the drain proceeds; a ticket red on attempt one and green on attempt two merging in ONE drain invocation drawing one `retry` unit; K identical terminal reasons short-circuiting (section 11.4); per-COMMAND base-diff attribution (section 7). PLUS the diagnosis real-model eval as TWO chained deliverables -- harness + committed fixture set (expected verdicts proven reachable under the fake LLM; hard-kill before the deadline records and pre-call cost cap pinned by tests against the committed report), then the spend ticket that only EXECUTES the merged harness under a flat per-run USD constant (shipped 5.00), agreement rate recorded (the triage-dedup eval is deferred to daemon-era entry, section 18; Rework and Retro stay unevaluated -- their production signal is the section 14 scorecard). PLUS the invariant auditor over the journal, green across the whole battery.
- *Settled contracts:*
  - NAMES: the battery lives in `eval/shakeout/` with its public bench at `eval/shakeout/bench.py` and suite `tests/test_shakeout.py`; the auditor is `chupa/audit.py`/`tests/test_audit.py`; caps `chupa/caps.py`/`tests/test_caps.py`; box `chupa/box.py`/`tests/test_box.py`; triage `chupa/triage.py`/`tests/test_triage.py`; Author `chupa/author.py`/`tests/test_author.py`; starting-state policy `chupa/policy.py`/`tests/test_policy.py`; requisition review `chupa/requisition.py`; the diagnosis eval `eval/diagnose.py` with fixtures under `eval/diagnose_fixtures/`; the review harness test `tests/test_eval_harness.py`. Later registries name these paths.
  - BENCH SEAM: `Bench.configure(parsed_config)` rebuilds the production runner, drain, redactor, log, and pipeline factory around a replacement config whose `state_dir` resolves to the existing bench state dir, preserving the disposable repo, journal, clock, process, filesystem, git adapter, report sink, and scripted-model seams; members select fixtures only through it and never assign private bench fields.
  - REPORT REQUIRED: a group run's report command is never excusable. When a `## Verification` command names `tickets/<stem>/<registered KNOWN artifact>`, the Check fails `verification` unless that artifact is in the OUTBOX after Verification, whatever per-command attribution says (paved road: make the named runner exit 0 so it writes the report); so a passing group Check implies its runner's double gate and every member's auditor came back green.
  - FIXTURE CORPORA: a diagnosis-eval case is ONE closed JSON envelope (ticket text, harvest, optional run record, expected answer), so the 12-case corpus plus harness and tests stays inside the section 7 diff gate.
  - SUPERSEDED BEHAVIOR (rule 5): the verdict-verb/`premise_bounce` deliverable owns `tests/test_drain_upgrade.py`; the base-diff attribution deliverable owns `tests/test_drain_reentry.py`; Author owns `tests/test_eval_harness.py`'s pre-Author `spec_major.author: null` expectation.
  - ATTRIBUTION: recorded per verification command; every base-red command files through `Box.enqueue` with `origin` equal to the reporting stem (the section 12 signature dedups within that stem, never across stems); the same attribution runs at post-rebase merge regating; the Phase 1 branch-only-red re-entry regression stays beside the new base-red case.
  - LADDER: the escalation deliverable fences `chupa/caps.py`/`tests/test_caps.py`; the rung rides the retry `cap_consumed` body through the existing `consume` writer, never a copy in `drain.py`.
  - BOX: one-time ingest resolves a linked worktree through a `git rev-parse --git-common-dir` operation owned by `chupa/git.py`, fenced by the box deliverable. Messages carry nullable `bug_origin` and `has_repro` (required together when `message_class: bug_report`); Author uses a named tracked-file listing operation in `git.py` and validates policy inputs before its paid call.
  - REQUISITION WIRING: the Author-path consumer fences `tests/test_triage.py`, and every triage integration script reaching Author supplies the newly mandatory review response. The Driver gate loop gains one generic `terminal_findings` hook so a configured terminal verdict (requisition `rma`) returns at once without discarding other gates' findings; the review target resolver reuses the complete ticket-schema admission predicate, reserved stems included, so grammar-invalid work never spends a review call.
  - PROVIDER FAILURES in shakeout follow section 6's classification-to-finding rule: auth expiry proves `to: infra_error` plus an `infra` `cap_consumed`; the harvested finding carries `auth_error` and the re-auth road.
- *Exit reads:* every spine stem's `to: merged` (emitter: the merge lane, via transitive `depends`); battery green including every named member (emitter: the committed `shakeout-report.json`, a registered KNOWN artifact with a closed schema declared by the report-lane deliverable -- member id, planted fault, observed terminal/event, producing run id -- written only by the group runs' OUTBOXes and lifted by the ONE stage-terminal lift path, whose owner `chupa/stages.py` and `tests/test_stages.py` the report-lane deliverable fences; the cumulative copy rests in the LAST group's ticket dir); auditor green across the battery (emitter: the auditor's Check-lane `checks.json`, never authored by the auditor's own fence). The exit ticket authors Phase 3's `core` admission from `19.P3`.

### 19.P3 Phase 3 -- Continuous daemon (core)

- *Deliverables (index; the registry below is the seedable form):* the asyncio scheduler (single-flight dispatch, D2) with watcher-driven re-prioritization; the serial merge queue with post-rebase re-gate, pre-admission INTEGRATION CHECK, red-streak pause, tree-hash assert, conflict-facts journaling, and both resolution rungs (section 9); the Rework stage + `specs/rework.md` (update/split/escalate, the supersedes map; never invoked inline from the admission path, which holds the single ticket-plane writer lock -- the mechanical rung returns a typed unresolved-conflict handoff that Rework consumes after the admission unwinds); THRESH in its flat-subscription form (per-provider concurrency caps, `cli` classification including `unclassified`, the circuit breaker, section 6); the daemon control surface (section 20) one boundary per ticket; heartbeat; restart-reconcile + orphan sweeper + `timers.py`; flake handling (section 11.5) as detection then release; the journal roll trigger (section 6 engine constants, 64 MiB / 24h); the storm breaker (section 12) as ledger -> producer wiring -> notification activation -> dispatch hold; the checkpoint push with failed-push re-fire (section 10); production `serve` composition; daemon-mode merge admission; recovery disposition; run-lane admission; the bounded soak machinery, runner, and run. Until Rework activates, a `split` dispatches to the Reject queue (section 11.4).
- *Exit reads:* a BOUNDED DETERMINISTIC soak: `daemon-soak-runner` drives the PRODUCTION `serve` composition IN-PROCESS through injected seams (section 15 harness ladder rung 4 -- the FIRST of the two sanctioned pre-cutover `serve` harness runs, never the cutover) with the injected clock advanced at least 24 hours per member, so every recurring daemon cycle fires; elapsed wall time is never evidence. The member list is CLOSED: `worker_killed_mid_run` (reconciled, its `recovery_alert` naming disposition and producing run, the stem re-run clean); `conflict_resolution_rungs` (both rungs, the correct one selected, main green after each); `semantic_conflict_integration_red` (integration-red WITHOUT main ever going red). Every fault lands in the box or an alert, never silence; a member is green only when its terminal passed AND the auditor is green over that member's own journal. Emitter: `tickets/soak-run/daemon-soak-report.json` (machinery `daemon-soak` + `daemon-soak-runner`, producer `soak-run`), re-derivable by the merged suite. The real 24-48h soak stays operator acceptance (section 13 touchpoint 7).
- *Settled contracts:* the control inbox, `pause`, and `kill` semantics are section 20's; flake identity is section 11.5's; storm identity and the drain's hold selector are section 12's. Construction rows landing inside already-reachable modules -- `dispatch-admission-boundary`, `dispatch-config-snapshot`, `background-consumers`, `control-inbox`, `dispatch-pause-boundary`, the four dormant kill boundaries, `flake-detection`, `storm-producer-wiring` -- prove dormancy BEHAVIORALLY (`19.I`): no production caller of the new seam, by a test over the composition harness once it exists, before it by a test over the CLI composition root. Large roots expected on-demand in most renders: `chupa/drain.py`, `chupa/__main__.py`, `tests/test_drain.py`, `tests/test_mergequeue.py`, `tests/test_merge.py`.

```yaml
# BEGIN_REGISTRY_P3
phase: 3
# Admissions in order. The first is authored by phase2-exit with phase3-continue;
# each later list is one phase3-continue-<nn> admission (plus its successor tail).
admissions:
  - [daemon-scheduler, seed-successor-proof]
  - [merge-queue]
  - [rework-stage]
  - [thresh-runtime]
  - [dispatch-admission-boundary, dispatch-config-snapshot]
  - [scheduler-activation]
  - [merge-queue-activation, rework-activation]
  - [background-consumers, control-inbox]
  - [dispatch-pause-boundary, pause-resume-activation]
  - [admission-holds-activation]
  - [kill-signal-journal, kill-executor-abort]
  - [kill-worker-stop, kill-failure-suppression]
  - [kill-cli-activation]
  - [heartbeat]
  - [restart-timers]
  - [flake-detection, flake-release]
  - [journal-roll, storm-ledger]
  - [storm-producer-wiring, storm-notification-activation]
  - [storm-dispatch-hold]
  - [checkpoint-push]
  - [serve-activation]
  - [serve-merge-admission]
  - [worker-recovery-disposition]
  - [outbox-only-admission]
  - [daemon-soak]
  - [daemon-soak-runner]
  - [soak-run]
  - [phase3-exit]
seeds:
  daemon-scheduler: {cite: [9], fence: [chupa/scheduler.py, chupa/watcher.py, tests/test_scheduler.py],
    does: "Dormant single-flight scheduler plus watcher re-prioritization; dormancy = the 19.I import-closure scan, failing once either module is reachable."}
  seed-successor-proof: {fence: [tests/test_seed_successor.py],
    does: "A merged ticket registers its successor through the real lift/intake/rescan path, end to end."}
  merge-queue: {deep: true, cite: [9, 10], fence: [chupa/mergequeue.py, chupa/merge.py, chupa/git.py, tests/test_mergequeue.py, tests/test_git.py],
    does: "Dormant serial admission: post-rebase mechanical regate, integration check running the ticket's Verification through the existing gate on the rebased worktree, red-streak pause, tree-hash assert, conflict facts, two typed resolution rungs. git.py adds only public stop-at-conflict, conflicted-path listing, and rebase-continue, preserving rebase/rebase_abort."}
  rework-stage: {deep: true, cite: [4, 9, 11], fence: [chupa/rework.py, specs/rework.md, chupa/mergequeue.py, tests/test_rework.py],
    does: "Dormant update/split/escalate plus the supersedes map, consuming the typed conflict handoff only after admission unwinds."}
  thresh-runtime: {deep: true, cite: [6], fence: [chupa/thresh.py, chupa/providers.py, chupa/config.py, tests/test_thresh.py, tests/test_providers.py],
    does: "Flat subscriptions, per-provider concurrency caps (limits.concurrency parses here), cli classified/unclassified failures, the breaker."}
  dispatch-admission-boundary: {cite: [9], fence: [chupa/daemon.py, tests/test_daemon_admission.py],
    does: "Dormant daemon admission/task boundary."}
  dispatch-config-snapshot: {cite: [15], depends: [dispatch-admission-boundary], fence: [chupa/daemon.py, chupa/config.py, tests/test_daemon_config.py],
    does: "Per-dispatch immutable config snapshot."}
  scheduler-activation: {deep: true, fence: [chupa/daemon.py, chupa/scheduler.py, chupa/watcher.py, chupa/__main__.py, tests/test_scheduler.py, tests/test_daemon_admission.py, tests/test_daemon_composition.py],
    does: "Daemon core reachable from production; lands the in-process production-composition harness (tests/test_daemon_composition.py); migrates the scheduler dormancy test and the daemon-absence assertion."}
  merge-queue-activation: {fence: [chupa/merge.py, tests/test_merge.py, tests/test_mergequeue.py, tests/test_daemon_composition.py],
    does: "Composes the queue into the production pipeline factory and migrates its composition-absence assertion; the bootstrap drain keeps inline Phase 1 admission (daemon-mode routing is serve-merge-admission)."}
  rework-activation: {depends: [merge-queue-activation], fence: [chupa/daemon.py, chupa/rework.py, chupa/mergequeue.py, tests/test_rework.py, tests/test_daemon_composition.py],
    does: "Rework consumes handoffs on the lock-owning writer; split stops routing to the Reject queue."}
  background-consumers: {fence: [chupa/daemon.py, tests/test_daemon_tasks.py],
    does: "Owned watcher, merge-queue, and box-consumer tasks (DaemonTasks)."}
  control-inbox: {cite: [20], depends: [background-consumers], fence: [chupa/control.py, chupa/daemon.py, chupa/seams.py, tests/test_control.py],
    does: "Dormant crash-safe inbox: identity-bound, exactly once, decision journaled before mutation; publication through a tested durable no-overwrite filesystem-seam operation."}
  dispatch-pause-boundary: {cite: [20], fence: [chupa/daemon.py, chupa/drain.py, tests/test_daemon_pause.py, tests/test_drain.py],
    does: "Pause precedes ALL durable dispatch accounting, the drain's retry-cap draw included."}
  pause-resume-activation: {cite: [20], depends: [dispatch-pause-boundary], fence: [chupa/daemon.py, chupa/control.py, chupa/drain.py, chupa/__main__.py, tests/test_daemon_pause.py, tests/test_control_cli.py, tests/test_daemon_composition.py],
    does: "CLI pause/resume route through the inbox while an engine holds the lock; direct locked behavior unchanged."}
  admission-holds-activation: {depends: [pause-resume-activation], fence: [chupa/mergequeue.py, chupa/merge.py, chupa/__main__.py, eval/shakeout/bench.py, tests/test_mergequeue.py, tests/test_merge.py, tests/test_daemon_composition.py],
    does: "Red-streak and tree-hash holds activate with identity-bound resume over ONE shared inbox: the CLI root shares it between the drain control factory and the pipeline factory, every direct compose_pipeline caller supplies it, no fallback constructs a second; minimal MergeQueue construction stays valid."}
  kill-signal-journal: {cite: [20], fence: [chupa/control.py, chupa/daemon.py, tests/test_kill_signal_journal.py], does: "Dormant kill-signal journaling."}
  kill-executor-abort: {cite: [6, 20], depends: [kill-signal-journal], fence: [chupa/daemon.py, chupa/driver.py, tests/test_kill_executor_abort.py], does: "Dormant executor abort atomicity."}
  kill-worker-stop: {cite: [20], fence: [chupa/daemon.py, tests/test_kill_worker_stop.py], does: "Dormant worker stop ordering: executor unwinds before worker cancel."}
  kill-failure-suppression: {cite: [20], depends: [kill-worker-stop], fence: [chupa/daemon.py, tests/test_kill_failure_suppression.py], does: "Dormant post-kill failure-path suppression."}
  kill-cli-activation: {deep: true, cite: [20], fence: [chupa/daemon.py, chupa/stages.py, chupa/drain.py, chupa/__main__.py, tests/test_kill_signal_journal.py, tests/test_kill_executor_abort.py, tests/test_kill_cli_activation.py],
    does: "Adds the kill verb against the live bootstrap drain per section 20; Stages exposes only its Driver abort; worker-stop and failure-suppression stay dormant until serve-activation. Other kill tests are preservation suites."}
  heartbeat: {cite: [9, 15], fence: [chupa/heartbeat.py, chupa/daemon.py, tests/test_heartbeat.py], does: "Heartbeat file plus external heartbeat."}
  restart-timers: {deep: true, cite: [6, 15], fence: [chupa/restart.py, chupa/timers.py, chupa/daemon.py, chupa/__main__.py, tests/test_restart_timers.py],
    does: "Restart-reconcile reaps orphans to abandoned, orphan sweeper, journaled timers armed, persisted, and re-armed at startup -- reap and re-arm before dispatch in the CLI/serve composition roots."}
  flake-detection: {cite: [11], fence: [chupa/flake.py, chupa/daemon.py, tests/test_flake.py], does: "Section 11.5 detection and quarantine through a dormant daemon composition hook."}
  flake-release: {cite: [11], depends: [flake-detection], fence: [chupa/flake.py, chupa/daemon.py, tests/test_flake.py], does: "Section 11.5 identity-bound mechanical release."}
  journal-roll: {cite: [6], fence: [chupa/journal.py, tests/test_journal_roll.py], does: "Roll at 64 MiB or 24h, engine constants."}
  storm-ledger: {cite: [12], depends: [journal-roll], fence: [chupa/storm.py, tests/test_storm.py], does: "Dormant section 12 occurrence ledger; no trip, message, notification, or hold."}
  storm-producer-wiring: {cite: [12], fence: [chupa/storm.py, chupa/box.py, chupa/daemon.py, tests/test_storm.py, tests/test_storm_producer.py],
    does: "Every box arrival, dedup hit included, records one stable occurrence; production stays dormant."}
  storm-notification-activation: {cite: [12], depends: [storm-producer-wiring], fence: [chupa/storm.py, chupa/box.py, chupa/daemon.py, chupa/__main__.py, tests/test_storm.py, tests/test_drain.py, tests/test_storm_notification_activation.py],
    does: "Activates the trip signal and its one P0 failure_report; migrates only the drain test's blanket no-box-event assertion to admit storm_occurrence events while still proving the drain never mutates or triages box records. No dispatch suppression."}
  storm-dispatch-hold: {deep: true, cite: [12, 20], fence: [chupa/storm.py, chupa/control.py, chupa/daemon.py, chupa/drain.py, chupa/__main__.py, tests/test_storm_hold.py],
    does: "Section 12 dispatch hold and identity-bound resume in the live drain; fences each predecessor storm test carrying a dispatch-absence assertion. Sole production owner of the hold."}
  checkpoint-push: {cite: [10], fence: [chupa/checkpoint.py, chupa/daemon.py, chupa/git.py, tests/test_checkpoint.py, tests/test_git.py, tests/test_mergequeue.py],
    does: "Public argv-only push in git.py (migrating only the git public-operation allowlist test); re-fires an incomplete push after restart, never duplicating a completed one."}
  serve-activation: {deep: true, cite: [18, 20], fence: [chupa/serve.py, chupa/daemon.py, chupa/__main__.py, tests/test_serve.py, tests/test_daemon_composition.py, tests/test_daemon_tasks.py, tests/test_kill_worker_stop.py, tests/test_kill_failure_suppression.py, tests/test_heartbeat.py, tests/test_storm.py],
    does: "The serve verb and continuous loop composing dispatch, watcher, merge, box, control, heartbeat, restart/timers, storm, checkpoint, and worker tasks; reconciles before dispatch, holds the lock for its lifetime, exits only via kill/signal or a terminal worker failure; activates worker-stop and failure suppression (decision before mutation, executor unwind before worker cancel); tests build the real graph in-process and replace serve-absence assertions."}
  serve-merge-admission: {deep: true, cite: [9], fence: [chupa/merge.py, chupa/serve.py, tests/test_merge.py, tests/test_mergequeue.py, tests/test_serve.py],
    does: "Explicit daemon-admission mode selected only by serve composition (drain keeps inline admit, never daemon holds): a settled run passes code-lane and seed-safety prechecks, then offers exactly one candidate to the MergeQueue, which owns rebase, both rungs, regate, integration, and holds; success retires worktree/branch and journals to: merged once with the real commit and reviewed SHA; gate_failed/rework leave main and branch intact. Tests drive the real serve-selected path, never queue admit from a harness."}
  worker-recovery-disposition: {deep: true, cite: [6, 15], fence: [chupa/reconcile.py, tests/test_reconcile.py],
    does: "Per reaped orphan, after abandoned and before worktree removal, one run-scoped signal {kind: recovery_alert, disposition: alert, outcome: abandoned, reason}; the terminal prevents re-emission on later restarts; no box mail or routing change."}
  outbox-only-admission: {deep: true, cite: ["19.L", 10], fence: [chupa/stages.py, chupa/merge.py, tests/test_stages.py, tests/test_merge.py],
    does: "The 19.L run-lane admission rule, at initial Verification and merge regate."}
  daemon-soak: {deep: true, fence: [eval/daemon_soak.py, chupa/artifacts.py, chupa/stages.py, tests/test_daemon_soak.py],
    does: "Closed daemon-soak-report.json schema (member, planted fault, observed terminal/event, disposition, producing run, auditor verdict, green), KNOWN-artifact registration, canonical ordinary-lane writer."}
  daemon-soak-runner: {deep: true, fence: [eval/daemon_soak.py, tests/test_daemon_soak.py, tests/test_daemon_soak_runner.py],
    does: "Public deterministic runner driving merged production serve in-process for the three closed members (exit reads above), deriving every field from member-local evidence and returning the report only to the writer."}
  soak-run: {fence: [tickets/soak-run/daemon-soak-report.json], does: "No code: invokes the merged runner and writer, leaving the report in its OUTBOX."}
  phase3-exit: {exit: true, fence: [tickets, tests/test_phase3_exit.py, tests/test_seeded_phase4_core.py],
    does: "Reads the committed soak report's green members through its artifacts schema; authors the 19.P4 core."}
# END_REGISTRY_P3
```

### 19.P3.daemon-scheduler Dormant scheduler and ticket watcher

- **Owner:** `chupa/scheduler.py` owns the dormant asyncio pending queue and single-flight dispatch boundary; `chupa/watcher.py` owns debounced ticket-directory change consumption and the last-known-good parsed ticket cache. `chupa/drain.py` remains the bootstrap eligibility-sort owner: reuse its `authored_at`, `sort_key`, and `SETTLED` without changing it. The watcher uses the existing `chupa.tickets.parse_ticket`; no second ticket grammar. Neither new module is imported by the production CLI closure until `scheduler-activation`.
- **Records:** Inputs are parsed `Ticket` records keyed by `stem`, their `frontmatter.state` (`draft`, `confirmed`, `rejected`, `merged`), `frontmatter.priority` (`P0` through `P3`), and `depends` (tuple of predecessor stems). Only `confirmed` tickets with every predecessor settled may enter the ready queue; `merged` and `already_satisfied` satisfy an edge, matching `drain.SETTLED`. Read journal `state_transition` events by envelope `ticket` and body `to` through the existing `last_states` fold, and pending Reject verdicts through `reject_queue`: a terminal with `routed: reject_queue` holds the stem until a later `signal: reject_verdict` resolves it. These records keep their existing writers; the scheduler never writes terminals or verdicts. Age reads the FIRST per-stem `EventType.SIGNAL` with body `signal: ticket_intake` (`tickets.INTAKE_SIGNAL`), using envelope `ts`, never file mtime; the existing ticket-plane intake owns that event, whose body is `{signal, source, state, new, commit}`. Reuse the existing sort key `(priority rank, missing age, timestamp or empty string, stem)`, with `P0` highest, oldest known timestamp first, missing age last, and stem the final tiebreak. Quarantined and provider-drought-parked stems are supplied as journal-derived held-stem sets by the caller; recompute eligibility on each selection, so removal of a hold releases the stem without changing its ticket. The caller supplies the current completed-but-unmerged count and `scheduler.max_unmerged` (existing config default `2`); at or above that limit no new dispatch starts. Pending tickets, cached parses, and the active slot are memory-only projections, never new durable records. The watcher alone writes `EventType.SIGNAL` with envelope `ticket: <stem>`, `key: null`, and body `{signal: watcher_parse_failure, path: tickets/<stem>/ticket.md, reason: <nonempty parse diagnostic>}` when a debounced candidate fails parsing; `WATCHER_PARSE_FAILURE = "watcher_parse_failure"` belongs to `chupa/watcher.py`. A failed parse preserves the complete previous parsed record and its sort position; without a previous parse the stem stays absent. A later valid parse replaces the cache, and a removed ticket drops its pending entry. No new frontmatter, config key, journal event type, or authoring event is introduced.
- **Observable:** Exercise the dormant components directly with injected ticket reads/change delivery, journal, dispatch callable, clock, and `Sleep`; no raw process or notification calls, and no watcher dependency or seam-module change. Coalesce edits until the debounce wait completes before publishing a parsed update; a further edit restarts that wait. Valid priority edits and new tickets re-sort pending work before the next selection. Await each dispatch to completion before starting another, including concurrent selection requests; clear the active slot on completion, exception, or cancellation. An edit never cancels or preempts active work: a newly eligible P0 takes the next free slot. Re-read eligibility and backpressure before that slot is filled. This construction does not activate a daemon loop, change bootstrap dispatch, draw caps, perform merge admission, or manufacture quarantine/drought decisions.
- **Tests:** `tests/test_scheduler.py` imports and exercises both new production modules. Named obligations: `test_single_flight_dispatch` (two concurrent offers cannot overlap); `test_dispatch_failure_and_cancellation_release_slot` (both unwind paths allow the next offer); `test_eligibility_and_hold_release` (confirmed state, settled dependencies including `already_satisfied`, Reject verdict fold, quarantine/drought exclusion and release); `test_priority_age_and_stem_order` (distinct authoring timestamps, first-event anchoring, missing age last, priority outranking age, stem tiebreak, no mtime dependence); `test_max_unmerged_backpressure` (boundary holds and release); `test_watcher_debounce` (partial writes and restarted waits cannot publish early); `test_watcher_reprioritizes_without_preemption` (edit/new P0 changes the next pick while active work finishes); `test_watcher_parse_failure_preserves_last_good` (old position retained, new invalid stem excluded, exact journal signal, valid recovery); `test_watcher_removal_drops_pending`; and `test_scheduler_and_watcher_are_dormant` (the `19.I` transitive import-closure scan rooted at `chupa/__main__.py`, recognizing both import idioms and proven to fail when either module becomes reachable). Timing tests advance injected time, never wall-clock sleeps. Activation migrates the dormancy assertion in its own fenced ticket.

### 19.P3.merge-queue Dormant serial merge admission

- **Owner:** `chupa/mergequeue.py` owns `MergeQueue`, its serial pending admissions, mechanical conflict resolution, typed unresolved-conflict handoff, integration-red streak, checked-tree assertion, and the host mechanical-check runner. `chupa/merge.py` retains ownership of admission gates, squash-message construction, and the existing inline bootstrap admission; extract reusable admission operations there without changing its public `merge(ctx, ticket, *, attempt)` behavior. `chupa/stages.py` owns all `Evidence` gathering, including the non-verification fields needed by safety gates. Construction extracts that gathering into `gather_safety_evidence`; `gather_evidence` reuses it and retains its public signature and full Verification behavior. Under section 9.5's seam-owner law, the authored merge-queue seed adds `chupa/stages.py` and `tests/test_stages.py` to the registry fence floor and includes them in its Context/on-demand closure; no evidence gatherer is copied into `mergequeue.py`. `chupa/git.py` owns every git operation. The new queue is exercised directly and remains unreachable from production until `merge-queue-activation`; daemon admission routing, Rework consumption, control-inbox hold release, and notification transport belong to their later activation rows.
- **Records:** An offer consists of the existing parsed `Ticket` and its integer `attempt`, using its stem verbatim as branch and worktree identity, `frontmatter.priority` (`P0` through `P3`), scope-fence prefixes, and parsed Verification argv tuples. Read the FIRST journal `EventType.SIGNAL` with `signal: ticket_intake` for each stem's age; its envelope `ts` and `ticket` are authored by the existing intake writer. Reuse `drain.authored_at` and `drain.sort_key`: `(priority rank, missing age, timestamp or empty string, stem)`, oldest known timestamp first and missing age last. Pending offers, the active admission, and the pause flag are memory-only projections, not new ticket frontmatter or run states. Capture the pre-rebase branch SHA as `reviewed_sha`; reuse `merge.Candidate` (`stem`, `reviewed_sha`, `changed_files`, main's `ticket_text`, nullable `review_text`, `seeds`, nullable `seed_checks_text`) and `SeedOnMain` (`stem`, nullable committed `ticket_sha` and `ticket_text`). Review owns the pinned `ApprovedInvoice` in `tickets/<stem>/review.md`; seeding Check owns the `Invoice.seeds` approvals in `checks.json`. Read seed identities from existing intake signals with `seeded_by: <offering stem>` and compare approvals to main's committed seed blobs, retaining the existing `SeedSafetyGate` behavior. A missing, malformed, snagged, or wrong-SHA approval refuses admission; a clean rebase carries the original approval without a model call.

  Reuse the stage-owned `Evidence` and `CommandResult` and the existing `CHECK_GATES`/`MERGE_GATES` and `run_gates` protocol. Evidence carries `stem`, `claimed`, the rebased `head_sha`, committed `changed_files`, `scope_fence`, `inserted_lines`, Verification results, lifted `run_record`, and nullable `plan_main`/`plan_head`; each command result is `{argv: list[str], rc: int | null, tail: str, base_red: bool}`. `ScopeFenceGate` and `RunRecordGate` judge this record. The existing `stages.gather_evidence` is the sole production producer and runs every ticket Verification command, including any base-red worktree rerun, before returning the non-verification fields. Construction splits out `stages.gather_safety_evidence(ctx, ticket, claimed)`, returning those same fields with `verification: []` and running no Verification command or base rerun. Full `gather_evidence` calls that one field gatherer and fills `verification` with its established results; Check and inline merge keep their existing calls. Safety never submits empty Verification results to `VerificationGate`. The stage-owned gatherer retains verification spools, redaction, and base-red attribution; the queue does not duplicate them or change `VerificationGate`'s established base-red policy. Gate findings retain `{code, path, line, message, paved_road, kind}` and `GateReport` retains `{code, verdict: pass | fail, findings, autofix_applied}`.

  Read the existing config `merge.safety_checks` (host check codes), `review.mechanical` entries (`code`, `argv`, `trigger: always | list[path-prefix]`, `severity: hard | soft`), and `merge.strategies`: `{paths: list[path-prefix], strategy: regenerate, argv: list[str]}` or `{paths: list[path-prefix], strategy: union}`. Configuration declares host checks but no existing runner executes them; `gather_evidence` executes only the ticket's Verification commands. The queue owns the first host-check runner, returning in-memory `CommandResult` and `GateReport` records, not a new artifact or entries in `Evidence.verification`. Safety selects the codes in `merge.safety_checks`; each must resolve to exactly one hard `review.mechanical` entry. A missing, ambiguous, or soft designation refuses safety with report and finding code `post_rebase_regate`, naming the designation and the paved road "declare exactly one hard review.mechanical entry for this code, or remove it from merge.safety_checks". Explicit fast designation runs the hard entry regardless of its trigger. Integration selects every `trigger: always`, `severity: hard` entry in config order, including ones already run in safety. Unselected soft or path-triggered entries are skipped without a report; the queue does not implement review-time trigger evaluation.

  Each executed host entry yields a report with its configured `code`, `autofix_applied: false`, and `verdict: pass` with no findings only for `rc: 0`. Nonzero exits, `TimeoutError`, and `ExecutableNotFound` yield `verdict: fail` with a finding using that same code, null `path`, `line`, and `kind`, and a scrubbed message naming argv, exit status or setup/timeout reason, and output tail. The paved road is "make the configured command exit 0 on the rebased candidate and retry" for a nonzero exit, "make the command finish within the ticket's stuck budget or correct that budget and retry" for a timeout, and "install the executable or correct argv/PATH in the child environment and retry" for an unresolvable executable. Timeout and unresolved execution use `rc: null`. Host results always have `base_red: false`: host checks get no base-worktree rerun or base-red exemption, so a required host failure refuses admission even if main would also fail. Only ticket Verification retains the existing base-red attribution policy.

  Only matching declared paths receive a strategy; an undeclared path or multiple matching strategies refuses mechanical resolution. A regenerate path must not also be agent-owned by the ticket fence. Strategy paths are exempted only in admission's scope-fence evaluation, without changing the authored ticket or the stage gate implementation.

  `chupa/mergequeue.py` alone owns `CONFLICT_FACTS = "merge_conflict_facts"`, `RED_STREAK = "merge_red_streak"`, `TREE_MISMATCH = "merge_tree_mismatch"`, and `RED_STREAK_LIMIT = 3` (an engine constant, no config key). It journals one `EventType.SIGNAL` per completed admission check or conflict refusal, with envelope `ticket: <stem>`, `key: null`, and body `{kind: merge_conflict_facts, conflicted_paths: list[str], resolving_rung: none | mechanical | rework, strategy_paths: list[str], integration_red_paths: list[str]}`. Path lists are sorted and unique; clean rebases use empty conflict/strategy lists and `none`; a mechanical resolution uses `mechanical`; `rework` identifies an unresolved handoff, never claims that Rework ran or resolved it. Integration-red paths are the rebased committed changed-file set when integration fails, otherwise empty. Repeated red attempts for one stem do not increment the streak: count consecutive distinct integration-red stems since the last integration-green candidate or explicit resume; safety failures and conflict handoffs do not count as integration outcomes. On reaching three, journal once `{kind: merge_red_streak, stems: list[str], limit: 3}` under the tripping stem and pause further admissions. On a checked/main tree mismatch, journal once `{kind: merge_tree_mismatch, checked_tree: str, main_tree: str}` under the admitted stem and pause immediately. Both signals use `key: null` and expose escalation through an injected consumer; production inbox binding and transport activation are deferred. A direct injected resume releases the construction's pause and clears its streak; it cannot preempt active admission.

  Both resolution rungs are typed at this boundary. Mechanical success continues admission; unresolved conflicts return a queue-owned immutable `ConflictHandoff` with `{stem: str, reviewed_sha: str, conflicted_paths: list[str], findings: list[Finding], approval_invalidated: true}` after aborting the rebase. This is an in-memory handoff for later `rework-stage`, not an artifact registration, journal terminal, new `StageResult.outcome`, or inline Rework invocation. Ordinary success/refusal retains `StageResult`: `ok` with existing `Admission` (`stem`, real squash `commit`, original `reviewed_sha`, existing artifact provenance), or `gate_failed` with no artifact and paved findings. The existing merge writer alone emits the squash Effect using key `merge/<stem>/<attempt>`, commit subject/trailers from `squash_message`, and `state_transition` body `{to: merged, commit: <real commit>, reviewed_sha: <original SHA>}`. A refusal emits no terminal; the runner remains the non-ok terminal writer. No ticket-plane output is committed on the branch.
- **Observable:** One serial async admission processes ready offers in the shared priority/age/stem order. Concurrent processing requests cannot overlap main mutation; a P0 arriving during admission takes the next free slot. Restore lifted tracked ticket-plane deletions from the branch's committed head using existing `Git.restore(..., source=stem)` BEFORE rebase, so the index is clean; the rebase then brings that plane to current main's content. Preserve this merged-code behavior rather than dirtying an old branch index with main's newer ticket-plane bytes. After rebase, gather safety evidence through `stages.gather_safety_evidence` and run cheap MERGE-SAFETY first (rebase-clean, scope fence, run-record, code-lane, pinned approval, seed-safety, and configured host fast checks); a refusal pays no full verification run or Verification base rerun. Only after safety passes, call full `stages.gather_evidence` and run the full applicable engine mechanical hard set and host mechanical checks with `trigger: always` and `severity: hard`, plus every ticket Verification command in the rebased worktree through the stage-owned evidence writer and `VerificationGate`.

  In both tiers, the queue executes host argv through `ctx.exec_.run` with `cwd=ctx.worktree(stem)`, `env=child_env(ctx.env, ctx.config)` (no serving provider), and `timeout=ticket.stuck_minutes * 60.0`; no new timeout config is introduced. Write argv, exit status, stdout, stderr, and timeout/setup diagnostics through `ctx.driver.spool.write(stem, attempt, name, text)`, whose existing write seam redacts configured secret values before filesystem persistence. Names are `merge-safety/host-<nn>.txt` and `merge-integration/host-<nn>.txt`, where `nn` is the entry's one-based, zero-padded position in `review.mechanical`, never its host-supplied code. Scrub returned tails with `ctx.driver.redactor.scrub` using the existing `OUTPUT_TAIL_CHARS` bound, and scrub finding messages before returning them. Output belongs only in attempt spools and returned findings, never the journal. A fast designation does not remove an always-hard check from integration. Neither tier re-runs model review or judges unrelated binary evidence already on main. Before main mutation capture the checked candidate's `HEAD^{tree}` via `Git.rev_parse`; squash only after both tiers pass. Immediately after the real squash commit assert `main^{tree}` equals that checked hash. A mismatch is an engine defect, emits its escalation and prevents further admission/retirement; it is never reported as a pre-merge refusal with main untouched.

  An integration-red candidate leaves main unchanged and preserves its branch/worktree, returning the integration findings for the failure spine. Below the distinct-stem limit the next ready offer proceeds immediately; at the limit the queue pauses until its direct release seam is exercised. A green candidate resets the streak, commits code only, journals merged once, then retires via `Git.worktree_remove` (remove + prune) and `Git.branch_delete`. Preserve existing approval, seed-safety, trailers, Effect custody, and inline bootstrap behavior; do not route bootstrap calls through the dormant queue or add daemon/GO supervision holds.

  Add only the public git operations `rebase_stop_at_conflict`, `conflicted_paths`, and `rebase_continue`. The first leaves a genuine conflicted rebase available for the mechanical rung instead of auto-aborting; failed rebases without conflicted paths are refusals and abort before returning. The second lists unmerged paths; the third continues a staged resolution noninteractively and can encounter another conflict, which repeats the same ladder. Keep `Git.rebase` and its existing abort-on-refusal behavior unchanged; use the wrapper's existing argv-only abort path for queue cleanup. Mechanical resolution applies only the config-declared strategies: `union` retains both sides' append-only additions, and `regenerate` takes one side and runs the declared generator argv in the worktree through process exec, with no provider secrets. Stage resolved paths through `Git.add` and continue until rebase finishes; generator failure or any remaining undeclared/unresolved conflict aborts and returns `ConflictHandoff`. No model call occurs under admission's writer boundary. Refusal, exception, and cancellation all abort any in-progress rebase before unwinding and release the serial slot, leaving the branch re-runnable. Strategy success preserves the approval but still runs both post-rebase tiers; a handoff invalidates approval and is consumed only after admission unwinds. No rerere cache, micro-rework, new config, shell command, or production composition change is part of construction.
- **Tests:** `tests/test_mergequeue.py` imports and exercises the dormant production queue with injected seams and real disposable git repos where tree/rebase behavior matters. Named obligations: `test_serial_priority_age_order` (concurrent requests, distinct intake clocks, missing age, stem tiebreak, no P0 preemption); `test_restore_rebase_safety_integration_order` (lifted tracked deletions and moved main); `test_safety_failure_skips_integration` (each safety gate and host fast check, no Verification or base rerun, stage-owned safety evidence); `test_verification_uses_rebased_worktree` (existing evidence/gate path and preserved base-red attribution); `test_always_hard_host_checks_run_before_squash` (config order, fast designation cannot omit integration); `test_host_check_environment_timeout_and_redaction` (both tiers, provider keys absent, stuck-budget timeout, exact spool paths, secrets scrubbed in spools and findings); `test_host_check_failure_reports` (nonzero, timed-out, and unresolvable commands, configured codes, null execution status, paved roads, main unchanged); `test_host_check_selection_fails_closed` (missing, ambiguous, and soft safety designations refused; explicitly designated path-triggered hard checks run in safety; unselected soft/path-triggered checks skipped without reports); `test_host_checks_have_no_base_red_exemption` (required host failure refuses without a base rerun while ticket Verification retains attribution); `test_semantic_conflict_never_moves_main` (two individually green branches, combined red, preserved branch and next admission proceeds); `test_clean_rebase_carries_pinned_approval` (no model call, wrong/missing approvals refused); `test_committed_seed_approval_preserved`; `test_squash_tree_trailers_and_retirement` (checked tree equality, code only, real commit and original SHA, one merged event, cleanup); `test_tree_mismatch_escalates_and_pauses`; `test_distinct_red_streak_pause_and_resume` (same-stem retries, three distinct reds, green/reset/release, exact signal); `test_declared_union_and_regenerate_resolve` (both strategies and repeated continue conflicts); `test_strategy_ownership_and_matching_fail_closed` (undeclared/ambiguous paths and dual ownership); `test_strategy_resolution_still_regates`; `test_unresolved_conflict_returns_typed_handoff_after_abort` (generator failure and undeclared conflict, invalidated approval, no inline Rework/main mutation); `test_conflict_facts_shapes` (clean, mechanical hits, handoff and semantic red); `test_admission_exception_and_cancellation_abort_and_release`; and `test_merge_queue_is_dormant` (the `19.I` transitive CLI import-closure scan, both import idioms, proven to fail when reachable, plus unchanged inline admission). `tests/test_git.py` adds named obligations `test_rebase_stop_at_conflict_preserves_conflicted_state`, `test_conflicted_paths_argv_and_output`, and `test_rebase_continue_is_noninteractive`; existing `test_refused_rebase_is_aborted_before_refusal_returns`, `test_rebase_success_does_not_abort`, and dir/env/timeout tests stay green. Run `tests/test_merge.py` unchanged as a preservation suite, especially its approval carry, base-red policy, ticket-plane restore, seed safety, and conflicted-rebase abort tests. `tests/test_stages.py` adds `test_gather_safety_evidence_runs_no_verification` (all non-verification fields match full evidence, empty Verification list, no command or base worktree) and `test_full_gather_evidence_reuses_safety_gatherer` (one metadata producer, unchanged public signature, full Verification and base-red reruns); its existing base-red, provider-env, anchored scope-fence, and run-record tests stay green. Construction tests use injected time and process/notification consumers; later activation tickets migrate dormancy and hold-release assertions in their own fences.

### 19.P3.seed-successor-proof Successor registration through the production drain

- **Owner:** `tests/test_seed_successor.py` owns this proof only; no new production module or behavior. Existing owners remain `chupa/stages.py` for seed review and ticket-plane lift, `chupa/tickets.py` for ticket validation and human intake, `chupa/merge.py` for code admission and the merged terminal, and `chupa/drain.py` for committed-ticket re-scan and dependency selection. Use the merged seeding fixtures in `tests/test_seed_path.py` and the CLI/drain fixtures in `tests/test_drain.py` as idioms; run them unchanged as preservation suites, together with `tests/test_merge.py`.
- **Records:** The disposable repo starts with one parent ticket; its Implement output creates a fresh `tickets/<successor>/ticket.md`, uncommitted on the parent's worktree, with `state: confirmed`, `source: seed`, `priority: P2`, `kind: chore`, `agent_tier: medium`, and `agent_effort: medium`. It is a complete grammar-valid ticket with `## Depends on` naming the parent, valid Plan contract, Context, fence, and Verification. The parent fences `tickets` for seed creation and a small code path for a real code-bearing admission; the successor also produces a small code change, avoiding run-lane admission or self-upgrade. Fixture Implement callbacks alone author these outputs; neither test setup nor dispatch hand-writes the successor on main.

  Check owns `tickets/<parent>/checks.json`; read it through the existing `Invoice` schema and assert the successor's `SeedReview` fields `{stem, ticket_sha, verdict, findings, mechanical}`, with `verdict: approve`, empty `findings`, and `ticket_sha` equal to the successor's committed git blob. Check alone writes the seed review signal under envelope `ticket: <successor>`, `key: null`, with body `{signal: requisition_verdict, seeding: <parent>, verdict: approve, ticket_sha: <blob SHA>, findings: [], text: <reviewed ticket text>}`. `stages.lift_seeds` owns the seed-only commit `chupa(<parent>): seeds` and the following `EventType.SIGNAL` under the successor with body `{signal: ticket_intake, source: seed, state: confirmed, new: true, commit: <seed commit SHA>, seeded_by: <parent>}` and `key: null`; this is the seed's intake record, never a second human-intake pass. The existing Effects writer owns the `effect_intent` with empty body and `effect_completion` with body `{result: {commit: <seed commit SHA>}}`, both keyed `ticket-plane/<parent>/<attempt>/seeds` under the parent. The existing merge writer owns each `state_transition` with body `{to: merged, commit: <real squash SHA>, reviewed_sha: <reviewed branch SHA>}`. `drain.SETTLED` remains `merged` and `already_satisfied`; a dependency is not satisfied by the intake signal or the mere presence of a committed seed. No new record, constant, frontmatter field, or config key is introduced.
- **Observable:** One invocation of the production CLI `drain` composition runs the parent and then its newly emitted successor to merged and quiescence. Supply a scripted `FakeLLM` through the existing pipeline seam bound to `runner.bind`; retain real `runner.drive`, Implement/Check/Review, seed lint and requisition review, `lift_seeds`, Effects/journal, merge admission, and the drain's re-scan. Use real disposable git repositories through `Git`, injected clock and sleep, and existing filesystem/process seams. At parent Review the approved seed is already committed and intake-recorded, while the parent has no merged terminal and the successor has not run. A direct call to the real drain scan and selector over that snapshot must include the committed successor in the scan but refuse to select it while its parent edge is unsettled. After parent admission the next scan discovers the successor and its now-settled edge without restarting drain, calling intake again, or registering a hook. Both branches commit code only; the seed travels exclusively through the ticket-plane commit. Observe one seed intake and one merged terminal per stem, with the parent's terminal before the successor's dispatch. No scripted dispatch may manufacture a merged terminal, no monkeypatch may replace scan/selection/lift/admission, and no real-model call or wall-clock sleep is evidence.
- **Tests:** `tests/test_seed_successor.py::test_merged_parent_registers_and_runs_successor_in_same_drain` proves all records and ordering above: successor absent at invocation start; approved seed blob and intake visible before parent merge; no successor execution before that terminal; same invocation dispatches the successor through the real pipeline; exactly one seed-only commit and intake signal; pinned Check approval and lift Effect result match the committed bytes and commit; parent and successor squash commits contain only their code paths; both real merged terminals and final quiescence. The fixture's request sequence must fail if lift, intake emission, re-scan, or dependency gating is bypassed. Verification runs `uv run pytest tests/test_seed_successor.py tests/test_seed_path.py tests/test_drain.py tests/test_merge.py`. This is an integration proof over merged behavior, not a scheduler construction or activation and not a historical seed snapshot test.

### 19.P3.rework-stage Dormant Rework orders and supersession

- **Owner:** `chupa/rework.py` owns the dormant Rework LLM stage, its composite rework-order schema, ticket-proposal validation, and supersedes-map writer and folds. `specs/rework.md` owns the governed `rework` prompt. `chupa/mergequeue.py` retains ownership of `ConflictHandoff` and admission unwind; it never calls Rework inline. The existing Driver owns model calls, effects, spools, schema re-prompts, and cost; `chupa/tickets.py` owns ticket grammar and `chupa/requisition.py` owns feasibility review. The existing failure spine retains terminal writes, cap draws, and capability selection. Construction exercises Rework directly; production consumption and ticket-plane application belong to `rework-activation`.
- **Records:** Consume the original parsed `Ticket` and its committed text, a snag list of existing `Finding` records (`code`, nullable `path` and `line`, `message`, `paved_road`, nullable `kind`), and an optional queue-owned `ConflictHandoff`. The handoff has exactly `{stem: str, reviewed_sha: str, conflicted_paths: list[str], findings: list[Finding], approval_invalidated: true}`; its stem must match the ticket, paths are sorted and unique, and its approval is never reusable. The caller supplies the run sequence/attempt and effective tier/effort; Rework does not allocate a run, reset a budget, or select its own capability.

  The model reply is a strict, extra-forbidden `{action: update | split | escalate, tickets: list[{stem: nonblank str, ticket: nonblank str}]}`. `update` carries exactly one proposal for the original stem; `split` carries at least two distinct fresh successor stems, never the original; `escalate` carries no tickets. Unknown actions or malformed combinations follow the Driver's bounded schema re-prompt loop. `chupa/rework.py` stamps the reply into one `ReworkOrder` derived from the existing `Artifact`, adding `stem`, integer `attempt`, `action`, and `tickets`; inherited `artifact_schema_version`, `produced_by_spec_version`, and `produced_at_sha` retain their existing meanings, with the SHA read from the supplied workspace's HEAD. This is one composite artifact, not a new Outcome or verdict-keyed artifact family. Success returns existing `StageResult(outcome: ok, artifact: ReworkOrder)`; failures retain the existing outcome vocabulary and paved findings. No new OUTBOX filename or KNOWN-artifact registration is introduced by construction.

  Ticket proposals use the existing closed frontmatter and body grammar. An update preserves the original `source` (`human`, `seed`, or `box:<class>`), `state: confirmed`, and starting `agent_tier` and `agent_effort` (each `low | medium | high | max`); a split inherits those values. Other content may change only to realize the rework order's narrowed or divided original goal. No escalation metadata enters frontmatter. Successor stems pass `stem_findings` and must be absent from both the repository's ticket directories and journal identities; proposals have no self-dependency or cycle, and a split successor must not depend on the superseded original. Validate every proposal with `validate_ticket` and review each separately through existing `review_ticket` before accepting the order. For sibling dependencies, use a disposable proposal tree containing all proposed successors and the original repository material required by validation/rendering; fresh-stem collision checks still read the original repository and journal. This tree is validation material only and never publishes a ticket or changes main. A snag feeds findings back; an RMA returns a paved failure for the existing failure spine, never an unreviewed ticket or automatic retry around the refusal. Construction returns reviewed proposals without editing ticket files, committing ticket-plane output, or retiring the original.

  `chupa/rework.py` owns `REWORK_ORDER = "rework_order"` and `SUPERSEDES = "supersedes"`. Emit one `EventType.SIGNAL` per accepted order with envelope `ticket: <original stem>`, `key: null`, body `{signal: rework_order, attempt: int, action: update | split | escalate}`; failed validation/review emits no accepted-order signal. The supersedes writer is a separate post-publication operation: after the lock-owning caller has committed every reviewed successor, append under the original stem, with `key: null`, `{signal: supersedes, successors: list[str]}`. Successors are nonempty, sorted, unique, and exclude the original. No map is emitted for update, escalation, or failed successor publication. Repeating the same map is a no-op; a conflicting replacement, self-edge, or transitive cycle refuses with a paved finding. The journal is the authority, never a side file or new frontmatter key. Map readers use envelope `ticket` as the old stem, resolve nested maps transitively, satisfy an original dependency only when every leaf successor is settled (`merged` or `already_satisfied`, matching existing `drain.SETTLED`), and propagate a killed (`rejected`) or `abandoned` leaf back to its superseded ancestors. Ordinary retryable failures remain unsettled, not dead; read latest `state_transition` body `to` by envelope `ticket` through existing `last_states`. These state records retain their existing writers. These are dormant reusable folds; construction does not change dispatch or the existing dead-dependency producer.
- **Observable:** `specs/rework.md` has `llm_surface: rework`, `consumes: snag-list`, `emits: rework-order`, `gates: [ticket_schema, requisition_review]`, starting `tier: high`, `effort: high`, and `version: "1.0"`, plus the existing five required prose sections. Render ticket, findings, conflict context, and re-prompt findings only through the existing spec renderer's data blocks and bound; all are untrusted evidence. Invoke the stage through `Driver.run` with surface `rework`, the caller's effective capability and time budget, and existing injected seams. Update produces a revised ticket proposal; split produces independently buildable reviewed successors and exposes post-publication supersession; escalation recommends the existing deterministic ladder without choosing or writing a rung. The failure-spine owner alone later consumes that recommendation through `next_rung` and the existing retry `cap_consumed` record (`cap`, `ticket_sha`, optional `rung: {tier, effort}`); Rework itself writes neither caps nor terminals.

  A conflict handoff is consumed only after admission has returned, aborted any unfinished rebase, and released its serial admission boundary. Rework sees the conflicted paths and original findings and preserves the invalidated-approval requirement: later implementation must pass Check and fresh Review before re-admission. It performs no conflict-only micro-rework, branch repair, squash, or reuse of the former approval. Both the transitive CLI import closure and the admission path remain free of Rework calls. Until `rework-activation`, production diagnosis `split` still routes to the Reject queue and the bootstrap drain's inline admission is unchanged.
- **Tests:** `tests/test_rework.py::test_update_order_is_reviewed_without_ticket_mutation` proves the single-original-stem proposal, preserved starting frontmatter, real grammar/feasibility paths, and no ticket writes. `test_split_order_requires_fresh_buildable_successors` proves distinct fresh stems, inherited frontmatter, sibling dependency validation in the disposable tree, dependency closure, and per-successor review; `test_rework_refuses_invalid_or_unreviewed_orders` covers unknown actions, cardinality, extra fields, identity collisions, invalid tickets, snag re-prompts, RMA, and no accepted-order/map signal on refusal. `test_escalate_order_does_not_edit_capability_or_draw_caps` proves an empty proposal list and unchanged frontmatter, rung history, and cap counts. `test_rework_spec_render_and_driver` pins the spec lint, deterministic fixture render, quoted payload delimiters, render-bound refusal before a model call, Driver schema re-prompts, artifact provenance, existing outcomes/cost, and exact accepted-order signal. `test_conflict_handoff_consumed_after_admission_unwinds` drives the real dormant queue's unresolved-conflict return and then Rework with a fake LLM, asserting abort and slot release precede the call, context matches the handoff, approval stays invalidated, and main/branch are untouched. `test_supersedes_record_after_publication_is_idempotent` proves exact journal shape, publication-before-map, no map after failed publication or non-split orders, replay without duplication, and conflicting/self/cyclic-map refusal. `test_supersedes_dependency_folds` covers nested all-successors settlement, an unsettled or retryable-failure successor, and a rejected/abandoned leaf propagating to original dependents. `test_rework_is_dormant` uses the `19.I` transitive CLI import-closure scan recognizing both import idioms and proves the queue never calls Rework inline; activation must migrate this assertion. Verification runs `uv run pytest tests/test_rework.py tests/test_mergequeue.py` with the latter unchanged as a preservation suite; existing failure-spine tests continue to pin split-to-Reject routing until activation.

### 19.P3.thresh-runtime Dormant flat-subscription provider thresholds

- **Owner:** `chupa/thresh.py` owns per-provider slot admission, FIFO cap waits, the breaker writer and journal fold, and the pre-call availability result. `chupa/providers.py` owns the dormant CLI failure classifier and creation of existing `ProviderCallError` records. `chupa/config.py` retains ownership of config validation: `Limits.concurrency` already parses as a required strict positive integer, and `CircuitBreaker.k` and `cooldown_minutes` already parse with defaults `3` and `10`; preserve these definitions rather than adding a second parser. Construction exercises the components directly with injected `Clock`, `Sleep`, journal, and provider-call/effect callbacks. Dormant pre-call selection skips open breakers as specified below; production wiring, shared session lifetime, quota Timers, and ordered failure-driven failover after an executed failure belong to `19.P4`'s `provider-cooldown-failover`; this construction changes no existing caller or constructor signature.
- **Records:** Read the configured provider names, each provider's `kind: cli` and `limits.concurrency`, the ordered route candidates and optional model override, and `circuit_breaker: {k: positive int, cooldown_minutes: positive int}`. Preserve `limits.est_cost_per_call_usd` and `quota_window_minutes`, existing model inheritance, placeholder refusal, and config's `kind: api` refusal. The caller supplies resolved existing `Served` records (`provider`, `model`) in route order, the owning nullable ticket, the existing run-scoped LLM effect key, and a nonnegative projected cap-wait duration in seconds for the first configured candidate (the primary) only. That estimate never governs a later candidate's queue. `SPILL_WAIT_SECONDS = 60` is an engine constant owned by `chupa/thresh.py`, never config. Admission returns the selected `Served` and nonnegative `waited_seconds`; an unavailable route returns a typed pre-call refusal naming its providers and the earliest breaker deadline, with a paved road to wait for that deadline or repair the configured route. The refusal also carries nonnegative `waited_seconds`, zero before any queue wait. This is not a new `Outcome`, terminal, cap draw, or model call.

  Slot counts and FIFO queues are session-local memory, shared across surfaces for a provider, never stored in a counter file. `chupa/thresh.py` alone writes `EventType.SIGNAL` with `key: null`, envelope `ticket` equal to the caller's ticket, and body `{signal: provider_cap_wait, provider: str, call_key: str, started_at: aware-UTC ISO timestamp, waited_seconds: nonnegative number, disposition: admitted | cancelled | unavailable}` once when each queued wait ends: `admitted` on reservation, `cancelled` on caller cancellation, or `unavailable` when the head's breaker recheck fails, before route reselection. Each record names the provider whose queue was left and retains the caller's ticket and call key. `PROVIDER_CAP_WAIT = "provider_cap_wait"` belongs to that module. Measure only time queued at the concurrency cap; immediate admission emits no wait record. Admission and refusal return the sum of this call's queue-wait records' durations, including waits ended by `unavailable`; each record measures its own queue episode from `started_at`. They expose the amount a later production caller excludes from the ticket and watchdog budgets; construction does not change those budgets' current owners.

  `chupa/thresh.py` also owns `PROVIDER_CALL_OUTCOME = "provider_call_outcome"` and its one signal writer: envelope `ticket` is the caller's ticket, `key: null`, body `{signal: provider_call_outcome, provider: str, call_key: str, failure_class: null | rate_limited | quota_exhausted | outage | auth_error | model_error | unclassified, open_until: null | aware-UTC ISO timestamp}`. Null failure means a successful executed call; null deadline means this result did not open the breaker. Write once per actually executed call, never for an effect replay, a cap wait, cancellation, setup refusal, or unavailable route. An `outage` or `unclassified` result advances that provider's consecutive breaker-failure streak; success or any other class resets it. The Kth consecutive counted failure records `open_until` at the injected completion clock plus `cooldown_minutes`. The journal fold reconstructs streaks and open deadlines independently by provider; no side file is authoritative. An open provider cannot admit a new call before its deadline; at equality it becomes available with a fresh streak, without an operator release or a new Timer. Already admitted calls finish normally; an older in-flight completion cannot shorten an outstanding open deadline. Journal the opening result before any subsequent selection acts on it. Quota cooldown Timer records retain their later Phase 4 owner.

  The classifier consumes exit code, the already scrubbed stderr tail (existing maximum `2000` characters), and an adapter-parsed failure message, including failed CLI events on exit zero; successful output is never classification input. Its closed result vocabulary is the six failure classes above, with unknown failures explicitly `unclassified`. Case-insensitive literal markers are evaluated in this order: the adapter's existing `AUTH_MARKERS` -> `auth_error`; `quota exhausted`, `usage limit reached`, `out of extra usage` -> `quota_exhausted`; `rate limit`, `too many requests` -> `rate_limited`; `service unavailable`, `internal server error`, `stream disconnected`, `at capacity` -> `outage`; `model unavailable`, `model not found`, `model is not supported` -> `model_error`; otherwise `unclassified`. Preserve each adapter's existing `LOGIN_ROAD` for authentication. Classified errors retain `ProviderCallError.provider`, `rc`, `stderr_tail`, `failure_class`, and `paved_road`; non-auth roads name the provider and advise waiting/retrying for rate/quota/outage or fixing the route for a model error. `unclassified` retains exit and scrubbed diagnostic evidence but has no finding road, so the existing Driver's finding mapping yields no Finding. The Driver remains the sole exception-to-Finding mapper and the failure spine remains the sole infra-cap and terminal writer. No new frontmatter, artifact, event type, USD ceiling, token bucket, or provider dependency is introduced; existing Effects and adapter owners retain cost capture and redaction.
- **Observable:** Admission reserves a provider slot BEFORE invoking the supplied effect callback. Counts never exceed that provider's cap and independent providers do not block one another. Selection first skips open breakers in configured route order and selects the first closed candidate, preserving its supplied `Served` model. A closed breaker means available even at a full cap. If the primary is open, admit the selected later candidate when it has a free slot; otherwise wait FIFO on that candidate, regardless of the primary's projected wait and without spilling onward. If the primary is closed but full, spill to the first later configured candidate that has a free slot and a closed breaker only when the primary's supplied projected wait is strictly greater than `60` seconds; otherwise wait FIFO on the primary. Exactly `60` seconds waits. A free slot for new selection also requires no earlier queued waiter. When a waiter reaches the head and a slot can be reserved, recheck that provider's breaker before reservation. If it is open, remove the waiter without taking a slot, write its `unavailable` wait record, and repeat the same pre-call selection over the original route with the original primary estimate. A later closed candidate can admit or queue FIFO under those rules; if every candidate is open, return the typed pre-call refusal. Do not wait in the old queue for breaker expiry. Cancelled and unavailable waiters leave no slot or queue leak; reselection that queues again joins the new queue's tail. Release reservations on success, exception, and cancellation. Cap-pressure selection happens before a call; a failed executed call is returned to the caller without an inline retry or migration to another provider. Only when every candidate's breaker is open, on initial selection or waiter reselection, return the pre-call refusal without running an effect or spending a cap. Advancing injected time to expiry releases that refusal.

  This is dormant construction under `19.I`: `chupa/thresh.py` stays outside the transitive CLI import closure; classifier operations added inside the already-reachable provider module have no production caller. Existing `ProviderLLM.call`, `resolve`, adapter invocation, preflight, write grants, and abort behavior remain unchanged. Direct tests wrap real dormant admission around existing Effects and scripted provider operations, proving selection precedes effect intent and that replay performs no provider operation or breaker-result write. No production drought park, quota hold, alert, Suggestion Box message, or failure-spine retry is activated here. The later provider activation fences and migrates both dormancy assertions and threads the shared payload and wait accounting through the production callers.
- **Tests:** `tests/test_thresh.py` names `test_per_provider_concurrency_caps` (boundary, independent providers, shared surfaces, reservation before effect intent); `test_cap_wait_is_fifo_and_journaled` (multiple waiters, exact signal and returned duration); `test_cap_wait_rechecks_open_breaker_before_admission` (breaker opens while queued, head recheck before reservation, exactly one `unavailable` record before reselection, later candidate free or full, all-open refusal with accumulated wait, repeated waits summed, FIFO tail on requeue, cancellation after reselection, no effect or slot leak on refusal); `test_cap_wait_cancellation_and_call_unwind_release_slots` (queued cancellation and all admitted unwind paths); `test_spill_requires_available_candidate_and_wait_over_sixty_seconds` (below/equal/above threshold, route order, full or open alternate, open primary with a later closed candidate free or full, original primary estimate ignored for the later candidate, no bypass of earlier waiters); `test_breaker_counts_only_consecutive_outage_and_unclassified` (K boundary, success and other-class resets, provider isolation); `test_breaker_rebuilds_from_journal_and_releases_at_deadline` (fresh instance, before/equal/after expiry, exact opening record, older in-flight completion); `test_open_route_refuses_without_effect_or_cap_draw` (initial and post-wait all-open refusal only, a closed full candidate queues instead of refusing, no invocation, cost, cap draw, or terminal, paved refusal and automatic expiry release); `test_effect_replay_does_not_record_another_provider_outcome`; and `test_thresh_is_dormant` (the `19.I` transitive CLI import-closure scan, both import idioms, proven to fail when reachable). All timing advances injected time, never wall-clock sleeps.

  `tests/test_providers.py` adds `test_cli_failure_classifier_closed_vocabulary_and_precedence` (every declared marker for both adapters, mixed markers, unknown diagnostics); `test_cli_failure_classifier_handles_exit_zero_error_events` (Claude error result and Codex failed turn, while successful output never classifies); `test_classified_error_preserves_scrubbed_evidence_and_login_road` (config-to-redactor path, exact error fields, adapter login roads, classified non-auth roads and no unclassified finding road); and `test_cli_failure_classifier_is_dormant` (production CLI composition never calls the new classifier, with a discriminating probe that fails when wired). Existing provider tests preserve first-candidate routing, inherited/pinned models, auth handling, cost floors, preflight, stdin prompts, key isolation, surface grants, and abort. Run `uv run pytest tests/test_thresh.py tests/test_providers.py tests/test_config.py tests/test_driver.py`; the last two are unchanged preservation suites, including required positive concurrency and existing breaker defaults. No test change outside the row's fence is required by construction.

### 19.P3.dispatch-admission-boundary Dormant daemon dispatch task ownership

- **Owner:** `chupa/daemon.py` owns `DaemonAdmission`, the dormant single-flight boundary around an injected `chupa.runner.Dispatch`. Its async `dispatch(ticket)` operation accepts the selected `Ticket`, owns the task executing that callback, and awaits its completion. `chupa/scheduler.py` retains eligibility, priority/age ordering, pending-ticket removal, and completed-but-unmerged backpressure; this boundary does not select tickets. Existing runner, stage, and merge owners retain pipeline execution, failure handling, durable accounting, and merge admission. Construction changes only `chupa/daemon.py` and `tests/test_daemon_admission.py`; production composition is deferred to `scheduler-activation`.
- **Records:** The input is the existing parsed `Ticket`, passed unchanged to the injected `Dispatch` (`Callable[[Ticket], Awaitable[str]]`). The callback's terminal string is returned unchanged; exceptions and cancellation propagate to the caller. The boundary's `active` ticket and `task` (`asyncio.Task[str]`) are memory-only ownership references, both `None` when idle. Acquire one serial slot before creating the task and retain it until the callback has fully unwound; publish both references for the active dispatch and clear both before releasing the slot. Waiting callers own no callback task. No new journal event, signal, body key, frontmatter value, artifact, config key, or engine constant is introduced. Existing `running` transitions and retry-cap draws remain with their dispatch-accounting writers in `chupa/runner.py` and `chupa/drain.py`; non-ok terminals remain runner-owned, and merged terminals remain merge-owned. This wrapper writes none of them and does not retry, translate a failure into a terminal, or duplicate admission accounting.
- **Observable:** Direct component tests exercise real `DaemonAdmission` with an injected async dispatch callback. Concurrent calls cannot overlap callbacks; a waiting request neither interrupts nor replaces the active ticket. Construction creates no task until explicitly dispatched. Each admitted call invokes the callback exactly once and returns its result only after completion. Success, exception, and cancellation all finish callback cleanup, clear ownership references, and release the slot so a subsequent dispatch can proceed. Cancelling a waiting caller never invokes its callback or disturbs the active task; cancelling the active dispatch cancels and awaits its owned callback before another dispatch starts. No detached worker survives the dispatch that owns it.

  Dormancy is behavioral under `19.I`: production CLI `run` and `drain` continue using their existing pipeline callback without constructing or calling this boundary. Before the production-composition harness exists, test the real CLI composition root with the existing injectable pipeline seam and a raising probe on `DaemonAdmission.dispatch`; the probe must fail the test if the new seam is wired. Also pin the absence of `chupa.daemon` from the transitive CLI import closure, recognizing both import idioms. `scheduler-activation` fences and migrates these assertions when it wires the boundary. Config snapshots, background-consumer ownership, pause, kill, daemon merge routing, and the continuous `serve` loop belong to their later registry rows.
- **Tests:** `tests/test_daemon_admission.py` names `test_admission_is_idle_until_dispatch` (no callback or task at construction, idle references); `test_dispatch_owns_task_and_returns_terminal` (same ticket, exactly one callback, observable active task, unchanged terminal and cleared references); `test_concurrent_dispatch_is_single_flight` (blocked first callback, waiting second call, no overlap or preemption); `test_dispatch_exception_unwinds_and_releases_slot` (original exception propagates, cleanup completes, next dispatch succeeds); `test_cancelled_waiter_never_dispatches` (active task unaffected, no callback for the cancelled waiter); `test_active_cancellation_awaits_cleanup_before_release` (callback cleanup held behind an injected barrier, no second callback until cleanup completes, cancellation propagates, no live owned task); and `test_daemon_admission_is_dormant` (real CLI `run` and `drain` composition with the raising probe, plus the `19.I` transitive import-closure scan proven to fail when reachable). Synchronize with injected callbacks and asyncio barriers, never wall-clock sleeps or real-model calls. Verification runs `uv run pytest tests/test_daemon_admission.py tests/test_scheduler.py tests/test_cli.py tests/test_drain.py`; the last three are unchanged preservation suites. No existing public signature or production caller changes during construction.

### 19.P3.dispatch-config-snapshot Dormant per-dispatch immutable configuration

- **Owner:** `chupa/config.py` owns `snapshot_config(config)`, a detached, recursively immutable `Config` snapshot preserving existing field-attribute access. `chupa/daemon.py` owns `snapshot_dispatch(load, bind)`, a dormant adapter returning the existing `chupa.runner.Dispatch`. Its injected zero-argument `load` returns the current validated `Config`; its injected `bind(snapshot)` returns the ticket callback for that snapshot. Compose this adapter as the callback of `DaemonAdmission`, so capture happens inside its serial slot, not while a ticket waits. No new module is introduced. The existing loader remains the sole parser and validator; `DaemonAdmission` retains task ownership, single-flight ordering, and cleanup. Construction changes only the row's `chupa/daemon.py`, `chupa/config.py`, and `tests/test_daemon_config.py`; production wiring belongs to `scheduler-activation`.
- **Records:** A snapshot contains every field of the supplied `Config`, including nested defaults and unset optional values, with the same keys and values as `config.model_dump(mode="python")`. Nested model records retain their field-attribute access but refuse assignment; dictionaries become read-only mappings, lists become tuples recursively, and scalar values, `Path` values, and `None` retain their values. No mutable container or model is shared with the source. Top-level replacement, nested record replacement, mapping insertion/deletion, and sequence mutation are refused; a shallow copy or a frozen outer model with mutable children is insufficient. Read provider names, auth environment-variable names, models and limits, ordered routing candidates, review triggers and severities, merge strategies, scheduler limits, caps, and every other existing config field without selecting a subset or adding defaults. Preserve path resolution, list order, schema handshake, explicit-null refusal, unknown-key refusal, reference checks, and the current `kind: api` refusal by using `load_config` before capture, never reparsing or revalidating the immutable representation. The snapshot helper is the sole constructor of the view; the dispatch adapter owns its per-call lifetime. No config key, frontmatter value, engine constant, journal event, signal, body key, artifact, snapshot identifier, or durable writer is added.
- **Observable:** Each explicitly invoked adapted dispatch calls `load` once, captures once, calls `bind` once with that snapshot, and awaits the resulting callback once with the original `Ticket`. It returns the callback's terminal string unchanged. A running callback retains the same snapshot for its entire lifetime: later source-model mutation, nested-container mutation, or a config-file edit cannot change it. The next admitted dispatch loads afresh and observes valid edits, including ceiling, routing, and severity changes. A waiting dispatch captures only after the preceding callback fully unwinds. A load or capture failure propagates before binding or invoking the ticket callback; there is no cached fallback to the previous valid config. Binding failures, callback exceptions, and cancellation propagate through `DaemonAdmission` without leaking ownership or preventing the next dispatch. This adapter writes no dispatch accounting, retries, terminals, or diagnostics.

  Construction is dormant under `19.I`: production CLI `run` and `drain` keep their existing composition and do not call `snapshot_dispatch` or `snapshot_config`. Test the real CLI composition root with its existing injected pipeline seam and raising probes on the new operations; prove the probes fail when the operations are wired. The daemon remains absent from the transitive CLI import closure, recognizing both import idioms. Preserve `load_config`'s return type and existing public signatures, including `DaemonAdmission.dispatch(ticket)` and `Dispatch = Callable[[Ticket], Awaitable[str]]`. This row does not globally freeze the mutable config models, add a watcher, change the bootstrap drain, or activate daemon composition. The later scheduler activation owns production use and migration of dormancy assertions.
- **Tests:** `tests/test_daemon_config.py` names `test_snapshot_preserves_all_validated_config_values` (recursive comparison with the complete Python-mode dump, resolved paths, defaults, unset optionals, and sequence order); `test_snapshot_is_recursively_immutable_and_detached` (top-level and nested assignment, mapping insertion/deletion, sequence mutation, and mutations of the original models and containers); `test_dispatch_captures_once_and_keeps_snapshot_until_completion` (one load/capture/bind/callback, original ticket, unchanged terminal, config-file and source edits during a blocked callback); `test_next_dispatch_observes_valid_config_edits` (ceiling, route, and severity changes through the real loader); `test_waiting_dispatch_captures_after_admission` (two calls through real `DaemonAdmission`, injected barriers, second load only after first cleanup); `test_invalid_reload_never_binds_or_uses_stale_config` (missing file, invalid YAML, explicit null, invalid schema, and valid recovery on the following dispatch); `test_snapshot_dispatch_unwinds_failures_and_cancellation` (load, bind, and callback errors, active and waiting cancellation, cleared ownership and successful subsequent dispatch); and `test_config_snapshot_is_dormant` (real CLI `run` and `drain`, discriminating raising probes, and the transitive import-closure scan). All callbacks and waits use injected seams and asyncio barriers, never real-model calls or wall-clock sleeps. Verification runs `uv run pytest tests/test_daemon_config.py tests/test_daemon_admission.py tests/test_config.py tests/test_cli.py tests/test_drain.py`; the last four are unchanged preservation suites, so construction requires no signature or caller migration outside the row's fence.

### 19.P3.scheduler-activation Production daemon core composition

- **Owner:** `chupa/daemon.py` owns the production daemon-core factory composing the existing `Scheduler`, `Watcher`, `DaemonAdmission`, and `snapshot_dispatch`; `chupa/__main__.py` owns its composition-root binding of checkout, config loader, pipeline binding, and injected seams. The in-process harness in `tests/test_daemon_composition.py` calls that production root builder, never constructs a parallel test graph. `chupa/scheduler.py` retains selection and backpressure; `chupa/watcher.py` retains debounce and parsing; `chupa/config.py` retains validation and snapshot construction. `chupa/runner.py` owns factoring production provider preparation into `async prepare_pipeline(checkout) -> Dispatch`, shared by the synchronous bootstrap `pipeline` and the admitted daemon callback; it retains `bind(checkout, llm)` as the sole Driver/StageContext binding. `chupa/runner.py`, `chupa/stages.py`, `chupa/driver.py`, and `chupa/providers.py` own accepting `ConfigSnapshot` in their config consumers; `chupa/redact.py`, `chupa/gates.py`, and `chupa/caps.py` own the corresponding downstream read-only consumers. No new engine module is introduced. This core is the graph later extended and driven by `serve-activation`; bootstrap `run` and `drain` retain their existing dispatch, retry accounting, reconciliation, lock lifetime, and inline merge admission.
- **Records:** Compose one shared journal and one instance of each core component. Wire `Watcher.publish` to `Scheduler.update`, `Watcher.remove` to `Scheduler.remove`, and `Scheduler.dispatch` to `DaemonAdmission.dispatch`, whose callback is `snapshot_dispatch(load, bind)`. The root supplies ticket reads returning text or `None` for a removed file, change delivery carrying ticket stems, the committed plan for `parse_ticket`, `Clock`, `Sleep`, and a debounce duration in seconds; preserve the watcher's existing injected interface without adding a watcher library or config key. The dispatch loader uses the same explicit `--config` path or checkout-relative `config.yaml` and the existing `load_config`; binding receives the complete detached immutable snapshot and returns the existing `Dispatch = Callable[[Ticket], Awaitable[str]]`. The root's synchronous `bind(snapshot)` creates a dispatch-local `Checkout` with `dataclasses.replace(checkout, config=snapshot)`, retaining its repo, env, executor, Git, journal, filesystem, clock, and sleep seams. Its returned async callback awaits `runner.prepare_pipeline` on that checkout, then awaits the resulting Dispatch with the original Ticket. The daemon root supplies a preparation seam `Callable[[Checkout], Awaitable[Dispatch]]` defaulting to `runner.prepare_pipeline`; its default binding uses this production preparation, never the synchronous `runner.pipeline` inside an admitted task. All dispatch-local pipeline consumers receive that same snapshot; snapshot capture occurs inside admission, once per admitted call, never at graph construction or while waiting.

  `Checkout.config`, `StageContext.config`, `Driver.from_config`, and provider config consumers explicitly accept `Config | ConfigSnapshot`. Provider routing, `Served.provider`, adapter construction, child-environment filtering, redactor construction, merge severity, and cap/rung reads also accept the snapshot's nested immutable records (including provider and caps records), mappings, and tuples. They read existing field attributes and sequence order without mutation, conversion back to `Config`, revalidation, or a second snapshot. `load_config` continues returning validated mutable `Config`; its schema and the existing `ConfigSnapshot` representation are unchanged.

  `runner.prepare_pipeline` constructs `ProviderLLM` from that checkout's config, awaits its existing `preflight()`, raises the existing `runner.Refusal` with the provider diagnostics and paved road on nonempty problems, and only on success calls `runner.bind` to construct Driver and StageContext. In daemon dispatch this all runs inside `DaemonAdmission`'s owned task after capture and before `drive` or any ticket-stage work; it runs once for each admitted snapshot, never at graph construction or while waiting. No admitted code calls `asyncio.run`. The existing synchronous `runner.pipeline(checkout) -> Dispatch` delegates to this same preparation using `asyncio.run` only at the outer bootstrap CLI binding before its run/drain event loop, preserving `Pipeline = Callable[[Checkout], Dispatch]`, startup preflight refusal, and the existing injected pipeline seam. There is one provider/preflight/stage preparation implementation, with no cached provider or stale preflight result reused across daemon admissions.

  Parsed `Ticket` records retain `stem`, `frontmatter.state` (`draft`, `confirmed`, `rejected`, `merged`), `frontmatter.priority` (`P0` through `P3`), and tuple `depends`. Selection reuses `drain.SETTLED` (`merged`, `already_satisfied`), `last_states`, `reject_queue`, `authored_at`, and `sort_key`: read `state_transition` body `to`, the existing Reject-routing/verdict records, and the first `ticket_intake` signal's envelope `ts`; order by priority, known age before missing age, oldest timestamp, then stem. The caller supplies current journal-derived quarantine/drought sets, completed-but-unmerged count, and existing `scheduler.max_unmerged` (default `2`), with selection re-reading them before each dispatch. Their policy owners remain unchanged. Watcher parse failures keep their sole writer, `chupa/watcher.py`, and constant `WATCHER_PARSE_FAILURE = "watcher_parse_failure"`: `EventType.SIGNAL`, envelope `ticket: <stem>`, `key: null`, body `{signal: watcher_parse_failure, path: tickets/<stem>/ticket.md, reason: <nonempty diagnostic>}`. Pending/cache/active/task references are memory-only. The callback's terminal is unchanged at admission; `Scheduler.dispatch_next` retains its selected-`Ticket` or `None` result. Runner, drain, intake, and merge remain the sole writers of their existing accounting, intake, and terminal records. Activation adds no event type, signal, body key, frontmatter value, artifact, config key, or engine constant.
- **Observable:** The daemon, scheduler, and watcher become reachable in the transitive production CLI import closure, recognizing both import idioms. Calling the production root builder constructs the real graph without dispatching host work, loading a per-dispatch snapshot, or starting background consumers. Explicitly drive its watcher and scheduler through injected delivery and callbacks: debounced valid updates alter the next selection, an invalid edit preserves the last-known-good record and position, an invalid new stem stays absent, and removal drops pending work. A P0 edit never preempts the active ticket. Concurrent selections remain single-flight through callback cleanup; success, exception, and cancellation clear ownership before another dispatch, and a cancelled waiter never invokes a callback. Running work keeps its snapshot despite later config edits; the next admission observes valid edits, and invalid reload fails before binding without a stale fallback. Existing eligibility, hold release, age ordering, and backpressure behavior is preserved through this graph.

  Migrate `test_scheduler_and_watcher_are_dormant` in `tests/test_scheduler.py` and the daemon-absence import-closure assertions in `test_daemon_admission_is_dormant` and `test_config_snapshot_is_dormant` to positive production reachability and graph evidence; keep every component behavior assertion and the bootstrap CLI preservation checks. The activation seed adds `tests/test_daemon_config.py` to its fence and Context under `19.L` ACTIVATION/CONTRADICTED TESTS because the predecessor pins daemon import absence there. Under `19.L` CALLER CLOSURE it also adds `chupa/runner.py`, `chupa/stages.py`, `chupa/driver.py`, `chupa/providers.py`, `chupa/redact.py`, `chupa/gates.py`, and `chupa/caps.py` for the production binding and snapshot-consumer changes, plus every direct caller found by the authoring-time grep; these existing paths enter Context/on-demand under its size rule, and each addition is recorded in the seeding test. The registry fence is the floor. Background task ownership, control, pause/kill, merge-queue/Rework activation, daemon admission routing, and the continuous `serve` verb remain their named later rows' contracts.
- **Tests:** `tests/test_daemon_composition.py` adds `test_production_core_uses_real_snapshot_pipeline` (default production preparation, real ProviderLLM, adapters, Driver and StageContext, snapshot identity at each config consumer, provider routing, secret filtering/redaction, severity and caps, original Ticket and terminal); `test_production_core_awaits_preflight_inside_admission` (running event loop, capture before provider construction and one awaited preflight before bind/stage work, no preparation at construction or for a waiting/cancelled waiter, fresh preparation after a config edit); and `test_production_core_unwinds_preflight_refusal_and_cancellation` (nonempty problems retain the existing Refusal and paved road, raised errors and cancellation during preflight propagate, no stage work starts, ownership clears after cleanup, and a subsequent valid admission succeeds). These tests retain the real preparation, preflight, and bind functions and use scripted process/filesystem seams for provider version/model probes and calls; stop before host work. Scripted pipeline callbacks alone are insufficient evidence for these three obligations. Existing bootstrap CLI/provider tests preserve preflight-before-run/refusal behavior and the synchronous injected Pipeline contract. `tests/test_daemon_composition.py` also names `test_production_root_builds_daemon_core_without_running_work` (real root factory, shared journal and correctly connected components, no callback, snapshot load, or background task at construction); `test_production_core_dispatches_through_admission_and_snapshot` (original ticket reaches the existing pipeline binding exactly once, one immutable snapshot shared by its consumers, terminal preserved at admission); `test_production_core_reprioritizes_without_preemption` (blocked active callback, debounced edit and new P0, next pick changes only after cleanup); `test_production_core_preserves_last_good_and_removes_tickets` (invalid existing/new input, exact parse-failure record, valid recovery and removal); `test_production_core_preserves_eligibility_order_and_backpressure` (settled dependencies, Reject/quarantine/drought holds and release, distinct intake ages, missing age, priority/stem tiebreaks, count at and below the limit); `test_production_core_reloads_config_only_after_admission` (waiting request captures after cleanup, active snapshot unchanged, next valid edit observed, invalid reload never binds); `test_production_core_unwinds_errors_and_cancellation` (callback/load/bind failures, active and waiting cancellation, no surviving owned task, subsequent dispatch succeeds); and `test_daemon_core_is_reachable_from_cli` (positive transitive closure, with a removed import edge proving the assertion discriminates). Preserve the predecessor component tests while migrating their negative closure assertions. Verification runs `uv run pytest tests/test_daemon_composition.py tests/test_scheduler.py tests/test_daemon_admission.py tests/test_daemon_config.py tests/test_config.py tests/test_cli.py tests/test_drain.py tests/test_providers.py tests/test_driver.py tests/test_stages.py tests/test_gates.py tests/test_caps.py`; existing suites outside the activation fence run unchanged as preservation suites. Use injected seams and asyncio barriers, with scripted pipeline callbacks for scheduler-only cases, never real-model calls, host work, or wall-clock waits. Later activations extend this same production harness.

### 19.P3.merge-queue-activation Production pipeline queue composition

- **Owner:** `chupa/merge.py` owns the production pipeline admission factory `compose_pipeline(ctx, *, escalate) -> MergeQueue`, returning the existing `MergeQueue` constructed with the pipeline's `StageContext` and the required keyword consumer unchanged. `chupa/mergequeue.py` retains sole ownership of serial admission, conflict resolution, integration checks, and queue state; no admission algorithm is copied into the factory. `chupa/runner.py` owns the existing production provider/stage binding (`pipeline` and `bind`) and inline call from `drive` to `merge`; `bind(checkout, llm)` builds a synchronous no-op escalation consumer and calls `compose_pipeline(ctx, escalate=consumer)` once after constructing its context, then returns the existing dispatch lambda. `pipeline(checkout)` and `bind(checkout, llm)` keep their signatures and returned `Dispatch` contract; `Checkout` gains no escalation field. The factory returns the queue directly; no callable attribute or StageContext/driver slot is added. No new engine module is introduced. Under `19.L` caller/composition closure, the activation seed adds `chupa/runner.py` to the registry fence floor and its Context/on-demand partition, and records that addition in its seeding test. The registry's `tests/test_daemon_composition.py` is the production harness landed by scheduler activation; extend that harness rather than creating a parallel graph.
- **Records:** Reuse the existing `StageContext` and its config, Git, filesystem, process exec, driver, clock, journal, Effects, and spool; the composed queue shares these exact instances with the pipeline. Preserve `MergeQueue(ctx, *, escalate)` and its injected synchronous `Callable[[Event], None]` consumer. Production's no-op returns `None` without writing, notifying, or otherwise handling the event: `MergeQueue._signal` already journals it before invoking the consumer. Until `19.P4`'s `notify-transport`, section 13's escalations remain journaled signals only. Direct factory callers must supply `escalate`; there is no default consumer. `admission-holds-activation` later adds the separate shared control inbox at every direct factory caller, as its registry row requires; the no-op escalation consumer neither constructs nor replaces that inbox. A freshly composed queue has `pending: {}`, `active: None`, `paused: false`, and `red_stems: []`; these remain memory-only. `offer(ticket, *, attempt)` stores the parsed `Ticket` and integer attempt by stem; `process()` returns `list[StageResult | ConflictHandoff]`. Ordinary results remain `ok` with `Admission` or `gate_failed` with no artifact; `Admission` retains `stem`, real `commit`, original `reviewed_sha`, and existing provenance. `ConflictHandoff` retains `stem`, `reviewed_sha`, sorted unique `conflicted_paths`, `findings`, and `approval_invalidated: true`; it is an in-memory result, never a new stage outcome or durable artifact.

  Activation introduces no event, signal, body key, frontmatter value, config key, or constant. Existing queue writers remain unchanged: `CONFLICT_FACTS = "merge_conflict_facts"` with `{kind, conflicted_paths, resolving_rung: none | mechanical | rework, strategy_paths, integration_red_paths}`; `RED_STREAK = "merge_red_streak"` with `{kind, stems, limit: 3}` and `RED_STREAK_LIMIT = 3`; `TREE_MISMATCH = "merge_tree_mismatch"` with `{kind, checked_tree, main_tree}`. Each is an `EventType.SIGNAL` with envelope ticket stem and null key, written only when the queue actually processes an admission. `merge.write_squash` remains the sole squash Effect and merged-transition writer (`merge/<stem>/<attempt>`, body `{to: merged, commit, reviewed_sha}`); composition writes none of these records.
- **Observable:** The queue becomes reachable through the production CLI's transitive import closure and is constructed by the production pipeline factory, using the actual pipeline context and supplied escalation consumer. Factory construction offers no ticket, performs no git operation or verification, emits no journal record, invokes no escalation, and starts no background task. The production harness wraps the real `compose_pipeline` at `runner.bind`'s call site, delegates with the exact context and consumer received, captures its returned queue, and returns that same queue to the caller. It exercises the real binding (directly with a scripted LLM or through the daemon's injected `prepare` seam), then explicitly offers/processes a reviewed candidate on the captured queue; it never substitutes a fake factory or constructs a second test-only queue. `build_daemon_core` and `prepare` continue handing out only the dispatch callable; capture occurs when preparation reaches `bind`, not when the daemon core is built. Direct harness exercise proves composition, not daemon routing.

  Bootstrap `run` and `drain` continue calling the existing inline `merge(ctx, ticket, *, attempt)` and retain its restore/rebase/regate, pinned approval, seed safety, base-red attribution, squash trailers, merged transition, and retirement behavior. They neither offer to nor process the composed queue and acquire no daemon holds. Daemon-mode routing belongs to `serve-merge-admission`; owned background consumption belongs to `background-consumers`; Rework handoff consumption belongs to `rework-activation`; identity-bound red-streak/tree-hash release belongs to `admission-holds-activation`. Composition does not activate these behaviors or notification transport. Migrate `tests/test_mergequeue.py::test_merge_queue_is_dormant` from its negative import-closure assertion to positive production reachability, preserving its inline-admission/no-conflict-facts proof; migrate any queue-absence assertion in the production composition harness in the same change.
- **Tests:** `tests/test_daemon_composition.py` adds named obligations `test_production_pipeline_composes_merge_queue` (real production binding, shared context/seams, fresh queue state, captured factory return, and identity of the required consumer passed by `bind`; invoking that production no-op returns `None` with no effect, while a direct factory call preserves a supplied recording consumer unchanged); `test_merge_queue_composition_has_no_side_effects` (no offer/process, git/verification, event, escalation, or background task at construction); and `test_composed_merge_queue_admits_reviewed_candidate` (queue captured from the real factory call during that binding, real disposable git repo, existing integration path, real commit/original reviewed SHA, one merged transition, retirement). In `tests/test_mergequeue.py`, replace the dormancy assertion with `test_merge_queue_is_reachable_from_production`, with a removed import edge proving the positive scan discriminates, and retain the inline/no-conflict-facts behavior as `test_inline_admission_does_not_use_merge_queue`. `tests/test_merge.py` adds `test_bootstrap_pipeline_keeps_inline_admission`, driving the production binding with a scripted LLM and proving queue offer/process are never invoked. Keep all existing queue algorithm and inline merge tests green, particularly approval carry, seed safety, base-red policy, lifted ticket-plane restore, and conflict abort. Verification runs `uv run pytest tests/test_merge.py tests/test_mergequeue.py tests/test_daemon_composition.py tests/test_cli.py tests/test_drain.py`; the last two are unchanged preservation suites. Use injected seams and disposable repos, never real-model calls or wall-clock waits.

### 19.P3.rework-activation Production Rework consumption and ticket-plane application

- **Owner:** `chupa/daemon.py` owns the production consumer of returned conflict handoffs and the binding of reviewed Rework application to the lock-owning ticket-plane writer. `chupa/rework.py` retains the existing stage, proposal validation, order schema, supersedes writer, and dependency folds; `chupa/mergequeue.py` retains admission and handoff ownership and never invokes Rework inline. `chupa/runner.py` owns failure dispatch, terminal ordering, retirement, and dead-dependency production; `chupa/drain.py` and `chupa/scheduler.py` own their existing eligibility projections. No new engine module is introduced. Extend the production graph and in-process harness from `scheduler-activation` and `merge-queue-activation`, never a parallel test graph. The seed depends on `merge-queue-activation` and adds `chupa/runner.py`, `chupa/drain.py`, `chupa/scheduler.py`, `tests/test_ladder.py`, `tests/test_drain.py`, `tests/test_scheduler.py`, and `tests/test_reject_queue.py`, and `tests/test_diagnose.py` to the registry fence floor under `19.L` caller/contradicted-test closure; partition existing files into Context/on-demand at authoring. Re-grep direct callers and dormancy assertions against the merged authoring head and record any further mechanically required fence additions in the seeding test.
- **Records:** Consume the existing `ConflictHandoff` with `{stem: str, reviewed_sha: str, conflicted_paths: list[str], findings: list[Finding], approval_invalidated: true}` returned by `MergeQueue.process`. Its paths are sorted and unique; its stem must match the original parsed ticket. Supply that ticket's committed text, findings, run sequence as `attempt`, workspace, effective tier/effort, and stuck budget to the existing `rework` operation. Read starting capability and source from committed ticket frontmatter, not the runner's effective-capability copy. Rework proposals preserve `source`, `state: confirmed`, starting `agent_tier`, and starting `agent_effort`; runtime escalation remains journal-derived. Reuse `ReworkOrder`: existing artifact provenance plus `{stem: nonblank str, attempt: nonnegative int, action: update | split | escalate, tickets: list[{stem: nonblank str, ticket: nonblank str}]}`. Update has exactly one original-stem proposal, split at least two distinct fresh successors excluding the original, and escalate none. Existing grammar and per-proposal `requisition_review` approval are mandatory before publication; no order is accepted on invalid proposals, snag exhaustion, or RMA.

  `chupa/rework.py` remains the sole writer of `REWORK_ORDER = "rework_order"`: `EventType.SIGNAL`, envelope `ticket: <original stem>`, `key: null`, body `{signal: rework_order, attempt: int, action: update | split | escalate}`. Accepted orders alone emit it; acceptance is not publication. The lock-owning consumer commits only the exact reviewed `tickets/<stem>/ticket.md` proposals through the section 10 ticket-plane Git/Effects lane, never a code branch or the human intake path that would stamp a new machine successor `source: human`. Update replaces only the original ticket; split publishes every successor before calling existing `record_supersedes`. That operation alone writes `SUPERSEDES = "supersedes"`: `EventType.SIGNAL`, original-stem envelope, null key, body `{signal: supersedes, successors: list[str]}`. Successors are sorted, unique, nonempty, exclude the original, and must all match committed reviewed bytes. Failed or partial publication writes no map and does not retire the original; replay of the same map is a no-op, while conflicting replacement, self-edge, or transitive cycle refuses with the existing paved finding. Update and escalation write no map. No new artifact filename, KNOWN registration, event type, signal, frontmatter field, config key, or constant is introduced.

  Read supersession through existing `supersedes_maps`, `successor_leaves`, `settled_dependencies`, and `dead_dependencies`, using journal envelope `ticket` and latest `state_transition` body `to`. An original dependency settles only when every transitive leaf is `merged` or `already_satisfied`; retryable non-ok leaves remain unsettled, and `rejected` or `abandoned` leaves propagate death to superseded ancestors. Apply these predicates at bootstrap admission/eligibility, daemon selection, and dead-dependency production without rewriting dependents' ticket files or treating the original's retirement as successor failure. Existing runner retirement owns the `rejected` stamp/transition; existing dead-dependency production retains `{signal: dead_dependency, dead: <stem>}` and its `failure_report` writer. Publish the map before retiring the split original through the existing reject mutation, so dependents resolve through successors. Reuse that mutation under the held writer lock; never call the lock-acquiring `verdict` entrypoint from inside it. Write the producing run terminal before the separate retirement transition; a run cannot retain a latest non-ok state after it has been retired. Escalation stays with `next_rung` and the existing retry `cap_consumed` record `{cap: retry, ticket_sha: <committed ticket blob SHA>, rung: {tier, effort}}`; Rework never selects a rung, writes a cap, resets lineage budgets, or emits a run terminal. Existing failure-spine writers retain diagnosis, cap, and terminal custody.
- **Observable:** Production Rework becomes reachable and is consumed by the same writer that holds the engine lock. A returned conflict handoff is processed only after `MergeQueue.process` has unwound, aborted the unfinished rebase, cleared its active candidate, and released the serial admission slot; ticket-plane application never reacquires a lock already held by the caller. Pass the original findings and conflict context unchanged to Rework. Invalidated approval stays invalidated: update or split goes through fresh Implement, Check, and Review before any later code admission, never conflict-only branch repair or reuse of the old approval. A handoff is not a merge, and its consumer neither squashes nor journals `to: merged`.

  Route production diagnosis `split` to reviewed Rework instead of the pre-activation Reject-queue fallback while budget remains; spent caps, explicit reject/abandon-human, and exhausted escalation keep their existing fail-closed paths. Activate the section 11.3 mechanical over-bound-render split route without a diagnosis call or cap draw for prompt-size arithmetic. Publication, requeue, and terminal handling retain harvest -> dispatch -> journal -> wipe ordering and one terminal per producing run; a failed Rework or publication returns paved failure through that handler, never silent success or an unreviewed rewrite. Updated content is observed on the next fresh dispatch; published successors enter the ordinary ticket rescan/selection path. A successfully superseded original is not dispatched again, and its existing dependents wait for every successor leaf. Keep bootstrap `run`/`drain` inline code admission unchanged. This activation composes and explicitly exercises handoff consumption; owned background queue tasks and continuous daemon admission still belong to `background-consumers` and `serve-merge-admission`.

  Migrate only the import-absence part of `tests/test_rework.py::test_rework_is_dormant` to positive production reachability, retaining the behavioral prohibition on inline admission calls. Migrate the `split` case of `tests/test_ladder.py::test_reject_verdicts_auto_keep_once_and_draw_down` to positive reviewed splitting; its reject and abandon-human cases remain. Migrate the over-bound case of `tests/test_diagnose.py::test_missing_workspace_and_no_call_short_circuits` to require Rework while still prohibiting diagnosis; workspace-gone and budget-exceeded remain mechanical short-circuits. Preserve every existing stage, proposal, map, queue, retry, and inline-admission invariant while extending their production consumers.
- **Tests:** `tests/test_daemon_composition.py` adds `test_production_composes_rework_without_running_it` (shared context, journal, seams, and writer; graph construction makes no model call, ticket write, event, or task); `test_production_consumes_conflict_handoff_after_unwind` (handoff from the composed real queue, abort/slot release before the model call, exact context, no inline Rework, no squash or merged transition, fresh approval required); `test_production_applies_reviewed_rework_orders` (update replaces exact reviewed original bytes, split commits every exact reviewed successor before map and retirement, escalation changes no ticket); and `test_production_refuses_failed_rework_publication` (validation/review refusal, failed/partial commit, no map/retirement or false success, paved handler result, map replay without duplication). `tests/test_rework.py` replaces the negative closure assertion with `test_rework_is_reachable_from_production`, proven to fail with the production import edge removed, and retains `test_admission_never_invokes_rework_inline`; existing proposal/frontmatter, provenance, bounded-render, timeout-cleanup, publication/map, and dependency-fold tests remain green.

  `tests/test_ladder.py` adds `test_split_dispatches_reviewed_rework` (real production failure path, one terminal after application, fresh successors, no split Reject marker, unchanged reject/abandon/exhausted paths) and `test_rework_escalation_preserves_starting_capability_and_caps` (effective capability passed to the call, starting frontmatter retained, existing deterministic rung and retry draw, no budget reset). `tests/test_drain.py` adds `test_rework_update_reenters_on_fresh_content`, `test_rework_split_successors_release_original_dependents` (ordinary rescan, original retired, all leaves required including nested maps and `already_satisfied`, retryable leaf does not settle), and `test_render_over_bound_dispatches_rework_without_diagnosis` (mechanical route, no diagnosis/cap draw, no zero-attempt Reject). `tests/test_scheduler.py::test_superseded_dependencies_require_all_successor_leaves` proves the same dependency rule through production selection. `tests/test_reject_queue.py::test_dead_dependencies_resolve_through_supersedes` covers rejected/abandoned leaf propagation, no premature death on mapped-original retirement, and idempotent existing dead-dependency records. `tests/test_diagnose.py::test_render_over_bound_calls_rework_but_not_diagnosis` migrates the old no-model-call assertion and proves the mechanical split route uses the production consumer without diagnosis or cap draws, including a refusal with a paved road when no usable workspace is available. Verification runs `uv run pytest tests/test_rework.py tests/test_daemon_composition.py tests/test_mergequeue.py tests/test_ladder.py tests/test_drain.py tests/test_scheduler.py tests/test_reject_queue.py tests/test_merge.py tests/test_diagnose.py tests/test_cli.py`; `tests/test_merge.py` and `tests/test_cli.py` are unchanged preservation suites. Use scripted LLMs, disposable repositories, and injected seams, never real-model calls or wall-clock waits.

### 19.P3.background-consumers Owned dormant background consumers

- **Owner:** `chupa/daemon.py` owns `DaemonTasks`, the lifetime boundary for the watcher, merge-queue, and Suggestion Box consumer tasks. No new engine module is introduced. Supply three named zero-argument async callbacks (`watcher`, `merge_queue`, `box_consumer`) at construction and explicitly await `run()` to drive them. Existing `Watcher.run(changes)` owns change consumption, debounce tasks, parsing, and watcher cleanup; `MergeQueue.process()` owns serial admission and its results; `triage_pass(checkout, llm)` owns sequential box triage and Author routing. Inject callbacks around those existing operations, never copy their algorithms or change their signatures. Construction changes only `chupa/daemon.py` and the new `tests/test_daemon_tasks.py`; production task startup and continuous consumer loops belong to `serve-activation`.
- **Records:** The three callbacks return awaitables; their return values are not dispatch terminals or merge results to reinterpret. `DaemonTasks` owns one task per callback during an explicit run and exposes those ownership references as a memory-only `tasks` tuple, empty before startup and after complete cleanup. Create callbacks' awaitables inside the owned tasks, so construction invokes nothing and a synchronous callback failure follows the same cleanup path as an async failure. Invoke each callback exactly once per run; never restart a failed consumer automatically. Refuse an overlapping run before invoking any callback, with the paved road to finish or cancel and await the existing run first. A later explicit run may begin only after all previous tasks have unwound.

  Existing watcher, queue, triage, Author, intake, runner, and merge writers retain their records and decisions. The task owner reads no ticket frontmatter, config field, journal event, or artifact and writes none. It adds no signal, body key, event type, frontmatter value, config key, engine constant, durable task registry, retry counter, or failure-report writer. A consumer's exception or cancellation is propagated to the awaiting caller, never converted into success, a run terminal, a retry, or a box message. The owner does not discard or manufacture queue outcomes: handling results from `MergeQueue.process()` remains the supplied consumer's responsibility.
- **Observable:** An explicit run starts all three consumers concurrently and remains their lifetime owner. Normal completion awaits all three; one consumer finishing does not cancel the others. A consumer failure cancels the remaining consumers and awaits every task's cleanup before propagating failure. Cancelling the owning run likewise cancels and awaits every consumer before clearing references or allowing a subsequent run. Repeated cancellation during cleanup cannot detach a consumer or let another run overlap that cleanup. Watcher cleanup includes its outstanding debounce tasks through the existing `Watcher.run` unwind; merge admission cleanup remains queue-owned. No task exception is left unobserved and no owned task survives the run. Use asyncio synchronization and injected consumer callbacks; timing and external effects remain behind their existing seams. No polling interval, filesystem watcher dependency, task restart policy, or additional loop is introduced here.

  Construction is dormant under `19.I`: production graph construction and CLI `run`/`drain` neither construct nor run `DaemonTasks`, and bootstrap box consumption remains operator-driven. Test the existing production composition harness once available; before that harness exists, use the real CLI composition root and its injectable pipeline seam. A raising construction/run probe must discriminate deliberate test wiring from the unchanged production path. Do not require `chupa.daemon` to be absent from the import closure: scheduler activation makes that module reachable before this row. `serve-activation` fences `tests/test_daemon_tasks.py` and migrates this behavioral dormancy assertion when it starts the owned consumers.
- **Tests:** `tests/test_daemon_tasks.py` names `test_construction_is_idle` (no callback, awaitable, or task, empty ownership tuple); `test_run_owns_three_concurrent_consumers` (all three enter before barriers release, exactly one invocation each, normal completion waits for every consumer, cleared references); `test_consumer_failure_cancels_and_awaits_siblings` (synchronous and async failures, blocked sibling cleanup, failure propagation only after unwind, exceptions observed); `test_run_cancellation_awaits_all_cleanup` (active consumers cancelled, repeated owner cancellation, no live task or premature reference clearing); `test_watcher_debounce_tasks_do_not_outlive_owner` (real injected `Watcher.run`, outstanding debounce waits cancelled and awaited); `test_overlapping_run_is_refused_until_cleanup_finishes` (no duplicate callbacks, paved refusal, success/failure/cancellation followed by a clean explicit run); `test_merge_results_remain_consumer_owned` (the supplied callback receives and handles queue results without owner interpretation); and `test_background_consumers_are_dormant` (production harness or real CLI `run`/`drain`, no background startup or box triage, probes proven to fail under deliberate wiring). Verification runs `uv run pytest tests/test_daemon_tasks.py tests/test_daemon_composition.py tests/test_scheduler.py tests/test_mergequeue.py tests/test_triage.py tests/test_cli.py tests/test_drain.py` once the predecessor composition harness has merged; all except the new task test file are unchanged preservation suites. Use injected seams, scripted callbacks, and asyncio barriers, never real-model calls or wall-clock waits.

### 19.P3.control-inbox Dormant durable identity-bound control inbox

- **Owner:** The new `chupa/control.py` owns typed control requests, publication, validation, journal-derived consumption, and lifecycle/hold identity matching. `chupa/daemon.py` owns the dormant consumer boundary supplied with the lock-holder's journal, lifecycle identity, current hold identities, and an injected application callback; it never opens a second journal writer. `chupa/seams.py` owns the filesystem publication primitive, in both `FileSystem` and `LocalFileSystem`. Use the existing `Journal.append` write-ahead fsync and `EventType.SIGNAL`, not a second decision store. Construction introduces no CLI routing, dispatch checkpoint, kill executor, worker task, polling loop, or production lifecycle startup; those belong to the named later activation rows.
- **Records:** Requests live under `<state_dir>/control/inbox/<request_id>.json`. A request is a closed JSON object `{request_id: str, lifecycle_id: str, verb: pause | resume | kill, hold_id: str | null}`. Request and lifecycle ids are nonempty opaque identities; request ids used as filenames are restricted to ASCII letters, digits, underscore, and hyphen, with no path separators. Filename and body identity must agree. The publisher supplies a fresh request id and the target lifecycle id; publication never generates or retargets an engine lifecycle. Each running engine's owner supplies a restart-unique lifecycle id, distinct from a checkout id, PID, ticket stem, or reused lockfile instance id. `pause` and `kill` require null `hold_id`; `resume` requires the exact nonempty identity of the hold it releases. Each pause or admission/storm hold has its own identity, never merely its kind. A resume without a hold identity is refused with the paved road to read the current hold and submit a new request. These files have no ticket frontmatter and change no ticket schema or configuration.

  Publication is a new filesystem-seam operation `publish(path, data: bytes) -> None`: create a private unique temporary file in the destination directory, write all bytes and fsync it, atomically publish the complete file without overwriting an existing destination, and fsync the destination directory before reporting success. Concurrent publishers cannot share a temporary filename. An existing destination raises `FileExistsError`, leaves its bytes unchanged, and requires a new request id; any interrupted private temporary file is never a consumable request. The seam owns directory creation and its durability, temporary cleanup, and every raw filesystem operation needed for publication. Existing `write` and `replace` semantics and callers remain unchanged; overwrite-capable `write` is not an inbox publication path. The CLI-side publisher writes only the request file, never a journal event, decision, or governed state.

  `chupa/control.py` alone owns `CONTROL_DECISION = "control_decision"`. The lock-holding consumer is its sole writer: one `EventType.SIGNAL` with envelope `ticket: null`, `key: null`, body `{kind: control_decision, request_id: str, lifecycle_id: str | null, verb: pause | resume | kill | null, hold_id: str | null, decision: accepted | stale | rejected, reason: str}`. A valid request retains its exact identities and verb; malformed input uses the safe filename identity and nulls for unvalidated fields, with a nonempty diagnostic reason. Unknown keys, wrong types, missing fields, unknown verbs, invalid identities, and incompatible hold fields are rejected before application; diagnostics give the valid request shape instead of echoing arbitrary input bytes. A valid request targeting another lifecycle, or a resume targeting an absent/different hold, is stale and mutates nothing. Accepted decisions name the matching lifecycle and, for resume, matching hold. Decisions are keyed logically by request id in the journal fold, not by ticket/run Effect keys. Reusing an already-decided request id never creates another decision or application, even with changed request bytes.

  Consume complete request files serially in deterministic filename order; journal append order is the decision order. Journal the decision durably before invoking any application callback, then derive consumed identities from that journal on every reconstruction. Keep decided request files as inert input; deletion or a separate processed marker is not the exactly-once authority. If journaling fails, application does not run and the request remains undecided. Recovery after a durable accepted decision and before application reconstructs the current lifecycle's governed projection from accepted decisions in journal order; it does not append another decision. Applying that projection must be idempotent, so repeated folds/reconstruction cannot repeat an external action. Old-lifecycle decisions remain recorded but cannot apply to a new lifecycle. An arbitrary callback with unreplayable side effects is not an exactly-once implementation; later kill construction owns abort completion and its applied record. Construction exercises application through an injected idempotent projection, without activating those later effects.
- **Observable:** Explicit publication and consumption exercise the real dormant component through injected filesystem, clock, journal, identity, and application seams. Every request gets at most one durable decision; accepted requests affect only their bound lifecycle and hold, after that decision is visible. Repeated scans, reconstructed consumers, duplicated publication, and interruption before/after publication or decision cannot lose a successfully published undecided request, expose partial JSON, overwrite a request, duplicate a decision, or release a later hold. Accepted pause decisions establish a pause whose identity is that request id; only a matching resume releases it. Fold decisions in journal order so the latest accepted pause/resume governs that projection; a previously filed resume never releases a subsequently created hold. A stale kill never invokes the application seam. This construction does not spend dispatch/retry accounting or implement kill execution.

  Dormancy under `19.I` is behavioral: production graph construction and CLI `run`/`drain` neither construct nor consume the inbox or publish a lifecycle. Test the production composition harness once it exists, otherwise the real CLI composition root with its injectable pipeline seam. Raising construction/consumption probes must fail under deliberate wiring and remain untouched by ordinary production calls. Do not require `chupa.daemon` import absence, since scheduler activation makes that module reachable. `pause-resume-activation`, the kill rows, admission/storm hold activations, and `serve-activation` own their production bindings and migrate only the dormancy assertions they invalidate. The pre-daemon direct locked control behavior remains outside this construction.
- **Tests:** `tests/test_control.py` names `test_request_shape_and_identity_fail_closed` (every schema/type/verb/filename refusal and paved road); `test_publication_is_durable_and_never_overwrites` (real disposable filesystem, file/directory fsync ordering, existing destination and concurrent publishers, complete visibility, preserved bytes); `test_publication_crash_points` (failure before file fsync, before/after atomic publication, and before directory fsync, ignored private temporaries, no success before durability); `test_publisher_never_writes_journal` (request-only publication); `test_decision_precedes_application` (callback reads its durable decision, journal failure prevents mutation); `test_request_is_decided_once` (repeated scans, consumer reconstruction, duplicate id with altered bytes, retained files); `test_decision_crash_reconstructs_projection` (crash before append and after durable acceptance/before application, no duplicate decision or external action); `test_lifecycle_identity_never_retargets` (restart-unique lifecycle, stale pause/resume/kill and prior decisions mutate nothing); `test_resume_matches_only_its_hold` (absent hold, premature resume, replaced hold, matching pause/admission/storm identities); `test_latest_accepted_pause_resume_wins` (ordered journal fold and repeated recovery); and `test_control_inbox_is_dormant` (production harness or real CLI `run`/`drain`, calibrated probes, no lifecycle, decision, control mutation, or consumer task). Verification runs `uv run pytest tests/test_control.py tests/test_cli.py tests/test_drain.py`, plus `tests/test_daemon_composition.py` unchanged once merged. All invariants are exercised through the production dormant component and seams, with disposable directories and synchronization barriers, never real-model calls or wall-clock waits.

### 19.P3.dispatch-pause-boundary Dormant pause checkpoint before dispatch accounting

- **Owner:** `chupa/daemon.py` owns the dormant pause checkpoint at `DaemonAdmission.dispatch`; `chupa/drain.py` owns its placement before the drain's durable offer accounting. No new engine module is introduced. Both accept an injected zero-argument async `before_dispatch` callback returning `None`, optional at construction/entry so existing callers retain their behavior. The callback consumes pending control requests and awaits release while the current lifecycle's pause projection is held; supply it explicitly to exercise this construction. The existing control inbox owns decisions and identity matching; this boundary neither duplicates that algorithm nor opens another journal writer. Production callback binding and CLI pause/resume routing belong to `pause-resume-activation`.
- **Records:** Reuse the control inbox's accepted `CONTROL_DECISION` records and lifecycle/hold projection from `19.P3.control-inbox`: accepted pause establishes the request id as hold identity; only accepted resume for that lifecycle and that exact hold releases it. Stale/rejected decisions mutate nothing; accepted decisions are folded in journal order, latest-wins. The supplied callback retains ownership of consumption and wakeup; the boundary stores no independent durable pause flag, decision, processed marker, or hold identity. A paused wait must continue to permit consumption of resume requests, using injected async wakeup rather than a wall-clock polling loop.

  Preserve the existing drain writers and shapes. `caps.consume` writes `EventType.CAP_CONSUMED` with envelope `ticket: <stem>`, `key: null`, body `{cap: retry, ticket_sha: <committed ticket blob SHA>}`, optionally `rung: {tier: <existing tier>, effort: <existing effort>}` from the prior terminal. `_Drain._run_one` writes `EventType.STATE_TRANSITION` with envelope ticket stem, null key, body `{to: running, ticket_sha: <same SHA>}`. A normal re-offer draws exactly one retry unit before `running`; a fresh offer, changed-ticket premise re-offer, or released `spec_gap_hold` draws none, preserving the existing lineage-scoped cap fold. `_Drain._select`'s machine keep remains the existing signal `{signal: reject_verdict, verdict: keep, actor: machine}` for the stem. Intake, reconcile, runner, and merge retain their writers; the boundary adds no event type, signal, body key, frontmatter value, artifact, configuration key, or constant.
- **Observable:** Await the checkpoint before ANY durable accounting for the next offer, including selection's machine keep, retry-cap consumption, the `running` transition, and dispatch-owned effects. In the drain, a wrapper around the final dispatch callback is too late: the checkpoint must precede `_select`'s offer mutations and `_run_one`'s accounting. Re-read eligibility and journal-derived budget after a paused wait; never dispatch a stale selection or draw against a stale budget. Complete awaited offer preparation before the final checkpoint and perform retry/running accounting without an intervening await after it returns. While held, no retry draw, running transition, snapshot capture, or dispatch callback starts. Cancellation or failure of the checkpoint propagates before those actions and leaves no fabricated terminal or spent retry unit.

  In `DaemonAdmission`, await the checkpoint inside the single-flight slot before creating the owned invocation task or binding its dispatch snapshot. An in-flight dispatch finishes normally when a later pause arrives; pause governs the next offer and never preempts active work. Cancelled waiters never dispatch, ownership clears after cleanup, and successful release preserves the original Ticket, callback terminal, retry-before-running order, and existing cap exceptions. Construction is behaviorally dormant under `19.I`: ordinary production graph construction and CLI `run`/`drain` supply no pause callback, consume no controls, and acquire no pause hold. Calibrate raising checkpoint probes through explicit wiring and prove ordinary production paths leave them untouched. `pause-resume-activation` migrates this dormancy assertion; kill execution, worker stop, admission/storm holds, and continuous serve remain their later rows' contracts.
- **Tests:** `tests/test_daemon_pause.py` names `test_pause_checkpoint_precedes_dispatch_and_snapshot` (single-flight checkpoint, no invocation or snapshot while held, original ticket and terminal after release); `test_pause_does_not_preempt_active_dispatch` (active work finishes, next offer waits); `test_only_matching_resume_releases_pause` (real dormant inbox, premature/stale/wrong-hold resumes, latest accepted pause/resume, durable decision visible before release); `test_checkpoint_failure_and_cancellation_leave_no_dispatch` (blocked and queued cancellation, raised failure, cleared ownership and later successful offer); and `test_dispatch_pause_boundary_is_dormant` (production composition harness or real CLI root, calibrated probes, no production checkpoint/control consumption). `tests/test_drain.py` adds `test_pause_precedes_fresh_offer_accounting`, `test_pause_precedes_retry_cap_draw`, `test_pause_precedes_machine_keep`, `test_pause_release_rechecks_eligibility_and_budget`, `test_pause_checkpoint_failure_spends_no_retry`, and `test_pause_preserves_free_premise_and_spec_gap_reoffers`, exercising the real drain with an explicitly supplied checkpoint and journal assertions before and after release. Verify exact retry/running ordering, optional rung preservation, no effects while held, and unchanged cap lineage and free re-offer cases. Run `uv run pytest tests/test_daemon_pause.py tests/test_drain.py tests/test_daemon_admission.py tests/test_daemon_config.py tests/test_control.py tests/test_daemon_composition.py`; the last four suites are unchanged preservation suites once their predecessor machinery merges. Use injected seams, disposable directories, scripted dispatch, and asyncio barriers, never real-model calls or wall-clock waits.

### 19.P3.pause-resume-activation Production pause/resume control routing

- **Owner:** `chupa/__main__.py` owns the `pause` and `resume` CLI routing and the shared control composition factory. `chupa/control.py` retains ownership of request publication, validation, exactly-once decisions, and lifecycle/hold matching; `chupa/daemon.py` owns the production consumer and pause projection; `chupa/drain.py` binds that consumer to the lock-owning drain and the predecessor's `before_dispatch` checkpoint. No new module is introduced. Activate the machinery specified by `control-inbox` and `dispatch-pause-boundary`, rather than implementing another inbox or pause algorithm. At authoring, read those merged predecessors' public operations and every direct caller before choosing the activation wiring. The current pre-activation CLI has no `pause`/`resume` parser entries: section 20's direct locked behavior is the required contract, not evidence of an already implemented verb.
- **Records:** Reuse `<state_dir>/control/inbox/<request_id>.json` and its closed request shape `{request_id: str, lifecycle_id: str, verb: pause | resume | kill, hold_id: str | null}` from `control-inbox`. This activation publishes only `pause` and `resume`: pause has null `hold_id`; resume binds the exact current pause request id. The CLI publisher supplies a fresh filename-safe request id and reads the target engine's restart-unique lifecycle identity and current pause identity; it never substitutes a PID, checkout id, or lockfile diagnostic `instance_id`. A missing/unavailable lifecycle or a resume with no current pause is refused with the paved road to read the running engine's current control identity and submit a new request. Never queue an unbound resume for a future hold.

  The lock-holding engine publishes its lifecycle and current pause projection under `<state_dir>/control/active.json`, a closed JSON object `{lifecycle_id: nonempty str, hold_id: nonempty str | null}`. `chupa/control.py` owns this discovery record's filesystem-seam writer; it is a projection, never decision authority. Publish only after acquiring the writer lock, refresh only after the corresponding durable decision, and retire before releasing the lock, including cancellation, failure, and self-upgrade handoff. A replacement engine generates a fresh lifecycle; stale discovery bytes or a publication racing replacement can at most produce a stale request, never retarget it. A publisher must establish lock contention before using discovery; missing or malformed discovery while the lock is held refuses rather than writing a journal signal or guessing an identity. Do not change the lockfile diagnostic schema or use it as a liveness protocol.

  Retain `CONTROL_DECISION = "control_decision"` and its sole writer, the lock-holding consumer: `EventType.SIGNAL`, null ticket/key, body `{kind: control_decision, request_id: str, lifecycle_id: str | null, verb: pause | resume | kill | null, hold_id: str | null, decision: accepted | stale | rejected, reason: str}`. Decisions precede projection mutation and discovery refresh; accepted pause establishes its request id as hold identity, accepted matching resume clears it, and stale/rejected requests change nothing. Fold accepted decisions in journal order, latest-wins, and recover without duplicate decisions or application. Retain decided inbox files as inert input. No new journal event type, decision signal, cap, frontmatter field, or configuration key is introduced. Dispatch accounting keeps the exact predecessor writers and shapes, including retry-before-running and free premise/spec-gap re-offers.
- **Observable:** With an engine holding the lock, CLI pause/resume publish durable requests through the existing no-overwrite publication seam and return without acquiring the engine's writer role, writing the journal, mutating its pause state, or constructing a pipeline. Publication success means submitted, never falsely claims applied. The real drain constructs one consumer using its own journal, filesystem and clock seams, publishes its identity before offers, and supplies its pause checkpoint before all next-offer accounting. The checkpoint consumes pending requests and continues consuming matching resumes while held through an injected async wakeup; an accepted pause must not let the drain report quiescence merely because dispatch is held. Re-read selection and budget after release. Existing in-flight work completes normally; pause never cancels an invocation or suppresses its terminal or merge.

  With no engine running, pause/resume acquire the same writer lock and apply directly under section 20's contract; never leave a request to act on an unrelated later lifecycle. The lock acquisition decides this route, not the existence of discovery bytes. A race losing that acquisition routes through the live inbox only after reading its identity; a missing identity refuses with a retry road. Keep ordinary `run` and bootstrap drain admission, reconciliation, caps, harvest, and self-upgrade ordering unchanged. Migrate the predecessor inbox and pause-checkpoint production-absence assertions to positive routing/consumption evidence, retaining their schema, durability, identity, and ordering assertions. Admission red-streak/tree-hash holds, storm holds, kill execution, owned worker tasks, and continuous `serve` activation remain their later rows' obligations.
- **Tests:** `tests/test_control_cli.py` names `test_live_pause_resume_publish_without_journal_write` (real CLI, held lock, durable exact request identities, no pipeline or second writer, submitted output); `test_resume_requires_current_pause_identity` (no hold, malformed/missing discovery, no guessed or future release, paved refusals); `test_pause_resume_apply_directly_under_lock` (no live engine, direct behavior and no deferred request); and `test_control_routing_lock_and_restart_races` (lock acquisition race, stale discovery/request, lifecycle replacement, no retargeting). `tests/test_daemon_composition.py` names `test_production_composes_one_pause_consumer` (shared seams and journal, graph construction has no decision or task); `test_live_drain_pause_blocks_all_offer_accounting` (real production root, fresh and retry offers, machine keep, snapshot and effects held, no false quiescence); `test_live_drain_resume_rechecks_selection_and_caps` (matching resume, changed eligibility/budget, exact retry/running order and free re-offers); and `test_control_lifecycle_cleanup_on_exit_and_handoff` (fresh identities, retirement on normal exit, failure, cancellation and before child launch).

  `tests/test_daemon_pause.py` replaces `test_dispatch_pause_boundary_is_dormant` with `test_dispatch_pause_boundary_is_active`, preserving active-work completion, cancellation cleanup and wrong-hold/stale/premature resume tests. The seeding ticket also fences `tests/test_control.py`, the predecessor's dormancy-pinning file under `19.L` ACTIVATION, and migrates only `test_control_inbox_is_dormant` to `test_control_inbox_is_active`; the registry fence is a floor. Verification runs `uv run pytest tests/test_daemon_pause.py tests/test_control_cli.py tests/test_daemon_composition.py tests/test_control.py tests/test_drain.py tests/test_cli.py tests/test_daemon_admission.py tests/test_daemon_config.py`; the last four are unchanged preservation suites. Exercise the real composed inbox and drain with disposable repositories, injected seams, scripted dispatch and asyncio barriers, never real-model calls or wall-clock waits. Each routing, identity, durability, accounting and cleanup assertion must fail when its production binding is deliberately removed or misordered.

### 19.P4 Phase 4 -- Reliability and providers

- *Deliverables:* the stuck/spiral watchdog as a staged chain -- the in-flight adapter EVENT STREAM (per-tool-call JSONL events surfaced at the driver/provider boundary to a consumer seam; spool capture, cleanup, and the post-terminal harvest reader unchanged); the NOTIFY transport (section 15 `Notifications.notify(argv)` seam running the config-declared argv command as an Effect with section 6's key domains and conservative re-send reconcile -- the ONE transport section 13 names; its merge IS the production flip for Phase 3's escalation emitters, storm breaker and red streak); the spend-without-progress DETECTOR + hard-timeout wiring (token/cost accumulated from the event stream since the last OBSERVED mutation to a `## Scope fence` path across section 9's three regions -- a tool-call request is never a mutation; a stream reporting no usage charges `limits.est_cost_per_call_usd` at call start; trips at spend exceeding 3x the serving row's per-call basis, an engine constant; ONE run-seq-keyed notification, the stuck alert run-BLIND; process-group kill on stuck); the ACTIVATION flipping EVERY production driver call, review included, to the watched path. Provider cooldown Timers and failover over the CONFIGURED candidates (`providers.py` owns ordered selection and served-identity stamps; `timers.py` + the journal own cooldown state; section 6's one-payload-per-session rule). The reliability battery and its run.
- *Exit reads (committed artifacts only):* every member green in `tickets/reliability-run/reliability-battery-report.json` (schema `ReliabilityBatteryReport` in `chupa/artifacts.py`), member order CLOSED: `classified_quota_exhaustion` (quota classified, cooldown deadline persisted), `all_candidates_cooling_recovery` (ordered candidate exhaustion, the all-cooling hold, the matching `timer_fired` recovery, the recovered served identity), `unclassified_failure_preservation` (an unknown failure stays `unclassified`), each run over the battery's multi-candidate FIXTURE registry and green only when observed equals expected and the member-local journal passes the auditor (emitters: machinery `reliability-battery`, producer `reliability-run`). The spiral soft-band notification (fired once, no auto-kill, its notify intent/completion pair in the run journal) and the hard-timeout group kill are obligations of `watchdog-detector`/`watchdog-activation` and their merged production-composition tests -- the hard-timeout test asserting the killed run is harvested -- read from `watchdog-activation`'s committed passing `checks.json`.

```yaml
# BEGIN_REGISTRY_P4
phase: 4
admissions:
  - [watchdog-event-stream, notify-transport]
  - [watchdog-detector, watchdog-activation]
  - [provider-cooldown-failover]
  - [reliability-battery]
  - [reliability-run]
  - [phase4-exit]
seeds:
  watchdog-event-stream: {cite: [6, 9, 15], fence: [chupa/watchdog.py, chupa/providers.py, chupa/seams.py, tests/test_watchdog.py, tests/test_providers.py],
    does: "Dormant in-flight event callback through the process-exec seam to a watchdog consumer seam."}
  notify-transport: {cite: [6, 13, 15], depends: [watchdog-event-stream], fence: [chupa/notify.py, chupa/config.py, chupa/seams.py, chupa/serve.py, chupa/__main__.py, tests/test_notify.py, tests/test_config.py, tests/test_serve.py],
    does: "Notifications seam, notify config parse, key domains and reconcile; serve reconciles Effect-backed notifications at startup and each poll, pushing storm and red-streak escalations; unset config warns once and stays status-only."}
  watchdog-detector: {cite: [9], fence: [chupa/watchdog.py, chupa/notify.py, tests/test_watchdog.py], does: "Dormant spend-without-progress detector and hard-timeout wiring."}
  watchdog-activation: {cite: [9], depends: [watchdog-detector], fence: [chupa/watchdog.py, chupa/driver.py, chupa/stages.py, chupa/notify.py, chupa/drain.py, chupa/serve.py, chupa/__main__.py, tests/test_watchdog.py, tests/test_watchdog_activation.py, tests/test_daemon_composition.py],
    does: "Every production driver call watched; proves soft-band notify-once and hard-timeout group kill through the production composition."}
  provider-cooldown-failover: {deep: true, cite: [6, 15], fence: [chupa/providers.py, chupa/watchdog.py, chupa/timers.py, chupa/runner.py, chupa/restart.py, chupa/daemon.py, chupa/stages.py, chupa/merge.py, chupa/drain.py, chupa/serve.py, chupa/__main__.py, eval/shakeout/bench.py, eval/daemon_soak.py, tests/test_provider_cooldown_failover.py, tests/test_providers.py, tests/test_restart_timers.py, tests/test_stages.py, tests/test_serve.py, tests/test_merge.py, tests/test_mergequeue.py, tests/test_daemon_composition.py],
    does: "Section 6 cooldown/failover with one registry/cooldown payload and one Timers lifetime per lock-held session, threaded to every provider-client construction site."}
  reliability-battery: {cite: [6], fence: [eval/reliability_battery.py, chupa/artifacts.py, chupa/stages.py, tests/test_reliability_battery.py],
    does: "Fault injection, closed report schema and registration, writer, and runner for the three closed members."}
  reliability-run: {fence: [tickets/reliability-run/reliability-battery-report.json], does: "No code: runs the merged battery once into its OUTBOX."}
  phase4-exit: {exit: true, fence: [tickets, tests/test_phase4_exit.py, tests/test_seeded_phase5_core.py],
    does: "Reads the committed report; authors the 19.P5 core."}
# END_REGISTRY_P4
```

### 19.P5 Phase 5 -- Sidecar + self-improvement (slim)

- *Deliverables:* the retro stage (section 14 count/time/signal triggers, committed retro report + window boundary) WITH its bootstrap-era INVOKER -- the drain itself, because nothing else can fire a retro before cutover (`serve` is daemon-era, the `retro` verb is an operator surface, and no run lane can produce `tickets/retro/<seq>.md`); WITH it the box's tombstone auto-reopen and retro itemization (section 12); the per-surface catch scorecard (the escape column ships in Phase 6), spend/calibration reporting, gate earn/prune reporting, bypass aggregation, and backlog hygiene (section 14's kept core); the status projection (section 13 touchpoint 5); the GO-baseline BINDING READER (section 12); the `retro` verb; `doctor`.
- *Settled contracts:*
  - INVOKER: an UNFORCED due check at the top of every drain dispatch iteration selects a trigger first (outside the failure-capturing block; none due returns with no signal): at least N=25 merged tickets in the window, a window at least M=7 days old, or one signal kind reaching S=5 in the window (per-kind identities exactly: a used non-empty `gate_bypass`; a Rework invocation; a terminal `state_transition` to `gate_failed`; an admission whose conflict facts carry integration-red paths). It runs ONE FORCED retro at quiescence and immediately before any phase-exit ticket dispatches, whenever a merge landed after the latest completed report. It runs in the MAIN checkout under the lock the drain holds, through a hook wired only from the drain entrypoint (default-off for direct `Drain` construction; the self-upgrade child re-wires it). The retro is an `LLMStage` named `retro` emitting a closed local `RetroArtifact` from `specs/retro.md`, run by the existing Driver with the session's shared provider payload; the Driver reaches the hook through a public read-only `Stages.driver` via `Pipeline.stages`, never private attributes or globals, and a missing Driver raises `RetroConstructionError` with a paved road. The hook writes `tickets/retro/<seq>.md` (zero-padded; `retro` is a reserved non-stem directory) and commits it through the ticket-plane Git/Effects seam, effect key `retro/<seq>`, whose completion is the window boundary -- no OUTBOX lift, no KNOWN-artifact registration. A failure after a trigger is selected appends one `signal` keyed `retro-failed/<window-boundary>/<trigger>` (body `{kind: retro_failed, window_boundary, trigger, error_code}`), enqueues ONE deduped `failure_report`, and suppresses every further attempt in that window until a later `retro/<seq>` completion.
  - RETRO -> BOX: one `retro_finding` per proposal carrying `retro_report_key`, `fixed_failure`, `overcorrection_risk`, `proposed_spec_paths`, with box origin `retro-proposal/<retro_report_key>/<proposal_id>` (`proposal_id` = first 16 hex of sha256 over the canonical fields); tombstone re-reports per section 12; authoring a ticket from a `retro_finding` appends one bridge `signal` keyed `retro-ticket/<stem>` (`{kind: retro_ticket_authored, box_id, retro_report_key, ticket_stem}`); at successful admission of a `source: box:retro_finding` ticket changing any `specs/*.md`, merge appends one `signal` keyed `retro-prompt-spec-change/<stem>/<squash-sha>` (`{kind: retro_prompt_spec_change_merged, box_id, retro_report_key, ticket_stem, squash_sha, changed_spec_paths}`); a missing or ambiguous bridge is a hard merge finding.
  - SCORECARD (pure, read-only): the retro window gains ordered `check_observations` `(ticket, code, verdict, bypassed)` from each completed `check/<ticket>/<run>` invoice; `project_scorecard(window)` returns immutable `Scorecard(boundary, merged_ticket_count, spend_usd, tokens, signal_counts, gate_failure_count, surfaces)` with rows `SurfaceScorecardRow(surface, evaluated_tickets, catches, escapes, bypass_count, catch_rate, escape_rate, prune_candidate)` sorted by surface; catches are non-bypassed fails; zero denominators give zero; `prune_candidate` iff at least 25 evaluated tickets with zero catches and zero escapes; escapes stay zero until Phase 6; the report renders a deterministic `## Surface scorecard` table.
  - STATUS: section 13 touchpoint 5; the production caller passes its injected clock, the real HEAD SHA via `Git.rev_parse`, and the real `specs/retro.md` version into the window projection -- no sentinel provenance.
  - BINDING READER: `resolve_baseline(config, events, *, specs_dir) -> BaselineResolution(state, binds)`, never raising, state CLOSED `ABSENT | NO_GO | GO | REVOKED`, selecting the LATEST complete `review_baseline` signal: none is ABSENT; a non-GO verdict is NO_GO; a GO binds only while its recorded identity equals the current registry resolution for every recorded tier on `review` and `author` and its spec-major equals the majors loaded from `specs/review.md` and `specs/author.md`, else REVOKED; empty routing, unresolved placeholders, unknown tiers, malformed fields, unreadable specs, or a torn tail resolve to the supervised side. It is the ONE reader: `chupa/author.py` is its sole starting-state caller, passing `binds` into `policy.starting_state` (the sole starting-state policy), and the Phase 6 supervised-merge hold is its only other consumer.
  - VERBS: `retro` takes the lock and runs the SAME composition as the hook forced; with no merge since the latest report it prints `retro: no merge since the latest completed report` and exits 0; success prints `retro: committed tickets/retro/<seq>.md`, exit 0; a selected run committing nothing prints `retro: no report committed; inspect status and the Suggestion Box`, exit 1; refusals exit 2. `doctor` (`chupa/doctor.py`) checks exactly `venv`, `git`, `config`, `lock`, `journal` in that order, read-only, rendering `doctor: ok|failed` then one `PASS|FAIL <name>: <detail>` per check; any failure exits 2, never a traceback.
- *Exit reads (committed artifacts and merged tests only):* the lexicographically latest committed `tickets/retro/<seq>.md`, committed by the forced pre-exit hook after the latest feature merge, carries a `## Surface scorecard`, numeric spend/tokens, only existing check surfaces, and a zero escape column; every scorecard entry resolves to real journal events and EXISTING stems -- a fabricated or fixture-derived entry is false-green (machinery: `retro-drain-invoker` + `scorecard-reporting`; producer: the forced pre-exit retro). The wired retro-finding -> box -> triage/Author -> prompt-spec-merge chain is re-exercised by merged `tests/test_retro_box.py` with `retro-box-activation`'s committed `checks.json` passing -- the live loop is a daemon-era observation (section 13 touchpoint 7). The binding reader's merged tests prove an injected Phase 1 NO-GO resolves unbound and an injected GO plus a spec-major bump resolves REVOKED, with `baseline-binding-reader`'s `checks.json` passing; no production GO exists before cutover.

```yaml
# BEGIN_REGISTRY_P5
phase: 5
admissions:
  - [retro-drain-invoker]
  - [retro-box-activation]
  - [scorecard-reporting]
  - [status-projection, baseline-binding-reader]
  - [retro-doctor-cli]
  - [phase5-exit]
seeds:
  retro-drain-invoker: {deep: true, cite: [13, 14], fence: [chupa/retro.py, specs/retro.md, tests/test_retro.py, chupa/drain.py, chupa/driver.py, chupa/stages.py, chupa/__main__.py, chupa/box.py, tests/test_drain.py, tests/test_driver.py, tests/test_stages.py, tests/test_box.py],
    does: "INVOKER contract plus the sections 13/19 Exit-read window renderer resolution and driver materialization on the same window-projection seam. Transition-risk preservation: every suite reaching `main([\"drain\"])` through to a merge (re-entry, upgrade, kill, storm, restart, provider, watchdog, pause, control) migrates only an assertion its scenario actually forces, else stays unchanged with the non-firing reason recorded in the seeding test."}
  retro-box-activation: {deep: true, cite: [12], depends: [retro-drain-invoker], fence: [chupa/retro.py, chupa/box.py, chupa/merge.py, chupa/author.py, chupa/triage.py, chupa/policy.py, chupa/stages.py, chupa/runner.py, chupa/daemon.py, chupa/drain.py, chupa/serve.py, chupa/status.py, chupa/__main__.py, tests/test_box.py, tests/test_merge.py, tests/test_author.py, tests/test_triage.py, tests/test_policy.py, tests/test_stages.py, tests/test_daemon_composition.py, tests/test_drain.py, tests/test_serve.py, tests/test_retro_box.py],
    does: "RETRO -> BOX contract; every production Box constructor with journal access receives the journal-backed rereport callback."}
  scorecard-reporting: {cite: [14], fence: [chupa/scorecard.py, tests/test_scorecard.py, chupa/retro.py, tests/test_retro.py], does: "SCORECARD contract; tests/test_retro.py assertions are preserved unchanged."}
  status-projection: {cite: [13], depends: [scorecard-reporting, retro-box-activation], fence: [chupa/status.py, tests/test_status.py, chupa/scorecard.py, tests/test_scorecard.py, chupa/box.py, tests/test_box.py, chupa/retro.py, tests/test_retro.py, chupa/__main__.py, tests/test_cli.py], does: "STATUS contract."}
  baseline-binding-reader: {cite: [12], depends: [retro-box-activation], fence: [chupa/baseline.py, tests/test_baseline.py, chupa/journal.py, chupa/config.py, chupa/policy.py, tests/test_policy.py, chupa/author.py, tests/test_author.py, tests/test_retro_box.py],
    does: "BINDING READER contract, migrating any interim go-binding helper into the one reader."}
  retro-doctor-cli: {cite: [18], fence: [chupa/doctor.py, tests/test_doctor.py, chupa/retro.py, chupa/__main__.py, tests/test_retro.py, tests/test_cli.py], does: "VERBS contract."}
  phase5-exit: {exit: true, fence: [tickets, tests/test_phase5_exit.py, tests/test_seeded_phase6_core.py], does: "Exit reads above; authors the 19.P6 core."}
# END_REGISTRY_P5
```

### 19.P6 Phase 6 -- External hosts + cutover

- *Deliverables:* the host-contract machinery -- the `chupa:core` managed-block renderer and drift classifier in `chupa/hostfiles.py` (section 8; FIRST ADOPTION: a routed CLI's conduct file with ZERO marker-like text gets the block INSERTED with every existing byte kept as project-owned remainder; malformed, partial, or duplicate marker text refuses; chupa's own CLAUDE.md/AGENTS.md are the first case), the `core_drift` gate ACTIVATION (an engine-shipped HARD code joining the merge-time mechanical re-run set), `migrate-config`, and `docs/host-contract.md` (the section 15 schema with a copyable commented `review`/`merge` example, the seam inventory, the report-inbox contract, managed-file ownership, cutover steps; foreign process-state adoption excluded until earned, D10). Host #1 is an OPERATOR-DECLARED input (section 0) -- a build declaring none simply waits at cutover; EVERY build scaffolds the committed fixture host `hosts/fixture/` and runs Phase 6 wiring and exit reads against it -- a host-root config profile, a miniature deterministic app with a replay-runner command, a CLOSED scenario list, bounded version-1 report fixtures, one merge-base regression defect, one machine-introduced escape scenario, and a scripted agent CLI (one more `kind: cli` provider behind the section 6 adapter contract) serving Author/Implement/Review/triage at zero model spend. The report inbox with EVERY loop seam owned (section 12 version-1 NORMATIVE report schema; metadata-first 1 MiB replay-file and 64 KiB log caps; bounded contents COPIED into durable box custody before the message records; the sequential triage consumer owns the runtime ingest caller, the evidence copy into the authored ticket's `evidence/`, and the `kind: bug` authoring path). WITH it the bug gate (`kind: bug`, `## Regression`, the merge-base overlay, section 7) and the scorecard ESCAPE column (triage's bug->range attribution plus the squash-trailer read op in `git.py`). The supervised-merge hold (sections 9, 12). The GO-grade baseline and the exit-receipt machinery. A host-work ticket carries no `Plan contract`.
- *Settled contracts:*
  - DRIFT: one `chupa/providers.py` resolver maps routing to conduct-file paths, shared by the `core` verb and the gate; the gate compares each committed managed block with a fresh branch-version render; the classifier is pure `missing | current | drifted | refused`.
  - MIGRATE-CONFIG: the sole older schema is version 0, identical to version 1 except `schema_version: 0`; the mapping changes only that scalar; the candidate validates through the real loader before one atomic replace with an adjacent backup; current version 1 is a byte-identical no-op; anything else refuses with no write.
  - ESCAPE: the source is a resolved `bug_report`'s `app_commit` (lowercase SHA or `BASE..HEAD`); git accepts only first-parent `HEAD` ancestry with one valid trailer pair; anything else is unattributed; each passed-Check report/ticket/surface counts once.
  - HOLD: durable HELD after merge safety and integration, before main mutation; held stems stop dispatch but keep their worktrees; identity-bound `confirm` releases without a cap keep signal; a moved main rebases and regates; restart reconstructs holds; the bootstrap self-build never holds.
  - GO-GRADE: the Phase 1 spike's set grown to at least 50 planted defects PLUS at least 15 clean (defect-free) fixtures, scored by `eval/harness.py` under a flat per-run cap (engine constant, shipped USD 5.00) for catch rate on planted defects and false-snag rate on clean fixtures; the run applies a per-call ceiling (an optional `LLMRequest` budget passed to a cost-reporting CLI, e.g. Claude `--max-budget-usd`; a provider without cost reporting refuses before spawn when its flat estimate exceeds the remainder), each call receiving the remaining cap. A run that exhausts the cap before scoring every fixture commits its measured PARTIAL report, which resolves `NO_GO` mechanically; an incomplete report can never record GO; a bounded re-run is the paved road. The AUTHOR-GRAPH CHECK runs the harness-local author prompt (NEVER production `specs/author.md`) over a committed fixture problem set into one committed graph artifact the operator judges. `--record-go` ships with this deliverable (the Phase 1 spike records NO-GO mechanically and has no GO mode), is operator-only, and refuses unless the report is complete with catch rate at least 0.85 AND false-snag rate at most 0.15 (engine constants); the operator's Author-graph judgment remains required above those floors. GO and NO-GO are both valid exits; cutover waits at NO-GO. The committed report embeds its verdict signal's journal identity.
  - RECEIPT: `exit-receipt.json` closed schema: per-read verdict, `host_loop_digest` and `baseline_report_digest` (lowercase SHA-256 of the validated `host-loop-report.json` and `review-baseline-report.json` bytes), the GO-grade verdict with its embedded verdict-signal identity, and `schema_version` -- no wall-clock or checkout-dependent field, so it regenerates byte-identical. The verdict is read ONLY from the committed GO-grade report: an incomplete report yields `NO_GO`; a complete one yields the verdict its embedded identity records; `phase6-exit` performs no journal read. `chupa/artifacts.py` owns schemas; `chupa/stages.py` KNOWN_ARTIFACTS validates OUTBOX bytes.
- *Exit reads:* `phase6-exit`'s harness launches `chupa serve` as a supervised SUBPROCESS against the fixture host's profile on a DISPOSABLE checkout -- the SECOND sanctioned pre-cutover `serve`, sized inside its `Time budget` -- in supervised mode (no GO is recordable pre-cutover), the harness PLAYING THE OPERATOR by writing `confirm` requests into the subprocess's control inbox for each draft fixture ticket and held candidate, each journaled with a MACHINE actor (never re-arming caps). Committed `host-loop-report.json` members, in order: at least 3 distinct-run `machine_ticket_merge` with zero engine-plane edits; `report_to_regression_bug_loop` (report -> replay -> regression fixture end to end); `escape_attribution` via the squash trailers (machinery `exit-receipt-machinery`, producer the exit's own harness run). The committed GO-grade report and its embedded verdict identity (machinery `go-grade-machinery`, producer `go-grade-run`). LIVE host reads -- K >= 10 machine-authored merges on host #1 and one real bug loop, counted only from this engine's own journal and provenance stamps -- are the operator's post-cutover acceptance. *Annex, any time after host #1:* a different-stack second host merges M >= 5 tickets with host-config and host-contract fixes only. Fleet is out of scope.

```yaml
# BEGIN_REGISTRY_P6
phase: 6
admissions:
  - [core-renderer, core-drift-classifier]
  - [core-drift-activation, migrate-config]
  - [host-contract-doc, fixture-host-scaffold]
  - [bug-gate-grammar, report-inbox-triage]
  - [escape-column]
  - [supervised-merge-hold]
  - [go-grade-machinery, go-grade-run]
  - [exit-receipt-machinery]
  - [phase6-exit]
seeds:
  core-renderer: {cite: [8, 15], fence: [chupa/hostfiles.py, tests/test_hostfiles.py, chupa/__main__.py, tests/test_cli.py], does: "Managed-block renderer, first adoption, byte-idempotent, no git or commit; core CLI registration."}
  core-drift-classifier: {cite: [8], depends: [core-renderer], fence: [chupa/hostfiles.py, tests/test_hostfiles.py], does: "Pure DRIFT classification, unreachable from production gates."}
  core-drift-activation: {cite: [7, 8], depends: [core-drift-classifier], fence: [chupa/hostfiles.py, chupa/gates.py, chupa/config.py, chupa/merge.py, chupa/providers.py, chupa/__main__.py, tests/test_hostfiles.py, tests/test_gates.py, tests/test_merge.py, tests/test_providers.py, tests/test_cli.py], does: "core_drift hard gate in the merge-time rerun set over the shared resolver; replaces the classifier-unreachable assertion."}
  migrate-config: {cite: [15], depends: [core-renderer], fence: [chupa/config.py, chupa/__main__.py, tests/test_config.py, tests/test_cli.py], does: "MIGRATE-CONFIG contract."}
  host-contract-doc: {cite: [15], depends: [migrate-config], fence: [docs/host-contract.md, tests/test_host_contract.py], does: "The host-contract doc; no production code."}
  fixture-host-scaffold: {depends: [host-contract-doc, core-drift-activation], fence: [hosts/fixture/, tests/test_fixture_host.py], does: "The fixture host as listed in Deliverables; no engine module."}
  bug-gate-grammar: {cite: [7, 13], depends: [fixture-host-scaffold], fence: [chupa/tickets.py, chupa/gates.py, chupa/stages.py, tests/test_tickets.py, tests/test_gates.py, tests/test_bug_gate.py], does: "kind: bug, mandatory ## Regression, head-pass/base-with-carries-overlay-fail hard gate; a test missing at base is never defect evidence."}
  report-inbox-triage: {cite: [12], depends: [bug-gate-grammar], fence: [chupa/inbox.py, chupa/box.py, chupa/triage.py, chupa/author.py, chupa/daemon.py, chupa/serve.py, tests/test_box.py, tests/test_triage.py, tests/test_author.py, tests/test_serve.py, tests/test_inbox.py], does: "The report inbox with every seam owned; daemon and live serve consumers wired."}
  escape-column: {cite: [10, 14], depends: [bug-gate-grammar, report-inbox-triage], fence: [chupa/scorecard.py, chupa/git.py, chupa/retro.py, chupa/__main__.py, tests/test_scorecard.py, tests/test_git.py, tests/test_retro.py, tests/test_cli.py, tests/test_mergequeue.py], does: "ESCAPE contract; the scorecard stays pure."}
  supervised-merge-hold: {deep: true, cite: [9, 12], depends: [escape-column], fence: [chupa/merge.py, chupa/mergequeue.py, chupa/serve.py, chupa/restart.py, chupa/baseline.py, chupa/control.py, chupa/__main__.py, chupa/stages.py, chupa/drain.py, chupa/runner.py, eval/daemon_soak.py, tests/test_merge.py, tests/test_mergequeue.py, tests/test_serve.py, tests/test_restart_timers.py, tests/test_baseline.py, tests/test_control_cli.py, tests/test_cli.py, tests/test_drain.py, tests/test_daemon_soak_runner.py, tests/test_supervised_merge_hold.py], does: "HOLD contract inside daemon-mode MergeQueue admission (after integration, before main moves), reconstructed by restart; the soak runner reads the candidate-base regate identity."}
  go-grade-machinery: {cite: [12, 13], depends: [supervised-merge-hold, fixture-host-scaffold], fence: [eval/harness.py, eval/fixtures/, chupa/artifacts.py, chupa/stages.py, chupa/llm.py, chupa/providers.py, tests/test_eval_harness.py, tests/test_stages.py, tests/test_providers.py, tests/test_go_grade.py], does: "GO-GRADE machinery: fixtures, closed review-baseline-report.json schema/registration/writer, per-call ceiling, partial-report rule, Author-graph artifact, gated --record-go."}
  go-grade-run: {depends: [go-grade-machinery], fence: [tickets/go-grade-run/review-baseline-report.json], does: "No code: one scored run into its OUTBOX, recording its verdict signal."}
  exit-receipt-machinery: {depends: [go-grade-run], fence: [chupa/artifacts.py, chupa/stages.py, eval/host_loop.py, tests/test_host_loop.py, tests/test_gates.py, tests/test_stages.py, hosts/fixture/], does: "Closed host-loop-report.json and exit-receipt.json schemas, registration, writers, and the host-loop runner driving supervised fixture serve."}
  phase6-exit: {exit: true, depends: [exit-receipt-machinery], fence: [tickets/phase6-exit/host-loop-report.json, tickets/phase6-exit/exit-receipt.json, tests/test_phase6_exit.py], does: "Runs eval/host_loop.py, reads the committed GO-grade report, commits the RECEIPT; no seeds, no engine edit."}
# END_REGISTRY_P6
```

## 20. Open decisions

Open experiments and undecided seams, each with the evidence that would close it. None blocks the build; each is a deliberate non-default awaiting data:

- **Capability tiering.** This plan ships the validated configuration: ticket default `medium`/`medium`, implement->codex, review+diagnose->claude, review pinned to a fixed strong tier (never on the escalation ladder -- a climbing reviewer blurs the baseline identity). The alternative bet -- a cheap implementer started at `low`/`max` under a strong author, climbing only on evidence -- is OPEN, currently disfavored by observed per-ticket review-snag churn; it closes when a run under each configuration compares merges-per-intervention at equal scope.
- **Single-adapter Phase 1.** Shipping one adapter in Phase 1 and deferring the second to Phase 4 would cut first-contact surface; it is OPEN and disfavored -- cross-provider review diversity from Phase 1 is part of the only lightly-attended completed recipe -- and closes only via a deliberate comparison run, never by default.
- **Daemon control channel.** DECIDED -- Phase 3 builds it (the deferral to "first daemon-era friction" re-bought a prior generation's paid lesson, and `19.P3` requires `kill`/`pause`/`resume` control before `serve`, so the friction is guaranteed, not conditional). A second CLI can never append journal signals while a daemon holds the single-writer lock (sections 6/9) -- the old interim contradicted that fence. While a live engine process -- the drain or the daemon -- holds the lock, control verbs act through a durable file-backed CONTROL INBOX of typed requests under the state dir: the CLI writes the request; the lock-holding engine process -- sole journal writer for its lifetime (section 18) -- consumes each request EXACTLY ONCE, journals its decision BEFORE mutating any state the decision governs, then applies it. Every request binds to identity: the restart-unique lifecycle id of the running engine process it targets (the running `drain` or later `serve`, section 12), and for a hold release the specific hold instance it releases (a storm-breaker trip, section 12; a red-streak or tree-hash admission pause, section 9) -- a `resume` filed before a hold exists, or a request from a prior lifecycle, can never release or stop a later one. `pause` takes effect BEFORE any durable dispatch accounting of the next offer -- section 9's "next safe checkpoint" MEANS pause precedes ALL dispatch accounting, a re-offer's retry draw included, or a consumed pause still spends cap draws before blocking execution; only `resume` releases it, latest-wins. With no engine process running, `pause`/`resume` take the lock themselves and apply directly -- the pre-daemon path is unchanged.

  `kill` is the one additive Phase 3 CLI verb. Against a live bootstrap `drain`, its control consumer runs concurrently with an in-flight dispatch as well as at offer boundaries. A current-lifecycle kill is accepted and journaled before mutation, latches that drain into stopping state, reaches the production `Driver` owned by `Stages` through the `Pipeline`/`Runner` composition, aborts and observes its active invocation, and admits no later ticket or retry draw; the killed run is left journal-valid terminal or restart-reconcilable before the lock releases, and the applied decision is journaled only after the abort unwinds. Stale-lifecycle requests are journaled stale and mutate nothing. With no engine running, `kill` takes the lock only to refuse (`nothing running to kill`), creating no lifecycle, decision, or latch. The worker-stop and kill-failure-suppression boundaries stay dormant until `serve-activation` composes the real worker tasks and activates them in the same order (decision before mutation, executor unwind before worker cancel); a test-only task graph is never production evidence.
- **Settled-ticket archive.** Merged stems currently rest in `tickets/` forever, folded out of eligibility by the journal; a physical archive (relocating settled dirs under `tickets/archive/`) is OPEN, earned by the first measured tooling pain from an unbounded tickets dir (it is the ARCH block's first plausible consumer).
- **Journal retention.** The roll trigger ships in Phase 3; retention/GC of rolled segments stays refused (section 18's ARCH deferral) until disk pressure is actually measured.

## 21. Appendix: embedded bootstrap sources (extraction blocks)

Both bootstrap sources live here. The section-0 cold-start extractor materializes each by pulling the lines between its `# BEGIN_<NAME>` / `# END_<NAME>` sentinel pair -- one minimal pattern, reused for both -- and writing them to disk, so the operator never hand-pastes either file. Keep the sentinel lines intact and exactly as written; the extractor keys on them.

**Bootstrap conductor** -- extracted to `bootstrap/conductor.py` (section 0).

````python
# BEGIN_CONDUCTOR
#!/usr/bin/env python3
"""Bootstrap conductor -- ONE-TIME operator tooling that drives the phase prompt
playbooks in CHUPA_PLAN.md to their exit gates so the human never hand-pastes.

Section-0 cold-start convenience, NOT engine code: it exists only until the
Phase 1 walking skeleton lands and chupa runs its own tickets, and D1 governs the
engine, not these conveniences. It still obeys the argv-list rule (subprocess.run
with lists, never shell=True, never string-assembled commands).

Automation is the DEFAULT, in three rungs the operator picks between -- coarser
rungs just run the finer one in order and gate every deliverable the same way:
  (no --phase)               -- run every conductor-owned phase (0 then 1) end
                                to end; this is the one command for the whole
                                bootstrap.
  --phase N                  -- run all of phase N's deliverables.
  --phase N --deliverable K  -- run exactly that one deliverable, commit it,
                                then stop.
`--auto` removes the designed real-model verdict pauses for a fully unattended
run. The rungs compose through bootstrap/state.json, so hand-stepping a few
deliverables then letting the default finish the rest resumes correctly.
Every rung SKIPS deliverables already recorded done; to redo the whole
bootstrap after editing the plan, delete bootstrap/state.json first. Rungs
REFUSE to run ahead of recorded progress -- a skipped phase or deliverable
would otherwise be ratcheted done without ever running.

Per deliverable: parse the next unrun prompt from this phase's playbook in
CHUPA_PLAN.md (the single source -- no copied checklist), run it in a FRESH
`claude -p` process (a separate scoped context, the anti-wander property; a
standing PREAMBLE carries the verify-in-place and file-don't-ask rules into
every context), then gate by the prompt's own stop-condition. Two checks bind
EVERY gate kind: the `claude` call must exit zero (transient failures are
retried with backoff; a persisting nonzero -- a dead or unauthenticated CLI --
halts, never a silent phantom completion), and the playbook item's
`expects:` files must exist on disk afterward (the agent-did-nothing check;
`-` waives it for journal-gated deliverables). Then per kind:
  pytest  -- re-run `uv run pytest` (never trust the agent's claim), then have
             a SECOND fresh context adversarially review the uncommitted diff
             against the good-enough bar's spine-breaking classes ONLY (state
             corruption, deadlock/stall, secret exposure, false-green tests
             that mirror the implementation -- the builder's own tests are
             not the last word on the builder); every other finding files to
             bootstrap/suggestions.md and passes. Verdict via
             bootstrap/review.json, missing/unparseable = fail closed. Gate
             findings (red suite or review fail) are fed back up to
             MAX_FIX_ATTEMPTS times, then halt. On pass commit + advance.
  verdict -- a real-model deliverable whose exit is a recorded verdict, not a
             green suite (Phase 1 prompts 2 and 9): run, then VERIFY in the
             journal that the artifact the stop-condition names appeared since
             the deliverable started -- a `signal` event when the prompt says
             verdict, a transition to `merged` when it says merged (the
             `state_transition` body's `to` field is a promoted envelope
             contract, section 6); on evidence
             commit, then pause for the operator to read the verdict (--auto
             continues without pausing; GO is not earnable during the
             bootstrap -- the --record-go mode is Phase 6's, section 19); on
             none, halt WITHOUT committing.
  none    -- no test and no verdict (the seed-files step): run, check
             expects, commit, advance.
Guards, all halt-for-operator: a preflight refuses to start without git, uv,
pnpm, and claude on PATH, or with claude older than its latest pnpm release; each phase's parsed deliverable count must match the
plan's stated count (a playbook format drift halts -- never a short parse
silently declared complete); a deliverable REFUSES to
start on a dirty tree (the commit sweeps `git add -A`, so anything already
dirty would splice into this deliverable's commit -- the halt names the
commit-then-rerun paved road; recovery is git revert, never stash or
reset); and a verdict deliverable
REFUSES to record done
until the journal carries its named artifact, never the context's claim.
Progress is bootstrap/state.json ({"phase": N, "done": K} -- phases below N are
complete, phase N has K deliverables done) so a halt resumes where it stopped;
delete it to start the whole bootstrap over from the first deliverable.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "CHUPA_PLAN.md"
STATE = ROOT / "bootstrap" / "state.json"
CONDUCTOR_PHASES = (0, 1)   # the phases the conductor owns; 2+ run via `chupa drain`
MAX_FIX_ATTEMPTS = 2
MAX_ATTEMPT_CALLS = 500   # per-launch model-call ceiling (section 19 bootstrap contract)
ATTEMPT_ID = datetime.now(timezone.utc).strftime("bs-%Y%m%dT%H%M%SZ")  # durable per-launch id (section 19)
CLAUDE_TRANSIENT_RETRIES = 2   # bounded backoff before a nonzero exit halts
CLAUDE_PACKAGE = "@anthropic-ai/claude-code"   # the bootstrap CLI's pnpm package (section 0 preflight)
EXPECTED_DELIVERABLES = {0: 11, 1: 17}   # playbook counts; a parse drift halts
REVIEW_FILE = ROOT / "bootstrap" / "review.json"
PREAMBLE = """\
Bootstrap deliverable for the chupa repo; CHUPA_PLAN.md is canonical.
If this deliverable's output already exists (a re-run over prior work),
VERIFY it against the plan and its stop-condition and change only what
fails them -- never rebuild green work. An out-of-scope problem is
appended to bootstrap/suggestions.md and left alone; never stop to ask.
Never run git commit, git add, or any other git write: the conductor
reviews your UNCOMMITTED diff and commits it only after review passes.
You run headless: your process ends the moment you stop replying, killing
anything still running. Run every command -- model calls, evals, authoring
-- in the FOREGROUND to completion; never background work or end your turn
waiting for it. Stop only when the stop-condition is actually met.

"""

CALLS = 0


def count_call():
    # section 19 bootstrap contract: every model call draws the attempt's
    # MAX_ATTEMPT_CALLS ceiling; the next no-flag launch is a fresh attempt.
    global CALLS
    CALLS += 1
    if CALLS > MAX_ATTEMPT_CALLS:
        sys.exit("attempt %s exceeded MAX_ATTEMPT_CALLS=%d -- halting; "
                 "re-run python3 bootstrap/conductor.py to start a fresh "
                 "attempt with a fresh ceiling" % (ATTEMPT_ID, MAX_ATTEMPT_CALLS))



def parse_deliverables(phase):
    text = PLAN.read_text()
    marker = "**Phase %d prompt playbook.**" % phase
    start = text.find(marker)
    if start == -1:
        sys.exit("no playbook for phase %d in CHUPA_PLAN.md" % phase)
    tail = text[start + len(marker):]
    stops = [m.start() for m in re.finditer(r"\*\*Phase \d+ prompt playbook\.\*\*", tail)]
    sec = re.search(r"\n## \d+\. ", tail)
    if sec:
        stops.append(sec.start())
    block = tail[:min(stops)] if stops else tail
    items = re.findall(
        r"\n(\d+) -- ([^\n]+):\nexpects: ([^\n]+)\n+```\n(.*?)\n```",
        block, re.S)
    parsed = [(title.strip(), expects.split(), prompt.strip())
              for _num, title, expects, prompt in items]
    want = EXPECTED_DELIVERABLES.get(phase)
    if want is not None and len(parsed) != want:
        sys.exit("phase %d playbook parsed %d deliverables, expected %d -- "
                 "the playbook format drifted ('N -- Title:' line, 'expects:' "
                 "line, one fenced prompt); fix CHUPA_PLAN.md, never skip"
                 % (phase, len(parsed), want))
    return parsed


def gate_of(prompt):
    low = re.sub(r"\s+", " ", prompt.lower())
    if "pytest" in low:
        return "pytest"
    if "verdict" in low or "merged" in low:
        return "verdict"
    return "none"


def run(cmd, **kw):
    return subprocess.run(cmd, cwd=str(ROOT), **kw)


def journal_evidence(prompt, started_at):
    """The mechanical half of a verdict gate: the artifact the stop-condition
    names must be IN the journal since `started_at`, never the context's
    claim. Returns the set of still-missing evidence kinds."""
    state_dir = ROOT / ".chupa" / "state"
    cfg = ROOT / "config.yaml"
    if cfg.exists():
        m = re.search(r"^state_dir:\s*(\S+)", cfg.read_text(), re.M)
        if m:
            state_dir = ROOT / m.group(1)
    low = re.sub(r"\s+", " ", prompt.lower())
    need = set()
    if "verdict" in low:
        need.add("signal")
    if "merged" in low:
        need.add("merged")
    seen = set()
    for seg in sorted((state_dir / "journal").glob("*.jsonl")):
        for line in seg.read_text().splitlines():
            try:
                e = json.loads(line)
            except ValueError:
                continue        # torn tail is the reader's normal case
            if e.get("ts", "") < started_at:
                continue
            if e.get("type") == "signal":
                seen.add("signal")
            if (e.get("type") == "state_transition"
                    and (e.get("body") or {}).get("to") == "merged"):
                seen.add("merged")
    return need - seen


def preflight():
    missing = [b for b in ("git", "uv", "pnpm", "claude") if not shutil.which(b)]
    if missing:
        sys.exit("missing required binaries: %s -- see the prerequisites table "
                 "(CHUPA_PLAN.md section 0)" % ", ".join(missing))
    installed = run(["claude", "--version"], capture_output=True, text=True).stdout.split()[:1]
    latest = run(["pnpm", "view", CLAUDE_PACKAGE, "version"], capture_output=True, text=True).stdout.strip()
    if not latest or installed != [latest]:
        sys.exit("claude %s is not the latest release %s -- run: pnpm add -g %s@latest"
                 % ((installed or ["(unknown)"])[0], latest or "(unreadable)", CLAUDE_PACKAGE))


def claude(prompt):
    # fresh one-shot context per deliverable; operator-owned bootstrap repo.
    # Transient nonzero exits (overload, network) get bounded retries with
    # backoff -- machine-retryable work never waits on an operator rerun.
    for attempt in range(CLAUDE_TRANSIENT_RETRIES + 1):
        count_call()
        r = run(["claude", "-p", PREAMBLE + prompt, "--dangerously-skip-permissions"])
        if r.returncode == 0:
            return
        if attempt < CLAUDE_TRANSIENT_RETRIES:
            wait = 30 * (attempt + 1)
            print("claude exited %d -- retrying in %ds (%d/%d)"
                  % (r.returncode, wait, attempt + 1, CLAUDE_TRANSIENT_RETRIES))
            time.sleep(wait)
    sys.exit("claude exited %d after %d retries -- persistent failure (auth? "
             "quota?); fix it and re-run the same command to continue; nothing "
             "gated, nothing committed, state not advanced"
             % (r.returncode, CLAUDE_TRANSIENT_RETRIES))


def adversarial_review(title, frozen=None):
    """Second fresh context reviews the builder's uncommitted work against
    the section 19 good-enough bar: FAIL only spine-breaking classes; every
    other finding files to bootstrap/suggestions.md and passes. New and
    untracked files are part of the
    review surface (git diff alone misses them). Transient failures --
    nonzero exit or an unparseable verdict file -- get bounded retries;
    a persisting one halts fail-closed. Returns [] on pass, findings on fail.
    A re-review pass receives the FROZEN first-pass blocking set; a NEW
    objection on a later pass is advisory (the section 0 freeze law)."""
    verdict = None
    for attempt in range(CLAUDE_TRANSIENT_RETRIES + 1):
        if REVIEW_FILE.exists():
            REVIEW_FILE.unlink()
        count_call()
        r = run(["claude", "-p",
                 "You are the adversarial reviewer for one chupa bootstrap "
                 "deliverable; CHUPA_PLAN.md is canonical. Review the working "
                 "tree's UNCOMMITTED work -- git status for the file set, git "
                 "diff for tracked changes, and READ each new/untracked file "
                 "in full (the diff does not show them) -- against the "
                 "plan sections the deliverable cites. FAIL only for the "
                 "bootstrap contract's spine-breaking classes (CHUPA_PLAN.md "
                 "section 19): state corruption, deadlock or permanent stall, "
                 "secret exposure, or false-green verification -- tests that "
                 "mirror the implementation instead of pinning real behavior "
                 "(orderings, refusals, crash points). A blocking finding "
                 "must be REPRODUCIBLE and must attach to THIS deliverable's "
                 "uncommitted diff -- never pre-existing code or later-phase "
                 "scope. Append every OTHER "
                 "finding (conformance drift, style, scope) as one-line items "
                 "to bootstrap/suggestions.md and still pass. Write EXACTLY "
                 "bootstrap/review.json: "
                 '{"verdict": "pass"} or {"verdict": "fail", "findings": '
                 '["..."]}. Change no file other than those two. '
                 + ("" if frozen is None else
                    "RE-REVIEW: the blocking set is FROZEN to the findings "
                    "listed after the deliverable name -- fail ONLY if one "
                    "of them is still unresolved; any NEW problem, whatever "
                    "its class, files to bootstrap/suggestions.md and never "
                    "fails. Frozen findings: " + "; ".join(frozen) + ". ")
                 + "Deliverable: " + title,
                 "--dangerously-skip-permissions"])
        if r.returncode != 0:
            if attempt < CLAUDE_TRANSIENT_RETRIES:
                wait = 30 * (attempt + 1)
                print("review context exited %d -- retrying in %ds"
                      % (r.returncode, wait))
                time.sleep(wait)
                continue
            sys.exit("review context exited %d after retries -- fix and "
                     "re-run the same command to continue" % r.returncode)
        try:
            verdict = json.loads(REVIEW_FILE.read_text())
            break
        except (OSError, ValueError):
            if attempt < CLAUDE_TRANSIENT_RETRIES:
                print("no parseable bootstrap/review.json -- re-asking the reviewer")
                continue
            sys.exit("no parseable bootstrap/review.json after %d asks -- "
                     "fail closed, halting for operator"
                     % (CLAUDE_TRANSIENT_RETRIES + 1))
    REVIEW_FILE.unlink()
    if verdict.get("verdict") == "pass":
        return []
    return verdict.get("findings") or ["review verdict: fail (no findings listed)"]


def pytest_green():
    return run(["uv", "run", "pytest", "-q"]).returncode == 0


def ensure_ignored():
    gi = ROOT / ".gitignore"
    txt = gi.read_text() if gi.exists() else ""
    add = [e for e in ("bootstrap/state.json", "bootstrap/review.json")
           if e not in txt]
    if add:
        sep = "" if (not txt or txt.endswith("\n")) else "\n"
        gi.write_text(txt + sep + "\n".join(add) + "\n")
        return True
    return False


def require_clean(phase, n):
    # the commit below sweeps `git add -A`, so a dirty tree at start would
    # splice unrelated work into this deliverable's commit -- halt instead.
    dirty = run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout.strip()
    if dirty:
        sys.exit("phase %d deliverable %d: tree is dirty (a prior halt leaves "
                 "its partial work uncommitted). To continue: commit it "
                 "(`git add -A` + a wip commit), then re-run the same command "
                 "-- verify-in-place converges over committed partial work, "
                 "and recovery is git revert, never stash or reset:\n%s"
                 % (phase, n, dirty))


def commit(msg):
    ensure_ignored()
    dirty = run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout.strip()
    if not dirty:
        return
    run(["git", "add", "-A"], check=True)
    run(["git", "commit", "-m", msg], check=True)


def load_state():
    # (phase, done): phases below `phase` are complete, `phase` has `done` done.
    if STATE.exists():
        s = json.loads(STATE.read_text())
        return int(s.get("phase", 0)), int(s.get("done", 0))
    return 0, 0


def save_state(phase, done):
    # Ratchet: an explicit rerun of an earlier deliverable must never rewind
    # the resume point past completed work.
    phase, done = max(load_state(), (phase, done))
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(
        {"phase": phase, "done": done, "attempt_id": ATTEMPT_ID}))


def run_deliverable(phase, items, i, auto):
    """Run one deliverable (0-based index i). Return True to keep going, False to
    pause on a verdict. Halts the process on a failed gate. Commits + records
    state on success."""
    title, expects, prompt = items[i]
    n = i + 1
    gate = gate_of(prompt)
    require_clean(phase, n)
    print("=== phase %d deliverable %d/%d (%s): %s ===" % (
        phase, n, len(items), gate, title))
    started_at = datetime.now(timezone.utc).isoformat()
    # the expects: files are the gate; a prompt that never names one would
    # otherwise fail the existence check on a correct but differently-placed build
    claude(prompt if expects == ["-"] else prompt + "\n\nRequired outputs -- "
           "the gate checks each exists on disk: " + " ".join(expects))
    missing = [] if expects == ["-"] else [p for p in expects
                                           if not (ROOT / p).exists()]
    if missing:
        save_state(phase, i)
        sys.exit("phase %d deliverable %d: expected outputs missing: %s -- the "
                 "agent run did not produce its deliverable; nothing committed"
                 % (phase, n, ", ".join(missing)))
    if gate == "verdict":
        missing_ev = journal_evidence(prompt, started_at)
        if missing_ev:
            save_state(phase, i)
            sys.exit("phase %d deliverable %d: journal shows no %s since start "
                     "-- halting for operator, nothing committed"
                     % (phase, n, "/".join(sorted(missing_ev))))
    if gate == "pytest":
        attempt = 0
        frozen = None
        while True:
            if not pytest_green():
                findings = ["uv run pytest is red"]
            else:
                findings = adversarial_review(title, frozen)
                if findings and frozen is None:
                    frozen = list(findings)   # the section 0 freeze law
            if not findings:
                break
            attempt += 1
            if attempt > MAX_FIX_ATTEMPTS:
                save_state(phase, i)
                sys.exit("phase %d deliverable %d still failing its gate after "
                         "%d fix attempts -- halting. Paved road: narrow or "
                         "split this deliverable's playbook prompt in "
                         "CHUPA_PLAN.md, then re-run exactly it:  python3 "
                         "bootstrap/conductor.py --phase %d --deliverable %d"
                         % (phase, n, MAX_FIX_ATTEMPTS, phase, n))
            claude("The last change failed its gate. Findings:\n- "
                   + "\n- ".join(findings) + "\n"
                   "Read them, fix the code (not the test, unless the test is "
                   "wrong per CHUPA_PLAN.md), keep the change minimal. Stop "
                   "when uv run pytest is green.")
    commit("bootstrap: phase %d deliverable %d -- %s" % (phase, n, title))
    save_state(phase, n)
    if gate == "verdict" and not auto and n < len(items):
        print("deliverable %d is a real-model step -- read its recorded verdict, "
              "then re-run to continue (--auto skips these pauses)." % n)
        return False
    return True


def run_phase(phase, start, auto):
    """Run phase `phase` from deliverable index `start`. Return True if the phase
    fully completed, False if it paused on a verdict (halts exit on red)."""
    items = parse_deliverables(phase)
    for i in range(start, len(items)):
        if not run_deliverable(phase, items, i, auto):
            return False
    print("phase %d complete." % phase)
    return True


def main():
    preflight()
    ap = argparse.ArgumentParser(description="chupa bootstrap conductor")
    ap.add_argument("--phase", type=int,
                    help="run one phase (default: every conductor phase, %s)"
                         % "->".join(map(str, CONDUCTOR_PHASES)))
    ap.add_argument("--deliverable", type=int,
                    help="with --phase: run exactly this deliverable "
                         "(1-based), then stop")
    ap.add_argument("--auto", action="store_true",
                    help="do not pause on real-model (verdict) deliverables")
    args = ap.parse_args()

    # ignore + commit the conductor's state files up front, so a halt before
    # the first deliverable commit can never dirty the tree with them.
    if ensure_ignored():
        changed = run(["git", "status", "--porcelain", "--", ".gitignore"],
                      capture_output=True, text=True).stdout.strip()
        if changed:
            run(["git", "add", ".gitignore"], check=True)
            run(["git", "commit", "-m",
                 "bootstrap: ignore conductor state files"], check=True)

    # finest rung: one named deliverable, then stop
    if args.deliverable is not None:
        if args.phase is None:
            ap.error("--deliverable requires --phase")
        items = parse_deliverables(args.phase)
        n = args.deliverable
        if not 1 <= n <= len(items):
            ap.error("phase %d has deliverables 1..%d, not %d"
                     % (args.phase, len(items), n))
        cur, done = load_state()
        if args.phase > cur:
            ap.error("phase %d is ahead of recorded progress (phase %d, %d "
                     "done) -- finish earlier phases first, or delete "
                     "bootstrap/state.json to start over"
                     % (args.phase, cur, done))
        if args.phase == cur and n > done + 1:
            ap.error("deliverable %d is ahead of recorded progress (%d "
                     "done) -- deliverables run in order; %d is next, or "
                     "delete bootstrap/state.json to start over"
                     % (n, done, done + 1))
        run_deliverable(args.phase, items, n - 1, args.auto)
        return

    # middle rung: one whole phase
    if args.phase is not None:
        cur, done = load_state()
        if args.phase > cur:
            ap.error("phase %d is ahead of recorded progress (phase %d, %d "
                     "done) -- finish earlier phases first, or delete "
                     "bootstrap/state.json to start over"
                     % (args.phase, cur, done))
        start = done if cur == args.phase else 0
        run_phase(args.phase, start, args.auto)
        return

    # default rung: every conductor-owned phase, end to end
    cur, done = load_state()
    for phase in CONDUCTOR_PHASES:
        if phase < cur:
            continue
        start = done if phase == cur else 0
        if not run_phase(phase, start, args.auto):
            return
        save_state(phase + 1, 0)
    print("conductor phases complete -- from here run `uv run python -m chupa "
          "drain` ONCE; it carries every remaining phase to quiescence "
          "(section 19).")


if __name__ == "__main__":
    main()
# END_CONDUCTOR
````

**README** -- extracted to `README.md`; GENERATED, so edit this block, never the file, then re-run the extractor. A deliberate POINTER, not a run-book: section 0 already is the operator path, and a parallel run-book is a second copy to drift (goal 1); a fuller README returns via D10 only if a stale-doc incident earns it.

````markdown
# BEGIN_README
# chupa

chupa is a continuously running orchestration engine that authors and runs
tickets against host repos, including itself. This README is GENERATED from
CHUPA_PLAN.md (the `# BEGIN_README` block in its appendix) -- edit that block,
never this file. CHUPA_PLAN.md is canonical for everything: read section 0
(cold start, prerequisites, the conductor and its rungs, the self-hosting
handoff) first, and run its one-time cold-start paste to seed the repo, venv,
and deps before any command below.

The lifecycle is four commands, run in order:

    python3 bootstrap/conductor.py            # bootstrap: Phase 0 then Phase 1, gated per deliverable
    python3 bootstrap/conductor.py --auto     # same, unattended (no verdict pauses)
    uv run python -m chupa drain             # after Phase 1: ONE drain self-hosts Phases 2-6 to quiescence
    uv run python -m chupa serve             # cutover: start the continuous daemon on host work (after GO is recorded)

Once `serve` is running, control it with `kill` / `pause` / `resume`; `status`
and `doctor` inspect at any time. Section 18 lists every verb; section 13
touchpoint 7 is the GO/cutover gate `serve` waits behind.
# END_README
````

## 22. Appendix: rationale and provenance (never cited)

Why the section 19 laws exist. Nothing here is a rule: the `Plan contract` resolver refuses section 22, and plan lint excludes it from every render budget. Edit a law in its unit; record why here.

- **One continuous drain, runs-to-done (`19.L` bootstrap contract).** The first implementation attempt died in Phase 2: a week of drains stopped on parked tickets whose fixes were simple, each waiting on an operator to "just rerun". Every drain-conduct rule removes one of those operator waits.
- **Recovery order (`19.L`).** Skipping it is the recurring failure: patching a ticket or code before the seed leaves the defect to reproduce at the next regeneration (section 1).
- **Seed buildability at authoring (`19.L`).** A grammar-valid but unbuildable seed reaches the serial chain, `premise_failed`s at Implement, and parks every downstream stem -- the single-step stall. The fence-gap escape behind mechanical rules 1-4 was paid in every prior build. Render feasibility is measured at the ladder TOP because escalation re-keys the bound smaller mid-lineage, so a render fitting only its authored rung dies on the ladder.
- **Caller closure, rule 5 (`19.L`).** In the squatch build, about 25 of 113 plan repairs added a direct caller (`compose_pipeline` users in tests and benches, `stages.compose`, provider payload users in `eval/`) or a public-surface allowlist test (the git operation allowlist, twice) to a fence after the seed parked.
- **Bounded batches and KNOWN-DEEP (`19.L`).** A batch clears review jointly at roughly per-seed-approval^N: nine seeds in one admission never cleared in thirteen attempts (best 1/9), and interlocked seeds sharing one closed member set churn as ONE batch. Depth, not count, drives review churn. The phase-exit seed bundles a multi-read exit test with the next phase's core, a shape that oscillates across attempts without ever presenting the K-identical terminal section 11.4 keys on -- hence KNOWN-HARD at start.
- **Grain law (`19.L`).** Every coarser "runtime" bundle was terminally rejected on a fresh genuine race per review pass; a micro-ticket chain builds one link per continuation and stalls a phase for days. `requisition_review` and the watchdog each proved unbuildable as one ticket in two prior builds; Phase 5 seeded flat cost one build a 27-attempt authoring grind and another a 7-way plan re-decomposition.
- **Registries instead of phase prose (`19.P3`-`19.P6`).** Prose phase bullets left ticket-level fences and orderings to seeding tickets, which invented them one `requisition_review` cycle at a time at the phase boundary, when the exit context is most loaded. The squatch build spent 35 plan repairs on Phase 3 alone and had to add six corrective deliverables: `serve-activation` (nothing composed production `serve`), `daemon-soak-runner` (schema and writer landed with no runner), `serve-merge-admission` (the merge queue was never production-reachable), `worker-recovery-disposition` (no run-scoped record of a reaped worker), `outbox-only-admission` (no-code run lanes were rejected for an empty diff), and the split of `admission-holds-activation` from pause activation. The registries are the settled outcome of that build, normalized.
- **Units and On-demand (`19.L`, sections 8, 13).** Seeds once cited whole sections. Section 19 reached 86 KB; a Phase 3 seed citing sections 6, 9-13, 15, 18, and 19 measured 186,586 characters before ticket text against a 120,000-character headroom. About 30 of the squatch build's 113 plan repairs only moved files between "embedded" and "read on demand" to fit, inventing the on-demand category 27 times against a rule that every fenced file be embedded.
- **Authoring-time seeding-test snapshots (`19.L`, section 0 prompt 17).** Seeding tests that compared recorded sizes with live files, or rescanned live markers, reddened historical tests whenever a later activation legitimately edited a fenced file -- five migration repairs in one build.
- **Construction/activation evidence contract (`19.I`).** Applied separately, section 9's production-exercise rule and the dormancy rule reject every mid-chain ticket in alternation; an AST scan missing the `from chupa import X` idiom is the convergent false-green dormancy proof. An absence assertion has no reference edge to the new symbol, so closure tracing never finds it.
- **Exit reads on committed artifacts (`19.L`).** The exit ticket runs on a clean checkout without the gitignored state dir, harness member journals die with their temp dirs, and a healthy self-build never produces a live flake, storm, quota, or spiral event to read.
- **Machinery/producer split and run-lane admission (`19.L`).** The engine lifts and validates from merged main, so a deliverable's own OUTBOX registration is not live during its own build: it can never lift its own report. The squatch soak landed schema and writer with no runner, and its no-code run was then rejected for an empty diff.
- **Retro invoker (`19.P5`).** Without the drain as invoker, nothing fires a retro before cutover: `phase5-exit` either parks `premise_failed` with no release or passes on fixture-only evidence with the loop never fired in production.
- **Phase 4 split from Phase 3.** The daemon's crash-recovery core is proven before provider and watchdog complexity is layered on.
- **GO-grade size and controls (`19.P6`).** Fifty, not twenty, planted defects: a 20-sample catch rate cannot statistically separate a 60% reviewer from a 90% one, and this number gates unsupervised merge. Clean controls: the squatch GO-grade report scored 50 known-bad, 0 clean, catch rate 1.0 -- a reviewer that snags everything scores perfectly, so the number could not tell judgment from reflex. The per-call ceiling and partial-NO-GO rule came from the same run exhausting its flat cap mid-set.
- **Suggestion Box admission (section 12).** After the squatch build completed, triage authored 45 draft tickets -- mostly config-strictness and test-only hardening -- with roughly 270 decision and tombstone records, re-invoking Author on every daemon scan for items whose authoring kept failing.
