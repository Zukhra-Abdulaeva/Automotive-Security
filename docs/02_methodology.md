# Security Testing Methodology

## Purpose

The Automotive Security Regression Lab uses a structured methodology to turn a defined security requirement into a reproducible security test.

The methodology separates:

* security requirements
* threat modeling
* attack hypotheses
* security-test definition
* test execution
* result evaluation
* evidence generation
* security-relevant observations

* remediation

* retesting

* regression testing

The methodology is implemented incrementally across the project phases.

The current implementation covers the security-test, evidence, Phase-8 example finding, and Phase-9 automated regression workflow through Phase 9.

Phase 7 extends the existing security-test and evidence workflow with a controlled regression lifecycle for the diagnostic authorization security property established by TC-001.

Phase 8 extends the workflow with structured example finding documentation based on the existing test and evidence results.

Phase 9 extends the methodology with an automated pytest security regression suite covering the established security properties of the simulated ECU.

Generalized security finding management, automated finding ingestion, remediation tracking, historical regression comparison, generalized regression orchestration, and CI/CD remain outside the current implementation.

---

## Methodology Overview

The long-term project methodology is:

```text
Security Requirement
        ↓
Threat Model
        ↓
Attack Surface
        ↓
Attack Hypothesis
        ↓
Security Test
        ↓
Test Execution
        ↓
Expected vs Actual
        ↓
Evidence
        ↓
Security Finding
        ↓
Root Cause
        ↓
Recommended Fix
        ↓
Implemented Fix
        ↓
Retest
        ↓
Regression
        ↓
Automated Regression
        ↓
CI/CD
````

Not all stages are currently implemented.

The currently implemented workflow is:

```text
Security Requirement
        ↓
Threat Model
        ↓
Attack Surface
        ↓
Attack Hypothesis
        ↓
Security Test
        ↓
Test Execution
        ↓
Expected vs Actual
        ↓
Evidence
        ↓
Controlled Security-Relevant Deviation
        ↓
Secure Retest
        ↓
Regression Evaluation
        ↓
Regression Evidence
        ↓
Example Finding Documentation
        ↓
Automated Security Regression Tests
```

Phase 7 implements the regression extension only for the diagnostic authorization security property represented by TC-001.
Phase 8 adds structured example finding documentation based on the existing security-test and evidence results.
Phase 9 adds an automated pytest regression suite for the established security properties represented by the current simulated ECU and test architecture.
The Phase-9 suite verifies the secure behavior of individual regression scenarios and validates that regression evidence represents the executed secure retest.
The distinction between implemented and planned capabilities is maintained throughout this document.

---

## Methodology Principles

### Define the Security Property First

The expected security behavior is defined before test execution.
The security test evaluates a security requirement rather than deriving the requirement from the observed implementation.

For TC-001, the requirement is:

```text
Protected diagnostic operations shall require authorization.
```

The expected behavior is therefore defined independently of the ECU implementation.

### Test Through the Target Boundary

Security tests interact with the system under test through the defined target interface.
The test does not depend on internal ECU implementation details.

The current execution path is:

```text
Security Test
     ↓
Test Runner
     ↓
ECU Adapter
     ↓
Simulated ECU
     ↓
Response
```

This keeps the security-test logic independent from the concrete ECU implementation.

### Separate Expected and Actual Behavior

The expected result represents the security requirement.
The actual result represents the behavior returned by the system under test.

The evaluation is:

```text
Expected Behavior
        +
Actual Behavior
        ↓
Test Result
```

For example:

```text
Expected = ACCESS_DENIED

Actual   = ACCESS_GRANTED
```

results in:

```text
FAIL
```

The expected security behavior is not changed to make an insecure implementation pass.

### Keep Evidence Separate from Execution

Evidence is generated after test execution.
The evidence layer records the completed observation but does not control target behavior or test execution.

The separation is:

```text
Test Execution
      ↓
Test Result
      ↓
Evidence
```

This keeps evidence generation independent from the system under test.

### Keep Tests Reproducible

A security test should produce the same security-relevant result when executed against the same defined target state and input.

The current simulation therefore avoids dependencies on:

* physical hardware
* external networks
* external services
* uncontrolled target state
* random security behavior

Execution timestamps are generated dynamically and are treated as execution metadata rather than as part of the security decision.
The Phase-9 regression suite additionally creates a fresh secure ECU simulator for each regression scenario. Authorization state and ECU state are explicitly configured where required by the scenario.
This isolates individual regression cases from state changes caused by preceding tests and keeps the regression execution deterministic.

## Regression Methodology

A regression test is created by preserving the security property and reproducing the relevant test condition after a security-relevant change.
The Phase-7 implementation follows this controlled sequence:

```text
Security Property
        ↓
Existing Test Condition
        ↓
Controlled Vulnerable Behavior
        ↓
Secure Retest
        ↓
Expected vs Actual
        ↓
Regression Result
        ↓
