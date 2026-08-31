# TC-002 — Message Validation

## 1. Scenario

A diagnostic requester submits a diagnostic-style request to the simulated ECU.

TC-002 verifies that the simulated ECU validates the request structure, operation, parameter values, and ECU operational state before security-relevant operation processing.

The test covers the following message-validation scenarios:

* malformed diagnostic input
* unsupported diagnostic operation
* parameter value outside the permitted range
* protected operation requested while the ECU is in a blocked state

The simulated ECU exposes deterministic response statuses for these conditions.

This test case represents a simulated automotive security concept and does not implement real UDS, CAN communication, a real ECU, or a real vehicle.

---

## 2. Objective

The objective of TC-002 is to verify that invalid or unsupported diagnostic requests are handled deterministically before the protected operation is granted.

The test verifies that:

* malformed requests are rejected as `INVALID_REQUEST`
* unsupported operations are rejected as `UNSUPPORTED_OPERATION`
* parameter values outside the permitted range are rejected as `REQUEST_REJECTED`
* protected operations are rejected while the ECU is in the `BLOCKED` state
* valid boundary parameter values are accepted when the ECU is authorized
* expected and actual ECU responses are compared by the Security Test Runner
* the resulting test execution is represented through the existing Evidence Framework

The test therefore evaluates message-validation behavior rather than only normal functional behavior.

---

## 3. Scope

TC-002 is limited to request validation and request-state handling implemented by the simulated ECU.

In scope:

* diagnostic request structure
* operation validation
* supported operation validation
* parameter structure validation
* parameter value range validation
* ECU operational state validation
* valid parameter boundary values
* deterministic response statuses
* expected versus actual behavior
* security-test execution
* security-test evidence

The protected operation used by the implemented scenarios is:

`PROTECTED_OPERATION`

The permitted parameter range is:

```text
MIN_PARAMETER_VALUE = 0
MAX_PARAMETER_VALUE = 255
```

Out of scope:

* real vehicle communication
* real ECU communication
* real CAN communication
* real UDS implementation
* external systems
* customer data
* productive systems
* network communication
* complete security finding management
* CVSS calculation
* complete regression suite
* CI/CD implementation

---

## 4. Information Gathering

The information required to execute TC-002 is defined by the simulated ECU interface and the existing test implementation.

### Diagnostic request structure

The simulated ECU accepts a diagnostic-style request represented as a mapping.

The supported request structure is:

```text
{
    "operation": "PROTECTED_OPERATION",
    "parameters": {
        "value": 0..255
    }
}
```

The `parameters` field is optional for backwards compatibility with TC-001.

### Supported operation

The simulated ECU currently supports:

```text
PROTECTED_OPERATION
```

An operation with a different value is treated as unsupported.

### Parameter range

The permitted integer parameter range is:

```text
0..255
```

The boundary values are therefore:

```text
0
255
```

Both boundary values are explicitly verified by the existing tests.

### ECU operational state

The simulated ECU supports the following operational states:

```text
READY
BLOCKED
```

A protected operation requested while the ECU is in the `BLOCKED` state must be rejected.

### Response statuses

The simulated ECU exposes the following deterministic response statuses:

```text
ACCESS_GRANTED

ACCESS_DENIED

INVALID_REQUEST

UNSUPPORTED_OPERATION

REQUEST_REJECTED
```

TC-002 specifically verifies:

```text
INVALID_REQUEST

UNSUPPORTED_OPERATION

REQUEST_REJECTED
```

The information used by this test is derived exclusively from the controlled simulation.

No external target or real automotive system is required.

---

## 5. Threat Model

### Asset

Protected Diagnostic Operation and the integrity of diagnostic request processing.

### Threat

An invalid, malformed, unsupported, or otherwise impermissible diagnostic request is processed as though it were a valid request.

### Potential attacker

A diagnostic requester capable of submitting requests to the modeled diagnostic interface.

### Security property

Invalid or impermissible requests must be rejected according to their defined validation condition before the protected operation is granted.

### Security assumption

The simulated ECU is responsible for validating the incoming request and enforcing the applicable operational-state restrictions.

The threat model is intentionally limited to the behavior represented by the simulation.

---

## 6. Attack Surface

The modeled diagnostic attack surface is:

```text
Diagnostic Interface
        |
        v
Request Structure
        |
        v
Operation Validation
        |
        v
Parameter Validation
        |
        v
ECU State Validation
        |
        v
Security-Relevant Operation
        |
        v
Response
```

The interface represents a simulated test surface.

No real CAN, UDS, vehicle network, ECU, or external diagnostic endpoint is used.

---

## 7. Attack Hypothesis

