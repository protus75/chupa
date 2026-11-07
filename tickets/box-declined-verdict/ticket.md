---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- box-view

## Runs before
- tests-split

## Context
- chupa/box.py
- chupa/triage.py
- chupa/author.py
- chupa/status.py
- vscode-chupa/media/box.js
- dev.py
- tests/integration/test_box.py
- tests/integration/test_dev.py
- tests/integration/test_status.py

## On-demand
- chupa/specs/triage.md
- chupa/observe.py
- chupa/__main__.py
- docs/how-chupa-works.md
- tests/integration/test_triage.py
- tests/integration/test_author.py
- tests/integration/test_watch.py
- tests/integration/test_cli.py
- tests/integration/test_flake.py
- tests/integration/test_serve.py
- tests/integration/test_retro_box.py
- tests/integration/test_storm_producer.py
- tests/integration/test_storm_notification_activation.py
- eval/daemon_soak.py

## Goal / Why
The operator read `resolution: decision` on a settled Suggestion Box message and could not tell what it meant (2026-11-07). `author` and `tombstone` name their outcome; `decision` does not. The verdict means triage chose not to build the message. After this change that verdict is called `declined` everywhere it is stored, shown, or asked of the model, and one command migrates the operator's existing box state.

The registry keeps its name: `tickets/decisions/` holds both declined and tombstone records, so `DECISIONS_DIR`, `DecisionRecord`, `read_registry`, the `chupa(decisions):` commit prefix, and the `ticket-plane/decisions/<record_id>` effect key stay as they are.

## Scope in / Scope out
- In: the verdict value `decision` becomes `declined` in every closed set that holds it:
  - `chupa/box.py`: `Verdict.verdict`, `Resolution.kind`, `DecisionRecord.kind`;
  - `chupa/triage.py`: `TriageReply.verdict`, the `_record` `kind` parameter, every `"decision"` literal (dismiss, superseded author verdict, unresolvable tombstone link), the `reopen_after_days` error text, and the existing-record lookup `f"decision-{message.id}"`;
  - `chupa/author.py`: `failure_decision` records `kind="declined"` with id `declined-<message id>`;
  - record ids built from the kind become `declined-<message id>`.
- In: names that mean this verdict are renamed with it: `failure_decision` to `failure_declined`, `AuthorOutcome.decision` to `AuthorOutcome.declined`, and the `decision -> <id>` triage output lines to `declined -> <id>`. Every call site changes in the same diff.
- In: `chupa/specs/triage.md`: the reply vocabulary and every prose use of the verdict say `declined`. The registry heading and the `decisions` data block keep their names.
- In: `chupa/status.py`: the resolved label is `declined`.
- In: `chupa/observe.py`: `boxCounts` key `decision` becomes `declined`.
- In: `vscode-chupa/media/box.js`: the header reads `c.declined` and prints `<n> declined`.
- In: a new `chupa migrate-box` verb that takes the writer lock (refusing exit 2 when held, as `dismiss` does) and rewrites `<state_dir>/box/*.json`:
  - It reads each file as raw JSON, because the old value no longer validates as `Message`.
  - A file whose `resolution.kind` is `decision` gets `declined`. A `resolution.link` that starts `decision-` gets `declined-` in its place.
  - It writes through the `FileSystem` seam and prints one `<id>: decision -> declined` line per changed file, then `migrate-box: <n> migrated`.
  - A second run changes no file and prints `migrate-box: 0 migrated`.
