# Architecture

## Purpose

The Automotive Security Regression Lab uses a fully simulated and deterministic
architecture for reproducible automotive security testing.

Phase 3 introduced a dedicated security test execution architecture that
separates security test logic from the simulated ECU implementation.

Phase 4 adds a dedicated Evidence Framework that records the result of a test
execution without coupling evidence generation to the ECU.

The architecture remains intentionally limited to a controlled simulation.
It does not implement a real CAN or UDS stack and performs no network
communication.

## System Context

The project models an automotive security testing concept in a controlled
Python environment.

The conceptual real-world relationship is:

```text
Security Tester
       |
       v
Diagnostic Interface
       |
       v
Gateway / Communication Layer
       |
       v
ECU
```

The current project abstracts this concept as:

```text
Security Test Case
       |
       v
Test Runner
       |
       v
ECU Adapter
       |
       v
Simulated ECU
       |
       v
Response
       |
       v
Evidence
```

The ECU simulator is the system under test.

No real vehicle, ECU, OEM system, customer data, production credential,
or production network is used.

## Test Architecture

The current architecture consists of five logical responsibilities:

```text
+--------------------------+
| Security Test / Test Case|
+------------+-------------+
             |
             v
+--------------------------+
|       Test Runner        |
+------------+-------------+
             |
             v
+--------------------------+
|       ECU Adapter        |
+------------+-------------+
             |
             v
+--------------------------+
|      ECU Simulator       |
+------------+-------------+
             |
             v
+--------------------------+
|         Response         |
+------------+-------------+
             |
             v
+--------------------------+
|      Evidence Model      |
+--------------------------+
```

The architecture separates:

* security test definition
* test execution
* target interaction
* simulated ECU behavior
* execution evidence

## SecurityTestCase

`SecurityTestCase` provides a minimal representation of a security test.

It currently contains:

* `test_id`
* `description`
* `request`
* `expected_status`

The abstraction provides the technical basis for later concrete security test
cases without implementing the complete test-case documentation defined for
future project phases.

## Test Runner

`SecurityTestRunner` coordinates the execution of a security test case.

Its responsibility is limited to:

1. accepting a test case
2. sending the request through the target interface
3. receiving the ECU response
4. comparing the actual response status with the expected status
5. returning a structured `TestResult`

The runner does not access internal ECU state.

Evidence generation is intentionally implemented as a separate layer. The
Evidence Framework consumes the completed test case and test result rather than
implementing test execution itself.

The runner does not implement:

* finding management
* CI/CD
* regression orchestration
* ECU security policy

## ECU Adapter

`ECUAdapter` separates the test runner from the concrete ECU simulator.

The adapter exposes the target interaction through the `ECUTarget` protocol:

```text
Test Runner
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

The adapter is responsible only for forwarding requests to the configured
target and returning its structured response.

The adapter does not contain security-test logic.

It does not:

* evaluate security findings
* generate evidence
* manage test results
* implement security policy decisions

This keeps the target abstraction independent from the test execution logic.

## ECU Simulator

`ECUSimulator` represents the simulated ECU and remains responsible for the
security behavior implemented in Phase 2.

It is responsible for:

* maintaining the configured security mode
* maintaining the authorization state
* validating incoming requests
* processing the protected operation
* applying the configured security policy
* returning deterministic responses

The simulator supports:

* `secure`
* `vulnerable`

The simulator remains independent from the test runner, adapter, and evidence
layers.

The ECU simulator does not generate or store test evidence.

## Evidence Framework

The Evidence Framework represents one completed security test execution as
structured evidence.

Its responsibility is to document:

* which test was executed
* which target was tested
* which preconditions existed
* which input was used
* what behavior was expected
* what behavior was observed
* whether the observation matched the expectation
* additional notes

The minimum evidence model contains:

* `test_id`
* `timestamp`
* `target`
* `preconditions`
* `input`
* `expected`
* `actual`
* `result`
* `notes`

The Evidence Framework can serialize the evidence model to JSON.

The evidence layer does not implement ECU security behavior and does not
modify the ECU simulator.

## Evidence Flow

A complete Phase 4 execution flow is:

```text
SecurityTestCase
       |
       | request
       v
SecurityTestRunner
       |
       | handle_request()
       v
ECUAdapter
       |
       v
ECUSimulator
       |
       | ECUResponse
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

The Evidence Framework therefore sits after test execution.

This keeps the System Under Test independent from evidence generation.

## Request and Response Flow

A security test execution follows this flow:

