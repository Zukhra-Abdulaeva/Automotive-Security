# Evidence Format

## Purpose

The Evidence Framework provides a structured, reproducible, and machine-readable representation of one security test execution.

The evidence format defines the structured representation of a completed security test execution in the Automotive Security Regression Lab.

Evidence provides a reproducible record of:

```text
test_id
timestamp
target
preconditions
input
expected
actual
result
notes
```

The same evidence model is used for the existing security test scenarios and for the TC-003 regression workflow.

Evidence records the relationship between:

```text
Security Test
      |
      v
Observation
      |
      v
Evidence
```

The framework documents what was tested, under which conditions, what was expected, what was actually observed, and whether the observed behavior matched the expected behavior.

The evidence is generated exclusively from the simulated test environment.

No real ECU data, production credentials, vehicle data, network traffic, or customer data is required.

Phase 8 uses the resulting evidence as an input to structured example finding documentation.

The Evidence Framework itself remains unchanged. It records test execution observations; the Phase-8 finding documents assess and document selected security-relevant observations.

## Evidence Model

Evidence is represented by the `Evidence` model in `security_lab.evidence`.

Each evidence record represents one executed security test case.

The model contains the following fields:

```text
test_id
timestamp
target
preconditions
input
expected
actual
result
notes
```

The required fields are:

| Field           | Description                                       |
| --------------- | ------------------------------------------------- |
| `test_id`       | Identifier of the executed security test          |
| `timestamp`     | UTC timestamp of the evidence creation            |
| `target`        | Test target against which the test was executed   |
| `preconditions` | Conditions that were established before execution |
| `input`         | Input used by the security test                   |
| `expected`      | Behavior expected by the test                     |
| `actual`        | Behavior actually observed                        |
| `result`        | Test execution result: `PASS` or `FAIL`           |
| `notes`         | Additional execution context or observations      |

The `test_id` identifies the test case associated with the execution.

The `timestamp` records when the evidence was generated.

The `target` identifies the security target used for the execution.

The `preconditions` record security-relevant conditions established before execution.

The `input` contains the request presented to the target.

The `expected` value represents the security behavior defined by the test case.

The `actual` value represents the response observed during execution.

The `result` represents the evaluated evidence result.

The `notes` field provides additional execution context.

The model is intentionally simple and can be extended later with optional fields such as `software_version`, `test_environment`, or `execution_id`.

## Required Fields

The following fields are mandatory:

```text
test_id
timestamp
target
preconditions
input
expected
actual
result
notes
```

Evidence without the mandatory fields must not be treated as valid evidence.

The Evidence Framework validates the required structure before evidence is accepted or serialized.

## Timestamp

The timestamp is generated dynamically when evidence is created.

It uses an ISO 8601 UTC representation.

Example:

```text
2026-08-23T21:52:16.789923Z
```

Tests must not depend on a fixed timestamp.

The timestamp is part of the execution evidence and identifies when the evidence record was generated.

## Result Semantics

Evidence supports two results:

```text
PASS
FAIL
```

### PASS

`PASS` means:

```text
expected == actual
```

The observed behavior matched the behavior expected by the test.

### FAIL

`FAIL` means:

```text
expected != actual
```

The observed behavior did not match the behavior expected by the test.

A `FAIL` result does **not** by itself confirm a security vulnerability.

It only documents that the observed behavior differed from the expected behavior.

Security assessment, finding classification, root-cause analysis, and impact assessment are outside the scope of the Evidence Framework.

## Evidence Generation

Evidence is generated through `EvidenceGenerator`.

The generator receives:

```text
SecurityTestCase
TestResult
target
preconditions
notes
```

The expected and actual response values are derived from the executed test result.

The evidence result is derived from the comparison of expected and actual behavior:

```text
expected == actual
        |
        v
      PASS

expected != actual
        |
        v
      FAIL
```

The generated evidence is validated before it is returned.

The EvidenceGenerator therefore connects the executed security test result with the structured Evidence model.

It does not independently execute the security test and does not implement the ECU security policy.

