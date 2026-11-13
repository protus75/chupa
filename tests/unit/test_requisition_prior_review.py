import asyncio
import inspect

from chupa.journal import Event, EventType
from chupa.requisition import FIRST_REVIEW, prior_review, render_prior_review, review_ticket


class FakeGit:
    def __init__(self):
        self.calls = []
        self.blobs = {"old-sha": "a\n", "new-sha": "later\n"}

    async def _run(self, repo, *args):
        self.calls.append((repo, *args))
        return self.blobs[args[1]]


def event(stem, body, type=EventType.SIGNAL):
    return Event(1, type, "time", stem, None, body)


def verdict(stem, sha, findings, verdict="snag"):
    return event(stem, {"signal": "requisition_verdict", "ticket_sha": sha, "verdict": verdict, "findings": findings})


def test_prior_is_required():
    assert inspect.signature(review_ticket).parameters["prior"].default is inspect.Parameter.empty


def test_missing_or_legacy_verdict_returns_first_review():
    git = FakeGit()
    for events in ([], [verdict("other", "old-sha", [])], [event("one", {"signal": "requisition_verdict"})], [event("one", {"signal": "other", "findings": []})]):
        assert asyncio.run(prior_review(git, "repo", events, "one", "current")) == FIRST_REVIEW
    assert git.calls == []


def test_findings_and_diff_use_latest_matching_verdict():
    git = FakeGit()
    events = [verdict("one", "new-sha", [{"code": "old", "message": "obsolete"}]), verdict("one", "old-sha", [{"code": "fence_gap", "message": "missing x"}])]
    result = asyncio.run(prior_review(git, "repo", events, "one", "a\nb\n"))
    assert "Verdict: snag" in result
    assert "- [fence_gap] missing x" in result
    assert "+b" in result
    assert "obsolete" not in result
    assert git.calls == [("repo", "show", "old-sha")]


def test_approval_with_no_findings_and_unchanged_text():
    git = FakeGit()
    result = asyncio.run(prior_review(git, "repo", [verdict("one", "old-sha", [], "approve")], "one", "a\n"))
    assert "Verdict: approve" in result
    assert "- none" in result
    assert "(unchanged)" in result


def test_shared_renderer_matches_recorded_review():
    findings = [{"code": "gap", "message": "missing\ncase"}]
    recorded = asyncio.run(prior_review(FakeGit(), "repo", [verdict("one", "old-sha", findings)], "one", "a\nnew\n"))
    assert render_prior_review("snag", findings, "a\n", "a\nnew\n") == recorded
    assert "- [gap] missing case" in recorded and "+new" in recorded
