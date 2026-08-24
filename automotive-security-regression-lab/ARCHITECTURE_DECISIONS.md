# Architecture Decisions

This document records the architecture decisions for the Automotive Security
Regression Lab.

The decisions documented here describe intentional architectural constraints
and design choices made during the implementation of the project.

Accepted decisions must remain consistent with the project masterprompt and
must not be silently contradicted by later phases.

---

## ADR-001 — The ECU is fully simulated

**Status:** Accepted  
**Phase:** 1  
**Source:** [MASTER]

The project uses a simulated ECU rather than a real vehicle ECU or productive
automotive system.

**Rationale:**

The project is explicitly defined as a controlled, fully simulated
automotive security-testing laboratory. This keeps the environment
reproducible and avoids interaction with real vehicles or productive
systems.

---

## ADR-002 — Security tests are intended to be reproducible and automatable

**Status:** Accepted  
**Phase:** 1  
**Source:** [MASTER]

The security-testing workflow is designed around repeatable automated
execution and evidence-oriented verification.

**Rationale:**

Reproducibility and automation are explicit project objectives and provide
the foundation for later regression-testing and continuous verification
activities.

The architecture therefore favors deterministic behavior, structured test
results, and machine-readable test information.

---

## ADR-003 — No interaction with real vehicles or productive systems

**Status:** Accepted  
**Phase:** 1  
**Source:** [MASTER]

The project does not interact with real vehicles, ECUs, OEM systems,
customer data, or productive systems.

**Rationale:**

This is an explicit project scope constraint.

The simulated environment is sufficient for demonstrating the intended
security-testing workflow while keeping execution controlled and
reproducible.

---

## ADR-004 — Test logic is separated from the ECU implementation

**Status:** Accepted  
**Phase:** 1  

**Source:** [MASTER]

The architecture separates security test cases and test execution from the
simulated ECU through an ECU target abstraction and adapter boundary.

**Rationale:**

The separation establishes a clear boundary between the security-test
mechanism and the system under test.

The ECU remains responsible for simulated system behavior, while the test
architecture is responsible for executing and evaluating security tests.

This separation also provides a stable boundary for the Evidence Framework
introduced in Phase 4.

---

## ADR-005 — Phase 1 uses a minimal Python/pytest foundation

**Status:** Accepted  
**Phase:** 1  
**Source:** [MASTER] + [SOURCE]

Phase 1 uses Python and pytest as the primary implementation and test
foundation without adding unnecessary security-specific runtime
dependencies.

**Rationale:**

The project requires a simple, reproducible local test environment.
Additional frameworks are not introduced unless a project requirement
justifies them.

The implementation therefore favors the Python standard library and pytest
for the core project functionality.

---

## ADR-006 — ECU security behavior is deterministic and mode-controlled

**Status:** Accepted  
**Phase:** 2  
**Source:** [MASTER]

The simulated ECU provides two explicit security modes:

- `secure`
- `vulnerable`

In `secure` mode, the protected operation requires explicit authorization.

In `vulnerable` mode, the protected operation is intentionally granted
without authorization.

**Rationale:**

The project requires a deterministic security target that can represent both
intended secure behavior and a controlled vulnerable behavior for
reproducible security testing.

Explicit security modes make the simulated security behavior predictable
and suitable for automated testing.

---

## ADR-007 — ECU responses use a structured deterministic response model

**Status:** Accepted  
**Phase:** 2  
**Source:** [MASTER]

The simulated ECU returns a structured `ECUResponse` containing a
deterministic response status and the corresponding operation.

The response can be converted into a simple dictionary representation using
`to_dict()`.

**Rationale:**

A structured response model provides a stable interface between the
simulated ECU and the test architecture.

Deterministic response values make test results reproducible and provide
stable input for the test-result and evidence layers.

---

## ADR-008 — Requests are validated before security processing

**Status:** Accepted  
**Phase:** 2  
**Source:** [MASTER]

The simulated ECU validates the request structure before applying the
security policy.

Requests must provide a valid operation string. Only the defined
`PROTECTED_OPERATION` is accepted. If optional `parameters` are provided,
they must be represented as a mapping.

Invalid request structures and unknown operations result in a deterministic
`INVALID_REQUEST` response.

**Rationale:**

Request validation provides a clear boundary between malformed input and
security-policy decisions.

This keeps the simulator deterministic and prevents malformed requests from
being interpreted as valid protected operations.

---

# Phase 4 — Evidence Framework

## ADR-009 — Security-test evidence is represented as a structured data model

**Status:** Accepted  
**Phase:** 4  
**Source:** [MASTER] + [INFERENCE]

Security-test evidence is represented as a dedicated structured data model
rather than as an unstructured log message or free-form text record.

The Phase-4 Evidence model contains:

- `test_id`
- `timestamp`
- `target`
- `preconditions`
- `input`
- `expected`
- `actual`
- `result`
- `notes`

**Rationale:**

Evidence must allow a reviewer or an automated process to identify what was
tested, against which target, under which conditions, with which input, what
behavior was expected, what behavior was actually observed, and what result
was obtained.

