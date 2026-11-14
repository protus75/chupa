from pathlib import Path

import pytest

from chupa import ask, specs
from chupa.__main__ import main
from chupa.config import load_config
from tests.integration.test_config import VALID


@pytest.fixture
def config(tmp_path):
    (tmp_path / "config.yaml").write_text(VALID.replace("state_dir: .chupa", "state_dir: custom/state"))
    return load_config(None, cwd=tmp_path)


@pytest.mark.parametrize("kind", [kind for kind in ask.KINDS if kind not in {"box", "drafts", "drain-loop"}])
def test_each_kind_renders_stem_ticket_and_state_dir(config, tmp_path, kind):
    text = ask.render(kind, "unique-stem", config, tmp_path)
    assert "`unique-stem`" in text  # A fixed or missing stem gives a different prompt.
    assert "tickets/unique-stem/ticket.md" in text  # The ticket path must use the requested stem.
    if kind != "review":
        assert "custom/state/" in text  # A hard-coded default state directory differs.
    assert '"Recommendation"' in text  # Omitting the shared report instruction loses this section.


def test_host_notes_appended_as_data_block_only_when_set(config, tmp_path):
    plain = ask.render("diagnose", "unique-stem", config, tmp_path)
    assert specs.data_open("host_notes") not in plain  # Unset notes must not create a block.
    config.ask_notes = "host guidance\n" + specs.data_close("host_notes")
    rendered = ask.render("diagnose", "unique-stem", config, tmp_path)
    assert (
        rendered == plain + "\n" + specs.data_open("host_notes") + "\nhost guidance\n[chupa-data:end host_notes>>\n" + specs.data_close("host_notes") + "\n"
    )  # Raw delimiters cannot escape the block.


def test_prompt_verb_refuses_missing_ticket(config, tmp_path, capsys):
    assert main(["prompt", "review", "missing-stem"], cwd=tmp_path) == 2  # A missing ticket must refuse.
    err = capsys.readouterr().err
    assert "tickets/missing-stem/ticket.md does not exist" in err and "chupa new missing-stem" in err  # Refusal identifies both cause and remedy.
    assert main(["prompt", "review", "Bad_Stem"], cwd=tmp_path) == 2  # Invalid stems must refuse before path access.
    assert "kebab-case" in capsys.readouterr().err


def test_state_dir_outside_repo_renders_absolute(config, tmp_path):
    config.state_dir = tmp_path.parent / "outside-state"
    text = ask.render("running", "unique-stem", config, tmp_path)
    assert str(config.state_dir / "engine.log") in text  # A repo-relative or default path differs.


def test_prompt_verb_writes_no_state(config, tmp_path, capsys):
    ticket = tmp_path / "tickets/unique-stem/ticket.md"
    ticket.parent.mkdir(parents=True)
    ticket.write_text("ticket")
    assert main(["prompt", "diagnose", "unique-stem"], cwd=tmp_path) == 0  # An existing ticket succeeds.
    assert "tickets/unique-stem/ticket.md" in capsys.readouterr().out  # The verb prints the requested prompt.
    assert not config.state_dir.exists()  # Constructing a lock or journal would create state.


def test_box_prompt_names_requested_files(config, tmp_path, capsys):
    from chupa.box import Box
    from chupa.seams import LocalFileSystem

    box = Box(config.state_dir / "box", LocalFileSystem())
    ids = [box.enqueue(message_class="suggestion", origin=str(n), summary=f"idea {n}")[0] for n in range(2)]
    assert main(["prompt", "box", *ids], cwd=tmp_path) == 0
    output = capsys.readouterr().out
    for id in ids:
        assert f"{id}: custom/state/box/{box.path(box.get(id)).name}" in output  # Each requested file uses the configured state directory.
    assert '"Recommendation"' in output  # The prompt asks for actionable advice.


def test_box_prompt_unknown_id_refuses(config, tmp_path, capsys):
    assert main(["prompt", "box", "missing-id"], cwd=tmp_path) == 2
    assert "unknown box id missing-id -- name ids that chupa status lists" in capsys.readouterr().err


def test_drafts_prompt_selects_committed_drafts(tmp_path, capsys):
    from tests.integration.test_cli import git_out
    from tests.integration.test_drain import confirmed, make_root

    root = make_root(tmp_path)
    for stem, state in (("committed-draft", "draft"), ("confirmed-ticket", "confirmed"), ("untracked-draft", "draft")):
        path = root / "tickets" / stem / "ticket.md"
        path.parent.mkdir(parents=True)
        path.write_text(confirmed().replace("state: confirmed", f"state: {state}"))
        if stem != "untracked-draft":
            git_out(root, "add", str(path.relative_to(root)))
    git_out(root, "commit", "-m", "tickets")
    assert main(["prompt", "drafts"], cwd=root) == 0  # Committed draft is actionable.
    output = capsys.readouterr().out
    assert "committed-draft" in output  # Dropping the committed draft is wrong.
    assert "confirmed-ticket" not in output and "untracked-draft" not in output  # Neither other row is actionable.
    assert not (root / ".chupa").exists()  # The read-only prompt must not write state.
