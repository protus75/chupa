---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- none

## Context
- chupa/__main__.py::_new
- chupa/tickets.py::missing_evidence_findings
- chupa/docs/host-authoring.md#Workflow
- chupa/docs/host-authoring.md#Bug tickets

## On-demand
- dev.py
- docs/how-chupa-works.md
- README.md
- tests/integration/test_cli.py
- tests/integration/test_tickets.py

## Goal / Why
`chupa new <stem> --kind bug` writes a bug ticket with no evidence. It prints a "has no evidence file" finding and exits 0, and the authoring guide puts evidence at step 3, after the sections are filled. So the ticket body gets written before anyone has captured the failure it fixes. The evidence comes later, or never, and the ticket fails at lint or intake for something that should have existed before the first line was written. On 2026-11-11, a session authored `requisition-prior-review` this way: the skeleton was created first and the evidence was gathered afterwards. The owner reports that bug tickets "just fail later all the time for stuff that should have been there from the onset."

When this ticket is done, a bug ticket cannot be started without its evidence. `new --kind bug` requires `--evidence <file>...` and copies those files into `tickets/<stem>/evidence/` when it writes the skeleton.

## Scope in / Scope out
- In: `chupa/__main__.py`:
  - The `new` parser gains `--evidence PATH [PATH ...]` (`nargs="+"`). `main` passes it to `_new`.
  - `_new(repo, stem, kind="feature", evidence=())` checks, before writing any file:
    - `kind == "bug"` with no evidence refuses (exit 2). The message says a bug ticket needs its evidence first. The paved road says to save the observed failure (output, log excerpt, or captured command output) to a file, then rerun `new <stem> --kind bug --evidence <file>`.
    - `--evidence` with `feature` or `chore` refuses (exit 2): evidence is for bug tickets.
    - Each path resolves against `repo` when relative, and must be an existing regular file that is not a symlink. Otherwise it refuses and names the path.
    - Two paths with the same file name refuse.
  - After the existing stem checks pass, `_new` writes the skeleton as today. It then copies each evidence file byte for byte to `tickets/<stem>/evidence/<name>`. The existing missing-evidence finding therefore no longer prints for a bug.
  - Every refusal leaves `tickets/<stem>/` uncreated.
- In: `dev.py`: its `new` parser gains the same `--evidence` argument and forwards it to `chupa new`.
- In: documentation:
  - `chupa/docs/host-authoring.md` Workflow:
    - Step 1 says a bug starts by saving the observed failure to a file and passing it with `--evidence`.
    - Step 3 ("For a bug, add the evidence file") is removed and the steps renumbered.
    - The Evidence subsection says `new` copies the files there.
  - `docs/how-chupa-works.md`: the `new` rows in the verb table (around line 57) and the dev command table (around line 93) say bugs require `--evidence` and that `new` copies the files into `tickets/<stem>/evidence/`. The "no evidence files are created" clause goes.
  - `README.md`: the `./dev.py new` line shows `[--evidence FILE...]`.
- Out:
  - Lint and intake evidence checks, which stay as they are.
  - The Author stage, which writes its own evidence.
  - `CLAUDE.md` and `AGENTS.md` managed blocks.

## Scope fence
- chupa/__main__.py
- dev.py
- chupa/docs/host-authoring.md
- docs/how-chupa-works.md
- README.md
- tests/integration/test_cli.py
- tests/integration/test_tickets.py
- tests/unit/test_new_evidence.py

## Acceptance criteria
1. New `tests/unit/test_new_evidence.py` never touches disk. It calls `_new` with a repo path that does not exist, and asserts that each of these raises `Refusal` before any file I/O. This keeps the `test-gate.toml` floor of 13 for `chupa/__main__.py`.
   - `kind="bug"` with no evidence. The road names `--evidence`.
   - `kind="feature"` with evidence `("x.txt",)`.
2. `tests/integration/test_cli.py::test_new_kind_flag`, rewritten:
   - `new fix-thing --kind bug` with no `--evidence` exits 2 and leaves `tickets/fix-thing` absent.
   - `new fix-thing --kind bug --evidence out.txt` (a file in the repo) exits 0.
     - `tickets/fix-thing/evidence/out.txt` has the same bytes as `out.txt`.
     - stdout has no "no evidence file" line.
     - `kind: bug` and `## Regression` are in the ticket.
3. `tests/integration/test_tickets.py`:
   - `test_new_bug_creates_no_evidence` becomes a test that `new t-bug --kind bug --evidence <file>` creates exactly `tickets/t-bug/ticket.md` and `tickets/t-bug/evidence/<file name>`.
   - `test_new_prints_bug_evidence_finding` passes evidence and asserts the missing-evidence finding is absent.
   - New cases each exit 2 and create no `tickets/<stem>` directory:
     - A missing evidence path.
     - A directory.
     - A symlink.
     - Two paths with the same file name.
     - `--kind feature --evidence <file>`.
4. `chupa/docs/host-authoring.md`'s Workflow has no step that adds evidence after `new`, and step 1 names `--evidence`.
5. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
- `new --kind bug` without evidence exits 0 or writes any file.
- A refused `new` leaves a partial `tickets/<stem>/` behind.
- Lint or intake evidence rules change.

## Time budget
- expected: 30m
- stuck: 60m
