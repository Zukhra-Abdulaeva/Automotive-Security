# TC-003 — Regression Workflow

## Purpose

TC-003 defines the finding-to-regression workflow of the Automotive Security Regression Lab.

The purpose of the workflow is to convert a confirmed security finding into a reproducible regression test that can be executed again after a security-relevant change.

The workflow establishes a traceable relationship between:

* the original security finding
* the affected security property
* the regression test case
* the expected security behavior
* the executed test result
* the generated evidence

TC-003 is therefore not a replacement for TC-001 or TC-002. It defines how an existing security finding is converted into a repeatable regression test and how the regression result is evaluated.

## Scope

The workflow applies to security findings that can be represented by the existing test architecture of the Automotive Security Regression Lab.

The current implementation provides the technical foundation required for this workflow:

* `ECUSimulator` provides a deterministic security target.
* `ECUAdapter` provides the target interface.
* `SecurityTestCase` defines the input and expected result of a test.
* `SecurityTestRunner` executes a test case and compares the actual response with the expected response.
* `EvidenceGenerator` creates structured evidence from a completed test execution.
* TC-001 and TC-002 provide existing security test scenarios that can serve as regression baselines.

The complete finding-to-regression workflow is the subject of Phase 7. Additional automation or orchestration is only considered implemented when it is present and verified in the source code and tests.

## Regression Principle

A security finding becomes a regression test when the security property affected by the finding is expressed as an explicit, reproducible test condition.

The regression test must define at minimum:

1. a unique test identifier
2. the security behavior being protected
3. the relevant preconditions
4. the test input
5. the expected security response
6. the actual security response obtained during execution
7. a deterministic pass/fail evaluation
8. evidence for the executed test

The regression test must verify the security property rather than merely verify that the test itself can be executed.

## Finding-to-Regression Workflow

The Phase-7 workflow consists of the following logical steps:

```text
Security Finding
       |
       v
Identify affected security property
       |
       v
Define regression condition
       |
       v
Define preconditions and input
       |
       v
Define expected security behavior
       |
       v
Create / extend regression test case
       |
       v
Execute through SecurityTestRunner
       |
       v
Compare actual result with expected result
       |
       v
Generate structured evidence
       |
       v
Evaluate regression result
       |
       +---- PASS ----> Security property remains enforced
       |
       +---- FAIL ----> Regression detected
```

Each step must remain traceable to the original security finding.

## Regression Test Case Definition

A regression test case is represented by the existing `SecurityTestCase` model.

The test case contains:

```text
test_id
description
request
expected_status
```

The `test_id` identifies the regression test uniquely.

The `description` identifies the security property or behavior being verified.

The `request` defines the input presented to the target.

The `expected_status` defines the security response required for the test to pass.

The expected response must represent the intended secure behavior. It must not be derived from the current actual response of the target.

## Preconditions

Regression tests must establish all security-relevant conditions required to reproduce the finding.

Relevant preconditions may include:

```text
authorization state
ECU operational state
security mode
target configuration
other security-relevant test conditions
```

Only preconditions that are relevant to the security property under test should be defined.

Preconditions must be explicit enough that the test execution can be reproduced.

## Input Definition

The regression test input must reproduce the condition that is relevant to the original finding.

For the current simulated ECU architecture, the input is represented by the request mapping accepted by `ECUSimulator.handle_request()`.

The request must be compatible with the target interface and must not depend on unspecified implementation behavior.

Where the finding concerns invalid, unauthorized, unsupported, or otherwise security-sensitive input, the regression test must preserve that condition explicitly.

## Expected Security Behavior

The expected behavior is the security requirement that must remain enforced after a security-relevant change.

Examples represented by the existing test architecture include:

```text
Unauthorized protected operation
    Expected: ACCESS_DENIED

Authorized protected operation
    Expected: ACCESS_GRANTED

Unsupported operation
    Expected: UNSUPPORTED_OPERATION

Malformed request
    Expected: INVALID_REQUEST

Invalid parameter or blocked ECU state
    Expected: REQUEST_REJECTED
```

These examples describe behavior already represented by existing test cases. They do not imply that a separate automated TC-003 implementation currently exists.

## Regression Execution

A regression test is executed through the existing test execution abstraction.

The intended execution flow is:

```text
SecurityTestCase
       |
       v
SecurityTestRunner
       |
       v
ECUTarget
       |
       v
ECUSimulator / target implementation
       |
       v
ECUResponse
       |
       v
actual_status
       |
       v
comparison with expected_status
       |
       v
TestResult
```

