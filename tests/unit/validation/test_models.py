"""Focused tests for passive validation models."""

from cds.validation.models import ValidationIssue, ValidationResult


def test_validation_issue_defaults_do_not_invent_a_finding() -> None:
    issue = ValidationIssue()

    assert issue.code is None
    assert issue.message is None
    assert issue.severity == "unknown"
    assert issue.field_path is None


def test_validation_result_defaults_remain_unevaluated() -> None:
    result = ValidationResult()

    assert result.is_valid is None
    assert result.issues == []


def test_validation_models_preserve_explicit_values() -> None:
    issue = ValidationIssue(
        code="missing_unit",
        message="A unit is required before calculation.",
        severity="error",
        field_path="serum_creatinine.unit",
    )
    result = ValidationResult(is_valid=False, issues=[issue])

    assert result.is_valid is False
    assert result.issues == [issue]
    assert result.issues[0] is issue


def test_validation_result_issue_lists_are_independent() -> None:
    first = ValidationResult()
    second = ValidationResult()

    first.issues.append(ValidationIssue(code="prototype_only", severity="warning"))

    assert len(first.issues) == 1
    assert second.issues == []