A structured model provides explicit fields for these concepts and avoids
relying on parsing conventions associated with unstructured log output.

The model is intentionally small and focused on the observation of a test
execution.

**Consequences:**

Positive:

- Evidence has a stable machine-readable structure.
- Required information is explicitly represented.
- Evidence can be validated programmatically.
- The structure can be extended with optional fields in later phases.
- Evidence can be serialized for automation.

Negative:

- The Evidence model must evolve if later phases require additional
  execution metadata.
- Backward compatibility may need to be considered when optional or new
  fields are introduced.

The Evidence model does not implement security finding management.

---

## ADR-010 — Evidence is generated outside the ECU and remains separate from test-target logic

**Status:** Accepted  
**Phase:** 4  
**Source:** [MASTER] + [INFERENCE]

The Evidence Framework is implemented outside the simulated ECU.

The ECU does not create, validate, serialize, or manage Evidence records.

The intended execution flow is:

```text
Security Test Case
        ↓
Test Runner
        ↓
ECU Adapter
        ↓
ECU Simulator
        ↓
Response
        ↓
Test Result
        ↓
Evidence
````

**Rationale:**

The ECU is the simulated system under test and must remain independent of
the mechanism used to document its test execution.

Coupling evidence generation to the ECU would mix system-under-test
responsibilities with test and reporting responsibilities.

Keeping the Evidence Framework outside the ECU preserves the architectural
separation established in Phase 3.

**Consequences:**

Positive:

* The ECU remains unaware of the test framework.
* Test-target implementation remains reusable.
* Evidence generation can evolve independently.
* The architecture supports later automation without modifying the ECU.

Negative:

* Evidence generation requires information from the completed test
  execution.
* The interface between `TestResult` and Evidence must remain consistent.

---

## ADR-011 — Evidence uses explicit PASS/FAIL semantics based on expected versus actual behavior

**Status:** Accepted
**Phase:** 4
**Source:** [MASTER] + [INFERENCE]

The Evidence Framework represents test execution results using two result
values:

* `PASS`
* `FAIL`

The semantics are:

```text
PASS
Expected behavior == Actual behavior

FAIL
Expected behavior != Actual behavior
```

The Evidence model validates that the declared result is consistent with
the expected and actual values.

**Rationale:**

The Evidence Framework documents whether the observed behavior matched the
behavior expected by the executed test.

Explicit result semantics prevent ambiguous interpretations of the evidence
record.

The distinction is intentionally limited to test-result semantics.

A `FAIL` result means:

> The observed behavior did not match the expected behavior.

A `FAIL` result does **not** by itself establish that a security
vulnerability has been confirmed.

Security finding assessment belongs to later project phases.

**Consequences:**

Positive:

* Result interpretation is deterministic.
* Evidence records can be evaluated automatically.
* Test outcomes remain comparable across executions.

Negative:

* PASS/FAIL does not represent a complete security risk assessment.
* Additional security assessment information is required before a result can
  be treated as a security finding.

---

## ADR-012 — Evidence is serialized as JSON for machine-readable exchange

**Status:** Accepted
**Phase:** 4
**Source:** [MASTER] + [INFERENCE]

The primary serialization format for Evidence is JSON.

The Evidence model provides a conversion path from the structured Evidence
object to a JSON-compatible dictionary representation and then to a JSON
document.

The intended representation is:

```text
Evidence Object
      ↓
Dictionary
      ↓