Evidence
```

The expected security behavior remains independent of the observed target behavior.

For the TC-001 authorization property:

```text
Unauthorized protected operation
        ↓
Expected: ACCESS_DENIED
```

The controlled vulnerable mode demonstrates the modeled deviation:

```text
VULNERABLE

authorization = false
        ↓
ACCESS_GRANTED
```

The secure retest verifies the intended behavior:

```text
SECURE

authorization = false
        ↓
ACCESS_DENIED
```

The regression result is determined by the existing `SecurityTestRunner` and the expected-versus-actual comparison.
The Evidence Framework then records the completed execution.
The regression methodology therefore reuses the existing test and evidence architecture instead of introducing a separate regression execution mechanism.
Phase 9 adds automated pytest verification around the established security properties.
The Phase-9 regression scenarios execute against a fresh secure ECU simulator and verify expected secure responses for authorization, message validation, boundary input, ECU state, and regression evidence.
Phase 9 does not reproduce the vulnerable state as part of the pytest regression suite. Controlled vulnerable-state reproduction remains part of the Phase-7 TC-003 regression workflow.

---

# Current Implemented Methodology

## Step 1 — Security Requirement

The first step is to define the security property that the test is intended to verify.
A security requirement describes expected security behavior without depending on a specific implementation.

For TC-001:

```text
Protected diagnostic operations shall require authorization.
```

For TC-002, the requirement is:

```text
Invalid diagnostic requests shall be rejected before security-relevant
operation processing.
```

The requirement is translated into testable conditions.

Unauthorized access:

```text
Authorization = false
+
PROTECTED_OPERATION
        ↓
ACCESS_DENIED
```

Authorized access:

```text
Authorization = true
+
PROTECTED_OPERATION
        ↓
ACCESS_GRANTED
```

The requirement remains unchanged during test execution.

---

## Step 2 — Threat Model

The threat model identifies the asset, threat, potential attacker, and security property relevant to the test.

For TC-001:

### Asset

```text
Protected Diagnostic Operation
```

### Threat

```text
Unauthorized execution of a protected diagnostic operation
```

### Potential Attacker

```text
Unauthorized diagnostic client
```

### Security Property

```text
Authorization must be enforced before execution of the protected operation.
```

The threat model is limited to the behavior represented by the controlled simulation.
It does not represent a complete production vehicle threat model.

For TC-002:

### Asset

```text
Protected ECU Request Processing
```

### Threat

```text
Malformed or invalid diagnostic input reaching security-relevant processing
```

### Potential Attacker

```text
Unauthorized or malformed diagnostic client
```

### Security Property

```text
Invalid requests shall be rejected before security-relevant operation processing.
```

The threat model is limited to the request-validation behavior represented by the controlled simulation.

---

## Step 3 — Attack Surface

The attack surface identifies the interface through which the security property is evaluated.

For TC-001:

```text
Diagnostic Request
        ↓
Protected Operation
        ↓
Authorization Check
        ↓
ECU Response
```

For TC-002:

```text
Diagnostic Request
        ↓
Request Validation
        ↓
Operation Processing
        ↓
ECU Response
```

Within the project, this is represented by the request interface exposed by the simulated ECU.
No real CAN bus, UDS endpoint, vehicle network, or physical diagnostic interface is involved.
The documented attack surface therefore represents the simulated target boundary.

---

## Step 4 — Attack Hypothesis

The attack hypothesis describes how the security requirement could be violated.

For TC-001:

```text
If authorization is not correctly enforced,
an unauthorized requester may be able to execute
the protected operation.
```

The hypothesis is tested by submitting the protected operation while authorization is disabled.

```text
authorization = false

PROTECTED_OPERATION
```

The secure target is expected to return:

```text
ACCESS_DENIED
```

The controlled vulnerable target intentionally returns:

```text
ACCESS_GRANTED
```

This provides a deterministic security-relevant deviation for testing.

For TC-002:

```text
If malformed, unsupported, or otherwise impermissible requests are not
correctly validated, an invalid request may reach security-relevant
operation processing.
```

The hypothesis is tested by submitting deterministic invalid or impermissible requests to the simulated ECU.

The expected response depends on the validation condition:

```text
Invalid request structure
        ↓
INVALID_REQUEST
```

```text
Unsupported operation
        ↓
UNSUPPORTED_OPERATION
```

```text
Invalid parameter data or blocked ECU state
        ↓
REQUEST_REJECTED
```

The test therefore verifies that invalid or impermissible input is rejected deterministically before protected operation processing.

---

## Step 5 — Security Test

The security test translates the security requirement and attack hypothesis into an executable test definition.

The current `SecurityTestCase` abstraction contains:
* `test_id`
* `description`
* `request`
* `expected_status`

For TC-001, the protected operation is:

```text
PROTECTED_OPERATION
```

The unauthorized scenario expects:

```text
ACCESS_DENIED
```

The authorized scenario expects:

```text
ACCESS_GRANTED
```

The expected result is defined by the security test and is not derived from the response returned by the target.
TC-002 extends the security-test set with message-validation scenarios.
TC-002 evaluates the externally observable ECU response against the defined expected behavior.

The TC-002 validation flow is:

```text
TC-002 — Message Validation
        ↓
