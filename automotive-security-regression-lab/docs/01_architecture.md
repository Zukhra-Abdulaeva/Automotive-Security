# Architecture

## Purpose

The Automotive Security Regression Lab uses a fully simulated and deterministic
architecture for reproducible automotive security testing.

Phase 3 introduces a dedicated security test execution architecture that
separates security test logic from the simulated ECU implementation.

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
Security Test
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
```

The ECU simulator is the system under test.

No real vehicle, ECU, OEM system, customer data, production credential,
or production network is used.

## Test Architecture

The Phase 3 architecture consists of four main runtime components:

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
+--------------------------+
```

The architecture separates the test mechanism from the implementation of the
system under test.

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

It does not implement:

* evidence generation
* finding management
* CI/CD
* regression orchestration

The current implementation is intentionally small.

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
<<<<<<< HEAD
      |
      v
Request Validation
      |
      v
Security Policy
      |
      +-------------------+
      |                   |
   secure             vulnerable
      |                   |
      v                   v
Authorization       Access Granted
      |
   +--+--+
   |     |
 denied granted
   |     |
   v     v
Access   Access
Denied   Granted
      \   /
       \ /
        v
    ECUResponse
=======
>>>>>>> 1f817c1 (Update project structure and tests)
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

The simulator remains independent from the test runner and adapter layers.

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

The test runner therefore interacts with the target through a defined
interface rather than accessing simulator internals.

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

## Determinism

The ECU simulation is deterministic.

For the same:

* security mode
* authorization state
* request

the simulator produces the same response.

This property supports reproducible automated testing.

## Architectural Separation

The key Phase 3 principle is:

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
```

The security test does not depend on internal simulator attributes such as:

```text
_internal_state
_authorized
_security_policy
```

Instead, communication occurs through the defined target interface.

This improves:

* testability
* maintainability
* target abstraction
* future extensibility

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
```

This is a possible future extension only.

No real ECU or communication adapter is implemented in Phase 3.

## Phase 3 Verification

The Phase 3 architecture was functionally exercised through three scenarios:

| Scenario                         | Expected          | Actual            | Result |
| -------------------------------- | ----------------- | ----------------- | ------ |
| Unauthorized protected operation | `ACCESS_DENIED`   | `ACCESS_DENIED`   | PASS   |
| Authorized protected operation   | `ACCESS_GRANTED`  | `ACCESS_GRANTED`  | PASS   |
| Invalid operation                | `INVALID_REQUEST` | `INVALID_REQUEST` | PASS   |

The existing pytest suite was also executed:

```text
10 passed in 0.04s
```

```text
TC-ARCH-001 → ACCESS_DENIED   PASS
TC-ARCH-002 → ACCESS_GRANTED  PASS
TC-ARCH-003 → INVALID_REQUEST PASS
```

## Phase 3 Scope

Implemented in Phase 3:

* security test case abstraction
* security test runner
* ECU target protocol
* ECU adapter
* separation between test execution and ECU implementation
* deterministic architecture verification

Not implemented in Phase 3:

* Evidence Framework
* evidence files
* execution IDs
* CI/CD artifacts
* complete regression suite
* security finding management
* root-cause workflow
* real ECU communication

These capabilities belong to later project phases.

## Architectural Principle

The central Phase 3 principle is:

**Separate the security test from the system under test.**

<<<<<<< HEAD
This separation allows later phases to build evidence, findings, retesting, regression testing, and CI/CD capabilities around the existing deterministic ECU security target without changing the fundamental simulation boundary.
=======
The ECU is the simulated target.

The Test Runner is the test mechanism.

The Adapter connects the two.

This separation provides the architectural foundation for later evidence,
finding, retest, regression, and CI/CD capabilities without implementing those
future phases prematurely.
>>>>>>> 1f817c1 (Update project structure and tests)
