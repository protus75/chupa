---
state: confirmed
source: seed
priority: P1
kind: feature
agent_tier: high
agent_effort: medium
---

## Depends on
- spine-diagnosis

## Context
- chupa/git.py
- chupa/seams.py
- chupa/config.py
- tests/test_git.py

## On-demand
- bootstrap/suggestions.md

## Plan contract
- 19.L
- 19.P2
- section 12

## Goal / Why
`chupa/box.py` is the Suggestion Box (section 12): a durable queue of one atomic JSON file per message under `<state_dir>/box/`, signature dedup at enqueue, and the decision-registry record format under `tickets/decisions/`. Its first messages are the lines of `bootstrap/suggestions.md`, the section 0 stand-in, ingested as ONE `suggestion` message per non-empty line. That file is then deleted in this diff.

Why: every later spine seed files into the box. The run record's second problems, the `reject` verb's dead-dependency reports, and base-red attribution all need it, and the triage consumer drains it. The mailbox must exist before its first letter (19.P2). Until now out-of-scope problems were appended to a markdown file nothing reads. Ingesting it once and deleting it leaves one durable queue, never two.

Owners (section 9 ownership law, 19.P2 NAMES and BOX): `chupa/box.py` owns the message schema, the queue directory, the signature recipe, dedup, the resolution status field, the registry record schema, and the one-time ingest. `chupa/git.py` owns the new `git_common_dir` op. Writing and committing registry records is the triage consumer's (a later seed), never this ticket's.

## Scope in / Scope out
- In: `chupa/box.py` constants:
  - `BOX_DIR = "box"` (the queue is `<state_dir>/box/`).
  - `MessageClass = Literal["suggestion", "failure_report", "override_report", "retro_finding", "bug_report"]` and `MESSAGE_CLASSES = get_args(MessageClass)`, the one copy of the class vocabulary.
  - `BOOTSTRAP_ORIGIN = "bootstrap-ingest"`, `BOOTSTRAP_FILE = "bootstrap/suggestions.md"`, `DECISIONS_DIR = "tickets/decisions"`.
- In: `normalize(reason) -> str`. It drops every whitespace-separated token that contains `/`, removes every run of digits, collapses whitespace to single spaces, and strips. It is deterministic and order-stable.
- In: `signature(*fields: str, reason: str) -> str`: the sha256 hex digest of `json.dumps([*fields, normalize(reason)], separators=(",", ":"))`. Two recipes use it:
  - An ENGINE-produced message signs `(message_class, origin, stage, outcome)` plus its reason, where `origin` is the producing stem.
  - A message with no stage (a bootstrap-ingested line, later a host report) signs `(message_class, origin)` plus its text. A bootstrap line therefore signs `("suggestion", "bootstrap-ingest")` plus the line.
- In: `Message`, a closed strict pydantic model with unknown keys refused. Fields:
  - `id`, `seq` (int >= 1), `signature` (64 lowercase hex), `message_class`, `summary` (non-blank, untrusted text).
  - `origin` (the producing stem, or `bootstrap-ingest`), `stage` and `outcome` (both null, or both set).
  - `bug_origin` (`self_diagnosed | player`) and `has_repro` (bool): both non-null exactly when `message_class` is `bug_report`, both null otherwise.
  - `status` (`pending | resolved`), `verdict` (nullable `Verdict`), `resolution` (nullable `Resolution`). `resolution` is non-null exactly when `status` is `resolved`.
  - `Verdict` is the consumer's recorded triage verdict: `verdict` (`author | tombstone | decision`), `produced_by_spec_version` (non-blank), `rationale` (non-blank).
  - `Resolution`: `kind` (`ticket | tombstone | decision`) and `link` (non-blank: the authored stem, or the registry record id).
- In: `Box(root, fs)` over the queue dir, writing only through the `FileSystem` seam's atomic `write`:
  - `enqueue(*, message_class, origin, summary, stage=None, outcome=None, reason=None, bug_origin=None, has_repro=None) -> tuple[str, bool]`. The reason defaults to the summary. When ANY existing message file (pending or resolved) has the same signature, it writes nothing and returns `(that id, False)`. Otherwise `seq` is one more than the highest existing seq (1 for an empty box). The file is `<seq:06d>-<sig8>.json` and the id is `box-<seq:06d>-<sig8>`, where `sig8` is the signature's first 8 hex chars. It writes `status: pending` and returns `(id, True)`.
  - `messages()` returns all messages in seq order, and `pending()` returns the pending ones. `get(id)` returns one message.
  - `record_verdict(id, verdict)` stores the verdict and leaves the message pending.
  - `resolve(id, resolution)` sets `resolved` with that resolution by atomic replace.
  - Resolving an already-resolved message, an unknown id, or a file in the dir that fails `Message` validation raises `BoxError` naming the id or file. A bad file is never skipped. Nothing is ever deleted: duplicates collapse at enqueue and resolutions are status fields.
