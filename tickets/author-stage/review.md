# Review: snag

The core flow is wired, but `tests/test_author.py` is missing the tests for acceptance criteria 3 and 4, `open_tickets` sends the wrong content, and a broad `except` hides `go_binds` failures by silently using `go=False`.

## Findings

- [acceptance] tests/test_author.py:28 Acceptance criteria 3 and 4 have no tests. Nothing in `tests/test_author.py` shows that an existing-stem reply or a reply failing `validate_ticket` re-prompts with the findings. Nothing shows that exhausting the allowance commits no ticket and writes one `decision-<id>` record. Nothing shows that a message whose journal already has `author_invoked` gets the decision record with zero author requests. (do instead: Add FakeLLM-driven tests to `tests/test_author.py`. (a) Use an author reply naming an existing stem and one failing `validate_ticket`. Assert the retry prompt carries their findings. (b) Exhaust the retry allowance and assert no `chupa(<stem>): ticket` commit, one `decision-<id>` record, and a `decision` resolution. (c) Pre-journal `author_invoked` for a pending message with an author verdict. Assert one decision record and no request with surface `author`.)
- [acceptance] tests/test_author.py:27 The test does not check everything criterion 2 requires. It never asserts that main gains exactly one `chupa(<stem>): ticket` commit, that there is exactly one `ticket_intake` signal (`any` accepts several), or that the request key is `llm/author/0/author/<seq>/1`. (do instead: Assert the subject of the new commit on main and that it is the only one. Assert the count of `ticket_intake` signals on the stem is exactly 1. Assert the EFFECT_COMPLETION key `llm/author/0/author/<message seq>/1`.)
- [logic] chupa/author.py:88 `open_tickets` is a list of raw `tickets/*/ticket.md` paths. It includes merged tickets and leaves out each stem's `## Goal / Why` first line. The scope requires each committed non-merged stem with its `## Goal / Why` first line. (do instead: For each tracked `tickets/<stem>/ticket.md`, read and parse it. Skip it if the stem is merged (use the journal/ticket state). Emit `<stem>: <first line of ## Goal / Why>`.)
- [logic] chupa/author.py:111 A bare `except Exception` around `go_binds(...)`/`baseline_identity(...)` swallows any error, including real bugs, and silently uses `go=False`. This is a defensive parallel path the ticket does not ask for. The ticket says `go=go_binds(events, baseline_identity(config, specs_dir))`. (do instead: Call `go_binds(checkout.journal.read(), baseline_identity(checkout.config, SPECS_DIR))` directly as specified. If a specific, documented error must map to supervised, catch only that exception type.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "6bb4c6193c540c57a7f2cea69f6d90973697059a",
  "stem": "author-stage",
  "reviewed_sha": "6bb4c6193c540c57a7f2cea69f6d90973697059a",
  "summary": "The core flow is wired, but `tests/test_author.py` is missing the tests for acceptance criteria 3 and 4, `open_tickets` sends the wrong content, and a broad `except` hides `go_binds` failures by silently using `go=False`.",
  "findings": [
    {
      "code": "acceptance",
      "path": "tests/test_author.py",
      "line": 28,
      "message": "Acceptance criteria 3 and 4 have no tests. Nothing in `tests/test_author.py` shows that an existing-stem reply or a reply failing `validate_ticket` re-prompts with the findings. Nothing shows that exhausting the allowance commits no ticket and writes one `decision-<id>` record. Nothing shows that a message whose journal already has `author_invoked` gets the decision record with zero author requests.",
      "paved_road": "Add FakeLLM-driven tests to `tests/test_author.py`. (a) Use an author reply naming an existing stem and one failing `validate_ticket`. Assert the retry prompt carries their findings. (b) Exhaust the retry allowance and assert no `chupa(<stem>): ticket` commit, one `decision-<id>` record, and a `decision` resolution. (c) Pre-journal `author_invoked` for a pending message with an author verdict. Assert one decision record and no request with surface `author`."
    },
    {
      "code": "acceptance",
      "path": "tests/test_author.py",
      "line": 27,
      "message": "The test does not check everything criterion 2 requires. It never asserts that main gains exactly one `chupa(<stem>): ticket` commit, that there is exactly one `ticket_intake` signal (`any` accepts several), or that the request key is `llm/author/0/author/<seq>/1`.",
      "paved_road": "Assert the subject of the new commit on main and that it is the only one. Assert the count of `ticket_intake` signals on the stem is exactly 1. Assert the EFFECT_COMPLETION key `llm/author/0/author/<message seq>/1`."
    },
    {
      "code": "logic",
      "path": "chupa/author.py",
      "line": 88,
      "message": "`open_tickets` is a list of raw `tickets/*/ticket.md` paths. It includes merged tickets and leaves out each stem's `## Goal / Why` first line. The scope requires each committed non-merged stem with its `## Goal / Why` first line.",
      "paved_road": "For each tracked `tickets/<stem>/ticket.md`, read and parse it. Skip it if the stem is merged (use the journal/ticket state). Emit `<stem>: <first line of ## Goal / Why>`."
    },
    {
      "code": "logic",
      "path": "chupa/author.py",
      "line": 111,
      "message": "A bare `except Exception` around `go_binds(...)`/`baseline_identity(...)` swallows any error, including real bugs, and silently uses `go=False`. This is a defensive parallel path the ticket does not ask for. The ticket says `go=go_binds(events, baseline_identity(config, specs_dir))`.",
      "paved_road": "Call `go_binds(checkout.journal.read(), baseline_identity(checkout.config, SPECS_DIR))` directly as specified. If a specific, documented error must map to supervised, catch only that exception type."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
