---
state: confirmed
source: human
priority: P2
kind: feature
---

## Goal / Why
Add a helper that runs Ruff against a user repository and returns its output to the job runner. The lint subprocess must receive only the parent environment entries needed to find and run the executable.

## Scope in / Scope out
In: launch the configured Ruff executable with `check .` from the repository directory; return its exit code, stdout, and stderr. Pass through only `PATH`, `LANG`, and `LC_ALL` when present in the parent environment.

Out: changing how jobs are scheduled, interpreting Ruff output, and forwarding any other parent environment entries.

## Scope fence
- `jobrunner/lint.py`
- `tests/test_lint.py`

## Acceptance criteria
1. The helper runs the configured executable with arguments `check .` and the repository as its working directory.
2. The child environment contains exactly the available parent values for `PATH`, `LANG`, and `LC_ALL`.
3. A nonzero Ruff exit code is returned with captured stdout and stderr, without raising an exception.
4. Tests cover the command, environment, and nonzero result.

## Verification
`python -m pytest -q tests/test_lint.py`
