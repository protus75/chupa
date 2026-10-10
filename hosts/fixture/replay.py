"""Python argv runner: 0 means healthy, 1 means observed defect."""

import json
import sys
from pathlib import Path

from app import replay


if __name__ == "__main__":
    result = replay(json.loads(Path(sys.argv[1]).read_bytes()))
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    raise SystemExit(1 if result["defect"] else 0)