JSON
```

**Rationale:**

Phase 4 requires machine-readable evidence and explicitly identifies JSON as
the primary serialization format.

JSON provides a simple representation that can be consumed by local tools,
test automation, and later artifact-processing mechanisms without coupling
the Evidence model to a specific CI/CD implementation.

**Consequences:**

Positive:

* Evidence can be stored and exchanged in a machine-readable format.
* JSON is suitable for automated processing.
* The representation remains independent of the ECU implementation.
* Later automation can consume the serialized representation.

Negative:

* JSON serialization must preserve the semantics of the Evidence model.
* Future schema extensions must be introduced carefully to avoid ambiguity.

Phase 4 does not implement CI/CD artifact handling.

---

## ADR-013 — Evidence validation is lightweight and performed by the Evidence model

**Status:** Accepted
**Phase:** 4
**Source:** [MASTER] + [INFERENCE]

Evidence validation is implemented directly within the Evidence Framework
using a lightweight validation strategy.

The validation process verifies the presence and consistency of required
evidence information.

At minimum, validation covers:

* required identifying fields
* target information
* preconditions structure
* expected behavior
* actual behavior
* result type
* result consistency

Invalid evidence is rejected rather than silently accepted.

**Rationale:**

Phase 4 requires protection against incomplete Evidence records but does not
require a separate validation framework.

A lightweight implementation keeps the project dependency footprint small
and makes the validation rules explicit and easy to review.

**Consequences:**

Positive:

* Invalid evidence cannot silently pass validation.
* Validation behavior is close to the data model.
* No unnecessary runtime dependency is introduced.
* Validation rules remain easy to understand.

Negative:

* More complex schema validation may require an architectural extension
  if future phases introduce substantially more complex evidence structures.

---

## ADR-014 — Evidence timestamps use runtime-generated ISO 8601 UTC values

**Status:** Accepted
**Phase:** 4
**Source:** [MASTER] + [INFERENCE]

Evidence records contain a runtime-generated timestamp represented using an
ISO-8601-compatible UTC representation.

The timestamp is generated when Evidence is created rather than being a
fixed value embedded in the implementation.

**Rationale:**

Evidence represents an actual test execution. The execution timestamp
therefore belongs to the generated evidence record and must not depend on a
fixed example timestamp.

Runtime generation also ensures that repeated test executions produce
execution-specific timestamps.

Tests must not rely on a fixed wall-clock timestamp.

**Consequences:**

Positive:

* Evidence records contain execution-time information.
* Generated records are suitable for repeated local execution.
* The timestamp representation is machine-readable.

Negative:

* Timestamp values naturally differ between executions.
* Tests must verify timestamp structure or presence rather than expect a
  fixed timestamp.

---

## ADR-015 — Evidence is not Security Finding Management

**Status:** Accepted
**Phase:** 4
**Source:** [MASTER]

The Evidence Framework documents the observation and result of a security
test execution.

It does not implement:

* security finding IDs
* severity classification
* CVSS calculation
* root-cause analysis
* customer security reports
* remediation tracking
* fix management

**Rationale:**

The masterprompt explicitly separates Evidence from Security Finding
Management.

Evidence answers:

```text
What was tested?
What was expected?
What actually happened?
What was the test result?
```

A later finding process answers questions such as:

```text
Is this a security issue?
Why is it a security issue?
What is the impact?
What is the root cause?
How should it be fixed?
```

Maintaining this boundary prevents the Evidence Framework from becoming an
implicit vulnerability-management system.

**Consequences:**

Positive:

* Evidence remains focused on test execution.
* Security assessment remains a separate engineering activity.
* Later finding-management functionality can consume evidence without
  requiring evidence records to contain finding semantics.

Negative:

* A FAIL evidence record cannot by itself provide a complete security
  assessment.
* Additional later workflow stages are required for finding analysis.

---

## ADR-016 — Phase 4 does not implement the future regression or CI/CD layers

**Status:** Accepted
**Phase:** 4
**Source:** [MASTER]

Phase 4 provides the Evidence Framework required to document test
executions, but it does not implement the complete regression framework or
CI/CD artifact workflow.

The following capabilities remain outside Phase 4:

* complete regression suite
* regression workflow
* GitHub Actions workflow
* CI/CD artifact handling
* end-to-end security assessment

**Rationale:**

The project is developed strictly phase by phase.

The Evidence Framework is intended to provide a reusable foundation for
later automation, but implementing that later automation during Phase 4
would violate the defined phase boundary.

**Consequences:**

Positive:

* Phase responsibilities remain clearly separated.
* The Evidence Framework can be reviewed independently.
* Future regression and CI/CD layers can consume Evidence without requiring
  premature implementation.

Negative:

* The complete Evidence-to-CI/CD workflow is not available after Phase 4.
* Later phases must define the integration behavior explicitly.

---

# Change Policy

Architecture changes must be documented in this file before they are
treated as accepted project decisions.

Later phases may add new Architecture Decision Records, but they must not
silently contradict accepted decisions.

If a later phase requires a change to an accepted decision, the change must
be explicitly documented and reviewed rather than silently modifying the
existing decision.

---

# Phase 4 Architectural Summary

The Phase-4 architecture establishes the following boundary:

```text
+-----------------------+
| Security Test Case    |
+-----------------------+
            |
            v
+-----------------------+
| Security Test Runner  |
+-----------------------+
            |
            v
+-----------------------+
| ECU Adapter           |
+-----------------------+
            |
            v
+-----------------------+
| Simulated ECU         |
| System Under Test     |
+-----------------------+
            |
            v
+-----------------------+
| ECU Response          |
+-----------------------+
            |
            v
+-----------------------+
| Test Result           |
+-----------------------+
            |
            v
+-----------------------+
| Evidence Framework    |
+-----------------------+
            |
            v
+-----------------------+
| JSON Evidence         |
+-----------------------+
```

The central Phase-4 architectural principle is:

**Evidence documents a security-test observation; it does not become part
of the system under test.**

This preserves the separation between:

* system behavior
* test execution
* test evidence
* later security assessment
* later regression automation

---

# Phase 4 Review Requirement

Before Phase 4 can be declared complete, the implementation and repository
must be reviewed against the Phase-4 masterprompt.

The review must verify at minimum:

* Evidence model implementation
* required-field validation
* PASS/FAIL semantics
* timestamp generation
* JSON serialization
* integration with Phase-3 `TestResult`
* separation from the ECU
* Evidence documentation
* architecture documentation
* test execution
* reproducibility
* absence of future-phase implementation
* repository state
* documentation consistency

Phase 4 must not be marked completed until the defined Quality Gate has
passed.

```