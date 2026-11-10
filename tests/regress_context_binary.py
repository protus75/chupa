"""Carried reproducer for a binary file accepted as ticket Context."""

import json
import sys
import tempfile
import traceback
from pathlib import Path


def main() -> int:
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from chupa.tickets import TicketInvalid, validate_ticket
        from tests.integration.test_tickets import VALID, complete

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n")
            text = complete(VALID.replace("chupa/thing.py\n\n## Goal", "image.png\n\n## Goal"))
            try:
                validate_ticket("t-one", text, root)
            except TicketInvalid as exc:
                if not any("Context" in finding.message for finding in exc.findings):
                    raise
                outcome, code = "pass", 0
            else:
                outcome, code = "defect", 1
    except Exception:
        traceback.print_exc(file=sys.stderr)
        outcome, code = "error", 2
    print(json.dumps({"regression_result": outcome}))
    return code


if __name__ == "__main__":
    sys.exit(main())
