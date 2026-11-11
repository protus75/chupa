"""Carried reproducer for the Recent Steps icon vocabulary."""

import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    try:
        import chupa.observe as observe

        if not hasattr(observe, "STEP_KINDS"):
            outcome, code = "defect", 1
        else:
            kinds = observe.STEP_KINDS
            result = subprocess.run(
                ["node", str(Path(__file__).with_name("vscode_step_icons.js")), json.dumps(list(kinds))],
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )
            icons = json.loads(result.stdout)
            if not isinstance(icons, dict) or set(icons) != set(kinds):
                raise ValueError("harness returned an invalid icon map")
            by_step = {}
            for kind, step in kinds.items():
                by_step.setdefault(step, set()).add(icons[kind])
            defect = any(not icon for icon in icons.values()) or any(len(ids) != 1 for ids in by_step.values()) or len({next(iter(ids)) for ids in by_step.values()}) != len(by_step)
            outcome, code = ("defect", 1) if defect else ("pass", 0)
    except (ImportError, OSError, subprocess.SubprocessError, ValueError) as error:
        print(error, file=sys.stderr)
        outcome, code = "error", 2
    print(json.dumps({"regression_result": outcome}))
    return code


if __name__ == "__main__":
    sys.exit(main())
