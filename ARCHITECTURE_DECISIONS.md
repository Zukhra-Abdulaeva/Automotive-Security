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

Structured security finding documentation is introduced in Phase 8.

This does not change the responsibility of the Evidence Framework and does not
introduce generalized security finding management.

Generalized security finding management may later address additional
information such as:

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
* Phase 8 can document representative security findings without changing the
  purpose of the Evidence Framework.
* Generalized finding management can be added in a later phase without
  changing the purpose of the Evidence Framework.
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

TC-003 defines the regression-test scenarios for the established security properties.

The automated regression test module is:

```text
04_tests/test_security_regression.py
```

The regression scenarios create their own SecurityTestCase instances with:

```text
test_id = TC-003
```

TC-001 remains the original security test that established the diagnostic authorization property. 
TC-003 verifies that the established security behavior remains preserved, but it does not reuse 
the TC-001 SecurityTestCase instance or retain TC-001 as the test identifier of the regression scenario.
The pytest functions use the `test_tc003_*` naming convention because they verify the TC-003 workflow.

The underlying `SecurityTestCase.test_id` remains:

```text
TC-001
```

This is intentional. TC-003 defines the regression workflow, while TC-001
defines the security property and test condition being reused as the
regression baseline.

The architectural relationship is therefore:

``text
TC-001
  |
  +-- establishes the security property
  |
  v
TC-003
  |
  +-- verifies the established property through regression scenarios
  |
  v
SecurityTestCase(test_id="TC-003")
```

For the protected operation, the established security property remains:

``text
Unauthorized protected operation
        ↓
ACCESS_DENIED
```

**Rationale:**

The security property established by TC-001 must remain stable while 
the regression workflow receives its own test identity.

Separating the test identifiers makes the distinction between the 
original security test and its later regression verification explicit 
and avoids conflating test-definition identity with regression-workflow identity.

**Consequences:**

Positive:

* TC-001 remains the original security-property definition.
* TC-003 has an explicit identity as a regression test.
* Regression scenarios can be extended independently without changing TC-001.
* Generated regression evidence can identify the regression execution 
directly through test_id=TC-003.

Negative:

* The relationship between TC-001 and TC-003 must remain documented because 
they represent different test layers.
* A regression test must not be interpreted as a replacement for the original 
security-property definition.

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

No separate regression-specific evidence generator or evidence model is introduced.

For the secure unauthorized protected-operation scenario, the resulting evidence contains:

test_id     = TC-003
target      = simulated-ecu

authorization = false
ecu_state     = READY
security_mode = SECURE

expected    = ACCESS_DENIED
actual      = ACCESS_DENIED
result      = PASS

**Rationale:**

Evidence must represent the actual test execution independently of the
pytest assertion mechanism.

This preserves the architectural separation established by the Evidence
Framework.

Using the existing Evidence Framework preserves the architectural 
separation between target behavior, test execution, and evidence handling.

Explicit evidence validation additionally ensures that the generated 
evidence satisfies the established Evidence Framework rules.

**Consequences:**

Positive:

* Evidence remains based on an executed TestResult.
* Expected and actual behavior remain machine-readable.
* Evidence validation can independently confirm result consistency.
* Regression evidence uses the existing Evidence Framework.
* Evidence consistency is checked automatically.
* No duplicate evidence-generation mechanism is required.

Negative:

* The Evidence model remains limited to execution evidence.
* Security finding management and remediation tracking remain outside the
  Evidence Framework.

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

## ADR-022 — Phase 8 uses structured example findings as a documentation layer

**Status:** Accepted

**Phase:** 8

**Source:** [MASTER] + [INFERENCE]

Phase 8 introduces structured example security findings based on the existing
security-test and Evidence Framework results.

The finding documents are:

```text
05_examples/sample_finding_SEC-001.md
05_examples/sample_finding_SEC-002.md
```

SEC-001 documents the controlled authorization deviation identified by TC-001:

```text
Expected: ACCESS_DENIED
Actual:   ACCESS_GRANTED
Result:   FAIL
```

SEC-002 documents a validation assessment in which no security-relevant
deviation was reproduced in the defined TC-002 scenarios.

The finding documents reference existing test and evidence information but do
not modify the Evidence model.

### Rationale:

Phase 8 requires representative security findings that demonstrate how a
security-test observation can be documented with security requirement,
reproduction information, evidence, impact, root cause, recommendation,
fix, retest, and regression relationship.

The findings must remain traceable to the existing test architecture and
must not introduce unsupported claims about real automotive systems.

### Consequences:

Positive:

* Security-relevant observations can be documented in a structured format.
* SEC-001 provides a reproducible example of a controlled security finding.
* SEC-002 demonstrates that a test result without a reproduced deviation can
also be documented without inventing a vulnerability.
* Findings remain traceable to existing TC-001 and TC-002 test behavior.
* The existing Evidence Framework remains unchanged.

Negative:

* Finding documents are static project artifacts rather than a generalized
finding-management system.
* Finding identifiers, severity, root cause, remediation, and status are
documented at the example-finding layer and are not added to the Evidence
data model.
* Automated finding ingestion, historical finding tracking, and generalized
finding management remain outside Phase 8.

ADR-023 — Automated regression verifies both security behavior and evidence consistency

Status: Accepted

Phase: 9

Source: [SOURCE]

The automated security regression suite verifies not only the expected security behavior but also the correctness of the evidence generated from an executed regression scenario.

The regression implementation contains dedicated scenarios for:

* Unauthorized protected operation
* Authorized protected operation
* Invalid message
* Unsupported operation
* Boundary input
* Blocked ECU state
* Regression evidence

The evidence-specific scenario performs the following sequence:

```text
Execute secure regression scenario
        ↓
Obtain TestResult
        ↓
Generate Evidence
        ↓
Check evidence fields
        ↓
Evidence.validate()
```


The test explicitly verifies the evidence identity, target, preconditions, expected value, actual value, and result.

The final validation call:

```text
evidence.validate()

```

is therefore part of the automated regression test itself.

### Rationale:

Security regression testing should verify not only that the system under test produces the expected security response, 
but also that the resulting test evidence correctly represents that execution.
Without evidence validation, a test could produce a correct ECU result while recording incomplete or inconsistent evidence.
The existing Evidence Framework already provides the required validation mechanism, so no additional validation framework is introduced.

### Consequences:

Positive:

* Regression execution verifies established security properties automatically.
* Evidence generation is exercised by the automated regression suite.
* Evidence consistency is verified automatically.
* The test ID, target, execution preconditions, expected value, actual value, and result are checked.
* The existing Evidence Framework is reused without introducing a second evidence mechanism.
* Evidence becomes a verified output of the regression execution rather than only a documentation artifact.

Negative:

* The automated regression suite verifies the defined evidence structure and consistency but does not implement generalized evidence management.
* Historical evidence comparison, baseline management, finding ingestion, remediation tracking, and CI/CD artifact handling remain outside the current architecture.
* Evidence validation confirms consistency of the recorded test result; it does not by itself establish the existence or severity of a security vulnerability.

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