```text
SecurityTestCase
       |
       | request
       v
SecurityTestRunner
       |
       | handle_request()
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
       | compare expected/actual status
       v
TestResult
```

Evidence generation then consumes the completed execution result:

```text
TestResult
       |
       v
EvidenceGenerator
       |
       v
Evidence
```

## Response Model

The simulator returns an `ECUResponse`.

The response contains:

* `status`
* `operation`

The available response statuses are:

```text
ACCESS_GRANTED
ACCESS_DENIED
INVALID_REQUEST
```

The response model is deterministic and can be converted into a dictionary
representation using `to_dict()`.

## Security Behavior

### Secure Mode

An unauthorized protected operation results in:

```text
PROTECTED_OPERATION
       |
       v
ACCESS_DENIED
```

An authorized protected operation results in:

```text
PROTECTED_OPERATION
       |
       v
ACCESS_GRANTED
```

### Vulnerable Mode

In vulnerable mode, the protected operation is intentionally granted without
authorization:

```text
PROTECTED_OPERATION
       |
       v
ACCESS_GRANTED
```

This behavior provides a controlled vulnerable state for security testing.

## Invalid Requests

Unknown operations are rejected by the simulator:

```text
Unknown operation
       |
       v
INVALID_REQUEST
```

Invalid request handling remains the responsibility of the ECU simulator.

The test runner only evaluates the response returned by the target.

## Evidence Result Semantics

The Evidence Framework supports two execution results:

```text
PASS
FAIL
```

`PASS` means:

```text
expected == actual
```

`FAIL` means:

```text
expected != actual
```

A `FAIL` result documents a mismatch between expected and observed behavior.

It does not automatically constitute a security vulnerability finding.

Finding assessment belongs to a later project phase.

## Determinism

The ECU simulation is deterministic.

For the same:

* security mode
* authorization state
* request

the simulator produces the same response.

Evidence generation does not require:

* network access
* physical hardware
* a real ECU
* external services
* random test data

The timestamp is generated at runtime and is intentionally time-dependent.

All other evidence content is derived from the test execution context.

## Architectural Separation

The key architectural principle is:

```text
Security Test Logic
        |
        v
    Test Runner
        |
        v
    ECU Adapter
        |
        v
   Security Target
        |
        v
    Test Result
        |
        v
     Evidence
```

The security test does not depend on internal simulator attributes such as:

```text
_internal_state
_authorized
_security_policy
```

Instead, communication occurs through the defined target interface.

The Evidence Framework does not access these internal simulator attributes.

This improves:

* testability
* maintainability
* target abstraction
* reproducibility
* separation of responsibilities

## Simulation Boundary

The current implementation is fully simulated.

It does not provide:

* real CAN communication
* real UDS communication
* physical ECU access
* vehicle network access
* production-system testing
* real penetration testing

The adapter architecture provides an abstraction boundary at the target
interface, but no real-world communication adapter is currently implemented.

## Future Extension

A future implementation could theoretically replace the simulated target
behind the adapter boundary with another compatible test target.

Conceptually:

```text
                 +------------------+
                 |                  |
                 v                  v
            ECU Simulator     Future Target
                 |                  |
                 +--------+---------+
                          |
                          v
                      ECUTarget
                          ^
                          |
                     Test Runner
                          |
                          v
                  Evidence Framework
```

This is a possible future extension only.

No real ECU or communication adapter is implemented.

## Phase 4 Scope

Implemented in Phase 4:

* structured evidence model
* mandatory evidence fields
* evidence validation
* `PASS` / `FAIL` semantics
* runtime timestamp
* JSON serialization
* integration with the existing Phase 3 test result
* separation of evidence generation from the ECU
* deterministic local tests

Not implemented in Phase 4:

* security finding management
* severity management
* CVSS calculation
* root-cause management
* fix tracking
* retest workflow
* complete security regression suite
* CI/CD pipeline
* real ECU communication
* real vehicle communication

## Security Finding Boundary

Evidence is not a vulnerability finding.

Evidence answers:

```text
What was tested?
What was expected?
What actually happened?
What was the test result?
```

A later finding process may answer:

```text
Is this a security issue?
Why?
What is the impact?
What is the root cause?
How should it be fixed?
```

These responsibilities remain intentionally separated.

## Architectural Principle

The central Phase 4 principle is:

**Keep evidence structured and separate from the system under test.**

The ECU is the simulated target.

The Test Runner is the test mechanism.

The Adapter connects the test mechanism to the target.

The Evidence Framework documents the resulting test observation.

This separation provides the architectural foundation for later finding,
retest, regression, and CI/CD capabilities without implementing those future
phases prematurely.