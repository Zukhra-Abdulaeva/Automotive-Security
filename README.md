# Automotive Security Regression Lab

**From Security Finding to Reproducible Automotive Security Tests**

## Project

The **Automotive Security Regression Lab** is a local, deterministic simulation environment for developing and demonstrating an automotive cybersecurity testing workflow.

The project models how a security requirement can be translated into a security test, executed against a simulated ECU, evaluated against expected behavior, captured as structured evidence, documented as a security finding, and verified again through regression testing.

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

The implemented workflow currently covers:

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
        ↓
Finding Documentation
        ↓
Secure Retest
        ↓
Automated Regression Verification
        ↓
CI Evidence
        ↓
GitHub Actions Artifact
```

The project is developed incrementally. Each capability is added on top of the previously verified architecture.

---

# Current Implementation

The current implementation combines deterministic ECU simulation, security-test execution, structured evidence, example security findings, controlled regression verification, automated pytest regression coverage, and CI/CD execution of the existing regression suite.

The resulting workflow is:

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
Finding Assessment
        ↓
Secure Retest
        ↓
Automated Regression Verification
        ↓
EvidenceGenerator
        ↓
Evidence.to_json()
        ↓
CI Evidence JSON Files
        ↓
GitHub Actions Artifact
```

The implementation remains local, deterministic, hardware-independent, and network-independent.

The CI workflow executes the existing automated regression implementation. It does not introduce a second Security Test implementation.

---

# Security Test Scenarios

## TC-001 — Diagnostic Authorization

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

### Threat Model

**Asset**

**Protected Diagnostic Operation**

**Threat**

Unauthorized execution of a protected diagnostic operation.

**Potential Attacker**

Unauthorized diagnostic client.

**Security Property**

Authorization must be enforced before the protected operation is granted.

**Security Assumption**

The simulated ECU is responsible for enforcing authorization for the protected operation.

The threat model is intentionally limited to the behavior represented by the simulator.

### Attack Hypothesis

The hypothesis is:

> If authorization is missing or incorrectly enforced, an unauthorized diagnostic requester may be able to execute a protected operation.

TC-001 evaluates this condition using:

```text
authorization = false
PROTECTED_OPERATION
```

The expected secure response is:

```text
ACCESS_DENIED
```

The controlled vulnerable simulation produces:

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

### Test Architecture

TC-001 uses the established security-test architecture:

```text
TC-001 Diagnostic Authorization
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

| Component            | Responsibility                                               |
| -------------------- | ------------------------------------------------------------ |
| `SecurityTestCase`   | Defines the security scenario and expected behavior          |
| `SecurityTestRunner` | Executes the test and evaluates expected vs. actual behavior |
| `ECUTarget`          | Defines the target interface                                 |
| `ECUAdapter`         | Connects the target interface to the simulator               |
| `ECUSimulator`       | Implements the simulated ECU behavior                        |
| `TestResult`         | Represents the evaluated execution result                    |
| `Evidence`           | Records structured execution evidence                        |

### Test Scenarios

TC-001 contains the following representative scenarios:

| Scenario                       | ECU Mode              | Authorization | Operation               | Expected Result   |
| ------------------------------ | --------------------- | ------------: | ----------------------- | ----------------- |
| Unauthorized access            | Secure                |       `false` | `PROTECTED_OPERATION`   | `ACCESS_DENIED`   |
| Authorized access              | Secure                |        `true` | `PROTECTED_OPERATION`   | `ACCESS_GRANTED`  |
| Vulnerable unauthorized access | Vulnerable            |       `false` | `PROTECTED_OPERATION`   | `ACCESS_GRANTED`  |
| Invalid request                | Controlled simulation |             — | Invalid operation/input | `INVALID_REQUEST` |

The vulnerable scenario is security-relevant because it produces:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_GRANTED
Result   = FAIL
```

The test therefore detects the modeled authorization deviation.

---

# TC-002 — Message Validation

TC-002 verifies deterministic validation of protected-operation message parameters and ECU operational state.

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

Boolean values are explicitly rejected because Python treats `bool` as a subclass of `int`.

Unknown operations are classified as:

