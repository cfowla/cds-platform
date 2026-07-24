# Prototype Release Checklist

> **Prototype only — not for direct clinical use.** This checklist is for research, education,
> software development, and reproducible prototype review using synthetic or properly de-identified
> data. Completing it does not authorize diagnosis, prescribing, medication-order verification, or
> patient-care use.

## Purpose and release boundary

Use this checklist before creating a prototype milestone tag. It gathers evidence that one exact
software and clinical-content state has been reviewed and reproduced. It does not:

- change clinical-content review status;
- make draft or retired content eligible for a recommendation;
- select a content version automatically;
- resolve a known limitation or blocker;
- replace independent clinical review; or
- authorize production deployment or direct clinical use.

A release decision is **no-go** until every required item is complete and every unresolved blocker
has an explicit disposition. Unchecked, unknown, unavailable, or not-applicable evidence must not be
interpreted as passing.

## 1. Identify the exact candidate

- [ ] Record the repository commit SHA: `<commit-sha>`.
- [ ] Record the candidate branch or immutable reference: `<reference>`.
- [ ] Record the package version from `pyproject.toml`: `<package-version>`.
- [ ] Record the Python version used for verification: `<python-version>`.
- [ ] Record the operating system and architecture: `<environment>`.
- [ ] Record the verification date and timezone: `<timestamp-with-utc-offset>`.
- [ ] Record the release custodian: `<name-and-role>`.
- [ ] Confirm the working tree was clean before verification.
- [ ] Confirm no file changed between verification and the release decision.

Do not use a branch name, file order, directory order, or the word `latest` as a substitute for an
exact commit or content version.

## 2. Confirm the prototype safety boundary

- [ ] The repository and release notes retain the prototype-only warning.
- [ ] The warning states that outputs are not clinical instructions.
- [ ] The warning states that only synthetic or properly de-identified data may be used.
- [ ] The release notes do not imply clinical validation, production readiness, or patient-care use.
- [ ] The candidate remains limited to the frozen adult Cockcroft-Gault renal-dose slice.
- [ ] No unsupported medication, population, renal method, regimen, interface, or setting was added.
- [ ] Unsupported or insufficient cases remain fail-closed with no dosing recommendation.

## 3. Complete full software verification

Run the configured checks from the repository root in a complete development environment. Do not
install missing dependencies in a constrained verification environment merely to produce a passing
claim.

```bash
python -m pytest -q
python -m ruff check .
PYTHONPATH=src python examples/cli_walkthrough.py --verify
```

For each command, record:

- exact command;
- start and completion timestamp;
- Python and dependency environment;
- exit status;
- complete pass, fail, skip, and warning counts; and
- durable evidence location.

Required outcomes:

- [ ] The full pytest suite passes with no unexplained failures or collection errors.
- [ ] Every skip or expected failure is listed and accepted explicitly.
- [ ] Ruff completes successfully using the repository configuration.
- [ ] The CLI walkthrough reports `7 synthetic CLI walkthrough scenarios verified.`
- [ ] Unit, integration, contract, content, safety-failure, and logging tests are included.
- [ ] No test was weakened, deleted, or reclassified solely to obtain a passing result.
- [ ] No GitHub Actions or CI passing claim is made unless that workflow actually ran.

Verification record:

- Pytest: `<result-and-evidence>`
- Ruff: `<result-and-evidence>`
- CLI walkthrough: `<result-and-evidence>`
- Accepted skips or limitations: `<details-or-none>`

## 4. Complete independent calculation review

The reviewer must independently evaluate the exact calculator implementation at the candidate
commit. Running the production calculator against its own expected values is not independent review.

- [ ] Reviewer name and role are recorded: `<name-and-role>`.
- [ ] The reviewer is independent of the implementation under review.
- [ ] The exact candidate commit and calculator implementation version are recorded.
- [ ] The equation matches `docs/RENAL_CALCULATOR_SPEC.md` exactly.
- [ ] Male and female cases are independently recalculated without calling the production service.
- [ ] The female coefficient is applied only to `Sex.FEMALE` in the specified operation order.
- [ ] Arithmetic uses the documented 28-digit local Decimal context and `ROUND_HALF_EVEN`.
- [ ] No serum-creatinine floor, cap, substitution, interpolation, or hidden correction is present.
- [ ] Exact units remain `kg`, `mg/dL`, and unindexed `mL/min`.
- [ ] The supplied weight and declared weight type are used unchanged after validation.
- [ ] Stored creatinine clearance remains unquantized for rule matching.
- [ ] Immediately below, at, and immediately above a synthetic boundary remain distinguishable.
- [ ] Reproducibility metadata and explicit times are retained.
- [ ] The reviewer records approval, requested changes, or rejection.

Independent calculation review record:

- Candidate commit: `<commit-sha>`
- Reviewer: `<name-and-role>`
- Review date: `<date>`
- Method and evidence: `<location>`
- Outcome: `<approved-requested-changes-rejected>`
- Limitations: `<details-or-none>`

The existing arithmetic record in `docs/RENAL_CALCULATOR_VERIFICATION.md` is supporting evidence. It
does not by itself prove independent human review or clinical validity.

## 5. Confirm clinical-content review status

Complete this section separately for every medication, regimen, and content version selected for the
candidate. A software test cannot substitute for independent clinical-content review.

### Cefepime

- Medication identifier: `<exact-id>`
- Regimen identifier: `<exact-id>`
- Content version: `<exact-version>`
- Rule identifier: `<exact-id>`
- Review status: `<draft-reviewed-retired>`
- Reviewer name and role: `<name-and-role>`
- Review date: `<date>`
- Reviewed content version: `<exact-version>`
- Source versions and citations: `<evidence-location>`
- [ ] Status is exactly `reviewed`.
- [ ] Reviewer metadata is complete and refers to the exact content version.
- [ ] Source-to-band traceability and limitations were independently checked.
- [ ] Boundary and golden cases were independently checked.

### Piperacillin-tazobactam

- Medication identifier: `<exact-id>`
- Regimen identifier: `<exact-id>`
- Content version: `<exact-version>`
- Rule identifier: `<exact-id>`
- Review status: `<draft-reviewed-retired>`
- Reviewer name and role: `<name-and-role>`
- Review date: `<date>`
- Reviewed content version: `<exact-version>`
- Source versions and citations: `<evidence-location>`
- [ ] Status is exactly `reviewed`.
- [ ] Reviewer metadata is complete and refers to the exact content version.
- [ ] Source-to-band traceability and limitations were independently checked.
- [ ] Boundary and golden cases were independently checked.

### Famotidine

- Medication identifier: `<exact-id>`
- Regimen identifier: `<exact-id>`
- Content version: `<exact-version>`
- Rule identifier: `<exact-id>`
- Review status: `<draft-reviewed-retired>`
- Reviewer name and role: `<name-and-role>`
- Review date: `<date>`
- Reviewed content version: `<exact-version>`
- Source versions and citations: `<evidence-location>`
- [ ] Status is exactly `reviewed`.
- [ ] Reviewer metadata is complete and refers to the exact content version.
- [ ] Source-to-band traceability and limitations were independently checked.
- [ ] Boundary and golden cases were independently checked.

Global content checks:

- [ ] Every selected version is requested explicitly by exact identifier.
- [ ] No draft or retired content can produce a recommendation.
- [ ] Schema validation rejects missing, unknown, duplicate, gapped, overlapping, contradictory, or
      unreachable content.
- [ ] Exactly one band owns each supported boundary.
- [ ] Every recommendation-bearing band cites declared source metadata.
- [ ] No source conflict, ambiguity, or unsupported extrapolation remains hidden.
- [ ] Supersession or rollback relationships are recorded outside the current schema when
      applicable.
- [ ] The selected content set has one durable release evidence record.

A missing qualified independent reviewer is a blocking no-go condition. Do not complete reviewer
fields with the content author, a software-only reviewer, a generic team name, or an automated
agent.

## 6. Verify fail-closed behavior and safety invariants

- [ ] Structural validation runs before calculation.
- [ ] Task-sufficiency validation runs before calculation or rule matching.
- [ ] Error-severity issues stop the workflow.
- [ ] Warnings cannot make insufficient input sufficient.
- [ ] Missing numerics remain `None`, never zero or another sentinel.
- [ ] Unknown categorical facts use explicit unknown states where defined.
- [ ] Ambiguous or unsupported units are not inferred, normalized, or converted.
- [ ] Unsupported sex, unstable renal function, renal replacement therapy, pregnancy, lactation, or
      out-of-scope population produces no recommendation.
- [ ] Exact medication, regimen, formulation, route, dose, frequency, indication, infusion, and
      content-version facts are required where applicable.
- [ ] Missing content, defective content, calculation errors, and unexpected system errors fail
      closed.
- [ ] Non-success results contain no dosing recommendation.
- [ ] Result status, `applied`, and `passed` retain their distinct documented meanings.
- [ ] Rule matching uses unrounded renal values.
- [ ] Calculators and rules remain pure and deterministic.
- [ ] Services do not read clinical-content files directly.

## 7. Confirm PHI and diagnostic controls

- [ ] Only synthetic or properly de-identified examples and fixtures are present.
- [ ] No real patient identifiers or clinical payloads appear in source, tests, examples, logs,
      screenshots, issues, pull requests, or release notes.
