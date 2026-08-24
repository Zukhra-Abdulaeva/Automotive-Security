# Evidence Format

## Purpose

The Evidence Framework provides a structured, reproducible, and
machine-readable representation of one security test execution.

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

The framework documents what was tested, under which conditions, what was
expected, what was actually observed, and whether the observed behavior
matched the expected behavior.

The evidence is generated exclusively from the simulated test environment.

No real ECU data, production credentials, vehicle data, network traffic, or
customer data is required.

## Evidence Model

Each evidence record represents one executed security test case.

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

The model is intentionally simple and can be extended later with optional
fields such as `software_version`, `test_environment`, or `execution_id`.

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

The Evidence Framework validates the required structure before evidence is
accepted or serialized.

## Timestamp

The timestamp is generated dynamically when evidence is created.

It uses an ISO 8601 UTC representation.

Example:

```text
2026-08-23T21:52:16.789923Z
```

Tests must not depend on a fixed timestamp.

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

Security assessment, finding classification, root-cause analysis, and impact
assessment are outside the scope of the Evidence Framework.

## JSON Serialization

Evidence can be serialized to JSON.

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

The timestamp in an actual evidence record is generated at runtime and is not
a fixed value.

JSON serialization provides a machine-readable representation that can later
be consumed by automation or stored as a test artifact.

CI/CD pipeline implementation is outside the scope of Phase 4.

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

Finding management is outside the scope of Phase 4.

## Architectural Boundary

The Evidence Framework is separated from the ECU simulation.

The ECU remains the System Under Test and has no knowledge of evidence
generation.

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
Evidence
```

The Evidence Framework consumes the result of test execution and represents
the observation in a structured form.

It does not implement ECU security policy.

## Determinism

Evidence generation does not require:

* network access
* physical hardware
* a real ECU
* external services
* random test data

The Evidence Framework can therefore be tested locally and reproducibly.

The timestamp is intentionally runtime-generated and is the only
time-dependent field in the evidence record.

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