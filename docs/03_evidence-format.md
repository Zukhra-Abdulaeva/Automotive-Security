# Evidence Format

## Purpose

The Evidence Framework provides a structured, reproducible, and
machine-readable representation of one security test execution.

The evidence format defines the structured representation of a completed
security test execution in the Automotive Security Regression Lab.

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
````

The same evidence model is used for the existing security test scenarios and
for the TC-003 regression workflow.

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

The `preconditions` record security-relevant conditions established before
execution.

The `input` contains the request presented to the target.

The `expected` value represents the security behavior defined by the test
case.

The `actual` value represents the response observed during execution.

The `result` represents the evaluated evidence result.

The `notes` field provides additional execution context.

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

The timestamp is part of the execution evidence and identifies when the
evidence record was generated.

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

It only documents that the observed behavior differed from the expected
behavior.

Security assessment, finding classification, root-cause analysis, and impact
assessment are outside the scope of the Evidence Framework.

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

The expected and actual response values are derived from the executed test
result.

The evidence result is derived from the comparison of expected and actual
behavior:

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

The EvidenceGenerator therefore connects the executed security test result
with the structured Evidence model.

It does not independently execute the security test and does not implement
the ECU security policy.

## Evidence Validation

`Evidence.validate()` verifies the structural and semantic consistency of an
evidence record.

The validation includes:

```text
required fields are present
preconditions are a mapping
result is PASS or FAIL
timestamp is valid ISO-8601 with timezone information
result matches the expected/actual comparison
```

An evidence record is therefore considered valid only when its declared
result is consistent with the recorded expected and actual behavior.

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

An invalid evidence record causes evidence validation to fail and must not be
treated as a valid evidence artifact.

## JSON Serialization

Evidence can be converted into a JSON-compatible dictionary using
`Evidence.to_dict()` and serialized using `Evidence.to_json()`.

Evidence can also be reconstructed from a dictionary using
`Evidence.from_dict()`.

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

The Evidence Framework itself does not implement CI/CD orchestration.
Phase 10 uses the existing Evidence Framework from the GitHub Actions
workflow to generate and upload regression evidence.

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
TestResult
        |
        v
EvidenceGenerator
        |
        v
Evidence
```

The Evidence Framework consumes the result of test execution and represents
the observation in a structured form.

It does not implement ECU security policy.

## Determinism

Evidence generation does not require:

```text
network access
physical hardware
a real ECU
external services
random test data
```

The Evidence Framework can therefore be tested locally and reproducibly.

The current evidence generation is deterministic with respect to the test
input, expected behavior, actual behavior, and explicitly supplied
preconditions.

The timestamp is intentionally runtime-generated and is the only
time-dependent field in the evidence record.

The current regression implementation uses the deterministic `ECUSimulator`
as its target.

No external network communication or external ECU availability is required
for the TC-003 evidence test.

## Phase 4 Scope

Implemented in Phase 4:

```text
structured evidence model
mandatory field validation
PASS / FAIL semantics
runtime timestamp
JSON serialization
integration with the existing Phase 3 test result
deterministic local evidence tests
```

Not implemented in Phase 4:

```text
security finding management
severity management
CVSS calculation
root-cause management
fix tracking
retest workflow
complete security regression suite
CI/CD pipeline
real ECU communication
real vehicle communication
```

The Phase-4 scope describes the capability introduced in Phase 4.
Later phases extend the use of the existing Evidence Framework without
changing its fundamental evidence model.

---

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

The Evidence Framework does not determine whether the observed deviation
constitutes a formal security finding.

Phase 5 therefore extended the practical use of the Evidence Framework
without changing its fundamental model or architectural boundary.

No separate evidence architecture was introduced for TC-001.

---

## Phase 6 — TC-002 Evidence Integration

Phase 6 introduced the second dedicated security test:

```text
TC-002 — Message Validation
```

The existing Evidence Framework is reused for TC-002 executions.

TC-002 verifies that invalid request structures or unsupported operations are
rejected before security-relevant operation processing.

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

For an unsupported operation, the current simulator distinguishes the
operation from a malformed request:

```text
Expected = UNSUPPORTED_OPERATION
Actual   = UNSUPPORTED_OPERATION
Result   = PASS
```

If the target returns a different response, the evidence records a failed
comparison:

```text
Expected != Actual
Result   = FAIL
```

The `FAIL` represents an observed deviation from the message-validation
requirement. It does not automatically constitute a formal security finding.

TC-002 uses the same evidence model and serialization mechanism established
in Phase 4.

No separate evidence format is introduced for TC-002.

---

## Phase 7 — TC-003 Regression Evidence Integration

Phase 7 introduces the TC-003 Regression Workflow.

TC-003 uses the existing Evidence Framework to represent the result of a
regression retest.

It does not introduce a separate evidence model, evidence schema, or
serialization mechanism.

The regression test uses the existing TC-001 `SecurityTestCase` and the
existing security test execution architecture.

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

The implemented TC-003 regression evidence test verifies that the generated
evidence represents the executed secure retest.

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

This demonstrates that TC-003 applies the existing evidence model to a
regression execution.

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

The TC-003 evidence workflow therefore records the secure regression retest
and the authorized-behavior verification using the existing Evidence model.

No separate evidence format is introduced for TC-003.

## Evidence and Regression Evaluation

Evidence records the result of the executed test.

It does not independently determine whether the underlying security
requirement is correct.

For TC-003, the expected behavior is defined by the regression
`SecurityTestCase` before execution.

For the unauthorized protected operation:

```text
precondition:
authorization = False