- [ ] Diagnostic helpers accept only controlled event fields.
- [ ] Logs omit patient identifiers, request and response payloads, arbitrary metadata, exception
      messages, exception arguments, and tracebacks.
- [ ] CLI diagnostics remain sanitized and do not expose patient details.
- [ ] Logging tests prove that synthetic identifiers and payload details are not disclosed.
- [ ] Any external release evidence was reviewed for PHI before retention or sharing.

Record the PHI review method, reviewer, date, scope, and evidence location:

`<phi-review-record>`

## 8. Confirm provenance and auditability

For each successful synthetic evaluation, verify that the structured result preserves, as
applicable:

- [ ] exact supplied patient, medication-order, and laboratory identifiers;
- [ ] exact input values and units;
- [ ] serum-creatinine collection time;
- [ ] evaluation date and timezone-aware evaluation or calculation time;
- [ ] derived age used by the equation;
- [ ] supplied weight, unit, and declared weight type;
- [ ] renal method and unrounded creatinine-clearance result;
- [ ] equation or implementation version;
- [ ] matched rule identifier and exact content version;
- [ ] rationale and monitoring information;
- [ ] assumptions and warnings;
- [ ] evidence and source versions; and
- [ ] provenance sufficient to reproduce the evaluation.

Canonical serialization must preserve Decimal strings, exact field names, enum wire values, UTC
normalization for aware datetimes, `None` as JSON `null`, and fixed response keys.

## 9. Capture release versions and evidence

- [ ] Repository commit SHA is immutable and recorded.
- [ ] Package version is recorded without implying semantic release maturity.
- [ ] Python and relevant dependency versions are recorded.
- [ ] Exact medication, regimen, content, rule, schema, and calculator versions are recorded.
- [ ] Source document names, dates, versions, and citations are recorded for each content version.
- [ ] Independent reviewer identities, roles, dates, and outcomes are recorded.
- [ ] Verification commands and results are retained in a durable change or release record.
- [ ] Any superseded or restored version is named explicitly.
- [ ] No version string was reused for materially different reviewed clinical content.
- [ ] The evidence record contains no PHI or real patient identifiers.

Release evidence location: `<durable-location>`

## 10. Revalidate current limitations and blockers

The following limitations are known at the time this checklist was created. Revalidate them against
the exact candidate rather than copying them forward as stale history.

- [ ] The CLI remains dependency-injected and has no standalone production composition root.
- [ ] No installed console-script entry point is declared.
- [ ] The walkthrough uses canned synthetic results and is not a clinical-content calculation run.
- [ ] No API, EHR, batch, streaming, persistence, or network interface is implemented or authorized.
- [ ] No automatic active-content-version registry exists.
- [ ] The content schema has no explicit supersession relationship.
- [ ] Conflicting supplied and declared body-weight type is not rejected before calculation.
- [ ] The famotidine adult minimum-weight boundary is not enforced in the full flow.
- [ ] Privacy-preserving logging helpers are not yet wired into every application or interface
      failure path.
- [ ] Any previously deferred focused pytest or full-repository verification has been rerun or
      remains an explicit blocker.
- [ ] Every additional candidate-specific limitation is documented below.

Additional limitations and dispositions:

`<limitation-disposition-record>`

A documented limitation is not automatically acceptable. The release custodian and appropriate
reviewers must explicitly classify each item as blocking, accepted for this nonclinical prototype,
or resolved with evidence.

## 11. Make the go or no-go decision

- [ ] Every required checklist item is complete.
- [ ] Every verification failure, skip, warning, and limitation has an explicit disposition.
- [ ] Independent calculation review is approved for the exact candidate.
- [ ] Independent clinical-content review is complete for every selected exact version.
- [ ] PHI controls and prototype warnings are confirmed.
- [ ] The release custodian confirms that no blocking item remains.

Decision: `<go-no-go>`

Candidate commit: `<commit-sha>`

Selected content versions: `<exact-versions>`

Decision maker and role: `<name-and-role>`

Decision timestamp with UTC offset: `<timestamp>`

Rationale and unresolved limitations: `<record>`

A `go` decision permits only creation of the named nonclinical prototype milestone described by this
record. It does not authorize direct clinical use, production deployment, or implicit selection of
any other software or content version.

## 12. Tagging handoff

Only after an explicit `go` decision:

1. Confirm the candidate commit still matches the verified commit.
2. Update the changelog or release record with the exact captured evidence.
3. Create the planned prototype tag on that exact commit.
4. Verify the tag resolves to the recorded commit.
5. Preserve the prototype warning and limitations in the release notes.
6. Do not modify content review metadata, code, tests, or documentation after verification without
   invalidating the decision and rerunning affected checks.

This section is a handoff to a separate bounded task. Creating or pushing a tag is outside the scope
of this checklist-creation task.
