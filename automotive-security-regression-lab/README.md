````markdown
# Automotive Security Regression Lab

**From Security Finding to Reproducible Automotive Security Tests**

## Project

The **Automotive Security Regression Lab** is a local, deterministic simulation environment for developing and demonstrating an automotive cybersecurity testing workflow.

The project models how a security requirement can be translated into a security test, executed against a simulated ECU, evaluated against expected behavior, and captured as structured evidence.

The laboratory does not connect to real vehicles, ECUs, vehicle networks, OEM infrastructure, or production systems. No real CAN or UDS communication is implemented.

The project is an engineering demonstration. It does not claim professional penetration-testing experience, real-world ECU assessment experience, or production cybersecurity validation.

---

# Project Vision

The long-term workflow is:

```text
Security Requirement
        ↓
Threat Model
        ↓
Attack Hypothesis
        ↓
Security Test
        ↓
Evidence
        ↓
Security Finding
        ↓
Root Cause
        ↓
Fix
        ↓
Retest
        ↓
Regression Test
        ↓
CI/CD
```

The current implementation covers the following part of this workflow:

```text
Security Requirement
        ↓
Security Test Case
        ↓
Test Execution
        ↓
ECU Response
        ↓
Test Result
        ↓
Structured Evidence
```

The project is developed incrementally. Each phase adds functionality on top of the previously verified architecture.

---

# Current Phase

## Phase 7 — TC-003 Regression Workflow

**Status: Implemented and locally verified**

Phase 7 extends the verified TC-001 and TC-002 security-test architecture with a controlled regression workflow for the diagnostic authorization security property.

The implementation is provided by:

```text
04_tests/test_security_regression.py
```

The verified lifecycle is:

```text
Controlled Vulnerable Behavior
        ↓
Original Security Condition
        ↓
Secure Retest
        ↓
Expected vs Actual
        ↓
Regression Evidence
        ↓
Evidence Validation
        ↓
Authorized Behavior Verification
```

TC-003 reuses the existing TC-001 security-test definition. The pytest functions are named `test_tc003_*`, while the underlying `SecurityTestCase.test_id` remains `TC-001`.

This reflects the architectural distinction between the TC-003 workflow and the TC-001 security property being regression-tested.

---

# What Phase 7 Adds

Phase 7 verifies the following regression workflow:

1. reproduce the controlled vulnerable behavior
2. preserve the original security expectation
3. execute the same unauthorized condition against the secure ECU
4. compare expected and actual behavior through `SecurityTestRunner`
5. generate structured Evidence from the executed `TestResult`
6. validate the generated Evidence
7. verify that authorized protected behavior remains functional

The controlled vulnerable-state demonstration produces:

```text
Expected: ACCESS_DENIED
Actual:   ACCESS_GRANTED
TestResult: FAIL
```

This is intentional. The pytest test verifies that the security deviation is correctly detected.

The secure regression retest produces:

```text
Expected: ACCESS_DENIED
Actual:   ACCESS_DENIED
TestResult: PASS
```

The authorized functional check produces:

```text
Expected: ACCESS_GRANTED
Actual:   ACCESS_GRANTED
TestResult: PASS
```

Phase 7 therefore demonstrates the regression lifecycle within the existing deterministic simulation architecture.

It does not implement generalized security finding management, automatic finding ingestion, automatic regression-test generation, historical result comparison, or CI/CD orchestration.

---

# TC-001 Security Scenario

TC-001 models a diagnostic requester attempting to execute a protected operation.

```text
Diagnostic Interface
        ↓
Protected Operation
        ↓
Authorization Check
        ↓
Response
```

The interface is entirely simulated. The scenario does not require a real diagnostic protocol, vehicle network, ECU, CAN bus, or UDS implementation.

---

# TC-001 Threat Model

### Asset

**Protected Diagnostic Operation**

### Threat

Unauthorized execution of a protected diagnostic operation.

### Potential Attacker

Unauthorized diagnostic client.

### Security Property

