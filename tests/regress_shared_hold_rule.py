"""Carried reproducer for the shared content hold."""

import json
import sys
import traceback
from pathlib import Path
from types import SimpleNamespace


def main():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    try:
        import chupa.drain as drain
        from chupa.observe import held

        if not hasattr(drain, "parked_blob"):
            print(json.dumps({"regression_result": "defect"}))
            return 1
        parked_blob = drain.parked_blob
        history = [
            SimpleNamespace(type="state_transition", ticket="work", body={"to": "running", "ticket_sha": "B"}),
            SimpleNamespace(type="state_transition", ticket="work", body={"to": "premise_failed"}),
        ]
        defect = parked_blob(history, "work") != "B" or "work" not in held(history, {"work": "B"})
    except Exception:
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"regression_result": "error"}))
        return 2
    print(json.dumps({"regression_result": "defect" if defect else "pass"}))
    return 1 if defect else 0


if __name__ == "__main__":
    sys.exit(main())
