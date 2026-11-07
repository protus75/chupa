"""Keep the host run guide's verb table aligned with the CLI."""

import argparse
import re
from pathlib import Path

from chupa.__main__ import _parser


def test_verb_table_matches_parser():
    doc = (Path(__file__).resolve().parents[2] / "docs/host-running.md").read_text()
    rows = re.findall(r"^\| `([^`]+)` \|", doc, re.M)
    subcommands = next(action for action in _parser()._actions if isinstance(action, argparse._SubParsersAction))
    # Set equality catches either an undocumented CLI verb or a stale table row.
    assert set(rows) == set(subcommands.choices)
    # A duplicate row is not another documented verb.
    assert len(rows) == len(set(rows))
