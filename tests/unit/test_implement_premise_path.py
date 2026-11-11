"""Implement premise failures must identify the affected file."""

import pytest
from pydantic import ValidationError

from chupa.stages import ImplementReply


def test_premise_findings_need_paths():
    reply = {
        "outcome": "premise_failed",
        "summary": "blocked",
        "surprises": "none",
        "dead_ends": "none",
        "predicted_vs_actual": "none",
        "findings": [{"code": "premise", "path": None, "message": "contradiction", "paved_road": "correct ticket"}],
    }
    with pytest.raises(ValidationError) as exc:
        ImplementReply.model_validate(reply)
    assert "naming `path`" in str(exc.value)
    assert "implement the ticket" in str(exc.value)

    reply["findings"][0]["path"] = "tickets/example/ticket.md"
    assert ImplementReply.model_validate(reply).findings[0].path == "tickets/example/ticket.md"
    reply["findings"][0]["path"] = " "
    with pytest.raises(ValidationError):
        ImplementReply.model_validate(reply)
    reply["outcome"] = "ok"
    reply["findings"] = []
    assert ImplementReply.model_validate(reply).outcome == "ok"
