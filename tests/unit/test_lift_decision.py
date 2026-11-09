from chupa.artifacts import SHAKEOUT_REPORT
from chupa.stages import LIFT_MAX_BYTES, _lift_decision


def test_lift_decision_selects_named_artifact_per_kind():
    assert _lift_decision("review", None, "review.md", False, 1) == "lift"
    assert _lift_decision("review", None, "run.md", False, 1) == "skip"
    assert _lift_decision("review", None, "notes.txt", False, 1) == "skip"
    assert _lift_decision("checks", None, "checks.json", False, 1) == "lift"
    assert _lift_decision("checks", None, f"nested/{SHAKEOUT_REPORT}", False, 1) == "lift"
    assert _lift_decision("unknown", None, "run.md", False, 1) == "skip"


def test_lift_decision_skips_symlink():
    assert _lift_decision("run-record", None, "run.md", True, 1) == "skip"


def test_lift_decision_only_overrides_kind():
    assert _lift_decision("harvest-rework", "attempts/1/harvest.json", "attempts/1/harvest.json", False, 1) == "lift"
    assert _lift_decision("harvest-rework", "attempts/1/harvest.json", "run.md", False, 1) == "skip"


def test_lift_decision_size_limit():
    assert _lift_decision("run-record", None, "run.md", False, LIFT_MAX_BYTES) == "lift"
    assert _lift_decision("run-record", None, "run.md", False, LIFT_MAX_BYTES + 1) == "too_large"
