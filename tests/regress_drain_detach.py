"""Carried reproducer for drain detachment at the engine verb."""

import contextlib
import io
import json
import sys
import tempfile
import traceback
from pathlib import Path
from unittest.mock import Mock


def main() -> int:
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from chupa.__main__ import _parser
        from chupa.__main__ import main as chupa_main
        from tests.integration.test_cli import ENV
        from tests.integration.test_drain import make_root

        with tempfile.TemporaryDirectory() as directory:
            root = make_root(Path(directory))
            spawn = Mock(return_value=4242)
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    _parser().parse_args(["drain", "--detach"])
                    result = chupa_main(["drain", "--detach"], cwd=root, env=ENV, spawn=spawn)
                defect = result != 0 or spawn.call_count != 1
            except SystemExit:
                defect = True
    except Exception:
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"regression_result": "error"}))
        return 2
    print(json.dumps({"regression_result": "defect" if defect else "pass"}))
    return 1 if defect else 0


if __name__ == "__main__":
    sys.exit(main())
