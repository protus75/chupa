---
state: confirmed
source: human
priority: P0
kind: bug
---

## Depends on
- none

## Runs before
- drain-ingests-report-inbox

## Context
- chupa/box.py::Box._enqueue
- chupa/box.py::Box.messages
- chupa/seams.py::LocalFileSystem.publish
- chupa/triage.py::report_intake
- tests/integration/test_cli.py::test_suggest_publishes_while_writer_lock_is_held
- tests/integration/test_triage.py::test_suggestion_drops_ingest_and_retry
- tests/regress_dev_test_args.py
- tests/unit/test_docs_verb.py

## On-demand
- chupa/__main__.py
- docs/how-chupa-works.md

## Goal / Why
A suggestion filed with `chupa suggest` does not appear in the Suggestion Box. On 2026-11-13 the operator filed six suggestions and started `./dev.py drain`, and none of them appeared. `.chupa/state/box/suggestions/` held 8 drop files, while `chupa status` showed `Suggestion Box (1 pending, 426 resolved)` (evidence: `tickets/suggest-lands-in-box/evidence/suggest-invisible.txt`). Triage is the step that works over messages already in the box, so a filed idea must be in the box the moment `suggest` exits, whatever else is running.

Observed: `chupa suggest "x"` publishes `<state_dir>/box/suggestions/<hex>.json` and prints `suggest: queued <hex>.json`. `Box.messages()` reads only `<state_dir>/box/*.json`, so the status and VS Code box views do not list the drop. Only `triage.report_intake` moves a drop into the box, and only `triage` and serve's `box_intake` call it. The operator runs `drain` (418 drain starts in `engine.log`, no serve), so drops waited until someone ran `triage`. The last session suggestions entered the box on 2026-11-11 and 2026-11-12, both after a triage.

Expected: `suggest` writes the `suggestion` message straight into the box, with no lock and no drop folder, and prints its box id.

Suspected cause: the `suggest-verb` design routed filing through a side folder because `Box._enqueue` picks `seq = max(existing) + 1` and then writes `<seq>-<sig8>.json`. Two processes enqueueing at once could pick the same `seq`, and their file names differ by signature, so neither write fails. Inspect and rule out `Box.messages()` filtering: it lists every `*.json` directly under the box root and filters nothing, so the drop is simply not there.

Fix shape: make a new message's `seq` a claim that cannot be taken twice. Before writing, `_enqueue` publishes an empty claim file `<box root>.seq/<seq:06d>` (a sibling directory, for example `<state_dir>/box.seq/`, so the box root holds only messages) with `fs.publish`. `publish` never overwrites an existing name (`os.link`), so a second claimer gets `FileExistsError`. On that error, `_enqueue` re-reads the messages, re-checks the signature, and claims the next `seq`: after a failed claim of seq N, it tries `max(N + 1, max(re-read seq) + 1)`. A `seq` is never reused, so gaps are allowed, and a claim left behind by a crashed write never blocks later enqueues. No lock is added anywhere.

Anti-patterns: do not add a lock or take the writer `Lockfile` in `suggest`. Do not make the box views list drop files: their ids would not be box ids, so `triage <id>` and `dismiss <id>` could not act on them.

Leftover drop files are not ingested after this change. The operator re-files the ones in this checkout with `chupa suggest` after merge.

