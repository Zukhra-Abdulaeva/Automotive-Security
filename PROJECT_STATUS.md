# Project Status

## Project

**Automotive Security Regression Lab**

**Project Vision:**  
From Security Finding to Reproducible Automotive Security Tests

---

## Current Status

**Current Phase:** Phase 7 — TC-003 Regression Workflow

**Status:** Implemented and locally verified

Phase 7 implements and verifies the defined TC-003 regression workflow for
the diagnostic authorization security property established by TC-001.

The current implementation provides:

- deterministic ECU simulation
- security-test abstraction
- structured test results
- Evidence Framework
- TC-001 Diagnostic Authorization
- TC-002 Message Validation
- TC-003 regression workflow verification
- controlled vulnerable-state reproduction
- secure retest of the same security condition
- regression evidence generation and validation
- authorized-behavior verification
- automated pytest verification

The project remains a local simulation. No real vehicle, ECU, CAN, UDS, OEM,
production, or external vehicle-network system is involved.

---

## Phase Status

| Phase | Description | Status |
|---|---|---|
| Phase 1 | Repository Foundation | Completed |
| Phase 2 | ECU Simulation | Completed |
| Phase 3 | Security Test Architecture | Completed |
| Phase 4 | Evidence Framework | Completed |
| Phase 5 | TC-001 Diagnostic Authorization | Completed |
| Phase 6 | TC-002 Message Validation | Completed |
| Phase 7 | TC-003 Regression Workflow | Implemented and verified |
| Phase 8 | Example Findings | Planned |
| Phase 9 | pytest Regression Suite | Planned |
| Phase 10 | CI/CD | Planned |
| Phase 11 | End-to-End Assessment | Planned |
| Phase 12 | Professional Documentation | Planned |
| Phase 13 | Technical Review | Planned |
| Phase 14 | Recruiter / Interview Review | Planned |

---

# Phase 1 — Repository Foundation

**Status: Completed**

Phase 1 established the project structure and local development baseline.

Implemented:

- Python project configuration
- pytest configuration
- repository structure
- initial documentation
- project scope definition
- architectural baseline
- deterministic local development environment

The project scope was defined as a controlled simulation environment.

---

# Phase 2 — ECU Simulation

**Status: Completed**

Phase 2 implemented the simulated ECU used as the system under test.

Implemented behavior includes:

- secure mode
- vulnerable mode
- authorization state
- protected operation
- request validation
- deterministic response statuses
- structured ECU responses

The simulator does not implement real CAN or UDS communication.

### Phase-2 Verification

The ECU test suite covers:

| Scenario | Expected behavior |
|---|---|
| Unauthorized protected operation in secure mode | `ACCESS_DENIED` |
| Authorized protected operation in secure mode | `ACCESS_GRANTED` |
| Unauthorized protected operation in vulnerable mode | `ACCESS_GRANTED` |
| Unknown operation | `UNSUPPORTED_OPERATION` |
| Invalid request input | `INVALID_REQUEST` |
| Invalid parameter structure | `INVALID_REQUEST` |

These tests provide the target behavior used by subsequent phases.

---

# Phase 3 — Security Test Architecture

**Status: Completed**

Phase 3 separated security-test execution from the simulated ECU.

The architecture introduced:

- `SecurityTestCase`
- `SecurityTestRunner`
- `TestResult`
- `ECUTarget`
- `ECUAdapter`

Execution path:

```text
SecurityTestCase
      ↓
SecurityTestRunner
      ↓
ECUTarget
      ↓
ECUAdapter
      ↓
ECUSimulator
      ↓
ECUResponse
      ↓
TestResult
```

The Test Runner communicates with the target through the `ECUTarget` abstraction and does not depend directly on the concrete ECU implementation.

### Phase-3 Verification

The architecture was verified with four scenarios:

