from chupa import ask, specs
from chupa.config import load_config
from tests.integration.test_config import VALID


def test_render_drafts(tmp_path):
    (tmp_path / "config.yaml").write_text(VALID.replace("state_dir: .chupa", "state_dir: custom/state"))
    config = load_config(None, cwd=tmp_path)
    config.ask_notes = "specific guidance"
    text = ask.render("drafts", ["a-one", "b-two"], config, tmp_path)
    assert text.index("- a-one: tickets/a-one/ticket.md") < text.index("- b-two: tickets/b-two/ticket.md")  # Neither a fixed path nor reversed stems works.
    assert "custom/state/box/" in text  # The default state path is wrong.
    for expected in ('"Recommendation"', "./dev.py confirm --yes", "./dev.py reject --yes", "gold plating"):
        assert expected in text  # Omitting either verdict or its bar loses instructions.
    assert text.endswith(f"{specs.data_open('host_notes')}\nspecific guidance\n{specs.data_close('host_notes')}\n")  # Notes must be appended as data.
