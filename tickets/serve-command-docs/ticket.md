---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
- remove-merge-hold
- serve-live-verdicts

## Context
- dev.py
- chupa/__main__.py
- docs/how-chupa-works.md
- docs/host-contract.md
- docs/host-authoring.md
- pyproject.toml
- chupa/lockfile.py
- tests/test_host_contract.py

## Goal / Why
Hosts don't know how to run chupa. Nothing chupa ships tells a host how to invoke it from the host checkout, that `serve` is the normal mode, or which commands work while it runs. So hosts write their own wrappers, run `drain` repeatedly, stop and start it around every decision, and learn the rules only by reading chupa's code. This repo's `./dev.py` also has no `serve` subcommand.

After this change:
- `./dev.py serve` starts serve.
- `chupa --help` tells a reader where the run guide is.
- One host-facing page, `docs/host-running.md`, says how to run chupa against a host.

## Scope in / Scope out
- In: `dev.py`: a `serve` subcommand that runs `chupa serve`, plus a docstring line.
- In: `docs/how-chupa-works.md` section 2.2: list `serve`.
- In: `chupa/__main__.py` `_parser`:
  - the top-level `description` names `docs/host-running.md`;
  - the `confirm`/`reject` help no longer says "under the lock". Each says the verdict goes to a running serve when one holds the lock.
- In: new `docs/host-running.md`. It covers, briefly:
  1. the exact invocation from a host checkout root against a chupa checkout, verified against `pyproject.toml` and a real run;
  2. `serve` is the normal mode, it runs until `kill` or Ctrl-C, and `drain` is a finite run to quiescence;
  3. a table listing every verb in `_parser`, whether it works while serve runs, and what it does. Config edits and new ticket files are picked up live. `confirm`/`reject` are published to the running serve;
  4. the commands that need serve stopped (those that take the lock outright), and why;
  5. lock rules: one writer per host, and never delete `chupa.lock`;
  6. drafts that Author writes wait for `confirm`.
- In: `docs/host-contract.md` and `docs/host-authoring.md` link to `docs/host-running.md`. `host-authoring.md` workflow step 4 says a running serve picks up the new ticket, and `drain` is the alternative.
- In: `docs/how-chupa-works.md` section 12 links to `docs/host-running.md`.
- In: `tests/test_host_running.py`: the verb table in `docs/host-running.md` lists exactly the verbs `_parser` defines, so the page cannot drift from the CLI.
- Out: new verbs; behaviour changes; host-specific wrappers.

## Scope fence
- dev.py
- chupa/__main__.py
- docs/host-running.md
- docs/how-chupa-works.md
- docs/host-contract.md
- docs/host-authoring.md
- tests/test_host_running.py

## Acceptance criteria
1. `./dev.py serve --help` exits 0, and `./dev.py --help` lists `serve`.
2. `uv run python -m chupa --help` output contains `docs/host-running.md`.
3. `tests/test_host_running.py` fails when a verb is added to `_parser` without a row in the `docs/host-running.md` verb table, or when a row names a verb `_parser` lacks. Checked by `uv run pytest tests/test_host_running.py`.
4. `docs/host-running.md` gives an invocation that the implementer ran from a scratch host checkout (`doctor` exits 0 against a fixture config), and the run log records it.
5. `docs/host-contract.md`, `docs/host-authoring.md` and `docs/how-chupa-works.md` section 12 link to `docs/host-running.md`.
6. `uv run pytest -q` exits 0.

## Verification
```
./dev.py serve --help
uv run python -m chupa --help
uv run pytest tests/test_host_running.py
uv run pytest -q
```

## Definition of rejected
A shell wrapper shipped by chupa; the run guide duplicated into more than one doc; a verb table that a test does not pin to `_parser`; any behaviour change.

## Time budget
- expected: 45m
- stuck: 90m
