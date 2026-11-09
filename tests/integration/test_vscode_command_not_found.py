"""Exercise errors from the VS Code extension's snapshot command."""

import json
import subprocess
from pathlib import Path

HARNESS = Path(__file__).parents[1] / "vscode_command_not_found.js"


def run_snapshot(tmp_path, binary):
    (tmp_path / "tickets").mkdir()
    result = subprocess.run(
        ["node", str(HARNESS), str(tmp_path), binary],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    return json.loads(result.stdout)


def test_missing_command_names_setting_and_workspace(tmp_path):
    message = run_snapshot(tmp_path, ".venv/bin/chupa-missing")
    assert message == (f"chupa command not found: .venv/bin/chupa-missing (run from {tmp_path}). Set chupa.command in settings.")


def test_other_command_failure_keeps_its_message(tmp_path):
    message = run_snapshot(tmp_path, "false")
    assert "chupa command not found" not in message
    assert "false" in message
