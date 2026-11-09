---
id: declined-box-000191-050e38bf
kind: declined
link: box-000191-050e38bf
reopen_after_days: 90
---
The note says the seed-path requisition review in Check builds its LLM effect key with the run sequence in both the `run_seq` slot and the `attempt` slot. If seed Check ran again within one run sequence, it would replay the earlier attempt's review verdict. The note asks to fill the `attempt` slot with the real attempt number.

The seed path this note describes no longer exists. Merged ticket `remove-seeding` removed the seeding lane, including seed review during Check. `Invoice.seeds` is kept only so older `checks.json` files can still be read. Current engine code calls requisition review only from author (`chupa/author.py`), rework (`chupa/rework.py`), and the runner/stages provider-failure paths, and none of these is a seed Check. Record declined-box-000187 already declined the related request to document the seed-path key shape, because no wrong replay had been seen. No reachable runtime path produces the replay this note describes.

- Merged stems include `remove-seeding`, and decision declined-box-000190-cc65207a confirms it removed the seed lift and the path for seeds authored during Implement.
- chupa/stages.py:154 comment: 'Historical checks.json files contain seed reviews; retro and triage parse them through Invoice.' Seed reviews are kept only so old files can be read.
- Grep for `requisition_review` in chupa/ finds no seed-Check caller. Only author.py, rework.py (key prefix `llm/<stem>/<attempt>/requisition_review/<attempt>/`), runner.py:184 and stages.py:1579 (provider-failure handling) use it.
- declined-box-000187-b982a3cc already declined pinning the seed-path requisition_review key shape because no wrong replay had been seen.

Message: box-000191-050e38bf
