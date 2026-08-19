# Automotive Security Regression Lab

**From Security Finding to Reproducible Automotive Security Tests**

## Project

The **Automotive Security Regression Lab** is a fully simulated, controlled laboratory for demonstrating a reproducible automotive security-testing workflow.

The project is intentionally limited to simulation. It does not interact with real vehicles, ECUs, OEM systems, customer data, or productive systems.

> **Project scope:** simulated security testing, controlled security-testing laboratory, educational automotive security simulation, and reproducible security regression workflow.

## Why this project exists

[MASTER] The project demonstrates how an engineering workflow can connect security requirements, threat modeling, attack hypotheses, security tests, evidence, findings, root-cause analysis, fixes, retesting, regression testing, and CI/CD.

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

[MASTER] The planned workflow is:

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

Phase 1 established the repository foundation. **Phase 2 — ECU Simulation** implements a deterministic simulated ECU with secure and vulnerable security modes, authorization handling, request validation, and structured responses. The Phase 2 behavior is verified by six automated pytest tests.

The complete security-testing workflow remains under development and will be implemented incrementally in later phases.

## Simulated automotive architecture

[MASTER] The planned test architecture is:

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
Evidence
```

Phase 2 implements the simulated ECU component of this architecture.

The `ECUSimulator` provides:

- secure and vulnerable security modes
- explicit authorization state
- protected operation handling
- request validation
- deterministic response statuses
- structured ECU responses

The simulated ECU does not implement a real CAN or UDS stack and performs no network communication.

The ECU adapter, evidence layer, test-runner architecture, regression workflow, and CI workflow remain deferred to later phases.

## Technology baseline

[MASTER] The primary technology baseline is Python with pytest as the test framework.

[SOURCE] Python 3.14 is the current documented Python 3.14 release line used as the reference for this project foundation. See the official Python documentation: https://docs.python.org/3.14/

[SOURCE] pytest supports project-level configuration in `pyproject.toml`. This repository uses the native `[tool.pytest]` configuration supported by pytest 9.0. See the official pytest configuration documentation: https://docs.pytest.org/en/stable/reference/customize.html

No additional security-specific runtime dependencies are introduced in Phase 2.

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
│   └── .gitkeep
├── 03_src/
│   └── security_lab/
│       ├── __init__.py
│       └── ecu_simulator.py
├── 04_tests/
│   ├── test_ecu_simulator.py
│   └── test_foundation.py
├── 05_examples/
│   └── .gitkeep
└── .github/
    └── workflows/
        └── .gitkeep
```

The `.gitkeep` files exist only to preserve otherwise empty directories in a Git working tree. They contain no project logic.

## Current project status

[MASTER] **Phase 2 — ECU Simulation** is the current completed phase.

Phase 1 established the repository structure, project metadata, documentation foundation, and pytest configuration.

Phase 2 implemented and verified a deterministic simulated ECU with:

- secure and vulnerable security modes
- explicit authorization state
- protected operation handling
- request validation
- deterministic response statuses
- structured ECU responses

The Phase 2 implementation is verified by six automated pytest tests.

Latest verification result:

```text
6 passed
```

## Phase boundaries

[MASTER] The following functionality is implemented in Phase 2:

- deterministic simulated ECU behavior
- secure and vulnerable security modes
- diagnostic authorization state
- protected operation handling
- request validation
- deterministic response statuses
- automated pytest verification

The following components are explicitly deferred to later phases:

- ECU adapter layer
- security test architecture
- evidence generation logic
- security findings
- root-cause analysis
- fix and retest workflow
- broader regression test framework
- GitHub Actions workflow logic

## Verification note

Phase 2 has been verified locally with the automated pytest test suite.

The verification covers:

- secure unauthorized access denial
- secure authorized access
- vulnerable unauthorized access
- unknown operation rejection
- invalid input rejection
- invalid parameter structure rejection

Latest verification result:

```text
6 passed
```
Security findings, evidence generation, root-cause analysis, fix and retest workflows, broader regression testing, and CI/CD results remain deferred to later phases.

## Technical references

- [SOURCE] Python documentation: https://docs.python.org/3.14/
- [SOURCE] pytest configuration documentation: https://docs.pytest.org/en/stable/reference/customize.html
- [SOURCE] pytest good integration practices: https://docs.pytest.org/en/stable/explanation/goodpractices.html