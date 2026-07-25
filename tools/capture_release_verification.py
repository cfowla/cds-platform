#!/usr/bin/env python3
"""Capture complete, durable verification evidence for one exact CDS candidate.

Prototype only -- not for direct clinical use. Retained output must contain only
synthetic or properly de-identified data and requires manual PHI review before commit.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import os
from pathlib import Path
import platform
import subprocess
import sys
import tomllib
from typing import Mapping, Sequence


PROTOTYPE_WARNING = (
    "Prototype only -- not for direct clinical use. Use only synthetic or properly "
    "de-identified data."
)
CLI_SUCCESS_TEXT = "7 synthetic CLI walkthrough scenarios verified."
DEFAULT_DISPOSITIONS = Path("docs/RELEASE_TEST_DISPOSITIONS.md")


@dataclass(frozen=True, slots=True)
class Command:
    """One command and its exact evidence-display form."""

    display: str
    arguments: tuple[str, ...]
    environment: Mapping[str, str] | None = None


@dataclass(frozen=True, slots=True)
class CommandResult:
    """Captured command output and timing."""

    exit_status: int
    output: str
    started_at: str
    completed_at: str


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _utc_filename_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _run_process(
    arguments: Sequence[str],
    *,
    cwd: Path,
    environment: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    merged_environment = os.environ.copy()
    if environment is not None:
        merged_environment.update(environment)
    return subprocess.run(
        list(arguments),
        cwd=cwd,
        env=merged_environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )


def _capture(command: Command, *, cwd: Path) -> CommandResult:
    started_at = _now()
    completed = _run_process(
        command.arguments,
        cwd=cwd,
        environment=command.environment,
    )
    return CommandResult(
        exit_status=completed.returncode,
        output=completed.stdout,
        started_at=started_at,
        completed_at=_now(),
    )


def _git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return _run_process(("git", *arguments), cwd=root)


def _git_value(root: Path, *arguments: str) -> str:
    completed = _git(root, *arguments)
    if completed.returncode != 0:
        detail = completed.stdout.strip() or "no diagnostic output"
        raise RuntimeError(f"git {' '.join(arguments)} failed: {detail}")
    return completed.stdout.strip()


def _write_command_evidence(handle, command: Command, result: CommandResult) -> None:
    handle.write(f"$ {command.display}\n")
    handle.write(f"Started: {result.started_at}\n")
    handle.write(result.output)
    if result.output and not result.output.endswith("\n"):
        handle.write("\n")
    if not result.output:
        handle.write("<no output>\n")
    handle.write(f"Completed: {result.completed_at}\n")
    handle.write(f"Exit status: {result.exit_status}\n\n")
    handle.flush()


def _environment_commands() -> tuple[Command, ...]:
    return (
        Command("git rev-parse HEAD", ("git", "rev-parse", "HEAD")),
        Command(
            "git status --short",
            ("git", "status", "--short", "--untracked-files=all"),
        ),
        Command("python --version", (sys.executable, "--version")),
        Command(
            "python -m pytest --version",
            (sys.executable, "-m", "pytest", "--version"),
        ),
        Command(
            "python -m ruff --version",
            (sys.executable, "-m", "ruff", "--version"),
        ),
    )


def _verification_commands() -> tuple[Command, ...]:
    return (
        Command(
            "python -m pytest -q",
            (sys.executable, "-m", "pytest", "-q"),
        ),
        Command(
            "python -m ruff check . --config pyproject.toml",
            (
                sys.executable,
                "-m",
                "ruff",
                "check",
                ".",
                "--config",
                "pyproject.toml",
            ),
        ),
        Command(
            "PYTHONPATH=src python examples/cli_walkthrough.py --verify",
            (sys.executable, "examples/cli_walkthrough.py", "--verify"),
            environment={"PYTHONPATH": "src"},
        ),
    )


def _parse_arguments(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture full verification evidence for one exact CDS prototype candidate."
    )
    parser.add_argument(
        "--release-custodian",
        required=True,
        help="Name and role of the release custodian responsible for this run.",
    )
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root or a path inside it. Defaults to the current directory.",
    )
    parser.add_argument(
        "--dispositions",
        type=Path,
        default=DEFAULT_DISPOSITIONS,
        help="Version-controlled skip/xfail/xpass disposition record.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Evidence file path. Defaults to a timestamped file under artifacts/verification.",
    )
    return parser.parse_args(argv)


def _resolve_inside(root: Path, path: Path) -> Path:
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def _package_version(root: Path) -> str:
    with (root / "pyproject.toml").open("rb") as pyproject:
        value = tomllib.load(pyproject).get("project", {}).get("version")
    return value if isinstance(value, str) and value else "<missing>"


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parse_arguments(argv)

    try:
        supplied_root = arguments.repository_root.resolve()
        root = Path(_git_value(supplied_root, "rev-parse", "--show-toplevel")).resolve()
        candidate_sha = _git_value(root, "rev-parse", "HEAD")
        candidate_ref = _git_value(root, "branch", "--show-current") or "<detached HEAD>"
    except RuntimeError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    initial_status = _git_value(root, "status", "--short", "--untracked-files=all")
    if initial_status:
        print(
            "ERROR: candidate verification requires a clean working tree before evidence "
            "generation.",
            file=sys.stderr,
        )
        print(initial_status, file=sys.stderr)
        return 2

    dispositions_path = _resolve_inside(root, arguments.dispositions)
    if not dispositions_path.is_file():
        print(
            f"ERROR: disposition record not found: {dispositions_path}",
            file=sys.stderr,
        )
        return 2

    output_path = (
        _resolve_inside(root, arguments.output)
        if arguments.output is not None
        else root
        / "artifacts"
        / "verification"
        / f"full-verification-{_utc_filename_stamp()}.txt"
    )
    if output_path.exists():
        print(f"ERROR: refusing to overwrite evidence: {output_path}", file=sys.stderr)
        return 2

    environment_results = tuple(
        (command, _capture(command, cwd=root)) for command in _environment_commands()
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    overall_success = all(
        result.exit_status == 0 for _, result in environment_results
    )
    cli_confirmed = False
    generated_at = _now()

    with output_path.open("x", encoding="utf-8") as evidence:
        evidence.write(f"{PROTOTYPE_WARNING}\n\n")
        evidence.write("===== CANDIDATE =====\n")
        evidence.write(f"Candidate commit: {candidate_sha}\n")
        evidence.write(f"Candidate reference: {candidate_ref}\n")
        evidence.write(f"Repository root: {root}\n")
        evidence.write(f"Package version: {_package_version(root)}\n")
        evidence.write(f"Python executable: {sys.executable}\n")
        evidence.write(f"Release custodian: {arguments.release_custodian}\n")
        evidence.write(f"Evidence generated at: {generated_at}\n")
        evidence.write(f"Operating system: {platform.platform()}\n")
        evidence.write(f"Architecture: {platform.machine()}\n")
        evidence.write("Pre-verification working tree: clean\n")
        evidence.write(f"Durable artifact location: {output_path}\n\n")

        evidence.write("===== MANUAL GATES =====\n")
        evidence.write(
            "PHI review: BLOCKING until a named reviewer confirms this artifact contains no "
            "PHI or real patient identifiers.\n"
        )
        evidence.write(
            "Independent calculation review: BLOCKING until completed for this exact candidate.\n"
        )
        evidence.write(
            "Qualified clinical-content review: BLOCKING until completed for every selected "
            "exact content version.\n"
        )
        evidence.write(
            "Release decision: BLOCKING; this evidence run does not record a go decision or "
            "authorize milestone tagging.\n\n"
        )

        evidence.write("===== ENVIRONMENT RECORD =====\n")
        for command, result in environment_results:
            _write_command_evidence(evidence, command, result)

        evidence.write("===== TEST DISPOSITIONS =====\n")
        evidence.write(f"Source: {dispositions_path}\n\n")
        disposition_text = dispositions_path.read_text(encoding="utf-8")
        evidence.write(disposition_text)
        if not disposition_text.endswith("\n"):
            evidence.write("\n")
        evidence.write("\n")
        evidence.flush()

        evidence.write("===== RELEASE VERIFICATION =====\n")
        for command in _verification_commands():
            result = _capture(command, cwd=root)
            _write_command_evidence(evidence, command, result)
            overall_success = overall_success and result.exit_status == 0
            if command.display.endswith("cli_walkthrough.py --verify"):
                cli_confirmed = CLI_SUCCESS_TEXT in result.output

        if not cli_confirmed:
            overall_success = False
            evidence.write(
                f"CLI confirmation: MISSING required text {CLI_SUCCESS_TEXT!r}\n\n"
            )
        else:
            evidence.write(f"CLI confirmation: {CLI_SUCCESS_TEXT}\n\n")

        final_sha = _git_value(root, "rev-parse", "HEAD")
        tracked_status = _git_value(root, "status", "--short", "--untracked-files=no")
        complete_status = _git_value(root, "status", "--short", "--untracked-files=all")
        try:
            relative_output = output_path.relative_to(root).as_posix()
        except ValueError:
            relative_output = None
        allowed_status = {f"?? {relative_output}"} if relative_output is not None else set()
        unexpected_status = {
            line for line in complete_status.splitlines() if line not in allowed_status
        }
        candidate_unchanged = (
            final_sha == candidate_sha and not tracked_status and not unexpected_status
        )
        overall_success = overall_success and candidate_unchanged

        evidence.write("===== POST-VERIFICATION STATE =====\n")
        evidence.write(f"Candidate commit after checks: {final_sha}\n")
        evidence.write(
            "Tracked candidate state: "
            + ("unchanged" if candidate_unchanged else "CHANGED -- verification invalid")
            + "\n"
        )
        evidence.write(
            "Unexpected generated files: "
            + ("none" if not unexpected_status else ", ".join(sorted(unexpected_status)))
            + "\n"
        )
        evidence.write("Complete working-tree status after evidence generation:\n")
        evidence.write(complete_status or "<clean>")
        evidence.write("\n")
        evidence.write(
            "Generated evidence is expected to be untracked after verification and is not part "
            "of the candidate. Review it for PHI and accuracy before committing it.\n"
        )
        evidence.write(f"Overall software verification: {'PASS' if overall_success else 'FAIL'}\n")

    print(f"Evidence written to {output_path}")
    return 0 if overall_success else 1


if __name__ == "__main__":
    raise SystemExit(main())