```text
UNSUPPORTED_OPERATION
```

Structurally invalid requests are classified as:

```text
INVALID_REQUEST
```

Requests that are structurally valid but violate a defined parameter or ECU-state constraint are classified as:

```text
REQUEST_REJECTED
```

The simulated ECU also supports the operational states:

```text
READY
BLOCKED
```

A protected operation issued while the ECU is blocked is rejected.

TC-002 therefore verifies:

* malformed request handling
* unsupported-operation handling
* parameter range enforcement
* boundary values `0` and `255`
* rejection of values below `0`
* rejection of values above `255`
* rejection of boolean values
* blocked-state handling

No security-relevant deviation is reproduced by the defined TC-002 scenarios.

---

# Controlled Vulnerable and Secure Behavior

The simulator supports two deterministic security modes.

## Secure Behavior

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

## Controlled Vulnerable Behavior

The vulnerable simulator intentionally omits effective authorization enforcement for the protected operation.

```text
Authorization = false
        ↓
PROTECTED_OPERATION
        ↓
ACCESS_GRANTED
```

This provides a deterministic security-test condition for demonstrating:

* expected-versus-actual comparison
* security-relevant test failure
* structured evidence
* security observation
* simulated remediation
* secure retest
* regression verification

It does not represent a real vulnerable vehicle, ECU, or production system.

---

# Evidence and Finding Workflow

The Evidence Framework provides structured execution evidence for the security-test workflow.

The execution path is:

```text
Security Test
        ↓
TestResult
        ↓
Evidence
        ↓
Finding Assessment
        ↓
Security Finding Documentation
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

Evidence records the observation. It does not independently constitute a formal security finding or assign vulnerability severity.

## Security Finding Examples

The project contains two representative finding artifacts:

```text
05_examples/sample_finding_SEC-001.md
05_examples/sample_finding_SEC-002.md
```

`SEC-001` documents the controlled authorization deviation reproduced by TC-001, including the modeled impact, root cause, simulated fix, retest, and regression relationship.

`SEC-002` documents the TC-002 message-validation assessment where no security-relevant deviation was reproduced.

The finding artifacts are documentation examples. They do not constitute a generalized security finding management system.

---

# Regression Verification

The project contains a controlled regression workflow for the authorization security property established by TC-001.

The workflow is:

```text
Controlled Vulnerable Behavior
        ↓
Original Security Condition
        ↓
Secure Retest
        ↓
Expected vs. Actual
        ↓
Regression Evidence
        ↓
Evidence Validation
        ↓
Authorized Behavior Verification
```

The vulnerable execution intentionally produces a failing `TestResult` because unauthorized access returns `ACCESS_GRANTED` where `ACCESS_DENIED` is required.

The surrounding pytest test passes because it verifies that the security deviation is detected correctly.

After the simulated correction, the same security property is evaluated against the secure ECU behavior:

```text
Authorization = false
        ↓
PROTECTED_OPERATION
        ↓
ACCESS_DENIED
        ↓
PASS
```

Authorized access remains valid:

```text
Authorization = true
        ↓
PROTECTED_OPERATION
        ↓
ACCESS_GRANTED
        ↓
PASS
```

The regression workflow is specific to the diagnostic authorization security property. It is not a generalized regression-orchestration platform.

---

# Automated Regression Verification

The implemented automated regression suite extends the existing test architecture with pytest-based verification of the secure regression behavior.

The suite is implemented in:

```text
04_tests/test_security_regression.py
```

The automated suite currently contains seven tests covering:

1. unauthorized protected operation
2. authorized protected operation
3. invalid message
4. unsupported operation
5. out-of-range boundary input
6. blocked ECU state
7. regression evidence generation and validation

Each scenario creates a fresh secure `ECUSimulator` to keep the test state isolated and deterministic.

The regression tests create their own `SecurityTestCase` instances with:

```text
test_id = TC-003
```

They reuse the established test architecture:

```text
SecurityTestCase
        ↓
SecurityTestRunner
        ↓
ECUAdapter
        ↓
ECUSimulator
        ↓
