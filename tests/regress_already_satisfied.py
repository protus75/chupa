"""Carried reproducer for settled terminals with historical Reject routing."""

import json
import sys
import traceback
from pathlib import Path


def main() -> int:
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from chupa.journal import Event, EventType
        from chupa.status import reject_queue

        stem = "harden-serve-activation-3"
        events = [
            Event(v=1, type=EventType.STATE_TRANSITION, ts="2026-01-01T00:00:00+00:00", ticket=stem, key=None, body=body)
            for body in (
                {"to": "running", "ticket_sha": "a42b1dab2ed0cdefe392cfaa8c100a37ebdbed27"},
                {"to": "already_satisfied", "stage": "check", "reason": "already_satisfied", "dispatch": "reject_queue", "routed": "reject_queue"},
            )
        ]
        defect = stem in reject_queue(events)
    except Exception:
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"regression_result": "error"}))
        return 2
    print(json.dumps({"regression_result": "defect" if defect else "pass"}))
    return 1 if defect else 0


if __name__ == "__main__":
    sys.exit(main())
