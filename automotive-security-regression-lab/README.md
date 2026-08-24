# Automotive Security Regression Lab

**From Security Finding to Reproducible Automotive Security Tests**

## Project

The **Automotive Security Regression Lab** is a fully simulated and controlled laboratory for demonstrating a reproducible automotive cybersecurity testing and regression workflow.

The project is intentionally limited to simulation. It does not interact with real vehicles, real ECUs, OEM systems, customer data, production systems, or external vehicle networks.

> **Project scope:** simulated automotive security testing, deterministic security verification, evidence-oriented test execution, controlled security assessment, and reproducible regression engineering.

The repository is designed as an engineering demonstration project. It shows how security-testing activities can be structured, automated, verified, documented, and progressively connected into a complete security regression workflow.

The project does **not** claim professional penetration-testing experience or real-world vehicle security testing experience. It demonstrates a structured and reproducible methodology within a controlled simulation environment.

---

## Why this project exists

Automotive cybersecurity testing is not only about executing a security test.

A professional engineering workflow must also be able to answer:

- What security behavior was tested?
- Which test case was executed?
- What was the expected result?
- What did the simulated target actually return?
- When and under which execution context was the test performed?
- Can the result be reproduced?
- Can the result be stored as structured evidence?
- Can the evidence later support a security finding?
- Can the same test eventually be executed again after a fix?
- Can the resulting regression test become part of CI/CD?

The Automotive Security Regression Lab develops these capabilities incrementally.

The intended long-term workflow is:

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

Phase 4 establishes the **Evidence Framework** required to make security-test execution observable, structured, and reproducible.

---

# Current Phase

## Phase 4 — Evidence Framework

Phase 4 extends the Phase-3 security test architecture with a dedicated evidence layer.

The central Phase-4 objective is:

> **Transform a deterministic security-test execution into structured, reproducible execution evidence.**

Phase 3 established the mechanism for executing a security test against the simulated ECU.

Phase 4 adds the capability to represent the outcome of that execution as structured evidence without coupling evidence management to the ECU implementation.

The architecture therefore evolves from:

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

to:

```text
Security Test Case
        ↓
Test Runner
        ↓
ECU Adapter
        ↓
Simulated ECU
        ↓
ECU Response
        ↓
Test Result
        ↓
Evidence
```

The evidence layer is deliberately introduced as a separate architectural concern.

---

# Phase History

## Phase 1 — Repository Foundation

Phase 1 established the repository and development foundation.

Implemented capabilities include:

* Python project metadata
* pytest configuration
* repository structure
* documentation foundation
* project scope definition
* initial architectural decisions

The project was explicitly constrained to a controlled simulation environment.

---

## Phase 2 — ECU Simulation

Phase 2 implemented the deterministic simulated ECU.

The ECU simulator provides:

* secure security mode
* vulnerable security mode
* explicit authorization state
* protected operation handling
* request validation
* deterministic response statuses
* structured ECU responses

The simulator intentionally does not implement a real CAN or UDS stack.

No network communication is performed.

---

## Phase 3 — Security Test Architecture

Phase 3 separated security-test logic from the simulated system under test.

The architecture introduced:

* `SecurityTestCase`
* `SecurityTestRunner`
* `TestResult`
* `ECUTarget`
* `ECUAdapter`

The test runner communicates with the simulated target through the `ECUTarget` abstraction rather than accessing ECU implementation details directly.

This established the architectural foundation required for reusable security tests and later evidence generation.

---

## Phase 4 — Evidence Framework

Phase 4 introduces structured evidence handling.

The evidence layer provides a dedicated representation of test-execution information.

The purpose is to ensure that a test result is not only evaluated in memory but can also be represented as structured evidence for later analysis and documentation.

Phase 4 focuses specifically on:

* evidence representation
* deterministic evidence content
* association between a test result and its evidence
* separation of evidence handling from ECU behavior
* reproducible evidence generation
* validation of the evidence model through automated tests

Phase 4 does **not** implement security findings, root-cause analysis, remediation, retesting workflows, regression orchestration, or CI/CD.

Those capabilities remain intentionally deferred to later phases.

---

# Phase-4 Architecture

The current architecture is:

```text
                    Security Test Case
                           │
                           ▼
                    Security Test Runner
                           │
                           ▼
                       ECUTarget
                           │
                           ▼
                       ECUAdapter
                           │
                           ▼
                     Simulated ECU
                           │
                           ▼
                      ECU Response
                           │
                           ▼
                       Test Result
                           │
                           ▼
                         Evidence
```

The architecture establishes a clear separation of responsibilities.

### Security Test Case

`SecurityTestCase` describes what should be tested.

It represents the test definition rather than the implementation of the simulated ECU.

The test case contains the information required by the runner to execute and evaluate the scenario.

---

### Security Test Runner

`SecurityTestRunner` controls test execution.

Its responsibility is to:

