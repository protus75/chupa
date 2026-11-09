"""Carried reproducer for infra re-offers consuming retry."""

import contextlib
import json
import sys
import traceback


def main() -> int:
    try:
        import pytest

        with contextlib.redirect_stdout(sys.stderr):
            result = pytest.main(["tests/unit/test_drain_reoffer.py", "-k", "infra_error", "-q", "-p", "no:cacheprovider"])
        verdict, code = {0: ("pass", 0), 1: ("defect", 1)}.get(result, ("error", 2))
    except BaseException:
        traceback.print_exc(file=sys.stderr)
        verdict, code = "error", 2
    print(json.dumps({"regression_result": verdict}))
    return code


if __name__ == "__main__":
    sys.exit(main())
