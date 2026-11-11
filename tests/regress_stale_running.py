"""Carried reproducer for rejecting an interrupted run."""

import contextlib
import io
import json
import sys
import tempfile
import traceback
from pathlib import Path


def main():
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from chupa.__main__ import main as chupa_main
        from chupa.journal import EventType
        from tests.integration.test_cli import ENV
        from tests.integration.test_drain import Clock, commit_ticket, confirmed, journal, make_root

        with tempfile.TemporaryDirectory() as directory:
            root = make_root(Path(directory))
            commit_ticket(root, "stale", confirmed())
            journal(root).append(EventType.STATE_TRANSITION, {"to": "running"}, ticket="stale")
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                result = chupa_main(["reject", "--yes", "stale"], cwd=root, env=ENV, clock=Clock())
            states = [e.body["to"] for e in journal(root).read() if e.type == EventType.STATE_TRANSITION and e.ticket == "stale"]
            defect = result != 0 or states[-1] != "rejected"
    except Exception:
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"regression_result": "error"}))
        return 2
    print(json.dumps({"regression_result": "defect" if defect else "pass"}))
    return 1 if defect else 0


if __name__ == "__main__":
    sys.exit(main())
