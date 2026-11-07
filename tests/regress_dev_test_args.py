"""Carried reproducer for leading pytest options in the dev command."""

import contextlib
import io
import json
import sys
import traceback
from pathlib import Path
from unittest.mock import Mock


def main() -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    calls = []
    try:
        import dev

        dev.sys.argv = ["dev.py", "test", "-k", "foo"]

        def record(argv, **kwargs):
            calls.append(argv)
            return Mock(returncode=0)

        dev.subprocess.run = record
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                dev.main()
        except SystemExit as error:
            if error.code == 2 and not calls:
                print(json.dumps({"regression_result": "defect"}))
                return 1
            raise
        if calls != [["uv", "run", "pytest", "-q", "-k", "foo"]]:
            raise AssertionError(f"unexpected calls: {calls!r}")
    except BaseException:
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"regression_result": "error"}))
        return 2
    print(json.dumps({"regression_result": "pass"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
