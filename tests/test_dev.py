from pathlib import Path
from unittest.mock import Mock, mock_open

import dev


def test_drain_detaches_and_appends_to_configured_state(monkeypatch, capsys):
    root = Path("/repo")
    output = root / "custom/state/drain.out"
    monkeypatch.setattr(dev, "ROOT", root)
    monkeypatch.setattr(dev.sys, "argv", ["dev.py", "drain"])
    monkeypatch.setattr(Path, "read_text", lambda path: "state_dir: custom/state\n")
    mkdir = Mock()
    monkeypatch.setattr(Path, "mkdir", mkdir)
    opener = mock_open()
    opened = []
    def open_output(path, mode):
        opened.append((path, mode))
        return opener(mode)
    monkeypatch.setattr(Path, "open", open_output)
    child = Mock(pid=7319)
    popen = Mock(return_value=child)
    monkeypatch.setattr(dev.subprocess, "Popen", popen)

    assert dev.main() is None  # A synchronous launcher would wait or return its child's status.
    mkdir.assert_called_once_with(parents=True, exist_ok=True)  # A fresh state directory must be created.
    opener.assert_called_once_with("a")  # Truncating output would erase previous runs.
    assert opened == [(output, "a")]  # The log must go under the configured state directory.
    stream = opener.return_value.__enter__.return_value
    popen.assert_called_once_with(
        ["uv", "run", "python", "-m", "chupa", "drain"],
        cwd=root, start_new_session=True, stdin=dev.subprocess.DEVNULL, stdout=stream, stderr=stream,
    )  # Inherited terminal streams or a shared session would not survive a reload.
    child.wait.assert_not_called()  # Waiting would keep the launcher attached.
    assert capsys.readouterr().out == f"dev: drain pid 7319, output {output}\n"  # Report this child and its configured output.
