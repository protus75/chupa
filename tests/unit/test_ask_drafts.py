from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from chupa import __main__ as entry
from chupa import ask, observe


def test_render_drafts_unit(monkeypatch):
    monkeypatch.setattr(Path, "read_text", lambda self: "${tickets}\n${state_dir}/box/")
    config = SimpleNamespace(state_dir=Path("/repo/custom"), ask_notes=None)
    text = ask.render("drafts", ["a-one", "b-two"], config, Path("/repo"))
    assert text == "- a-one: tickets/a-one/ticket.md\n- b-two: tickets/b-two/ticket.md\ncustom/box/"  # Fixed, dropped, or reordered stems differ.


def test_selection(monkeypatch, capsys):
    monkeypatch.setattr(entry, "load_config", lambda *a, **k: SimpleNamespace(state_dir=Path("/state"), providers=[], ask_notes=None))
    monkeypatch.setattr(entry, "child_env", lambda *a: {})
    monkeypatch.setattr(observe, "snapshot", lambda ctx: {"rows": [{"stem": "draft-one", "draft": True}, {"stem": "not-draft", "draft": False}, {"stem": "draft-two", "draft": True}]})
    render = Mock(return_value="the prompt")
    monkeypatch.setattr(ask, "render", render)
    assert entry.main(["prompt", "drafts"]) == 0  # A refusal is not successful selection.
    assert render.call_args.args[:2] == ("drafts", ["draft-one", "draft-two"])  # Wrong predicate or ordering differs.
    assert capsys.readouterr().out == "the prompt"  # The rendered prompt must be printed.


@pytest.mark.parametrize(
    ("args", "road"),
    [
        (["prompt", "drafts", "some-stem"], "run chupa prompt drafts with no stems"),
        (["prompt", "drafts"], "run triage, or author a ticket with chupa new"),
        (["prompt", "box"], "name at least one box id"),
    ],
)
def test_refusals(monkeypatch, capsys, args, road):
    monkeypatch.setattr(entry, "load_config", lambda *a, **k: SimpleNamespace(state_dir=Path("/state"), providers=[], ask_notes=None))
    monkeypatch.setattr(entry, "child_env", lambda *a: {})
    monkeypatch.setattr(observe, "snapshot", lambda ctx: {"rows": [{"stem": "other", "draft": False}]})
    render = Mock()
    monkeypatch.setattr(ask, "render", render)
    assert entry.main(args) == 2  # These requests must refuse.
    output = capsys.readouterr()
    assert road in output.err  # A generic error provides no remedy.
    assert output.out == ""  # Refusals must not emit a prompt.
    render.assert_not_called()
