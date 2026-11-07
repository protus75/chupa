"""Build the source-to-test coverage map on demand."""

import json
from pathlib import Path
from uuid import uuid4

from chupa.git import Git, GitError
from chupa.runner import Refusal
from chupa.seams import ExecutableNotFound, FileSystem, ProcessExec
from chupa.stages import coverage_contexts


def reduce_map(report: dict) -> dict[str, list[str]]:
    return {
        name: sorted({context.split("|", 1)[0].split("::", 1)[0] for values in lines.values() for context in values if "|" in context})
        for name, lines in coverage_contexts(report).items()
    }


async def build(*, repo: Path, config, exec_: ProcessExec, git: Git, fs: FileSystem, env) -> None:
    setting = config.review.coverage_map
    if setting is None:
        raise Refusal("review.coverage_map is absent", "configure review.coverage_map and retry covmap")
    report = repo / setting.report
    try:
        report.unlink(missing_ok=True)
        rc, _, _ = await exec_.run(setting.argv, cwd=repo, env=env, timeout=None)
        if rc:
            raise Refusal(f"coverage command exited {rc}", "fix review.coverage_map.argv and retry covmap")
        try:
            files = reduce_map(json.loads(report.read_text()))
        except (OSError, UnicodeError, ValueError, KeyError, TypeError):
            raise Refusal("missing or invalid coverage report", "generate a coverage JSON report with test contexts and retry covmap") from None
        sha = await git.rev_parse(repo, "main")
        destination = config.state_dir / "coverage-map.json"
        temporary = destination.with_name(f".coverage-map-{uuid4().hex}.json")
        fs.publish(temporary, json.dumps({"sha": sha, "files": files}).encode())
        fs.replace(temporary, destination)
    except (ExecutableNotFound, TimeoutError, OSError, GitError) as exc:
        raise Refusal(f"coverage map build failed: {exc}", "fix the command, report, or repository and retry covmap") from None
    finally:
        report.unlink(missing_ok=True)
