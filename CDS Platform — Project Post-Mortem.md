# CDS Platform — Project Post-Mortem

**Status:** Archived  
**Archived:** August 7, 2026  
**Outcome:** Educational prototype completed in part; intentionally discontinued before release or clinical use.

## Summary

The CDS Platform was an attempt to learn how a safety-conscious clinical decision-support system could be structured in Python.

The project evolved from architectural exploration into a working, narrowly bounded renal-function and renal-dose-adjustment prototype. It established typed clinical models, strict validation, deterministic calculations, versioned clinical content, rule evaluation, structured outputs, provenance, automated testing, and explicit safety boundaries.

The project is being discontinued because continuing to develop a generalized CDS platform is no longer the best use of its developer's time.

The primary objective going forward is deeper clinical knowledge and stronger clinical practice. Building software intended to perform increasingly large portions of that reasoning would consume substantial time while partially displacing the deliberate clinical work that currently has greater educational value.

This repository therefore remains an educational artifact, not an unfinished product roadmap.

## Original Goal

The project was intended to explore how clinical decision-support software could be built around several principles:

- typed clinical data
- validation before computation
- deterministic and inspectable calculations
- simple rule evaluation
- clinical content separated from application logic
- explicit handling of missing or unsupported information
- traceable recommendations
- assumptions, warnings, evidence, and provenance
- behavior-focused automated testing
- fail-closed behavior when required clinical information is unavailable

The initial implementation was deliberately restricted to an adult Cockcroft–Gault renal-function calculation followed by limited renal-dose evaluation for cefepime, piperacillin–tazobactam, and famotidine.

The repository was never intended or authorized for direct clinical use.

## What Was Accomplished

The project demonstrated substantially more than a simple calculator.

It produced a layered Python architecture containing domain models, validation, pure calculation services, rule evaluation, versioned YAML clinical content, repository boundaries, application orchestration, mapping, interfaces, serialization, and testing.

The project established explicit representations for:

- patients and clinical observations
- medication orders
- renal-function calculations
- recommendations and alerts
- contraindications
- assumptions
- warnings
- evidence
- provenance
- incomplete and unsupported evaluations
- system failures

The renal workflow was designed to validate inputs before calculation, avoid silent assumptions, preserve calculation inputs, use exact rule matching, and fail closed when a recommendation could not safely be generated.

The project also developed substantial experience with:

- Python project structure
- typed models
- dataclasses and domain modeling
- architectural boundaries
- dependency direction
- YAML-backed content
- deterministic serialization
- unit, integration, contract, parameterized, and golden testing
- Git and GitHub workflows
- pull requests
- release candidates
- software verification
- clinical-content review
- provenance and auditability
- safety-oriented software design

These are durable outcomes even though the platform itself will not continue.

## What Went Well

### Safety constraints were treated as architecture

Clinical uncertainty was not treated merely as an error-handling problem.

Missing data, ambiguous units, unsupported populations, unstable renal function, unsupported regimens, conflicting information, and missing content were modeled as explicit states that could stop computation.

This is an important design principle worth retaining.

### Clinical content was separated from software behavior

Medication guidance, thresholds, citations, versions, and review information were represented as inspectable content rather than being scattered through application code.

This made the relationship between evidence and software behavior substantially clearer.

### Outputs became traceable

The project moved beyond returning a number or recommendation.

Results could preserve the calculation, source inputs, assumptions, warnings, evidence, provenance, rule identifiers, content versions, and failure state.

This is particularly useful for future clinical tools.

### Testing became part of the reasoning process

Boundary testing, unsupported cases, contradictory inputs, golden cases, and fail-closed behavior demonstrated how tests can function as executable specifications rather than merely regression protection.

### The project exposed real software-engineering complexity

The project provided practical exposure to architecture, dependencies, abstractions, validation, testing, packaging, Git workflows, release management, and verification.

That learning remains useful even if this particular system never progresses further.

## What Became Too Expensive

The project gradually changed character.

Initially, most work directly represented clinical concepts or calculations.

Later work increasingly concerned:

- architecture enforcement
- generic platform abstractions
- compatibility contracts
- release-state documentation
- candidate verification
- environment verification
- release evidence
- serialization contracts
- generalized feature infrastructure
- maintaining relationships among numerous architectural layers

These are legitimate concerns for a production clinical system.

They are not necessarily the highest-value concerns for a personal educational project.