Request Validation
        ↓
+-----------------------------+
| Invalid request structure   | → INVALID_REQUEST
| Invalid parameter data      | → REQUEST_REJECTED
| Unsupported operation       | → UNSUPPORTED_OPERATION
| Blocked ECU state           | → REQUEST_REJECTED
+-----------------------------+
```

TC-002 therefore distinguishes between malformed or invalid request data, unsupported operations, and requests that are rejected because of parameter or ECU-state restrictions.

The expected response semantics are:

```text
Condition                                  Expected response
Request is not a valid mapping              INVALID_REQUEST
Operation is missing or empty               INVALID_REQUEST
Parameters are not a valid mapping          INVALID_REQUEST
Parameter value is outside 0..255           REQUEST_REJECTED
Parameter value is a boolean                REQUEST_REJECTED
Operation is not supported                  UNSUPPORTED_OPERATION
ECU is blocked                              REQUEST_REJECTED
```

The test verifies these externally observable response semantics without depending on the ECU simulator's internal validation implementation.
TC-002 is limited to deterministic message and parameter validation.
It does not introduce or imply a formal security-finding lifecycle, remediation management, regression management, or CI/CD workflow.
The test remains independent from the internal request-validation implementation of the ECU simulator.

### Phase-9 Automated Regression Test Definition

Phase 9 introduces a dedicated pytest regression suite in:

```text
04_tests/test_security_regression.py
```

The suite creates `SecurityTestCase` instances with:

```text
test_id = TC-003
```

These Phase-9 regression test cases reuse the existing security-test architecture, including `SecurityTestRunner`, `ECUAdapter`, `ECUSimulator`, and the existing response-status model.
They are not the same test-case definition as the TC-001 test case.
Each regression scenario uses a fresh secure ECU simulator. Authorization and ECU state are explicitly configured where required.
The verified Phase-9 regression scenarios are:

```text
Unauthorized protected operation
        ↓
Expected = ACCESS_DENIED
Actual   = ACCESS_DENIED
```

```text
Authorized protected operation
        ↓
Expected = ACCESS_GRANTED
Actual   = ACCESS_GRANTED
```

```text
Invalid message
        ↓
Expected = INVALID_REQUEST
Actual   = INVALID_REQUEST
```

```text
Unsupported operation
        ↓
Expected = UNSUPPORTED_OPERATION
Actual   = UNSUPPORTED_OPERATION
```

```text
Out-of-range boundary input

value = 256
        ↓
Expected = REQUEST_REJECTED
Actual   = REQUEST_REJECTED
```

```text
Protected operation while ECU is blocked
        ↓
Expected = REQUEST_REJECTED
Actual   = REQUEST_REJECTED
```

The seventh regression scenario additionally verifies that evidence generated from the secure retest contains the expected test identifier, target, preconditions, expected response, actual response, PASS result, and a valid Evidence object.
Phase 9 therefore automates verification of established security properties but does not introduce a new target, adapter, runner, evidence model, communication layer, or generalized regression orchestration mechanism.

---

## Step 6 — Preconditions

Security tests are executed under defined preconditions.

For TC-001, the relevant authorization states are:

Unauthorized:

```text
authorization = false
```

Authorized:

```text
authorization = true
```

The ECU security mode is also explicitly configured:

```text
secure
```

or:

```text
vulnerable
```

The vulnerable mode is used only to reproduce the intended security-relevant deviation in the controlled simulation.
For TC-002, the target is configured as a secure simulated ECU through the same target abstraction used by the security-test infrastructure.
The TC-002 scenarios establish their required conditions through the defined test inputs and explicit ECU state where required.

Invalid request structure:

```text
invalid request structure
```

Unsupported operation:

```text
unsupported operation
```

Invalid parameter value:

```text
parameter value outside 0..255
```

Blocked ECU state:

```text
ecu_state = blocked
```

The expected response depends on the specific validation condition and is defined by the individual TC-002 test case.
TC-002 does not require a separate authorization precondition for the message-validation scenarios, except where authorization is explicitly configured to establish the blocked-state scenario.
For Phase 9, each regression scenario starts with a fresh secure ECU simulator.

The relevant preconditions are explicitly configured per scenario:

```text
security_mode = secure

authorization = false or true

ecu_state = ready or blocked
```

This prevents state leakage between individual regression scenarios.

---

## Step 7 — Test Execution

The Test Runner executes the test through the target abstraction.

The execution path is:

```text
SecurityTestCase
        ↓
SecurityTestRunner
        ↓
ECUTarget
        ↓
ECUAdapter
        ↓
ECUSimulator
        ↓