If request validation is missing or incorrectly enforced, a diagnostic requester may be able to submit malformed, unsupported, out-of-range, or state-incompatible requests that are processed as valid operations.

TC-002 tests this hypothesis by submitting deterministic invalid or impermissible requests to the simulated ECU.

The test verifies that the ECU does not grant the protected operation when request validation or ECU-state requirements are violated.

---

## 8. Test Setup

The test uses the existing security-test architecture:

```text
TC-002
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

The TC-002 implementation creates a secure simulated ECU:

```text
SecurityMode.SECURE
```

The `ECUAdapter` exposes the simulator through the target interface used by the `SecurityTestRunner`.

The `SecurityTestRunner` executes each `SecurityTestCase` and compares the actual ECU response status with the expected response status.

The Evidence Framework represents the resulting test execution as structured evidence.

The test does not depend on the internal request-validation implementation for determining the expected result. The ECU remains the system under test, and TC-002 evaluates its externally observable response.

For the unexpected-state scenario, the explicit ECU state is established as a test precondition.

---

## 9. Preconditions

TC-002 uses scenario-specific preconditions.

### Scenario A — Invalid Input

The request does not contain a valid operation.

The implemented request is:

```text
{
    "parameters": {}
}
```

Expected response:

```text
INVALID_REQUEST
```

### Scenario B — Unsupported Operation

The request contains an operation that is not supported by the simulated ECU.

The implemented request is:

```text
{
    "operation": "UNSUPPORTED_OPERATION"
}
```

Expected response:

```text
UNSUPPORTED_OPERATION
```

### Scenario C — Boundary Condition

The request uses the protected operation with a parameter value above the permitted range.

The implemented request is:

```text
{
    "operation": "PROTECTED_OPERATION",
    "parameters": {
        "value": 256
    }
}
```

The permitted maximum is:

```text
255
```

Expected response:

```text
REQUEST_REJECTED
```

### Scenario D — Unexpected ECU State

The ECU is explicitly configured as authorized and blocked.

Preconditions:

```text
authorization = true
ecu_state = BLOCKED
```

The request is:

```text
{
    "operation": "PROTECTED_OPERATION",
    "parameters": {
        "value": 100
    }
}
```

Expected response:

```text
REQUEST_REJECTED
```

### Valid Boundary Values

The parameter boundary values are also verified independently.

The ECU is configured as authorized:

```text
authorization = true
```

The following values are tested:

```text
0
255
```

Both values are within the permitted range and are expected to be accepted.

Expected response:

```text
ACCESS_GRANTED
```

---

## 10. Test Execution

### Test A — Invalid Input

The test submits:

```text
{
    "parameters": {}
}
```

Expected behavior:

```text
INVALID_REQUEST
```

The actual ECU response is compared against the expected response.

A conforming execution produces:

```text
Expected = INVALID_REQUEST
Actual   = INVALID_REQUEST
Result   = PASS
```

### Test B — Unsupported Operation

The test submits:

```text
{
    "operation": "UNSUPPORTED_OPERATION"
}
```

Expected behavior:

```text
UNSUPPORTED_OPERATION
```

A conforming execution produces:

```text
Expected = UNSUPPORTED_OPERATION
Actual   = UNSUPPORTED_OPERATION
Result   = PASS
```

### Test C — Boundary Condition

The test submits:

```text
{
    "operation": "PROTECTED_OPERATION",
    "parameters": {
        "value": 256
    }
}
```

The permitted range ends at:

```text
255
```

Expected behavior:

```text
REQUEST_REJECTED
```

A conforming execution produces:

```text
Expected = REQUEST_REJECTED
Actual   = REQUEST_REJECTED
Result   = PASS
```

### Test D — Unexpected ECU State

The ECU is configured with:

```text
authorization = true
ecu_state = BLOCKED
```

The test submits:

```text
{
    "operation": "PROTECTED_OPERATION",
    "parameters": {
        "value": 100
    }
}
```

Expected behavior:

```text
REQUEST_REJECTED
```

A conforming execution produces:

```text
Expected = REQUEST_REJECTED
Actual   = REQUEST_REJECTED
Result   = PASS
```

The test therefore verifies that authorization alone does not permit the protected operation while the ECU is in the blocked state.

### Result Evaluation

For every TC-002 scenario, the `SecurityTestRunner` compares:

```text
Expected Status
      |
      v
Actual Status
```

The test passes when:

```text
Expected == Actual
```

The test fails when:

```text
Expected != Actual
```

The resulting `TestResult` contains:

```text
test_id

expected_status

actual_status

passed
```

---

## 11. Expected Behavior

The simulated ECU shall reject invalid or impermissible diagnostic requests according to the validation rule represented by each scenario.

The expected behavior is:

```text
Scenario                    Input Condition             Expected Response

