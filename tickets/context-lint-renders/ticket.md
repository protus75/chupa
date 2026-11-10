---
state: confirmed
source: human
priority: P0
kind: bug
---

## Depends on
- none

## Context
- chupa/tickets.py::context_path
- chupa/tickets.py::context_excerpt
- chupa/tickets.py::parse_ticket
- chupa/stages.py::implement_inputs
- tests/integration/test_tickets.py::complete
- tests/integration/test_tickets.py::refusal
- tests/integration/test_tickets.py::test_context_directory_is_refused
- tests/integration/test_tickets.py::test_context_binary_selector_and_fenced_heading
- tests/regress_context_directory.py
- chupa/docs/host-authoring.md#What each section is for
- docs/how-chupa-works.md#4.2 Implement

## Goal / Why
Lint admits a `## Context` entry that Implement's input render cannot read, and the render's exception stops the whole drain. On 2026-11-10 `vscode-readme-screenshot` and `vscode-marketplace-icon` listed PNG files whole in Context. `parse_ticket` reads a file's text only for a `::` or `#` selector, so the whole-file PNG entries passed `./dev.py lint`. The requisition review then called `implement_inputs`, whose `read_text()` raised `UnicodeDecodeError` and ended the drain (evidence/drain-unicode-crash.txt). This is the second instance of the defect: `context-rejects-directory` fixed a Context directory that crashed the drain in the same render, by adding one more check to lint. The root model is that lint and the render decide separately whether an entry is usable, so they can disagree again. After this change, lint admits a Context entry only if the function that renders Context text in `implement_inputs` returns its text without raising. A non-UTF-8 file is refused at lint with a finding, so the drain never reaches it.

## Scope in / Scope out
- In: `chupa/tickets.py`. Add one function that returns the rendered text of one ticket Context entry: it reads `repo / context_path(entry)` as text and passes it to `context_excerpt`. `parse_ticket` calls it for every Context entry, whole-file entries included, and turns a `ValueError` or `UnicodeError` into the existing Context finding. Keep the extension pre-check (`context_excerpt(item, None)`) ahead of the read, so `image.png#x` is still refused for its extension before any decoding. Extend the finding's paved road to say that Context embeds UTF-8 text files only, and that a binary file is named by path in `## Goal / Why` or `## Scope in / Scope out`.
- In: `chupa/stages.py`. `implement_inputs` renders each ticket Context entry by calling that same function. `config.context_files` rendering is unchanged.
- In: `tests/integration/test_tickets.py`. Add a test: a ticket whose Context lists a whole file `image.png` holding `b"\x89PNG\r\n\x1a\n"` is refused with one finding whose message names `Context` and whose paved road is present. Without the fix, `validate_ticket` admits it.
- In: `tests/regress_context_binary.py`, the carried reproducer, shaped like `tests/regress_context_directory.py`. It prints `defect` when `validate_ticket` admits the whole-file PNG Context entry, and `pass` when it is refused with a Context finding.
- In: `chupa/docs/host-authoring.md` `Context` bullet and `docs/how-chupa-works.md` §4.2: Context files are UTF-8 text, and lint renders each entry exactly as Implement does.
- Out: drain or runner exception containment (a ticket whose render raises still stops the drain; that is a separate design item), `config.context_files` validation, `## On-demand` validation, and the two vscode tickets.

## Scope fence
- chupa/tickets.py
- chupa/stages.py
- tests/integration/test_tickets.py
- tests/regress_context_binary.py
- chupa/docs/host-authoring.md
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_tickets.py` passes. It includes the new test: a whole-file Context entry naming a PNG is refused with a Context finding, not admitted.
2. `./dev.py test tests/integration/test_tickets.py -k "context_binary_selector or context_directory or context_whole_file"` passes unchanged: `image.png#x` is still refused with a message naming `.md`, a directory is still refused, and a whole text file still renders unexcerpted.
3. `uv run python tests/regress_context_binary.py` prints `{"regression_result": "pass"}` and exits 0.
4. `chupa/stages.py` `implement_inputs` contains no `read_text()` call for ticket Context entries, only the call to the new `chupa/tickets.py` function, checked by reading the branch diff.
5. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_tickets.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- lint checks binary content by file extension or a magic-byte denylist instead of rendering the entry;
- `implement_inputs` and `parse_ticket` read or excerpt ticket Context through different code paths;
- the change adds exception handling in `chupa/drain.py`, `chupa/runner.py`, or `chupa/requisition.py`;
- `image.png#x` is no longer refused for its extension.

## Time budget
- expected: 25m
- stuck: 60m

## Regression
```
uv run python tests/regress_context_binary.py
```
- carries: tests/regress_context_binary.py