- In: the registry record format. `DecisionRecord` is a closed strict model: `id`, `kind` (`decision | tombstone`), `link` (non-blank), and `reopen_after_days` (int >= 1, REQUIRED, no default).
  - `record_path(id)` returns `tickets/decisions/<id>.md`.
  - `render_record(record, body) -> str` writes YAML frontmatter (via `yaml.safe_dump`) between `---` fences, then the body.
  - `parse_record(text) -> tuple[DecisionRecord, str]` refuses missing frontmatter, unknown keys, and a missing `reopen_after_days` with `BoxError`.
  - `read_registry(repo)` returns every `tickets/decisions/*.md` record, sorted by id.
- In: `chupa/git.py` gains `git_common_dir(dir) -> Path`, which runs `rev-parse --git-common-dir`. A relative result is resolved against `dir`.
- In: the one-time bootstrap ingest.
  - `ingest_bootstrap(box, text) -> list[str]` enqueues ONE `suggestion` message per non-empty line, origin `bootstrap-ingest`, no stage or outcome. The summary is the line stripped of surrounding whitespace, otherwise verbatim. It returns the ids in line order. A re-ingest creates nothing.
  - `async def ingest_main_checkout(cwd, git, fs) -> int`: the MAIN checkout root is the parent of `git_common_dir(cwd)`, so from a linked worktree it reads and writes the main checkout, never the worktree's own copy. It loads that root's `config.yaml` with `load_config(None, cwd=root)`, reads `<root>/bootstrap/suggestions.md` (absent: ingests nothing), enqueues into `Box(config.state_dir / BOX_DIR, fs)`, and returns the count of newly created messages.
  - Running `python -m chupa.box` calls it with the real seams (`SubprocessExec`, `LocalFileSystem`, `Git` with `os.environ`) from the process cwd and prints `ingested <n> new suggestion messages`. This is the ticket's first `## Verification` command. It runs at Check while main still carries the file, and again harmlessly at any re-run.
- In: `bootstrap/suggestions.md` is DELETED in this diff.
- Out: filing run-record second problems (the next seed, `second-problems-filing`), the triage consumer and every registry write or commit, and the `reject` verb's reports.
- Out: the storm-control circuit breaker and its occurrence ledger (Phase 3, beside the daemon's continuous producers), and tombstone auto-reopen, re-report counting, and retro itemization (Phase 5, with the retro stage that reads them).
- Out: the host report inbox (Phase 6), ingesting outbox box-message files at lift, and any `status` projection of the box.

## Scope fence
- chupa/box.py
- tests/test_box.py
- chupa/git.py
- tests/test_git.py
- bootstrap/suggestions.md

## Acceptance criteria
1. `tests/test_box.py` proves the signature recipe. Two reasons differing only in a path token and a line number sign identically. Changing the class, origin, stage, or outcome changes the signature. A bootstrap line's signature equals the sha256 of `["suggestion","bootstrap-ingest",<normalized line>]` serialized compactly.
2. `tests/test_box.py` proves enqueue and dedup. The file name and id follow `<seq:06d>-<sig8>.json` and `box-<seq:06d>-<sig8>`. A second enqueue with the same signature returns `(the first id, False)` and leaves the file count unchanged, including when the first message is resolved. Seqs increase by one. Each file validates as `Message`. A `bug_report` without `bug_origin` and `has_repro`, those fields on another class, and a stage without an outcome are each refused.
3. `tests/test_box.py` proves durability. `record_verdict` keeps the message pending. `resolve` sets `resolved` and the resolution, and a second `resolve` raises `BoxError`. A corrupt file raises `BoxError` naming it. A fresh `Box` over the same dir reads the same messages.
4. `tests/test_box.py` proves the registry format. `render_record` then `parse_record` round-trips. A record missing `reopen_after_days`, or carrying an unknown key, is refused. `read_registry` returns records sorted by id.
5. `tests/test_box.py` builds a temp repo with `config.yaml` and a two-line-plus-blank `bootstrap/suggestions.md`, adds a linked worktree with `git worktree add`, and deletes the worktree's copy of the file. `ingest_main_checkout` run from the worktree creates exactly two `suggestion` messages in the MAIN checkout's `<state_dir>/box/`, each with origin `bootstrap-ingest` and summary equal to its stripped line, and creates nothing under the worktree. A second run returns 0. A checkout without the file returns 0.
6. `tests/test_git.py` covers `git_common_dir` from the main checkout and from a linked worktree, both resolving to the main checkout's `.git`.
7. The first `## Verification` command exits 0, and the second proves `bootstrap/suggestions.md` is gone from the branch.
8. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run python -m chupa.box
uv run python -c "from pathlib import Path; assert not Path('bootstrap/suggestions.md').exists()"
uv run pytest -q tests/test_box.py tests/test_git.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- A message file is ever deleted, or a duplicate gets a second file.
- A second signature recipe or dedup path exists outside `chupa/box.py`.
- The ingest writes to a worktree-local state dir, or reads the worktree's copy of the file.
- `bootstrap/suggestions.md` is edited rather than deleted, or survives on the branch.
- A storm breaker, reopen counter, triage call, or registry commit is added.
- The diff touches a file outside the fence.

## Time budget
- expected: 75m
- stuck: 150m