ECUResponse
```

The Test Runner does not access internal ECU state.
The simulator processes the request and returns a structured response.
The response is then evaluated against the expected result defined by the security test.
Phase 9 invokes this existing execution path from pytest regression tests.
The pytest layer therefore acts as an automated verification layer around the established security-test architecture rather than replacing the Test Runner.

---

## Step 8 — Expected vs Actual Evaluation

The test result is determined by comparing expected and actual behavior.

The evaluation rule is:

```text
Expected == Actual
        ↓
PASS
```

and:

```text
Expected != Actual
        ↓
FAIL
```

Secure unauthorized execution:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_DENIED
Result   = PASS
```

Controlled vulnerable execution:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_GRANTED
Result   = FAIL
```

The `FAIL` represents an observed deviation from the defined security requirement.
It does not automatically establish a formal security finding.
In Phase 9, pytest additionally asserts the expected `TestResult` state.
A passing pytest regression test therefore confirms that the defined regression scenario produced the expected secure result.

For example:

```text
SecurityTestCase expected: ACCESS_DENIED
ECU actual:                ACCESS_DENIED
TestResult.passed:         True
pytest test:               PASS
```

---

## Step 9 — Evidence Generation

After test execution, the result can be represented as structured evidence.

The evidence flow is:

```text
Test Result
      ↓
Evidence Generator
      ↓
Evidence Model
      ↓
JSON
```

The current Evidence model records:

* `test_id`
* `timestamp`
* `target`
* `preconditions`
* `input`
* `expected`
* `actual`
* `result`
* `notes`

Evidence records what happened during the test execution.

It does not modify the target, expected result, or test execution.
Phase 9 additionally verifies regression evidence for the secure unauthorized protected-operation scenario.
The regression evidence contains the executed secure conditions:

```text
authorization = false
ecu_state = READY
security_mode = SECURE
```

and verifies:

```text
expected = ACCESS_DENIED
actual = ACCESS_DENIED
result = PASS
```

The generated evidence is then validated through the existing Evidence Framework.
This verifies that the regression evidence is structurally consistent with the executed secure retest.

---

## Step 10 — Security Finding Documentation

Phase 8 converts selected security-test observations into structured example finding documentation.
A finding is not created solely because a test returned `FAIL`.
The finding documentation is based on the relationship:

```text
Security Requirement
        ↓
Security Test
        ↓
Observed Behavior
        ↓
Evidence
        ↓
Security-Relevant Assessment
        ↓
Finding Documentation
```

For SEC-001, TC-001 reproduces a defined security-relevant deviation:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_GRANTED
Result   = FAIL
```

The observation is then documented with:

```text
Security Requirement
Threat Model
Preconditions
Reproduction Steps
Expected Behavior
Actual Behavior
Evidence
Security Impact
Exploitability
Root Cause
Recommendation
Fix
Retest
Regression Test
Status
```

For SEC-002, TC-002 does not reproduce a security-relevant deviation.

The corresponding documentation therefore records:

```text
Expected == Actual
        ↓
No security-relevant deviation reproduced
```

SEC-002 is retained as a Phase-8 example of structured assessment documentation and is not presented as a demonstrated vulnerability.

The finding documents are stored under:

```text
05_examples/
```

Phase 8 does not introduce automated finding ingestion, finding storage, historical finding tracking, or generalized vulnerability management.

---

## Security Test Result vs. Test Framework Result

The TC-003 lifecycle demonstration distinguishes between the security test result and the pytest test result.

For the controlled vulnerable behavior:

```text
SecurityTestCase expected: ACCESS_DENIED
ECUSimulator actual:       ACCESS_GRANTED
TestResult.passed:         False
```

The pytest test passes because it asserts that this deviation is correctly detected.

Therefore:

```text
pytest PASS
```

does not mean:

```text
SecurityTestResult PASS
```

for the vulnerable-state demonstration.

For the secure regression retest, both results are positive:

```text
SecurityTestCase expected: ACCESS_DENIED
ECUSimulator actual:       ACCESS_DENIED
TestResult.passed:         True
pytest test:               PASS
```

This distinction is required for a correct interpretation of the Phase-7 test lifecycle.
Phase 9 extends this distinction by asserting the expected secure `TestResult` through pytest.
The Phase-9 regression suite itself is expected to pass when the established security properties remain satisfied.

---

# TC-001 Methodology Example

TC-001 applies the implemented methodology as follows.

## Security Requirement

```text
Protected diagnostic operations shall require authorization.
```

## Threat

```text
Unauthorized execution of a protected diagnostic operation.
```

## Attack Surface

```text
Diagnostic Request
        ↓
Protected Operation
        ↓
Authorization Check
```

## Attack Hypothesis

```text
An unauthorized requester may execute the protected operation

if authorization is not correctly enforced.
```

## Preconditions

```text
authorization = false
ECU mode = secure or vulnerable
```

## Input

```text
PROTECTED_OPERATION
```

## Expected Secure Result

```text
ACCESS_DENIED
```