TC-002-A                    Missing operation           INVALID_REQUEST

TC-002-B                    Unsupported operation       UNSUPPORTED_OPERATION

TC-002-C                    value = 256                 REQUEST_REJECTED

TC-002-D                    ECU state = BLOCKED        REQUEST_REJECTED
                            authorization = true
```

The permitted parameter boundaries are:

```text
value = 0     -> ACCESS_GRANTED

value = 255   -> ACCESS_GRANTED
```

when the ECU is authorized and otherwise in an acceptable operational state.

The validation behavior is therefore:

```text
Invalid Request
      |
      v
INVALID_REQUEST

Unsupported Operation
      |
      v
UNSUPPORTED_OPERATION

Out-of-Range Parameter
      |
      v
REQUEST_REJECTED

Blocked ECU State
      |
      v
REQUEST_REJECTED
```

---

## 12. Actual Behavior

The actual behavior is obtained from the simulated ECU during test execution.

The test implementation does not hard-code the actual result into the test case documentation.

For each execution, the `SecurityTestRunner` sends the request through the `ECUAdapter` to the simulated ECU and records the returned `ResponseStatus`.

For conforming executions, the observed responses are:

```text
TC-002-A -> INVALID_REQUEST

TC-002-B -> UNSUPPORTED_OPERATION

TC-002-C -> REQUEST_REJECTED

TC-002-D -> REQUEST_REJECTED
```

For the valid boundary-value verification:

```text
value = 0   -> ACCESS_GRANTED

value = 255 -> ACCESS_GRANTED
```

The actual execution result must be taken from the test execution rather than hard-coded into the test case documentation.

---

## 13. Evidence

TC-002 uses the Evidence Framework established in Phase 4.

The same evidence model is reused for every TC-002 execution.

A conforming TC-002 execution is represented by the relationship:

```text
Security Requirement
        |
        v
Security Test
        |
        v
Test Execution
        |
        v
Expected vs Actual
        |
        v
TestResult
        |
        v
Evidence
```

For example, TC-002-A may produce:

```json
{
  "test_id": "TC-002-A",
  "timestamp": "2026-08-29T12:00:00.000000Z",
  "target": "simulated-ecu",
  "preconditions": {},
  "input": {
    "parameters": {}
  },
  "expected": "INVALID_REQUEST",
  "actual": "INVALID_REQUEST",
  "result": "PASS",
  "notes": "Malformed request without an operation must be rejected."
}
```

TC-002-B may produce:

```json
{
  "test_id": "TC-002-B",
  "timestamp": "2026-08-29T12:00:00.000000Z",
  "target": "simulated-ecu",
  "preconditions": {},
  "input": {
    "operation": "UNSUPPORTED_OPERATION"
  },
  "expected": "UNSUPPORTED_OPERATION",
  "actual": "UNSUPPORTED_OPERATION",
  "result": "PASS",
  "notes": "Unsupported diagnostic operation must be rejected."
}
```

TC-002-C may produce:

```json
{
  "test_id": "TC-002-C",
  "timestamp": "2026-08-29T12:00:00.000000Z",
  "target": "simulated-ecu",
  "preconditions": {},
  "input": {
    "operation": "PROTECTED_OPERATION",
    "parameters": {
      "value": 256
    }
  },
  "expected": "REQUEST_REJECTED",
  "actual": "REQUEST_REJECTED",
  "result": "PASS",
  "notes": "Parameter value above the permitted range must be rejected."
}
```

TC-002-D may produce:

```json
{
  "test_id": "TC-002-D",
  "timestamp": "2026-08-29T12:00:00.000000Z",
  "target": "simulated-ecu",
  "preconditions": {
    "authorization": true,
    "ecu_state": "BLOCKED"
  },
  "input": {
    "operation": "PROTECTED_OPERATION",
    "parameters": {
      "value": 100
    }
  },
  "expected": "REQUEST_REJECTED",
  "actual": "REQUEST_REJECTED",
  "result": "PASS",
  "notes": "Protected operation must be rejected while ECU is blocked."
}
```

The timestamps shown in the examples are illustrative.

Actual evidence timestamps are generated dynamically by the existing Evidence Framework at execution time.

Evidence documents the test observation and result.

It does not by itself constitute a formal security finding.

---

## 14. Vulnerability Assessment

If the simulated ECU accepts an invalid request or processes an impermissible request contrary to the expected validation behavior, the observed behavior represents a deviation from the message-validation requirement tested by TC-002.

Examples include:

```text
Invalid request
      |
      v
Unexpectedly processed
      |
      v
Security-relevant deviation
```

or:

```text
Out-of-range parameter
      |
      v
Protected operation accepted
      |
      v
