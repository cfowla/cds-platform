# Current Work

This file is replaced after every task. It is not an append-only diary.

## Repository execution mode

Use the repository checkout supplied by the execution environment. If no checkout is available,
use the GitHub connector to materialize only the named files and concretely required imports in a
bounded verification checkout.

GitHub is the authoritative source and destination for repository files.

Prohibited unless explicitly requested:
- repository cloning or filesystem searches for another checkout
- GitHub Actions or CI investigation
- workflow creation or modification
- web search
- PR creation, management, or merge
- broad repository review
- substitute functional test runners

Use only the named files and task-specified commands. Do not install missing test dependencies.

## Roadmap position

- Days 1–39 are complete.
- **Day 39 — Implement the content repository interface** is complete.
- Current sequential task: **Day 40 — Implement an in-memory repository**.

## Current state

- `docs/RENAL_DOSE_CONTENT_SCHEMA.md` remains the normative version 1 YAML contract.
- `src/cds/repositories/renal_content_schema.py` continues to validate YAML text or parsed mappings
  without file I/O, normalization, repair, or typed conversion.
- `src/cds/repositories/renal_content.py` now defines immutable, typed renal-dose content objects for
  exact quantities, intervals, medication and regimen facts, supported context, renal bands,
  recommendations, evidence sources, review metadata, and the complete versioned document.
- `RenalDoseContentKey` represents the exact case-sensitive
  `(medication_id, regimen_id, content_version)` repository key. It performs no aliasing, trimming,
  case folding, fallback, or version selection.
- `RenalDoseContentRepository` is a runtime-checkable protocol whose `get(key)` operation returns one
  typed `RenalDoseContent` document or raises the existing `ContentNotFound` exception when the exact
  key is absent.
- Review state remains explicit. Draft and retired content are representable but the interface does
  not assign rule-matching eligibility or current-version policy.
- No in-memory repository, YAML repository, file access, schema-to-model mapper, version-selection
  policy, matcher, rule, recommendation behavior, or package-level public re-export was added.

## Verification

- Focused collection completed successfully:
  `PYTHONPATH=src python -m pytest tests/unit/repositories/test_renal_content.py --collect-only -q`
- Result: `9 tests collected in 0.02s`.
- Focused command completed successfully:
  `PYTHONPATH=src python -m pytest tests/unit/repositories/test_renal_content.py -q`
- Result: `9 passed in 0.04s`.
- `python -m compileall -q src/cds/repositories/renal_content.py tests/unit/repositories/test_renal_content.py`
  completed successfully.
- No full-suite, lint, type-check, CI, or GitHub Actions passing claim is made.

## Additional files inspected

- `AGENTS.md` — required for repository workflow, bounded-checkout, architecture, and close rules.
- `docs/RENAL_DOSE_CONTENT_SCHEMA.md` — required to mirror the exact version 1 typed content shape and
  lookup-key contract without adding clinical values or policy.
- `src/cds/repositories/renal_content_schema.py` — required to preserve the existing validator and
  avoid duplicating schema validation or YAML parsing in the interface task.
- `src/cds/domain/exceptions.py` — required to use the existing `ContentNotFound` contract.
- `src/cds/domain/enums.py` and `src/cds/domain/outputs.py` — inspected to preserve existing renal and
  recommendation wire values without changing public domain contracts.
- `src/cds/repositories/__init__.py`, `src/cds/domain/__init__.py`, and `src/cds/__init__.py` —
  inspected to preserve package boundaries in the bounded verification checkout.
- `tests/unit/repositories/test_renal_content_schema.py` — inspected only for focused repository-test
  conventions and synthetic-fixture style.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Structural and task-sufficiency validation must complete before calculation or rule matching.
- Missing, invalid, unsupported, ambiguous, unstable, and out-of-scope clinical facts fail closed
  without a dosing recommendation.
- Exact medication, regimen, and content-version keys are matched without aliases, normalization,
  fuzzy matching, interpolation, extrapolation, fallback, or automatic version selection.
- Content defects prevent a document from becoming usable and are not silently repaired.
- Clinical decimal values and units remain explicit; renal-band matching will use the stored
  unquantized value.
- Draft or retired content is never eligible for rule matching.
- Clinical scope, supported medications and populations, renal method, safety behavior, intended
  users, interfaces, public domain contracts, and serialization behavior remain unchanged.

## Blockers

- The schema validator still returns a validated mapping because schema-to-model conversion belongs
  to a later YAML repository or mapper task.
- No concrete repository implementation exists yet; consumers cannot retrieve stored content until
  the in-memory repository is implemented.
- Medication-specific authoritative source selection, final supported variants, reviewed renal
  bands, and reviewer identity remain deliberately deferred.

## Next exact action

> Day 40 — implement a deterministic in-memory `RenalDoseContentRepository` keyed only by exact
> `RenalDoseContentKey` values, rejecting duplicate keys and raising `ContentNotFound` for every
> absent case without aliases, fallback, file access, or version-selection policy.
