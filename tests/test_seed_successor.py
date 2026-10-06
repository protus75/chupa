"""End-to-end proof that a seeded successor joins the running drain."""

from datetime import UTC, datetime
from pathlib import Path

from chupa.__main__ import main
from chupa.journal import EventType, Journal
from chupa.llm import FakeLLM
from chupa import runner
from tests.test_seed_path import requisition, seed_text, seeding_text
from tests.test_stages import CONFIG, ENV, STEM, agent, git, implement_reply, verdict

SUCCESSOR = "seeded-successor"


def clock() -> datetime:
    return datetime(2026, 10, 6, tzinfo=UTC)


def seeded_successor() -> str:
    return (seed_text(SUCCESSOR).replace("chupa/thing.py", "marker.txt")
            .replace("## Depends on\nnone", f"## Depends on\n- {STEM}"))


def implement_and_seed(seed: str):
    def act(req):
        assert req.worktree is not None
        (req.worktree / "marker.txt").write_text("predecessor\n")
        git(req.worktree, "add", "marker.txt")
        git(req.worktree, "commit", "-m", "work")
        path = req.worktree / "tickets" / SUCCESSOR / "ticket.md"
        path.parent.mkdir(parents=True)
        path.write_text(seed)
        return implement_reply()

    return act


def journal(repo: Path) -> list:
    return Journal(repo / ".chupa" / "state", clock).read()


def test_a_merged_ticket_seeds_and_dispatches_its_successor_in_the_same_drain(tmp_path):
    repo = tmp_path / "repo"
    (repo / "chupa").mkdir(parents=True)
    (repo / "chupa" / "thing.py").write_text("")
    (repo / "marker.txt").write_text("")
    (repo / "CHUPA_PLAN.md").write_text("### 19.L Build laws\nSeed law.\n\n### 19.P2 Phase 2\nPhase law.\n")
    routes = (
        "  - {tier: high, surface: review, candidates: [{provider: fake}]}\n"
        "  - {tier: high, surface: requisition_review, candidates: [{provider: fake, model: high-seed}]}\n"
    )
    (repo / "config.yaml").write_text(CONFIG.replace("review: {}", routes + "review: {}"))
    (repo / ".gitignore").write_text(".chupa/\n")
    predecessor = repo / "tickets" / STEM / "ticket.md"
    predecessor.parent.mkdir(parents=True)
    predecessor.write_text(seeding_text().replace("chupa/thing.py", "marker.txt"))
    git(repo, "init", "-b", "main")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "base with predecessor")

    llm = FakeLLM([
        implement_and_seed(seeded_successor()),
        requisition("approve"),
        verdict(),
        agent({"marker.txt": "successor\n"}),
        verdict(),
    ])

    assert main(["drain"], cwd=repo, env=ENV, clock=clock,
                pipeline=lambda checkout: runner.bind(checkout, llm)) == 0

    subjects = git(repo, "log", "--format=%s", "main").splitlines()
    assert subjects.count(f"chupa({STEM}): seeds") == 1
    seed_ticket_sha = git(repo, "rev-parse", f"main:tickets/{SUCCESSOR}/ticket.md").strip()
    seed_commit = git(repo, "log", "--format=%H", "--grep", f"chupa({STEM}): seeds", "main").strip()
    events = journal(repo)
    [intake] = [e for e in events if e.type == EventType.SIGNAL and e.ticket == SUCCESSOR
                and e.body.get("signal") == "ticket_intake"]
    assert intake.body == {"signal": "ticket_intake", "source": "seed", "state": "confirmed", "new": True,
                           "commit": seed_commit, "seeded_by": STEM}
    assert seed_ticket_sha == git(repo, "rev-parse", f"{seed_commit}:tickets/{SUCCESSOR}/ticket.md").strip()

    transitions = [(e.ticket, e.body["to"]) for e in events if e.type == EventType.STATE_TRANSITION]
    assert transitions.index((STEM, "merged")) < transitions.index((SUCCESSOR, "running"))
    assert transitions[-2:] == [(SUCCESSOR, "running"), (SUCCESSOR, "merged")]
