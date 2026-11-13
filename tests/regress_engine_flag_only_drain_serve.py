"""Carried reproducer for a non-engine lock holder showing the Stop button."""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from chupa import observe
from tests.unit.test_menu_admission import fake_snapshot_inputs

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    (root / "chupa.lock").write_text(json.dumps({"pid": 712, "started_at": "2026-11-06T07:19:00+00:00"}))
    ctx = observe.Context(root, root, root / "config.yaml", None, None, None)
    with (
        patch.object(observe.os, "kill"),
        patch.object(observe, "processes", return_value=[(712, 1, "python -m chupa triage")]),
        patch.object(observe, "ticket_menu_inputs", fake_snapshot_inputs),
        patch.object(observe, "uncommitted_tickets", return_value=(set(), set())),
        patch.object(observe, "committed_ticket_shas", return_value={}),
        patch.object(observe, "commits", return_value={}),
    ):
        passed = observe.snapshot(ctx)["engine"] is False

print(json.dumps({"regression_result": "pass" if passed else "defect"}))
sys.exit(0 if passed else 1)