## Controlled Vulnerable Result

```text
ACCESS_GRANTED
```

## Evaluation

```text
Expected != Actual
        ↓
FAIL
```

## Evidence

```text
Test ID
Target
Preconditions
Input
Expected
Actual
Result
Timestamp
Notes
```

The authorized scenario additionally verifies:

```text
authorization = true

PROTECTED_OPERATION
        ↓
ACCESS_GRANTED
```

This confirms that authorization enforcement does not prevent valid authorized access.

# TC-002 Methodology Example

TC-002 applies the implemented methodology to message validation.

## Security Requirement

```text
Invalid diagnostic requests shall be rejected before security-relevant
operation processing.
```

## Threat

```text
Malformed, unsupported, or impermissible diagnostic input may reach
security-relevant processing.
```

## Attack Surface

```text
Diagnostic Request
        ↓
Request Validation
        ↓
Operation Processing
```

## Attack Hypothesis

```text
An invalid requester may reach operation processing if request validation
is not correctly enforced.
```

## Preconditions

```text
ECU mode = secure
```

Scenario-specific conditions may additionally include:

```text
ECU state = blocked
```

where required by the test scenario.

## Input

```text
Invalid request structure
or
Unsupported operation
or
Invalid parameter data
or
Protected operation while ECU is blocked
```

## Expected Result

The expected response depends on the validation condition:

```text
Invalid request structure -> INVALID_REQUEST
Unsupported operation -> UNSUPPORTED_OPERATION
Invalid parameter data -> REQUEST_REJECTED
Protected operation while ECU is blocked -> REQUEST_REJECTED
```

Valid parameter boundary values are separately verified:

```text
value = 0   -> ACCESS_GRANTED
value = 255 -> ACCESS_GRANTED
```

when the ECU is authorized and otherwise in an acceptable operational state.

## Evaluation

```text
Expected == Actual
        ↓
PASS
```

A deviation from the expected response results in:

```text
FAIL
```

The `FAIL` represents an observed deviation from the defined message-validation requirement.
It does not automatically establish a formal security finding.

## Evidence

TC-002 uses the existing Evidence Framework and records the same structured execution information as the other security tests:

```text
Test ID
Target
Preconditions
Input
Expected
Actual
Result
Timestamp
Notes
```

---

# TC-003 Methodology Example

TC-003 applies the implemented methodology to the controlled regression of the diagnostic authorization security property established by TC-001.
The TC-003 regression workflow and the Phase-9 pytest regression suite must be distinguished.
The Phase-7 TC-003 workflow demonstrates the complete controlled regression lifecycle, including vulnerable-state reproduction, secure retest, regression evidence, and authorized-behavior verification.
Phase 9 provides automated pytest verification of established security properties and the secure regression evidence.

## Security Property

```text
Protected diagnostic operations shall require authorization.
```

## Existing Test Condition

```text
authorization = false

PROTECTED_OPERATION
```

The expected security behavior remains:

```text
ACCESS_DENIED
```

## Controlled Vulnerable-State Reproduction

The vulnerable mode represents the modeled pre-fix behavior in a controlled simulation.

```text
VULNERABLE

authorization = false
        ↓
ACCESS_GRANTED
```

The resulting security test outcome is:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_GRANTED
Result   = FAIL
```

The `FAIL` is intentional for this lifecycle step because TC-003 verifies that the original security deviation can be reproduced and detected.

## Secure Retest

The same unauthorized condition is then executed against the secure simulator mode:

```text
SECURE

authorization = false
        ↓
ACCESS_DENIED
```

The resulting security test outcome is:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_DENIED
Result   = PASS
```

This verifies that the diagnostic authorization security property is restored in the controlled secure state.

## Authorized-Behavior Verification

TC-003 additionally verifies that valid authorized access remains available:

```text
SECURE

authorization = true
        ↓
ACCESS_GRANTED
```

The resulting security test outcome is:

```text
Expected = ACCESS_GRANTED
Actual   = ACCESS_GRANTED
Result   = PASS
```

This ensures that the regression verification does not only check rejection of unauthorized access but also confirms preservation of authorized behavior.

## Regression Evidence

The regression evidence is generated from the executed `TestResult`.

The workflow is:

```text
Controlled Vulnerable Behavior
        ↓
Original Security Condition
        ↓
Secure Retest
        ↓
Expected vs Actual
        ↓
Regression Evidence
        ↓
Evidence Validation
        ↓
Authorized Behavior Verification
```

The Evidence Framework records the executed regression result and validates the resulting Evidence object.

TC-003 does not introduce a separate evidence model or a separate execution mechanism.

## Phase-9 Automated Regression Verification

Phase 9 verifies the established security properties through:

```text
04_tests/test_security_regression.py
```

The suite defines its own `SecurityTestCase` instances with:

```text
test_id = TC-003
```

These test cases reuse the existing test execution architecture but are distinct from the TC-001 test-case definition.
Each scenario uses a fresh secure ECU simulator.

