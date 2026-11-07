"""Carried reproducer for Reject-queue reoffers."""

import json
import sys
import traceback
from pathlib import Path
from types import SimpleNamespace


def main():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    try:
        import chupa.drain as drain

        awaiting_operator = drain.awaiting_operator
        reofferable = drain.reofferable
    except AttributeError:
        print(json.dumps({"regression_result": "defect"}))
        return 1
    except Exception:
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"regression_result": "error"}))
        return 2
    try:
        from chupa.config import Caps

        history = [SimpleNamespace(type="state_transition", ticket="work", body={"to": "gate_failed", "routed": "reject_queue"})]
        spent = history + [SimpleNamespace(type="cap_consumed", ticket="work", body={"cap": "retry"})]
        limits = Caps(retry=1)
        defect = not reofferable(history, "work", limits) or not awaiting_operator(spent, "work", limits)
    except Exception:
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"regression_result": "error"}))
        return 2
    print(json.dumps({"regression_result": "defect" if defect else "pass"}))
    return 1 if defect else 0


if __name__ == "__main__":
    sys.exit(main())