TestResult
```

The Evidence Framework is reused without introducing a new evidence schema or evidence component.

The automated evidence verification confirms that a secure unauthorized protected-operation scenario produces:

```text
test_id = TC-003
target = simulated-ecu

authorization = false
ecu_state = READY
security_mode = SECURE

input    = PROTECTED_OPERATION
expected = ACCESS_DENIED
actual   = ACCESS_DENIED
result   = PASS
```

The evidence is also validated through the existing `Evidence.validate()` mechanism.

This automation does not introduce:

* a new Evidence model
* a new evidence schema
* a new communication layer
* a new ECU adapter
* a new test runner
* generalized regression orchestration
* historical baseline comparison
* automated finding ingestion

CI/CD integration is implemented separately in Phase 10. The CI workflow executes this existing regression suite and consumes its generated evidence; it does not add another Security Test implementation.

The automated regression suite therefore extends verification coverage while preserving the existing architecture.

---

# Root Cause and Retest Model

For the controlled vulnerable simulator, the modeled root cause is:

> The authorization state is not enforced before the protected operation is granted.

This describes the behavior implemented by the simulator. It is not intended as a root-cause claim about a real ECU.

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

The corrected system behavior is verified by retesting the security condition and by automated regression verification.

---

# Architectural Principles

## Separate the Security Test from the System Under Test

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

## Separate Execution from Evidence

```text
Test Execution
        ↓
Test Result
        ↓
Evidence
```

Evidence records execution results without controlling ECU behavior.

## Keep the Simulated ECU Deterministic

```text
Same Input
    +
Same ECU State
    ↓
Same Security Decision
```

The secure and vulnerable simulator modes are deterministic.

## Keep the Security Requirement Separate from the Test Implementation

The security requirement is:

```text
Protected diagnostic operations shall require authorization.
```

TC-001 verifies this requirement.

The regression workflow and automated regression suite verify that the required behavior remains satisfied after the simulated correction.

The expected result must not be changed simply because the implementation behaves differently.

## Fix the System Under Test, Not the Security Test

A security-relevant deviation is corrected in the simulated ECU.

The original security property remains the verification basis.

Regression verification determines whether the corrected implementation satisfies the required behavior.

---

# CI/CD Security Regression Pipeline

Phase 10 integrates the existing automated security regression suite into GitHub Actions.

The CI chain is:

```text
Security Regression Tests
        ↓
EvidenceGenerator
        ↓
Evidence
        ↓
Evidence.to_json()
        ↓
CI Evidence JSON Files
        ↓
GitHub Actions Artifact
```

The CI workflow is implemented in:

```text
.github/workflows/security-regression.yml
```

## Single Source of Truth

`04_tests/test_security_regression.py` remains the central Security Regression test logic.

GitHub Actions executes this existing regression test implementation:

```text
GitHub Actions
        ↓
04_tests/test_security_regression.py
        ↓
Existing Security Regression Logic
```

The CI workflow does not implement a second Security Test logic.

The workflow is responsible for CI orchestration, evidence generation, and artifact upload. The Evidence Framework remains responsible for evidence generation, validation, and JSON serialization.

## CI Workflow

The workflow is configured for:

```text
push
pull_request
```

The implemented CI sequence is:

```text
Repository Checkout
        ↓
Python 3.12
        ↓
Install pytest>=9,<10
        ↓
Run Security Regression Tests
        ↓
Generate CI Evidence
        ↓
Upload Evidence Artifact
```

The security regression test command is:

```text
pytest -v 04_tests/test_security_regression.py
```

Evidence generation is executed after the regression test step with `if: always()` so that evidence generation is attempted even when the pytest step fails.

The generated evidence is written to:

```text
ci-evidence/
```

The CI artifact is uploaded with the name:

```text
security-regression-evidence
```

The artifact contains the generated JSON evidence files.

## CI Evidence Output

The current CI evidence generation produces six JSON files:

```text
ci-evidence/TC-003_unauthorized_protected_operation.json
ci-evidence/TC-003_authorized_protected_operation.json
ci-evidence/TC-003_invalid_message.json
ci-evidence/TC-003_unsupported_operation.json
ci-evidence/TC-003_boundary_input.json
ci-evidence/TC-003_unexpected_state.json
```

The six files represent the evidence generated for the six regression scenarios.

The seventh pytest test validates the regression evidence generation and evidence contents; it does not create a separate scenario evidence file.

The evidence files use the existing Evidence model and `Evidence.to_json()` serialization.

No separate CI evidence schema is introduced.

## CI Failure Semantics

The pytest step is intentionally not configured with `continue-on-error`.

Therefore a regression assertion failure causes the GitHub Actions job to fail:

```text
Security Regression Assertion
        ↓
