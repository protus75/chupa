"""Carried reproducer for verification commands naming branch-only paths."""

import contextlib
import json
import sys
import traceback


def main() -> int:
    try:
        import pytest

        with contextlib.redirect_stdout(sys.stderr):
            rc = pytest.main(["tests/integration/test_stages.py", "-k", "test_red_command_naming_a_branch_added_file_is_not_base_red", "-q", "-p", "no:cacheprovider"])
        if rc == 0:
            result, code = "pass", 0
        elif rc == 1:
            result, code = "defect", 1
        else:
            result, code = "error", 2
    except BaseException:
        traceback.print_exc(file=sys.stderr)
        result, code = "error", 2
    print(json.dumps({"regression_result": result}))
    return code


if __name__ == "__main__":
    sys.exit(main())
