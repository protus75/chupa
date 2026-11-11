import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from chupa.__main__ import main


def test_drain_detach_spawns_and_returns(monkeypatch, capsys):
    monkeypatch.setattr("chupa.__main__.load_config", lambda *args, **kwargs: SimpleNamespace(state_dir=Path("/state")))
    spawn = Mock(return_value=4242)
    assert main(["drain", "--detach"], cwd=Path("/repo"), env={}, spawn=spawn) == 0
    spawn.assert_called_once_with([sys.executable, "-m", "chupa", "drain"], cwd=Path("/repo"), env={}, output=Path("/state/drain.out"))
    assert capsys.readouterr().out == "drain: pid 4242, output /state/drain.out\n"
