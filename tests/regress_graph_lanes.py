"""Carried reproducer for the Tickets view graph layout (duplicate lanes, blocked-to-queued lanes, rotation colors)."""

import json
import sys
import traceback
from pathlib import Path

SECTIONS = {"blocked", "queued", "running", "merged"}


def row(stem: str, section: str, depends: list[str]) -> dict:
    return {"stem": stem, "section": section, "depends": depends}


def main() -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    try:
        from chupa.graph import layout
    except ModuleNotFoundError as error:
        if error.name != "chupa.graph":
            traceback.print_exc(file=sys.stderr)
            print(json.dumps({"regression_result": "error"}))
            return 2
        # The base commit computes the layout in vscode-chupa/media JavaScript, which is the defect.
        print(json.dumps({"regression_result": "defect"}))
        return 1
    try:
        shared = layout([row("a", "queued", ["d"]), row("b", "queued", ["d"]), row("c", "queued", []), row("d", "running", [])])
        blocked = layout([row("x", "blocked", ["y"]), row("y", "queued", []), row("z", "running", [])])
        lanes = [lane for g in shared + blocked for lane in g["lanesIn"] + g["lanesOut"] if lane["id"] is not None]
        defect = (
            any(sum(lane["id"] == "d" for lane in g["lanesOut"]) > 2 for g in shared)
            or blocked[0]["parents"] != []
            or any(lane["section"] not in SECTIONS for lane in lanes)
        )
    except Exception:
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"regression_result": "error"}))
        return 2
    print(json.dumps({"regression_result": "defect" if defect else "pass"}))
    return 1 if defect else 0


if __name__ == "__main__":
    sys.exit(main())