Authorization must be enforced before the protected operation is granted.

### Security Assumption

The simulated ECU is responsible for enforcing authorization for the protected operation.

The threat model is intentionally limited to the behavior represented by the simulator.

---

# TC-001 Attack Hypothesis

The test hypothesis is:

> If authorization is missing or incorrectly enforced, an unauthorized diagnostic requester may be able to execute a protected operation.

TC-001 evaluates this hypothesis using:

```text
authorization = false
PROTECTED_OPERATION
```

The expected secure response is:

```text
ACCESS_DENIED
```

The vulnerable simulation produces:

```text
ACCESS_GRANTED
```

The authorized positive case is also verified:

```text
authorization = true
PROTECTED_OPERATION
        ↓
ACCESS_GRANTED
```

---

# TC-001 Test Architecture

TC-001 uses the architecture established in Phases 3 and 4.

```text
TC-001
  ↓
SecurityTestRunner
  ↓
ECUAdapter
  ↓
ECUSimulator
  ↓
ECU Response
  ↓
TestResult
  ↓
Evidence
```

The test does not access internal ECU implementation details directly.

The responsibilities are separated as follows:

| Component | Responsibility |
| --- | --- |
| `SecurityTestCase` | Defines the security scenario and expected behavior |
| `SecurityTestRunner` | Executes the test and evaluates expected vs. actual behavior |
| `ECUTarget` | Defines the target interface |
| `ECUAdapter` | Connects the target interface to the simulator |
| `ECUSimulator` | Implements the simulated ECU behavior |
| `TestResult` | Represents the evaluated execution result |
| `Evidence` | Records structured execution evidence |

This keeps the security test independent from the concrete ECU implementation.

---

# TC-001 Test Scenarios

TC-001 contains four verification scenarios:

| Scenario | ECU Mode | Authorization | Operation | Expected Result |
| --- | --- | ---: | --- | --- |
| Unauthorized access | Secure | `false` | `PROTECTED_OPERATION` | `ACCESS_DENIED` |
| Authorized access | Secure | `true` | `PROTECTED_OPERATION` | `ACCESS_GRANTED` |
| Vulnerable unauthorized access | Vulnerable | `false` | `PROTECTED_OPERATION` | `ACCESS_GRANTED` |
| Invalid request | Controlled simulation | — | Invalid operation/input | `INVALID_REQUEST` |

The third scenario is the security-relevant case.

When evaluated against the security requirement, it produces:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_GRANTED
Result   = FAIL
```

The test therefore detects the modeled authorization deviation.

---

# Secure ECU Behavior

The secure simulator enforces authorization before granting the protected operation.

Unauthorized:

```text
Authorization = false
        ↓
PROTECTED_OPERATION
        ↓
ACCESS_DENIED
```

Authorized:

```text
Authorization = true
        ↓
PROTECTED_OPERATION
        ↓
ACCESS_GRANTED
```

The security test verifies this behavior through the target abstraction.

The expected result is derived from the security requirement and is not changed to match the implementation.

---

# Controlled Vulnerable ECU Behavior

The vulnerable simulator intentionally omits effective authorization enforcement for the protected operation.

```text
Authorization = false
        ↓
PROTECTED_OPERATION
        ↓
ACCESS_GRANTED
```

This provides a deterministic security-test condition.

The vulnerable mode is used to demonstrate:

* expected-versus-actual comparison
* security-relevant test failure
* structured evidence
* security observation
* later retesting

It does not represent a real vulnerable vehicle, ECU, or production system.

---

# Evidence Integration

Phase 4 introduced the Evidence Framework used by TC-001.

The execution path is:

```text
TC-001
  ↓
TestResult
  ↓
