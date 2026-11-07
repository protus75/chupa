"""SIGKILL `git status` mid-run and report whether .git/index.lock is left behind, with and without --no-optional-locks."""

import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def repo() -> Path:
    root = Path(tempfile.mkdtemp(prefix="stale-lock-"))
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, check=True)
    for i in range(20000):
        (root / f"f{i}.txt").write_text(str(i))
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "seed"], cwd=root, check=True)
    for i in range(0, 20000, 2):
        os.utime(root / f"f{i}.txt")  # stat-dirty entries make status refresh and write the index
    return root


def trial(flags: list[str]) -> tuple[int, int]:
    root = repo()
    lock = root / ".git" / "index.lock"
    proc = subprocess.Popen(["git", *flags, "-C", str(root), "status", "--porcelain"], stdout=subprocess.DEVNULL, start_new_session=True)
    seen = 0
    deadline = time.monotonic() + 10
    while proc.poll() is None and time.monotonic() < deadline:
        if lock.exists():
            seen += 1
            if seen == 3:
                os.killpg(proc.pid, signal.SIGKILL)
                break
    proc.wait()
    return seen, int(lock.exists())


for flags in ([], ["--no-optional-locks"]):
    results = [trial(flags) for _ in range(5)]
    print(f"git {' '.join(flags) or '(no flags)'} status: lock seen while running in {sum(s > 0 for s, _ in results)}/5, stale index.lock after SIGKILL in {sum(l for _, l in results)}/5")
print(subprocess.run(["git", "--version"], capture_output=True, text=True).stdout.strip(), file=sys.stdout)