The verified regression conditions are:

```text
Unauthorized protected operation
        ↓
ACCESS_DENIED
```

```text
Authorized protected operation
        ↓
ACCESS_GRANTED
```

```text
Invalid request
        ↓
INVALID_REQUEST
```

```text
Unsupported operation
        ↓
UNSUPPORTED_OPERATION
```

```text
Out-of-range parameter value

value = 256
        ↓
REQUEST_REJECTED
```

```text
Blocked ECU state
        ↓
REQUEST_REJECTED
```

The final Phase-9 scenario verifies that the generated regression evidence represents the secure retest and that the evidence object passes validation.
The Phase-9 suite therefore verifies established security behavior automatically without implementing vulnerable-state reproduction, historical comparison, or generalized regression orchestration.

---

# Evidence and Traceability

The methodology maintains traceability from the security requirement to the test execution and resulting evidence.

The current relationship is:

```text
Security Requirement
        ↓
Threat Model
        ↓
Attack Surface
        ↓
Attack Hypothesis
        ↓
Security Test
        ↓
Test Execution
        ↓
Test Result
        ↓
Evidence
```

This allows a test execution to be related to the security property it was designed to verify.
The current implementation provides this relationship for the implemented security tests, including TC-001 and TC-002, at the test and evidence level.
For TC-003, the existing TC-001 security property is reused to provide a controlled regression workflow.
Phase 8 extends the documentation layer by relating selected existing test and evidence results to structured example findings.
Phase 9 extends automated verification of the established security properties and verifies that the regression evidence generated from a secure retest matches the executed test result.

The Phase-9 relationship is:

```text
Established Security Property
        ↓
Phase-9 Regression Test Case
        ↓
SecurityTestRunner
        ↓
Secure ECU Execution
        ↓
TestResult
        ↓
Regression Evidence
        ↓
Evidence Validation
```

The current Phase-8 relationship is:

```text
Security Requirement
        ↓
Security Test
        ↓
Test Result
        ↓
Evidence
        ↓
Example Finding
```

SEC-001 is based on the controlled security-relevant deviation reproduced by TC-001.
SEC-002 documents the TC-002 assessment where no security-relevant deviation was reproduced.
More advanced requirement identifiers, finding identifiers, and automated traceability are planned for later phases.

---

# Reproducibility

Reproducibility is a core requirement of the methodology.
The same test should be executable repeatedly against the same defined target state and input.

The current simulation supports this through:
* deterministic ECU behavior
* explicit security modes
* explicit authorization state
* controlled requests
* deterministic response statuses
* structured evidence
* absence of external dependencies

The Phase-9 regression suite additionally supports reproducibility by:
* creating a fresh secure ECU simulator for each regression scenario
* explicitly configuring authorization where required
* explicitly configuring ECU state where required
* using deterministic request inputs
* using fixed expected response statuses
* avoiding dependency on previous test execution state

The execution timestamp changes between runs.
This is expected because the timestamp records when the test was executed.
It does not affect the security-test result.

---

# Validation of the Test Infrastructure

The methodology applies verification to both the simulated target and the security-test infrastructure.

The current verification layers are:

```text
ECU Simulation Tests
        ↓
Security Test Architecture Tests
        ↓
Evidence Framework Tests
        ↓
TC-001 Security Test
        ↓
TC-002 Security Test
        ↓
TC-003 Regression Workflow Tests
        ↓
Phase-9 Security Regression Suite
        ↓
Complete pytest Suite
```

Phase 9 provides the following verified regression coverage:

```text
Unauthorized protected operation
Authorized protected operation
Invalid message
Unsupported operation
Boundary input validation
Blocked ECU state
Regression evidence validation
```

The dedicated Phase-9 regression suite was locally verified with:

```text
7 passed
```

The complete pytest suite was locally verified with:

```text
41 passed
```

The verified test distribution is:

```text
ECU Simulation Tests                 6
Evidence Framework Tests            14
Foundation Test                     1
Security Regression Tests           7
TC-001 Security Test                4
TC-002 Security Test                5
Test Runner Tests                   4
Total                               41
```

This allows changes in the ECU simulation, test architecture, evidence handling, security-test implementation, or established regression properties to be detected through automated tests.
The test infrastructure is therefore treated as software that also requires verification.
Phase 9 remains a local deterministic pytest verification layer.
CI/CD execution is not part of Phase 9.

---

# Future Security Lifecycle

The project currently demonstrates a controlled retest and regression workflow through Phase 7, structured example finding documentation through Phase 8, and automated pytest regression verification through Phase 9.

The following capabilities remain future work:

```text
Generalized Security Finding Management
        ↓
Automated Finding Ingestion
        ↓
Remediation Tracking
        ↓
Historical Regression Comparison
        ↓
Generalized Regression Orchestration
        ↓
CI/CD
```