1. accept a security test case
2. send the request through the target abstraction
3. receive the ECU response
4. compare expected and actual behavior
5. create a structured test result
6. provide the result to the evidence layer

The runner does not access internal ECU state.

It therefore remains independent from the concrete ECU implementation.

---

### ECU Target

`ECUTarget` defines the interface through which the security test communicates with the system under test.

The target abstraction prevents the test runner from depending directly on a concrete simulator implementation.

This creates a stable boundary for future target implementations while keeping the current project fully simulated.

---

### ECU Adapter

`ECUAdapter` connects the abstract target interface to the concrete `ECUSimulator`.

The adapter is responsible for target communication within the simulation.

It does not contain security-test logic and does not implement findings or remediation handling.

---

### Simulated ECU

`ECUSimulator` remains responsible for simulated ECU behavior.

It provides:

* secure and vulnerable security modes
* explicit authorization handling
* protected operation handling
* request validation
* deterministic response statuses
* structured ECU responses

The ECU simulator remains isolated from the evidence framework.

---

### Test Result

`TestResult` represents the evaluated outcome of a security-test execution.

It provides the boundary between test execution and evidence generation.

This separation is important because a test result represents an evaluation, while evidence represents the structured information retained from that evaluation.

---

### Evidence

The Phase-4 evidence layer provides a structured representation of execution evidence.

Evidence is intentionally treated as a separate concern from both:

* the simulated ECU
* the security-test execution mechanism

This separation allows later phases to build findings and regression workflows on top of stable execution evidence without modifying the ECU simulation.

---

# Evidence Engineering Principles

Phase 4 follows several principles.

## 1. Evidence must be deterministic

The same test scenario executed against the same deterministic target state must produce equivalent evidence.

Evidence must not depend on uncontrolled external systems.

---

## 2. Evidence must be structured

Evidence should be represented using explicit fields rather than relying only on free-form text.

Structured evidence can later be consumed by:

* reporting
* finding generation
* regression analysis
* automated validation
* CI/CD pipelines

---

## 3. Evidence must remain traceable to the test

Evidence must be associated with the security-test execution that produced it.

The evidence layer therefore remains connected to the test result rather than directly to internal ECU implementation details.

---

## 4. Evidence must not contain hidden ECU logic

The evidence framework records execution information.

It does not determine the security behavior of the ECU.

Security behavior remains the responsibility of the simulated target.

---

## 5. Evidence generation must not change test behavior

The introduction of evidence handling must not modify the security decision of the ECU or alter the expected result of the test.

Evidence is an observation and recording layer.

It is not part of the security policy.

---

## 6. Evidence must support reproducibility

A security test should be capable of being executed repeatedly and evaluated consistently.

The evidence model therefore provides a foundation for later:

* retesting
* regression testing
* comparison of executions
* automated reporting
* CI/CD verification

---

# Phase-4 Security Test Scenarios

The Phase-4 evidence framework operates on the deterministic security-test
architecture established in Phase 3.

The evidence tests verify that evidence can be generated from executed
`SecurityTestCase` and `TestResult` objects.

The underlying simulated ECU scenarios include:

| Scenario | Expected Response |
| --- | --- |
| Unauthorized protected operation in secure mode | `ACCESS_DENIED` |
| Authorized protected operation in secure mode | `ACCESS_GRANTED` |
| Invalid operation | `INVALID_REQUEST` |
| Unauthorized protected operation in vulnerable mode | `ACCESS_GRANTED` |

The evidence layer does not hard-code these ECU security decisions.
It records the expected and actual result produced by the test execution.

---

# Phase-4 Verification

The current repository contains 25 pytest test cases.

Current test distribution:

```text
04_tests/test_ecu_simulator.py: 6
04_tests/test_evidence.py: 14
04_tests/test_foundation.py: 1
04_tests/test_test_runner.py: 4
```

The current collection was verified with:

```text
python -m pytest --collect-only -q
```

The complete test suite must be executed with:

```text
python -m pytest -q
```

Phase 4 is considered complete only after the complete pytest suite has
passed and the final repository quality gate has been reviewed.

The successful test execution confirms that the current Phase-4 implementation preserves the behavior established in earlier phases while adding the evidence layer.

The verification covers the existing ECU behavior, test architecture, and Phase-4 evidence functionality.

The exact test count is intentionally reported from the latest local verification rather than being treated as a permanent project invariant.

---

# Evidence Framework Scope

Phase 4 implements:

* structured evidence representation
* evidence generation associated with test execution
* deterministic evidence content
* separation between test results and evidence
* automated evidence validation
* preservation of the Phase-3 test architecture
* reproducible evidence-oriented execution

Phase 4 does **not** implement:

* security findings
* vulnerability classification
* root-cause analysis
* remediation tracking
* fix implementation
* retest orchestration
* regression orchestration
* CI/CD pipelines
* real ECU communication
* real CAN communication
* real UDS communication
* network-based vehicle interaction

These capabilities belong to later phases.

---

# Repository Structure

