"""Status surfaces confirmed policy classes using write-free queue and journal reads."""

from chupa.__main__ import main
from chupa.box import Box, Resolution
from chupa.daemon import storm_producer
from chupa.journal import Journal
from chupa.seams import LocalFileSystem
from chupa.status import project, render
from tests.test_cli import ENV
from tests.test_drain import Clock, make_root
from tests.test_retro_box import PROPOSAL


def test_status_surfaces_confirmed_class_tombstones(tmp_path, monkeypatch, capsys):
    root = make_root(tmp_path)
    clock = Clock()
    journal = Journal(root / ".chupa/state", clock)
    fs = LocalFileSystem()
    box = storm_producer(root=root / ".chupa/state/box", fs=fs, journal=journal, clock=clock)
    ids = []
    for cls in ("failure_report", "retro_finding", "suggestion"):
        evidence = {**PROPOSAL, "retro_report_key": "retro/1"} if cls == "retro_finding" else {}
        id, _ = box.enqueue(message_class=cls, origin=cls, summary="observed concern", occurrence_id=cls, **evidence)
        box.resolve(id, Resolution(kind="tombstone", link=f"tombstone-{id}"))
        ids.append(id)
    before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
    def forbidden(*args, **kwargs):
        raise AssertionError("status tried to write")
    monkeypatch.setattr(LocalFileSystem, "write", forbidden)
    monkeypatch.setattr(Journal, "append", forbidden)
    status = project(journal.read(), box=box)
    assert status.tombstones == tuple((m.id, m.message_class, 0) for m in box.messages()[:2])
    output = render(status)
    assert all(id in output for id in ids[:2]) and ids[2] not in output
    assert main(["status"], cwd=root, env=ENV, clock=clock) == 0
    assert capsys.readouterr().out == output
    assert {p: p.read_bytes() for p in root.rglob("*") if p.is_file()} == before
    monkeypatch.undo()
    for n in range(3):
        box.record_rereport(ids[0], occurrence_id=f"fresh/{n}")
    before = journal.read()
    current = project(before, box=Box(box.root, fs))
    assert current.tombstones == ((ids[1], "retro_finding", 0),)
    assert current.reopens == ({"kind": "tombstone_auto_reopened", "box_id": ids[0],
                                "signature": box.get(ids[0]).signature, "reports": 3},)
    assert ids[0] in render(current) and journal.read() == before
