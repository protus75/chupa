---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
none

## Context
- chupa/__main__.py
- chupa/tickets.py
- tests/test_cli.py
- dev.py
- vscode-chupa/extension.js
- vscode-chupa/package.json
- docs/how-chupa-works.md
- vscode-chupa/snapshot.py
- docs/host-running.md

## On-demand
- docs/host-authoring.md

## Goal / Why
Reordering a ticket that has not run yet means hand-editing its `priority:` frontmatter or its `## Runs before` section. The operator's VS Code extension (`vscode-chupa`) needs right-click "Set priority…" and "Run before…" on queued and blocked tickets. Editing ticket text in JavaScript would be a second implementation of the ticket format that `chupa/tickets.py` owns, so the edit belongs in a chupa verb that the extension calls (2026-11-06).

After this change, `chupa order <stem> [--priority P0|P1|P2|P3] [--runs-before [STEM ...]]` rewrites only those two parts of `tickets/<stem>/ticket.md` in the working tree. It validates the result with the intake lint before writing, and intake commits the edit like any other hand edit.

## Scope in / Scope out
- In: `chupa/__main__.py` adds the `order` verb, beside `new`.
  - It takes no lock, because authorship is outside the lock fence, as with `new`. It writes through `LocalFileSystem`.
  - It requires at least one of `--priority` and `--runs-before`.
- In: what it does.
  - `--priority` replaces the frontmatter `priority:` value.
  - `--runs-before STEM ...` replaces the `## Runs before` bullets with those stems, adding the section if absent.
  - `--runs-before` with no stems removes the section.
  - Every other byte of the file is unchanged.
- In: refusals. Each one is a `runner.Refusal` with a paved road, and leaves the file untouched:
  - a bad or missing stem;
  - a stem whose journaled last state is settled, `rejected`, or `running` ("editing a ticket during its run stops it with ticket_changed; reorder it after the run ends");
  - neither option given;
  - a result that fails `validate_ticket`, which covers self-edges, unknown stems, and `Runs before` cycles. The refusal names the first finding.
- In: on success it prints the changed fields and exits 0.
- In: the edit helper lives in `chupa/tickets.py` beside `template`: a pure function from ticket text to new text, so the verb only validates and writes.
- In: `dev.py`: `./dev.py order STEM [--priority P] [--runs-before [STEM ...]]` passes through to `chupa order`.
- In: `vscode-chupa`. On queued and blocked rows only, the Tickets right-click menu gains:
  - "Set priority…": a quick pick of P0–P3 with the current one marked;
  - "Run before…": a multi-select quick pick of the other unmerged stems, with the current `runsBefore` preselected.

  Each runs `./dev.py order` with `execFile` (argv list, repo root as cwd). Each shows the command's refusal text in an error message on a non-zero exit, and refreshes the snapshot on success. Both commands are declared in `package.json` with `webview/context` entries using the existing `chupaSection` context key, and are hidden from the command palette.
- In: tests in `tests/test_cli.py`:
  - `test_order_sets_priority`: only the `priority:` line changes;
  - `test_order_sets_and_clears_runs_before`;
  - `test_order_refuses_cycle_and_leaves_file`;
  - `test_order_refuses_running_and_settled`;
  - `test_order_takes_no_lock`: no `.chupa` dir is created.
- In: docs.
  - `docs/how-chupa-works.md` section 2.1: a row for `order`.
  - Section 2.2: a row for `./dev.py order`.
  - `docs/host-authoring.md`: one sentence beside `Runs before` naming `chupa order`.
  - `docs/host-running.md`: an `order` row in the verb table beside `new`, "Works while serve runs?" = Yes.
- Out: `Depends on` edits, all other frontmatter fields, intake, and the scheduler.

## Scope fence
- chupa/__main__.py
- chupa/tickets.py
- tests/test_cli.py
- dev.py
- vscode-chupa/extension.js
- vscode-chupa/package.json
- docs/how-chupa-works.md
- docs/host-authoring.md
- docs/host-running.md

## Acceptance criteria
1. `uv run pytest -q tests/test_cli.py` exits 0, including the five tests above.
2. `node --check vscode-chupa/extension.js` exits 0, and `vscode-chupa/package.json` declares both commands with `webview/context` entries limited to queued and blocked rows.
3. `docs/how-chupa-works.md` sections 2.1 and 2.2, `docs/host-authoring.md`, and the `docs/host-running.md` verb table describe `order`.
4. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_cli.py
node --check vscode-chupa/extension.js
uv run pytest -q
```

## Definition of rejected
Reject the branch if `order` takes the writer lock, commits, edits any byte outside the `priority:` line and the `## Runs before` section, writes a ticket that fails `validate_ticket`, edits a running, settled, or rejected ticket, or if the extension edits ticket text itself.

## Time budget
- expected: 45m
- stuck: 120m