| Test ID | Scenario | Expected | Actual | Result |
|---|---|---|---|---|
| `TC-ARCH-001` | Unauthorized protected operation | `ACCESS_DENIED` | `ACCESS_DENIED` | PASS |
| `TC-ARCH-002` | Authorized protected operation | `ACCESS_GRANTED` | `ACCESS_GRANTED` | PASS |
| `TC-ARCH-003` | Invalid operation | `UNSUPPORTED_OPERATION` | `UNSUPPORTED_OPERATION` | PASS |
| `TC-ARCH-004` | Vulnerable unauthorized operation | `ACCESS_GRANTED` | `ACCESS_GRANTED` | PASS |

---

# Phase 4 — Evidence Framework

**Status: Completed**

Phase 4 added structured evidence generation to the existing test architecture.

Primary implementation:

```text
03_src/security_lab/evidence.py
```

Evidence tests:

```text
04_tests/test_evidence.py
```

The data flow is:

```text
Security Test
      ↓
Test Result
      ↓
Evidence
      ↓
JSON
```

### Evidence Model

The Evidence model contains:

- `test_id`
- `timestamp`
- `target`
- `preconditions`
- `input`
- `expected`
- `actual`
- `result`
- `notes`

Supported result values:

```text
PASS
FAIL
```

Result semantics:

```text
PASS → expected == actual

FAIL → expected != actual
```

### Validation

The Evidence Framework validates:

- required identifying information
- target information
- preconditions
- expected behavior
- actual behavior
- result value
- expected/actual consistency

Invalid records raise:

```text
EvidenceValidationError
```

### Serialization

Evidence can be converted through:

```text
Evidence
   ↓
to_dict()
   ↓
JSON-compatible data
   ↓
to_json()
   ↓
JSON
```

The execution timestamp is generated at runtime using a UTC ISO-8601 representation.

---

# Phase 5 — TC-001 Diagnostic Authorization

**Status: Implemented and Verified**

Phase 5 introduces the first dedicated security test case.

```text
TC-001 — Diagnostic Authorization
```

### Security Requirement

```text
Protected diagnostic operations shall require authorization.
```

### Test Target

```text
PROTECTED_OPERATION
```

### Authorization States

```text
authorization = false

authorization = true
```

### Expected Secure Behavior

Unauthorized:

```text
authorization = false

        +

PROTECTED_OPERATION

        ↓

ACCESS_DENIED
```

Authorized:

```text
authorization = true

        +

PROTECTED_OPERATION

        ↓

ACCESS_GRANTED
```

The vulnerable ECU mode intentionally produces `ACCESS_GRANTED` for the unauthorized case. This is a controlled simulation of the security-relevant deviation tested by TC-001.

---

## Phase 5 — Message Validation Extension

The simulated ECU now distinguishes between invalid requests and unsupported operations.

The current response semantics are:

| Condition | Response |
|---|---|
| Request is not a mapping | `INVALID_REQUEST` |
| Operation is missing or empty | `INVALID_REQUEST` |
| Operation is not supported | `UNSUPPORTED_OPERATION` |
| Parameters are not a mapping | `INVALID_REQUEST` |
| Parameter value is outside `0..255` | `REQUEST_REJECTED` |
| Parameter value is a boolean | `REQUEST_REJECTED` |
| ECU is blocked | `REQUEST_REJECTED` |
| Valid protected operation without authorization | `ACCESS_DENIED` |
| Valid protected operation with authorization | `ACCESS_GRANTED` |

Parameter validation is explicitly limited to integer values from `0` through `255`. Python boolean values are excluded even though `bool` is a subclass of `int`.

The boundary behavior is:

| Input | Expected response |
|---:|---|
| `-1` | `REQUEST_REJECTED` |
| `0` | Valid parameter |
| `255` | Valid parameter |
| `256` | `REQUEST_REJECTED` |

This validation behavior is covered by the dedicated TC-002 message-validation tests.

---

## Phase-5 Implementation

The TC-001 test module is:

```text
04_tests/test_tc001_diagnostic_authorization.py
```

It uses the existing security-test infrastructure:

```text
03_src/security_lab/ecu_simulator.py

03_src/security_lab/ecu_adapter.py

03_src/security_lab/test_runner.py

03_src/security_lab/evidence.py
```

