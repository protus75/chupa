from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from chupa import __main__ as cli
from chupa.box import Box, Message


class MemoryFS:
    def __init__(self):
        self.files = {}

    def publish(self, path, data):
        if path in self.files:
            raise FileExistsError(path)
        self.files[path] = data

    def write(self, path, data):
        self.files[path] = data


def memory_box(monkeypatch):
    fs = MemoryFS()
    root = Path("/state/box")
    box = Box(root, fs)
    monkeypatch.setattr(box, "messages", lambda: sorted((Message.model_validate_json(data) for path, data in fs.files.items() if path.parent == root), key=lambda m: m.seq))
    return box, fs


def test_abandoned_claim_advances(monkeypatch):
    box, fs = memory_box(monkeypatch)
    fs.files[Path("/state/box.seq/000001")] = b""
    id, created = box.enqueue(message_class="suggestion", origin="session", summary="abandoned claim")
    assert created and id.startswith("box-000002-")
    assert [m.seq for m in box.messages()] == [2]


def test_competing_claim_advances(monkeypatch):
    box, fs = memory_box(monkeypatch)
    publish = fs.publish

    def compete(path, data):
        if path.name == "000001":
            fs.files[path] = b""
        publish(path, data)

    monkeypatch.setattr(fs, "publish", compete)
    id, created = box.enqueue(message_class="suggestion", origin="session", summary="competing claim")
    assert created and id.startswith("box-000002-")
    assert [m.summary for m in box.messages()] == ["competing claim"]


def test_suggest_output(monkeypatch, capsys):
    import chupa.box as box_module

    box = Mock()
    box.enqueue.side_effect = [("box-000007-abcdef12", True), ("box-000007-abcdef12", False)]
    monkeypatch.setattr(box_module, "Box", Mock(return_value=box))
    monkeypatch.setattr(cli, "load_config", lambda *a, **kw: SimpleNamespace(state_dir=Path("/state")))
    monkeypatch.setattr(cli, "child_env", lambda *a: {})
    monkeypatch.setattr(cli, "LocalFileSystem", MemoryFS)
    assert cli.main(["suggest", "a distinct idea"], cwd=Path("/host"), env={}) == 0
    assert cli.main(["suggest", "a distinct idea"], cwd=Path("/host"), env={}) == 0
    assert capsys.readouterr().out.splitlines() == ["suggest: filed box-000007-abcdef12", "suggest: already in the box as box-000007-abcdef12"]
    assert box.enqueue.call_args.kwargs["summary"] == "a distinct idea"
    assert box.enqueue.call_args.kwargs["origin"] == "session"
