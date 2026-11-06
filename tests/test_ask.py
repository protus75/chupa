from pathlib import Path

import pytest

from chupa import ask, specs
from chupa.__main__ import main
from chupa.config import load_config
from tests.test_config import VALID


@pytest.fixture
def config(tmp_path):
    (tmp_path / "config.yaml").write_text(VALID.replace("state_dir: .chupa", "state_dir: custom/state"))
    return load_config(None, cwd=tmp_path)


@pytest.mark.parametrize("kind", ask.KINDS)
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
    assert rendered == plain + "\n" + specs.data_open("host_notes") + "\nhost guidance\n[chupa-data:end host_notes>>\n" + specs.data_close("host_notes") + "\n"  # Raw delimiters cannot escape the block.


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
