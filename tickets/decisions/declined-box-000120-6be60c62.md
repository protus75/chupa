---
id: declined-box-000120-6be60c62
kind: declined
link: box-000120-6be60c62
reopen_after_days: 90
---
`read_candidate` in `chupa/merge.py:208-209` reads `ticket.md` and `review.md` from the main checkout with `Path.read_text`. It does not go through the FileSystem seam. The note says this breaks the injectable-seams rule.

This is a seam-style preference and shows no wrong runtime behavior. The FileSystem seam in `chupa/seams.py` has only `write` and `replace` verbs, so it has no read verb these calls could use. Decision declined-box-000025-cf8cefbd already declined the same pattern for `load_config`: add a read verb only when a fake-driven test needs one. The real problem with these two reads is that they read the working tree instead of main's committed blobs. Decision declined-box-000119-08d6c51a already declined that. Moving the reads onto a seam would not change what merge reads or decides.

- chupa/merge.py:208 `ticket_text=(ctx.repo / ticket_path(stem)).read_text()`
- chupa/merge.py:209 `review_text=review_md.read_text() if review_md.is_file() else None`
- chupa/seams.py FileSystem defines only `write` (205) and `replace` (209); no read verb
- declined-box-000025-cf8cefbd declined the same raw-read-versus-seam pattern for config
- declined-box-000119-08d6c51a covers what these same reads read (working tree versus committed main)

Message: box-000120-6be60c62