## Evidence Validation

`Evidence.validate()` verifies the structural and semantic consistency of an evidence record.

The validation includes:

```text
required fields are present
preconditions are a mapping
result is PASS or FAIL
timestamp is valid ISO-8601 with timezone information
result matches the expected/actual comparison
```

An evidence record is therefore considered valid only when its declared result is consistent with the recorded expected and actual behavior.

For example:

```text
expected = ACCESS_DENIED
actual   = ACCESS_DENIED
result   = PASS
```

is consistent.

The following is inconsistent:

```text
expected = ACCESS_DENIED
actual   = ACCESS_GRANTED
result   = PASS
```

because the expected and actual values differ.

An invalid evidence record causes evidence validation to fail and must not be treated as a valid evidence artifact.

## JSON Serialization

Evidence can be converted into a JSON-compatible dictionary using `Evidence.to_dict()` and serialized using `Evidence.to_json()`.

Evidence can also be reconstructed from a dictionary using `Evidence.from_dict()`.

Example:

```json
{
  "actual": "ACCESS_DENIED",
  "expected": "ACCESS_DENIED",
  "input": {
    "operation": "PROTECTED_OPERATION"
  },
  "notes": "Unauthorized protected operation was rejected.",
  "preconditions": {
    "authorization": false
  },
  "result": "PASS",
  "target": "simulated-ecu",
  "test_id": "TC-001",
  "timestamp": "2026-08-23T21:52:16.789923Z"
}
```

The timestamp in an actual evidence record is generated at runtime and is not a fixed value.

JSON serialization provides a machine-readable representation that can later be consumed by automation or stored as a test artifact.

CI/CD pipeline implementation is outside the scope of the Evidence Framework.

## Security Testing Context

A security test may establish a security requirement such as:

```text
Protected operation requires authorization.
```

A corresponding test may use:

```text
Authorization = false
Operation = PROTECTED_OPERATION
Expected = ACCESS_DENIED
```

If the simulated ECU returns:

```text
Actual = ACCESS_GRANTED
```

the resulting evidence is:

```text
result = FAIL
```

This evidence documents the observed test result.

It does not automatically create a security finding.

The conceptual distinction is:

```text
Security Test
      |
      v
Observation
      |
      v
Evidence
      |
      v
Security Finding
```

Finding management is outside the scope of the Evidence Framework.

Phase 8 nevertheless consumes existing evidence as supporting information for the example findings SEC-001 and SEC-002.

This does not extend the Evidence Framework into a finding-management system.

## Architectural Boundary

The Evidence Framework is separated from the ECU simulation.

The ECU remains the System Under Test and has no knowledge of evidence generation.

The intended architecture is:

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
ECU Simulator
        |
        v
Response
        |
        v
TestResult
        |
        v
EvidenceGenerator
        |
        v
