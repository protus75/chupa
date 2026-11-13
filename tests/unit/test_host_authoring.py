"""Keep critical ticket-writing guidance in the host authoring guide."""

from pathlib import Path


def test_critical_authoring_guidance_is_present():
    doc = (Path(__file__).resolve().parents[2] / "chupa/docs/host-authoring.md").read_text()
    for phrase in (
        "has a criterion whose test fails when the invariant is dropped",
        "depends on the ticket that creates it",
        "names every edit the change forces there",
        "reads its fence and criteria",
        "names the one expectation that may change",
        "marked hand-built",
        "before any change that destroys it",
    ):
        assert phrase in doc
