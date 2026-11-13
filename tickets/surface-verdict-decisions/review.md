# Review: snag

The projection, render, snapshot and extension changes meet the acceptance criteria, but a rejected decision's null verb shows as the literal `None` in `chupa status` and as an empty string in the extension, and the unit test locks in the `None` output.

## Findings

- [logic] chupa/status.py:162 The projection passes `e.body["verb"]` through unchanged. Every `rejected` control_decision journals `verb: None` (chupa/control.py:232 and the check at :141), so each rejected row carries `None`. `render` (status.py:211) then formats it as `a-request: None : rejected -- ...`, which shows a Python `None` to the operator. The extension draws the same row without it. The ticket already maps an absent `stem` to "" so one projection serves both surfaces, but it does not do the same for `verb`. (do instead: Normalize the verb in the projection the same way as stem (for example `e.body["verb"] or ""`), type the field `str`, and let both render and the snapshot use that value.)
- [logic] vscode-chupa/media/view.js:73 `d.verb ?? ''` replaces a snapshot value in JavaScript. The extension shows "" for a rejected decision while `chupa status` shows `None`, so the two surfaces disagree on the same row. Substituting values in JavaScript also breaks the rule that the extension only draws given fields. (do instead: Have the Python projection emit "" for a missing verb, then draw `${d.verb}` directly with no null handling in JavaScript.)
- [logic] tests/unit/test_status_verdict_decisions.py:16 The assertion expects `- a-request: None : rejected -- invalid request` and the tuple assertion on line 15 expects `None` as the verb. Both lock in the `None` leaking into operator output instead of checking how a non-admission rejected decision should display. (do instead: After normalizing verb to "", assert the tuple `("a-request", "", "", "rejected", "invalid request")` and a render line with no `None` in it.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "745b21810734ef76c14e5ae321b58eb23b372217",
  "stem": "surface-verdict-decisions",
  "reviewed_sha": "745b21810734ef76c14e5ae321b58eb23b372217",
  "summary": "The projection, render, snapshot and extension changes meet the acceptance criteria, but a rejected decision's null verb shows as the literal `None` in `chupa status` and as an empty string in the extension, and the unit test locks in the `None` output.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/status.py",
      "line": 162,
      "message": "The projection passes `e.body[\"verb\"]` through unchanged. Every `rejected` control_decision journals `verb: None` (chupa/control.py:232 and the check at :141), so each rejected row carries `None`. `render` (status.py:211) then formats it as `a-request: None : rejected -- ...`, which shows a Python `None` to the operator. The extension draws the same row without it. The ticket already maps an absent `stem` to \"\" so one projection serves both surfaces, but it does not do the same for `verb`.",
      "paved_road": "Normalize the verb in the projection the same way as stem (for example `e.body[\"verb\"] or \"\"`), type the field `str`, and let both render and the snapshot use that value.",
      "kind": null,
      "unit": null
    },
    {
      "code": "logic",
      "path": "vscode-chupa/media/view.js",
      "line": 73,
      "message": "`d.verb ?? ''` replaces a snapshot value in JavaScript. The extension shows \"\" for a rejected decision while `chupa status` shows `None`, so the two surfaces disagree on the same row. Substituting values in JavaScript also breaks the rule that the extension only draws given fields.",
      "paved_road": "Have the Python projection emit \"\" for a missing verb, then draw `${d.verb}` directly with no null handling in JavaScript.",
      "kind": null,
      "unit": null
    },
    {
      "code": "logic",
      "path": "tests/unit/test_status_verdict_decisions.py",
      "line": 16,
      "message": "The assertion expects `- a-request: None : rejected -- invalid request` and the tuple assertion on line 15 expects `None` as the verb. Both lock in the `None` leaking into operator output instead of checking how a non-admission rejected decision should display.",
      "paved_road": "After normalizing verb to \"\", assert the tuple `(\"a-request\", \"\", \"\", \"rejected\", \"invalid request\")` and a render line with no `None` in it.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.5",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
