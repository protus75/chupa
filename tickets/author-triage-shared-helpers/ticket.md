---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
- author-open-tickets-deleted

## Context
- chupa/author.py::_goal
- chupa/author.py::_open_tickets
- chupa/author.py::_commit_record
- chupa/author.py::author
- chupa/triage.py::_committed
- chupa/triage.py::_commit_record
- chupa/triage.py::_goal
- chupa/triage.py::_record
- chupa/triage.py::_settle_pass
- chupa/status.py::last_states
- tests/integration/test_drain.py::make_root
- tests/integration/test_drain.py::commit_ticket
- tests/integration/test_drain.py::pause_checkout

## Goal / Why
`chupa/author.py` and `chupa/triage.py` each carry their own copy of `_goal` and `_commit_record` (identical), and each builds its own open-ticket list for its prompt's `open_tickets` input. The two lists have drifted: author lists `git ls-files` index entries, reads them from disk, and builds a journal state map by hand; triage's inline loop in `_settle_pass` globs `tickets/*/ticket.md` on disk and keeps stems that are committed at HEAD (`_committed`) and not merged per `chupa.status.last_states`. The drift already produced one crash (author-open-tickets-deleted).

After this change there is exactly one copy of each helper, in `chupa/author.py`, and both stages build `open_tickets` with the same function using triage's semantics, so the two prompts can no longer disagree about which tickets are open.

## Scope in / Scope out
- In: `chupa/author.py` owns the single copy of four public functions, named without the leading underscore because `chupa/triage.py` imports them (triage already imports only public names from author):
  - `goal(text)`: the body of today's `_goal`, unchanged.
  - `commit_record(checkout, driver, record_id)`: the body of today's `_commit_record`, unchanged.
  - `committed(checkout, path)`: the body of today's `triage._committed`, unchanged.
  - `list_open_tickets(checkout) -> str`: for each `tickets/*/ticket.md` on disk in sorted order, a `"<stem>: <goal>"` line when the path is `committed` at HEAD and the stem's `last_states(checkout.journal.read())` value is not `"merged"`; lines joined with `"\n"`. It replaces `_open_tickets` and its hand-built states dict; it is not named `open_tickets` because both callers already bind a local `open_tickets`.
- In: `author()` calls `list_open_tickets`; `failure_declined` calls `commit_record`.
- In: `chupa/triage.py` deletes its `_committed`, `_commit_record`, `_goal` and the inline `open_tickets` loop in `_settle_pass`; it imports `commit_record`, `committed` and `list_open_tickets` from `chupa.author` and uses them at every former call site (`_record`, the record recovery and tombstone-link checks in `_settle_pass`). `_settle_pass` keeps its own `merged` list, which still feeds the `merged` prompt input and the tombstone check. `chupa/triage.py` imports `goal` only if a remaining line still uses it.
- In: `tests/regress_author_open_tickets_deleted.py` (created by author-open-tickets-deleted) now calls `author.list_open_tickets`; its fake checkout gains `git.rev_parse`, an async function that returns a sha string for any argument, so `live` counts as committed. Its pass/defect/error mapping and printed JSON are unchanged; on the branch head it prints `pass`.
- In: new test `test_list_open_tickets_requires_disk_commit_and_not_merged` in `tests/integration/test_author.py`. It builds a real repo with `make_root` and `commit_ticket`, and a checkout with `pause_checkout`:
  - `live`: committed and on disk; listed as `live: <its goal line>`.
  - `gone`: committed, then its `ticket.md` deleted from disk without committing the deletion; not listed (rules out the old index-based listing, which lists or crashes on it).
  - `draft`: written to disk, never committed; not listed (rules out a disk-only glob).
  - `done`: committed and on disk, with a journal `STATE_TRANSITION` to `merged`; not listed (rules out dropping the merged filter).
  The test asserts the return value equals exactly the one `live` line.
