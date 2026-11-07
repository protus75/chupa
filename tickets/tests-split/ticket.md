---
state: confirmed
source: human
priority: P2
kind: chore
gate_bypass:
  - code: diff_budget
    reason: one-time mechanical move of every test module into tests/unit and tests/integration, approved by the operator
---

## Depends on
- testguard
- source-graph-ast
- covgate
- covgate-runs-tests
- testreport
- flake-check
- flake-edit-coverage
- test-rules-prompt
- merge-skip-unchanged
- implement-test-rules
- review-all-findings
- core-authoring-rule
- ticket-review-command
- drop-plan-citations-1
- drop-plan-citations-2
- drop-plan-citations-3
- plan-off-serve-path
- remove-bootstrap-ingest
- remove-phase-exits
- remove-plan-gap-hardening
- remove-plan-grammar
- remove-plan-text-tests
- remove-seeding

## Context
- pyproject.toml
- docs/how-chupa-works.md

## Goal / Why
Unit and integration tests must be physically separate, so either suite can run alone and the unit suite can run under `chupa.testguard` with coverage. Today `tests/` is one flat directory of `test_*.py` modules. After this change every test module lives in `tests/unit/` or `tests/integration/`, classified mechanically:
- A module is a unit module only if it requests no `tmp_path`, `tmp_path_factory` or `tmpdir` fixture, and every test in it passes when run alone under `-p chupa.testguard`. The guard blocks processes and network, and the fixture rule keeps disk IO out.
- Every other module is an integration module.

Every open ticket naming a `tests/` path is a dependency, because moving the files would break those tickets' paths. This ticket runs after them all.

## Scope in / Scope out
- In: classify every `tests/test_*.py` by the rule above, then `git mv` it to `tests/unit/` or `tests/integration/`.
  - To classify a module, run `uv run pytest <module> -p chupa.testguard -n 0 -q`. The module is unit only if this exits 0 and the module source never names `tmp_path`, `tmp_path_factory` or `tmpdir`.
  - `tests/waiting.py` and `tests/regress_*.py` stay in `tests/`: they are shared helpers and carried bug reproducers that tickets reference by path.
- In: update every `from tests.test_<name> import` and `import tests.test_<name>` in `tests/` to the module's new package path (`tests.unit.test_<name>` or `tests.integration.test_<name>`). This includes `tests/waiting.py` and `tests/regress_*.py`, which stay in place.
- In: one mechanical location fix per moved module.
  - Repo-root anchors computed from `__file__` (`Path(__file__).resolve().parents[1]`, `.parent.parent`) gain one level (`parents[2]`).
  - Sibling-file reads point at the file's new location. Examples: `tests/test_merge.py` reading `test_stages.py` next to itself, and `tests/test_specs.py` reading `tests/test_specs.py` and `tests/test_plan_lint.py`.
  - Find them with `grep -n __file__` and by reading for `tests/test_` path strings.
- In: `pyproject.toml`: the ruff per-file ignore key `"tests/test_hostfiles.py"` becomes `"tests/**/test_hostfiles.py"`, so it still matches after the move.
- In: `docs/how-chupa-works.md` section 2.2: tests live in `tests/unit/` (no disk, network or process; run under `chupa.testguard`) and `tests/integration/`. Run one suite with `./dev.py test tests/unit` or `./dev.py test tests/integration`.
- Out:
  - rewriting any test, beyond its import paths, to make it unit-clean (converting integration tests to fakes is later work);
  - every other `pyproject.toml` setting (`testpaths = ["tests"]` still collects both suites);
  - chupa's `config.yaml` checks (ticket `chupa-test-gates`);
  - moving `tests/waiting.py` and `tests/regress_*.py` (their imports are updated like any other module's).

## Scope fence
- tests
- pyproject.toml
- docs/how-chupa-works.md

## Acceptance criteria
1. No `test_*.py` remains directly in `tests/`: `uv run python -c "import pathlib,sys; sys.exit(any(pathlib.Path('tests').glob('test_*.py')))"` exits 0.
2. The unit suite is guard-clean. `uv run pytest tests/unit -p chupa.testguard -q` exits 0. A unit module that spawns a process or opens a connection fails this command.
3. No unit module touches disk through pytest's temp fixtures. `uv run python -c "import pathlib,re,sys; sys.exit(any(re.search(r'\b(tmp_path|tmp_path_factory|tmpdir)\b', p.read_text()) for p in pathlib.Path('tests/unit').glob('*.py')))"` exits 0.
4. Nothing is lost. The multiset of test function names under `tests/` equals that at the merge base with `main`, checked by the Verification command starting `uv run python -c "import ast,subprocess`. It fails if a test function was dropped, renamed or duplicated.
5. No import of the old flat module paths remains, including in `tests/regress_*.py` and `tests/waiting.py`. Checked by the Verification command starting `uv run python -c "import ast,pathlib,sys; sys.exit(any(isinstance(n,ast.ImportFrom)`.
6. `./dev.py test` exits 0.
7. `docs/how-chupa-works.md` section 2.2 names `tests/unit/` and `tests/integration/`.
8. `pyproject.toml`'s ruff per-file ignores name `tests/**/test_hostfiles.py` and no longer name `tests/test_hostfiles.py`.

## Verification
```
uv run python -c "import pathlib,sys; sys.exit(any(pathlib.Path('tests').glob('test_*.py')))"
uv run pytest tests/unit -p chupa.testguard -q
uv run python -c "import pathlib,re,sys; sys.exit(any(re.search(r'\b(tmp_path|tmp_path_factory|tmpdir)\b', p.read_text()) for p in pathlib.Path('tests/unit').glob('*.py')))"
uv run python -c "import ast,subprocess,pathlib,collections as c;b=subprocess.run(['git','merge-base','HEAD','main'],capture_output=True,text=True,check=True).stdout.strip();names=lambda src:[n.name for n in ast.walk(ast.parse(src)) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name.startswith('test')];old=c.Counter(x for f in subprocess.run(['git','ls-tree','-r','--name-only',b,'tests/'],capture_output=True,text=True,check=True).stdout.split() if pathlib.PurePath(f).name.startswith('test_') and f.endswith('.py') for x in names(subprocess.run(['git','show',b+':'+f],capture_output=True,text=True,check=True).stdout));new=c.Counter(x for p in pathlib.Path('tests').rglob('test_*.py') for x in names(p.read_text()));assert old==new,(old-new,new-old)"
uv run python -c "import ast,pathlib,sys; sys.exit(any(isinstance(n,ast.ImportFrom) and (n.module or '').startswith('tests.test_') for p in pathlib.Path('tests').rglob('*.py') for n in ast.walk(ast.parse(p.read_text()))))"
./dev.py test
uv run python -c "import tomllib; i = tomllib.load(open('pyproject.toml', 'rb'))['tool']['ruff']['lint']['per-file-ignores']; assert 'tests/**/test_hostfiles.py' in i and 'tests/test_hostfiles.py' not in i"
```

## Definition of rejected
A test's assertions or logic change beyond import paths and file-location anchors; a module that fails the classification rule is placed in `tests/unit/`; a test is deleted or skipped; `tests/waiting.py` or `tests/regress_*.py` move.

## Time budget
- expected: 60m
- stuck: 150m
