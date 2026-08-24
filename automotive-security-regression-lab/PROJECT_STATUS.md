# Project Status

## Project

**Automotive Security Regression Lab**

**Project Vision:**  
**From Security Finding to Reproducible Automotive Security Tests**

---

## Current Phase

**Current Phase: Phase 4 — Evidence Framework**

**Status: In Progress — Verification and Quality Gate**

Phase 4 introduces the structured Evidence Framework that documents
security-test observations in a machine-readable and reproducible format.

The Evidence Framework is intentionally separated from the simulated ECU,
the test target, and the test execution mechanism.

---

## Completed Phases

- Phase 1 — Repository Foundation
- Phase 2 — ECU Simulation
- Phase 3 — Security Test Architecture

---

## Phase 4 Objective

Establish a structured Evidence Framework for documenting the outcome of
security-test executions.

The Evidence Framework provides a consistent representation of:

- test identity
- execution timestamp
- test target
- execution preconditions
- test input
- expected behavior
- actual observed behavior
- test result
- execution notes

The objective is to make security-test observations:

- structured
- reproducible
- machine-readable
- human-readable
- deterministic
- JSON-compatible
- suitable for later automation

The Evidence Framework forms the architectural bridge between:

```text
Security Test
      ↓
Test Result
      ↓
Evidence
      ↓
Security Finding
```

The Evidence layer documents the observation of a test execution.

It does not determine whether an observed failure constitutes a confirmed
security vulnerability.

---

## Phase 1 — Repository Foundation

Phase 1 established the repository foundation and project structure.

The repository foundation provides:

* Python project configuration
* pytest-based test execution
* source and test directory structure
* documentation structure
* project scope and boundaries
* deterministic local development environment

Phase 1 was implemented and verified locally.

---

## Phase 2 — ECU Simulation

Phase 2 implemented the fully simulated ECU test target.

The simulated ECU provides:

* secure security mode
* vulnerable security mode
* explicit authorization state
* protected operation handling
* request validation
* deterministic response statuses
* structured ECU responses

The simulated ECU does not implement a real CAN or UDS stack.

It does not communicate with real vehicles, ECUs, OEM systems, or
productive systems.

Phase 2 was implemented and verified locally.

### Phase 2 Test Coverage

The Phase-2 ECU test suite verifies:

1. secure mode denies unauthorized access
2. secure mode grants authorized access
3. vulnerable mode grants unauthorized access
4. unknown operations are rejected
5. invalid request input is rejected
6. invalid parameter structures are rejected

All defined Phase-2 ECU tests passed during the Phase-2 verification.

---

## Phase 3 — Security Test Architecture

Phase 3 introduced the security-test execution architecture that separates
security-test logic from the simulated ECU implementation.

The Phase-3 architecture provides:

* `SecurityTestCase`
* `SecurityTestRunner`
* `ECUTarget`
* `ECUAdapter`
* structured `TestResult`
* separation between test execution and ECU implementation

The architecture follows:

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
```

The ECU remains the system under test.

The Test Runner remains responsible for test execution.

The ECU Adapter provides the target boundary.

Evidence is introduced separately in Phase 4 and is not implemented inside
the ECU.

### Phase 3 Verification

The Phase-3 architecture was functionally verified through the following
test-runner scenarios:

| Test ID       | Scenario                         | Expected          | Actual            | Result |
| ------------- | -------------------------------- | ----------------- | ----------------- | ------ |
| `TC-ARCH-001` | Unauthorized protected operation | `ACCESS_DENIED`   | `ACCESS_DENIED`   | PASS   |
| `TC-ARCH-002` | Authorized protected operation   | `ACCESS_GRANTED`  | `ACCESS_GRANTED`  | PASS   |
| `TC-ARCH-003` | Invalid operation                | `INVALID_REQUEST` | `INVALID_REQUEST` | PASS   |

The complete Phase-3 pytest verification recorded:

```text
10 passed in 0.04s
```

Phase 3 is therefore retained as completed project history and is not
reinterpreted as part of the Phase-4 implementation.

---

# Phase 4 — Evidence Framework

## Phase 4 Scope

Phase 4 implements the structured Evidence Framework.

The central implementation is:

```text
03_src/security_lab/evidence.py
```

The corresponding framework tests are located in:

```text
04_tests/test_evidence.py
```

The Evidence Framework is designed to consume the result of an existing
Phase-3 test execution without coupling the ECU to evidence generation.

The intended data flow is:

```text
Security Test Case
        ↓