- Out: any change to prompt specs (`chupa/specs/author.md`, `chupa/specs/triage.md`) or their inputs' format; the other `ls_files` callers in `chupa/author.py` and `chupa/daemon.py`; any other helper shared between the two modules; new abstractions beyond moving these four functions.
- Docs: `docs/how-chupa-works.md` does not name these private helpers or describe the open-ticket listing, so it is unchanged.
- In: new `tests/unit/test_author.py` with fakes and no disk, for the `chupa/author.py` unit coverage floor:
  - `test_committed_true_when_rev_parse_resolves`: a fake `git.rev_parse` returning a sha gives `True`, not `False`.
  - `test_committed_false_on_git_error`: a fake `git.rev_parse` raising `GitError` gives `False`, not a propagated exception.
  - `test_goal_first_nonblank_line`: `goal("x\n## Goal / Why\n\n  first  \nsecond\n")` returns `"first"`, not `""` or `"second"`; text without the heading returns `""`.
  `list_open_tickets` is covered by the integration test above; a unit test cannot build the on-disk repo it lists.
- Unaffected tests: `tests/integration/test_box.py`, `test_checkpoint.py`, `test_cli.py`, `test_daemon_composition.py`, `test_daemon_soak.py`, `test_daemon_soak_runner.py`, `test_daemon_tasks.py`, `test_fixture_host.py`, `test_heartbeat.py`, `test_hostfiles.py`, `test_inbox.py`, `test_merge.py`, `test_provider_cooldown_failover.py`, `test_retro.py`, `test_retro_box.py`, `test_serve.py`, `test_triage.py` and `test_watchdog_activation.py` reference none of `_goal`, `_commit_record`, `_committed` or `_open_tickets`; their only patches of these modules (`triage.triage_pass`, and `test_triage.py`'s `triage.author`) target names this ticket keeps; and none asserts the `open_tickets` prompt input (`test_retro_box.py` and `test_triage.py` check only message fields in rendered prompts), so the listing's new semantics leave their results unchanged.

## Scope fence
- chupa/author.py
- chupa/triage.py
- tests/integration/test_author.py
- tests/unit/test_author.py
- tests/regress_author_open_tickets_deleted.py

## Acceptance criteria
1. `./dev.py test tests/integration/test_author.py -k list_open_tickets` passes: the result is exactly the `live` line, not one that also lists `gone`, `draft` or `done`, and the call does not raise `FileNotFoundError` on `gone`.
2. `uv run python tests/regress_author_open_tickets_deleted.py` prints `{"regression_result": "pass"}` and exits 0, not `error` from a fake checkout missing `rev_parse`.
3. `uv run python -c "import chupa.triage as t; assert not any(hasattr(t, n) for n in ('_goal', '_commit_record', '_committed'))"` exits 0: triage holds no copy of the moved helpers.
4. `uv run python -c "import chupa.author as a; assert not any(hasattr(a, n) for n in ('_goal', '_commit_record', '_open_tickets'))"` exits 0: author keeps only the public names.
5. `./dev.py test tests/unit/test_author.py` passes: `committed` is `True` on a resolved `rev_parse` and `False`, not raising, on `GitError`; `goal` returns the first non-blank line after the heading, not `""` or the second line.
6. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_author.py -k list_open_tickets
uv run python tests/regress_author_open_tickets_deleted.py
uv run python -c "import chupa.triage as t; assert not any(hasattr(t, n) for n in ('_goal', '_commit_record', '_committed'))"
uv run python -c "import chupa.author as a; assert not any(hasattr(a, n) for n in ('_goal', '_commit_record', '_open_tickets'))"
./dev.py test tests/unit/test_author.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- `chupa/author.py` imports from `chupa.triage`;
- either module keeps a second copy of a moved helper, or a compatibility alias for an old name;
- `list_open_tickets` catches `FileNotFoundError` or any broader exception instead of listing only paths present on disk;
- `list_open_tickets` builds its own journal state map instead of calling `last_states`;
- the reproducer's pass/defect/error mapping or its `"live: live goal"` expectation changes.

## Time budget
- expected: 30m
- stuck: 90m
