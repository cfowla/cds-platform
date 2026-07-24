"""Verification for the saved Day 70 synthetic CLI walkthrough."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CASES = ROOT / "examples" / "cli_walkthrough_cases.json"
RUNNER = ROOT / "examples" / "cli_walkthrough.py"

_REQUIRED_SCENARIOS = {
    "cefepime",
    "piperacillin_tazobactam",
    "famotidine",
    "incomplete",
    "unsupported",
    "content_failure",
    "system_failure",
}
_FAIL_CLOSED_SCENARIOS = {
    "incomplete",
    "unsupported",
    "content_failure",
    "system_failure",
}


def test_saved_walkthrough_snapshots_verify() -> None:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT / "src")
    completed = subprocess.run(
        [sys.executable, str(RUNNER), "--verify"],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout == "7 synthetic CLI walkthrough scenarios verified.\n"


def test_walkthrough_covers_required_and_fail_closed_scenarios() -> None:
    payload = json.loads(CASES.read_text(encoding="utf-8"))
    scenarios = payload["scenarios"]

    assert set(scenarios) == _REQUIRED_SCENARIOS
    for name in _FAIL_CLOSED_SCENARIOS:
        result = scenarios[name]["response"]["rule_result"]
        assert scenarios[name]["expected_exit"] != 0
        assert result["recommendations"] == []
