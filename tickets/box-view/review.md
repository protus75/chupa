# Review: snag

The snapshot, menus and box view match the ticket, but on every snapshot refresh both webviews re-post their focus, so Details ends up on whichever view posted last instead of the last row hovered or pinned.

## Findings

- [logic] vscode-chupa/media/box.js:24 update() runs on every render, so each snapshot refresh posts {type:'focus', id: pinned ?? hovered}. The Tickets view's view.js also calls focus() on every render. Suppose a ticket and a box message are both pinned and the operator last pinned or hovered the ticket. On the next refresh, both views post their focus and the second one to arrive replaces the first, so Details can jump to the box message. The ticket requires Details to show the item last hovered or pinned, falling back to the other view's pin. (do instead: Post focus from box.js only on user actions (hover, mouseleave, click, contextmenu, keys), not on data renders. When a render drops the pinned id, post the focus change only if the id really changed. Alternatively, have DetailsView.setFocus ignore a post whose id equals the id already recorded in this.focuses[kind], so a repeated post does not take focus back.)
- [logic] vscode-chupa/extension.js:229 setFocus moves focus to `kind` whenever `id` is truthy, even when the id has not changed since that view's last post. Because both views re-post their unchanged pins on every refresh, the last view to post takes focus instead of the view the operator last used. (do instead: Change this.focus only when the id differs from this.focuses[kind] (save the old value before overwriting it). Keep the existing fallback to the other view's pin when the id is cleared.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "f8ff7afdb6b9ea2d31abf5e707a4c2f02b1f2b0d",
  "stem": "box-view",
  "reviewed_sha": "f8ff7afdb6b9ea2d31abf5e707a4c2f02b1f2b0d",
  "summary": "The snapshot, menus and box view match the ticket, but on every snapshot refresh both webviews re-post their focus, so Details ends up on whichever view posted last instead of the last row hovered or pinned.",
  "findings": [
    {
      "code": "logic",
      "path": "vscode-chupa/media/box.js",
      "line": 24,
      "message": "update() runs on every render, so each snapshot refresh posts {type:'focus', id: pinned ?? hovered}. The Tickets view's view.js also calls focus() on every render. Suppose a ticket and a box message are both pinned and the operator last pinned or hovered the ticket. On the next refresh, both views post their focus and the second one to arrive replaces the first, so Details can jump to the box message. The ticket requires Details to show the item last hovered or pinned, falling back to the other view's pin.",
      "paved_road": "Post focus from box.js only on user actions (hover, mouseleave, click, contextmenu, keys), not on data renders. When a render drops the pinned id, post the focus change only if the id really changed. Alternatively, have DetailsView.setFocus ignore a post whose id equals the id already recorded in this.focuses[kind], so a repeated post does not take focus back.",
      "kind": null,
      "unit": null
    },
    {
      "code": "logic",
      "path": "vscode-chupa/extension.js",
      "line": 229,
      "message": "setFocus moves focus to `kind` whenever `id` is truthy, even when the id has not changed since that view's last post. Because both views re-post their unchanged pins on every refresh, the last view to post takes focus instead of the view the operator last used.",
      "paved_road": "Change this.focus only when the id differs from this.focuses[kind] (save the old value before overwriting it). Keep the existing fallback to the other view's pin when the id is cleared.",
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