Evidence
```

The Evidence Framework consumes the result of test execution and represents the observation in a structured form.

It does not implement ECU security policy.

## Determinism

Evidence generation does not require:

* network access
* physical hardware
* a real ECU
* external services
* random test data

The Evidence Framework can therefore be tested locally and reproducibly.

The current evidence generation is deterministic with respect to the test input, expected behavior, actual behavior, and explicitly supplied preconditions.

The timestamp is intentionally runtime-generated and is the only time-dependent field in the evidence record.

The current regression implementation uses the deterministic `ECUSimulator` as its target.

No external network communication or external ECU availability is required for the TC-003 evidence test.

## Phase 4 Scope

Implemented in Phase 4:

* structured evidence model
* mandatory field validation
* `PASS` / `FAIL` semantics
* runtime timestamp
* JSON serialization
* integration with the existing Phase 3 test result
* deterministic local evidence tests

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

## Phase 5 — TC-001 Evidence Integration

Phase 5 introduced the first dedicated security test:

```text
TC-001 — Diagnostic Authorization
```

The existing Evidence Framework was reused to record TC-001 executions.

TC-001 evidence represents the relationship between:

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

For the unauthorized TC-001 scenario, the expected secure behavior is:

```text
ACCESS_DENIED
```

A controlled vulnerable execution may produce:

```text
Actual = ACCESS_GRANTED
```

which results in:

```text
result = FAIL
```

The Evidence Framework does not determine whether the observed deviation constitutes a formal security finding.

Phase 5 therefore extended the practical use of the Evidence Framework without changing its fundamental model or architectural boundary.

No separate evidence architecture was introduced for TC-001.

---

## Phase 6 — TC-002 Evidence Integration

Phase 6 introduced the second dedicated security test:

```text
TC-002 — Message Validation
```

The existing Evidence Framework is reused for TC-002 executions.

TC-002 verifies that invalid request structures or unsupported operations are rejected before security-relevant operation processing.

For a malformed or otherwise invalid request, the expected response is:

```text
INVALID_REQUEST
```

A conforming execution therefore produces:

```text
Expected = INVALID_REQUEST
Actual   = INVALID_REQUEST
Result   = PASS
```

For an unsupported operation, the current simulator distinguishes the operation from a malformed request:

```text
Expected = UNSUPPORTED_OPERATION
Actual   = UNSUPPORTED_OPERATION
Result   = PASS
```

If the target returns a different response, the evidence records a failed comparison:

```text
Expected != Actual
Result   = FAIL
```

The `FAIL` represents an observed deviation from the message-validation requirement. It does not automatically constitute a formal security finding.

TC-002 uses the same evidence model and serialization mechanism established in Phase 4.

No separate evidence format is introduced for TC-002.

---

## Phase 7 — TC-003 Regression Evidence Integration

Phase 7 introduces the TC-003 Regression Workflow.

TC-003 uses the existing Evidence Framework to represent the result of a regression retest.

It does not introduce a separate evidence model, evidence schema, or serialization mechanism.

The regression test uses the existing TC-001 `SecurityTestCase` and the existing security test execution architecture.

The regression workflow is:

```text
SecurityTestCase
      |
      v
SecurityTestRunner
      |
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
Evidence.validate()
```

The implemented TC-003 regression evidence test verifies that the generated evidence represents the executed secure retest.

The regression test verifies, among other fields:

```text
test_id       == TC-001
target        == simulated-ecu
authorization == False
expected      == ACCESS_DENIED
actual        == ACCESS_DENIED
result        == PASS
```

The generated evidence is then validated using:

```text
Evidence.validate()
```

This demonstrates that TC-003 applies the existing evidence model to a regression execution.

The controlled vulnerable-state reproduction is:

```text
SecurityMode.VULNERABLE
Authorization = false
Operation = PROTECTED_OPERATION
Expected = ACCESS_DENIED
Actual = ACCESS_GRANTED
Result = FAIL
```

This evidence represents the modeled pre-fix security deviation.

The secure regression retest is:

```text
SecurityMode.SECURE
Authorization = false
Operation = PROTECTED_OPERATION
Expected = ACCESS_DENIED
Actual = ACCESS_DENIED
Result = PASS
```

The regression evidence is generated from the executed `TestResult`.

TC-003 also verifies that authorized behavior remains available:

```text
Authorization = true
Operation = PROTECTED_OPERATION
Expected = ACCESS_GRANTED
Actual = ACCESS_GRANTED
Result = PASS
```

The TC-003 evidence workflow therefore records the secure regression retest and the authorized-behavior verification using the existing Evidence model.

No separate evidence format is introduced for TC-003.

## Evidence and Regression Evaluation

Evidence records the result of the executed test.

It does not independently determine whether the underlying security requirement is correct.

For TC-003, the expected behavior is defined by the regression `SecurityTestCase` before execution.

For the unauthorized protected operation:

```text
precondition:

authorization = False

expected:

ACCESS_DENIED
```

The actual result is obtained from the ECU execution.

The regression outcome is then determined by comparing expected and actual behavior.

A `PASS` indicates that the expected security behavior was observed.

A `FAIL` indicates that the observed behavior differs from the defined security expectation and requires investigation.

A regression failure must not automatically be interpreted as proof of a new vulnerability.

## Traceability

Evidence preserves the relationship between the test definition and its execution result through the `test_id`.

The intended relationship is:

```text
Security Finding
      |
      v
