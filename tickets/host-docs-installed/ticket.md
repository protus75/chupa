---
state: confirmed
source: human
priority: P0
kind: feature
---

## Depends on
none

## Context
- chupa/__main__.py::_parser
- chupa/__main__.py::_new
- dev.py
- docs/host-authoring.md
- docs/host-running.md
- tests/unit/test_host_running.py
- tests/integration/test_tickets.py::test_new_prints_bug_evidence_finding
- tests/integration/test_dev.py::test_suggest_forwards_summary

## On-demand
- docs/host-contract.md
- docs/how-chupa-works.md
- tests/integration/test_host_contract.py

## Goal / Why
The host guides (`docs/host-authoring.md`, `docs/host-running.md`, `docs/host-contract.md`) are not in the wheel, which ships only the `chupa` package. A host that installs chupa has no local copy; the only pointers are GitHub links in the README. Agents in a host cannot read them, so they write tickets and run chupa from memory. When this ticket is done, the three guides live inside the installed package (as `chupa/specs/*.md` already do), `chupa docs` prints each one's absolute installed path, and `chupa new` prints the authoring guide's path when the agent needs it. Agents read the guides from the local install, never from a URL. `core-authoring-first` then tells every session to run `chupa docs`.

## Scope in / Scope out
- In: `git mv` the three guides from `docs/` to `chupa/docs/`. Their relative links to each other keep working. Replace each link from a moved guide to `how-chupa-works.md` with plain text, since that file is not shipped.
- In: new verb `chupa docs`, no lock, no arguments, dispatched in `main` before any config or checkout is read, like `migrate-config`. It prints one line per guide: `<absolute path>  <one-line purpose>`, in the order authoring, running, contract. Paths resolve from the `chupa` package directory (`Path(chupa.__file__).parent / "docs"`), never from the repo or cwd. Add the row to the verb table in `chupa/docs/host-running.md` and to `docs/how-chupa-works.md` section 2.1.
- In: `./dev.py docs` forwards to `chupa docs`, like `suggest`; add it to `docs/how-chupa-works.md` section 2.2.
- In: `_new` prints `read the ticket authoring guide before filling sections: <path>` after `authored <rel>`. The refusal for an existing ticket names the same path in its paved road: `read <path>, then edit it in place, or pick a new stem`.
- In: update every other reference to the old paths: `README.md` and `vscode-chupa/README.md` links (same GitHub form, new path), the `_parser` description in `chupa/__main__.py` (name `chupa docs`), the `config.yaml` first-line comment, `docs/how-chupa-works.md`, `CLAUDE.md` and `AGENTS.md` outside the `chupa:core` markers if they name a moved file, and the tests that read the guides by path.
- Out: the guides' content beyond the link changes above; `docs/how-chupa-works.md` stays in `docs/`; `CORE_TEMPLATE`; `CHUPA_PLAN.md`.

## Scope fence
- docs/host-authoring.md
- docs/host-running.md
- docs/host-contract.md
- chupa/docs
- chupa/__main__.py
- dev.py
- docs/how-chupa-works.md
- README.md
- vscode-chupa/README.md
- config.yaml
- CLAUDE.md
- AGENTS.md
- tests/unit/test_host_running.py
- tests/integration/test_host_contract.py
- tests/integration/test_tickets.py
- tests/integration/test_cli.py
- tests/integration/test_dev.py
- tests/unit/test_docs_verb.py

## Acceptance criteria
1. The three guides exist under `chupa/docs/` and not under `docs/`, checked by `./dev.py test tests/unit/test_host_running.py tests/unit/test_docs_verb.py tests/integration/test_host_contract.py` reading them at the new paths.
2. A test in `tests/integration/test_cli.py` runs `chupa docs` and asserts three lines, each path absolute, existing, and under `Path(chupa.__file__).parent`, not under the test's repo root, and not a URL.
3. A test in `tests/integration/test_tickets.py` asserts `_new` prints the authoring guide's installed path, and that the already-exists refusal's paved road contains the same path.
4. `tests/integration/test_dev.py` asserts `./dev.py docs` forwards to `["uv", "run", "python", "-m", "chupa", "docs"]`.
5. New `tests/unit/test_docs_verb.py` calls `chupa.__main__.main` with `["docs"]` under `capsys` and asserts three lines in the order authoring, running, contract, each path starting with `str(Path(chupa.__file__).parent / "docs")`. It touches no disk and makes no existence checks; this unit test covers the `docs` branch for the `chupa/__main__.py` coverage floor in `test-gate.toml`.
6. `git grep -nE "docs/host-(authoring|running|contract)\.md"` outside `tickets/` and `CHUPA_PLAN.md` returns nothing.

## Verification
```
./dev.py test tests/unit/test_host_running.py tests/unit/test_docs_verb.py tests/integration/test_host_contract.py tests/integration/test_cli.py tests/integration/test_tickets.py tests/integration/test_dev.py
```

## Definition of rejected
A guide's content changes beyond the link changes named above, a printed path is a URL or resolves from the repo or cwd, or `CHUPA_PLAN.md` is edited.

## Time budget
- expected: 30m
- stuck: 75m
