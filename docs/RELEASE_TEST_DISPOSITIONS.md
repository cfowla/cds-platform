# Release Test Dispositions

> **Prototype only — not for direct clinical use.** This record concerns software-test coverage
> only. It does not authorize patient-care use, accept a clinical limitation, complete independent
> review, or constitute a release decision.

## Placeholder skip inventory

The failed Day 83 evidence recorded 16 skipped placeholder modules. Each contained the same skipped
`test_placeholder` and asserted no behavior. The modules are removed because the intended behavior
is now exercised by the concrete tests listed below. Their removal is not counted as a passing test.

| Removed placeholder | Existing concrete coverage |
| --- | --- |
| `tests/contract/test_input_contract.py` | `tests/contract/test_renal_dose_interface_contracts.py`; `tests/unit/mappers/test_renal_dose_request.py` |
| `tests/contract/test_output_contract.py` | `tests/contract/test_domain_serialization_contracts.py`; `tests/contract/test_renal_dose_interface_contracts.py`; `tests/unit/mappers/test_renal_dose_response.py` |
| `tests/integration/test_application_flow.py` | `tests/integration/test_renal_dose_matrix.py`; `tests/integration/test_safety_failure_drill.py` |
| `tests/integration/test_renal_dosing_flow.py` | `tests/integration/test_cefepime_end_to_end.py`; `tests/integration/test_renal_dose_matrix.py`; `tests/integration/test_renal_safety_invariants.py` |
| `tests/unit/app/test_use_cases.py` | `tests/unit/app/test_renal_dose.py` |
| `tests/unit/content/test_content_schema.py` | `tests/unit/repositories/test_renal_content_schema.py`; `tests/unit/repositories/test_yaml_renal_content.py` |
| `tests/unit/domain/test_constants.py` | `tests/unit/domain/test_enums.py`; `tests/unit/domain/test_module_exports.py` |
| `tests/unit/mappers/test_input.py` | `tests/unit/mappers/test_renal_dose_request.py` |
| `tests/unit/mappers/test_output.py` | `tests/unit/mappers/test_renal_dose_response.py` |
| `tests/unit/repositories/test_content.py` | `tests/unit/repositories/test_renal_content.py`; medication-specific repository tests |
| `tests/unit/repositories/test_protocols.py` | `tests/unit/repositories/test_renal_content.py` |
| `tests/unit/utils/test_datetime.py` | `tests/unit/utils/test_serialization.py` |
| `tests/unit/utils/test_identifiers.py` | `tests/contract/test_renal_dose_interface_contracts.py`; `tests/unit/mappers/test_renal_dose_request.py` |
| `tests/unit/validation/test_results.py` | `tests/unit/validation/test_models.py` |
| `tests/unit/validation/test_structural.py` | `tests/unit/validation/test_lab.py`; `tests/unit/validation/test_patient.py`; `tests/unit/validation/test_validation_matrix.py` |
| `tests/unit/validation/test_sufficiency.py` | `tests/unit/validation/test_medication.py`; `tests/unit/validation/test_renal.py`; `tests/unit/validation/test_validation_matrix.py` |

Future components or contracts require behavior-specific tests. A placeholder skip must not be
reintroduced merely to reserve a path.

## Expected failures

No skip, XFAIL, or XPASS is currently approved for the release suite.

The former `UNSUP-FAM-WEIGHT` strict XFAIL is a normal passing integration case after enforcement of
the exact famotidine 40 kg adult minimum-weight boundary. The earlier retained Work Package 7
artifact remains historically accurate for its candidate and still records the limitations present
at that time.

## Runtime disposition rule

For every candidate, the durable verification artifact must reproduce the actual pytest
skip/XFAIL/XPASS report. Any skip, XFAIL, or XPASS not named here is unreviewed and blocks a release
decision until it receives an exact disposition.
