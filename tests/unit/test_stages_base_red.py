from chupa.stages import _names_branch_only_path


def test_dash_prefixed_token_is_skipped():
    assert not _names_branch_only_path(["-new"], {"-new"}.__contains__, set().__contains__)


def test_node_id_is_cut_to_its_file():
    assert _names_branch_only_path(["tests/new.py::test_one"], {"tests/new.py"}.__contains__, set().__contains__)


def test_token_present_in_both_worktrees_is_not_branch_only():
    assert not _names_branch_only_path(["tests/existing.py"], {"tests/existing.py"}.__contains__, {"tests/existing.py"}.__contains__)


def test_token_present_only_in_branch_is_branch_only():
    assert _names_branch_only_path(["tests/new.py"], {"tests/new.py"}.__contains__, set().__contains__)
