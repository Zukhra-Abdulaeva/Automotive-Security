# Security Testing Methodology

## Purpose

The Automotive Security Regression Lab uses a structured methodology to turn a
defined security requirement into a reproducible security test.

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

The current implementation covers the security-test and evidence workflow
through Phase 5 — TC-001 Diagnostic Authorization.

Later phases extend this workflow into security finding management, remediation,
retesting, regression testing, and CI/CD.

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
```

The distinction between implemented and planned capabilities is maintained
throughout this document.

---

## Methodology Principles

### Define the Security Property First

The expected security behavior is defined before test execution.

The security test evaluates a security requirement rather than deriving the
requirement from the observed implementation.

For TC-001, the requirement is:

```text
Protected diagnostic operations shall require authorization.
```

The expected behavior is therefore defined independently of the ECU
implementation.

---

### Test Through the Target Boundary

Security tests interact with the system under test through the defined target
interface.

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

This keeps the security-test logic independent from the concrete ECU
implementation.

---

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

The expected security behavior is not changed to make an insecure
implementation pass.

---

### Keep Evidence Separate from Execution

Evidence is generated after test execution.

The evidence layer records the completed observation but does not control
target behavior or test execution.

The separation is:

```text
Test Execution
      ↓
Test Result
      ↓
Evidence
```

This keeps evidence generation independent from the system under test.

---

### Keep Tests Reproducible

A security test should produce the same security-relevant result when executed
against the same defined target state and input.

The current simulation therefore avoids dependencies on:

* physical hardware
* external networks
* external services
* uncontrolled target state
* random security behavior

Execution timestamps are generated dynamically and are treated as execution
metadata rather than as part of the security decision.

---

# Current Implemented Methodology

## Step 1 — Security Requirement

The first step is to define the security property that the test is intended
to verify.

A security requirement describes expected security behavior without depending
on a specific implementation.

For TC-001:

```text
Protected diagnostic operations shall require authorization.
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

The threat model identifies the asset, threat, potential attacker, and
security property relevant to the test.

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

The threat model is limited to the behavior represented by the controlled
simulation.

It does not represent a complete production vehicle threat model.

---

## Step 3 — Attack Surface

The attack surface identifies the interface through which the security
property is evaluated.

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

Within the project, this is represented by the request interface exposed by
the simulated ECU.

No real CAN bus, UDS endpoint, vehicle network, or physical diagnostic
interface is involved.

The documented attack surface therefore represents the simulated target
boundary.

---

## Step 4 — Attack Hypothesis

The attack hypothesis describes how the security requirement could be
violated.

For TC-001:

```text
If authorization is not correctly enforced,
an unauthorized requester may be able to execute
the protected operation.
```

The hypothesis is tested by submitting the protected operation while
authorization is disabled.

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

---

## Step 5 — Security Test

The security test translates the security requirement and attack hypothesis
into an executable test definition.

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

The expected result is defined by the security test and is not derived from
the response returned by the target.

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

The vulnerable mode is used only to reproduce the intended security-relevant
deviation in the controlled simulation.

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

The response is then evaluated against the expected result defined by the
security test.

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

The `FAIL` represents an observed deviation from the defined security
requirement.

It does not automatically establish a formal security finding.

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

This confirms that authorization enforcement does not prevent valid
authorized access.

---

# Evidence and Traceability

The methodology maintains traceability from the security requirement to the
test execution and resulting evidence.

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

This allows a test execution to be related to the security property it was
designed to verify.

The current implementation provides this relationship at the test and
evidence level.

More advanced requirement identifiers, finding identifiers, and automated
traceability are planned for later phases.

---

# Reproducibility

Reproducibility is a core requirement of the methodology.

The same test should be executable repeatedly against the same defined target
state and input.

The current simulation supports this through:

* deterministic ECU behavior
* explicit security modes
* explicit authorization state
* controlled requests
* deterministic response statuses
* structured evidence
* absence of external dependencies

The execution timestamp changes between runs.

This is expected because the timestamp records when the test was executed.

It does not affect the security-test result.

---

# Validation of the Test Infrastructure

The methodology applies verification to both the simulated target and the
security-test infrastructure.

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
Complete pytest Suite
```

This allows changes in the ECU simulation, test architecture, evidence
handling, or security-test implementation to be detected through automated
tests.

The test infrastructure is therefore treated as software that also requires
verification.

---

# Future Security Lifecycle

The long-term methodology extends the current test and evidence workflow into
a complete security lifecycle.

The target workflow is:

```text
Security-Relevant Observation
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
```

These stages are part of the target methodology but are not yet implemented
as a complete workflow in the current phase.

---

## Security Finding

A security finding formalizes a confirmed security-relevant observation.

The finding process will provide a structured basis for documenting:

* affected security property
* observed behavior
* security impact
* root cause
* remediation
* verification status

A test `FAIL` alone is not treated as a complete finding.

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

Generalized root-cause management belongs to a later project phase.

---

## Recommended Fix

The remediation should address the security cause rather than modify the
security test expectation.

For TC-001, the simulated ECU must enforce authorization before granting the
protected operation.

The required security property remains:

```text
Protected diagnostic operations shall require authorization.
```

The security test is not weakened to accommodate an insecure implementation.

---

## Implemented Fix

The implemented fix changes the system under test so that it satisfies the
security requirement.

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

The purpose of the retest is to verify that the security property is now
satisfied.

---

## Regression

Retesting verifies the specific corrected security behavior.

Regression testing verifies that previously established security behavior
remains correct after later changes.

The target workflow is:

```text
Code Change
      ↓
Regression Suite
      ↓
Existing Security Tests
      ↓
Results
      ↓
Evidence
```

The current project does not yet implement a complete regression orchestration
layer.

Regression capabilities are introduced in later project phases.

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

The regression suite will provide repeatable execution of established
security tests.

The current implementation verifies the existing test set through pytest,
but the complete regression workflow belongs to a later phase.

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
Finding → Root Cause → Fix → Retest → Regression
        ↓
Phase 8
SEC-001 / SEC-002
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

The methodology is currently defined for the controlled simulation
environment of the Automotive Security Regression Lab.

It does not define procedures for:

* real vehicle security assessments
* physical ECU testing
* real CAN communication
* real UDS communication
* production diagnostic interfaces
* OEM infrastructure
* customer systems
* production penetration testing

The methodology demonstrates engineering principles for reproducible
security testing.

It is not presented as a complete operational methodology for real-world
automotive penetration testing.

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
* local pytest verification

The following capabilities belong to later project phases:

* TC-002 Message Validation
* security finding management
* root-cause management
* remediation tracking
* retest workflow as a generalized project capability
* complete regression orchestration
* SEC-001 / SEC-002 example findings
* dedicated pytest regression suite
* CI/CD integration
* end-to-end assessment
* professional documentation package
* technical review
* recruiter / interview review

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

Only the stages implemented in the current project phase are treated as
verified capabilities.

The methodology keeps the security requirement, system under test, test
execution, evidence, and later security-lifecycle activities separate.

This separation provides a controlled basis for extending individual security
tests into a reproducible security regression workflow and, ultimately, an
automated CI/CD process.
