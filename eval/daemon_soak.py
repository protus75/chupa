"""Canonical soak report writer (CHUPA_PLAN.md 19.P3.daemon-soak)."""

from pathlib import Path

from chupa.artifacts import DaemonSoakReport
from chupa.seams import FileSystem


def write_report(path: Path, report: DaemonSoakReport, fs: FileSystem) -> None:
    # Revalidate nested lists and values that model_construct/model_copy can bypass.
    validated = DaemonSoakReport.model_validate(report.model_dump())
    if any(not entry.green for entry in validated.entries):
        raise ValueError("refusing a red daemon soak report; resolve observations and auditor violations first")
    fs.write(path, (validated.model_dump_json(indent=2) + "\n").encode("utf-8"))
