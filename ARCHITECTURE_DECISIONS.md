# Architecture Decisions

This document records the architecture decisions for the Automotive Security Regression Lab.

The decisions documented here describe intentional architecture constraints,
design choices, and implementation boundaries.

Accepted architecture decisions must remain consistent with the project
masterprompt and must not be silently contradicted by later implementation
or documentation changes.

## ADR-001 — ECU fully simulated

**Status:** Accepted
**Phase:** 1
**Source:** [MASTER]

The ECU used by the Automotive Security Regression Lab is fully simulated.

The project does not communicate with a real ECU or a productive automotive
system.

**Rationale:**

A simulated ECU provides a controlled, deterministic, reproducible, and safe
environment for developing and validating the security-test architecture.

**Consequences:**

- No real vehicle or ECU communication is required.
- Test execution is deterministic and locally reproducible.
- The project can demonstrate automotive security-test concepts without
  interacting with productive systems.
- Findings and test results represent the defined simulation behavior and
  must not be interpreted as evidence from a real vehicle.

## ADR-002 — Security tests reproducible and automatable

**Status:** Accepted
**Phase:** 1
**Source:** [MASTER]

Security tests shall be reproducible and automatable.

The test architecture therefore supports repeatable execution, deterministic
test behavior, structured results, and machine-readable test information.

**Rationale:**

Reproducibility is required to verify security requirements consistently and
to support later automated regression testing.

**Consequences:**

- Security tests can be executed repeatedly.
- Test outcomes can be evaluated programmatically.
- Structured test results provide a stable basis for evidence generation.
- Future CI/CD integration can build on the existing test architecture.

## ADR-003 — No real vehicles or productive systems

**Status:** Accepted
**Phase:** 1
**Source:** [MASTER]

The project does not use real vehicles, real ECUs, OEM systems, customer
systems, production environments, or production data.

**Rationale:**

The project is intended as a controlled security-testing laboratory and
portfolio implementation.

**Consequences:**

- All demonstrated security behavior is simulated.
- No productive automotive infrastructure is required.
- The architecture can be executed locally without external vehicle
  communication.

## ADR-004 — Test logic separated from ECU implementation

**Status:** Accepted
**Phase:** 1
**Source:** [MASTER]

Security-test logic and ECU implementation are separated.

The security-test architecture communicates with the simulated ECU through
an ECU target abstraction and adapter boundary.

The ECU is responsible for modeled system behavior.

The test architecture is responsible for test execution and evaluation.

**Rationale:**

This separation prevents security-test logic from being directly coupled to
the internal implementation of the simulated ECU.

It also provides a stable architectural boundary for later evidence
generation and regression workflows.

**Consequences:**

- ECU behavior can evolve independently from test execution logic.
- Security tests can use a stable target interface.
- Evidence generation remains outside the ECU implementation.

## ADR-005 — Phase 1 minimal Python/pytest foundation

**Status:** Accepted
**Phase:** 1
**Source:** [MASTER] + [SOURCE]

The initial project foundation uses Python and pytest.

No unnecessary security runtime dependencies are introduced.

The implementation uses the Python standard library and pytest where
appropriate.

**Rationale:**

The initial phase requires a small, deterministic, maintainable technical
foundation.

**Consequences:**

- The project remains lightweight.
- Test execution is locally reproducible.
- Additional dependencies can be introduced only when justified by later
  requirements.

## ADR-006 — ECU security behavior deterministic and mode-controlled

**Status:** Accepted
**Phase:** 2
**Source:** [MASTER]

The simulated ECU provides deterministic security behavior through explicit
security modes.

The supported modes are:

```text
SECURE
VULNERABLE
````

In secure mode, the protected operation requires authorization.

In vulnerable mode, the protected operation is intentionally accessible
without authorization.

**Rationale:**

Explicit security modes allow secure and vulnerable behavior to be reproduced
deterministically for security-test development.

**Consequences:**

* Secure behavior can be tested independently.
* Controlled vulnerable behavior can be reproduced.
* The vulnerable mode is a simulation mechanism and does not represent a
  real-world vulnerability.

## ADR-007 — ECU responses use a structured deterministic model

**Status:** Accepted
**Phase:** 2
**Source:** [MASTER]

ECU responses are represented by the structured `ECUResponse` model.

The response contains deterministic status information and the related
operation.

The response can be converted to a dictionary using `to_dict()`.

**Rationale:**

Structured responses provide a stable interface between ECU behavior,
security-test execution, and result generation.

**Consequences:**

* Test results can evaluate explicit response values.
* Response data can be used by later evidence generation.
* Response serialization remains deterministic.

## ADR-008 — Requests are validated before security processing

**Status:** Accepted
**Phase:** 2
**Source:** [MASTER]

Incoming ECU requests are validated before security processing.

The modeled validation behavior distinguishes malformed requests,
unsupported operations, and rejected parameters.

The current semantics are:

```text
Malformed request structure
    → INVALID_REQUEST

