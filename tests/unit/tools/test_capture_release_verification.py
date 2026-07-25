"""Focused tests for durable release-verification evidence capture."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "tools" / "capture_release_verification.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("capture_release_verification", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _completed(arguments, output: str = "", status: int = 0):
    return subprocess.CompletedProcess(arguments, status, stdout=output)


def _repository(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "repository"
    disposition = root / "docs" / "RELEASE_TEST_DISPOSITIONS.md"
    disposition.parent.mkdir(parents=True)
    disposition.write_text("# Dispositions\n\nNo placeholder skips remain.\n", encoding="utf-8")
    (root / "pyproject.toml").write_text("[project]\nversion = '0.1.0'\n", encoding="utf-8")
    return root, disposition


def _fake_runner(module, root: Path, *, pytest_status: int = 0, dirty: bool = False):
    calls: list[tuple[str, ...]] = []

    def run(arguments, *, cwd, environment=None):
        command = tuple(arguments)
        calls.append(command)
        assert cwd == root
        assert environment is None or environment == {"PYTHONPATH": "src"}

        if command == ("git", "rev-parse", "--show-toplevel"):
            return _completed(arguments, f"{root}\n")
        if command == ("git", "rev-parse", "HEAD"):
            return _completed(arguments, "0123456789abcdef\n")
        if command == ("git", "branch", "--show-current"):
            return _completed(arguments, "agent/work-package-6\n")
        if command == ("git", "status", "--short", "--untracked-files=no"):
            return _completed(arguments)
        if command == ("git", "status", "--short", "--untracked-files=all"):
            if dirty:
                return _completed(arguments, " M CURRENT.md\n")
            return _completed(arguments)
        if command == (sys.executable, "--version"):
            return _completed(arguments, "Python 3.12.0\n")
        if command == (sys.executable, "-m", "pytest", "--version"):
            return _completed(arguments, "pytest 8.4.0\n")
        if command == (sys.executable, "-m", "ruff", "--version"):
            return _completed(arguments, "ruff 0.12.0\n")
        if command == (sys.executable, "-m", "pytest", "-q"):
            return _completed(
                arguments,
                "2 passed, 2 xfailed in 0.10s\n",
                pytest_status,
            )
        if command[:4] == (sys.executable, "-m", "ruff", "check"):
            return _completed(arguments, "All checks passed!\n")
        if command == (sys.executable, "examples/cli_walkthrough.py", "--verify"):
            return _completed(arguments, f"{module.CLI_SUCCESS_TEXT}\n")
        raise AssertionError(f"Unexpected command: {command}")

    return run, calls


def test_successful_capture_records_complete_commands_and_manual_blockers(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    root, disposition = _repository(tmp_path)
    output = root / "artifacts" / "verification" / "evidence.txt"
    runner, calls = _fake_runner(module, root)
    monkeypatch.setattr(module, "_run_process", runner)

    exit_status = module.main(
        [
            "--release-custodian",
            "Synthetic Custodian, Software Review",
            "--repository-root",
            str(root),
            "--dispositions",
            str(disposition),
            "--output",
            str(output),
        ]
    )

    evidence = output.read_text(encoding="utf-8")
    assert exit_status == 0
    assert "$ python -m pytest -q\n" in evidence
    assert "$ python -m ruff check . --config pyproject.toml\n" in evidence
    assert "$ PYTHONPATH=src python examples/cli_walkthrough.py --verify\n" in evidence
    assert "2 passed, 2 xfailed in 0.10s" in evidence
    assert "Package version: 0.1.0" in evidence
    assert module.CLI_SUCCESS_TEXT in evidence
    assert "PHI review: BLOCKING" in evidence
    assert "Tracked candidate state: unchanged" in evidence
    assert "Overall software verification: PASS" in evidence
    assert (sys.executable, "-m", "pytest", "-q") in calls


def test_failed_check_is_retained_and_does_not_short_circuit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    root, disposition = _repository(tmp_path)
    output = root / "artifacts" / "verification" / "failed.txt"
    runner, calls = _fake_runner(module, root, pytest_status=1)
    monkeypatch.setattr(module, "_run_process", runner)

    exit_status = module.main(
        [
            "--release-custodian",
            "Synthetic Custodian, Software Review",
            "--repository-root",
            str(root),
            "--dispositions",
            str(disposition),
            "--output",
            str(output),
        ]
    )

    evidence = output.read_text(encoding="utf-8")
    assert exit_status == 1
    assert "Exit status: 1" in evidence
    assert "Overall software verification: FAIL" in evidence
    assert (sys.executable, "-m", "ruff", "check", ".", "--config", "pyproject.toml") in calls
    assert (sys.executable, "examples/cli_walkthrough.py", "--verify") in calls


def test_dirty_candidate_is_rejected_before_artifact_creation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = _load_module()
    root, disposition = _repository(tmp_path)
    output = root / "artifacts" / "verification" / "must-not-exist.txt"
    runner, _ = _fake_runner(module, root, dirty=True)
    monkeypatch.setattr(module, "_run_process", runner)

    exit_status = module.main(
        [
            "--release-custodian",
            "Synthetic Custodian, Software Review",
            "--repository-root",
            str(root),
            "--dispositions",
            str(disposition),
            "--output",
            str(output),
        ]
    )

    assert exit_status == 2
    assert not output.exists()
    assert "requires a clean working tree" in capsys.readouterr().err