TC-001 does not bypass the target abstraction or modify the expected result to accommodate the vulnerable behavior.

---

## Phase-5 Scenarios

TC-001 covers four scenarios:

| Scenario | ECU Mode | Authorization | Operation | Expected |
|---|---|---:|---|---|
| Unauthorized access | Secure | `false` | `PROTECTED_OPERATION` | `ACCESS_DENIED` |
| Authorized access | Secure | `true` | `PROTECTED_OPERATION` | `ACCESS_GRANTED` |
| Unauthorized access | Vulnerable | `false` | `PROTECTED_OPERATION` | `ACCESS_GRANTED` |
| Invalid request | Controlled simulation | — | Invalid input | `INVALID_REQUEST` |

The vulnerable scenario is evaluated against the security requirement:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_GRANTED
```

This produces:

```text
FAIL
```

when represented as security-test evidence.

The `FAIL` represents the observed mismatch. It is not a formal vulnerability classification or severity assessment.

---

# Phase-5 Test Architecture

TC-001 uses the architecture established in Phases 3 and 4:

```text
TC-001
  ↓
SecurityTestCase
  ↓
SecurityTestRunner
  ↓
ECUAdapter
  ↓
ECUSimulator
  ↓
ECUResponse
  ↓
TestResult
  ↓
Evidence
```

Responsibilities remain separated:

| Component | Responsibility |
|---|---|
| `ECUSimulator` | Simulated ECU behavior |
| `ECUAdapter` | Target boundary |
| `SecurityTestRunner` | Test execution and evaluation |
| `TestResult` | Evaluated test outcome |
| Evidence Framework | Structured execution evidence |
| TC-001 | Security-test definition |

---

# Phase-5 Retest Model

TC-001 is designed to support retesting after a simulated security fix.

The intended workflow is:

```text
Vulnerable Behavior

      ↓

Test Observation

      ↓

Evidence

      ↓

Simulated Fix

      ↓

Same TC-001

      ↓

Retest
```

The security requirement and expected result remain unchanged during retest.

For the unauthorized case, the expected result remains:

```text
ACCESS_DENIED
```

A corrected implementation must therefore satisfy:

```text
authorization = false

+

PROTECTED_OPERATION

↓