Missing or invalid operation
    → INVALID_REQUEST

Valid but unsupported operation
    → UNSUPPORTED_OPERATION

Invalid parameter structure
    → INVALID_REQUEST

Parameter outside 0..255
    → REQUEST_REJECTED
```

**Rationale:**

Request validation establishes a clear boundary between malformed input,
unsupported operations, and security or policy decisions.

**Consequences:**

* Invalid request structures are rejected deterministically.
* Unsupported operations are distinguishable from malformed requests.
* Parameter constraints are explicitly testable.

## Phase 4 — Evidence Framework

### ADR-009 — Security-test evidence uses a structured data model

**Status:** Accepted
**Phase:** 4
**Source:** [MASTER] + [INFERENCE]

Security-test evidence is represented by a structured Evidence data model.

The model contains:

```text
test_id
timestamp
target
preconditions
input
expected
actual
result
notes
```

**Rationale:**

A structured evidence model allows reviewers and automation to identify what
was tested, against which target, under which conditions, with which input,
and with which expected and actual result.

**Consequences:**

Positive:

* Evidence is machine-readable.
* Evidence has a stable structure.
* Evidence can be validated independently from the ECU.
* The model can be extended when later phases require additional metadata.

Negative:

* Extensions must preserve compatibility with the existing evidence
  structure where required.
* The Evidence model does not provide security finding management.

### ADR-010 — Evidence is generated outside the ECU and remains separate from target logic

**Status:** Accepted
**Phase:** 4
**Source:** [MASTER] + [INFERENCE]

The ECU does not create, validate, serialize, or manage Evidence.

Evidence is generated by the security-test architecture after test execution.

The architectural flow is:

```text
Security Test Case
        ↓
Security Test Runner
        ↓
ECU Adapter
        ↓
ECU Simulator
        ↓
ECU Response
        ↓
Test Result
        ↓
Evidence
```

**Rationale:**

The system under test must remain separated from the mechanism that records
and validates security-test observations.

**Consequences:**

Positive:

* ECU implementation remains independent of evidence handling.
* Evidence can be generated from structured test results.
* Test execution and evidence handling remain separable.

Negative:

* Evidence generation requires structured test results.
* Later evidence extensions must preserve the separation between target and
  evidence layers.

### ADR-011 — Evidence uses explicit PASS/FAIL based on expected versus actual behavior

**Status:** Accepted
**Phase:** 4
**Source:** [MASTER] + [INFERENCE]

Evidence uses explicit `PASS` and `FAIL` results.

The result is determined by comparing the expected and actual values:

```text
expected == actual
    → PASS

expected != actual
    → FAIL
```

Evidence validation verifies that the declared result is consistent with the
expected and actual values.

A `FAIL` result does not by itself establish that a security vulnerability
exists.

**Rationale:**

The Evidence Framework records the outcome of the defined security test.
Security finding classification is a separate concern.

**Consequences:**

* Test results are deterministic.
* Evidence consistency can be validated.
* Security findings can be assessed separately in later project phases.

### ADR-012 — Evidence is serialized as JSON

**Status:** Accepted
**Phase:** 4
**Source:** [MASTER] + [INFERENCE]

Evidence is serialized as JSON.

The serialization flow is:

```text
Evidence object
      ↓
to_dict()
      ↓
JSON-compatible data
      ↓
to_json()
      ↓
