"""Carried reproducer for status taking an optional index lock."""

import asyncio
import json
import sys
import traceback
from pathlib import Path


def main() -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    try:
        from chupa.git import Git
        from tests.integration.test_git import commit_lock

        class RecordingExec:
            def __init__(self):
                self.calls = []

            async def run(self, argv, **kwargs):
                self.calls.append(list(argv))
                return 0, "", ""

        exec_ = RecordingExec()
        asyncio.run(Git(exec_, env={}, timeout=30, commit_lock=commit_lock(Path("/repo/.chupa/state"))).status_porcelain(Path("/repo")))
        argv = exec_.calls[0]
        status = argv.index("status")
        result = "pass" if "--no-optional-locks" in argv[:status] else "defect"
    except Exception:
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"regression_result": "error"}))
        return 2
    print(json.dumps({"regression_result": result}))
    return 0 if result == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
