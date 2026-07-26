"""Explicit application composition root contracts."""

from __future__ import annotations

from dataclasses import dataclass

from cds.app.features import FeatureDefinition, FeatureRegistry

__all__ = ["ApplicationComposition", "compose_application"]


@dataclass(frozen=True, slots=True, kw_only=True)
class ApplicationComposition:
    """Carry assembled feature definitions without constructing dependencies in interfaces."""

    features: FeatureRegistry


def compose_application(*, features: tuple[FeatureDefinition, ...]) -> ApplicationComposition:
    """Assemble an application from explicit preconfigured feature dependencies.

    This initial composition root deliberately performs no file discovery, environment lookup,
    implicit content selection, or clinical registration. Feature-specific factories may be added
    later while interfaces continue to depend only on the returned composition.
    """

    return ApplicationComposition(features=FeatureRegistry(features))
