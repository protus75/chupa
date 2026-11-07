---
state: confirmed
source: human
priority: P2
kind: bug
---

## Depends on
none

## Context
- dev.py
- tests/test_dev.py
- tests/regress_graph_lanes.py

## Goal / Why
`./dev.py test [args]` is documented as "args go to pytest", but any pytest option given before the first positional argument is refused. `./dev.py test --durations=25`, `./dev.py test -k foo`, and `./dev.py test -q` each exit 2 with `./dev.py: error: unrecognized arguments`, while `./dev.py test tests --durations=25` works (evidence: `evidence/leading-options.txt`). Cause: `dev.py` declares the `test` arguments with `nargs=argparse.REMAINDER` on a subparser, and argparse does not hand a leading option to a REMAINDER positional. Found on 2026-11-07 when timing the suite with `--durations`.

After this change every argument after `test` reaches pytest unchanged and in order, whether or not it starts with `-`.

## Scope in / Scope out
- In: `dev.py`: `./dev.py test <args>` runs `["uv", "run", "pytest", "-q", *args]` for any `args`, including ones that start with `-`.
- In: `tests/test_dev.py`: new `test_test_passes_leading_options_to_pytest`. With `sys.argv` set to `["dev.py", "test", "--durations=25", "-k", "foo"]` and `dev.subprocess.run` faked to return code 0, `dev.main()` calls `subprocess.run` exactly once with argv `["uv", "run", "pytest", "-q", "--durations=25", "-k", "foo"]`. The same test also asserts that `["dev.py", "lint", "--bogus"]` still raises `SystemExit` with code 2, so other subcommands keep rejecting unknown options.
- In: new `tests/regress_dev_test_args.py`, the carried reproducer. Like `tests/regress_graph_lanes.py`, it puts the repo root on `sys.path` and imports `dev`. It sets `dev.sys.argv` to `["dev.py", "test", "-k", "foo"]`, replaces `dev.subprocess.run` with a recorder that returns code 0, and calls `dev.main()`.
  - `SystemExit` with code 2 before any recorded call: prints `{"regression_result": "defect"}` and exits 1.
  - Exactly one recorded call with argv `["uv", "run", "pytest", "-q", "-k", "foo"]`: prints `{"regression_result": "pass"}` and exits 0.
  - Anything else, including a failed import of `dev`: the traceback goes to stderr, and it prints `{"regression_result": "error"}` and exits 2.
  - Nothing but the one JSON object goes to stdout. `dev.run` prints its `$ ...` line to stdout, so the reproducer redirects stdout around `dev.main()` and prints the result after.
- Out: every other subcommand's arguments and behavior, the bare `./dev.py` suite run, and `docs/how-chupa-works.md` (its `test [args]` row already says "pytest with those args").

## Scope fence
- dev.py
- tests/test_dev.py
- tests/regress_dev_test_args.py

## Acceptance criteria
1. `./dev.py test tests/test_dev.py` exits 0 and includes `test_test_passes_leading_options_to_pytest`. The test fails if a leading option is dropped, reordered, or refused with exit 2, and fails if `lint --bogus` is accepted rather than exiting 2.
2. `uv run python tests/regress_dev_test_args.py` prints `{"regression_result": "pass"}` and exits 0 on the branch head.
3. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/test_dev.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- a subcommand other than `test` accepts arguments it rejected before;
- the `test` argv is reordered, deduplicated, or has anything added besides the existing `-q`;
- the reproducer prints `pass` on the merge base.

## Time budget
- expected: 15m
- stuck: 45m

## Regression
```
uv run python tests/regress_dev_test_args.py
```
- carries: tests/regress_dev_test_args.py