JSON
```

**Rationale:**

JSON provides a simple, machine-readable representation that can be consumed
by tests, automation, and later CI/CD components.

**Consequences:**

* Evidence can be stored and processed programmatically.
* JSON remains independent from a specific CI/CD platform.
* Phase 4 does not define CI/CD artifact handling.

### ADR-013 — Evidence validation remains lightweight and is implemented in the Evidence model

**Status:** Accepted
**Phase:** 4
**Source:** [MASTER] + [INFERENCE]

Evidence validation is implemented directly in the Evidence model.

Validation covers the required identifying fields, target, preconditions,
expected value, actual value, result type, and consistency between expected,
actual, and result.

Invalid evidence raises `EvidenceValidationError`.

**Rationale:**

The Evidence Framework requires deterministic validation without introducing
an unnecessary validation framework.

**Consequences:**

* Invalid evidence records are rejected.
* Evidence consistency can be checked locally.
* The validation implementation remains small and understandable.

### ADR-014 — Evidence timestamps use runtime-generated ISO 8601 UTC

**Status:** Accepted
**Phase:** 4
**Source:** [MASTER] + [INFERENCE]

Evidence timestamps are generated at runtime using UTC and ISO 8601 format.

Tests do not depend on a fixed wall-clock timestamp.

**Rationale:**

Evidence should record the actual execution time while remaining suitable for
automated test execution.

**Consequences:**

* Evidence contains execution-time metadata.
* Tests remain independent from a fixed timestamp.
* Timestamp handling remains deterministic in format but not in value.

### ADR-015 — Evidence is not Security Finding Management

**Status:** Accepted
**Phase:** 4
**Source:** [MASTER]

The Evidence Framework does not implement security finding management.

Evidence documents the observation and result of a security test.

Security finding management may later address additional information such as:

```text
Finding ID
Severity
CVSS
Root Cause
Customer Report
Remediation
Fix Management
```

Evidence answers:

```text
What was tested?
What was expected?
What actually happened?
What was the test result?
```

A security finding answers additional questions concerning the identified
issue, impact, root cause, and remediation.

**Rationale:**

Evidence and finding management represent different architectural concerns.

**Consequences:**

* Evidence remains focused on test execution.
* Finding management can be added in a later phase without changing the
  purpose of the Evidence Framework.
* Evidence must not be interpreted as a complete security finding record.

### ADR-016 — Phase 4 does not implement future regression or CI/CD layers

**Status:** Accepted
**Phase:** 4
**Source:** [MASTER]

Phase 4 implements the Evidence Framework only.

Future functionality such as:

```text
Complete regression suite
Regression workflow
GitHub Actions
CI/CD integration
CI/CD artifact handling
End-to-end assessment
```

is outside the scope of Phase 4.

**Rationale:**

The project is implemented phase by phase. Future architecture layers must
not be implemented implicitly as part of an earlier phase.

**Consequences:**

* Phase 4 remains limited to evidence generation and validation.
* Later phases can build on the Evidence Framework.
* Phase-specific scope remains traceable.

## ADR-017 — Request validation distinguishes malformed, unsupported, and rejected input

**Status:** Accepted
**Phase:** 6
**Source:** [MASTER] + [INFERENCE]

The ECU request-validation layer distinguishes malformed input,
unsupported operations, and rejected parameters.

The defined semantics are:

```text
Malformed request structure
    → INVALID_REQUEST

Missing or invalid operation
    → INVALID_REQUEST

Valid but unsupported operation
    → UNSUPPORTED_OPERATION

Invalid parameter structure
    → INVALID_REQUEST

Parameter outside 0..255
    → REQUEST_REJECTED

Boolean parameter
    → REQUEST_REJECTED
```

The valid numeric parameter range is inclusive:

```text
0..255
```

Boolean values are explicitly excluded even though Python treats `bool` as a
subclass of `int`.

**Rationale:**

TC-002 requires deterministic and distinguishable message-validation
behavior.

The distinction between malformed input, unsupported operations, and rejected
parameters provides a clear and machine-readable validation model.

**Consequences:**

* Invalid request structures remain distinguishable from unsupported
  operations.
* Parameter boundary behavior is deterministic.
* Boolean values cannot unintentionally pass numeric range validation.
* Future validation rules must preserve these distinctions unless an
  explicit architecture change is accepted.

## ADR-018 — TC-003 reuses the existing TC-001 security test definition

**Status:** Accepted
**Phase:** 7
**Source:** [TC-003] + [SOURCE]

The Phase-7 regression workflow reuses the existing TC-001
`SecurityTestCase` definition for the diagnostic authorization security
property.

The regression test module is:

```text
04_tests/test_security_regression.py
```

The pytest functions use the `test_tc003_*` naming convention because they
verify the TC-003 workflow.

The underlying `SecurityTestCase.test_id` remains:

```text
TC-001
```

This is intentional. TC-003 defines the regression workflow, while TC-001
defines the security property and test condition being reused as the
regression baseline.

**Rationale:**

The regression workflow must preserve the original security expectation
rather than create a different expectation merely for regression purposes.

For the protected operation, the security property remains:

```text
Unauthorized protected operation
        ↓
