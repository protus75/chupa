"""Carried reproducer for duplicate dependency lanes in the Tickets view graph."""

import json
import shutil
import subprocess
import sys
import traceback
from pathlib import Path


def main() -> int:
    try:
        node = shutil.which("node")
        if node is None:
            raise RuntimeError("node is not on PATH")
        code = subprocess.run([node, str(Path(__file__).resolve().parent / "fixtures" / "graph_lanes.js")], check=False).returncode
        if code not in (0, 1):
            raise RuntimeError(f"graph_lanes.js exited {code}")
        defect = code == 1
    except Exception:
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"regression_result": "error"}))
        return 2
    print(json.dumps({"regression_result": "defect" if defect else "pass"}))
    return 1 if defect else 0


if __name__ == "__main__":
    sys.exit(main())