expected:
ACCESS_DENIED
```

The actual result is obtained from the ECU execution.

The regression outcome is then determined by comparing expected and actual
behavior.

A `PASS` indicates that the expected security behavior was observed.

A `FAIL` indicates that the observed behavior differs from the defined
security expectation and requires investigation.

A regression failure must not automatically be interpreted as proof of a new
vulnerability.

## Traceability

Evidence preserves the relationship between the test definition and its
execution result through the `test_id`.

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

For the current TC-003 implementation, the regression workflow reuses the
existing `TC-001` security-test identifier because the regression verifies
the security property originally established by TC-001.

The `test_tc003_*` pytest function names identify the Phase-7 regression test
functions. They do not change the `SecurityTestCase.test_id`.

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

TC-003 identifies the regression workflow, while TC-001 identifies the
original security test case whose security property is being re-tested.

The Phase-9 automated regression suite uses distinct regression
`SecurityTestCase` instances with `test_id = TC-003`. This is separate from
the Phase-7 lifecycle test described above and does not change the identity
of the original TC-001 security property.

## Serialization

Evidence can be converted into a JSON-compatible dictionary using
`Evidence.to_dict()` and serialized using `Evidence.to_json()`.

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

The timestamp value is generated during execution and therefore varies
between executions.

## Current Evidence Framework Scope

Following completion of Phase 7, the Evidence Framework supports evidence
generation for the currently implemented security tests and the controlled
TC-003 regression workflow:

```text
TC-001 — Diagnostic Authorization

TC-002 — Message Validation

TC-003 — Regression Workflow
```

Both security tests and the regression workflow use the same evidence
structure:

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

TC-003 uses the existing TC-001 security-test definition for the Phase-7
controlled regression lifecycle and does not introduce a separate evidence
schema.

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

The Evidence Framework therefore provides a common evidence representation
across the implemented security-test set and the controlled regression
workflow.

The framework does not require a different evidence schema for each test
case.

Test-specific information is represented through the existing fields such as
`test_id`, `preconditions`, `input`, `expected`, `actual`, and `notes`.

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

The timestamp shown in examples is illustrative. Actual evidence timestamps
are generated at runtime.

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

The `test_id` remains `TC-001` in this Phase-7 lifecycle example because
TC-003 reuses the existing TC-001 security-test definition. TC-003 identifies
the regression workflow, not a new security-test definition.

The generated evidence is subsequently validated using
`Evidence.validate()`.

The timestamp shown in the example is illustrative. Actual evidence
timestamps are generated at runtime.

---

## Automated Regression Evidence

The Evidence Framework is integrated into the automated security regression tests.

This integration does not introduce a new evidence schema or a separate regression-specific evidence model. Instead, the existing `EvidenceGenerator`, `Evidence`, and validation mechanisms are used directly with executed regression test cases and their results.

The automated regression tests verify two related properties:

1. the security behavior remains correct, and
2. the evidence representing that behavior is correct and internally consistent.

### Evidence Generation from an Executed Regression Test

A regression scenario is executed through the existing security test infrastructure:

```text
SecurityTestCase
      |
      v
SecurityTestRunner
      |
      v
ECUAdapter
      |
      v
ECUSimulator
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

The generated evidence therefore represents an actually executed test scenario rather than a manually constructed result.

For the protected-operation regression scenario, the generated evidence contains:

```text
test_id     = TC-003
target      = simulated-ecu
expected    = ACCESS_DENIED
actual      = ACCESS_DENIED
result      = PASS
```

The execution context is recorded through the evidence preconditions:

```text
authorization = false
ecu_state     = READY
security_mode = SECURE
```

This makes the security condition under which the result was obtained explicit and reproducible.

### Evidence Validation is Part of the Automated Test

The regression test does not stop after checking the ECU response.

After evidence generation, the evidence object is explicitly validated:

```text
evidence.validate()
```

This is significant because it verifies that the evidence itself satisfies the Evidence Framework rules.

