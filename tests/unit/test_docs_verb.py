from pathlib import Path
from unittest.mock import Mock

import pytest

import chupa
from chupa import __main__ as cli
from chupa.runner import Refusal


def test_docs_without_config_or_lock(monkeypatch, capsys):
    monkeypatch.setattr(cli, "load_config", Mock(side_effect=AssertionError("config read")))
    monkeypatch.setattr(cli, "Lockfile", Mock(side_effect=AssertionError("lock taken")))
    assert cli.main(["docs"], cwd=Path("/absent-host")) == 0
    lines = capsys.readouterr().out.splitlines()
    directory = Path(chupa.__file__).parent / "docs"
    assert [line.split("  ")[0] for line in lines] == [str(directory / f"host-{name}.md") for name in ("authoring", "running", "contract", "qwen")]
    assert all(line.split("  ")[1] for line in lines)


def test_new_guide_paths_without_disk(monkeypatch, capsys):
    fs = Mock()
    monkeypatch.setattr(cli, "LocalFileSystem", lambda: fs)
    monkeypatch.setattr(cli, "template", lambda kind: "skeleton")
    monkeypatch.setattr(cli, "validate_ticket", lambda stem, text, repo: "ticket")
    monkeypatch.setattr(cli, "evidence_findings", lambda ticket, repo: [])
    monkeypatch.setattr(Path, "exists", lambda self: False)
    guide = Path(chupa.__file__).parent / "docs" / "host-authoring.md"
    assert cli._new(Path("/host"), "new-ticket") == 0
    assert f"read the ticket authoring guide before filling sections: {guide}" in capsys.readouterr().out.splitlines()
    fs.write.assert_called_once_with(Path("/host/tickets/new-ticket/ticket.md"), b"skeleton")
    monkeypatch.setattr(Path, "exists", lambda self: True)
    with pytest.raises(Refusal) as error:
        cli._new(Path("/host"), "new-ticket")
    assert f"read {guide}, then edit it in place, or pick a new stem" in str(error.value)