ACCESS_DENIED
```

The test itself is not weakened to accommodate an insecure implementation.

---

## TC-001 Verification

TC-001 is verified through four pytest tests covering:

- secure unauthorized behavior
- secure authorized behavior
- controlled vulnerable behavior
- machine-readable vulnerable evidence

The TC-001 test module is:

```text
04_tests/test_tc001_diagnostic_authorization.py
```

The expected verification result is:

```text
4 passed
```

---

## Phase 6 — TC-002 Message Validation

**Status: Implemented and Verified**

Phase 6 introduces the second dedicated security test case.

```text
TC-002 — Message Validation
```

TC-002 verifies deterministic request and parameter validation within the simulated ECU.

The test case distinguishes invalid requests, unsupported operations, rejected parameter values, unexpected ECU states, and valid boundary values.

### Response Semantics

The current response semantics are:

| Condition | Response |
|---|---|
| Request is not a mapping | `INVALID_REQUEST` |
| Operation is missing or empty | `INVALID_REQUEST` |
| Operation is not supported | `UNSUPPORTED_OPERATION` |
| Parameters are not a mapping | `INVALID_REQUEST` |
| Parameter value is outside `0..255` | `REQUEST_REJECTED` |
| Parameter value is a boolean | `REQUEST_REJECTED` |
| ECU is blocked | `REQUEST_REJECTED` |
| Valid protected operation without authorization | `ACCESS_DENIED` |
| Valid protected operation with authorization | `ACCESS_GRANTED` |

Parameter validation is explicitly limited to integer values from 0 through 255. Python boolean values are excluded even though `bool` is a subclass of `int`.

### Boundary Behavior

| Input | Expected response |
|---:|---|
| `-1` | `REQUEST_REJECTED` |
| `0` | Valid parameter |
| `255` | Valid parameter |
| `256` | `REQUEST_REJECTED` |

This validation behavior is covered by the dedicated TC-002 message-validation tests.

### Phase-6 Implementation

The TC-002 test module is:

```text
04_tests/test_tc002_message_validation.py
```

TC-002 uses the existing ECU simulation and security-test infrastructure. The tests evaluate the actual ECU response against the defined expected response status.

The test case does not bypass the ECU interface or directly manipulate the expected result.

### Phase-6 Scenarios

TC-002 covers four primary validation scenarios:

| Test ID | Scenario | Expected |
|---|---|---|
| TC-002-A | Invalid input | `INVALID_REQUEST` |
| TC-002-B | Unsupported operation | `UNSUPPORTED_OPERATION` |
| TC-002-C | Boundary condition | `REQUEST_REJECTED` |
| TC-002-D | Unexpected ECU state | `REQUEST_REJECTED` |

The dedicated test suite additionally verifies that the valid parameter boundary values 0 and 255 are accepted for the protected operation.

### TC-002 Verification

TC-002 is implemented and locally verified.

The dedicated test module is:

```text
04_tests/test_tc002_message_validation.py
```

The dedicated verification was executed with:

```text
pytest -q 04_tests/test_tc002_message_validation.py
```

Result:

```text
5 passed
```

The complete test suite was subsequently executed with:

```text
pytest -q
```

Result:

```text
34 passed
```

TC-002 verifies deterministic request validation, including unsupported operations, invalid parameter structures, valid parameter boundaries, out-of-range values, unexpected ECU state, and boolean exclusion.

---

# Phase 7 — TC-003 Regression Workflow

**Status: Implemented and locally verified**

Phase 7 implements the defined regression workflow for the diagnostic
authorization security property established by TC-001.

The implementation is contained in:

```text
04_tests/test_security_regression.py
```

The verified workflow covers:

```text
Controlled vulnerable behavior
        ↓
Original security condition
        ↓
Secure retest
        ↓
Expected vs actual evaluation
        ↓
Structured evidence
        ↓
Evidence validation
        ↓
Authorized behavior verification
```

The four TC-003 test functions verify:

| Test | Purpose |
|---|---|
| `test_tc003_reproduces_original_vulnerable_behavior` | Demonstrates the controlled pre-fix behavior in `SecurityMode.VULNERABLE` |
| `test_tc003_retest_confirms_secure_behavior` | Verifies that the same unauthorized condition is denied in `SecurityMode.SECURE` |
| `test_tc003_regression_evidence_matches_retest_result` | Verifies that generated Evidence represents the executed secure retest |
| `test_tc003_regression_preserves_authorized_behavior` | Verifies that authorized protected access remains available |

The first test intentionally observes:

```text
Expected: ACCESS_DENIED
Actual:   ACCESS_GRANTED
Result:   FAIL
```

The pytest assertion verifies that this controlled vulnerable result is correctly recognized as a failed security test.

The test itself passes because it is a lifecycle demonstration of the expected pre-fix deviation.

The secure regression condition verifies:

```text
Authorization: false
Operation:     PROTECTED_OPERATION
Expected:      ACCESS_DENIED
Actual:        ACCESS_DENIED
Result:        PASS
```

The authorized functional condition verifies:

```text
Authorization: true
Operation:     PROTECTED_OPERATION
Expected:      ACCESS_GRANTED
Actual:        ACCESS_GRANTED
Result:        PASS
```

The current Phase-7 implementation does not provide generalized finding management, automatic finding ingestion, automatic test generation, automatic regression registration, historical result comparison, or regression orchestration.

---

## Complete Test Suite

The complete suite was executed from:

```text
04_tests
```

with:

```text
pytest -q
```

Result:

```text
38 passed
```

Current test distribution:

```text
04_tests/test_ecu_simulator.py: 6

04_tests/test_evidence.py: 14

04_tests/test_foundation.py: 1

04_tests/test_test_runner.py: 4

04_tests/test_tc001_diagnostic_authorization.py: 4

