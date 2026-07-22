# CDS Daily Task Prompt Template

Use this template in a **fresh conversation** for each CDS implementation task. Replace every angle-bracket placeholder and remove any instruction that does not apply.

Keep the task limited to one deliverable. The repository, not prior chat history, is the durable source of truth.

## Copyable prompt

```markdown
@GitHub /cds-platform repo

Implement: **<one precise deliverable>**

## Read first

Read only:

- `AGENTS.md`
- `CURRENT.md`
- `<directly relevant implementation module>`
- `<directly relevant test module>`

Open additional files only when required to resolve a direct import, existing public contract, targeted test failure, or material ambiguity.

## Required behavior

- <observable requirement 1>
- <observable requirement 2>
- <observable requirement 3>

## Non-goals

- Do not <adjacent task or refactor>.
- Do not <future feature, integration, or abstraction>.
- Do not modify unrelated modules or tests.
- Do not broaden the current vertical slice.

## Workflow

### Orient

- Read the four files listed above.
- Run the narrowest relevant existing test file or test selection.
- State the single deliverable in one sentence.

### Build

- Make the smallest coherent change that satisfies the required behavior.
- Preserve repository architecture, safety conventions, public imports, and serialized contracts unless this task explicitly changes them.
- Add or update focused tests for changed behavior.

### Close

- Run the targeted tests first and report the exact command and result.
- Run the full test suite only when this task completes a feature, reaches a weekly checkpoint, changes a shared contract, or otherwise requires merge-level verification.
- Replace `CURRENT.md` with the new current state and one exact next action; do not append a task diary.
- Do not create a `DAY_*_CHECKPOINT.md` file or any other task-history file.
- Put implementation history, rationale, verification details, and noteworthy limitations in the pull-request description.

## Delivery

- Use the connected GitHub repository interface.
- Create a focused branch and pull request containing only this task.
- Verify the pull-request diff contains no unrelated changes.
- Merge the pull request after required checks pass.

## Done when

- <specific acceptance criterion 1>
- <specific acceptance criterion 2>
- `<targeted test command>` passes.
```

## Minimal example

```markdown
@GitHub /cds-platform repo

Implement: **passive `ValidationIssue` and `ValidationResult` models**

## Read first

Read only:

- `AGENTS.md`
- `CURRENT.md`
- `src/cds/validation/models.py`
- `tests/unit/validation/test_models.py`

Open additional files only when required to resolve a direct import, existing public contract, targeted test failure, or material ambiguity.

## Required behavior

- Represent validation status and severity with explicit typed values.
- Preserve safe incomplete defaults.
- Keep validation execution and renal sufficiency rules out of the models.

## Non-goals

- Do not implement renal sufficiency rules.
- Do not add validation orchestration or service logic.
- Do not modify unrelated domain models.
- Do not broaden the current vertical slice.

## Workflow

### Orient

- Read the four files listed above.
- Run `python -m pytest tests/unit/validation/test_models.py -q` if the file exists; otherwise run the narrowest relevant validation test selection.
- State the single deliverable in one sentence.

### Build

- Make the smallest coherent change that satisfies the required behavior.
- Preserve repository architecture, safety conventions, public imports, and serialized contracts.
- Add focused tests for construction, defaults, and independent mutable fields.

### Close

- Run targeted validation tests first and report the exact command and result.
- Run the full suite because this completes the passive validation-model foundation.
- Replace `CURRENT.md` with the new current state and one exact next action; do not append a task diary.
- Do not create a `DAY_*_CHECKPOINT.md` file or any other task-history file.
- Put implementation history, rationale, verification details, and noteworthy limitations in the pull-request description.

## Delivery

- Use the connected GitHub repository interface.
- Create a focused branch and pull request containing only this task.
- Verify the pull-request diff contains no unrelated changes.
- Merge the pull request after required checks pass.

## Done when

- Both models import and can be instantiated independently.
- Missing or incomplete validation state is explicit rather than represented by blank strings.
- Targeted tests and the full test suite pass.
```