Evidence
```

A vulnerable TC-001 execution can be represented as:

```json
{
  "test_id": "TC-001",
  "target": "simulated-ecu",
  "preconditions": {
    "authorization": false
  },
  "input": "PROTECTED_OPERATION",
  "expected": "ACCESS_DENIED",
  "actual": "ACCESS_GRANTED",
  "result": "FAIL",
  "notes": "Protected operation was accepted without authorization."
}
```

The timestamp is generated by the Evidence Framework during execution.

Evidence records the observation. It does not by itself constitute a formal security finding.

---

# Evidence Semantics

The Evidence Framework evaluates the relationship between expected and actual behavior:

```text
PASS
Expected behavior == Actual behavior

FAIL
Expected behavior != Actual behavior
```

For the vulnerable TC-001 scenario:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_GRANTED
```

the resulting evidence state is:

```text
FAIL
```

This means that the observed behavior does not satisfy the expected security behavior.

It does not independently assign vulnerability severity, CVSS, customer impact, or production vulnerability status.

---

# TC-001 Security Observation

The vulnerable execution demonstrates the following deviation:

```text
Unauthorized request
        ↓
Protected operation accepted
        ↓
Expected authorization control not enforced
```

The modeled security requirement is:

> **Protected diagnostic operations shall require authorization.**

Therefore:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_GRANTED
```

is a security-relevant deviation.

Phase 5 does not assign a formal vulnerability identifier or severity.

The following remain outside the current implementation:

* CVSS
* formal vulnerability classification
* customer impact assessment
* production impact assessment
* security finding management

---

# TC-001 Root Cause Model

For the controlled vulnerable simulator, the modeled root cause is:

> **The authorization state is not enforced before the protected operation is granted.**

This describes the behavior implemented by the simulator.

It is not intended as a root-cause claim about a real ECU.

---

# TC-001 Fix Model

The corrective behavior is implemented in the simulated ECU.

The required control flow is:

```text
Authorization Decision
        ↓
Protected Operation
```

Unauthorized:

```text
authorization = false
PROTECTED_OPERATION
        ↓
ACCESS_DENIED
```

Authorized:

```text
authorization = true
PROTECTED_OPERATION
        ↓
ACCESS_GRANTED
```

The security test is not weakened to make the implementation pass.

The security requirement and expected result remain unchanged.

---

# TC-001 Retest Model

After correcting the simulated ECU behavior, the same TC-001 test case can be executed again.

```text
Vulnerable Behavior
        ↓
Evidence
        ↓
Simulated Fix
        ↓
Same TC-001
        ↓
Retest
        ↓