Security Test Runner
        ↓
ECU Adapter
        ↓
ECU Simulator
        ↓
Test Result
        ↓
Evidence Generator
        ↓
Evidence Model
        ↓
JSON
```

---

## Phase 4 Evidence Model

The Evidence model contains the following required data elements:

* `test_id`
* `timestamp`
* `target`
* `preconditions`
* `input`
* `expected`
* `actual`
* `result`
* `notes`

The evidence result is represented by:

* `PASS`
* `FAIL`

The implemented semantics are:

```text
PASS
Expected behavior == Actual behavior

FAIL
Expected behavior != Actual behavior
```

A `FAIL` evidence record means that the observed behavior did not match
the expected behavior.

A `FAIL` result is not, by itself, a confirmed security vulnerability.

Security findings, severity assessment, root-cause analysis, remediation,
and related activities remain outside the Phase-4 Evidence Framework.

---

## Phase 4 Evidence Validation

Evidence validation ensures that required evidence information is not
silently omitted.

The Evidence implementation validates:

* required identifying information
* target information
* preconditions structure
* expected behavior
* actual behavior
* result semantics
* consistency between expected and actual behavior

Invalid evidence records are rejected through the defined
`EvidenceValidationError`.

The validation model intentionally remains lightweight and does not
introduce an unnecessary external validation framework.

---

## Phase 4 Timestamp Handling

Evidence supports an automatically generated execution timestamp.

The implementation generates the timestamp at runtime using an
ISO-8601-compatible UTC representation.

Evidence tests do not depend on a fixed execution timestamp.

This keeps evidence generation suitable for repeated local test execution.

---

## Phase 4 JSON Serialization

Evidence can be serialized into a machine-readable JSON representation.

The serialization path is:

```text
Evidence Object
      ↓
to_dict()
      ↓
JSON-compatible representation
      ↓
to_json()
      ↓
JSON
```

The JSON representation contains the structured evidence fields and
represents the result value as `PASS` or `FAIL`.

---

## Phase 4 Test Coverage

The Evidence Framework tests cover the required Phase-4 scenarios:

1. valid evidence is accepted
2. missing required evidence fields are rejected
3. PASS evidence is accepted when expected behavior equals actual behavior
4. FAIL evidence is accepted when expected behavior differs from actual behavior
5. evidence can be serialized to JSON
6. evidence can be generated from a Phase-3 `SecurityTestCase` and `TestResult`

The tests are designed to remain:

* local
* deterministic
* hardware-independent
* network-independent
* independent of real ECU communication
* independent of external services

---

## Phase 4 Verification

The repository was verified using pytest collection and execution.

The current pytest collection contains:

```text
25 tests
```

The current test distribution is:

04_tests/test_ecu_simulator.py: 6
04_tests/test_evidence.py: 14
04_tests/test_foundation.py: 1
04_tests/test_test_runner.py: 4

The current verification command is:

```text
python -m pytest --collect-only -q
```

The collection result confirms that all currently implemented test modules
are discoverable by pytest.

The complete execution verification must be performed with:

```text
python -m pytest -q
```

Phase 4 must only be marked completed after the complete test suite has
returned a successful result.

No execution time is recorded here because it was not present in the
provided pytest output.

The Phase-4 Evidence Framework tests therefore have been executed as part
of the local pytest suite.

Further Phase-4 verification remains subject to the final repository,
documentation, architecture, red-team, and quality-gate review.

---

## Phase 4 Architectural Boundary

The Evidence Framework remains separate from the simulated ECU.

The ECU does not:

* create evidence
* serialize evidence
* generate test reports
* manage security findings

The Test Runner remains responsible for test execution.

The Evidence Framework consumes the resulting test information and creates
structured execution evidence.

This preserves the separation:

```text
ECU
→ System Under Test

