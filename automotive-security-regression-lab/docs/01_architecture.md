# Architecture

## Purpose

The Automotive Security Regression Lab uses a deterministic software
architecture for developing and executing automotive security tests against a
simulated ECU.

The architecture was introduced in Phase 3 and extended in Phase 4 with the Evidence Framework. 
Phase 5 adds TC-001 — Diagnostic Authorization, and Phase 6 adds TC-002 — Message Validation.

The architecture separates the following responsibilities:

- security-test definition
- test execution
- target interaction
- simulated ECU behavior
- test-result evaluation
- evidence generation

The separation is intentional. The security test defines the expected
security behavior, the simulated ECU provides the system-under-test behavior,
the Test Runner evaluates the execution result, and the Evidence Framework
records the resulting observation.

The project remains fully simulated and deterministic. It does not communicate
with real vehicles, real ECUs, CAN networks, UDS endpoints, OEM systems, or
production systems.

---

## System Context

The project models the basic relationship between a security tester and an
automotive system in a controlled Python environment.

A simplified real-world concept can be represented as:

```text
Security Tester
       |
       v
Diagnostic Interface
       |
       v
Communication Layer
       |
       v
ECU
````

The project does not implement this real-world communication stack.

Instead, the current implementation represents the testing workflow through
the following local architecture:

```text
Security Test Case
       |
       v
Security Test Runner
       |
       v
ECU Adapter
       |
       v
Simulated ECU
       |
       v
ECU Response
       |
       v
Test Result
       |
       v
Evidence
```

The `ECUSimulator` is the system under test.

The security-test infrastructure communicates with the simulated target
through the defined target interface. It does not directly manipulate the
internal implementation of the ECU simulator.

---

## Architectural Components

The current architecture consists of the following logical components:

```text
+---------------------------+
|    Security Test Case     |
+-------------+-------------+
              |
              v
+---------------------------+
|     SecurityTestRunner    |
+-------------+-------------+
              |
              v
+---------------------------+
|        ECUTarget          |
+-------------+-------------+
              |
              v
+---------------------------+
|        ECUAdapter         |
+-------------+-------------+
              |
              v
+---------------------------+
|       ECUSimulator        |
+-------------+-------------+
              |
              v
+---------------------------+
|        ECUResponse        |
+-------------+-------------+
              |
              v
+---------------------------+
|        TestResult         |
+-------------+-------------+
              |
              v
+---------------------------+
|    Evidence Framework     |
+---------------------------+
```

Each component has a defined responsibility.

The architecture deliberately prevents security-test logic, ECU security
behavior, and evidence generation from being combined into a single
component.

---

## SecurityTestCase

`SecurityTestCase` represents the definition of a security test.

The current implementation contains:

* `test_id`
* `description`
* `request`
* `expected_status`

The test case defines the request that is sent to the target and the response
status that is expected for the defined security scenario.

For TC-001, the test case represents the protected diagnostic operation and
the expected authorization behavior.

The test case does not implement the ECU security policy.

The expected result is therefore defined independently from the concrete
implementation of the simulated ECU.

---

## SecurityTestRunner

`SecurityTestRunner` controls the execution of a security test.

Its responsibilities are:

1. accept a `SecurityTestCase`
2. send the request through the target interface
3. receive the ECU response
4. compare the actual response status with the expected status
5. create a structured `TestResult`

The execution flow is:

```text
SecurityTestCase
       |
       v
SecurityTestRunner
       |
       v
Target
       |
       v
ECU Response
       |
       v
Expected vs Actual
       |
       v
TestResult
```

The Test Runner does not access internal ECU state.

It does not implement:

* ECU security policy
* authorization decisions
* security finding management
* evidence storage
* regression orchestration
* CI/CD

The Test Runner is responsible for executing and evaluating the security
test, not for implementing the security behavior being tested.

---

## ECUTarget

`ECUTarget` defines the target interface used by the security-test runner.

The abstraction separates the test infrastructure from the concrete target
implementation.

The current relationship is:

```text
SecurityTestRunner
        |
        v
    ECUTarget
        |
        v
    ECUAdapter
        |
        v
   ECUSimulator
