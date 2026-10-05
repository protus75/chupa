"""Findings-fed re-entry behind the `drain` verb (CHUPA_PLAN.md sections 11.2, 19.P1) against a temp checkout.

A stem re-offered after a non-ok terminal renders the prior terminal's durable findings artifacts (review.md
reject findings, a failing checks.json) as a prior-attempts block in criteria-position; ticket.md is never
written. The production stage pipeline runs behind a scripted FakeLLM.
"""

from pathlib import Path

from chupa import runner
from chupa.__main__ import main
from chupa.llm import FakeLLM
from chupa.specs import data_close, data_open
from chupa.stages import PRIOR_ATTEMPTS
from tests.test_stages import ENV, SNAG, STEM, agent, git, verdict
from tests.test_terminal import author, clock, repo, transitions  # noqa: F401 -- `repo` is the fixture


class NoChild:
    """The merge admits `chupa/thing.py`, a self-upgrade: the handoff's re-exec is faked to a quiescent child."""

    async def run(self, argv, *, cwd, env, timeout, stdin_path=None):
        return 0, "", ""


def drain(repo: Path, script: list) -> tuple[int, FakeLLM]:
    llm = FakeLLM(script)
    code = main(["drain"], cwd=repo, env=ENV, clock=clock, pipeline=lambda c: runner.bind(c, llm), reexec=NoChild())
    return code, llm


def implements(llm: FakeLLM) -> list[str]:
    return [r.rendered for r in llm.requests if r.surface == "implement"]


def ticket_block(rendered: str) -> str:
    """The rendered ticket data block: the prompt section the acceptance criteria live in."""
    return rendered.split(data_open("ticket"), 1)[1].split(data_close("ticket"), 1)[0]


def between_criteria_and_next_section(block: str) -> str:
    return block.split("## Acceptance criteria", 1)[1].split("## Verification", 1)[0]


def test_a_reoffer_after_a_review_reject_renders_its_findings_in_criteria_position(repo):
    author(repo)
    ticket_md = None

    def capture_ticket(req):
        nonlocal ticket_md
        ticket_md = (repo / "tickets" / STEM / "ticket.md").read_text()
        return agent({"chupa/thing.py": "ok\n"})(req)

    code, llm = drain(repo, [agent({"chupa/thing.py": "ok\n"}), verdict("snag", [SNAG]),
                             capture_ticket, verdict()])

    assert code == 0
    assert [t["to"] for t in transitions(repo)] == ["running", "gate_failed", "running", "merged"]
    first, second = implements(llm)
    assert PRIOR_ATTEMPTS not in first
    block = ticket_block(second)
    criteria = between_criteria_and_next_section(block)
    assert PRIOR_ATTEMPTS in criteria
    assert SNAG["message"] in criteria and SNAG["paved_road"] in criteria
    # Rendered fresh, never written into the ticket file.
    assert PRIOR_ATTEMPTS not in ticket_md
    assert PRIOR_ATTEMPTS not in git(repo, "show", f"main:tickets/{STEM}/ticket.md")


def test_a_reoffer_after_a_red_check_renders_the_failing_checks(repo):
    author(repo)
    code, llm = drain(repo, [agent({"chupa/thing.py": "nope\n"}), agent({"chupa/thing.py": "ok\n"}), verdict()])

    assert code == 0
    first, second = implements(llm)
    assert PRIOR_ATTEMPTS not in first
    criteria = between_criteria_and_next_section(ticket_block(second))
    assert PRIOR_ATTEMPTS in criteria
    assert "`gate_failed` at check" in criteria
    assert "`grep -q ok chupa/thing.py` exited 1" in criteria  # the red verification command's finding


def test_a_stale_review_md_never_feeds_a_later_check_failure(repo):
    # Attempt 1 rejected at review; attempt 2 went red at check: attempt 3 sees the check, not the stale reject.
    author(repo)
    code, llm = drain(repo, [agent({"chupa/thing.py": "ok\n"}), verdict("snag", [SNAG]),
                             agent({"chupa/thing.py": "nope\n"}),
                             agent({"chupa/thing.py": "ok\n"}), verdict()])

    assert code == 0
    third = between_criteria_and_next_section(ticket_block(implements(llm)[2]))
    assert "`gate_failed` at check" in third
    assert SNAG["message"] not in third
