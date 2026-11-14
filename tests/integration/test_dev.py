from pathlib import Path
from unittest.mock import Mock

import pytest

import dev


def test_drain_forwards_detach(monkeypatch):
    monkeypatch.setattr(dev.sys, "argv", ["dev.py", "drain"])
    run = Mock(return_value=Mock(returncode=0))
    popen = Mock()
    monkeypatch.setattr(dev.subprocess, "run", run)
    monkeypatch.setattr(dev.subprocess, "Popen", popen)
    dev.main()
    run.assert_called_once_with(["uv", "run", "python", "-m", "chupa", "drain", "--detach"], cwd=dev.ROOT, check=False)
    popen.assert_not_called()


def test_publish_uploads_built_files(tmp_path, monkeypatch):
    monkeypatch.setattr(dev, "ROOT", tmp_path)
    monkeypatch.setattr(dev.sys, "argv", ["dev.py", "publish"])
    monkeypatch.setenv("UV_PUBLISH_TOKEN", "test-token")
    calls = []

    def fake_run(argv, *, cwd, check):
        calls.append((argv, cwd, check))
        if argv[:2] == ["uv", "build"]:
            directory = Path(argv[3])
            (directory / "chupa-0.1.1.whl").write_bytes(b"wheel")
            (directory / "chupa-0.1.1.tar.gz").write_bytes(b"sdist")
        return Mock(returncode=0)

    monkeypatch.setattr(dev.subprocess, "run", fake_run)
    dev.main()
    bump, build, publish = calls  # Extra calls, including git or a second bump, must fail.
    directory = Path(build[0][3])
    assert bump == (["uv", "version", "--bump", "patch"], tmp_path, False)  # The bump must precede the build.
    assert build == (["uv", "build", "-o", str(directory)], tmp_path, False)  # Build into the temporary directory.
    assert publish == (["uv", "publish", str(directory / "chupa-0.1.1.tar.gz"), str(directory / "chupa-0.1.1.whl")], tmp_path, False)  # Upload both actual artifacts.


def test_publish_refuses_without_token(monkeypatch):
    monkeypatch.setattr(dev.sys, "argv", ["dev.py", "publish"])
    monkeypatch.delenv("UV_PUBLISH_TOKEN", raising=False)
    run = Mock()
    monkeypatch.setattr(dev.subprocess, "run", run)

    with pytest.raises(SystemExit) as error:
        dev.main()
    assert "UV_PUBLISH_TOKEN" in str(error.value.code)  # A generic failure would not identify the missing credential.
    assert error.value.code != 0  # Refusal must not report success.
    run.assert_not_called()  # Refusal must happen before the bump or any other subprocess.


def test_suggest_forwards_summary(monkeypatch):
    monkeypatch.setattr(dev.sys, "argv", ["dev.py", "suggest", "an idea"])
    run = Mock()
    monkeypatch.setattr(dev, "run", run)
    dev.main()
    run.assert_called_once_with(["uv", "run", "python", "-m", "chupa", "suggest", "an idea"])


def test_core_forwards_once(monkeypatch):
    monkeypatch.setattr(dev.sys, "argv", ["dev.py", "core"])
    run = Mock()
    monkeypatch.setattr(dev, "run", run)
    dev.main()
    run.assert_called_once_with(["uv", "run", "python", "-m", "chupa", "core"])


def test_test_passes_leading_options_to_pytest(monkeypatch):
    monkeypatch.setattr(dev.sys, "argv", ["dev.py", "test", "--durations=25", "-k", "foo"])
    run = Mock(return_value=Mock(returncode=0))
    monkeypatch.setattr(dev.subprocess, "run", run)
    dev.main()
    run.assert_called_once_with(
        ["uv", "run", "pytest", "-q", "--durations=25", "-k", "foo"],
        cwd=dev.ROOT,
        check=False,
    )  # Leading options must reach pytest in their original order.

    monkeypatch.setattr(dev.sys, "argv", ["dev.py", "lint", "--bogus"])
    with pytest.raises(SystemExit) as error:
        dev.main()
    assert error.value.code == 2  # Other commands must still reject unknown options.


@pytest.mark.parametrize("verb", ["triage", "dismiss"])
def test_box_verbs_forward_all_ids_once(monkeypatch, verb):
    monkeypatch.setattr(dev.sys, "argv", ["dev.py", verb, "box-one", "box-two"])
    call = Mock()
    monkeypatch.setattr(dev, "chupa", call)
    dev.main()
    call.assert_called_once_with(verb, "box-one", "box-two")  # One pass must receive both IDs.


@pytest.fixture
def vscode_package(tmp_path, monkeypatch):
    extension = tmp_path / "vscode-chupa"
    extension.mkdir()
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "9.8.7"\n')
    (extension / "README.md").write_text("# chupa tickets\n\nBuilt for [chupa 0.0.1](https://pypi.org/project/chupa/0.0.1/).\n\ntail\n")
    (extension / "package.json").write_text('{"version": "1.2.3"}')
    monkeypatch.setattr(dev, "ROOT", tmp_path)
    monkeypatch.setattr(dev.sys, "argv", ["dev.py", "vscode-package"])
    return tmp_path / "dist" / "vscode-chupa-1.2.3.vsix"


