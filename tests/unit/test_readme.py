"""Keep the PyPI README suitable for host users."""

import argparse
import re
from pathlib import Path

from chupa.__main__ import _parser

README = Path(__file__).resolve().parents[2] / "README.md"


def test_links_are_absolute():
    targets = re.findall(r"\]\(([^)]*)\)", README.read_text())
    assert all(target.startswith("https://") for target in targets)


def test_dev_commands_only_in_developer_section():
    readme = README.read_text()
    heading = "## Developing chupa"
    assert readme.count(heading) == 1
    first_command = readme.find("./dev.py")
    assert first_command == -1 or first_command > readme.index(heading)


def test_links_github_project():
    targets = re.findall(r"\]\(([^)]*)\)", README.read_text())
    assert "https://github.com/protus75/chupa" in targets


def test_chupa_verbs_exist():
    verbs = re.findall(r"uv run chupa ([^\s`]+)", README.read_text())
    subcommands = next(action for action in _parser()._actions if isinstance(action, argparse._SubParsersAction))
    assert all(verb in subcommands.choices for verb in verbs if verb != "<verb>" and not verb.startswith("-"))
