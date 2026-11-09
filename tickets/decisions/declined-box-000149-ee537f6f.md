---
id: declined-box-000149-ee537f6f
kind: declined
link: box-000149-ee537f6f
reopen_after_days: 90
---
A bootstrap note warned that the drain's self-upgrade re-exec ran a fixed `drain --parked ...` command. A parent started with `--config <path>` would then hand off to a child on the default config, which could use a different state dir and lock. It asked for section 18 to say whether the handoff carries `--config`, or for the handoff to be refused from a non-default config. Current code already passes `--config` to the child.

The gap no longer exists. `chupa/__main__.py:491` builds the drain handoff argv as `["--config", str(args.config)]` when the parent got `--config`, followed by `drain`. `chupa/drain.py:298-299` appends the `--parked` stems to that argv for the re-exec. The child therefore runs on the same config, state dir and lock as the parent. The remaining request is a wording change to the frozen plan, and the plan is never edited.

- chupa/__main__.py:491 argv=(["--config", str(args.config)] if args.config else []) + ["drain"]
- chupa/drain.py:298-299 reexec.run(reexec_argv([*argv, *(--parked stems)...]))
- CHUPA_PLAN.md is a frozen design record and is never edited

Message: box-000149-ee537f6f