04_tests/test_tc002_message_validation.py: 5

04_tests/test_security_regression.py: 4
```

Total:

```text
38 tests
```

The complete suite verifies that the current implementation integrates the ECU simulation, security-test architecture, Evidence Framework, TC-001, TC-002, and TC-003 without regressions.

The test count reflects the current repository state and is not treated as a permanent project invariant.

---

# Current Quality Gate

Phase 7 verification confirms:

* TC-001 is implemented and verified
* TC-002 is implemented and verified
* TC-003 regression workflow tests are implemented and verified
* 4 TC-001 tests pass
* 5 TC-002 tests pass
* 4 TC-003 regression workflow tests pass
* the complete pytest suite passes
* all 38 current tests pass
* Phase-2 ECU tests remain passing
* Phase-3 architecture tests remain passing
* Phase-4 Evidence tests remain passing
* secure authorization behavior remains enforced
* controlled vulnerable authorization behavior remains reproducible
* the secure retest confirms `ACCESS_DENIED` for unauthorized protected access
* authorized protected access remains available
* regression evidence is generated and validated
* expected and actual evidence values remain consistent
* unsupported operations are distinguished from invalid requests
* parameter boundary validation is enforced
* boolean parameter values are rejected
* no real automotive communication was introduced

**Current result: Phase-7 implementation, verification, and testing complete.**

Remaining activity:

* documentation consistency review
* repository quality review

---

# Current Repository Capabilities

The repository currently provides:

```text
ECU Simulation
      ↓
Security Test Architecture
      ↓
Evidence Framework
      ↓
TC-001 Diagnostic Authorization
      ↓
TC-002 Message Validation
      ↓
TC-003 Regression Workflow Verification
      ↓
Automated Verification
```

The current implementation supports:

* structured evidence
* JSON evidence serialization
* abstract target communication
* automated pytest verification
* security requirement verification
* expected-versus-actual evaluation
* deterministic local ECU simulation
* controlled vulnerable-state testing
* secure retest execution
* regression evidence generation
* regression evidence validation
* preservation of authorized behavior
* deterministic request and parameter validation
* explicit response semantics for unsupported operations and rejected requests

---

# Security and Scope Boundary

The project is limited to local simulation.

It does not provide:

* real vehicle communication
* real ECU communication
* real CAN communication
* real UDS communication
* vehicle-network interaction
* OEM integration
* customer-data processing
* productive credentials
* production-system access
* unauthorized security testing

The vulnerable ECU mode is a local test condition and does not represent a claim about an actual vehicle, ECU, OEM system, or production environment.

---

# Deferred Work

The following capabilities are not implemented in the current phase:

* generalized security finding management
* example security findings
* generalized root-cause management
* remediation tracking
* generalized regression orchestration
* CI/CD integration
* end-to-end assessment
* professional documentation package
* technical review
* recruiter / interview review

Planned sequence:

```text
Phase 8  → Example Findings
Phase 9  → pytest Regression Suite
Phase 10 → CI/CD
Phase 11 → End-to-End Assessment
Phase 12 → Professional Documentation
Phase 13 → Technical Review
Phase 14 → Recruiter / Interview Review
```

---

# Documentation References

| Document | Purpose |
|---|---|
| `README.md` | Project overview, scope, architecture, and development phases |
| `PROJECT_STATUS.md` | Current implementation and verification status |
| `ARCHITECTURE_DECISIONS.md` | Architectural decisions and rationale |
| `docs/01_architecture.md` | Detailed architecture |
| `docs/02_methodology.md` | Security-testing methodology |
| `docs/03_evidence-format.md` | Evidence Framework and evidence format |
| `docs/04_end-to-end-assessment-case.md` | End-to-end assessment structure |
| `01_threat_model/01_attack_surface.md` | Modeled attack surface |
| `02_test_cases/TC-001-diagnostic-authorization.md` | TC-001 security-test specification |
| `02_test_cases/TC-002-message-validation.md` | TC-002 security-test specification |

---

# Next Phase

**Phase 8 — Example Findings**