The runner determines whether the actual response status matches the expected response status.

A matching result is a passed test.

A non-matching result is a failed test and indicates that the expected security behavior was not observed.

## Evidence Generation

A completed regression execution must be representable as structured evidence using the existing evidence model.

The evidence contains:

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

The `EvidenceGenerator` derives the expected and actual response values from the `SecurityTestCase` and `TestResult`.

The evidence result is `PASS` when expected and actual behavior are equal. Otherwise the evidence result is `FAIL`.

Evidence validation must remain consistent with the existing `Evidence` validation rules.

## Regression Result

The regression result is determined from the comparison between expected and actual behavior.

```text
Expected behavior == Actual behavior
        |
        v
      PASS

Expected behavior != Actual behavior
        |
        v
      FAIL
```

A `PASS` means that the security behavior defined by the regression test was observed during execution.

A `FAIL` means that the observed behavior differs from the defined security expectation and therefore requires investigation.

A regression failure must not automatically be interpreted as proof of a new vulnerability. It indicates that the defined security behavior was not reproduced during the test execution and requires further analysis.

## Relationship to Existing Test Cases

TC-001 and TC-002 remain independent security test cases.

TC-001 verifies diagnostic authorization behavior.

TC-002 verifies message validation behavior.

TC-003 defines the workflow by which a security finding can be converted into a regression test and subsequently executed and evidenced.

The existing test cases may therefore serve as regression sources when a finding corresponds to one of their security properties.

```text
TC-001 / TC-002
      |
      | existing security behavior
      v
Security Finding
      |
      v
TC-003 Regression Workflow
      |
      v
Reproducible regression execution
```

TC-003 must not change the security semantics of TC-001 or TC-002.

## Determinism

The regression workflow must produce reproducible results under equivalent test conditions.

The current project architecture supports deterministic execution through the simulated ECU.

The regression test must therefore avoid dependencies on:

* uncontrolled network communication
* external ECU availability
* nondeterministic target behavior
* unspecified environmental state
* manually interpreted response values

Where external or hardware-based targets are introduced in a later phase, their behavior must still be represented through the defined target abstraction.

## Traceability

A regression test must remain traceable from the original finding to the executed evidence.

The intended relationship is:

```text
Finding
  |
  +-- affected security property
          |
          +-- regression test ID
                  |
                  +-- test input
                  |
                  +-- expected behavior
                  |
                  +-- execution result
                          |
                          +-- evidence
```

The unique test identifier is the primary identifier used to connect the test definition with its execution result and evidence.

## Phase-7 Implementation Boundary

The following distinction is mandatory for the current project state.

### Already implemented

The repository already contains the technical building blocks required for test execution and evidence generation:

```text
ECUSimulator
ECUAdapter
SecurityTestCase
SecurityTestRunner
TestResult
Evidence
EvidenceGenerator
TC-001
TC-002
```

These components provide the existing execution and evidence foundation.

### Defined by TC-003

This document defines:

```text
finding-to-regression workflow
regression test requirements
precondition handling
expected security behavior
execution flow
result evaluation
evidence relationship
traceability requirements
determinism requirements
```

### Not claimed as implemented by this document

The following functions must not be considered implemented solely because they are defined in this specification:

```text
automatic finding ingestion
automatic regression-test generation
automatic regression-test registration
automatic regression-suite orchestration
automatic finding-to-test traceability
automatic historical comparison
automatic regression reporting
```

Such functionality requires corresponding source-code implementation and verification.

## Verification Criteria

TC-003 is technically acceptable when the implemented Phase-7 workflow can demonstrate that:

```text
1. A security finding can be expressed as a defined security property.

2. The security property can be represented by a reproducible regression condition.

3. The regression condition can be represented by a SecurityTestCase.

4. The test can be executed through the existing target and runner abstractions.

5. The actual result is compared with the defined expected result.

6. The result can be represented as PASS or FAIL.

7. Structured evidence can be generated for the execution.

8. The evidence remains consistent with the executed test result.

9. Existing TC-001 functionality remains operational.

10. Existing TC-002 functionality remains operational.

11. No regression-test functionality is described as implemented unless it
    is present in the verified source code.

12. The resulting implementation remains deterministic and reproducible.
```

## Phase-7 Status

TC-003 defines the technical regression workflow and its required behavior.

At this stage, the document is the specification for the Phase-7 implementation.

The workflow itself is not considered fully implemented until the required source-code changes and corresponding tests have been completed and verified.

The Phase-7 quality gate must therefore be based on the verified implementation and test results rather than on the presence of this document alone.

