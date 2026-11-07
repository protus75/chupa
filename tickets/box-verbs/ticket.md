---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
none

## Context
- chupa/box.py
- chupa/triage.py
- chupa/status.py
- chupa/ask.py
- chupa/specs/ask/review.md
- chupa/__main__.py
- dev.py
- tests/test_status.py
- tests/test_triage.py
- tests/test_ask.py
- tests/test_dev.py
- tests/test_box.py
- tests/test_host_running.py
- docs/how-chupa-works.md
- docs/host-running.md

## Goal / Why
The Suggestion Box holds 327 pending messages, and the operator cannot see any of them: `status` does not list the box (2026-11-06). The operator wants to read the messages and settle them by hand, one or many at a time. Triage runs only when the operator asks; nothing here triages on its own.

This is the engine half of the Suggestion Box work; `box-view` adds the snapshot and the VS Code view on top of these verbs.

After this change:
- `status` lists every Suggestion Box message and its state.
- `chupa triage [ID ...]` triages only the named messages, or every pending one when no id is given.
- `chupa dismiss ID ...` settles messages as operator decisions without a model call.
- `chupa prompt box ID ...` prints a Claude prompt for discussing the named messages.

## Scope in / Scope out
- In: `chupa/box.py`: rename `Box._path` to `Box.path` (public) and update its callers, so later consumers name a message's file without copying the filename rule.
- In: `chupa/status.py`:
  - `Status` gains the box messages, in arrival (`seq`) order, oldest first. Each has: id, class, a state label, and the summary's first line cut to 120 characters (`...` marks a cut).
  - The state label is `pending`, `reopened` (pending with `reopen: true`), `author -> <stem>` (resolution kind `ticket`), `tombstone -> <link>`, or `decision`.
  - `render` adds the block `Suggestion Box (<N> pending, <M> resolved):` after the Reject queue, with one line per message: `<id>: <class>: <label>: <summary>`. An empty box renders `(none)`, as the other blocks do.
- In: `chupa/triage.py`:
  - `triage_pass(checkout, llm, ids=frozenset())`. With ids, it settles only those pending messages; a named message that is already resolved is skipped. An id the box does not hold raises `BoxError` before the pass journals its `triage_pass` signal or makes any call.
  - New `dismiss(checkout, ids) -> list[str]`, with no model call. Every id is checked before anything is written; an unknown id raises `BoxError` and settles none of them. Each pending message gets a decision record `decision-<id>` (link: the message id; `reopen_after_days: 30`; body says it was dismissed by the operator), committed through the same Effects-keyed `ticket-plane/decisions/<record>` commit triage uses, then resolved as `decision`. An already-resolved id prints `<id>: already resolved -> <link>` and writes nothing.
- In: `chupa/ask.py` and new `chupa/specs/ask/box.md`: a `box` prompt kind. It names each message's id and its file under the state dir, and asks Claude to read them and report in plain English, ending with a "Recommendation" section of exact `./dev.py triage`, `./dev.py dismiss`, or ticket-authoring steps, matching the other ask prompts.
- In: `chupa/__main__.py`:
  - `triage` takes optional ids; `dismiss` takes one or more ids. Both hold the writer lock like `triage` does today.
  - `prompt box ID ...` takes one or more ids and takes no lock. The ticket kinds still take exactly one stem.
  - An unknown id refuses with exit 2: `chupa <verb>: unknown box id <id> -- name ids that chupa status lists`.
- In: `dev.py`: `triage [ID ...]` and `dismiss ID ...`, each passing every id to one chupa call (one triage pass, not one per id), with docstring lines.
- In: tests:
  - `tests/test_status.py`: the block lists pending and resolved messages oldest first with their labels; a multi-line summary renders as its first line only, not the whole text; a 200-character summary is cut to 117 characters plus `...`; an empty box renders `(none)`.
  - `tests/test_triage.py`:
    - `triage <id>` with two pending messages settles the named one only and makes one model call, not two;
    - an unknown id exits 2 with no model call and no `triage_pass` signal;
    - `dismiss` of two ids commits two decision records with no model call;
    - a repeated dismiss prints `already resolved` and adds no commit;
    - `dismiss <pending> <unknown>` exits 2 and leaves the pending message pending.
  - `tests/test_ask.py`: the `box` prompt names every requested id and its file under a non-default state dir.
  - `tests/test_dev.py`: `triage` and `dismiss` pass every id to a single chupa call.
  - The `Box.path` rename updates `tests/test_box.py`, `tests/test_daemon_soak.py`, and `tests/test_storm_notification_activation.py`.
- In: docs.
  - `docs/how-chupa-works.md`:
    - section 2.1: `triage [id ...]`, `dismiss`, and `prompt box`;
    - section 2.2: `./dev.py triage` and `./dev.py dismiss`;
    - section 9.2: dismiss;
    - section 10.3: the Suggestion Box block.
  - `docs/host-running.md`: a `dismiss` row in the verb table (works while serve runs: No), which `tests/test_host_running.py::test_verb_table_matches_parser` requires; the `triage` and `prompt` rows mention ids.
- Out:
  - the snapshot and anything under `vscode-chupa/` (ticket `box-view`);
  - automatic triage of any kind;
  - bulk dismissal from the CLI with no ids;
  - deleting box files;
  - a new resolution kind.

## Scope fence
- chupa/box.py
- chupa/status.py
- chupa/triage.py
- chupa/ask.py
- chupa/specs/ask/box.md
- chupa/__main__.py
- dev.py
- tests/test_status.py
- tests/test_triage.py
- tests/test_ask.py
- tests/test_dev.py
- tests/test_box.py
- tests/test_daemon_soak.py
- tests/test_storm_notification_activation.py
- docs/how-chupa-works.md
- docs/host-running.md

## Acceptance criteria
1. `./dev.py test tests/test_status.py tests/test_triage.py tests/test_ask.py tests/test_dev.py tests/test_box.py` exits 0, including every test listed in Scope in.
2. `./dev.py test tests/test_host_running.py` exits 0: the verb table lists `dismiss`.
3. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/test_status.py tests/test_triage.py tests/test_ask.py tests/test_dev.py tests/test_box.py
./dev.py test tests/test_host_running.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- anything triages without an operator command naming it (`triage`);
- `dismiss` makes a model call, or deletes or rewrites a box file other than through `Box.resolve`;
- an unknown id settles any message;
- `status` writes anything;
- anything under `vscode-chupa/` changes.

## Time budget
- expected: 60m
- stuck: 120m
