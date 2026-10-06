"""Fault-injection member for merge admission's refused-rebase cleanup."""

import json
import subprocess

from chupa.journal import EventType
from chupa.git import RebaseRefused
from eval.shakeout.bench import Bench
from eval.shakeout.run import Member, Observation
from eval.shakeout.stages import _commit, _configure_diagnosis, _finding, _ticket


async def _conflicted_rebase(bench: Bench) -> Observation:
    stem = "conflicted-rebase"
    target = "merge.txt"
    bench.add_ticket(stem, _ticket(stem, target, f"test -f {target}"))
    _configure_diagnosis(bench)
    reviewed_sha: list[str] = []
    main_at_admission: dict[str, str] = {}
    refusal: dict[str, str] = {}
    cleanup: dict[str, object] = {}
    remove = bench.git.worktree_remove
    rebase = bench.git.rebase
    diff = bench.git.diff

    async def observe_rebase(dir, onto) -> None:
        main_at_admission["before"] = await bench.git.rev_parse(bench.repo, "main")
        try:
            await rebase(dir, onto)
        except RebaseRefused:
            main_at_admission["after"] = await bench.git.rev_parse(bench.repo, "main")
            refusal["head"] = await bench.git.rev_parse(dir, "HEAD")
            refusal["status"] = await bench.git._run(dir, "status")
            raise

    async def observe_diff(dir, base, branch) -> str:
        if base == "main" and branch == stem:
            reviewed_sha.append(await bench.git.rev_parse(bench.repo, stem))
        return await diff(dir, base, branch)

    async def observe_remove(dir, path) -> None:
        if path == bench.config.worktree_root / stem:
            git_dir = await bench.git._run(path, "rev-parse", "--git-dir")
            status = await bench.git._run(path, "status")
            cleanup.update({
                "git_dir": git_dir.strip(),
                "status": status,
                "head": await bench.git.rev_parse(path, "HEAD"),
                "main": await bench.git.rev_parse(bench.repo, "main"),
                "rebase_merge": (path / git_dir.strip() / "rebase-merge").exists(),
                "rebase_apply": (path / git_dir.strip() / "rebase-apply").exists(),
            })
        await remove(dir, path)

    bench.git.worktree_remove = observe_remove
    bench.git.rebase = observe_rebase
    bench.git.diff = observe_diff

    def implement(request) -> str:
        return _commit(request, {target: "branch\n"})

    def move_main(_request) -> str:
        (bench.repo / target).write_text("main\n")
        subprocess.run(["git", "-C", str(bench.repo), "add", target], env=bench.env, check=True)
        subprocess.run(["git", "-C", str(bench.repo), "commit", "-m", "shakeout main conflict"],
                       env=bench.env, check=True, capture_output=True)
        return json.dumps({"verdict": "approve", "summary": "approved", "findings": []})

    bench.script([implement, move_main,
                  json.dumps({"verdict": "reject", "lessons": ["resolve the conflict"]})])
    report = await bench.drain()

    terminals = [event.body for event in bench.journal.read()
                 if event.type == EventType.STATE_TRANSITION and event.ticket == stem
                 and event.body.get("to") == "gate_failed"]
    assert terminals, (report.render(), [event.body for event in bench.journal.read()
                                         if event.type == EventType.STATE_TRANSITION and event.ticket == stem], cleanup,
                       main_at_admission)
    terminal, = terminals
    finding = _finding(bench, stem, "post_rebase_regate")
    assert terminal["stage"] == "merge"
    assert refusal["head"] == reviewed_sha[-1]
    assert main_at_admission["before"] == main_at_admission["after"]
    assert not cleanup["rebase_merge"] and not cleanup["rebase_apply"]
    assert "rebase in progress" not in refusal["status"].lower()
    assert "rebase in progress" not in cleanup["status"].lower()
    assert finding.code == "post_rebase_regate"
    return Observation("conflicted_rebase_refused_cleanly", f"{stem}/0")


MEMBERS = (
    Member("conflicted_rebase", "merge", "main and branch edit the same line after Review",
           "conflicted_rebase_refused_cleanly", _conflicted_rebase),
)