Secure Behavior
```

The important regression principle is that the original security test remains unchanged.

The system under test is corrected, and the existing test is reused to determine whether the security requirement is now satisfied.

Phase 7 implements this lifecycle as a controlled regression workflow through TC-003.

---

# Phase History

## Phase 1 — Repository Foundation

Established:

* Python project configuration
* pytest configuration
* repository structure
* documentation structure
* project scope
* initial architectural decisions
* deterministic local development environment

---

## Phase 2 — ECU Simulation

Implemented the deterministic simulated ECU with:

* secure mode
* vulnerable mode
* authorization state
* protected operation handling
* request validation
* deterministic response statuses
* structured ECU responses

The simulator does not implement a real CAN or UDS stack.

### Phase 2 Test Coverage

The ECU tests verify:

1. secure mode denies unauthorized access
2. secure mode grants authorized access
3. vulnerable mode grants unauthorized access
4. unknown operations are rejected
5. invalid request input is rejected
6. invalid parameter structures are rejected

---

## Phase 3 — Security Test Architecture

Introduced:

* `SecurityTestCase`
* `SecurityTestRunner`
* `TestResult`
* `ECUTarget`
* `ECUAdapter`

The resulting execution path is:

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

The runner communicates with the target through `ECUTarget` instead of depending directly on `ECUSimulator`.

### Phase 3 Verification

| Test ID | Scenario | Expected | Actual | Result |
| --- | --- | --- | --- | --- |
| `TC-ARCH-001` | Unauthorized protected operation | `ACCESS_DENIED` | `ACCESS_DENIED` | PASS |
| `TC-ARCH-002` | Authorized protected operation | `ACCESS_GRANTED` | `ACCESS_GRANTED` | PASS |
| `TC-ARCH-003` | Invalid operation | `INVALID_REQUEST` | `INVALID_REQUEST` | PASS |
| `TC-ARCH-004` | Vulnerable unauthorized protected operation | `ACCESS_GRANTED` | `ACCESS_GRANTED` | PASS |

---

## Phase 4 — Evidence Framework

Introduced the structured Evidence Framework.

Primary implementation:

```text
03_src/security_lab/evidence.py
```

Framework tests:

```text
04_tests/test_evidence.py
```

The data flow is:

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

The Evidence model contains:

* `test_id`
* `timestamp`
* `target`
* `preconditions`
* `input`
* `expected`
* `actual`
* `result`
* `notes`

Supported result states:

```text
PASS
FAIL
```

Evidence validation rejects invalid or incomplete records through:

```text
EvidenceValidationError
```

Evidence also supports runtime timestamp generation and JSON serialization through the existing `to_dict()` and `to_json()` interfaces.

---

## Phase 5 — TC-001 Diagnostic Authorization

Introduced:

* `TC-001 — Diagnostic Authorization`
* secure unauthorized scenario
* secure authorized scenario
* controlled vulnerable unauthorized scenario
* invalid-request scenario
* automated TC-001 tests
* integration with the Phase-3 test architecture
* integration with the Phase-4 Evidence Framework
* a defined simulated fix/retest model

---

## Phase 6 — TC-002 Message Validation

Introduced:

* `TC-002 — Message Validation`
* deterministic message parameter validation
* valid boundary values `0` and `255`
* rejection of values below `0`
* rejection of values above `255`
* rejection of boolean values despite Python's `bool`/`int` relationship
* explicit `UNSUPPORTED_OPERATION` response semantics
* explicit `REQUEST_REJECTED` response semantics
* ECU operational states `READY` and `BLOCKED`
* blocked-state request rejection
* automated TC-002 verification
* integration with the existing security-test architecture

TC-002 verifies that a protected operation accepts only valid message parameters and rejects values outside the defined parameter range.

The implemented parameter range is:

```text
0 <= value <= 255
```

Boundary behavior:

```text
-1    → REQUEST_REJECTED
0     → accepted
255   → accepted
256   → REQUEST_REJECTED
```

Boolean values are rejected explicitly because Python treats bool as a subclass of int.

Unknown operations are classified as:

```text
UNSUPPORTED_OPERATION
```

Structurally invalid requests remain classified as:

```text
INVALID_REQUEST
```

A request that is structurally valid but violates a defined parameter or ECU-state constraint is classified as:

```text
REQUEST_REJECTED
```

---

## Phase 7 — TC-003 Regression Workflow

Introduced:

* `TC-003 — Regression Workflow`
* controlled vulnerable-state reproduction
* reuse of the existing TC-001 security-test definition
* secure regression retest of the original authorization condition
* expected-versus-actual evaluation through `SecurityTestRunner`
* structured regression evidence generation
* regression evidence validation
* authorized protected-behavior verification
* automated TC-003 regression workflow tests

The implementation is provided by:

```text
04_tests/test_security_regression.py
```

TC-003 uses the existing TC-001 security property as the regression condition rather than redefining the security requirement.

The lifecycle is:

```text
Controlled Vulnerable Behavior
        ↓
Original Security Condition
        ↓
Secure Retest
        ↓
Expected vs Actual
        ↓
Regression Evidence
        ↓
Evidence Validation
        ↓
Authorized Behavior Verification
```

The vulnerable-state test intentionally produces a failing `TestResult` because the controlled vulnerable ECU returns `ACCESS_GRANTED` where `ACCESS_DENIED` is expected.

The pytest test itself passes because it verifies that the security deviation is correctly detected.

---

# Current Architecture

The current architecture combines the verified capabilities of Phases 1–7:

```text
Security Requirement
        ↓
Threat Model
        ↓
Attack Hypothesis
        ↓
