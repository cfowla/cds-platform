"""Closed-schema validation for version 1 renal-dose YAML content.

This module validates repository content before any typed content model, rule matcher, or
service can use it. It accepts YAML text or an already parsed Python object, performs no file I/O,
and never normalizes identifiers, units, or clinical decimal strings.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
import re
from typing import Any, Final
from urllib.parse import urlparse

import yaml

from cds.domain.exceptions import ValidationError

__all__ = [
    "ContentSchemaError",
    "load_renal_dose_content_yaml",
    "validate_renal_dose_content",
]

_IDENTIFIER_RE: Final = re.compile(r"^[a-z][a-z0-9_]*$")
_DECIMAL_RE: Final = re.compile(r"^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$")
_DATE_RE: Final = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_PLACEHOLDER_RE: Final = re.compile(r"<[^>]+>")

_SUPPORTED_MEDICATION_IDS: Final = {
    "cefepime",
    "piperacillin_tazobactam",
    "famotidine",
}
_SUPPORTED_DOSE_UNITS: Final = {"mg", "g"}
_SUPPORTED_TIME_UNITS: Final = {"hours", "minutes"}
_SUPPORTED_ACTIONS: Final = {
    "continue",
    "adjust_dose",
    "hold",
    "stop",
    "avoid",
    "monitor",
    "switch",
    "clarify",
    "none",
}
_SUPPORTED_EVIDENCE_LEVELS: Final = {
    "guideline",
    "primary_literature",
    "local_policy",
    "expert_opinion",
}
_SUPPORTED_REVIEW_STATUSES: Final = {"draft", "reviewed", "retired"}


class ContentSchemaError(ValidationError):
    """Raised when renal-dose content violates the normative version 1 schema."""

    def __init__(self, path: str, message: str) -> None:
        self.path = path
        self.message = message
        super().__init__(f"{path}: {message}")


class _UniqueKeySafeLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys instead of overwriting them."""


