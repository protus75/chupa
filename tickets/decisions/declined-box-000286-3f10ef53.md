---
id: declined-box-000286-3f10ef53
kind: declined
link: box-000286-3f10ef53
reopen_after_days: 90
---
`load_config` in `chupa/config.py` turns only `yaml.YAMLError` into `ConfigError` (lines 294-296). A malformed explicit tag such as `!!int abc` makes `yaml.safe_load` raise `ValueError`, which escapes as a traceback. `migrate_config` already catches `ValueError` (line 335), so the two loaders treat the same bad input differently.

The gap is real but not materially harmful. It only shows up when an operator hand-writes an explicit YAML type tag with a bad value, which is a rare and unusual config edit. Even then the load still fails closed: no config gets loaded, nothing runs, and the traceback names the bad value. The operator loses the formatted refusal text and gets exit 1 instead of exit 2. No run, drain or host has been reported failing this way. Registry record declined-box-000097-cd50f4c0 already declined the broader request to map unexpected engine exceptions to exit 2, and this is one narrow case of that.

- chupa/config.py:294-296: load_config wraps yaml.safe_load in `except yaml.YAMLError` only
- chupa/config.py:335: migrate_config catches `(ValueError, yaml.YAMLError)`, so the merged migrate-config ticket fixed this only for its own loader
- PyYAML's SafeConstructor builds `!!int` with int(), which raises ValueError on a bad value instead of YAMLError
- No incident, run record or operator report shows this input reached in practice; declined-box-000097-cd50f4c0 covers the general uncaught-exception-to-exit-code question

Message: box-000286-3f10ef53
