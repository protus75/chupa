---
id: tombstone-box-000340-d8203fea
kind: tombstone
link: chupa-ruff-config
reopen_after_days: 14
---
The report says `uv run ruff check .` is red on main again (38 findings, mostly E501 in tests/ and chupa/stats.py) after the ruff cleanup tickets, and that nothing keeps it clean, so a ticket cannot list ruff in its Verification. The cleanup half repeats open ticket chupa-ruff-config, whose acceptance criteria already require `uv run ruff check .` and `uv run ruff format --check .` to exit 0, with any findings added by later merges fixed by hand across the whole Python tree. The 'no check keeps it clean' half is wrong: config.yaml already declares hard `trigger: always` host checks for both commands and ruff autofix steps.

The repair this message asks for, making whole-repo ruff exit 0 on main, is the stated goal of chupa-ruff-config. That ticket's Scope in tells it to fix findings that later merges add anywhere under chupa/, eval/ and tests/, which covers the new E501s. Registry record tombstone-box-000338-98ba883a already sent the same 'whole-repo ruff red on base' report to that stem. The proposed guard against regressions already exists: config.yaml:46-47 runs `ruff check .` and `ruff format --check .` as hard, always-triggered mechanical checks, and lines 32-33 run ruff fix and format as autofix. Whatever lets new findings through those checks, such as base-red attribution, would be a separate finding that needs its own evidence. This message does not supply that evidence.

- Open ticket chupa-ruff-config: acceptance criteria 1-2 require `uv run ruff check .` and `uv run ruff format --check .` to exit 0, and Scope in covers 'findings that later merges add anywhere under chupa/, eval/ and tests/'
- config.yaml:46-47 declares `lint` (`uv run ruff check .`) and `format` (`uv run ruff format --check .`) as `trigger: always, severity: hard` mechanical checks
- config.yaml:32-33 declares ruff-fix and ruff-format autofix steps on *.py
- Registry tombstone-box-000338-98ba883a already linked a whole-repo-ruff-red-on-base report to chupa-ruff-config
- Merged chupa-ruff-reclean* tickets show the regrowth pattern the open ticket's 'later merges' clause handles

Message: box-000340-d8203fea
