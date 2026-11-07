---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
none

## Context
- dev.py
- tests/integration/test_dev.py
- pyproject.toml
- docs/how-chupa-works.md

## Goal / Why
`./dev.py publish` uploads the version already in `pyproject.toml` and never bumps it, so a second release needs a hand edit first; PyPI refuses a version it has seen, so forgetting means a failed upload (2026-11-07). `./dev.py vscode` already bumps its patch version on every run for the same reason.

After this change `./dev.py publish` runs `uv version --bump patch` before it builds, so each publish uploads a fresh patch version.

## Scope in / Scope out
- In: `dev.py` `publish`: after the `UV_PUBLISH_TOKEN` check, `run(["uv", "version", "--bump", "patch"])`, then the existing build and upload. The module docstring line and `--help` text say it bumps the patch version.
- In: `tests/integration/test_dev.py`:
  - `test_publish_uploads_built_files` expects three calls in order (`uv version --bump patch`, `uv build -o <tmp>`, `uv publish <files>`) and drops its "must not bump" assertion;
  - new `test_publish_refuses_without_token`: with `UV_PUBLISH_TOKEN` unset, `dev.main()` exits non-zero naming `UV_PUBLISH_TOKEN` and the faked `dev.subprocess.run` is never called.
- In: `docs/how-chupa-works.md` section 2.2 `publish` row: it bumps the patch version, then builds and uploads; committing `pyproject.toml` and `uv.lock` is left to the operator.
- Out:
  - minor or major bumps, and any bump option;
  - git commits, tags, pushes;
  - the `vscode` and `vscode-package` commands;
  - engine code under `chupa/`.

## Scope fence
- dev.py
- tests/integration/test_dev.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `tests/integration/test_dev.py::test_publish_uploads_built_files` passes: with `UV_PUBLISH_TOKEN` set and `dev.subprocess.run` faked, `./dev.py publish` makes exactly three calls, `["uv", "version", "--bump", "patch"]`, `["uv", "build", "-o", <tmp>]`, then `["uv", "publish", <each built file>]`. It rules out no bump, a bump after the build (which would upload the old version again), a second bump, and any git call.
2. `tests/integration/test_dev.py::test_publish_refuses_without_token` passes: with `UV_PUBLISH_TOKEN` unset, publish exits non-zero naming `UV_PUBLISH_TOKEN` and makes zero `dev.subprocess.run` calls, not a bump followed by the refusal.
3. The `publish` row in `docs/how-chupa-works.md` section 2.2 and the `dev.py` docstring line say publish bumps the patch version.
4. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_dev.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- publish bumps the version when `UV_PUBLISH_TOKEN` is unset;
- publish commits, tags, or pushes;
- a bump option or a second bump path is added.

## Time budget
- expected: 20m
- stuck: 60m
