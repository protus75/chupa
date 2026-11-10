from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from chupa.artifacts import (
    BaselineSignal,
    ReviewBaselineReport,
    _check_ordered_members,
    _check_producing_run,
)


def test_producing_run_check():
    assert _check_producing_run("member-0/0") is None
    for invalid in ("nosep", "member/x1", "Upper/0"):
        with pytest.raises(ValueError, match="producing_run must be <ticket stem>/<nonnegative run sequence>"):
            _check_producing_run(invalid)


def test_integer_version_check():
    for model, field, message in (
        (BaselineSignal, "v", "signal v must be the integer 1"),
        (ReviewBaselineReport, "schema_version", "schema_version must be the integer 1"),
    ):
        with pytest.raises(ValidationError) as exc:
            model.model_validate({field: True})
        assert any(error["loc"] == (field,) and error["msg"] == f"Value error, {message}" for error in exc.value.errors())


def test_ordered_members_check():
    members = ("first", "second", "third")
    entries = [SimpleNamespace(member=member) for member in members]
    assert _check_ordered_members(entries, members) is None
    with pytest.raises(ValueError) as exc:
        _check_ordered_members(list(reversed(entries)), members)
    assert str(exc.value) == f"entries must contain exactly {members}, in order"
