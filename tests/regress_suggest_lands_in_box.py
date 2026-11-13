"""Carried reproducer for suggestions invisible until intake."""

import contextlib
import io
import json
import sys
import tempfile
import traceback
from pathlib import Path


def main() -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    try:
        from chupa.box import Box
        from chupa.seams import LocalFileSystem
        from tests.integration.test_cli import cli, root

        with tempfile.TemporaryDirectory() as directory:
            repo = root.__wrapped__(Path(directory))
            with contextlib.redirect_stdout(io.StringIO()):
                result = cli(repo, "suggest", "a distinct idea")
            if result != 0:
                raise RuntimeError(f"suggest exited {result}")
            messages = Box(repo / ".chupa/state/box", LocalFileSystem()).messages()
            if not any(m.message_class == "suggestion" and m.status == "pending" and m.summary == "a distinct idea" for m in messages):
                print(json.dumps({"regression_result": "defect"}))
                return 1
    except BaseException:
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"regression_result": "error"}))
        return 2
    print(json.dumps({"regression_result": "pass"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