pytest FAIL
        ↓
GitHub Actions Job FAIL
```

Evidence generation and artifact upload use `if: always()`:

```text
Security Regression Assertion
        ↓
pytest FAIL
        ↓
GitHub Actions Job FAIL
        ↓
Evidence Generation
        ↓
Evidence Upload
        ↓
security-regression-evidence Artifact
```

This preserves the failure status of the regression job while keeping the generated evidence available for inspection.

## Verified Successful CI Run

The push of commit `78c943f` to `main` triggered an actual GitHub Actions execution.

The verified run was:

| Checkpoint | Status | Evidence |
| --------------------------------- | ---------------- | --------------------- |
| GitHub Actions execution | [VERIFIED] | Run #1 |
| Trigger | [VERIFIED] | `push` |
| Workflow | [VERIFIED] | `Security Regression` |
| Branch | [VERIFIED] | `main` |
| Commit | [VERIFIED] | `78c943f` |
| Job | [VERIFIED] | `security-regression` |
| Overall status | [VERIFIED] | `Success` |
| Runtime | [VERIFIED] | 11 s |
| Artifact | [VERIFIED] | 1 artifact |

The artifact name is:

```text
security-regression-evidence
```

Artifact size:

```text
2.59 KB
```

SHA-256:

```text
e337895fd207dbfdeb30358cef5194c6a895b3e0d8e72feae9896a591585503f
```

The successful run demonstrates that the existing Security Regression suite can be executed in GitHub Actions and that the resulting evidence can be generated and uploaded as a CI artifact.

## Controlled CI Failure Verification

The CI failure behavior was verified separately on the dedicated branch:

```text
ci/controlled-failure-test
```

A single Security Regression assertion was intentionally changed to an incorrect expectation.

The test commit was:

```text
25432a4 test: verify CI failure handling
```

The corresponding local pytest result was:

```text
1 failed, 6 passed
```

The subsequent GitHub Actions Run #2 was triggered by `push` and failed as expected.

| Checkpoint | Status | Evidence |
| -------------------------------- | ---------------- | ------------------------------ |
| Controlled assertion failure | [VERIFIED] | `25432a4` |
| Local pytest failure | [VERIFIED] | 1 failed, 6 passed |
| GitHub Actions execution | [VERIFIED] | Run #2 |
| Trigger | [VERIFIED] | `push` |
| CI job | [VERIFIED] | `security-regression` |
| GitHub Actions status | [VERIFIED] | `Failed` |
| Exit code | [VERIFIED] | `1` |
| Evidence artifact despite failure | [VERIFIED] | `security-regression-evidence` |
| Artifact size | [VERIFIED] | 2.59 KB |

The controlled failure therefore verifies the intended CI behavior:

```text
Security Regression Assertion
        ↓
pytest FAIL
        ↓
GitHub Actions Job FAIL
        ↓
Evidence Generation / Upload
        ↓
