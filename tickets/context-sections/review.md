# Review: snag

Section selectors work for the tested cases, but the Markdown heading scan treats `#` lines inside fenced code blocks as headings, and a selector on a binary file crashes lint instead of producing a finding.

## Findings

- [logic] chupa/tickets.py:254 The heading scan matches every line with `^ {0,3}#{1,6}[ \t]`, including lines inside fenced code blocks. In docs/host-contract.md, the fenced comment at line 46 (`# worktree_root: .chupa/worktrees`) counts as a level-1 heading. So `docs/host-contract.md#Copyable configuration` stops at line 46 and silently drops the rest of the section. A fenced `# Two` comment could also make `#Two` look like a duplicate heading. The ticket asks for a match on ATX headings, and a fenced line is not one. (do instead: Track fence state while scanning: toggle on lines that start with ``` or ~~~ (0-3 leading spaces), and skip heading matches while inside a fence. Add a test where a `#` comment inside a fenced block does not end the excerpt.)
- [logic] chupa/tickets.py:223 context_excerpt reads the file with `(repo / path).read_text()` before it checks the selector's extension. For a selector on a non-UTF-8 file such as `assets/logo.png#x`, the read raises UnicodeDecodeError. parse_ticket catches only ValueError, so intake crashes instead of returning the required 'selector on another extension' finding. (do instead: Check the extension against the selector form before reading the file (`::` needs `.py`, `#` needs `.md`) and raise ValueError on a mismatch. Read the file only after that check passes.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "0f5cfbcd64f00038156ebeab351d8ed58eae7b69",
  "stem": "context-sections",
  "reviewed_sha": "0f5cfbcd64f00038156ebeab351d8ed58eae7b69",
  "summary": "Section selectors work for the tested cases, but the Markdown heading scan treats `#` lines inside fenced code blocks as headings, and a selector on a binary file crashes lint instead of producing a finding.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/tickets.py",
      "line": 254,
      "message": "The heading scan matches every line with `^ {0,3}#{1,6}[ \\t]`, including lines inside fenced code blocks. In docs/host-contract.md, the fenced comment at line 46 (`# worktree_root: .chupa/worktrees`) counts as a level-1 heading. So `docs/host-contract.md#Copyable configuration` stops at line 46 and silently drops the rest of the section. A fenced `# Two` comment could also make `#Two` look like a duplicate heading. The ticket asks for a match on ATX headings, and a fenced line is not one.",
      "paved_road": "Track fence state while scanning: toggle on lines that start with ``` or ~~~ (0-3 leading spaces), and skip heading matches while inside a fence. Add a test where a `#` comment inside a fenced block does not end the excerpt.",
      "kind": null,
      "unit": null
    },
    {
      "code": "logic",
      "path": "chupa/tickets.py",
      "line": 223,
      "message": "context_excerpt reads the file with `(repo / path).read_text()` before it checks the selector's extension. For a selector on a non-UTF-8 file such as `assets/logo.png#x`, the read raises UnicodeDecodeError. parse_ticket catches only ValueError, so intake crashes instead of returning the required 'selector on another extension' finding.",
      "paved_road": "Check the extension against the selector form before reading the file (`::` needs `.py`, `#` needs `.md`) and raise ValueError on a mismatch. Read the file only after that check passes.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