Phase 7 therefore provides a verified regression workflow for the defined TC-001 security property.
Phase 8 provides structured example finding documentation based on existing test and evidence results.
Phase 9 provides automated pytest verification of established security properties.
Neither Phase 7, Phase 8, nor Phase 9 implements a generalized security finding, remediation, historical comparison, or regression management platform.

---

## Security Finding

Phase 8 introduces structured example security findings based on the existing security-test and evidence workflow.

The finding documentation formalizes a security-relevant observation by recording:
* affected security property
* observed behavior
* security impact
* exploitability
* root cause where supported by implementation evidence
* recommendation
* fix
* retest
* regression relationship
* status

A test `FAIL` alone is not treated as a complete finding.
SEC-001 demonstrates the finding workflow for the controlled authorization deviation reproduced by TC-001.
SEC-002 demonstrates the documentation of an assessment result where no security-relevant deviation was reproduced by TC-002.
The finding documents are portfolio documentation artifacts. They do not implement a generalized finding-management system.

---

## Root Cause

Root-cause analysis determines why the observed security behavior occurred.

For the controlled vulnerable TC-001 scenario, the modeled root cause is:

```text
The authorization state is not enforced before execution
of the protected operation.
```

This describes the behavior of the simulated target.
It is not a claim about a real ECU implementation.
Phase 8 documents root cause for a finding where the available implementation evidence supports a concrete cause.
For SEC-001, the root cause is directly traceable to the deliberate vulnerable branch in `ECUSimulator.handle_request()`.
SEC-002 does not establish a security-relevant deviation and therefore does not assign a vulnerability root cause.

---

## Recommended Fix

The remediation should address the security cause rather than modify the security test expectation.
For TC-001, the simulated ECU must enforce authorization before granting the protected operation.

The required security property remains:

```text
Protected diagnostic operations shall require authorization.
```

The security test is not weakened to accommodate an insecure implementation.
SEC-001 documents this remediation relationship explicitly.
For SEC-002, no corrective fix is claimed because no security-relevant deviation was reproduced.

---

## Implemented Fix

The implemented fix changes the system under test so that it satisfies the security requirement.

The expected relationship is:

```text
Security Requirement
        ↓
Test Failure
        ↓
Root Cause
        ↓
Fix
        ↓
Same Security Test
```

The test expectation remains unchanged.
Phase 8 documents the implemented fix and retest relationship for SEC-001.
This documentation does not constitute a generalized finding, remediation, or retest management capability.

---

## Retest

After a fix, the original security test is executed again.
The retest uses the same security requirement and security-test logic.

The intended flow is:

```text
Security-Relevant Deviation
        ↓
Fix
        ↓
Same Security Test
        ↓
Retest
        ↓
Expected Secure Behavior
```

For TC-001:

```text
authorization = false

PROTECTED_OPERATION
        ↓
ACCESS_DENIED
```

and:

```text
authorization = true

PROTECTED_OPERATION
        ↓
ACCESS_GRANTED
```

The purpose of the retest is to verify that the security property is now satisfied.
Phase 7 implements a controlled retest as part of TC-003 for the diagnostic authorization security property.
Phase 8 documents the retest relationship for SEC-001.
A generalized project-level retest workflow remains future work.

---

## Regression

Retesting verifies the specific corrected security behavior.
Regression testing verifies that previously established security behavior remains correct after later changes.

The current Phase-7 regression workflow is:

```text
Original Security Condition
        ↓
Controlled Vulnerable-State Reproduction
        ↓
Secure Retest
        ↓
Regression Evaluation
        ↓
Regression Evidence
```

This workflow is implemented specifically for the diagnostic authorization security property represented by TC-001.

Phase 9 adds automated pytest verification of established security properties:

```text
Established Security Properties
        ↓
Phase-9 Regression Tests
        ↓
Secure ECU Execution
        ↓
Expected vs Actual
        ↓
Automated Regression Result
```

The Phase-9 suite covers authorization, request validation, boundary input handling, ECU state restrictions, and regression evidence validation.
The project does not implement historical result comparison or a generalized regression orchestration layer.

---

## Automated Regression

The long-term regression model is:

```text
Security Test Cases
        ↓
Automated Regression Suite
        ↓
Test Results
        ↓
Evidence
```

Phase 7 provides a verified, specific regression workflow through TC-003.
Phase 9 provides the currently implemented automated pytest regression suite.

The Phase-9 suite is located in:

```text
04_tests/test_security_regression.py
```

It verifies established security properties against fresh secure ECU simulator instances.

The verified scenarios are:

```text
Unauthorized protected operation -> ACCESS_DENIED
Authorized protected operation -> ACCESS_GRANTED
Invalid message -> INVALID_REQUEST
Unsupported operation -> UNSUPPORTED_OPERATION
Out-of-range parameter value -> REQUEST_REJECTED
Blocked ECU state -> REQUEST_REJECTED
Regression evidence -> validated PASS evidence
```

The dedicated regression suite currently contains seven pytest tests.

Local verification confirmed:

```text
7 passed
```

