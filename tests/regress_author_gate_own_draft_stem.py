"""Carried reproducer for an author gate rejecting its own draft stem."""

import json
import sys
import tempfile
import traceback
from pathlib import Path
from types import SimpleNamespace


def main() -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    try:
        from chupa import author

        author.validate_ticket = lambda stem, text, repo: None
        with tempfile.TemporaryDirectory() as directory:
            events = []
            checkout = SimpleNamespace(repo=Path(directory), journal=SimpleNamespace(read=lambda: events))
            candidate = author.AuthorReply(stem="draft-stem", ticket="t")
            gate = author.AuthorGate(checkout)
            first = gate.check(candidate, checkout.repo)
            if first.verdict != "pass":
                raise ValueError(f"first check failed: {first}")
            events.append(SimpleNamespace(ticket="draft-stem", key="llm/author/1/requisition_review/7/1"))
            second = gate.check(candidate, checkout.repo)
            fresh = author.AuthorGate(checkout).check(candidate, checkout.repo)

            def journal_finding(report):
                return any("already named in the journal" in finding.message for finding in report.findings)

            if fresh.verdict != "fail" or not journal_finding(fresh):
                raise ValueError(f"fresh gate did not reject journal stem: {fresh}")
            if second.verdict == "fail" and journal_finding(second):
                print(json.dumps({"regression_result": "defect"}))
                return 1
            if second.verdict != "pass":
                raise ValueError(f"second check failed unexpectedly: {second}")
    except Exception:
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"regression_result": "error"}))
        return 2
    print(json.dumps({"regression_result": "pass"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
