"""Validate coverage thresholds and evaluate a coverage.py JSON report."""

import json
import math
import sys
import tomllib
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


class GateInvalid(ValueError):
    def __init__(self, key: str, reason: str):
        self.key = key
        super().__init__(f"{key}: {reason}")


@dataclass(frozen=True)
class Gate:
    default: float
    repository: float
    packages: dict[str, float]
    files: dict[str, float]
    budget_seconds: float
    repository_explicit: bool


def parse_gate(text: str) -> Gate:
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise GateInvalid("gate", str(exc)) from exc

    def table(value, key, allowed):
        if not isinstance(value, dict):
            raise GateInvalid(key, "expected a table")
        for name in value:
            if name not in allowed:
                raise GateInvalid(f"{key}.{name}" if key else name, "unknown key")
        return value

    def number(value, key, *, budget=False):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or (value <= 0 if budget else not 0 <= value <= 100):
            raise GateInvalid(key, "expected a positive number" if budget else "expected a number from 0 to 100")
        return value

    def paths(value, key):
        if not isinstance(value, dict):
            raise GateInvalid(key, "expected a table")
        result = {}
        for path, threshold in value.items():
            dotted = f"{key}.{path}"
            p = PurePosixPath(path)
            if not path or p.is_absolute() or str(p) != path or any(part in (".", "..") for part in path.split("/")) or "\\" in path:
                raise GateInvalid(dotted, "expected a repo-relative POSIX path")
            result[path] = number(threshold, dotted)
        return result

    table(data, "", {"coverage", "unit"})
    coverage = table(data.get("coverage", {}), "coverage", {"default", "repository", "packages", "files"})
    if "default" not in coverage:
        raise GateInvalid("coverage.default", "required")
    default = number(coverage["default"], "coverage.default")
    unit = table(data.get("unit", {}), "unit", {"budget_seconds"})
    return Gate(
        default,
        number(coverage.get("repository", default), "coverage.repository"),
        paths(coverage.get("packages", {}), "coverage.packages"),
        paths(coverage.get("files", {}), "coverage.files"),
        number(unit.get("budget_seconds", 60), "unit.budget_seconds", budget=True),
        "repository" in coverage,
    )


def evaluate(gate: Gate, report: dict) -> list[str]:
    """Return failures; reject reports that cannot provide the required counts."""
    try:
        if not isinstance(report, dict) or report["meta"]["format"] != 3 or not isinstance(report["files"], dict):
            raise ValueError("expected coverage.py JSON format 3")
        files = report["files"]
        counts = {}
        for path, entry in files.items():
            summary = entry["summary"]
            values = [summary["covered_lines"], summary["num_statements"], summary.get("covered_branches", 0), summary.get("num_branches", 0)]
            if (
                not isinstance(path, str)
                or any(type(n) is not int or n < 0 for n in values)
                or values[0] > values[1]
                or values[2] > values[3]
                or not isinstance(entry["missing_lines"], list)
                or any(type(n) is not int or n < 1 for n in entry["missing_lines"])
            ):
                raise ValueError("invalid file summary or missing lines")
            counts[path] = values
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError("invalid coverage.py JSON report") from exc

    def percent(paths):
        covered = sum(counts[p][0] + counts[p][2] for p in paths)
        total = sum(counts[p][1] + counts[p][3] for p in paths)
        return 100 * covered / total if total else 100.0

    def matches(path, package):
        return path == package or path.startswith(package + "/")

    failures = []
    road = "add unit tests that execute the missing lines. Lowering a threshold in the gate file is a human ticket's decision."

    def check(name, paths, minimum, source, missing=None):
        value = percent(paths)
        if value < minimum:
            lines = f"; missing lines: {missing}" if missing is not None else ""
            failures.append(f"{name}: {value:.2f}% below {minimum}% ({source}){lines} -- {road}")

    check("repository", files, gate.repository, "coverage.repository" if gate.repository_explicit else "coverage.default")
    for package, minimum in gate.packages.items():
        check(package, [p for p in files if matches(p, package)], minimum, f"coverage.packages.{package}")
    for path, entry in files.items():
        packages = [p for p in gate.packages if matches(path, p)]
        if path in gate.files:
            minimum, source = gate.files[path], f"coverage.files.{path}"
        elif packages:
            package = max(packages, key=len)
            minimum, source = gate.packages[package], f"coverage.packages.{package}"
        else:
            minimum, source = gate.default, "coverage.default"
        check(path, [path], minimum, source, entry["missing_lines"])
    return failures


def run_gate(argv: Sequence[str], *, gate_path: Path, report_path: Path, run: Callable[[Sequence[str]], int]) -> int:
    try:
        report_path.unlink(missing_ok=True)
    except OSError as exc:
        print(f"chupa covgate: cannot remove report {report_path}: {exc} -- make the report writable and retry", file=sys.stderr)
        return 2
    rc = run(argv)
    if rc:
        return rc
    try:
        gate = parse_gate(gate_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, GateInvalid) as exc:
        print(f"chupa covgate: invalid gate {gate_path}: {exc} -- fix the gate file and retry", file=sys.stderr)
        return 2
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        failures = evaluate(gate, report)
    except FileNotFoundError:
        print(f"chupa covgate: missing report {report_path} -- command must write --cov-report=json:{report_path}", file=sys.stderr)
        return 2
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"chupa covgate: invalid report {report_path}: {exc} -- generate a coverage.py JSON format 3 report and retry", file=sys.stderr)
        return 2
    for failure in failures:
        print(failure)
    return 1 if failures else 0
