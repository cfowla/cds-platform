"""Stable string enums used by the CDS domain layer."""

from enum import StrEnum

__all__ = ["RenalMethod", "ResultStatus", "Sex", "WeightType"]


class Sex(StrEnum):
    """Sex value required by the configured renal calculation."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class ResultStatus(StrEnum):
    """Top-level outcome of a CDS evaluation."""

    SUCCESS = "success"
    SUCCESS_WITH_WARNINGS = "success_with_warnings"
    INCOMPLETE = "incomplete"
    NOT_APPLICABLE = "not_applicable"
    FAILED = "failed"


class RenalMethod(StrEnum):
    """Method used to calculate or measure renal function."""

    COCKCROFT_GAULT = "cockcroft_gault"
    CKD_EPI = "ckd_epi"
    MDRD = "mdrd"
    MEASURED_CRCL = "measured_crcl"
    UNKNOWN = "unknown"


class WeightType(StrEnum):
    """Declared body-weight type supplied to a calculation."""

    ACTUAL = "actual"
    IDEAL = "ideal"
    ADJUSTED = "adjusted"
    OTHER = "other"
    UNKNOWN = "unknown"
