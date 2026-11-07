---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
none

## Runs before
- status-optional-locks
- soak-report-head-race

## Context
- chupa/__main__.py
- chupa/box.py
- chupa/triage.py
- chupa/serve.py
- chupa/seams.py
- chupa/inbox.py
- dev.py
- CLAUDE.md
- docs/how-chupa-works.md
- docs/host-running.md
- tests/test_cli.py
- tests/test_triage.py
- tests/test_dev.py
- tests/test_host_running.py

## Goal / Why
A chat session has no way to put an idea into the Suggestion Box. Only engine stages enqueue messages, and `report_inbox` takes only host bug reports in a closed schema. So sessions end replies with loose "want me to file a ticket for X?" offers, which are lost when the chat ends or become hand-written tickets nobody triaged. The operator decided on 2026-11-07 that chats file potential ideas to the box instead.

After this change, `chupa suggest "<summary>"` (in this repo, `./dev.py suggest "<summary>"`) records the idea, and it becomes a pending `suggestion` message that `triage` settles like any other. It works while a drain or serve holds the writer lock: the verb only drops a file, and the lock holder ingests it. Session conduct tells chats to use it.

## Scope in / Scope out
- In: `chupa/__main__.py`: a `suggest` verb with one positional `summary`. It takes no lock and runs no intake.
  - A blank or whitespace-only summary is an engine refusal: exit 2, `chupa suggest: blank summary -- pass the idea as one quoted argument`.
  - Otherwise it publishes `{"summary": <summary>}` as JSON to `<state_dir>/box/suggestions/<uuid4 hex>.json` with `checkout.fs.publish`, prints `suggest: queued <file name>`, and exits 0.
- In: `chupa/triage.py` `report_intake` ingests suggestion drops in both of its branches (with and without `report_inbox`), before it returns the box. Serve's `box_intake` and `triage_pass` already call it. For each `<state_dir>/box/suggestions/*.json`, in sorted name order:
  - `box.enqueue(message_class="suggestion", origin="session", summary=<summary>, occurrence_id=<file stem>)`;
  - then `checkout.fs.replace` moves the file to `<state_dir>/box/suggestions/consumed/<same name>`.
  - A file that is not a JSON object with exactly one nonblank string `summary` stays where it is and is logged as `suggestion_intake_refused` with the file name, the way `ingest` logs `report_intake_refused`. Other drops still ingest.
  - A crash between `enqueue` and `replace` must not create a second message on the next intake. The same summary folds into the existing message by signature.
- In: `dev.py`: a `suggest` subcommand taking one `summary` argument and running `chupa suggest <summary>`, with a docstring line.
- In: `CLAUDE.md` section B (Session conduct), a new bullet after **Announce unsolicited dives**: **File ideas to the box.** A potential idea, improvement, or second problem a session notices but the user did not ask for is filed with `./dev.py suggest "<summary>"`, not offered as a loose ticket suggestion in the reply. The reply names what was filed in one line. Why: a margin suggestion dies with the chat, while the box keeps it for triage. `AGENTS.md` has no session-conduct section, so it does not change.
- In: `docs/how-chupa-works.md`: a section 2.1 verb row for `suggest` (Lock: no), a section 2.2 row for `./dev.py suggest`, and a sentence in section 9.1 saying sessions file `suggestion` messages with `suggest`, which `triage` and serve's box intake ingest from `state_dir/box/suggestions/`.
- In: `docs/host-running.md`: a `suggest` verb-table row (works while serve runs: Yes), which `tests/test_host_running.py::test_verb_table_matches_parser` requires.
- In: tests:
  - `tests/test_cli.py`: `suggest` writes exactly one `*.json` under `<state_dir>/box/suggestions/` whose JSON is `{"summary": ...}`, adds no journal event, and exits 0 while another process holds the writer lock. A blank summary exits 2 and writes no file.
  - `tests/test_triage.py`: two drops ingest as two pending `suggestion` messages with `origin` `session` and the dropped summaries, and both files move to `consumed/`. A malformed drop stays in place and creates no message, while a valid one beside it still ingests. Running `report_intake` again after a drop was enqueued but not moved leaves exactly one message, not two. With `report_inbox` unset, drops still ingest.
  - `tests/test_dev.py`: `./dev.py suggest "an idea"` runs `["uv", "run", "python", "-m", "chupa", "suggest", "an idea"]`.
- Out: triage's settling logic and spec; the Author stage; `report_inbox` and `inbox.ingest`; new message classes or fields; any summary length cap; the VS Code extension; `AGENTS.md`; the managed engine-conduct block.

## Scope fence
- chupa/__main__.py
- chupa/triage.py
- dev.py
- CLAUDE.md
- docs/how-chupa-works.md
- docs/host-running.md
- tests/test_cli.py
- tests/test_triage.py
- tests/test_dev.py

## Acceptance criteria
1. `./dev.py test tests/test_cli.py tests/test_triage.py tests/test_dev.py tests/test_host_running.py` exits 0, including the tests above. The lock-held test fails if `suggest` takes or waits on the lock. The retry test fails if a second message appears. The malformed-drop test fails if the bad file is consumed or blocks the valid one.
2. `CLAUDE.md` section B contains the **File ideas to the box.** bullet naming `./dev.py suggest`, and the managed `## Engine conduct` block at the top is byte-for-byte unchanged.
3. `docs/how-chupa-works.md` sections 2.1, 2.2, and 9.1, and `docs/host-running.md`'s verb table, name `suggest`.
4. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/test_cli.py tests/test_triage.py tests/test_dev.py tests/test_host_running.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- `suggest` takes the writer lock, runs intake, writes the journal, or writes a box message file directly;
- a drop is consumed without becoming a message, or a retried drop becomes two messages;
- a new message class, message field, or config key is added;
- triage's settling behavior or the Author stage changes;
- the managed engine-conduct block in `CLAUDE.md` or any part of `AGENTS.md` changes.

## Time budget
- expected: 45m
- stuck: 120m
