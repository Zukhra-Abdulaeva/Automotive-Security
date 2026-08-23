
# Architecture

## Purpose

The Automotive Security Regression Lab uses a fully simulated and deterministic architecture for reproducible automotive security testing.

The architecture is intentionally limited to a controlled simulation. It does not implement a real CAN or UDS stack and performs no network communication.

## System Architecture

The current Phase 2 architecture is:

```text
Security Test
      |
      v
ECUSimulator
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
```

The `ECUSimulator` is the central security target of the current implementation.

## Main Components

### ECUSimulator

`ECUSimulator` represents the simulated ECU.

It is responsible for:

* maintaining the configured security mode
* maintaining the authorization state
* validating incoming requests
* processing the protected operation
* applying the configured security policy
* returning deterministic responses

The simulator supports two security modes:

* `secure`
* `vulnerable`

## Request Processing

The simulator accepts diagnostic-style requests with the following basic structure:

```python
{
    "operation": "PROTECTED_OPERATION"
}
```

An optional `parameters` mapping is also accepted for future extensions.

Before security processing takes place, the request is validated.

Invalid requests result in:

```text
INVALID_REQUEST
```

This separates malformed input from security-policy decisions.

## Security Policy

The security policy depends on the configured mode.

### Secure Mode

In secure mode, the protected operation requires explicit authorization.

```text
Unauthorized request
        |
        v
ACCESS_DENIED
```

With authorization:

```text
Authorized request
        |
        v
ACCESS_GRANTED
```

### Vulnerable Mode

In vulnerable mode, the protected operation is intentionally granted without authorization.

```text
Unauthorized request
        |
        v
ACCESS_GRANTED
```

This behavior is intentional and exists to provide a controlled vulnerable state for later security testing and regression testing.

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

The response model is deterministic and can be converted into a dictionary representation using `to_dict()`.

This provides a stable interface for later test, evidence, finding, and regression layers.

## Determinism

The ECU simulation is deterministic.

For the same:

* security mode
* authorization state
* request

the simulator produces the same response.

This property is required for reproducible automated testing.

## Test Boundary

The current Phase 2 test architecture directly exercises the `ECUSimulator`.

```text
pytest test
     |
     v
ECUSimulator
     |
     v
ECUResponse
     |
     v
assertion
```

The test logic remains separated from the ECU implementation.

A dedicated ECU adapter layer is intentionally deferred to a later phase.

## Current Scope

Implemented in Phase 2:

* simulated ECU
* secure security mode
* vulnerable security mode
* authorization state
* protected operation
* request validation
* deterministic response statuses
* structured ECU responses
* automated pytest verification

Deferred to later phases:

* ECU adapter layer
* formal security test architecture
* evidence generation
* security findings
* root-cause analysis
* fix and retest workflow
* broader regression framework
* CI/CD workflow

## Verification

The Phase 2 implementation is verified by six automated pytest tests.

Latest verification result:

```text
6 passed
```

## Architectural Principle

The architecture follows a simple separation:

```text
Test Logic
    |
    v
Security Target
    |
    v
Deterministic Response
```

This separation allows later phases to build evidence, findings, retesting, regression testing, and CI/CD capabilities around the existing deterministic ECU security target without changing the fundamental simulation boundary.
