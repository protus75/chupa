"""Carried reproducer for lint accepting a stuck budget above the drain ceiling."""

import contextlib
import json
import sys
import traceback


def main() -> int:
    try:
        import pytest

        with contextlib.redirect_stdout(sys.stderr):
            result = pytest.main(["tests/integration/test_lint_verb.py", "-k", "test_lint_flags_stuck_over_drain_ceiling", "-q", "-p", "no:cacheprovider"])
        verdict, code = {0: ("pass", 0), 1: ("defect", 1)}.get(result, ("error", 2))
    except BaseException:
        traceback.print_exc(file=sys.stderr)
        verdict, code = "error", 2
    print(json.dumps({"regression_result": verdict}))
    return code


if __name__ == "__main__":
    sys.exit(main())