- In: `dev.py` gains `migrate-box`, which runs `chupa migrate-box`.
- In: tests:
  - every existing assertion or fixture using the box `decision` value or `decision-` record id flips to `declined`, including the `Verdict`/`Resolution` fixtures in `tests/integration/test_storm_producer.py` and `tests/integration/test_storm_notification_activation.py`;
  - `tests/integration/test_box.py`: migrating a box with one `decision` resolution, one `tombstone`, and one pending message rewrites only the first, so `Box.messages()` loads all three. A migration that leaves `decision`, rewrites the tombstone, or drops the link prefix fails;
  - `tests/integration/test_box.py`: `Resolution(kind="decision", ...)` raises `ValidationError`, not accepted;
  - `tests/integration/test_cli.py`: `migrate-box` exits 2 and changes no file while the lock is held; a second run reports `0 migrated`;
  - `tests/integration/test_dev.py`: `migrate-box` forwards to `chupa migrate-box`.
- In: `docs/how-chupa-works.md`:
  - section 9.2 describes `declined`;
  - the `triage.md` row in the spec table lists `author / tombstone / declined`;
  - the section 2.1 verb table adds `migrate-box`;
  - the section 2.2 `./dev.py` table adds `migrate-box`.
- In: `docs/host-running.md`: the verb table adds `migrate-box` (works while serve runs: No, it takes the writer lock), so `tests/unit/test_host_running.py::test_verb_table_matches_parser` passes.
- Out:
  - every file under `tickets/`: the committed `tickets/decisions/decision-*.md` records are renamed to `declined-*.md` by the operator right after merge, outside this branch;
  - the control-plane `decision` field (`control_decision`, kill/stop/pause/storm journal bodies) and every unrelated prose use of the word;
  - the registry directory, `DecisionRecord` class name, commit prefix, and effect keys;
  - `chupa/specs/triage.md` frontmatter `version`;
  - `reopen_after_days` behavior;
  - `CHUPA_PLAN.md` and past journal events.

## Scope fence
- chupa/box.py
- chupa/triage.py
- chupa/author.py
- chupa/status.py
- chupa/observe.py
- chupa/__main__.py
- chupa/specs/triage.md
- vscode-chupa/media/box.js
- dev.py
- docs/how-chupa-works.md
- docs/host-running.md
- eval/daemon_soak.py
- tests/integration/test_box.py
- tests/integration/test_triage.py
- tests/integration/test_author.py
- tests/integration/test_watch.py
- tests/integration/test_status.py
- tests/integration/test_cli.py
- tests/integration/test_dev.py
- tests/integration/test_flake.py
- tests/integration/test_serve.py
- tests/integration/test_retro_box.py
- tests/integration/test_storm_producer.py
- tests/integration/test_storm_notification_activation.py

## Acceptance criteria
1. `./dev.py test tests/integration/test_box.py tests/integration/test_triage.py tests/integration/test_author.py tests/integration/test_watch.py tests/integration/test_status.py tests/integration/test_cli.py tests/integration/test_dev.py tests/integration/test_flake.py tests/integration/test_serve.py tests/integration/test_retro_box.py` exits 0, including every new test in Scope in.
2. `git grep -n -e '"decision"' -e 'decision-{' -e 'c.decision' -- chupa/box.py chupa/triage.py chupa/author.py chupa/status.py chupa/observe.py vscode-chupa/media/box.js eval/daemon_soak.py` prints nothing: no box verdict literal, count key, or record-id prefix survives. (The control plane's `body["decision"]` lives in other files and is out of scope.)
3. The branch changes no file under `tickets/`.
4. `node --check vscode-chupa/media/box.js` exits 0.
5. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_box.py tests/integration/test_triage.py tests/integration/test_author.py tests/integration/test_watch.py tests/integration/test_status.py tests/integration/test_cli.py tests/integration/test_dev.py tests/integration/test_flake.py tests/integration/test_serve.py tests/integration/test_retro_box.py
node --check vscode-chupa/media/box.js
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- any model or reader accepts both `decision` and `declined` (a compatibility path instead of the migration);
- `migrate-box` validates through `Message` before rewriting, so it refuses the files it exists to fix;
- the control-plane `decision` fields, the registry directory, the commit prefix, or effect keys change;
- the tombstone record or any pending box message is rewritten.

## Time budget
- expected: 60m
- stuck: 120m