```

The target interface defines how the test infrastructure interacts with the
system under test.

The current implementation uses the simulated ECU behind this interface.

No real vehicle communication protocol is implemented through `ECUTarget`.

---

## ECUAdapter

`ECUAdapter` connects the abstract `ECUTarget` interface to the concrete
`ECUSimulator`.

Its responsibility is to forward requests to the configured target and return
the resulting response.

The adapter does not:

* define security requirements
* implement security-test logic
* make authorization decisions
* evaluate security findings
* generate evidence
* modify test results

The adapter therefore provides the boundary between the generic test
execution layer and the concrete simulated target.

This separation allows the test infrastructure to remain independent from
the concrete ECU simulator implementation.

---

## ECUSimulator

`ECUSimulator` represents the simulated ECU and is the system under test.

The simulator was introduced in Phase 2 and provides the target behavior used
by the security-test architecture.

Its responsibilities include:

* maintaining the configured security mode
* maintaining the authorization state
* validating incoming requests
* processing the requested operation
* applying the configured security behavior
* returning a deterministic `ECUResponse`

The simulator supports two security modes:

```text
secure
vulnerable
```

### Secure Mode

Secure mode enforces authorization before granting the protected operation.

```text
authorization = false
PROTECTED_OPERATION
       |
       v
ACCESS_DENIED
```

and:

```text
authorization = true
PROTECTED_OPERATION
       |
       v
ACCESS_GRANTED
```

### Vulnerable Mode

Vulnerable mode intentionally reproduces the authorization deviation used by
the security tests:

```text
authorization = false
PROTECTED_OPERATION
       |
       v
ACCESS_GRANTED
```

The vulnerable behavior is a controlled simulation condition. It does not
represent a real ECU vulnerability or a claim about a production automotive
system.

The simulator remains independent from the Test Runner and Evidence
Framework.

It does not generate, store, or evaluate test evidence.

---

## ECUResponse

The simulator returns an `ECUResponse`.

The current response model contains:

* `status`
* `operation`

The supported response statuses are:

```text
ACCESS_GRANTED
ACCESS_DENIED
INVALID_REQUEST
```

The response represents the behavior observed by the security-test
infrastructure.

For a given security mode, authorization state, and request, the simulator
produces a deterministic response.

The response can be converted into a dictionary representation using
`to_dict()`.

---

## TestResult

`TestResult` represents the evaluated outcome of a security-test execution.

The result is created by comparing the expected status defined by the
security test with the actual status returned by the target.

Conceptually:

```text
Expected Status
       |
       +
       |
Actual Status
       |
       v
Comparison
       |
       v
TestResult
```

The `TestResult` therefore forms the boundary between test execution and
evidence generation.

The ECU simulator does not determine the final test result.

It only returns the response representing the behavior of the system under
test.

---

## Evidence Framework

The Evidence Framework records the result of a completed security-test
execution in a structured format.

The current Evidence model contains:

* `test_id`
* `timestamp`
* `target`
* `preconditions`
* `input`
* `expected`
* `actual`
* `result`
* `notes`

The Evidence Framework operates after test execution:

```text
Security Test
       |
       v
Test Result
       |
       v
Evidence
```

The Evidence Framework does not implement security behavior.

It does not change the ECU response, modify the expected result, or determine
the security policy of the system under test.

Evidence represents the observation produced by a test execution.

---

## Evidence Result Semantics

The Evidence Framework currently supports two result values:

```text
PASS
FAIL
```

The semantics are:

```text
PASS
Expected == Actual
```

and:

```text
FAIL
Expected != Actual
```

For example, if the security requirement requires:

```text
Expected = ACCESS_DENIED
```

but the controlled vulnerable ECU returns:

```text
Actual = ACCESS_GRANTED
```

the resulting evidence represents:

```text
FAIL
```

The `FAIL` indicates that the observed behavior did not match the expected
security behavior.

It does not automatically constitute a formal security vulnerability
finding.

Formal finding assessment, severity classification, root-cause management,
and remediation tracking belong to later project phases.

---

## Complete Test Execution Flow

The current execution flow is:

```text
SecurityTestCase
       |
       | request
       v
SecurityTestRunner
       |
       | handle_request()
       v
ECUTarget
       |
       v
ECUAdapter
       |
       | handle_request()
       v
ECUSimulator
       |
       | ECUResponse
       v
ECUAdapter
       |
       v
SecurityTestRunner
       |
       | compare expected / actual
       v
TestResult
       |
       v
EvidenceGenerator
       |
       v
Evidence
       |
       v
JSON
```

The execution path separates target behavior from test evaluation and evidence
generation.

This means that the ECU simulator remains unaware of the Evidence Framework.

---

## TC-001 in the Current Architecture

Phase 5 introduces:

```text
TC-001 — Diagnostic Authorization
```

TC-001 verifies the security requirement:

```text
Protected diagnostic operations shall require authorization.
```

The protected operation is:

```text
PROTECTED_OPERATION
```

The secure behavior is:

```text
authorization = false
PROTECTED_OPERATION
       |
       v
