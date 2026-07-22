# Adult Cockcroft–Gault Independent Verification

> **Prototype only — not for direct clinical use.** This verification uses synthetic data for
> research, education, and software development. It does not validate the calculator or its
> outputs for patient-care decisions.

## Scope

This record verifies the arithmetic examples and the preservation of unrounded calculator output
for future renal-band comparisons. It does not change the normative contract in
[`RENAL_CALCULATOR_SPEC.md`](RENAL_CALCULATOR_SPEC.md), define clinical dosing bands, or verify a
medication recommendation.

## Independent method

The reference values were recalculated without calling `cds.services.renal`:

1. Determine completed age from the explicit birth and evaluation dates.
2. Represent every supplied decimal as an exact integer ratio.
3. Evaluate the base Cockcroft–Gault equation with exact rational arithmetic.
4. Convert the exact base fraction to `Decimal` using 28 significant digits and
   `ROUND_HALF_EVEN`, reproducing the specified division boundary.
5. For the female case only, multiply that context-rounded base value by exact
   `Decimal("0.85")` in the same 28-digit context, reproducing the specified second operation.
6. Apply no presentation quantization.
7. Compare the resulting fixed decimal string with the value asserted by the focused service
   tests.

This path is independent of the production calculator's intermediate Decimal operations. The
fixed expected strings remain reviewable even if the service implementation later changes.

## Verified synthetic golden cases

| Case | Age | Sex | Weight | Serum creatinine | Exact rational result | Expected stored `mL/min` |
|---|---:|---|---:|---:|---:|---:|
| Normal | 40 | male | 72.5 kg | 0.9 mg/dL | `18125/162` | `111.8827160493827160493827160` |
| Impaired | 75 | male | 63.4 kg | 1.8 mg/dL | `20605/648` | `31.79783950617283950617283951` |
| Metadata fixture | 45 | male | 72.40 kg | 1.13 mg/dL | `85975/1017` | `84.53785644051130776794493609` |
| Sex-coefficient fixture | 45 | female | 72.40 kg | 1.13 mg/dL | `292315/4068` | `71.85717797443461160275319568` |

The female row deliberately follows the normative two-step Decimal operation order. Rounding the
single exact fraction `292315/4068` only once at the end would produce
`71.85717797443461160275319567`; that is not the specified calculator operation sequence.

## Future band-boundary preservation

The focused test uses a synthetic threshold of `60 mL/min` solely to prove that future matching
can compare the stored value rather than a display-rounded value. The fixture is a 68-year-old
male with a supplied 60 kg weight.

| Position | Serum creatinine | Exact rational result | Expected stored `mL/min` | Hypothetical one-decimal display |
|---|---:|---:|---:|---:|
| Immediately above | 0.99999 mg/dL | `2000000/33333` | `60.00060000600006000060000600` | `60.0` |
| At threshold | 1 mg/dL | `60/1` | `60` | `60.0` |
| Immediately below | 1.00001 mg/dL | `6000000/100001` | `59.99940000599994000059999400` | `60.0` |

All three values would display identically at one decimal place but remain ordered correctly in
stored form. A future band predicate must compare these stored values directly.

## Limitations

- This is software arithmetic verification, not independent clinical validation.
- The cases are synthetic and do not establish safe or appropriate dosing thresholds.
- No renal-band predicate, clinical content, medication rule, or recommendation exists at this
  checkpoint, so actual band selection cannot yet be verified.
- The independent path uses exact rational arithmetic but still uses Python's Decimal conversion
  for the specified 28-digit final representation.
- Four golden cases and one synthetic threshold triplet do not exhaust the supported numeric
  domain.
- The focused pytest module was not executed in the supplied environment because `pytest` was not
  installed. The deferred command is recorded in `CURRENT.md`.
