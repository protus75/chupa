import pytest
from pydantic import ValidationError

from chupa.artifacts import (
    DAEMON_SOAK_MEMBERS,
    RELIABILITY_BATTERY_MEMBERS,
    BaselineSignal,
    DaemonSoakReport,
    ReliabilityBatteryReport,
    ReviewBaselineReport,
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
    daemon_expected = (
        ("abandoned_alerted_then_merged", "alert"),
        ("mechanical_and_rework_main_green", "resolved"),
        ("integration_red_main_green", "refused"),
    )
    daemon = [
        dict(member=member, planted_fault="fault", expected=expected, observed=expected, disposition=disposition, producing_run="member-0/0", auditor=[], green=True)
        for member, (expected, disposition) in zip(DAEMON_SOAK_MEMBERS, daemon_expected)
    ]
    battery_expected = ("quota_classified_cooldown_persisted", "all_cooling_held_timer_fired_recovered", "unknown_failure_unclassified")
    battery = [
        dict(member=member, planted_fault="fault", expected=expected, observed=expected, producing_run="member-0/0", auditor=[], green=True)
        for member, expected in zip(RELIABILITY_BATTERY_MEMBERS, battery_expected)
    ]
    for model, members, entries in (
        (DaemonSoakReport, DAEMON_SOAK_MEMBERS, daemon),
        (ReliabilityBatteryReport, RELIABILITY_BATTERY_MEMBERS, battery),
    ):
        data = dict(produced_by_spec_version=1, produced_at_sha="abc", entries=entries)
        assert tuple(entry.member for entry in model(**data).entries) == members
        with pytest.raises(ValidationError) as exc:
            model(**(data | {"entries": list(reversed(entries))}))
        assert f"entries must contain exactly {members}, in order" in str(exc.value)