## Scope in / Scope out
Scope in:
- `chupa/box.py`, `Box._enqueue`: claim each new message's `seq` by publishing `self.root.with_name(self.root.name + ".seq") / f"{seq:06d}"` with `self.fs.publish` before `_write`. On `FileExistsError` for seq N, re-read `self.messages()`, re-run the signature check, and try `max(N + 1, max(re-read seq) + 1)`. The signature-match branch is unchanged. `messages()` and the box root's contents are unchanged.
- `chupa/__main__.py`, the `suggest` branch: build `Box(config.state_dir / "box", checkout.fs, rereport=RereportJournal(checkout.journal))` and call `enqueue(message_class="suggestion", origin="session", summary=args.summary, occurrence_id=<uuid4 hex>)`. When `enqueue` creates the message, print `suggest: filed <box id>`. When it returns an existing message, print `suggest: already in the box as <box id>`. It takes no lock and writes no drop file. A blank summary is refused exactly as today.
- `chupa/triage.py`, `report_intake`: delete the `suggestions/` drop branch. `report_inbox` ingestion is unchanged.
- `tests/integration/test_cli.py`: replace `test_suggest_publishes_while_writer_lock_is_held`. While another process holds the writer lock, `suggest "a distinct idea"` exits 0, leaves exactly one pending `suggestion` message in `Box(<state_dir>/box)` with that summary and origin `session`, prints `suggest: filed <that id>`, and creates no `box/suggestions/` directory. Add a case where the same summary filed twice prints `suggest: already in the box as <id>` and leaves one message. Keep `test_suggest_refuses_blank`, changing its drop-folder assertion to "no box message".
- `tests/integration/test_box.py`: add the on-disk race test. Two `Box` objects on the same `tmp_path` root enqueue different summaries. Inject the race at the read: wrap the first Box's `messages` so that its first call runs the second Box's `enqueue` to completion and then returns the stale empty list, and later calls read normally. At base both messages get seq 1 and the test fails. At head the first Box's claim of seq 1 raises `FileExistsError` and it takes seq 2. Both messages exist with distinct `seq` values. The current code gives both the same `seq` and fails it.
- Create `tests/unit/test_suggest_box.py`, which lint requires because `chupa/__main__.py`, `chupa/box.py`, and `chupa/triage.py` have unit coverage floors. It touches no disk. Use an in-memory `FileSystem` fake whose `publish` raises `FileExistsError` for an existing path and whose `write` stores messages in a dict, and monkeypatch `Box.messages` to read that dict. It holds three tests. (a) A claim already exists for seq 1 with no message (a crashed write): `enqueue` returns a message with seq 2 and terminates. (b) A competing claim appears for the seq being tried: the message gets the next free seq. (c) The `suggest` branch run through `chupa.__main__.main` with fakes in the style of `tests/unit/test_docs_verb.py`, covering the `filed` and `already in the box` lines.
- `tests/integration/test_triage.py`: delete `test_suggestion_drops_ingest_and_retry`, since the drop branch it covers is gone.
- `tests/integration/test_storm_producer.py`: the state-directory listing asserted in `test_storm_producer_hook_is_active` (`(tmp_path / "direct").iterdir()` equals `{"box", "journal", "journal.lock"}`) also includes `"box.seq"`, since the claim directory is now part of the on-disk layout.
- `tests/integration/test_daemon_composition.py`: give `ScriptFS` a `publish(path, data)` method that raises `FileExistsError` when the path is already in `self.files` and otherwise stores it, so `CoreRig` users that create box messages (`tests/integration/test_storm_notification_activation.py`, `tests/integration/test_provider_cooldown_failover.py`) keep working.
- Create `tests/regress_suggest_lands_in_box.py`, the carried reproducer, in the style of `tests/regress_dev_test_args.py`. In a temporary repo set up as the `root` fixture in `tests/integration/test_cli.py` sets one up, it runs `suggest` through the CLI `main` under `contextlib.redirect_stdout(io.StringIO())`, as `tests/regress_dev_test_args.py` does, so only the JSON result reaches stdout. It prints `pass` (exit 0) when `Box(<state_dir>/box).messages()` holds a pending suggestion with that summary, and `defect` (non-zero exit) when it holds none. A setup failure prints `error`.
- `docs/how-chupa-works.md`: the section 2.1 `suggest` row says it files the idea straight into the Suggestion Box. The section 9.1 sentence says sessions file `suggestion` messages with `suggest` directly into the box, and it drops the `state_dir/box/suggestions/` intake wording.
- `chupa/docs/host-running.md`: the `suggest` row's description reads "File an idea into the Suggestion Box."
- `README.md`: the `uv run chupa suggest` line's comment reads `# file an idea into the Suggestion Box`.

Scope out:
- `chupa/drain.py` and `chupa/serve.py`; making drain ingest `report_inbox`, which is `drain-ingests-report-inbox`; triage's settling; the VS Code extension; `Box.messages()`; locking of any kind.

## Scope fence
- chupa/box.py
- chupa/__main__.py
- chupa/triage.py
- tests/integration/test_cli.py
- tests/integration/test_box.py
- tests/unit/test_suggest_box.py
- tests/integration/test_triage.py
- tests/integration/test_storm_producer.py
- tests/integration/test_daemon_composition.py
- tests/regress_suggest_lands_in_box.py
- docs/how-chupa-works.md
- chupa/docs/host-running.md
- README.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_cli.py` passes a test in which, with another process holding the writer lock, `suggest "a distinct idea"` exits 0 and `Box(<state_dir>/box).messages()` holds exactly one pending `suggestion` with that summary and origin `session`, and no `box/suggestions/` directory exists. The current code writes a drop and leaves the box empty, so it fails.
2. The same file passes a test in which filing the same summary twice prints `suggest: already in the box as <id>` the second time and leaves exactly one message. A `suggest` that creates a second message fails it.
3. `./dev.py test tests/integration/test_box.py` passes the on-disk race test: two enqueues racing for one `seq` end with two messages whose `seq` values differ. The current `_enqueue`, which writes both at the same `seq`, fails it.
4. `./dev.py test tests/unit/test_suggest_box.py` passes the leftover-claim test: with a claim for seq 1 and no message, `enqueue` returns seq 2. An implementation that retries `max(re-read seq) + 1` loops forever on seq 1 and fails it.
5. `uv run python tests/regress_suggest_lands_in_box.py` prints `{"regression_result": "pass"}` on the branch and `{"regression_result": "defect"}` at the merge base.
6. `chupa/__main__.py` and `chupa/box.py` gain no `Lockfile`, `flock`, or other lock use, checked by reading the diff.

## Verification
```
./dev.py test tests/integration/test_cli.py tests/unit/test_suggest_box.py tests/integration/test_box.py tests/integration/test_triage.py tests/integration/test_storm_producer.py tests/integration/test_inbox.py tests/unit/test_host_running.py tests/integration/test_daemon_composition.py tests/integration/test_storm_notification_activation.py tests/integration/test_provider_cooldown_failover.py
```

## Regression
```
uv run python tests/regress_suggest_lands_in_box.py
```
- carries: tests/regress_suggest_lands_in_box.py

## Definition of rejected
- Any new lock, or `suggest` taking the writer lock.
- `suggest` still writes a file under `box/suggestions/`.
- The box views list drop files or invent ids for them.
- Two concurrent enqueues can still produce two messages with the same `seq`.
- This change writes a seq claim file anywhere under the box root (claims belong in the sibling `<root>.seq` directory).
- Any file outside the scope fence changes.

## Time budget
- expected: 40m
- stuck: 90m