The automated test therefore covers both levels:

```text
Security behavior
    |
    +-- expected status == actual status
    |
    +-- test result == PASS
    |
    v
Evidence generation
    |
    +-- correct test ID
    +-- correct target
    +-- correct preconditions
    +-- correct expected value
    +-- correct actual value
    +-- correct result
    |
    v
Evidence validation
```

This establishes that a successful regression test produces evidence that is not only present, but also structurally and semantically valid.

### Evidence Represents the Secure Retest

The regression evidence records the secure behavior that must remain preserved.

For the protected-operation scenario, an unauthorized request is expected to produce:

```text
Expected: ACCESS_DENIED
Actual:   ACCESS_DENIED
Result:   PASS
```

The evidence therefore documents the security property being verified:

> An unauthorized protected operation remains denied in secure ECU mode.

The evidence does not itself reproduce the historical vulnerable behavior. Vulnerable behavior reproduction and secure retest comparison remain part of the controlled regression workflow. The automated regression suite verifies that the established secure behavior remains intact.

### Explicit Execution Context

The automated regression scenarios create a fresh secure ECU instance for each scenario:

```text
ecu = ECUSimulator(
    mode=SecurityMode.SECURE,
    state=state,
)
```

Authorization and ECU state are then explicitly configured before execution.

This provides test isolation and prevents state left by one scenario from influencing another scenario or its generated evidence.

The resulting evidence can therefore be interpreted together with its recorded preconditions rather than relying on implicit simulator state.

### Coverage of Evidence-Relevant Security Conditions

The automated regression suite covers several established security properties whose results can be represented by the existing evidence model:

| Scenario                                 | Expected result         |
| ---------------------------------------- | ----------------------- |
| Unauthorized protected operation         | `ACCESS_DENIED`         |
| Authorized protected operation           | `ACCESS_GRANTED`        |
| Invalid message                          | `INVALID_REQUEST`       |
| Unsupported operation                    | `UNSUPPORTED_OPERATION` |
| Out-of-range boundary input              | `REQUEST_REJECTED`      |
| Protected operation in blocked ECU state | `REQUEST_REJECTED`      |

The evidence-specific regression test additionally verifies that the secure unauthorized-operation scenario is represented correctly in the Evidence Framework.

### No Evidence Schema Change

The automated regression integration does **not** add new evidence fields.

The existing evidence structure remains:

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

The extension is therefore in the **usage and verification of the existing model**, not in the model itself.

The Evidence Framework is now exercised as part of an automated regression path:

```text
Execute regression scenario
        |
        v
Obtain TestResult
        |
        v
Generate Evidence
        |
        v
Validate Evidence
```

This strengthens the traceability between executed security behavior and its recorded evidence without introducing a second evidence mechanism.

### Evidence and Security Finding Boundary

Evidence remains supporting information for a security finding.

The automated regression tests do not automatically create or update security findings. They verify established security properties and can generate evidence demonstrating the observed result.

The separation remains:

```text
Security Finding
        |
        v
Security Property
        |
        v
Regression Test
        |
        v
TestResult
        |
        v
Evidence
```

Evidence documents the observed test result and execution context. It does not replace the finding, root-cause analysis, remediation information, or regression workflow.

### Current Evidence Scope

The current implementation supports:

```text
structured security-test evidence
deterministic evidence generation
explicit execution preconditions
expected-versus-actual result recording
PASS/FAIL semantics
evidence validation
JSON serialization and deserialization
integration with TC-001, TC-002, and TC-003 security testing
automated verification that regression evidence represents the executed secure retest
```

The current Evidence Framework does not provide:

```text
automated security-finding ingestion
historical evidence comparison
baseline management
generalized regression orchestration
automated remediation tracking
```

CI/CD evidence collection is implemented in Phase 10 at the workflow level by
reusing the existing Evidence Framework. It does not constitute a new
Evidence Framework capability or a change to the evidence schema.

---

## Phase 10 — CI/CD Evidence Integration

Phase 10 integrates the existing automated Security Regression suite with
GitHub Actions.

The CI workflow is defined in:

```text
.github/workflows/security-regression.yml
```

The workflow executes the existing regression test logic from:

```text
04_tests/test_security_regression.py
```

This file remains the Single Source of Truth for the Security Regression test
logic. GitHub Actions does not introduce a second Security Regression test
implementation.

The CI evidence chain is:

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

The workflow is configured for:

```text
push
pull_request
```

The verified CI environment uses:

```text
Python 3.12
pytest>=9,<10
```

The relevant CI execution sequence is:

```text
Repository Checkout
        ↓
Python 3.12 Setup
        ↓
pytest Installation
        ↓
04_tests/test_security_regression.py
        ↓
Regression Evidence Generation
        ↓
Evidence.to_json()
        ↓
Evidence Artifact Upload
```