The Phase-9 suite does not implement:

```text
Vulnerable-state reproduction
Historical result comparison
Finding ingestion
Finding lifecycle management
Generalized regression orchestration
CI/CD execution
```

Those capabilities remain outside the current implementation.

---

## CI/CD

The final automation stage is integration with CI/CD.

The target workflow is:

```text
Code Change
      ↓
CI Pipeline
      ↓
Security Regression Suite
      ↓
Test Results
      ↓
Pipeline Decision
```

The current project uses local pytest execution for verification.

Phase 9 provides the automated pytest regression suite that is intended to become part of the later CI/CD execution flow.

GitHub Actions and automated CI/CD execution are planned for Phase 10.

---

# Relationship to Project Phases

The methodology is developed incrementally together with the project.

```text
Phase 0
Project Definition
        ↓
Phase 1
Repository Foundation
        ↓
Phase 2
ECU Simulation
        ↓
Phase 3
Security Test Architecture
        ↓
Phase 4
Evidence Framework
        ↓
Phase 5
TC-001
        ↓
Phase 6
TC-002
        ↓
Phase 7
TC-003 Regression Workflow
        ↓
Phase 8
Example Findings
SEC-001 / SEC-002 structured example finding documentation
        ↓
Phase 9
pytest Regression Suite
        ↓
Phase 10
GitHub Actions / CI/CD
        ↓
Phase 11
End-to-End Assessment
        ↓
Phase 12
Professional Documentation
        ↓
Phase 13
Technical Review
        ↓
Phase 14
Recruiter / Interview Review
```

Each phase adds a concrete capability to the overall methodology.
The project does not treat planned stages as completed functionality.

---

# Scope and Limitations

The methodology is currently defined for the controlled simulation environment of the Automotive Security Regression Lab.

It does not define procedures for:
* real vehicle security assessments
* physical ECU testing
* real CAN communication
* real UDS communication
* production diagnostic interfaces
* OEM infrastructure
* customer systems
* production penetration testing

The methodology demonstrates engineering principles for reproducible security testing.
It is not presented as a complete operational methodology for real-world automotive penetration testing.

---

# Current Implementation Status

The methodology currently supports:

```text
Security Requirement
        ↓
Threat Model
        ↓
Attack Surface
        ↓
Attack Hypothesis
        ↓
Security Test
        ↓
Test Execution
        ↓
Expected vs Actual
        ↓
Evidence
        ↓
Controlled Security-Relevant Deviation
        ↓
Secure Retest
        ↓
Regression Evaluation
        ↓
Regression Evidence
        ↓
Example Finding Documentation
        ↓
Automated Security Regression Tests
```

Implemented capabilities include:
* deterministic ECU simulation
* secure and vulnerable ECU modes
* security-test abstractions
* target abstraction through `ECUTarget`
* ECU adapter
* automated test execution
* expected-versus-actual evaluation
* structured evidence
* JSON serialization
* TC-001 Diagnostic Authorization
* TC-002 Message Validation
* TC-003 Regression Workflow
* Phase-9 automated pytest security regression suite
* local pytest verification

The Phase-9 regression suite verifies seven scenarios covering:

```text
Unauthorized protected operation
Authorized protected operation
Invalid message
Unsupported operation
Boundary input validation
Blocked ECU state
Regression evidence validation
```

The local verification status is:

```text
Dedicated Phase-9 regression suite: 7 passed
Complete pytest suite:              41 passed
```

The following capabilities belong to later project phases:
* generalized security finding management
* automated finding ingestion
* root-cause management as a generalized lifecycle capability
* remediation tracking
* generalized retest workflow
* historical regression comparison
* generalized regression orchestration
* CI/CD integration
* end-to-end assessment
* professional documentation package
* technical review
* recruiter / interview review

Phase 8 additionally provides the following documentation artifacts:

```text
SEC-001 — Unauthorized access to protected diagnostic operation
SEC-002 — No security-relevant deviation reproduced in diagnostic message validation
```

These are structured example findings and assessment records. They do not constitute a generalized finding-management implementation.
Phase 9 additionally provides an automated pytest regression verification layer.
This layer does not constitute a generalized regression-management platform and does not include CI/CD execution.

---

# Methodological Principle

The central principle of the Automotive Security Regression Lab is:

```text
Define the security property
        ↓
Model the threat
        ↓
Formulate the attack hypothesis
        ↓
Test the property
        ↓
Observe the target
        ↓
Record the result
        ↓
Correct the implementation
        ↓
Retest
        ↓
Prevent regression
```

Only the stages implemented in the current project phase are treated as verified capabilities.
The methodology keeps the security requirement, system under test, test execution, evidence, and later security-lifecycle activities separate.
Phase 9 strengthens the regression stage by providing automated pytest verification of established security properties while preserving the existing security-test and evidence architecture.
This separation provides a controlled basis for extending individual security tests into a reproducible security regression workflow and, ultimately, an automated CI/CD process.
