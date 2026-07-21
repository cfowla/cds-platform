# Safety Invariants

This file is the concise safety checklist for ordinary implementation work. [`PROJECT_CHARTER.md`](../PROJECT_CHARTER.md) remains the authoritative source for project scope, safety constraints, and change control. When this summary and the charter differ, follow the charter.

## Non-negotiable rules

1. **Prototype outputs are not clinical instructions.** Preserve the warning that the project is for research, education, and software development only and is not for direct clinical use.
2. **Use synthetic or properly de-identified data only.** Do not commit protected health information or real patient identifiers to code, fixtures, logs, issues, pull requests, screenshots, or examples.
3. **Validate before calculating or matching rules.** Structural validity, units, ranges, timestamps, task sufficiency, population, medication, and regimen support must be checked first.
4. **Never fabricate missing clinical values.** Represent an unknown numeric value as `None`, never as zero or another placeholder that could be interpreted as observed data.
5. **Never convert an ambiguous unit.** Reject or return an incomplete result when a required unit is missing, unrecognized, or insufficiently specified.
6. **Do not silently infer clinical context.** Do not infer a body-weight method, indication, regimen, formulation, route, frequency, infusion strategy, renal stability, or other required fact.
7. **Insufficient or unsupported cases fail closed.** Missing critical data, unsupported populations or regimens, unstable renal function, renal replacement therapy, absent content, or ambiguous rule matches must produce no dosing recommendation.
8. **Stay inside explicitly chartered scope.** Do not extrapolate to unsupported medications, populations, renal methods, clinical domains, or delivery interfaces without a separately approved scope change.
9. **Make every permitted assumption explicit.** Attach assumptions and warnings to the structured result and preserve where they were introduced.
10. **Keep clinical content inspectable and versioned.** Store rules separately from calculation logic with identifiers, boundaries, citations, source dates or versions, content versions, review metadata, and limitations.
11. **Detect content defects rather than resolving them silently.** Missing, overlapping, contradictory, or unreachable rule ranges must produce validation or system errors.
12. **Keep calculators and rule evaluators pure and deterministic.** Use typed input and output, with no network calls, direct file reads, hidden mutable state, or interface logic.
13. **Access content through a repository boundary.** Services must not load YAML, files, databases, or external APIs directly.
14. **Preserve auditability.** Results must retain the inputs and units used, equation and implementation version, selected weight and type, unrounded calculation result, matched rule and content version, rationale, assumptions, warnings, evidence, provenance, and evaluation time as applicable.
15. **Test safety boundaries, not only successful cases.** Cover missing, invalid, contradictory, unsupported, and immediately-below/at/immediately-above boundary cases, including proof that unsupported cases return no recommendation.

## When to reopen the full charter

Read [`PROJECT_CHARTER.md`](../PROJECT_CHARTER.md) before changing medication coverage, population, renal method, clinical setting, data source, user-facing interface, intended user, non-goals, safety behavior, or clinical-content requirements.
