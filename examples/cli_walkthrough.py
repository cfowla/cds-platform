"""Reproducible synthetic CLI walkthrough scenarios for Day 70.

This harness exercises the dependency-injected interface only. Scenario results are canned,
synthetic snapshots and do not validate clinical content or dosing logic.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any, Sequence

from cds.interfaces.cli import main as cli_main

_SCENARIO_FILE = Path(__file__).with_name("cli_walkthrough_cases.json")


@dataclass(slots=True)
class _WalkthroughResult:
    validation: dict[str, Any]
    rule_result: dict[str, Any]


class _WalkthroughUseCase:
    def __init__(self, result: _WalkthroughResult) -> None:
        self._result = result
        self.call_count = 0

    def evaluate(self, **_: object) -> _WalkthroughResult:
        self.call_count += 1
        return self._result


def _load_payload() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    payload = json.loads(_SCENARIO_FILE.read_text(encoding="utf-8"))
    base_request = payload.get("base_request")
    scenarios = payload.get("scenarios")
    if not isinstance(base_request, dict) or not isinstance(scenarios, dict):
        raise ValueError(
            "Walkthrough scenario file must contain 'base_request' and 'scenarios' objects."
        )
    return base_request, scenarios


def _run_scenario(
    name: str,
    base_request: dict[str, Any],
    scenario: dict[str, Any],
    *,
    summary: bool,
    output_path: Path | None,
) -> tuple[int, str, str, int]:
    request = dict(base_request)
    request.update(scenario["request_overrides"])
    response = scenario["response"]
    use_case = _WalkthroughUseCase(
        _WalkthroughResult(
            validation=response["validation"],
            rule_result=response["rule_result"],
        )
    )
    stdout = StringIO()
    stderr = StringIO()

    with tempfile.TemporaryDirectory(prefix="cds-cli-walkthrough-") as temporary_directory:
        request_path = Path(temporary_directory) / f"{name}.json"
        request_path.write_text(
            json.dumps(request, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        argv = [str(request_path)]
        if output_path is not None:
            argv.extend(["--output", str(output_path)])
        if summary:
            argv.append("--summary")
        exit_code = cli_main(argv, use_case=use_case, stdout=stdout, stderr=stderr)

    canonical_output = (
        output_path.read_text(encoding="utf-8")
        if output_path is not None and output_path.exists()
        else stdout.getvalue()
    )
    return exit_code, canonical_output, stderr.getvalue(), use_case.call_count


def _verify(
    base_request: dict[str, Any],
    scenarios: dict[str, dict[str, Any]],
) -> int:
    failures: list[str] = []
    for name, scenario in scenarios.items():
        exit_code, canonical_output, stderr, call_count = _run_scenario(
            name,
            base_request,
            scenario,
            summary=False,
            output_path=None,
        )
        expected_output = json.dumps(
            scenario["response"],
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        if exit_code != scenario["expected_exit"]:
            failures.append(
                f"{name}: exit {exit_code}, expected {scenario['expected_exit']}"
            )
        if canonical_output != f"{expected_output}\n":
            failures.append(f"{name}: canonical output did not match the saved snapshot")
        if call_count != 1:
            failures.append(f"{name}: configured use case was called {call_count} times")
        for text in scenario["stderr_contains"]:
            if text not in stderr:
                failures.append(f"{name}: stderr did not contain {text!r}")
        recommendations = scenario["response"]["rule_result"].get("recommendations", [])
        if name in {"incomplete", "unsupported", "content_failure", "system_failure"}:
            if recommendations:
                failures.append(f"{name}: fail-closed scenario contained a recommendation")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1

    print(f"{len(scenarios)} synthetic CLI walkthrough scenarios verified.")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run saved synthetic renal-dose CLI interface walkthroughs. "
            "Canned results are not clinical validation."
        )
    )
    parser.add_argument("scenario", nargs="?", help="Saved walkthrough scenario name.")
    parser.add_argument("--verify", action="store_true", help="Verify every saved snapshot.")
    parser.add_argument("--summary", action="store_true", help="Request the CLI summary.")
    parser.add_argument("--output", type=Path, help="Write canonical JSON to this path.")
    arguments = parser.parse_args(argv)

    base_request, scenarios = _load_payload()
    if arguments.verify:
        if arguments.scenario or arguments.output or arguments.summary:
            parser.error("--verify cannot be combined with a scenario, --output, or --summary")
        return _verify(base_request, scenarios)

    if arguments.scenario not in scenarios:
        parser.error("scenario must be one of: " + ", ".join(sorted(scenarios)))

    exit_code, canonical_output, stderr, _ = _run_scenario(
        arguments.scenario,
        base_request,
        scenarios[arguments.scenario],
        summary=arguments.summary,
        output_path=arguments.output,
    )
    if arguments.output is None:
        sys.stdout.write(canonical_output)
    sys.stderr.write(stderr)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
