---
id: tombstone-box-000213-3bd066d7
kind: tombstone
link: declined-box-000041-605fce3c
reopen_after_days: 90
---
Each stage run gets the full `caps.retry` allowance for in-stage re-prompts, and the drain draws its cross-attempt retries from a separate journal count. Section 11.1 says the two should share one budget. The proposed fix passes the remaining budget from the journal into the driver as a `retries_left` argument.

Registry record declined-box-000041-605fce3c already decided this request: the driver takes the full `caps.retry` per stage run while the drain draws retries separately, and the proposed fix is a journal-derived `retries_left` argument. Record tombstone-box-000135-077801c3 also links to it. This message asks for the same thing in different words.

- declined-box-000041-605fce3c: the driver gives every stage run the full `caps.retry` in-stage re-prompts while the drain draws retries separately, and the note asks to pass the journal-derived remaining budget as `retries_left`
- tombstone-box-000135-077801c3 links the same one-budget section 11.1 concern to declined-box-000041-605fce3c

Message: box-000213-3bd066d7