security-regression-evidence Artifact
```

The intentionally introduced failure was restored with:

```text
a604f08 test: restore security regression expectation
```

The restored regression suite was executed locally again with:

```text
7 passed in 0.06s
```

`main` remained unchanged at commit `78c943f` and remained synchronized with `origin/main`.

## CI Verification Boundary

The actual `push` execution, successful artifact generation, controlled CI failure, and artifact generation after failure have been verified.

A separate actual `pull_request` GitHub Actions execution has not yet been verified and is therefore not documented as completed.

The workflow configuration nevertheless includes the `pull_request` trigger.

## Technical Note

GitHub reported a technical warning:

```text
Node.js 20 is deprecated
```

The warning was observed in connection with the currently used GitHub Actions:

```text
actions/checkout@v4
actions/setup-python@v5
actions/upload-artifact@v4
```

The verified workflow behavior was correct for both the successful CI run and the controlled failure run.

The Node.js warning is therefore currently treated as a technical note and not as a demonstrated CI pipeline failure.

---

# Verification

The repository was locally verified using the project-specific Python virtual environment.

The verification environment was activated from the project root with:

```text
.\.venv\Scripts\Activate.ps1
```

The active environment was confirmed by the (.venv) PowerShell prompt.

Latest complete test execution:

```text
pytest -v
```

Result:

```text
41 passed
```

Current test distribution:

```text
ECU Simulation:          6
Evidence Framework:     14
Foundation:              1
Security Regression:     7
TC-001:                  4
TC-002:                  5
Test Runner:             4
--------------------------
Total:                  41
```

The test count reflects the current repository state and is not treated as a permanent project invariant.

The verified automated regression behavior includes:

```text
Secure ECU
    ↓
Unauthorized Protected Operation
    ↓
ACCESS_DENIED
    ↓
PASS
```

and:

```text
Secure ECU
    ↓
Authorized Protected Operation
    ↓
ACCESS_GRANTED
    ↓
PASS
```

The controlled vulnerable-state workflow separately verifies that the security test detects:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_GRANTED
Result   = FAIL
```

The dedicated Security Regression suite was also verified independently:

```text
pytest -v 04_tests/test_security_regression.py
```

Result:

```text
7 passed
```

CI execution was additionally verified through the successful GitHub Actions run and the controlled CI failure described in the CI/CD Security Regression Pipeline section.

The CI evidence generation was verified to produce six JSON evidence files and upload them as the `security-regression-evidence` artifact.

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
TC-001 Security Tests
        ↓
TC-002 Security Tests
        ↓
Regression Workflow Tests
        ↓
Automated Regression Suite
        ↓
Complete pytest Suite
        ↓
CI Execution
```

Testing the infrastructure itself helps identify regressions in the mechanisms used to execute and evaluate security tests.

The CI pipeline does not replace the local test suite. It executes the established Security Regression suite in an automated environment and preserves the resulting evidence as a CI artifact.

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
│   ├── .gitkeep
│   ├── sample_finding_SEC-001.md
│   └── sample_finding_SEC-002.md
│
└── .github/
    └── workflows/
        ├── .gitkeep
        └── security-regression.yml
```

The `.gitkeep` files only preserve otherwise empty directories in Git. They contain no project logic.

---

# Technology Baseline

The project currently uses:

* Python
* pytest
* Python standard library components where practical
* GitHub Actions for CI execution

The CI workflow uses:

```text
Python 3.12
pytest>=9,<10
```

The implementation intentionally keeps runtime dependencies small.

The laboratory is:

* locally executable
* deterministic
* hardware-independent
* network-independent
* reproducible

The CI workflow does not require real ECU hardware, vehicle-network access, external ECU availability, or external security services.

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

# Current Scope and Limitations

The current implementation provides:

* deterministic ECU simulation
* secure and controlled vulnerable ECU modes
* security-test abstraction
* target abstraction through `ECUTarget`
* ECU integration through `ECUAdapter`
* expected-versus-actual evaluation
* structured execution evidence
* evidence validation
* TC-001 diagnostic authorization testing
* TC-002 message validation testing
* controlled TC-003 regression workflow
* SEC-001 and SEC-002 example finding documentation
* automated pytest regression verification
* local reproducible verification
* GitHub Actions execution of the Security Regression suite
* CI evidence generation
* CI evidence JSON serialization
* GitHub Actions artifact upload
* verified CI failure handling with evidence artifact generation

The following capabilities remain outside the current implementation:

* generalized security finding management
* automatic finding ingestion
* formal vulnerability classification
* automated severity calculation
* CVSS calculation
* customer security reporting
* generalized root-cause management
* generalized remediation tracking
* historical finding comparison
* generalized regression orchestration
* automated pull-request execution verification
* real ECU communication
* real CAN communication
* real UDS communication
* real vehicle-network interaction