Test Runner
→ Test Execution

Evidence
→ Test Execution Documentation
```

---

## Phase 4 Documentation

The Phase-4 documentation includes:

```text
docs/03_evidence-format.md
```

This document defines:

* Evidence purpose
* Evidence model
* required fields
* PASS / FAIL semantics
* JSON serialization
* complete evidence example
* distinction between evidence and security findings

The architecture documentation is updated to represent the Phase-4
evidence layer:

```text
Test Case
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
```

---

## Phase 4 Architecture Decision

Phase 4 introduces the architectural decision that security-test evidence
is represented as a structured data model and can be serialized to JSON.

The Evidence model is intentionally independent of the ECU implementation.

The corresponding architecture decision is recorded in:

```text
ARCHITECTURE_DECISIONS.md
```

The decision must remain consistent with the implemented Evidence model.

---

## Security Scope

The project remains fully simulated.

Phase 4 does not introduce:

* real vehicle communication
* real ECU communication
* real CAN communication
* real UDS communication
* OEM systems
* customer data
* productive credentials
* productive systems

The Evidence Framework documents simulated security-test executions only.

---

## Explicit Phase Boundaries

Phase 4 implements the Evidence Framework only.

The following capabilities are intentionally not implemented as part of
Phase 4:

* security finding management
* security finding IDs
* severity management
* CVSS calculation
* root-cause management
* customer security reports
* fix tracking
* retest workflow
* complete security regression suite
* CI/CD workflows
* end-to-end assessment
* real ECU communication

These capabilities belong to later project phases.

---

## Open Issues / Deferred Later Phases

The following project phases remain intentionally deferred:

* Phase 5 — TC-001 Diagnostic Authorization
* Phase 6 — TC-002 Message Validation
* Phase 7 — TC-003 Regression Workflow
* Phase 8 — Example Findings
* Phase 9 — pytest Regression Suite
* Phase 10 — CI/CD
* Phase 11 — End-to-End Assessment
* Phase 12 — Professional Documentation
* Phase 13 — Technical Review
* Phase 14 — Recruiter / Interview Review

No implementation from these later phases is included in Phase 4.

In particular, Phase 4 does not implement the Phase-9 regression suite,
Phase-10 CI/CD workflows, or Phase-8 security findings.

---

## Current Verification State

At the completion of the Phase-4 verification, the following capabilities
have been implemented and verified:

* Evidence data model: implemented and verified
* Required-field validation: implemented and verified
* PASS / FAIL semantics: implemented and verified
* Timestamp generation: implemented and verified
* JSON serialization: implemented and verified
* Evidence generation from Phase-3 test results: implemented and verified
* Evidence framework tests: passed
* Full pytest suite: passed
* Evidence documentation: reviewed
* Architecture documentation: reviewed
* Repository state: reviewed
* Phase-4 scope boundaries: reviewed

The current pytest suite contains:

```text
25 tests
```

Test distribution:

04_tests/test_ecu_simulator.py: 6
04_tests/test_evidence.py: 14
04_tests/test_foundation.py: 1
04_tests/test_test_runner.py: 4

Phase 4 can be marked completed only after the final technical,
documentation, architectural, and repository quality checks have passed.

---

## Next Phase

**Next Phase: Phase 5 — TC-001 Diagnostic Authorization**

Phase 5 must not be started automatically.

It may begin only after Phase 4 has passed its final verification,
technical review, documentation review, red-team review, and Quality Gate.