Security Property
      |
      v
SecurityTestCase
      |
      v
TestResult
      |
      v
Evidence
```

For the current TC-003 implementation, the regression test uses the existing `TC-001` test identifier because the regression verifies the security property originally established by TC-001.

The `test_tc003_*` pytest function names identify the Phase-7 regression test functions. They do not change the `SecurityTestCase.test_id`.

Therefore:

```text
pytest test function:

test_tc003_retest_confirms_secure_behavior

SecurityTestCase.test_id:

TC-001
```

This distinction is intentional.

```text
TC-003
  = Regression Workflow

test_tc003_*
  = pytest regression/lifecycle tests

TC-001
  = SecurityTestCase.test_id of the currently
    regressed Diagnostic-Authorization property
```

TC-003 identifies the regression workflow, while TC-001 identifies the original security test case whose security property is being re-tested.

## Serialization

Evidence can be converted into a JSON-compatible dictionary using `Evidence.to_dict()` and serialized using `Evidence.to_json()`.

The serialized representation contains:

```text
{
  "actual": "ACCESS_DENIED",
  "expected": "ACCESS_DENIED",
  "input": {
    "operation": "PROTECTED_OPERATION"
  },
  "notes": "Retest confirms that unauthorized protected operation is denied.",
  "preconditions": {
    "authorization": false
  },
  "result": "PASS",
  "target": "simulated-ecu",
  "test_id": "TC-001",
  "timestamp": "..."
}
```

The timestamp value is generated during execution and therefore varies between executions.

## Current Evidence Framework Scope

Following completion of Phase 8, the Evidence Framework supports evidence generation for the currently implemented security tests and the controlled TC-003 regression workflow.

Phase 8 consumes this existing evidence for structured example finding documentation but does not modify the Evidence Framework model.

The current implemented security-test and regression workflows are:

```text
TC-001 — Diagnostic Authorization

TC-002 — Message Validation

TC-003 — Regression Workflow
```

Both security tests and the regression workflow use the same evidence structure:

```text
test_id
timestamp
target
preconditions
input
expected
actual
result
notes
```

TC-003 uses the existing TC-001 security-test definition and does not introduce a separate `SecurityTestCase` evidence identity.

The evidence workflow is:

```text
Security Test
       |
       v
Test Execution
       |
       v
TestResult
       |
       v
EvidenceGenerator
       |
       v
Evidence Model
       |
       v
Evidence.validate()
       |
       v