The Evidence Framework is therefore reused by CI rather than replaced by
CI-specific evidence logic.

### CI Evidence Generation

Phase 10 generates six JSON evidence files from the automated regression
execution.

The generated evidence files are:

```text
TC-003_unauthorized_protected_operation.json
TC-003_authorized_protected_operation.json
TC-003_invalid_message.json
TC-003_unsupported_operation.json
TC-003_boundary_input.json
TC-003_unexpected_state.json
```

The evidence files are generated from the existing regression execution and
serialized using the existing `Evidence.to_json()` mechanism.

The resulting directory is:

```text
ci-evidence/
```

The directory is uploaded by GitHub Actions as:

```text
security-regression-evidence
```

This does not introduce a new evidence schema. The CI artifact contains the
same structured Evidence JSON representation used by the existing Evidence
Framework.

### CI Success and Failure Handling

The CI workflow separates the Security Regression test outcome from the
availability of regression evidence.

The pytest step is allowed to fail normally so that a security regression
failure causes the GitHub Actions job to fail.

Evidence generation and artifact upload are configured to execute with
`always()`.

The intended failure path is therefore:

```text
Security Regression Assertion
        ↓
pytest FAIL
        ↓
GitHub Actions Job FAIL
        ↓
Evidence Generation
        ↓
Evidence Artifact Upload
```

This behavior was verified through a controlled CI failure test.

A single Security Regression assertion was intentionally changed so that the
expected status no longer matched the actual secure ECU response.

The local result was:

```text
1 failed, 6 passed
```

The corresponding GitHub Actions execution failed with exit code `1`, while
the `security-regression-evidence` artifact was still generated and uploaded.

This verifies that CI failure does not prevent the configured evidence path
from producing an artifact.

### Verified Successful CI Execution

The push of commit `78c943f` to `main` triggered the GitHub Actions workflow
and completed successfully.

The verified execution was:

```text
Workflow: Security Regression
Run: #1
Trigger: push
Branch: main
Commit: 78c943f
Job: security-regression
Status: Success
Duration: 11 s
Artifact count: 1
Artifact: security-regression-evidence
Artifact size: 2.59 KB
```

The SHA-256 digest of the generated artifact was:

```text
e337895fd207dbfdeb30358cef5194c6a895b3e0d8e72feae9896a591585503f
```

The CI evidence artifact was therefore verified for the successful workflow
execution.

### Verified Controlled CI Failure

The controlled failure was executed on:

```text
ci/controlled-failure-test
```

The failure commit was:

```text
25432a4 test: verify CI failure handling
```

The corresponding GitHub Actions Run #2 was:

```text
Workflow: Security Regression
Run: #2
Trigger: push
Branch: ci/controlled-failure-test
Commit: 25432a4
Job: security-regression
Status: Failed
Exit Code: 1
Artifact: security-regression-evidence
Artifact size: 2.59 KB
```

The failure demonstrates that the Security Regression assertion correctly
causes the CI job to fail while the configured evidence generation and
artifact upload path remains available.

The intentional test change was subsequently restored with:

```text
a604f08 test: restore security regression expectation
```

The restored regression suite was locally verified with:

```text
7 passed in 0.06s
```

The `main` branch remained unchanged at `78c943f` and was clean and
synchronized with `origin/main`.

### CI Trigger Verification Status

The `push` trigger has been verified through actual GitHub Actions executions,
including the successful Run #1 and the controlled failure Run #2.

The `pull_request` trigger is configured in the workflow but has not yet been
verified through a separate actual pull-request execution.

Therefore, the current Evidence Framework documentation does not treat a
pull-request execution as a completed verification result.

### Technical CI Note

GitHub Actions reported a Node.js 20 deprecation warning for the currently
used actions during the verified runs.

The affected actions were:

```text
actions/checkout@v4
actions/setup-python@v5
actions/upload-artifact@v4
```

The warning did not prevent the successful CI execution and did not prevent
the controlled failure behavior.

This is documented as a technical compatibility note and not as a
pipeline failure.

### Phase-10 Evidence Boundary

Phase 10 extends the use of the existing Evidence Framework into the CI
execution path.

The architecture remains:

```text
Security Regression Test
        ↓
TestResult
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

No new evidence fields, evidence model, validation mechanism, or serialization
format is introduced by Phase 10.

The CI workflow also does not implement separate Security Regression test
logic.

The following capabilities remain outside the current Evidence Framework:

```text
automated security-finding ingestion
historical evidence comparison
baseline management
generalized regression orchestration
automated remediation tracking
```

The GitHub Actions workflow provides CI execution and artifact handling for
the currently implemented regression suite. It does not constitute a
generalized security evidence-management platform.
