# Automotive Security Regression Lab

**From Security Finding to Reproducible Automotive Security Tests**

## Project

The **Automotive Security Regression Lab** is a fully simulated, controlled laboratory for demonstrating a reproducible automotive security-testing workflow.

The project is intentionally limited to simulation. It does not interact with real vehicles, ECUs, OEM systems, customer data, or productive systems.

> **Project scope:** simulated security testing, controlled security-testing laboratory, educational automotive security simulation, and reproducible security regression workflow.

## Why this project exists

The project demonstrates how an engineering workflow can connect security requirements, threat modeling, attack hypotheses, security tests, evidence, findings, root-cause analysis, fixes, retesting, regression testing, and CI/CD.

The project is designed to demonstrate the connection between:

- Automotive testing
- Quality engineering
- System analysis
- Security testing
- Root-cause analysis
- Python test automation
- Regression testing
- CI/CD

The repository does **not** claim professional penetration-testing experience. It demonstrates a structured, simulated methodology instead.

## Security-engineering workflow

The planned workflow is:

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

Phase 1 established the repository foundation.

Phase 2 implemented a deterministic simulated ECU with secure and vulnerable security modes, authorization handling, request validation, and structured responses.

Phase 3 introduces the security test execution architecture that separates security test logic from the simulated ECU implementation.

The complete security-testing workflow remains under development and will be implemented incrementally in later phases.

## Simulated automotive architecture

The current Phase-3 test architecture is:

```text
Security Test Case
        ↓
Test Runner
        ↓
ECU Adapter
        ↓
Simulated ECU
        ↓
Response
        ↓
Test Result
```

The architecture is intentionally simple and establishes a clear boundary between the security test mechanism and the simulated system under test.

### Security Test Case

`SecurityTestCase` provides the basic abstraction for a security test case.

It currently contains:

* test ID
* description
* request
* expected response status

### Security Test Runner

`SecurityTestRunner` coordinates the execution of a security test case.

Its responsibility is to:

1. accept a test case
2. send the request through the target interface
3. receive the ECU response
4. compare expected and actual response status
5. return a structured `TestResult`

The runner does not access internal ECU state.

### ECU Adapter

`ECUAdapter` provides the target boundary between the test runner and the concrete simulated ECU.

The `ECUTarget` protocol defines the interface used by the test runner.

The adapter contains no security-test logic and does not implement findings or evidence management.

### Simulated ECU

The `ECUSimulator` remains responsible for the security behavior implemented in Phase 2.

It provides:

* secure and vulnerable security modes
* explicit authorization state
* protected operation handling
* request validation
* deterministic response statuses
* structured ECU responses

The simulated ECU does not implement a real CAN or UDS stack and performs no network communication.

## Phase 3 security-test scenarios

The Phase-3 architecture is verified through the following scenarios:

| Test ID       | Scenario                                    | Expected Result   |
| ------------- | ------------------------------------------- | ----------------- |
| `TC-ARCH-001` | Unauthorized protected operation            | `ACCESS_DENIED`   |
| `TC-ARCH-002` | Authorized protected operation              | `ACCESS_GRANTED`  |
| `TC-ARCH-003` | Invalid operation                           | `INVALID_REQUEST` |
| `TC-ARCH-004` | Vulnerable unauthorized protected operation | `ACCESS_GRANTED`  |

These tests exercise the test runner and target abstraction rather than accessing ECU implementation details directly.

## Technology baseline

The primary technology baseline is Python with pytest as the test framework.

No unnecessary security-specific runtime dependencies are introduced.

## Repository structure

```text
automotive-security-regression-lab/
├── README.md
├── PROJECT_STATUS.md
├── ARCHITECTURE_DECISIONS.md
├── pyproject.toml
├── .gitignore
├── docs/
│   ├── .gitkeep
│   ├── 01_architecture.md
│   ├── 02_methodology.md
│   ├── 03_evidence-format.md
│   └── 04_end-to-end-assessment-case.md
├── 01_threat_model/
│   └── .gitkeep
├── 02_test_cases/
│   ├── TC-001-diagnostic-authorization.md
│   ├── TC-002-message-validation.md
│   └── TC-003-regression-workflow.md
├── 03_src/
│   └── security_lab/
│       ├── __init__.py
│       ├── ecu_simulator.py
│       ├── ecu_adapter.py
│       └── test_runner.py
├── 04_tests/
│   ├── test_ecu_simulator.py
│   ├── test_foundation.py
│   └── test_test_runner.py
├── 05_examples/
│   └── .gitkeep
└── .github/
    └── workflows/
        └── .gitkeep
```

The `.gitkeep` files exist only to preserve otherwise empty directories in a Git working tree. They contain no project logic.

## Current project status

**Phase 3 — Security Test Architecture**

Phase 1 established the repository structure, project metadata, documentation foundation, and pytest configuration.

Phase 2 implemented and verified the deterministic simulated ECU.

Phase 3 implemented and verified:

* `SecurityTestCase`
* `SecurityTestRunner`
* `TestResult`
* `ECUTarget`
* `ECUAdapter`
* separation between security test logic and ECU implementation
* deterministic security-test execution

## Phase 3 verification

The Phase-3 test architecture was executed locally with pytest.

Verified scenarios include:

* secure unauthorized protected operation
* secure authorized protected operation
* vulnerable unauthorized protected operation
* invalid operation

The selected Phase-2 and Phase-3 test files were also executed together successfully.

Latest verified combined result:

```text
11 passed
```

The Phase-3 test runner itself currently contains four architecture scenarios.

## Phase boundaries

Phase 3 implements:

* security test case abstraction
* security test runner
* ECU target abstraction
* ECU adapter
* deterministic test execution
* separation between test mechanism and simulated system under test

The following functionality belongs to later phases:

* formal Evidence Framework
* evidence files and execution evidence
* security findings
* root-cause analysis
* fix and retest workflow
* complete regression framework
* CI/CD workflow
* end-to-end assessment

No real ECU communication or production-system testing is implemented.

## Architectural principle

The central Phase-3 principle is:

**Separate the security test from the system under test.**

```text
Security Test
      ↓
Test Runner
      ↓
ECU Adapter
      ↓
Security Target
```

The ECU is the simulated target.

The Test Runner is the test mechanism.

The Adapter connects the two.

This separation provides the architectural foundation for later evidence, findings, retesting, regression, and CI/CD capabilities without implementing those later phases prematurely.

## Technical references

* Python documentation: [https://docs.python.org/3.14/](https://docs.python.org/3.14/)
* pytest documentation: [https://docs.pytest.org/en/stable/](https://docs.pytest.org/en/stable/)
* pytest good integration practices: [https://docs.pytest.org/en/stable/explanation/goodpractices.html](https://docs.pytest.org/en/stable/explanation/goodpractices.html)