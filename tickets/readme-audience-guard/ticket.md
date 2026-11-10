---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
- pypi-readme-user-guide

## Context
- README.md
- tests/unit/test_host_running.py
- chupa/__main__.py::_parser

## Goal / Why
`README.md` is the PyPI page (`readme = "README.md"` in `pyproject.toml`). Before `pypi-readme-user-guide`, it drifted into a developer-only page: it showed `./dev.py` commands that do not exist in a host project, and its relative links broke on PyPI. Nothing checked either. After this change, a unit test fails when the README regains any of those defects. That covers a relative link, a `./dev.py` command outside the developer section, a missing GitHub link, or a `uv run chupa` verb the CLI does not have.

## Scope in / Scope out
- In: new `tests/unit/test_readme.py`, following the style of `tests/unit/test_host_running.py`: read `README.md` from the repo root with `Path(__file__).resolve().parents[2]` and use `_parser()` for the verb set. Four tests:
  - `test_links_are_absolute`: every markdown link or image target (`](...)`) starts with `https://`.
  - `test_dev_commands_only_in_developer_section`: `## Developing chupa` occurs exactly once, and every occurrence of `./dev.py` comes after it.
  - `test_links_github_project`: the README contains a link whose target is exactly `https://github.com/protus75/chupa`.
  - `test_chupa_verbs_exist`: every word following `uv run chupa ` in the README (ignoring the `<verb>` placeholder) is a subcommand choice of `_parser()`.
- Out: `README.md` itself, other docs, `chupa/` code, and `pyproject.toml`. If a test fails on the merged README, report it as a second problem; do not edit the README.

## Scope fence
- tests/unit/test_readme.py

## Acceptance criteria
1. `./dev.py test tests/unit/test_readme.py` runs the four named tests, and all pass on the merged README.
2. `test_links_are_absolute` checks the prefix `https://`, so it rules out relative targets such as `docs/host-contract.md#install` and bare anchors such as `#install`, not only `http://` targets.
3. `test_dev_commands_only_in_developer_section` asserts the heading occurs exactly once and compares the first `./dev.py` offset against it. That rules out a README with no `## Developing chupa` heading and a README with a `./dev.py` line above the heading that would pass a check of the last occurrence only.
4. `test_chupa_verbs_exist` compares against `_parser()` subcommand choices, so it rules out a README naming a verb that `uv run chupa --help` does not list, such as `uv run chupa frobnicate`.
5. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/unit/test_readme.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- any file other than `tests/unit/test_readme.py` changes;
- a test reads a hardcoded verb list instead of `_parser()`;
- a test passes on a README with a relative link target.

## Time budget
- expected: 15m
- stuck: 45m