JSON
```

All implemented security tests and the regression workflow use the same Evidence model

Test-specific information is represented through the existing fields such as `test_id`, `preconditions`, `input`, `expected`, `actual`, and `notes`.

---

## Current Evidence Examples

### TC-001 — Diagnostic Authorization

A successful unauthorized-access protection test may produce:

```json
{
  "test_id": "TC-001",
  "timestamp": "2026-08-23T21:52:16.789923Z",
  "target": "simulated-ecu",
  "preconditions": {
    "authorization": false
  },
  "input": {
    "operation": "PROTECTED_OPERATION"
  },
  "expected": "ACCESS_DENIED",
  "actual": "ACCESS_DENIED",
  "result": "PASS",
  "notes": "Unauthorized protected operation was rejected."
}
```

A controlled vulnerable execution may instead record:

```text
expected = ACCESS_DENIED
actual   = ACCESS_GRANTED
result   = FAIL
```

### TC-002 — Message Validation

A conforming invalid-request test may produce:

```json
{
  "test_id": "TC-002",
  "timestamp": "2026-08-29T12:00:00.000000Z",
  "target": "simulated-ecu",
  "preconditions": {
    "target_interface": "configured"
  },
  "input": {
    "operation": "UNSUPPORTED_OPERATION"
  },
  "expected": "UNSUPPORTED_OPERATION",
  "actual": "UNSUPPORTED_OPERATION",
  "result": "PASS",
  "notes": "Unsupported operation was rejected by the simulated ECU."
}
```

The timestamp shown in examples is illustrative. Actual evidence timestamps are generated at runtime.

### TC-003 — Regression Workflow

A successful secure regression retest may produce:

```json
{
  "test_id": "TC-001",
  "timestamp": "2026-09-02T12:00:00.000000Z",
  "target": "simulated-ecu",
  "preconditions": {
    "authorization": false,
    "security_mode": "SECURE"
  },
  "input": {
    "operation": "PROTECTED_OPERATION"
  },
  "expected": "ACCESS_DENIED",
  "actual": "ACCESS_DENIED",
  "result": "PASS",
  "notes": "Secure regression retest confirmed unauthorized access remains denied."
}
```

The `test_id` remains `TC-001` because TC-003 reuses the existing TC-001 security-test definition. TC-003 identifies the regression workflow, not a new security-test definition.

The generated evidence is subsequently validated using `Evidence.validate()`.

The timestamp shown in the example is illustrative. Actual evidence timestamps are generated at runtime.

---

## Evidence and Security Finding Boundary

Evidence is not a vulnerability finding.

Evidence answers:

```text
What was tested?
What were the preconditions?
What input was used?
What behavior was expected?
What behavior was observed?
What was the resulting test status?
```

A finding assessment may answer:

```text
Is this a security issue?
Why?
What is the security impact?
What is the root cause?
How should it be fixed?
Has the fix been verified?
```

The distinction remains valid after Phase 8.

The current Evidence Framework records test observations and evaluation
results. It does not perform formal vulnerability classification, root-cause
analysis, remediation tracking, historical regression comparison, or
generalized regression management.

Phase 8 uses existing test results and evidence as supporting information for
structured example finding documentation. The finding assessment adds
security-relevant information such as impact, exploitability, root cause,
recommendation, fix, retest, and regression relationship. These assessment
attributes are not part of the Evidence model.

The Phase-7 regression workflow demonstrates a controlled retest and evidence
generation for the TC-001 security property. Phase 8 builds structured
finding documentation on top of this existing evidence without extending the
Evidence Framework into a finding-management system.

The relationship is:

```text
Security Test
       |
       v
Test Result
       |
       v
Evidence
       |
       v
Finding Assessment
       |
       v
Example Finding
```

The Evidence Framework remains responsible for recording the executed test observation.

The Phase-8 finding documentation adds assessment information that is not part of the Evidence model.

For SEC-001, the evidence supports documentation of the controlled authorization deviation:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_GRANTED
Result   = FAIL
```

The finding then documents the supported security impact, exploitability, root cause, recommendation, fix, retest, and regression relationship.

For SEC-002, the evaluated TC-002 scenarios conform to the expected response behavior:

```text
Expected == Actual
        |
        v
PASS
```

The corresponding finding document records that no security-relevant deviation was reproduced.

SEC-002 is therefore an assessment example and not a demonstrated vulnerability.

The finding documents are stored separately from the Evidence Framework:

```text
05_examples/sample_finding_SEC-001.md
05_examples/sample_finding_SEC-002.md
```

No finding identifier is added to the current `Evidence` model.

No automated evidence-to-finding ingestion is implemented in Phase 8.

---

## Current Implementation Status

The evidence model and evidence generation mechanism are implemented in the current repository.

The current implementation includes:

```text
Evidence

EvidenceResult

EvidenceValidationError

EvidenceGenerator

Evidence.validate()

Evidence.to_dict()

Evidence.to_json()

Evidence.from_dict()
```

TC-001 and TC-002 use `EvidenceGenerator` for their security test scenarios.

TC-003 additionally demonstrates regression evidence generation and
validation for the secure retest of the TC-001 authorization property.

Phase 8 adds structured example finding documentation based on existing test
results and evidence.

The Evidence Framework itself remains limited to execution evidence and does
not implement finding management.

TC-003 verifies that the generated evidence contains the expected test
identity, target, preconditions, expected behavior, actual behavior, and
result before the evidence is validated.