ACCESS_DENIED
```

and:

```text
authorization = true
PROTECTED_OPERATION
       |
       v
ACCESS_GRANTED
```

The controlled vulnerable behavior is:

```text
authorization = false
PROTECTED_OPERATION
       |
       v
ACCESS_GRANTED
```

The security test evaluates these responses through the existing test
architecture.

The test does not access the internal authorization implementation of the
simulated ECU.

---

## TC-002 in the Current Architecture

Phase 6 introduces:

```text
TC-002 — Message Validation
```

TC-002 extends the existing security-test architecture without introducing a 
new communication layer.

The test uses the same architectural path:

TC-002
   |
   v
SecurityTestCase
   |
   v
SecurityTestRunner
   |
   v
ECUTarget
   |
   v
ECUAdapter
   |
   v
ECUSimulator
   |
   v
ECUResponse
   |
   v
TestResult
   |
   v
Evidence

TC-002 verifies message/request validation behavior through the existing 
target abstraction.

The security test does not access internal ECU implementation details.

The expected behavior remains defined by the security-test specification 
and is evaluated independently from the concrete ECU implementation.

TC-002 therefore reuses the architectural separation established in 
Phases 3, 4, and 5.

No new communication layer is introduced by TC-002.

---

## Request and Response Flow

A request moves through the target boundary before reaching the simulated
ECU.

```text
SecurityTestCase
       |
       | request
       v
SecurityTestRunner
       |
       v
ECUTarget
       |
       v
ECUAdapter
       |
       v
ECUSimulator
       |
       | ECUResponse
       v
ECUAdapter
       |
       v
SecurityTestRunner
       |
       | compare expected / actual
       v
TestResult
```

The Test Runner therefore interacts with the target through the defined
interface instead of directly calling ECU implementation details.

---

## Invalid Requests

The simulated ECU validates incoming requests.

An unsupported operation results in:

```text
Unknown Operation
       |
       v
INVALID_REQUEST
```

Invalid request handling is part of the ECU simulator.

The Test Runner does not implement request validation. It evaluates the
response returned by the target.

This keeps target behavior and test evaluation separate.

---

## Determinism

Deterministic behavior is a core requirement of the current architecture.

For the same:

* security mode
* authorization state
* request

the simulator produces the same response.

This allows security tests to be repeated under equivalent conditions and
makes test results reproducible.

The current architecture does not depend on:

* physical hardware
* vehicle networks
* external services
* network access
* random test data

The Evidence Framework generates a runtime timestamp. The timestamp is
therefore expected to differ between executions.

The remaining evidence fields are derived from the test execution and target
state.

---

## Architectural Separation

The central architectural separation is:

```text
Security Test Definition
          |
          v
    Test Execution
          |
          v
    Target Boundary
          |
          v
    System Under Test
          |
          v
      Test Result
          |
          v
       Evidence
```

The security test does not depend on internal simulator attributes.

For example, the test infrastructure does not directly manipulate internal
state such as:

```text
_internal_state
_authorized
_security_policy
```

Communication with the target occurs through the defined target interface.

The Evidence Framework also does not access internal ECU state.

This separation provides clear boundaries between:

* what is being tested
* how the test is executed
* how the target behaves
* how the result is evaluated
* how the observation is recorded

---

## Simulation Boundary

The current implementation is completely local and simulated.

It does not provide:

* real CAN communication
* real UDS communication
* physical ECU access
* vehicle-network communication
* production-system testing
* OEM-system integration
* real penetration testing

The `ECUTarget` abstraction provides a software boundary for target
interaction, but no real-world communication adapter is currently implemented.

The project therefore demonstrates the testing architecture and workflow
without introducing external automotive communication.

---

## Future Target Extension

The target abstraction provides an extension point for future compatible test
targets.

Conceptually:

```text
                       +------------------+
                       |                  |
                       v                  v
                 ECUSimulator       Future Target
                       |                  |
                       +--------+---------+
                                |
                                v
                            ECUTarget
                                ^
                                |
                         SecurityTestRunner
                                |
                                v
                        Evidence Framework
