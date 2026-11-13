"""Carried reproducer for reviewing a committed ticket during a drain."""

import json
import sys
import tempfile
import traceback
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


def main():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    try:
        import chupa.observe as watch
        from tests.unit.test_menu_admission import fake_snapshot_inputs

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ctx = watch.Context(root, root / "state", root / "config.yaml", None, None, None)
            ticket = SimpleNamespace(stem="ready", frontmatter=SimpleNamespace(priority="P1", state="confirmed"), depends=(), runs_before=(), sections={})
            with (
                patch.object(watch, "load_tickets", return_value=({"ready": ticket}, {})),
                patch.object(watch, "journal", return_value=[]),
                patch.object(watch, "lock_holder", return_value=object()),
                patch.object(watch, "running_stems", return_value=[]),
                patch.object(watch, "ticket_menu_inputs", fake_snapshot_inputs),
                patch.object(watch, "uncommitted_tickets", return_value=(set(), set())),
                patch.object(watch, "committed_ticket_shas", return_value={"ready": "sha"}),
                patch.object(watch, "commits", return_value={}),
            ):
                row = next(row for row in watch.snapshot(ctx)["rows"] if row["stem"] == "ready")
                defect = row["section"] != "queued" or row["menu"]["chupaReview"] != "on"
    except Exception:
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"regression_result": "error"}))
        return 2
    print(json.dumps({"regression_result": "defect" if defect else "pass"}))
    return 1 if defect else 0


if __name__ == "__main__":
    sys.exit(main())
