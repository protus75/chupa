"""Carried reproducer for requisition findings missing from the drain report."""

import contextlib
import io
import json
import sys
import tempfile
import traceback
from pathlib import Path


def main() -> int:
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from chupa import runner
        from chupa.__main__ import main as chupa_main
        from chupa.journal import EventType
        from chupa.llm import FakeLLM
        from tests.integration.test_cli import ENV
        from tests.integration.test_drain import Clock, commit_ticket, confirmed, journal, make_root
        from tests.integration.test_rework import requisition

        with tempfile.TemporaryDirectory() as directory:
            root = make_root(Path(directory))
            commit_ticket(root, "review-park", confirmed())
            llm = FakeLLM([requisition("snag")])
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = chupa_main(["drain"], cwd=root, env=ENV, clock=Clock(), pipeline=lambda c: runner.bind(c, llm))
            terminal = [e.body for e in journal(root).read() if e.type == EventType.STATE_TRANSITION and e.ticket == "review-park"][-1]
            if result != 0 or terminal.get("stage") != "requisition" or not terminal.get("reason"):
                raise RuntimeError("requisition park was not produced")
            defect = f"\n  - {terminal['reason']}" not in output.getvalue().split("parked:\n", 1)[1].split("\n\n", 1)[0]
    except Exception:
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"regression_result": "error"}))
        return 2
    print(json.dumps({"regression_result": "defect" if defect else "pass"}))
    return 1 if defect else 0


if __name__ == "__main__":
    sys.exit(main())
