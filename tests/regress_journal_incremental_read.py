import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from chupa import journal as module


def main():
    with tempfile.TemporaryDirectory() as directory:
        j = module.Journal(Path(directory), lambda: datetime(2026, 8, 4, tzinfo=UTC))
        for n in range(500):
            j.append("timer_armed", {"n": n})
        j.read()
        count = 0
        parse = module._parse_line

        def counted(path, lineno, raw):
            nonlocal count
            count += 1
            return parse(path, lineno, raw)

        module._parse_line = counted
        j.read()
        result = "pass" if count == 0 else "defect"
        print(json.dumps({"regression_result": result}))
        return 0 if result == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