Security Test Case
        ↓
Security Test Runner
        ↓
ECUTarget
        ↓
ECUAdapter
        ↓
Simulated ECU
        ↓
ECU Response
        ↓
TestResult
        ↓
Evidence
        ↓
TC-003 Regression Workflow
```

The implementation separates the security requirement, test definition, execution mechanism, target implementation, and evidence representation.

TC-003 extends the existing execution and evidence architecture without introducing a generalized regression-orchestration layer.

---

# Architectural Principles

## Separate the security test from the system under test

```text
Security Test
      ↓
Test Runner
      ↓
ECU Adapter
      ↓
Security Target
```

The test runner does not depend directly on the concrete ECU implementation.

---

## Separate execution from evidence

```text
Test Execution
      ↓
Test Result
      ↓
Evidence
```

Evidence records execution results without controlling ECU behavior.

---

## Keep the simulated ECU deterministic

```text
Same Input
    +
Same ECU State
    ↓
Same Security Decision
```

The secure and vulnerable simulator modes are both deterministic.

---

## Keep the security requirement separate from the test implementation

The requirement is:

```text
Protected diagnostic operations shall require authorization.
```

TC-001 verifies that requirement.

TC-003 reuses the TC-001 security condition for regression verification.

The expected result must not be changed simply because the implementation currently behaves differently.

---

## Fix the system under test, not the security test

A security-relevant deviation is corrected in the simulated ECU.

The original test remains the verification mechanism for the security property.

TC-003 then reuses that security condition to verify the secure behavior.

---

# Verification

The current repository has been locally verified with the complete pytest suite.

Latest complete execution:

```text
pytest -q
```

Result:

```text
38 passed
```

The dedicated TC-003 regression workflow module was also executed independently:

```text
pytest -q 04_tests/test_security_regression.py
```

Result:

```text
.... [100%]

4 passed
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

The test count reflects the current repository state and is not treated as a permanent project invariant.

---

# Testing Philosophy

Automated tests verify both the simulated security target and the security-test infrastructure.

The current verification layers are:

```text
ECU Simulation Tests
        ↓
Security Test Architecture Tests
        ↓
Evidence Framework Tests
        ↓
TC-001 Security Test
        ↓
TC-002 Security Tests
        ↓
TC-003 Regression Workflow Tests
        ↓
Complete pytest Suite
```

Testing the infrastructure itself helps identify regressions in the mechanisms used to execute and evaluate security tests.

---

# Repository Structure

```text
automotive-security-regression-lab/

├── README.md
├── PROJECT_STATUS.md
├── ARCHITECTURE_DECISIONS.md
├── pyproject.toml
├── .gitattributes
├── .gitignore
│
├── docs/
│   ├── .gitkeep
│   ├── 01_architecture.md
│   ├── 02_methodology.md
│   ├── 03_evidence-format.md
│   └── 04_end-to-end-assessment-case.md
│
├── 01_threat_model/
│   ├── .gitkeep
│   └── 01_attack_surface.md
│
├── 02_test_cases/
│   ├── .gitkeep
│   ├── TC-001-diagnostic-authorization.md
│   ├── TC-002-message-validation.md
│   └── TC-003-regression-workflow.md
│
├── 03_src/
│   └── security_lab/
│       ├── __init__.py
│       ├── ecu_simulator.py
│       ├── ecu_adapter.py
│       ├── evidence.py
│       └── test_runner.py
│
├── 04_tests/
│   ├── .gitkeep
│   ├── test_ecu_simulator.py
│   ├── test_evidence.py
│   ├── test_foundation.py
│   ├── test_test_runner.py
│   ├── test_tc001_diagnostic_authorization.py
│   ├── test_tc002_message_validation.py
│   └── test_security_regression.py
│
├── 05_examples/
│   └── .gitkeep
│
└── .github/
    └── workflows/
        └── .gitkeep
```

The `.gitkeep` files only preserve otherwise empty directories in Git. They contain no project logic.

---

# Technology Baseline

