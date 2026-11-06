"""Carried reproducer for lint accepting an implementation path."""

import json
import re
import sys
import traceback
from pathlib import Path


def main() -> int:
    try:
        root = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(root))
        from chupa.tickets import TicketInvalid, template, validate_ticket

        values = {
            "none or bullets of existing ticket stems": "none",
            "existing repo-relative read-first path": "chupa/tickets.py",
            "observable outcome and why it matters": "Lint rejects implementation paths.",
            "what changes and what stays outside this ticket": "In: lint. Out: other checks.",
            "repo-relative writable path prefix": "chupa/tickets.py",
            "measurable outcome naming a check in backticks": "`lint` rejects the path.",
            "argv command that exits 0": "true",
            "outcome that rejects the branch": "Lint accepts the path.",
            "estimated integer minutes": "10",
            "larger deadline in integer minutes": "20",
            "one argv command emitting the regression_result JSON protocol": "true",
            "test or fixture path prefix needed by the command": "vscode-chupa/media/graph.js",
        }
        text = re.sub(r"<([^<>]+)>", lambda match: values[match[1]], template("bug"))
        try:
            validate_ticket("regress-carries", text, root)
        except TicketInvalid as error:
            if not any("vscode-chupa/media/graph.js" in finding.message for finding in error.findings):
                raise
            defect = False
        else:
            defect = True
    except Exception:
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"regression_result": "error"}))
        return 2
    print(json.dumps({"regression_result": "defect" if defect else "pass"}))
    return 1 if defect else 0


if __name__ == "__main__":
    sys.exit(main())
