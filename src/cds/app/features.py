"""Feature definitions and exact feature registry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from cds.app.results import EvaluationResult

__all__ = [
    "EvaluationUseCase",
    "EvaluationValidator",
    "FeatureDefinition",
    "FeatureRegistry",
]


class EvaluationUseCase(Protocol):
    """Evaluate one feature-specific request through an application-owned contract."""

    def evaluate(self, request: Any, /) -> EvaluationResult:
        ...


class EvaluationValidator(Protocol):
    """Validate one feature request before calculation or rule evaluation."""

    def validate(self, request: Any, /) -> Any:
        ...


@dataclass(frozen=True, slots=True, kw_only=True)
class FeatureDefinition:
    """Bind one exact feature identifier to its application dependencies."""

    feature_id: str
    validator: EvaluationValidator
    use_case: EvaluationUseCase
    rule_registry: Any
    content_repository: Any | None = None


class FeatureRegistry:
    """Store exact feature definitions without normalization, aliasing, or fallback."""

    def __init__(self, definitions: tuple[FeatureDefinition, ...] = ()) -> None:
        items: dict[str, FeatureDefinition] = {}
        for definition in definitions:
            if not definition.feature_id:
                raise ValueError("feature_id must be a nonempty exact value")
            if definition.feature_id in items:
                raise ValueError(f"duplicate feature registration {definition.feature_id!r}")
            items[definition.feature_id] = definition
        self._definitions: Mapping[str, FeatureDefinition] = items

    def get(self, feature_id: str, /) -> FeatureDefinition | None:
        """Return one exact feature definition or ``None`` without fallback."""

        return self._definitions.get(feature_id)

    def require(self, feature_id: str, /) -> FeatureDefinition:
        """Return one exact definition or raise a sanitized configuration error."""

        definition = self.get(feature_id)
        if definition is None:
            raise KeyError(f"unregistered feature identifier {feature_id!r}")
        return definition