The project currently uses:

* Python
* pytest
* Python standard library components where practical

The implementation intentionally keeps runtime dependencies small.

The laboratory is:

* locally executable
* deterministic
* hardware-independent
* network-independent
* reproducible

---

# Security Scope and Safety Boundary

The laboratory is fully simulated and runs locally.

It does not:

* connect to real vehicles or ECUs
* send traffic to vehicle networks
* interact with OEM infrastructure
* access customer data
* use production credentials
* interact with production systems
* perform unauthorized security testing
* implement real CAN communication
* implement real UDS communication

The vulnerable ECU mode is a controlled test condition within the simulator.

It must not be interpreted as evidence of a vulnerability in a real vehicle, ECU, OEM system, or production environment.

---

# Phase Boundaries

Phase 7 includes the TC-003 Regression Workflow in addition to the previously verified TC-001 Diagnostic Authorization and TC-002 Message Validation tests.

The current regression implementation is specific to the diagnostic authorization security property established by TC-001.

The following capabilities are not part of the current implementation:

* generalized security finding management
* automatic finding ingestion
* formal vulnerability classification
* severity management
* CVSS calculation
* customer security reporting
* production impact assessment
* generalized root-cause management
* generalized remediation tracking
* automatic regression-test generation
* historical result comparison
* generalized regression orchestration
* CI/CD workflows
* real ECU communication
* real CAN communication
* real UDS communication
* real vehicle-network interaction

These capabilities are reserved for later phases.

---

# Current Project Status

### Implemented

**Phase 1**

* repository foundation
* Python project configuration
* pytest-based verification
* documentation structure
* project scope

**Phase 2**

* deterministic ECU simulation
* secure mode
* vulnerable mode
* authorization state
* protected operation
* request validation
* structured responses

**Phase 3**

* `SecurityTestCase`
* `SecurityTestRunner`
* `TestResult`
* `ECUTarget`
* `ECUAdapter`
* separation between test execution and ECU implementation

**Phase 4**

* structured Evidence model
* required-field validation
* PASS / FAIL semantics
* timestamp generation
* JSON serialization
* evidence generation from test execution

**Phase 5**

* `TC-001 — Diagnostic Authorization`
* secure unauthorized scenario
* secure authorized scenario
* controlled vulnerable unauthorized scenario
* invalid-request scenario
* automated TC-001 tests
* integration with the existing test architecture
* integration with the Evidence Framework
* simulated fix/retest model

**Phase 6**

* `TC-002 — Message Validation`
* deterministic message parameter validation
* valid boundary values `0` and `255`
* rejection of values below `0`
* rejection of values above `255`
* rejection of boolean values
* explicit `UNSUPPORTED_OPERATION` response semantics
* explicit `REQUEST_REJECTED` response semantics
* ECU operational states `READY` and `BLOCKED`
* blocked-state request rejection
* automated TC-002 verification

**Phase 7**

* `TC-003 — Regression Workflow`
* controlled vulnerable-state reproduction
* reuse of TC-001 as the original security condition
* secure regression retest
* expected-versus-actual evaluation
* regression evidence generation
* regression evidence validation
* authorized-behavior verification
* automated TC-003 workflow tests

---

# Current Verification State

The latest complete local verification reports:

```text
38 passed
```

The verified scope is:

```text
Phase 2 ECU Simulation
        +
Phase 3 Security Test Architecture
        +
Phase 4 Evidence Framework
        +
Phase 5 TC-001
        +
Phase 6 TC-002
        +
Phase 7 TC-003
        ↓
Complete pytest Verification
```

The implementation remains fully local and deterministic.

The current verified regression behavior includes:

```text
Controlled Vulnerable State
        ↓
ACCESS_GRANTED without authorization
        ↓
Security TestResult = FAIL
        ↓
Secure Retest
        ↓
ACCESS_DENIED without authorization
        ↓
Security TestResult = PASS
```

Authorized protected access remains available:

