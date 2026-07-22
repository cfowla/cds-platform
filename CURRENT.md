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

- Days 1–38 are complete.
- **Day 38 — Implement content schema validation** is complete.
- Current sequential task: **Day 39 — Implement the content repository interface**.

## Current state

- `docs/RENAL_DOSE_CONTENT_SCHEMA.md` remains the normative version 1 YAML contract.
- `src/cds/repositories/renal_content_schema.py` now provides a repository-layer YAML text loader
  and closed-schema validator with no direct file I/O.
- YAML parsing uses the declared `PyYAML>=6.0` runtime dependency and a safe loader that rejects
  duplicate mapping keys instead of silently overwriting them.
- The validator returns a document only after enforcing exact required and unknown-key behavior,
  scalar node types, identifiers, versions, quoted clinical decimals, exact supported units and
  context, renal-domain partition invariants, outcome consistency, source references, and review
  metadata.
- Content defects raise `ContentSchemaError`, a typed `ValidationError`, and prevent the document
  from becoming usable. Values are not normalized, converted, repaired, interpolated, or defaulted.
- `src/cds/content/renal/cefepime_synthetic_fixture.yaml` remains draft synthetic content and passes
  schema validation without becoming eligible for rule matching or patient-care use.
- No typed clinical-content model, repository interface, in-memory repository, file-backed YAML
  repository, version-selection policy, matcher, rule, recommendation behavior, or public import was
  added.

## Verification

- Focused command completed successfully:
  `PYTHONPATH=src python -m pytest tests/unit/repositories/test_renal_content_schema.py -q`
- Result: `55 passed in 0.33s`.
- `python -m compileall -q src/cds/repositories/renal_content_schema.py tests/unit/repositories/test_renal_content_schema.py`
  completed successfully.
- A direct fixture load completed successfully and reported the expected content ID and two renal
  bands.
- Ruff was unavailable in the supplied environment, so no lint passing claim is made.
- No full-suite, CI, or GitHub Actions passing claim is made.

## Additional files inspected

- `AGENTS.md` — required for repository workflow, bounded-checkout, architecture, and close rules.
- `BACKLOG.md` — inspected to confirm that schema invariants are resolved while medication-specific
  sources, identifiers, and clinical values remain deferred.
- `src/cds/domain/exceptions.py` — inspected because the validator uses the existing typed
  `ValidationError` contract.
- `src/cds/domain/enums.py` and `src/cds/domain/outputs.py` — inspected to confirm stable renal-method
  and recommendation-action wire values referenced by the schema.
- `tests/unit/validation/test_renal.py` — inspected only for the repository's focused pytest style.
- `src/cds/repositories/__init__.py`, `src/cds/content/__init__.py`, and `src/cds/__init__.py` —
  inspected to preserve existing package boundaries without adding public exports.
- `pyproject.toml` — inspected and edited to declare the YAML parser required by this task.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Structural and task-sufficiency validation must complete before calculation or rule matching.
- Missing, invalid, unsupported, ambiguous, unstable, and out-of-scope clinical facts fail closed
  without a dosing recommendation.
- Exact medication and regimen facts are matched without aliases, normalization, fuzzy matching,
  interpolation, extrapolation, or fallback.
- Content defects prevent a document from becoming usable and are not silently repaired.
- Clinical decimal values and units remain explicit; renal-band matching will use the stored
  unquantized value.
- Draft or retired content is never eligible for rule matching.
- Clinical scope, supported medications and populations, renal method, safety behavior, intended
  users, interfaces, public domain contracts, and serialization behavior remain unchanged.

## Blockers

- The validator currently returns a validated mapping because typed content objects and their
  repository interface are scheduled for subsequent tasks.
- Medication-specific authoritative source selection, final supported variants, reviewed renal
  bands, and reviewer identity remain deliberately deferred.

## Next exact action

> Day 39 — define the content repository interface that returns typed, versioned renal-dose content
> by the exact `(medication_id, regimen_id, content_version)` key without aliases, normalization,
> fallback, file access, or version-selection policy.