```

This diagram represents an architectural possibility, not a current
implementation.

The repository currently uses the simulated ECU only.

No real ECU adapter, CAN adapter, or UDS adapter is implemented.

Any future target would need to satisfy the defined target interaction
contract without requiring changes to the fundamental security-test execution
model.

---

## Phase History

### Phase 1 — Repository Foundation

Phase 1 established the project and development foundation.

It introduced:

* Python project configuration
* pytest-based verification
* repository structure
* documentation structure
* project scope
* initial architectural decisions
* deterministic local development environment

### Phase 2 — ECU Simulation

Phase 2 implemented the deterministic simulated ECU.

It introduced:

* secure mode
* vulnerable mode
* authorization state
* protected operation handling
* request validation
* deterministic response statuses
* structured ECU responses

### Phase 3 — Security Test Architecture

Phase 3 separated security-test execution from the simulated ECU.

It introduced:

* `SecurityTestCase`
* `SecurityTestRunner`
* `TestResult`
* `ECUTarget`
* `ECUAdapter`

The resulting architecture established the target boundary used by later
security tests.

### Phase 4 — Evidence Framework

Phase 4 introduced structured evidence generation.

It added:

* the Evidence model
* mandatory evidence fields
* evidence validation
* `PASS` / `FAIL` semantics
* runtime timestamps
* JSON serialization
* evidence generation from `TestResult`

The Evidence Framework was deliberately kept separate from the ECU and Test
Runner.

### Phase 5 — TC-001 Diagnostic Authorization

Phase 5 introduced the first dedicated security test case:

```text
TC-001 — Diagnostic Authorization
```

TC-001 reuses the existing Phase-3 test architecture and Phase-4 Evidence
Framework.

No new communication layer was required.

The test evaluates the authorization behavior of the simulated ECU and
provides the basis for the subsequent finding, fix, retest, and regression
workflow planned for later phases.

### Phase 6 introduced the second dedicated security test case:

```text
TC-002 — Message Validation
```

TC-002 reuses the existing security-test architecture and Evidence Framework.

The test validates message/request handling through the existing target abstraction 
and does not introduce real automotive communication.

Phase 6 therefore extends the security-test coverage without changing the fundamental 
architectural boundaries established in earlier phases.

---

## Current Architectural Scope

The current implementation provides:

* deterministic ECU simulation
* secure and vulnerable security modes
* authorization handling
* protected operation handling
* request validation
* target abstraction
* security-test execution
* expected-versus-actual evaluation
* structured test results
* structured evidence
* evidence validation
* JSON serialization
* TC-001 Diagnostic Authorization
* TC-002 Message Validation

The following capabilities are outside the current implementation:

* real CAN communication
* real UDS communication
* physical ECU communication
* vehicle-network communication
* production-system testing
* OEM-system integration
* formal vulnerability management
* severity management
* CVSS calculation
* generalized security-finding management
* complete regression orchestration
* CI/CD integration

These capabilities are reserved for later project phases.

---

## Architectural Principles

The current architecture follows several principles.

### 1. Separate the Test from the System Under Test

The security test must not depend directly on the internal implementation of
the ECU simulator.

The target abstraction provides the boundary between test execution and the
system under test.

### 2. Keep Security Behavior in the Target

The simulated ECU is responsible for its security behavior.

The Test Runner must evaluate that behavior rather than implement or replace
it.

### 3. Separate Execution from Evidence

The Test Runner produces a `TestResult`.

The Evidence Framework consumes the completed result and records the
observation.

Evidence generation therefore does not control test execution.

### 4. Keep Expected Security Behavior Independent from the Implementation

The expected result is derived from the security requirement represented by
the test case.

The expected result must not be changed simply to make an insecure
implementation pass.

### 5. Keep the Simulation Deterministic

Equivalent input and target state must produce equivalent target behavior.

This is required for reproducible local security testing.

### 6. Add Future Workflow Stages Only When Their Prerequisites Exist

The project is developed incrementally:

```text
ECU Simulation
       |
       v
Security Test Architecture
       |
       v
Evidence Framework
       |
       v
TC-001
       |
       v
TC-002
       |
       v
Future Security Finding
       |
       v
Future Retest
       |
       v
Future Regression
       |
       v
Future CI/CD
```

Later workflow stages are not implemented inside earlier architectural layers
just to anticipate future functionality.

---

## Architecture and Project Scope

The architecture is intentionally smaller than a real automotive cybersecurity
test environment.

The purpose of the project is to demonstrate how a security requirement can be
translated into a reproducible security test and how the resulting execution
can be evaluated and recorded as structured evidence.

The project does not attempt to reproduce a complete automotive
communication stack, production ECU, or real vehicle environment.

The current architecture therefore provides the minimum separation required
for the demonstrated workflow while keeping the implementation deterministic,
local, and understandable.

The long-term architecture can build additional security workflow stages on
top of these stable boundaries without changing the basic responsibilities of
the existing components.