Security-relevant deviation
```

The exact classification of such a deviation depends on the applicable security assessment process.

No CVSS score or formal severity classification is assigned by TC-002.

A `FAIL` result documents that expected and actual behavior differ.

It does not automatically constitute a formal security finding.

Formal Security Finding Management is outside the scope of TC-002.

---

## 15. Root Cause

TC-002 does not automatically determine a root cause from a failed execution.

The test establishes whether the simulated ECU response matches the expected message-validation behavior.

A failed execution may indicate that one of the modeled validation controls is missing or incorrectly enforced.

Potential areas for later root-cause analysis include:

```text
Request Parsing
      |
      v
Operation Validation
      |
      v
Parameter Validation
      |
      v
ECU State Validation
      |
      v
Operation Processing
```

Root-cause determination is outside the responsibility of the Evidence Framework and the test-result comparison.

Any root-cause statement must therefore be based on the actual implementation and execution evidence.

---

## 16. Recommendation

The simulated ECU should validate diagnostic requests before allowing security-relevant operation processing.

The modeled validation sequence should ensure that:

```text
Request
  |
  v
Structure Valid
  |
  v
Operation Supported
  |
  v
Parameters Valid
  |
  v
ECU State Permits Operation
  |
  v
Security-Relevant Processing
```

Invalid requests, unsupported operations, out-of-range parameters, and requests incompatible with the ECU operational state should be rejected according to the defined response semantics.

The expected result is defined by the security test. It must not be modified to accommodate the observed ECU behavior.

---

## 17. Fix

The secure simulated ECU implements the validation behavior required by the TC-002 scenarios.

The implemented validation includes:

```text
Request must be a mapping
        |
        v
Operation must be a non-empty string
        |
        v
Operation must be supported
        |
        v
Parameters must be a mapping
        |
        v
Parameter value must be an integer
        |
        v
Boolean values are not accepted as integers
        |
        v
Parameter value must be within 0..255
        |
        v
ECU state must permit operation
```

Only after these validation steps does the simulated ECU evaluate the authorization and security mode for the protected operation.

The test implementation therefore verifies the behavior of the ECU rather than replacing the ECU validation logic.

The Test Runner and Evidence Framework remain responsible for test execution and evidence representation respectively.

---

## 18. Retest

After any simulated validation fix, TC-002 must be executed again.

The same security test cases are used.

The retest must not replace the original security test with a new test that only produces the desired result.

The TC-002 retest flow is:

```text
Observed Validation Deviation
        |
        v
Evidence
        |
        v
Fix
        |
        v
Same TC-002
        |
        v
Retest
        |
        v
Expected Validation Behavior
```

The expected retest behavior is:

```text
TC-002-A -> INVALID_REQUEST

TC-002-B -> UNSUPPORTED_OPERATION

TC-002-C -> REQUEST_REJECTED

TC-002-D -> REQUEST_REJECTED
```

The valid parameter boundaries must remain accepted:

```text
value = 0   -> ACCESS_GRANTED

value = 255 -> ACCESS_GRANTED
```

The retest therefore verifies both rejection behavior and preservation of the defined valid boundary conditions.

---

## 19. Regression Test

TC-002 provides the technical basis for future regression coverage of message-validation behavior.

The essential properties are:

```text
Malformed request
      |
      v
INVALID_REQUEST
```

```text
Unsupported operation
      |
      v
UNSUPPORTED_OPERATION
```

```text
Out-of-range parameter
      |
      v
REQUEST_REJECTED
```

```text
Protected operation + BLOCKED state
      |
      v
REQUEST_REJECTED
```

and:

```text
Authorized + valid boundary value 0
      |
      v
ACCESS_GRANTED
```

```text
Authorized + valid boundary value 255
      |
      v
ACCESS_GRANTED
```

These checks can later be incorporated into the project's broader regression architecture.

The current TC-002 implementation does not introduce a separate regression-management workflow or a complete regression suite.

---

## Phase 6 Boundary

TC-002 is a controlled automotive security simulation.

It does not represent:

```text
a real penetration test

a real ECU assessment

a real vehicle test

a real UDS implementation

a real CAN communication test

a complete vulnerability-management process

a complete regression suite

a CI/CD pipeline

a real automotive diagnostic endpoint
```

The validation behavior exists only within the deterministic simulated ECU.

The Security Test Runner executes the defined scenarios.

The ECU simulator provides the system-under-test behavior.

The ECU adapter provides the target interface.

The Evidence Framework documents the resulting test observations.

The current TC-002 implementation therefore establishes a deterministic message-validation security test using the existing security-test and evidence architecture. It does not introduce a separate finding-management, remediation-management, regression-management, or CI/CD workflow.