def _construct_unique_mapping(
    loader: _UniqueKeySafeLoader,
    node: yaml.nodes.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            already_present = key in mapping
        except TypeError as exc:
            raise ContentSchemaError("$", "mapping keys must be hashable scalar values") from exc
        if already_present:
            raise ContentSchemaError("$", f"duplicate YAML mapping key {key!r}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def load_renal_dose_content_yaml(yaml_text: str) -> dict[str, Any]:
    """Parse one YAML document and return it only after complete schema validation."""

    if not isinstance(yaml_text, str):
        raise ContentSchemaError("$", "YAML input must be text")
    try:
        document = yaml.load(yaml_text, Loader=_UniqueKeySafeLoader)
    except ContentSchemaError:
        raise
    except yaml.YAMLError as exc:
        raise ContentSchemaError("$", f"invalid YAML: {exc}") from exc
    return validate_renal_dose_content(document)


def validate_renal_dose_content(document: object) -> dict[str, Any]:
    """Validate a parsed renal-dose content document without mutating or normalizing it."""

    root = _closed_mapping(
        document,
        "$",
        (
            "schema_version",
            "content_id",
            "content_version",
            "rule_id",
            "medication",
            "regimen",
            "supported_context",
            "renal_domain",
            "renal_bands",
            "sources",
            "review",
            "limitations",
        ),
    )

    schema_version = _nonempty_string(root["schema_version"], "$.schema_version")
    if schema_version != "1":
        _fail("$.schema_version", 'must be exactly "1"')

    content_id = _identifier(root["content_id"], "$.content_id")
    _nonempty_string(root["content_version"], "$.content_version")
    _identifier(root["rule_id"], "$.rule_id")

    medication_id = _validate_medication(root["medication"])
    regimen = _validate_regimen(root["regimen"])
    expected_content_id = f"renal_dose_{medication_id}_{regimen['id']}"
    if content_id != expected_content_id:
        _fail("$.content_id", f"must equal {expected_content_id!r}")

    _validate_supported_context(root["supported_context"])
    renal_domain = _interval(root["renal_domain"], "$.renal_domain")
    source_references = _validate_bands(root["renal_bands"], renal_domain, regimen)
    source_ids = _validate_sources(root["sources"])
    unresolved = sorted(source_references - source_ids)
    if unresolved:
        _fail("$.renal_bands", f"contains unresolved source_ids: {', '.join(unresolved)}")

    _validate_review(root["review"], root["content_version"])
    _string_list(root["limitations"], "$.limitations", minimum=1)
    return root


def _validate_medication(value: object) -> str:
    medication = _closed_mapping(value, "$.medication", ("id", "display"))
    medication_id = _identifier(medication["id"], "$.medication.id")
    if medication_id not in _SUPPORTED_MEDICATION_IDS:
        _fail("$.medication.id", "is not a supported first-slice medication identifier")
    _nonempty_string(medication["display"], "$.medication.display")
    return medication_id


def _validate_regimen(value: object) -> dict[str, Any]:
    regimen = _closed_mapping(
        value,
        "$.regimen",
        (
            "id",
            "display",
            "indication_ids",
            "route_id",
            "formulation_id",
            "base_dose",
            "frequency_interval",
            "infusion_duration",
        ),
    )
    _identifier(regimen["id"], "$.regimen.id")
    _nonempty_string(regimen["display"], "$.regimen.display")
    _identifier_list(regimen["indication_ids"], "$.regimen.indication_ids", minimum=1)
    _identifier(regimen["route_id"], "$.regimen.route_id")
    _nullable_identifier(regimen["formulation_id"], "$.regimen.formulation_id")
    _quantity(regimen["base_dose"], "$.regimen.base_dose", unit_kind="dose", positive=True)
    _quantity(
        regimen["frequency_interval"],
        "$.regimen.frequency_interval",
        unit_kind="time",
        positive=True,
    )
    if regimen["infusion_duration"] is not None:
        _quantity(
            regimen["infusion_duration"],
            "$.regimen.infusion_duration",
            unit_kind="time",
            positive=True,
        )
    return regimen


def _validate_supported_context(value: object) -> None:
    context = _closed_mapping(
        value,
        "$.supported_context",
        (
            "minimum_age_years",
            "renal_method",
            "renal_unit",
            "renal_function_stable",
            "renal_replacement_therapy",
            "limitations",
        ),
    )
    if type(context["minimum_age_years"]) is not int or context["minimum_age_years"] != 18:
        _fail("$.supported_context.minimum_age_years", "must be the YAML integer 18")
    if context["renal_method"] != "cockcroft_gault":
        _fail("$.supported_context.renal_method", 'must be exactly "cockcroft_gault"')
    if context["renal_unit"] != "mL/min":
        _fail("$.supported_context.renal_unit", 'must be exactly "mL/min"')
    if context["renal_function_stable"] is not True:
        _fail("$.supported_context.renal_function_stable", "must be true")
    if context["renal_replacement_therapy"] is not False:
        _fail("$.supported_context.renal_replacement_therapy", "must be false")
    _string_list(context["limitations"], "$.supported_context.limitations", minimum=1)


def _validate_bands(
    value: object,
    renal_domain: tuple[tuple[Decimal, bool] | None, tuple[Decimal, bool] | None],
    regimen: dict[str, Any],
) -> set[str]:
    bands = _list(value, "$.renal_bands", minimum=1)
    parsed: list[
        tuple[tuple[Decimal, bool] | None, tuple[Decimal, bool] | None]
    ] = []
    band_ids: set[str] = set()
    source_references: set[str] = set()

    for index, raw_band in enumerate(bands):
        path = f"$.renal_bands[{index}]"
        band = _closed_mapping(
            raw_band,
            path,
            (
                "id",
                "lower",
                "upper",
                "outcome",
                "recommendation",
                "no_recommendation_reason",
                "source_ids",
                "limitations",
            ),
        )
        band_id = _identifier(band["id"], f"{path}.id")
        if band_id in band_ids:
            _fail(f"{path}.id", f"duplicate band identifier {band_id!r}")
        band_ids.add(band_id)

        interval = _interval_parts(band["lower"], band["upper"], path)
        parsed.append(interval)
        _validate_outcome(band, path, regimen)
        source_ids = _identifier_list(band["source_ids"], f"{path}.source_ids", minimum=1)
        source_references.update(source_ids)
        _string_list(band["limitations"], f"{path}.limitations", minimum=0)

    if parsed[0][0] != renal_domain[0]:
        _fail("$.renal_bands[0].lower", "must exactly reproduce renal_domain.lower")
    if parsed[-1][1] != renal_domain[1]:
        _fail(
            f"$.renal_bands[{len(parsed) - 1}].upper",
            "must exactly reproduce renal_domain.upper",
        )

    for index in range(1, len(parsed)):
        previous_upper = parsed[index - 1][1]
        current_lower = parsed[index][0]
        path = f"$.renal_bands[{index}].lower"
        if previous_upper is None or current_lower is None:
            _fail(path, "only the domain edges may be unbounded")
        previous_value, previous_inclusive = previous_upper
        current_value, current_inclusive = current_lower
        if previous_value < current_value:
            _fail(path, "creates a gap after the previous renal band")
        if previous_value > current_value:
            _fail(path, "overlaps or is unsorted relative to the previous renal band")
        if previous_inclusive == current_inclusive:
            ownership = "included by both" if previous_inclusive else "excluded by both"
            _fail(path, f"shared boundary is {ownership} adjacent bands")

    return source_references


def _validate_outcome(band: dict[str, Any], path: str, regimen: dict[str, Any]) -> None:
    outcome = _nonempty_string(band["outcome"], f"{path}.outcome")
    if outcome == "recommendation":
        if band["recommendation"] is None:
            _fail(f"{path}.recommendation", "is required for recommendation outcome")
        if band["no_recommendation_reason"] is not None:
            _fail(
                f"{path}.no_recommendation_reason",
                "must be null for recommendation outcome",
            )
        _validate_recommendation(band["recommendation"], f"{path}.recommendation", regimen)
        return
    if outcome == "no_recommendation":
        if band["recommendation"] is not None:
            _fail(f"{path}.recommendation", "must be null for no_recommendation outcome")
        _nonempty_string(
            band["no_recommendation_reason"],
            f"{path}.no_recommendation_reason",
        )
        return
    _fail(f"{path}.outcome", 'must be "recommendation" or "no_recommendation"')


def _validate_recommendation(value: object, path: str, regimen: dict[str, Any]) -> None:
    recommendation = _closed_mapping(
        value,
        path,
        (
            "action",
            "dose",
            "route_id",
            "frequency_interval",
            "infusion_duration",
            "rationale",
            "monitoring",
        ),
    )
    action = _nonempty_string(recommendation["action"], f"{path}.action")
    if action not in _SUPPORTED_ACTIONS:
        _fail(f"{path}.action", "is not an implemented recommendation action")

    requires_regimen = action in {"continue", "adjust_dose"}
    if requires_regimen:
        dose = _quantity(recommendation["dose"], f"{path}.dose", unit_kind="dose", positive=True)
        route_id = _identifier(recommendation["route_id"], f"{path}.route_id")
        interval = _quantity(
            recommendation["frequency_interval"],
            f"{path}.frequency_interval",
            unit_kind="time",
            positive=True,
        )
        if dose[1] != regimen["base_dose"]["unit"]:
            _fail(f"{path}.dose.unit", "must use the exact base-dose unit")
        if route_id != regimen["route_id"]:
            _fail(f"{path}.route_id", "must match regimen.route_id exactly")
        if interval[1] != regimen["frequency_interval"]["unit"]:
            _fail(f"{path}.frequency_interval.unit", "must use the exact regimen interval unit")
        if regimen["infusion_duration"] is not None:
            infusion = _quantity(
                recommendation["infusion_duration"],
                f"{path}.infusion_duration",
                unit_kind="time",
                positive=True,
            )
            if infusion[1] != regimen["infusion_duration"]["unit"]:
                _fail(
                    f"{path}.infusion_duration.unit",
                    "must use the exact regimen infusion-duration unit",
                )
        elif recommendation["infusion_duration"] is not None:
            _quantity(
                recommendation["infusion_duration"],
                f"{path}.infusion_duration",
                unit_kind="time",
                positive=True,
            )
    else:
        _nullable_quantity(recommendation["dose"], f"{path}.dose", "dose")
        _nullable_identifier(recommendation["route_id"], f"{path}.route_id")
        _nullable_quantity(
            recommendation["frequency_interval"],
            f"{path}.frequency_interval",
            "time",
        )
        _nullable_quantity(
            recommendation["infusion_duration"],
            f"{path}.infusion_duration",
            "time",
        )

    _nonempty_string(recommendation["rationale"], f"{path}.rationale")
    _string_list(recommendation["monitoring"], f"{path}.monitoring", minimum=0)


def _validate_sources(value: object) -> set[str]:
    sources = _list(value, "$.sources", minimum=1)
    source_ids: set[str] = set()
    for index, raw_source in enumerate(sources):
        path = f"$.sources[{index}]"
        source = _closed_mapping(
            raw_source,
            path,
            (
                "id",
                "evidence_level",
                "citation",
                "source_document",
                "source_version",
                "publication_date",
                "url",
            ),
        )
        source_id = _identifier(source["id"], f"{path}.id")
        if source_id in source_ids:
            _fail(f"{path}.id", f"duplicate source identifier {source_id!r}")
        source_ids.add(source_id)

        evidence_level = _nonempty_string(source["evidence_level"], f"{path}.evidence_level")
        if evidence_level not in _SUPPORTED_EVIDENCE_LEVELS:
            _fail(f"{path}.evidence_level", "is not a supported evidence level")
        _nonempty_string(source["citation"], f"{path}.citation")
        _nonempty_string(source["source_document"], f"{path}.source_document")
        _nonempty_string(source["source_version"], f"{path}.source_version")
        _nullable_date_string(source["publication_date"], f"{path}.publication_date")
        _nullable_https_url(source["url"], f"{path}.url")
    return source_ids


def _validate_review(value: object, content_version: object) -> None:
    review = _closed_mapping(
        value,
        "$.review",
        (
            "status",
            "reviewed_content_version",
            "reviewer",
            "reviewer_role",
            "reviewed_on",
            "notes",
        ),
    )
    status = _nonempty_string(review["status"], "$.review.status")
    if status not in _SUPPORTED_REVIEW_STATUSES:
        _fail("$.review.status", "must be draft, reviewed, or retired")
    _nullable_nonempty_string(review["notes"], "$.review.notes")

    metadata = (
        review["reviewed_content_version"],
        review["reviewer"],
        review["reviewer_role"],
        review["reviewed_on"],
    )
    if status == "draft":
        if any(item is not None for item in metadata):
            _fail("$.review", "draft content must have null reviewer and reviewed-version fields")
        return

    if status == "reviewed":
        _complete_review_metadata(review, content_version)
        return

    if all(item is None for item in metadata):
        return
    if any(item is None for item in metadata):
        _fail("$.review", "retired review metadata must be either complete or entirely null")
    _complete_review_metadata(review, content_version)


def _complete_review_metadata(review: dict[str, Any], content_version: object) -> None:
    reviewed_version = _nonempty_string(
        review["reviewed_content_version"],
        "$.review.reviewed_content_version",
    )
    if reviewed_version != content_version:
        _fail(
            "$.review.reviewed_content_version",
            "must exactly equal the document content_version",
        )
    _nonempty_string(review["reviewer"], "$.review.reviewer")
    _nonempty_string(review["reviewer_role"], "$.review.reviewer_role")
    _date_string(review["reviewed_on"], "$.review.reviewed_on")


def _closed_mapping(value: object, path: str, required_keys: tuple[str, ...]) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail(path, "must be a mapping")
    non_string_keys = [key for key in value if not isinstance(key, str)]
    if non_string_keys:
        _fail(path, "mapping keys must be strings")
    missing = [key for key in required_keys if key not in value]
    if missing:
        _fail(path, f"missing required key(s): {', '.join(missing)}")
    unknown = sorted(set(value) - set(required_keys))
    if unknown:
        _fail(path, f"unknown key(s): {', '.join(unknown)}")
    return value


def _list(value: object, path: str, minimum: int) -> list[Any]:
    if not isinstance(value, list):
        _fail(path, "must be a list")
    if len(value) < minimum:
        _fail(path, f"must contain at least {minimum} item(s)")
    return value


def _nonempty_string(value: object, path: str) -> str:
    if not isinstance(value, str):
        _fail(path, "must be a string")
    if not value.strip():
        _fail(path, "must not be empty")
    if _PLACEHOLDER_RE.search(value):
        _fail(path, "must not contain an angle-bracket placeholder")
    return value


def _nullable_nonempty_string(value: object, path: str) -> str | None:
    if value is None:
        return None
    return _nonempty_string(value, path)


def _identifier(value: object, path: str) -> str:
    text = _nonempty_string(value, path)
    if not _IDENTIFIER_RE.fullmatch(text):
        _fail(path, "must match ^[a-z][a-z0-9_]*$")
    return text


def _nullable_identifier(value: object, path: str) -> str | None:
    if value is None:
        return None
    return _identifier(value, path)


def _identifier_list(value: object, path: str, minimum: int) -> list[str]:
    items = _list(value, path, minimum)
    identifiers: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(items):
        identifier = _identifier(item, f"{path}[{index}]")
        if identifier in seen:
            _fail(f"{path}[{index}]", f"duplicate identifier {identifier!r}")
        seen.add(identifier)
        identifiers.append(identifier)
    return identifiers


def _string_list(value: object, path: str, minimum: int) -> list[str]:
    items = _list(value, path, minimum)
    return [_nonempty_string(item, f"{path}[{index}]") for index, item in enumerate(items)]


def _decimal_string(value: object, path: str) -> Decimal:
    if not isinstance(value, str):
        _fail(path, "must be a quoted decimal string")
    if not _DECIMAL_RE.fullmatch(value):
        _fail(path, "has invalid decimal syntax")
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ContentSchemaError(path, "has invalid decimal syntax") from exc


def _quantity(
    value: object,
    path: str,
    *,
    unit_kind: str,
    positive: bool,
) -> tuple[Decimal, str]:
    quantity = _closed_mapping(value, path, ("value", "unit"))
    decimal_value = _decimal_string(quantity["value"], f"{path}.value")
    if positive and decimal_value <= 0:
        _fail(f"{path}.value", "must be greater than zero")
    unit = _nonempty_string(quantity["unit"], f"{path}.unit")
    allowed_units = _SUPPORTED_DOSE_UNITS if unit_kind == "dose" else _SUPPORTED_TIME_UNITS
    if unit not in allowed_units:
        _fail(f"{path}.unit", f"unsupported {unit_kind} unit {unit!r}")
    return decimal_value, unit


def _nullable_quantity(value: object, path: str, unit_kind: str) -> None:
    if value is None:
        return
    _quantity(value, path, unit_kind=unit_kind, positive=True)


def _endpoint(value: object, path: str) -> tuple[Decimal, bool] | None:
    if value is None:
        return None
    endpoint = _closed_mapping(value, path, ("value", "inclusive"))
    decimal_value = _decimal_string(endpoint["value"], f"{path}.value")
    if type(endpoint["inclusive"]) is not bool:
        _fail(f"{path}.inclusive", "must be a boolean")
    return decimal_value, endpoint["inclusive"]


def _interval(
    value: object,
    path: str,
) -> tuple[tuple[Decimal, bool] | None, tuple[Decimal, bool] | None]:
    interval = _closed_mapping(value, path, ("lower", "upper"))
    return _interval_parts(interval["lower"], interval["upper"], path)


def _interval_parts(
    lower_value: object,
    upper_value: object,
    path: str,
) -> tuple[tuple[Decimal, bool] | None, tuple[Decimal, bool] | None]:
    lower = _endpoint(lower_value, f"{path}.lower")
    upper = _endpoint(upper_value, f"{path}.upper")
    if lower is not None and upper is not None:
        if lower[0] > upper[0]:
            _fail(path, "interval lower boundary exceeds upper boundary")
        if lower[0] == upper[0] and not (lower[1] and upper[1]):
            _fail(path, "interval is empty or unreachable")
    return lower, upper


def _date_string(value: object, path: str) -> str:
    text = _nonempty_string(value, path)
    if not _DATE_RE.fullmatch(text):
        _fail(path, "must be a quoted ISO 8601 YYYY-MM-DD date")
    try:
        date.fromisoformat(text)
    except ValueError as exc:
        raise ContentSchemaError(path, "must be a valid calendar date") from exc
    return text


def _nullable_date_string(value: object, path: str) -> str | None:
    if value is None:
        return None
    return _date_string(value, path)


def _nullable_https_url(value: object, path: str) -> str | None:
    if value is None:
        return None
    text = _nonempty_string(value, path)
    parsed = urlparse(text)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        _fail(path, "must be an absolute HTTPS URL")
    return text


def _fail(path: str, message: str) -> None:
    raise ContentSchemaError(path, message)