These capabilities are reserved for later development.

The CI/CD workflow is implemented for the current Security Regression suite. It is not a generalized CI/CD security-testing platform.

---

# Project Status

## Implemented

### Repository Foundation

* Python project configuration
* pytest-based verification
* documentation structure
* project scope
* deterministic local development environment

### ECU Simulation

* deterministic ECU simulation
* secure mode
* vulnerable mode
* authorization state
* protected operation
* request validation
* structured responses

### Security Test Architecture

* `SecurityTestCase`
* `SecurityTestRunner`
* `TestResult`
* `ECUTarget`
* `ECUAdapter`
* separation between test execution and ECU implementation

### Evidence Framework

* structured Evidence model
* required-field validation
* PASS / FAIL semantics
* timestamp generation
* JSON serialization
* evidence generation from test execution
* evidence validation

### TC-001 — Diagnostic Authorization

* secure unauthorized scenario
* secure authorized scenario
* controlled vulnerable unauthorized scenario
* invalid-request scenario
* automated TC-001 tests
* integration with the existing test architecture
* integration with the Evidence Framework
* simulated fix/retest model

### TC-002 — Message Validation

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

### TC-003 — Regression Workflow

* controlled vulnerable-state reproduction
* secure regression retest
* expected-versus-actual evaluation
* regression evidence generation
* regression evidence validation
* authorized-behavior verification
* automated regression workflow verification

### Security Finding Documentation

* `SEC-001` structured security finding documentation
* `SEC-002` structured assessment documentation
* traceability to TC-001 and TC-002
* Evidence-compatible evidence representation
* modeled root cause for the SEC-001 controlled deviation
* simulated fix and retest documentation
* documented regression relationship
* distinction between demonstrated deviation and no-deviation assessment

### Automated Regression Verification

* pytest-based regression suite
* seven regression scenarios
* fresh secure ECU per scenario
* secure authorization verification
* message validation verification
* blocked-state verification
* evidence generation verification
* evidence validation verification
* complete local pytest verification

### CI/CD Security Regression Pipeline

* GitHub Actions workflow
* `push` trigger
* `pull_request` trigger
* Python 3.12 CI environment
* installation of `pytest>=9,<10`
* execution of the existing `04_tests/test_security_regression.py`
* CI evidence generation
* six CI evidence JSON files
* GitHub Actions artifact upload
* artifact generation with `if: always()`
* evidence availability after a controlled regression failure
* verified successful CI execution
* verified controlled CI failure handling
* verified restoration of the regression expectation

---

# Current Verification State

The latest complete local verification reports:

```text
41 passed
```

The dedicated automated regression suite reports:

```text
7 passed
```

The CI evidence generation currently produces:

```text
6 JSON files
```

The verified implementation therefore covers:

```text
ECU Simulation
        +
Security Test Architecture
        +
Evidence Framework
        +
TC-001
        +
TC-002
        +
TC-003 Regression Workflow
        +
Automated Regression Verification
        +
CI/CD Security Regression Pipeline
        ↓
Complete Local and CI Verification
```

The controlled regression behavior is:

```text
Controlled Vulnerable State
        ↓
ACCESS_GRANTED without authorization
        ↓
Security TestResult = FAIL
        ↓
Simulated Correction
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

The example finding artifacts are documentation outputs and are verified separately from automated pytest execution.

The successful CI run verified the following:

```text
GitHub Actions
        ↓
Security Regression
        ↓
Success
        ↓
Evidence Generation
        ↓
security-regression-evidence
```

The controlled CI failure verified:

```text
Security Regression Assertion
        ↓
pytest FAIL
        ↓
GitHub Actions Job FAIL
        ↓
Evidence Generation / Upload
        ↓
security-regression-evidence
```

The actual `push` CI execution has been verified.

A separate actual `pull_request` execution has not yet been verified.

---

# What the Project Demonstrates

The current laboratory demonstrates a traceable security-testing workflow:

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
Reuse Security Property for Retest
        ↓
Verify Regression Condition
        ↓
Automate Regression Verification
        ↓
Execute Regression in CI
        ↓
Preserve CI Evidence as Artifact
```

