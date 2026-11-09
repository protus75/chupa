---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- none

## Context
- chupa/runner.py::verdict
- chupa/runner.py::verdict_locked
- chupa/control.py::AdmissionRequest
- chupa/control.py::validate_request
- chupa/control.py::ControlInbox.settle_admissions
- chupa/serve.py::Serve.apply_verdict
- chupa/observe.py
- tests/integration/test_control_cli.py::test_live_verdict_recovery_and_refusal
- tests/integration/test_control_cli.py::test_yes_matches_typed_verdict
- docs/how-chupa-works.md#6.6 The Reject queue, keep and kill

## On-demand
- chupa/__main__.py
- tests/integration/test_watch.py

## Goal / Why
`confirm <stem>` refuses to keep a Reject-queue stem when the previous operator keep carried the same committed `ticket.md` blob (`already kept at this ticket content; edit the ticket before re-enqueueing`). That refusal is how AI agents in chat sessions, which run `chupa confirm <stem> --yes`, are stopped from resubmitting the same unrunnable ticket over and over. It must stay for every command-line confirm.

The VS Code extension's Confirm action runs the same `confirm <stem> --yes`, so it gets the same refusal. But only a person uses the extension. On 2026-11-08 `core-drift-preflight` failed on a pytest name collision that `tests-package-init` fixed on main 20 minutes later. The ticket text was right, yet the operator could not keep it from the extension without making an edit.

After this change, the extension sends `confirm <stem> --extension`. That keep is accepted at unchanged ticket content, with or without a running serve. Command-line `confirm`, with or without `--yes`, still refuses a repeat keep at unchanged content.

## Scope in / Scope out
- In: `chupa/__main__.py`. `confirm` and `reject` gain a `--extension` flag. Like `--yes`, it skips the terminal check and the `y` prompt. `_verdict` passes it to `runner.verdict`, and when serve holds the lock it publishes the `AdmissionRequest` with `actor="extension"` instead of `"operator"`.
- In: `chupa/control.py`. The admission `actor` vocabulary becomes `operator | machine | extension` in `AdmissionRequest`, `validate_request` and `_ADMISSION_SHAPE`. `settle_admissions` passes `body["actor"]` to its verdict callback as a fourth argument.
- In: `chupa/serve.py` `apply_verdict(stem, verb, key, actor)` passes `extension=actor == "extension"` to `runner.verdict_locked`.
- In: `chupa/runner.py`. `verdict` and `verdict_locked` take a keyword `extension: bool = False`. `verdict_locked` skips the `already kept at this ticket content` refusal only when `extension` is true. Everything else is unchanged:
  - The keep signal is still `{"signal": "reject_verdict", "verdict": "keep", "actor": "operator", "ticket_sha": ...}`, so the cap fold reads it as before.
  - The `neither a draft nor in the Reject queue` refusal still applies to every caller.
- In: `chupa/observe.py`: `verdictCommands` becomes `{verb: [verb, "--extension"]}` for `confirm` and `reject`. `vscode-chupa/extension.js` already draws this argv unchanged.
- In: tests.
  - `tests/integration/test_watch.py`: the `verdictCommands` assertion expects `--extension`.
  - `tests/integration/test_control_cli.py`: the `crash_after` wrapper in `test_live_verdict_recovery_and_refusal` takes and forwards `actor`.
  - `tests/integration/test_control_cli.py`, new test built like `test_yes_matches_typed_verdict`, with serve not running:
    - Ready one stem and route it to the Reject queue, then `confirm --yes` it.
    - Route it to the Reject queue again with `ticket.md` unchanged. A second `confirm --yes` exits 2 with `already kept at this ticket content`.
    - `confirm --extension` then exits 0, and the journal holds two operator `keep` signals with the same `ticket_sha`, not one.
  - `tests/integration/test_control_cli.py`, the same repeat with serve live: a request published with `--extension` journals a second keep, and one published with `--yes` is refused with `already kept at this ticket content`.
- In: `docs/how-chupa-works.md`:
  - Section 6.6: the same-content refusal binds command-line `confirm` and not the extension's `--extension`.
  - Section 2.1, `confirm` row: name `--extension`.
- Out: machine keeps, cap folds, the keep signal's shape, `reject` semantics (it accepts `--extension` only to skip the prompt), the `ticket_changed` hold, premise parks, `dev.py`, and `vscode-chupa/`.

## Scope fence
- chupa/__main__.py
- chupa/control.py
- chupa/serve.py
- chupa/runner.py
- chupa/observe.py
- tests/integration/test_control_cli.py
- tests/integration/test_watch.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_control_cli.py` passes, including the new tests. In them, a repeat `confirm --extension` at unchanged ticket content journals a second operator keep (not exit 2), and a repeat `confirm --yes` still exits 2 with `already kept at this ticket content` (not exit 0), both with and without a live serve.
2. `./dev.py test tests/integration/test_watch.py` passes with `verdictCommands` equal to `{"confirm": ["confirm", "--extension"], "reject": ["reject", "--extension"]}`.
3. `docs/how-chupa-works.md` section 6.6 and the `confirm` row in section 2.1 name `--extension` and say the same-content refusal binds the command line only.
4. `./dev.py test` passes.

## Verification
```
./dev.py test tests/integration/test_control_cli.py tests/integration/test_watch.py
./dev.py test
```

## Definition of rejected
A command-line `confirm` (with or without `--yes`) keeps a stem at unchanged ticket content after a prior operator keep, the extension's confirm is still refused at unchanged content, or the keep signal's `actor` stops being `operator`.

## Time budget
- expected: 40m
- stuck: 90m