The infrastructure required to safely generalize the application began consuming more effort than the individual clinical features it was intended to support.

## Scope Expansion

A particularly useful stopping signal was the transition from implementing one bounded renal workflow to designing generic evaluation and feature contracts.

At that point, the project was no longer primarily answering:

> How should this clinical problem be represented and evaluated?

It was increasingly answering:

> How should an extensible clinical decision-support platform represent arbitrary future clinical problems?

The second problem is dramatically larger.

Solving it well requires considerably more software-engineering experience, testing infrastructure, governance, clinical-content management, security work, interoperability work, and eventually regulatory and organizational support.

That problem does not need to be solved for the original learning objectives to have been successful.

## Why Development Is Stopping

The central tradeoff is opportunity cost.

Time spent building a system capable of performing clinical reasoning is time that could instead be spent performing, studying, recording, and refining that clinical reasoning directly.

At the current stage of development, improving personal clinical knowledge and clinical practice has greater value than increasing the capability of the CDS platform.

Future software projects should therefore augment learning and clinical reasoning rather than attempt to replace large portions of them.

The project is being stopped intentionally rather than because another technical blocker must first be solved.

## Key Lessons

### Build the smallest useful thing

A bounded calculator, validator, reference tool, or workflow can provide substantial value without becoming a platform.

Platform architecture should emerge only after multiple completed tools demonstrate a genuine shared requirement.

### Repetition should justify abstraction

A hypothetical future requirement is usually insufficient justification for another abstraction.

Shared infrastructure should generally be extracted after the same problem has been encountered repeatedly.

### Clinical tools should increase useful cognitive work

For personal projects, the highest-value tool is not necessarily the one that automates the most work.

A better criterion is whether the tool helps its user:

- notice more
- reason more consistently
- retrieve evidence faster
- document reasoning
- compare cases
- identify uncertainty
- learn from prior decisions

Automation that removes the reasoning being deliberately practiced may be counterproductive.

### Software rigor has a cost

Typed models, validation, provenance, testing, versioning, release gates, architecture constraints, and auditability are valuable.

Together they also create substantial maintenance overhead.

The appropriate level of rigor depends on the intended use of the software.

A personal learning aid and a production clinical CDS system should not be engineered as though they have identical requirements.

### Disposable software is acceptable

Not every successful prototype needs to become a maintained application.

Code can accomplish its purpose by teaching a concept, testing an idea, or revealing requirements.

Archiving that code can be the appropriate definition of done.

## What Should Be Reused

Future projects may freely reuse concepts learned here, particularly:

- typed domain modeling
- explicit units
- `None` rather than fabricated values
- validation before calculation
- pure calculation functions
- explicit unsupported states
- assumptions and warnings
- evidence and provenance
- versioned clinical content
- parameterized boundary tests
- fail-closed behavior where clinically appropriate

The CDS Platform itself should not become a mandatory dependency for future projects.

Reuse ideas before reusing infrastructure.

## Future Project Selection Criteria

A future personal clinical software project should preferably:

1. solve one clearly bounded problem;
2. have an obvious input and output;
3. reinforce rather than replace clinical reasoning;
4. produce something useful before substantial infrastructure is required;
5. remain understandable without a large architectural framework;
6. use abstractions only after repetition demonstrates their value;
7. be capable of being abandoned without creating significant maintenance debt; and
8. teach either a clinical concept or a software concept intentionally.

Projects that immediately require a platform, plugin architecture, generic rule engine, interoperability layer, production deployment model, or broad clinical knowledge representation should generally be deferred.

## Repository Disposition

The repository is preserved as a historical and educational artifact.

It is not released for clinical use.

The existing release `no-go` remains in effect. No additional verification work is required solely for archival purposes.

Open experimental platform-expansion work should remain unmerged.

The repository may be consulted for design patterns, tests, architectural ideas, or historical reference.

Unarchiving it should not itself imply resumption of the CDS Platform roadmap. Any future revival should begin with a new project charter and a new assessment of whether building a generalized CDS system remains the appropriate objective.

## Final Assessment

The CDS Platform succeeded as an educational project.

Its most valuable outputs are not a deployable CDS application. They are the engineering concepts learned while attempting to build one, the clearer understanding of what production-quality clinical software actually requires, and the recognition that the next highest-value work lies elsewhere.

The project is complete as a learning artifact.

Development ends here.