def test_vscode_package_prints_windows_path_under_wsl(vscode_package, monkeypatch, capsys):
    monkeypatch.setenv("WSL_DISTRO_NAME", "DifferentDistro")
    windows_path = r"\\wsl.localhost\Distro\repo\dist\vscode-chupa-1.2.3.vsix"
    run = Mock(side_effect=[Mock(returncode=0), Mock(returncode=0, stdout=f" {windows_path}\n")])
    monkeypatch.setattr(dev.subprocess, "run", run)

    dev.main()

    assert run.call_args_list[1] == ((["wslpath", "-w", str(vscode_package)],), {"capture_output": True, "text": True, "check": False})  # Translate the packaged VSIX, not another path.
    output = capsys.readouterr().out.splitlines()
    assert f"dev: upload {vscode_package} at https://marketplace.visualstudio.com/manage/publishers/chunkydragon" in output  # Keep the existing upload instruction.
    assert f"dev: Windows path {windows_path}" in output  # Print stripped wslpath output, not a path built from the distro.


def test_vscode_package_skips_wslpath_outside_wsl(vscode_package, monkeypatch, capsys):
    monkeypatch.delenv("WSL_DISTRO_NAME", raising=False)
    run = Mock(return_value=Mock(returncode=0))
    monkeypatch.setattr(dev.subprocess, "run", run)

    dev.main()

    run.assert_called_once_with(
        ["npx", "--yes", "@vscode/vsce", "package", "--no-dependencies", "-o", str(vscode_package)], cwd=dev.ROOT / "vscode-chupa", check=False
    )  # No translation subprocess outside WSL.
    assert "Windows path" not in capsys.readouterr().out  # Do not print a fabricated path outside WSL.


def test_vscode_package_stops_when_wslpath_fails(vscode_package, monkeypatch, capsys):
    monkeypatch.setenv("WSL_DISTRO_NAME", "Distro")
    run = Mock(side_effect=[Mock(returncode=0), Mock(returncode=1, stdout="failed output")])
    monkeypatch.setattr(dev.subprocess, "run", run)

    with pytest.raises(SystemExit) as error:
        dev.main()

    assert "wslpath" in str(error.value.code)  # Identify the failing translation command.
    assert "Windows path" not in capsys.readouterr().out  # Never print failed output as a path.
    assert run.call_args.args[0] == ["wslpath", "-w", str(vscode_package)]  # The failure must come from translating the packaged VSIX.


def test_vscode_package_stamps_chupa_version(vscode_package, monkeypatch, capsys):
    monkeypatch.delenv("WSL_DISTRO_NAME", raising=False)
    readme = dev.ROOT / "vscode-chupa" / "README.md"
    packaged = []

    def fake_run(argv, *, cwd, check):
        if argv[0] == "npx":
            packaged.append(readme.read_text())
        return Mock(returncode=0)

    monkeypatch.setattr(dev.subprocess, "run", fake_run)
    dev.main()
    expected = "# chupa tickets\n\nBuilt for [chupa 9.8.7](https://pypi.org/project/chupa/9.8.7/).\n\ntail\n"
    assert packaged == [expected]  # The package must see the engine version and intact surrounding text.
    assert readme.read_text() == expected  # The stamped README must remain for the operator.
    assert "dev: built for chupa 9.8.7" in capsys.readouterr().out  # Report the engine version, not the extension version.


def test_vscode_package_stops_without_built_for_line(vscode_package, monkeypatch):
    readme = dev.ROOT / "vscode-chupa" / "README.md"
    original = "# chupa tickets\n\ntail\n"
    readme.write_text(original)
    run = Mock()
    monkeypatch.setattr(dev.subprocess, "run", run)
    with pytest.raises(SystemExit) as error:
        dev.main()
    assert str(error.value.code).startswith("dev:") and "Built for" in str(error.value.code)  # Explain the missing marker.
    run.assert_not_called()  # Do not package without a version marker.
    assert readme.read_text() == original  # Do not silently append a marker.


def test_docs_forwards(monkeypatch):
    monkeypatch.setattr(dev.sys, "argv", ["dev.py", "docs"])
    run = Mock()
    monkeypatch.setattr(dev, "run", run)
    dev.main()
    run.assert_called_once_with(["uv", "run", "python", "-m", "chupa", "docs"])


def test_probe_forwards(monkeypatch):
    monkeypatch.setattr(dev.sys, "argv", ["dev.py", "probe", "qwen"])
    run = Mock()
    monkeypatch.setattr(dev, "run", run)
    dev.main()
    run.assert_called_once_with(["uv", "run", "python", "-m", "chupa", "probe", "qwen"])


def test_prompt_forwards_once(monkeypatch):
    monkeypatch.setattr(dev.sys, "argv", ["dev.py", "prompt", "drafts"])
    run = Mock()
    monkeypatch.setattr(dev, "run", run)
    dev.main()
    run.assert_called_once_with(["uv", "run", "python", "-m", "chupa", "prompt", "drafts"])  # No extra call or stem.