ACCESS_DENIED
```

Reusing the existing test definition also demonstrates that a previously
defined security test can serve as the basis for a later regression
execution.

**Consequences:**

Positive:

* The original TC-001 security expectation remains authoritative.
* Regression execution does not duplicate or redefine the security property.
* The relationship between TC-001 and TC-003 remains explicit.
* Changes to regression execution do not alter TC-001 security semantics.

Negative:

* The pytest module name and function prefix identify TC-003 while the
  underlying `SecurityTestCase` retains `TC-001`.
* Test identifiers must therefore be interpreted according to their
  respective layers.

## ADR-019 — Vulnerable and secure ECU modes provide controlled lifecycle states

**Status:** Accepted
**Phase:** 7
**Source:** [SOURCE] + [TC-003]

The `ECUSimulator` provides explicit `SecurityMode.SECURE` and
`SecurityMode.VULNERABLE` modes.

These modes are used by TC-003 to demonstrate the controlled lifecycle of a
security-relevant deviation and its subsequent secure retest.

The modes do not represent a runtime security-fix mechanism and do not
modify the simulator during test execution.

The modeled behavior is:

```text
VULNERABLE + unauthorized
        ↓
ACCESS_GRANTED

SECURE + unauthorized
        ↓
ACCESS_DENIED
```

**Rationale:**

The project requires deterministic reproduction of the security-relevant
condition and deterministic verification of the corrected security
behavior.

The two explicit simulator modes allow the lifecycle to be demonstrated
without external systems, uncontrolled environmental state, or real
vehicle communication.

The secure mode represents the intended security behavior. The vulnerable
mode represents a controlled test condition used to reproduce the modeled
pre-fix deviation.

**Consequences:**

Positive:

* Pre-fix and secure behavior can be reproduced deterministically.
* The original security condition can be retested with the same input.
* No real ECU or external system is required.
* TC-003 remains locally executable.

Negative:

* The vulnerable mode is a simulation mechanism and must not be interpreted
  as evidence of a real-world vulnerability.
* The lifecycle does not represent an actual software patch process.
* The implementation does not provide automated finding-to-fix management.

## ADR-020 — Regression evidence is generated from the executed TestResult

**Status:** Accepted
**Phase:** 7
**Source:** [TC-003] + [SOURCE]

TC-003 generates regression evidence through the existing
`EvidenceGenerator` using the executed `SecurityTestCase` and `TestResult`.

The evidence result is derived from the expected and actual response values
rather than from the pytest assertion itself.

The relationship is:

```text
SecurityTestCase
      ↓
SecurityTestRunner
      ↓
TestResult
      ↓
EvidenceGenerator
      ↓
Evidence
      ↓
Evidence.validate()
```

**Rationale:**

Evidence must represent the actual test execution independently of the
pytest assertion mechanism.

This preserves the architectural separation established by the Evidence
Framework.

**Consequences:**

Positive:

* Evidence remains coupled to the executed test result rather than to test
  implementation details.
* Expected and actual behavior remain machine-readable.
* Evidence validation can independently confirm result consistency.

Negative:

* The Evidence model remains limited to execution evidence.
* Security finding management and remediation tracking remain outside the
  current implementation.

## ADR-021 — TC-003 distinguishes lifecycle demonstration from regression retest

**Status:** Accepted
**Phase:** 7
**Source:** [TC-003] + [SOURCE]

The TC-003 test module contains both a controlled lifecycle demonstration and
actual secure regression/retest verification.

The roles are:

```text
Lifecycle Demonstration
    └── test_tc003_reproduces_original_vulnerable_behavior()

Regression / Retest
    ├── test_tc003_retest_confirms_secure_behavior()
    ├── test_tc003_regression_evidence_matches_retest_result()
    └── test_tc003_regression_preserves_authorized_behavior()
```

The vulnerable-behavior test intentionally verifies a non-passing
`TestResult` because the simulated vulnerable ECU returns
`ACCESS_GRANTED` where `ACCESS_DENIED` is required.

The pytest test passes because it verifies that the deviation is correctly
detected.

**Rationale:**

This separation allows Phase 7 to demonstrate the complete controlled
security-test lifecycle without treating the vulnerable-state reproduction
itself as a successful security regression result.

**Consequences:**

* The lifecycle demonstration must not be described as a passing security
  result.
* The secure retest is the actual regression verification.
* A pytest pass does not necessarily mean that the underlying security
  `TestResult` is `PASS`; the vulnerable-behavior demonstration is the
  explicit example of this distinction.

## Change Policy

Architecture changes must be documented in this file before they are treated
as accepted architecture decisions.

Later project phases may add new ADRs.

Later phases must not silently contradict accepted architecture decisions.
If an existing decision must change, the change must be explicitly
documented and reviewed.

New implementation behavior that introduces a meaningful architecture
decision shall be documented as a new ADR rather than being silently added
to an existing historical decision.
