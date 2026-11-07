---
id: declined-box-000039-af7f01a0
kind: declined
link: box-000039-af7f01a0
reopen_after_days: 180
---
A bootstrap note asked for a `prompt_path` field on `LLMRequest`, so the CLI adapter could learn where the driver spooled the prompt file it sends on stdin. The adapter now writes its own spool file, so the field is not needed.

The gap described is gone. The CLI adapter takes `req.rendered`, scrubs it, writes it to its own per-call `prompt.md` under its capture directory, and passes that path as `stdin_path` to the exec seam. No path has to travel from the driver through `LLMRequest`, and no wrong runtime behavior can be reached. What is left is a plan-wording point about the frozen bootstrap design, which is not a buildable gap.

- chupa/providers.py:314-317 builds call_dir/prompt.md and writes self._redactor.scrub(req.rendered) through the FileSystem seam
- chupa/providers.py:316 comment: the prompt reaches the CLI only as a file on stdin
- chupa/providers.py:324 passes stdin_path=prompt to self._exec.run
- chupa/seams.py:103-112 the exec seam opens stdin_path as the child's stdin
- chupa/llm.py:15 LLMRequest has no prompt_path field and needs none

Message: box-000039-af7f01a0
