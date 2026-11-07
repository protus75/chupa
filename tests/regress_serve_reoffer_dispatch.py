"""Carried reproducer for serve's Reject-queue re-offer selection."""

import asyncio
import inspect
import json
import sys
import tempfile
import traceback
from pathlib import Path


def main():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    try:
        from chupa.scheduler import Scheduler

        if "caps" not in inspect.signature(Scheduler).parameters:
            result = "defect"
        else:
            from tests.integration.test_scheduler import Rig

            with tempfile.TemporaryDirectory() as directory:
                rig = Rig(Path(directory))
                rig.add("work")
                rig.transition("work", "gate_failed", routed="reject_queue")
                ticket = asyncio.run(rig.scheduler.dispatch_next())
                result = "pass" if ticket is not None and ticket.stem == "work" else "defect"
    except Exception:
        traceback.print_exc(file=sys.stderr)
        result = "error"
    print(json.dumps({"regression_result": result}))
    return {"pass": 0, "defect": 1, "error": 2}[result]


if __name__ == "__main__":
    sys.exit(main())
