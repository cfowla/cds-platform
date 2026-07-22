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

- Days 1–40 are complete.
- **Day 40 — Implement an in-memory repository** is complete.
- Current sequential task: **Day 41 — Implement a YAML repository**.

## Current state

- `docs/RENAL_DOSE_CONTENT_SCHEMA.md` remains the normative version 1 YAML contract.
- `src/cds/repositories/renal_content_schema.py` continues to validate YAML text or parsed mappings
  without file I/O, normalization, repair, or typed conversion.
- `src/cds/repositories/renal_content.py` defines immutable, typed renal-dose content objects for
  exact quantities, intervals, medication and regimen facts, supported context, renal bands,
  recommendations, evidence sources, review metadata, and the complete versioned document.
- `RenalDoseContentKey` represents the exact case-sensitive
  `(medication_id, regimen_id, content_version)` repository key. It performs no aliasing, trimming,
  case folding, fallback, or version selection.
- `RenalDoseContentRepository` remains the runtime-checkable exact-key repository protocol.
- `InMemoryRenalDoseContentRepository` now copies supplied typed documents into private exact-key
  storage, rejects every duplicate key with `ValueError`, and returns the original document object
  only for the exact requested key.
- Missing keys, including case, whitespace, regimen, medication, and version mismatches, raise the
  existing `ContentNotFound` exception without fallback or automatic version selection.
- The in-memory repository performs no file access, YAML parsing, schema validation, typed mapping,
  clinical validation, review-eligibility filtering, rule matching, or mutation of supplied content.
- No YAML repository, file-to-model mapper, version-selection policy, matcher, rule, recommendation
  behavior, or package-level public re-export was added.

## Verification

- Focused collection completed successfully:
  `PYTHONPATH=src python -m pytest tests/unit/repositories/test_renal_content.py --collect-only -q`
- Result: `13 tests collected in 0.02s`.
- Focused command completed successfully:
  `PYTHONPATH=src python -m pytest tests/unit/repositories/test_renal_content.py -q`
- Result: `13 passed in 0.06s`.
- `python -m compileall -q src/cds/repositories/renal_content.py tests/unit/repositories/test_renal_content.py`
  completed successfully.
- Ruff was not installed in the bounded environment, so no lint passing claim is made.
- No full-suite, type-check, CI, or GitHub Actions passing claim is made.

## Additional files inspected

- `AGENTS.md` — required for repository workflow, bounded-checkout, architecture, verification, and
  close rules.
- `docs/SAFETY_INVARIANTS.md` — required to preserve the exact-key repository boundary and fail-closed
  content behavior.
- `src/cds/domain/exceptions.py` — directly imported by the repository module and required to preserve
  the existing `ContentNotFound` contract.
- `src/cds/repositories/__init__.py`, `src/cds/domain/__init__.py`, and `src/cds/__init__.py` — required
  ancestor package files for the bounded verification checkout; none were changed.
- `pyproject.toml` — required to confirm the declared pytest configuration and development dependency;
  it was not changed.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Structural and task-sufficiency validation must complete before calculation or rule matching.
- Missing, invalid, unsupported, ambiguous, unstable, and out-of-scope clinical facts fail closed
  without a dosing recommendation.
- Exact medication, regimen, and content-version keys are matched without aliases, normalization,
  fuzzy matching, interpolation, extrapolation, fallback, or automatic version selection.
- Duplicate exact repository keys are rejected rather than overwritten.
- Content defects prevent a document from becoming usable and are not silently repaired.
- Clinical decimal values and units remain explicit; renal-band matching will use the stored
  unquantized value.
- Draft or retired content is never eligible for rule matching.
- Clinical scope, supported medications and populations, renal method, safety behavior, intended
  users, interfaces, public domain contracts, and serialization behavior remain unchanged.

## Blockers

- The schema validator still returns a validated mapping because schema-to-model conversion belongs
  to the YAML repository or a directly bounded mapper used by it.
- No YAML-backed repository exists; runtime content retrieval currently requires callers or tests to
  supply already typed `RenalDoseContent` documents.
- Medication-specific authoritative source selection, final supported variants, reviewed renal
  bands, and reviewer identity remain deliberately deferred.

## Next exact action

> Day 41 — implement a YAML-backed `RenalDoseContentRepository` that performs file access, YAML
> parsing, version 1 schema validation, and explicit validated-mapping-to-typed-content conversion
> only inside the repository boundary, while preserving exact-key lookup and fail-closed errors.
