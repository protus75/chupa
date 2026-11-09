from chupa.__main__ import stuck_ceiling_finding


def test_stuck_over_ceiling_finding():
    finding = stuck_ceiling_finding(91, 90)
    assert finding is not None
    assert "91m" in finding and "90m" in finding
    assert "lower `- stuck:`" in finding and "split" in finding
    assert stuck_ceiling_finding(90, 90) is None