```text
Authorization = true
        +
PROTECTED_OPERATION
        ↓
ACCESS_GRANTED
```

---

# What the Project Demonstrates

The current laboratory demonstrates a traceable security-test workflow:

```text
Define Security Requirement
        ↓
Model Threat
        ↓
Define Attack Hypothesis
        ↓
Define Security Test
        ↓
Execute Test
        ↓
Observe Simulated Target
        ↓
Evaluate Expected vs. Actual
        ↓
Generate Evidence
        ↓
Identify Security-Relevant Deviation
        ↓
Model Corrective Action
        ↓
Reuse Test for Retest
        ↓
Verify Regression Condition
```

The current implementation does not yet provide a generalized finding-management or regression platform.

The intended future extension is:

```text
Evidence
    ↓
Security Finding
    ↓
Root Cause
    ↓
Fix
    ↓
Retest
    ↓
Regression
    ↓
CI/CD
```

---

# Professional Positioning

This repository demonstrates engineering methodology within a controlled simulation environment.

It demonstrates:

* automotive security-test design
* security requirement verification
* threat-oriented test definition
* deterministic security simulation
* system-under-test abstraction
* separation of test logic and implementation
* structured evidence generation
* expected-versus-actual evaluation
* Python test automation
* reproducible verification
* controlled vulnerable-state simulation
* simulated fix and retest methodology
* regression workflow verification
* architectural documentation

It does not represent:

* a real penetration-testing engagement
* a real ECU assessment
* a real vehicle assessment
* a production cybersecurity validation
* an OEM security assessment
* professional operational penetration-testing experience

---

# Next Phase

## Phase 8 — Example Findings

The next phase will introduce representative security findings based on the established test and evidence workflow.

The existing TC-001, TC-002, and TC-003 implementations remain unchanged unless a later phase explicitly requires an architectural extension.

---

# Documentation Map

| Document | Purpose |
| --- | --- |
| `README.md` | Project overview, architecture, status, scope, and development phases |
| `PROJECT_STATUS.md` | Detailed implementation and verification status |
| `ARCHITECTURE_DECISIONS.md` | Recorded architectural decisions and rationale |
| `docs/01_architecture.md` | Detailed architecture |
| `docs/02_methodology.md` | Security-testing methodology |
| `docs/03_evidence-format.md` | Evidence Framework and evidence format |
| `docs/04_end-to-end-assessment-case.md` | Future end-to-end assessment structure |
| `02_test_cases/TC-001-diagnostic-authorization.md` | Detailed TC-001 specification |
| `02_test_cases/TC-002-message-validation.md` | Detailed TC-002 specification |
| `02_test_cases/TC-003-regression-workflow.md` | Detailed TC-003 regression workflow specification |
| `01_threat_model/01_attack_surface.md` | Modeled attack-surface information |

The README provides the project-level view. Detailed implementation and methodology are maintained in the corresponding documentation files.

---

# Final Scope Statement

The Automotive Security Regression Lab is a controlled, deterministic simulation environment for demonstrating how automotive security requirements can be transformed into reproducible security tests and structured execution evidence.

The current implementation covers:

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
TC-003 Regression Workflow
        ↓
Automated Verification
```

The current Phase-7 regression implementation is specific to the diagnostic authorization security property established by TC-001.

It demonstrates a controlled vulnerable-state reproduction, secure retest, expected-versus-actual evaluation, structured evidence generation, and authorized-behavior verification.

It is not yet a generalized regression platform.

The long-term workflow is:

```text
Security Requirement
        ↓
Threat Model
        ↓
Security Test
        ↓
Evidence
        ↓
Security Finding
        ↓
Root Cause
        ↓
Fix
        ↓
Retest
        ↓
Regression
        ↓
CI/CD
```

Each stage is added after the architectural capabilities required by that stage have been implemented and verified.

---

# Technical References

* [Python Documentation](https://docs.python.org/3.14/)
* [pytest Documentation](https://docs.pytest.org/en/stable/)
* [pytest Good Integration Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)
````