The current repository structure is:

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
│   └── test_test_runner.py
│
├── 05_examples/
│   └── .gitkeep
│
└── .github/
    └── workflows/
        └── .gitkeep
```

The `.gitkeep` files exist only to preserve otherwise empty directories in the Git working tree. They contain no project logic.

---

# Technology Baseline

The primary technology baseline is:

* Python
* pytest
* standard Python library components where practical

The project intentionally avoids unnecessary runtime dependencies.

The architecture is designed to remain understandable, deterministic, and easy to execute in a clean local environment.

---

# Testing Philosophy

The project uses automated tests as an engineering verification mechanism.

Tests are intended to verify both:

1. the behavior of the simulated security target
2. the correctness of the security-test infrastructure

This distinction is important.

The project does not treat the test framework itself as trusted without verification.

The test infrastructure is also tested.

The current test layers cover:

```text
ECU Simulation Tests
        ↓
Test Architecture Tests
        ↓
Evidence Framework Tests
        ↓
Complete pytest Suite
```

This layered approach provides a foundation for later regression testing.

---

# Architectural Principles

The project currently follows these core architectural principles:

### Separate the security test from the system under test

```text
Security Test
      ↓
Test Runner
      ↓
ECU Adapter
      ↓
Security Target
```

### Separate execution from evidence

```text
Test Execution
      ↓
Test Result
      ↓
Evidence
```

### Keep the simulated ECU deterministic

```text
Same Input
    +
Same ECU State
    ↓
Same Security Decision
    ↓
Same Expected Result
```

### Introduce later workflow stages only when their architectural prerequisites exist

The project deliberately develops the workflow incrementally.

Evidence is introduced before findings.

Findings will be introduced before root-cause analysis.

Root-cause analysis will precede fix and retest workflows.

Regression automation will build on validated retesting behavior.

CI/CD will build on a stable regression suite.

This prevents later functionality from being implemented prematurely or coupled incorrectly to earlier layers.

---

# Current Project Status

**Phase 4 — Evidence Framework**

The current project status is:

**Status: Verification / Quality Gate**

Completed phases:

* Phase 1 — Repository Foundation
* Phase 2 — ECU Simulation
* Phase 3 — Security Test Architecture
* Phase 4 — Evidence Framework

Phase 4 extends the previously established architecture without changing the fundamental security-target model.

The project now contains a deterministic path from:

```text
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

This represents the first complete execution-to-evidence path within the laboratory.

---

# Phase Boundaries

Phase 4 intentionally stops at the evidence layer.

The following phases remain outside the current implementation:

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

This boundary is intentional and is part of the project's incremental development strategy.

---

# What Phase 4 Demonstrates

Phase 4 demonstrates that a security test can be treated as an engineering artifact rather than only as an assertion.

The execution now has a conceptual lifecycle:

```text
Define Test
    ↓
Execute Test
    ↓
Observe Target
    ↓
Evaluate Result
    ↓
Create Evidence
    ↓
Preserve Evidence
```

This provides the foundation for the next stage of the project:

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
```

The project therefore moves from a pure test-execution architecture toward a traceable security-engineering workflow.

---

# Safety and Scope

This project is intentionally designed as a controlled simulation.

It does not:

* connect to real vehicles
* connect to real ECUs
* send traffic to vehicle networks
* implement a production CAN stack
* implement a production UDS stack
* interact with OEM infrastructure
* access customer data
* interact with productive systems
* perform unauthorized security testing

All security behavior is simulated locally and deterministically.

The vulnerable ECU mode exists exclusively as a controlled test condition for demonstrating security verification and regression concepts.

---

# Professional Positioning

The repository is intended to demonstrate engineering methodology rather than claim operational experience.

It demonstrates:

* structured security-test design
* deterministic test execution
* abstraction of the system under test
* separation of test logic and implementation
* evidence-oriented verification
* Python test automation
* reproducible engineering workflows
* architectural documentation
* controlled security simulation

It does not represent a real-world penetration-testing engagement.

---

# Next Phase

## Phase 5 — TC-001 Diagnostic Authorization

The next phase will introduce the first dedicated security test case based on the project's diagnostic-authorization scenario.

Phase 5 will build on the evidence architecture established in Phase 4.

The expected conceptual workflow will become:

```text
TC-001 Diagnostic Authorization
              ↓
       Security Test Runner
              ↓
          ECU Target
              ↓
        Simulated ECU
              ↓
          Test Result
              ↓
           Evidence
```

Phase 5 will not replace the Phase-4 evidence architecture.

It will use the established architecture as the basis for a concrete security test case.

---

# Technical References

* Python documentation: [https://docs.python.org/3.14/](https://docs.python.org/3.14/)
* pytest documentation: [https://docs.pytest.org/en/stable/](https://docs.pytest.org/en/stable/)
* pytest good integration practices: [https://docs.pytest.org/en/stable/explanation/goodpractices.html](https://docs.pytest.org/en/stable/explanation/goodpractices.html)