The project also demonstrates how assessment results can be documented as structured security finding artifacts:

```text
Evidence
    ↓
Finding Assessment
    ↓
Security Finding Documentation
```

`SEC-001` demonstrates documentation of a reproduced security-relevant deviation.

`SEC-002` demonstrates documentation of an assessment result where no security-relevant deviation was reproduced.

The current implementation does not provide a generalized finding-management or regression platform.

The CI implementation is likewise specific to the established Security Regression suite. It provides automated execution 
and evidence artifact handling, but not generalized security-test orchestration.

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
* automated regression testing
* CI/CD execution of an established security regression suite
* CI evidence generation and artifact handling
* architectural documentation
* structured security finding documentation
* traceability from security tests to findings
* root-cause and retest documentation for a controlled finding
* distinction between a reproduced security deviation and a no-deviation assessment

It does not represent:

* a real penetration-testing engagement
* a real ECU assessment
* a real vehicle assessment
* a production cybersecurity validation
* an OEM security assessment
* professional operational penetration-testing experience

---

# Documentation Map

| Document                                           | Purpose                                                                |
| -------------------------------------------------- | ---------------------------------------------------------------------- |
| `README.md`                                        | Project overview, architecture, status, scope, and development context |
| `PROJECT_STATUS.md`                                | Detailed implementation and verification status                        |
| `ARCHITECTURE_DECISIONS.md`                        | Recorded architectural decisions and rationale                         |
| `docs/01_architecture.md`                          | Detailed architecture                                                  |
| `docs/02_methodology.md`                           | Security-testing methodology                                           |
| `docs/03_evidence-format.md`                       | Evidence Framework and evidence format                                 |
| `docs/04_end-to-end-assessment-case.md`            | Future end-to-end assessment structure                                 |
| `02_test_cases/TC-001-diagnostic-authorization.md` | Detailed TC-001 specification                                          |
| `02_test_cases/TC-002-message-validation.md`       | Detailed TC-002 specification                                          |
| `02_test_cases/TC-003-regression-workflow.md`      | Detailed TC-003 regression workflow specification                      |
| `01_threat_model/01_attack_surface.md`             | Modeled attack-surface information                                     |

The README provides the project-level view. Detailed implementation, methodology, evidence, architecture, CI/CD, and test specifications are maintained in the corresponding documentation files.

---

# Final Scope Statement

The Automotive Security Regression Lab is a controlled, deterministic simulation environment for demonstrating how automotive security requirements can be transformed into reproducible security tests, structured execution evidence, security finding documentation, and regression verification.

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
Automated Regression Verification
        ↓
CI/CD Security Regression Pipeline
```

The assessment documentation layer is:

```text
TC-001 / TC-002
        ↓
Evidence
        ↓
SEC-001 / SEC-002 Example Findings
```

The regression verification layer is:

```text
Security Property
        ↓
Controlled Vulnerable Behavior
        ↓
Secure Retest
        ↓
Expected vs. Actual
        ↓
Regression Evidence
        ↓
Automated Regression Verification
```

The CI evidence layer is:

```text
Security Regression Tests
        ↓
EvidenceGenerator
        ↓
Evidence
        ↓
Evidence.to_json()
        ↓
CI Evidence JSON Files
        ↓
GitHub Actions Artifact
```

The current implementation therefore demonstrates not only security-test execution and structured evidence generation, but also controlled security finding documentation, simulated remediation and retest, automated verification of the resulting secure behavior, and execution of the established regression suite in GitHub Actions with preserved CI evidence.

The regression implementation remains specific to the diagnostic authorization security property established by TC-001. It is not a generalized regression platform.

The CI workflow executes the existing Security Regression suite and does not introduce a second Security Test implementation.

The long-term workflow remains:

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

Each stage is added only after the architectural capabilities required by that stage have been implemented and verified.

---

# Technical References

* [Python Documentation](https://docs.python.org/3.14/)
* [pytest Documentation](https://docs.pytest.org/en/stable/)
* [pytest Good Integration Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)
