from chupa import ask
from chupa.__main__ import main
from chupa.config import load_config
from tests.integration.test_config import VALID


def test_drain_loop_renders_state_dir_and_loop_prefix(tmp_path):
    (tmp_path / "config.yaml").write_text(VALID.replace("state_dir: .chupa", "state_dir: custom/state"))
    config = load_config(None, cwd=tmp_path)
    text = ask.render("drain-loop", "", config, tmp_path)
    assert text.startswith("/loop ")  # Dropping the loop prefix differs.
    assert "custom/state/drain.out" in text  # A fixed state path differs.
    assert ".chupa/state" not in text  # A hard-coded default differs.


def test_drain_loop_keeps_owner_verdict_limits(tmp_path):
    (tmp_path / "config.yaml").write_text(VALID)
    text = ask.render("drain-loop", "", load_config(None, cwd=tmp_path), tmp_path)
    assert "Never run `confirm` or `reject`" in text  # Omitting owner verdict limits differs.
    assert "ticket_changed" in text  # Omitting the running-ticket hold differs.


def test_prompt_verb_drain_loop_prints_without_state(tmp_path, capsys):
    (tmp_path / "config.yaml").write_text(VALID)
    config = load_config(None, cwd=tmp_path)
    assert main(["prompt", "drain-loop"], cwd=tmp_path) == 0  # A refusal differs.
    assert capsys.readouterr().out.startswith("/loop ")  # Empty or non-loop output differs.
    assert not config.state_dir.exists()  # Taking a lock or writing state creates the directory.
