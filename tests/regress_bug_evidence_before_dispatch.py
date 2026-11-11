"""Carried reproducer for bug evidence before dispatch."""

import contextlib
import json
import sys
import traceback
from pathlib import Path


def main() -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    try:
        import pytest

        with contextlib.redirect_stdout(sys.stderr):
            result = pytest.main(["tests/unit/test_parse_ticket_evidence.py", "-k", "without_evidence_is_invalid", "-q", "-p", "no:cacheprovider"])
        verdict, code = {0: ("pass", 0), 1: ("defect", 1)}.get(result, ("error", 2))
    except BaseException:
        traceback.print_exc(file=sys.stderr)
        verdict, code = "error", 2
    print(json.dumps({"regression_result": verdict}))
    return code


if __name__ == "__main__":
    sys.exit(main())
