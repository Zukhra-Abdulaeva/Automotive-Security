# Architecture

## Purpose

The Automotive Security Regression Lab uses a deterministic software
architecture for developing and executing automotive security tests against a
simulated ECU.

The architecture was introduced in Phase 3 and extended in Phase 4 with the
Evidence Framework. Phase 5 adds TC-001 — Diagnostic Authorization, Phase 6
adds TC-002 — Message Validation, Phase 7 adds the verified TC-003 Regression
Workflow, Phase 8 adds structured example finding documentation for the
security observations represented by TC-001 and TC-002, Phase 9 adds the
automated pytest security regression suite for established security
properties, and Phase 10 adds the minimal GitHub Actions CI/CD pipeline for
automated execution of the established security regression suite and
collection of regression evidence.

The architecture separates the following responsibilities:

* security-test definition
* test execution
* target interaction
* simulated ECU behavior
* test-result evaluation
* evidence generation
* automated regression verification
* CI/CD execution and evidence artifact handling

The separation is intentional. The security test defines the expected
security behavior, the simulated ECU provides the system-under-test behavior,
the Test Runner evaluates the execution result, and the Evidence Framework
records the resulting observation. Phase 9 adds automated regression tests as
a verification layer around these existing components rather than introducing
a second execution architecture. Phase 10 executes this established
regression suite through GitHub Actions and collects the generated evidence
without introducing a second security-test implementation.

The project remains fully simulated and deterministic. It does not communicate
with real vehicles, real ECUs, CAN networks, UDS endpoints, OEM systems, or
production systems.

---

## System Context

The project models the basic relationship between a security tester and an
automotive system in a controlled Python environment.

A simplified real-world concept can be represented as:

```text
Security Tester
       |
       v
Diagnostic Interface
       |
       v
Communication Layer
       |
       v
ECU
```

The project does not implement this real-world communication stack.

Instead, the current implementation represents the testing workflow through
the following local architecture:

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

Phase 9 adds an automated verification layer around the existing execution
architecture:

```text
Established Security Properties
          |
          v
04_tests/test_security_regression.py
          |
          v
SecurityTestCase
          |
          v
SecurityTestRunner
          |
          v
ECUAdapter
          |
          v
Fresh Secure ECUSimulator
          |
          v
TestResult
          |
          v
EvidenceGenerator
```

This Phase-9 path represents automated pytest verification. It does not
replace the existing runtime architecture.

Phase 10 adds the CI/CD execution layer around the established Phase-9
regression suite:

```text
GitHub Event
       |
       +-- push
       |
       +-- pull_request
       |
       v
GitHub Actions
       |
       v
Checkout Repository
       |
       v
Python 3.12
       |
       v
Install Dependencies
       |
       v
pytest Security Regression Suite
       |
       v
04_tests/test_security_regression.py
       |
       v
Existing Regression Execution Path
       |
       v
EvidenceGenerator
       |
       v
Evidence
       |
       v
Evidence.to_json()
       |
       v
CI Evidence JSON Files
       |
       v
GitHub Actions Artifact
```

The CI/CD layer does not replace the local regression architecture. It invokes
the established regression test module and uses its existing execution and
evidence-generation path.

---

## Phase-7 Regression Flow

Phase 7 reuses the existing architecture rather than introducing a separate
regression execution stack.

The TC-003 execution path is:

```text
Existing TC-001 SecurityTestCase
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
ECUResponse
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

The regression workflow uses the same security condition in both simulator
modes:

```text
SecurityMode.VULNERABLE
        |
        v
Controlled reproduction of the modeled deviation
        |
        v
SecurityMode.SECURE
        |
        v
Retest of the same unauthorized condition
```

The regression module does not modify the `SecurityTestRunner`,
`ECUAdapter`, or Evidence Framework.

TC-003 therefore extends the use of the existing architecture rather than
introducing a new execution abstraction.

The `ECUSimulator` is the system under test.

The security-test infrastructure communicates with the simulated target
through the defined target interface. It does not directly manipulate the
internal implementation of the ECU simulator.

---

## Architectural Components

The current architecture consists of the following logical components:

```text
+---------------------------+
|    Security Test Case     |
+-------------+-------------+
              |
              v
+---------------------------+
|     SecurityTestRunner    |
+-------------+-------------+
              |
              v
+---------------------------+
|        ECUTarget          |
+-------------+-------------+
              |
              v
+---------------------------+
|        ECUAdapter         |
+-------------+-------------+
              |
              v
+---------------------------+
|        ECUSimulator       |
+-------------+-------------+
              |
              v
+---------------------------+
|       ECUResponse         |
+-------------+-------------+
              |
              v
+---------------------------+
|        TestResult         |
+-------------+-------------+
              |
              v
+---------------------------+
|    Evidence Framework     |
+---------------------------+
```

Each component has a defined responsibility.

The architecture deliberately prevents security-test logic, ECU security
behavior, and evidence generation from being combined into a single
component.

Phase 9 does not add another target, adapter, runner, response model, or
evidence model. It adds automated pytest verification around the established
components.

Phase 10 does not add another target, adapter, runner, response model, or
evidence model either. It adds a CI/CD execution layer that invokes the
established regression suite and stores the generated evidence as a GitHub
Actions artifact.

---

## SecurityTestCase

`SecurityTestCase` represents the definition of a security test.

The current implementation contains:

* `test_id`
* `description`
* `request`
* `expected_status`

The test case defines the request that is sent to the target and the response
status that is expected for the defined security scenario.

For TC-001, the test case represents the protected diagnostic operation and
the expected authorization behavior.

The test case does not implement the ECU security policy.

The expected result is therefore defined independently from the concrete
implementation of the simulated ECU.

For the Phase-7 TC-003 regression workflow, the existing TC-001
`SecurityTestCase` is reused as described in the Phase-7 implementation.

Phase 9 uses the same `SecurityTestCase` architecture but creates its own
test-case instances inside `04_tests/test_security_regression.py`. These
regression scenarios use:

```text
test_id = "TC-003"
```

They therefore reuse the established `SecurityTestCase` structure and the
existing execution architecture without reusing the same TC-001
`SecurityTestCase` instance or definition.

The Phase-9 relationship is:

```text
Phase-9 automated regression test
        |
        v
04_tests/test_security_regression.py
        |
        v
SecurityTestCase
        |
        +-- test_id = "TC-003"
        |
        +-- request = defined regression scenario
        |
        +-- expected_status = established security behavior
        |
        v
SecurityTestRunner
```

This distinction preserves the original Phase-7 architecture while allowing
Phase 9 to define independent automated regression scenarios using the same
test-case model.

Phase 10 does not redefine these test cases. GitHub Actions invokes the
existing Phase-9 regression suite and therefore uses the same established
test-case definitions and expected security behavior.

---

## SecurityTestRunner

`SecurityTestRunner` controls the execution of a security test.

Its responsibilities are:

1. accept a `SecurityTestCase`
2. send the request through the target interface
3. receive the ECU response
4. compare the actual response status with the expected status
5. create a structured `TestResult`

The execution flow is:

```text
SecurityTestCase
       |
       v
SecurityTestRunner
       |
       v
Target
       |
       v
ECU Response
       |
       v
Expected vs Actual
       |
       v
TestResult
```

The Test Runner does not access internal ECU state.

It does not implement:

* ECU security policy
* authorization decisions
* security finding management
* evidence storage
* regression orchestration
* CI/CD

The Test Runner is responsible for executing and evaluating the security
test, not for implementing the security behavior being tested.

For TC-003, the existing `SecurityTestRunner` remains responsible for the
expected-versus-actual comparison. No separate regression execution engine
is introduced.

Phase 9 also uses the existing `SecurityTestRunner`. The pytest regression
suite therefore verifies the behavior of the established test execution
architecture rather than introducing a separate regression runner.

Phase 10 does not modify the responsibilities of the Test Runner. GitHub
Actions invokes the existing regression suite from outside the test execution
architecture.

---

## ECUTarget

`ECUTarget` defines the target interface used by the security-test runner.

The abstraction separates the test infrastructure from the concrete target
implementation.

The current relationship is:

```text
SecurityTestRunner
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

The target interface defines how the test infrastructure interacts with the
system under test.

The current implementation uses the simulated ECU behind this interface.

No real vehicle communication protocol is implemented through `ECUTarget`.

Phase 9 does not introduce another target interface. The automated regression
suite executes against the existing simulated target.

Phase 10 does not introduce another target interface. The CI/CD workflow
executes the same simulated target through the established regression path.

---

## ECUAdapter

`ECUAdapter` connects the abstract `ECUTarget` interface to the concrete
`ECUSimulator`.

Its responsibility is to forward requests to the configured target and return
the resulting response.

The adapter does not:

* define security requirements
* implement security-test logic
* make authorization decisions
* evaluate security findings
* generate evidence
* modify test results

The adapter therefore provides the boundary between the generic test
execution layer and the concrete simulated target.

This separation allows the test infrastructure to remain independent from the
concrete ECU simulator implementation.

Phase 9 reuses the same adapter boundary for automated regression execution.

Phase 10 does not change or bypass the adapter boundary. The CI/CD workflow
executes the existing regression suite, which continues to use the established
adapter and simulated target.

---

## ECUSimulator

`ECUSimulator` represents the simulated ECU and is the system under test.

The simulator was introduced in Phase 2 and provides the target behavior used
by the security-test architecture.

Its responsibilities include:

* maintaining the configured security mode
* maintaining the authorization state
* validating incoming requests
* processing the requested operation
* applying the configured security behavior
* returning a deterministic `ECUResponse`

The simulator supports two security modes:

```text
secure
vulnerable
```

### Secure Mode

Secure mode enforces authorization before granting the protected operation.

```text
authorization = false
PROTECTED_OPERATION
       |
       v
ACCESS_DENIED
```

and:

```text
authorization = true
PROTECTED_OPERATION
       |
       v
ACCESS_GRANTED
```

### Vulnerable Mode

Vulnerable mode intentionally reproduces the authorization deviation used by
the security tests:

```text
authorization = false
PROTECTED_OPERATION
       |
       v
ACCESS_GRANTED
```

The vulnerable behavior is a controlled simulation condition. It does not
represent a real ECU vulnerability or a claim about a production automotive
system.

For Phase 7, the vulnerable mode is used to reproduce the modeled pre-fix
behavior in a controlled test environment. Secure mode represents the
intended secure behavior used for the regression retest.

Phase 9 executes its automated regression scenarios against fresh secure
simulator instances. Vulnerable-state reproduction remains part of the
controlled Phase-7 regression workflow and is not duplicated by the Phase-9
pytest suite.

The simulator remains independent from the Test Runner and Evidence
Framework.

It does not generate, store, or evaluate test evidence.

Phase 10 does not alter the simulator or introduce a CI-specific target
behavior. The CI/CD pipeline executes the same deterministic secure simulator
behavior used by the Phase-9 regression suite.

---

## ECUResponse

The simulator returns an `ECUResponse`.

The current response model contains:

* `status`
* `operation`

The supported response statuses are:

```text
ACCESS_GRANTED
ACCESS_DENIED
INVALID_REQUEST
UNSUPPORTED_OPERATION
REQUEST_REJECTED
```

The response represents the behavior observed by the security-test
infrastructure.

For a given security mode, authorization state, and request, the simulator
produces a deterministic response.

The response can be converted into a dictionary representation using
`to_dict()`.

---

## TestResult

`TestResult` represents the evaluated outcome of a security-test execution.

The result is created by comparing the expected status defined by the
security test with the actual status returned by the target.

Conceptually:

```text
Expected Status
       |
       +
       |
Actual Status
       |
       v
Comparison
       |
       v
TestResult
```

The `TestResult` therefore forms the boundary between test execution and
evidence generation.

The ECU simulator does not determine the final test result.

It only returns the response representing the behavior of the system under
test.

For the TC-003 vulnerable-state demonstration, the expected security behavior
remains `ACCESS_DENIED`, while the controlled vulnerable simulator returns
`ACCESS_GRANTED`. The resulting `TestResult` is therefore a failed security
test result.

For Phase 9, the automated pytest suite asserts the resulting `TestResult`
against the established expected security behavior. A pytest PASS therefore
means that the regression assertion itself succeeded; it does not change the
semantics of the underlying `TestResult`.

Phase 10 preserves this distinction. A failed pytest assertion causes the
GitHub Actions job to fail, while the CI workflow itself does not redefine
the security-test result semantics.

---

## Evidence Framework

The Evidence Framework records the result of a completed security-test
execution in a structured format.

The current Evidence model contains:

* `test_id`
* `timestamp`
* `target`
* `preconditions`
* `input`
* `expected`
* `actual`
* `result`
* `notes`

The Evidence Framework operates after test execution:

```text
Security Test
       |
       v
Test Result
       |
       v
Evidence
```

The Evidence Framework does not implement security behavior.

It does not change the ECU response, modify the expected result, or determine
the security policy of the system under test.

Evidence represents the observation produced by a test execution.

For TC-003, regression evidence is generated from the executed regression
retest result. The Evidence Framework itself does not determine whether a
security regression exists.

Phase 9 reuses the existing Evidence Framework for regression-evidence
verification. The dedicated regression suite contains a scenario that
generates evidence from the secure retest result and validates the generated
evidence.

Phase 10 reuses the same Evidence Framework for CI evidence generation. The
CI/CD evidence path is:

```text
Security Regression Tests
       |
       v
EvidenceGenerator
       |
       v
Evidence
       |
       v
Evidence.to_json()
       |
       v
CI Evidence JSON Files
       |
       v
GitHub Actions Artifact
```

The CI workflow does not introduce a second evidence model or a second
evidence-generation implementation. The generated JSON files are serialized
instances of the existing `Evidence` model.

The CI artifact provides the generated evidence as a workflow output. It does
not constitute a separate finding-management or historical evidence system.

---

## Evidence Result Semantics

The Evidence Framework currently supports two result values:

```text
PASS
FAIL
```

The semantics are:

```text
PASS
Expected == Actual
```

and:

```text
FAIL
Expected != Actual
```

For example, if the security requirement requires:

```text
Expected = ACCESS_DENIED
```

but the controlled vulnerable ECU returns:

```text
Actual = ACCESS_GRANTED
```

the resulting evidence represents:

```text
FAIL
```

The `FAIL` indicates that the observed behavior did not match the expected
security behavior.

It does not automatically constitute a formal security vulnerability
finding.

Phase 8 introduces structured example finding documentation based on existing
test and evidence results.

The finding examples document security requirement, observed behavior,
security impact, exploitability, root cause where supported, recommendation,
fix, retest, and regression relationship.

Generalized finding management, automated finding ingestion, historical
finding tracking, and generalized remediation management remain outside the
current architecture.

Phase 9 verifies that regression evidence produced from a secure retest
contains the expected test identifier, target, preconditions, expected
behavior, actual behavior, and PASS result.

Phase 10 does not change these evidence semantics. CI execution evaluates the
same regression assertions, and CI evidence is generated using the existing
Evidence Framework.

---

## Complete Test Execution Flow

The current execution flow is:

```text
SecurityTestCase
       |
       | request
       v
SecurityTestRunner
       |
       | handle_request()
       v
ECUTarget
       |
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

The execution path separates target behavior from test evaluation and evidence
generation.

This means that the ECU simulator remains unaware of the Evidence Framework.

Phase 9 adds automated pytest assertions around this execution path. It does
not change the underlying request, response, result, or evidence flow.

Phase 10 invokes this established execution path from GitHub Actions:

```text
GitHub Event
       |
       v
GitHub Actions
       |
       v
pytest
       |
       v
04_tests/test_security_regression.py
       |
       v
Existing Test Execution Flow
       |
       v
EvidenceGenerator
       |
       v
Evidence.to_json()
       |
       v
CI Evidence JSON Files
       |
       v
GitHub Actions Artifact
```

The CI/CD layer therefore surrounds the existing execution flow instead of
creating a parallel security-test implementation.

---

## TC-001 in the Current Architecture

Phase 5 introduces:

```text
TC-001 — Diagnostic Authorization
```

TC-001 verifies the security requirement:

```text
Protected diagnostic operations shall require authorization.
```

The protected operation is:

```text
PROTECTED_OPERATION
```

The secure behavior is:

```text
authorization = false
PROTECTED_OPERATION
       |
       v
ACCESS_DENIED
```

and:

```text
authorization = true
PROTECTED_OPERATION
       |
       v
ACCESS_GRANTED
```

The controlled vulnerable behavior is:

```text
authorization = false
PROTECTED_OPERATION
       |
       v
ACCESS_GRANTED
```

The security test evaluates these responses through the existing test
architecture.

The test does not access the internal authorization implementation of the
simulated ECU.

TC-001 therefore provides the security property that is reused by the
Phase-7 regression workflow.

---

## TC-002 in the Current Architecture

Phase 6 introduces:

```text
TC-002 — Message Validation
```

TC-002 extends the existing security-test architecture without introducing a
new communication layer.

The test uses the same architectural path:

```text
TC-002
   |
   v
SecurityTestCase
   |
   v
SecurityTestRunner
   |
   v
ECUTarget
   |
   v
ECUAdapter
   |
   v
ECUSimulator
   |
   v
ECUResponse
   |
   v
TestResult
   |
   v
Evidence
```

TC-002 verifies message/request validation behavior through the existing
target abstraction.

The security test does not access internal ECU implementation details.

The expected behavior remains defined by the security-test specification
and is evaluated independently from the concrete ECU implementation.

TC-002 therefore reuses the architectural separation established in
Phases 3, 4, and 5.

No new communication layer is introduced by TC-002.

---

## TC-003 in the Current Architecture

Phase 7 introduces:

```text
TC-003 — Regression Workflow
```

TC-003 extends the existing architecture by demonstrating a controlled
regression lifecycle for the diagnostic authorization security property
established by TC-001.

TC-003 does not introduce a new security-test definition, target abstraction,
communication layer, or regression execution engine.

The workflow reuses the existing TC-001 `SecurityTestCase`:

```text
TC-003
   |
   v
Existing TC-001 SecurityTestCase
   |
   v
SecurityTestRunner
   |
   v
ECUTarget
   |
   v
ECUAdapter
   |
   v
ECUSimulator
   |
   v
ECUResponse
   |
   v
TestResult
   |
   v
EvidenceGenerator
   |
   v
Regression Evidence
```

The regression lifecycle consists of two controlled target states.

First, the vulnerable behavior reproduces the original modeled deviation:

```text
VULNERABLE
authorization = false
PROTECTED_OPERATION
       |
       v
ACCESS_GRANTED
```

The original security expectation remains:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_GRANTED
Result   = FAIL
```

The failed security result demonstrates that the original security condition
is correctly detected.

Second, the same unauthorized condition is executed against the secure
simulator:

```text
SECURE
authorization = false
PROTECTED_OPERATION
       |
       v
ACCESS_DENIED
```

The regression retest therefore produces:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_DENIED
Result   = PASS
```

The resulting `TestResult` is used to generate and validate regression
evidence.

The authorized behavior is also verified to ensure that the secure behavior
does not remove the intended authorized operation:

```text
authorization = true
PROTECTED_OPERATION
       |
       v
ACCESS_GRANTED
```

TC-003 therefore verifies both the restored security property and the
preservation of the authorized behavior.

Phase 9 is distinct from this Phase-7 workflow. Phase 7 demonstrates the
controlled regression lifecycle, including vulnerable-state reproduction.
Phase 9 provides an automated pytest regression suite for established
security properties and does not reproduce vulnerable behavior in the
dedicated regression test file.

---

## Phase-9 Automated Security Regression Suite

Phase 9 introduces automated pytest verification for established security
properties.

The dedicated regression suite is implemented in:

```text
04_tests/test_security_regression.py
```

The suite reuses the existing security-test execution architecture:

```text
Phase-9 Regression Test
        |
        v
SecurityTestCase
        |
        v
SecurityTestRunner
        |
        v
ECUAdapter
        |
        v
Fresh Secure ECUSimulator
        |
        v
TestResult
        |
        v
EvidenceGenerator
```

Each regression scenario creates a fresh `ECUSimulator` in secure mode and
explicitly configures the required authorization state and, where required,
the ECU state.

The dedicated suite verifies the following established behaviors:

```text
1. Unauthorized protected operation
   Expected = ACCESS_DENIED

2. Authorized protected operation
   Expected = ACCESS_GRANTED

3. Invalid message
   Expected = INVALID_REQUEST

4. Unsupported operation
   Expected = UNSUPPORTED_OPERATION

5. Boundary input outside the accepted parameter range
   Expected = REQUEST_REJECTED

6. Protected operation in blocked ECU state
   Expected = REQUEST_REJECTED

7. Regression evidence for the secure unauthorized retest
   Expected = ACCESS_DENIED
   Actual   = ACCESS_DENIED
   Evidence Result = PASS
```

The boundary-input regression scenario uses an out-of-range parameter value of
`256` and verifies that validation cannot be bypassed.

The blocked-state regression scenario verifies that an authorized request does
not enable protected behavior when the ECU is in the blocked state.

The evidence regression scenario generates evidence from the executed secure
retest and validates the resulting evidence object.

Phase 9 does not introduce:

```text
A new target implementation
A new adapter
A new test runner
A new response model
A new evidence model
A generalized regression engine
Historical result comparison
Automatic finding management
CI/CD integration
```

The Phase-9 suite is therefore an automated verification layer over the
existing architecture rather than a new runtime architecture.

Phase 10 adds CI/CD execution around this existing suite without moving the
security regression logic into the workflow file.

---

## Phase-10 CI/CD Regression Architecture

Phase 10 introduces a minimal GitHub Actions workflow for automated execution
of the established security regression suite.

The workflow is implemented in:

```text
.github/workflows/security-regression.yml
```

The configured event triggers are:

```text
push
pull_request
```

The workflow execution path is:

```text
GitHub Event
       |
       v
Checkout Repository
       |
       v
Set up Python 3.12
       |
       v
Install Project Dependencies
       |
       v
Run Security Regression Tests
       |
       v
Generate CI Evidence
       |
       v
Upload CI Evidence
```

The security regression test execution is:

```text
GitHub Actions
       |
       v
pytest -v 04_tests/test_security_regression.py
       |
       v
04_tests/test_security_regression.py
       |
       v
Existing SecurityTestCase / SecurityTestRunner /
ECUAdapter / ECUSimulator / TestResult Path
```

The CI evidence path is:

```text
Security Regression Execution
       |
       v
EvidenceGenerator
       |
       v
Evidence
       |
       v
Evidence.to_json()
       |
       v
ci-evidence/*.json
       |
       v
security-regression-evidence
```

The workflow uses Python 3.12, matching the current project environment and
the `requires-python = ">=3.12"` project requirement.

The workflow installs the project's current development test dependency:

```text
pytest>=9,<10
```

The CI workflow does not contain separate security assertions for the
individual security scenarios. The security regression assertions remain in
`04_tests/test_security_regression.py`.

This establishes the CI Single Source of Truth:

```text
04_tests/test_security_regression.py
             |
             v
Security Regression Logic
             |
             +--------------------+
             |                    |
             v                    v
        Local pytest        GitHub Actions
                                  |
                                  v
                             pytest
```

Local execution and CI execution therefore use the same regression test
module rather than maintaining two independent security-test implementations.

The CI evidence generation also reuses the existing regression execution path
and `EvidenceGenerator`. It does not introduce a second security-test runner,
second Evidence model, or alternative evidence semantics.

The workflow is intentionally limited to:

```text
Test execution
Evidence generation
Evidence artifact upload
```

It does not implement:

```text
Deployment
Production integration
Vehicle communication
External security systems
Finding management
Historical regression comparison
Automatic remediation
Generalized regression orchestration
```

---

## Phase-8 Security Finding Documentation

Phase 8 introduces structured example findings based on the security-test and
evidence results already established by TC-001 and TC-002.

The finding documentation does not introduce a new execution layer.

The relationship is:

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
Evidence
       |
       v
Example Finding
       |
       v
Root Cause / Recommendation / Fix / Retest
       |
       v
Regression Relationship
```

For SEC-001, the finding documents the controlled vulnerable authorization
behavior reproduced by TC-001:

```text
TC-001
Expected = ACCESS_DENIED
Actual   = ACCESS_GRANTED
Result   = FAIL
       |
       v
SEC-001
Unauthorized access to protected diagnostic operation
```

The root cause is traced to the deliberate vulnerable branch in the simulated
ECU implementation.

For SEC-002, the finding documentation records that the TC-002 validation
scenarios did not reproduce a security-relevant deviation:

```text
TC-002
Expected == Actual
       |
       v
No security-relevant deviation reproduced
       |
       v
SEC-002 example documentation
```

SEC-002 therefore does not represent a demonstrated vulnerability.

Phase 8 does not introduce a finding-management engine, database, automated
finding ingestion, or generalized vulnerability lifecycle.

The finding files are structured documentation artifacts that consume the
results of the existing test and evidence workflow.

---

## Security Test Result vs. Test Framework Result

The TC-003 lifecycle demonstration distinguishes between the security test
result and the pytest test result.

For the controlled vulnerable behavior:

```text
SecurityTestCase expected: ACCESS_DENIED
ECUSimulator actual:       ACCESS_GRANTED
TestResult.passed:         False
```

The pytest test passes because it asserts that this deviation is correctly
detected.

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
TestResult.passed:          True
pytest test:               PASS
```

This distinction is required for a correct interpretation of the Phase-7
test lifecycle.

Phase 9 applies the same distinction. A pytest PASS means that the automated
regression assertion succeeded. For secure regression scenarios, this
normally corresponds to a `TestResult` with `passed = True`, while the
pytest framework result remains a separate verification-layer result.

Phase 10 preserves this distinction in CI. A GitHub Actions job PASS means
that the configured pytest execution completed successfully. It does not
create a new security-result semantic distinct from the established
`TestResult` and Evidence semantics.

A pytest failure causes the CI job to fail because the workflow does not
continue past a failed security regression test as a successful pipeline
result.

---

## Request and Response Flow

A request moves through the target boundary before reaching the simulated
ECU.

```text
SecurityTestCase
       |
       | request
       v
SecurityTestRunner
       |
       v
ECUTarget
       |
       v
ECUAdapter
       |
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
       | compare expected / actual
       v
TestResult
```

The Test Runner therefore interacts with the target through the defined
interface instead of directly calling ECU implementation details.

---

## Invalid Requests

The simulated ECU validates incoming requests.

The current request validation distinguishes between malformed requests,
unsupported operations, and valid operations that violate request or state
constraints.

A malformed or missing operation results in:

```text
Invalid or Missing Operation
       |
       v
INVALID_REQUEST
```

An unsupported operation results in:

```text
Unknown Operation
       |
       v
UNSUPPORTED_OPERATION
```

A valid request that violates parameter or ECU-state constraints results in:

```text
Invalid Parameter or ECU State
       |
       v
REQUEST_REJECTED
```

Invalid request handling is part of the ECU simulator.

The Test Runner does not implement request validation. It evaluates the
response returned by the target.

This keeps target behavior and test evaluation separate.

Phase 9 verifies these existing validation behaviors through automated
regression scenarios without moving validation logic into the test suite.

---

## Determinism

Deterministic behavior is a core requirement of the current architecture.

For the same:

* security mode
* authorization state
* request

the simulator produces the same response.

This allows security tests to be repeated under equivalent conditions and
makes test results reproducible.

The current architecture does not depend on:

* physical hardware
* vehicle networks
* external services
* network access
* random test data

The Evidence Framework generates a runtime timestamp. The timestamp is
therefore expected to differ between executions.

The remaining evidence fields are derived from the test execution and target
state.

The Phase-7 regression workflow remains deterministic because the vulnerable
and secure target states are explicitly configured and the same defined
security condition is evaluated through the existing execution architecture.

Phase 9 preserves this determinism by creating a fresh secure ECU simulator
for each regression scenario and explicitly configuring the required
authorization and ECU state.

Phase 10 preserves the same deterministic test behavior because GitHub Actions
executes the established regression suite with the same defined test inputs
and simulated target behavior.

The generated evidence timestamp remains runtime-dependent and is expected to
differ between executions.

---

## Architectural Separation

The central architectural separation is:

```text
Security Test Definition
          |
          v
    Test Execution
          |
          v
    Target Boundary
          |
          v
    System Under Test
          |
          v
      Test Result
          |
          v
       Evidence
```

The security test does not depend on internal simulator attributes.

For example, the test infrastructure does not directly manipulate internal
state such as:

```text
_internal_state
_authorized
_security_policy
```

Communication with the target occurs through the defined target interface.

The Evidence Framework also does not access internal ECU state.

This separation provides clear boundaries between:

* what is being tested
* how the test is executed
* how the target behaves
* how the result is evaluated
* how the observation is recorded

The TC-003 regression workflow follows the same separation. Regression
evaluation operates on the executed test result and does not require direct
access to internal ECU implementation details.

Phase 8 follows the same boundary. Example finding documentation consumes
existing test and evidence results but does not modify target behavior, test
execution, or evidence generation.

Phase 9 also follows the same boundary. The automated regression tests
configure the target through its defined public behavior and evaluate the
returned results through the existing test architecture.

Phase 10 extends the workflow boundary without changing these responsibilities.
GitHub Actions provides the external execution mechanism, while the existing
Python test and evidence architecture remains responsible for security-test
execution, result evaluation, and evidence generation.

---

## Simulation Boundary

The current implementation is completely local and simulated.

It does not provide:

* real CAN communication
* real UDS communication
* physical ECU access
* vehicle-network communication
* production-system testing
* OEM-system integration

The `ECUTarget` abstraction provides a software boundary for target
interaction, but no real-world communication adapter is currently implemented.

The project therefore demonstrates the testing architecture and workflow
without introducing external automotive communication.

Phase 10 does not change this simulation boundary. GitHub Actions executes the
same simulated Python environment and does not provide a connection to a real
vehicle, ECU, CAN network, UDS endpoint, OEM system, or production system.

---

## Future Target Extension

The target abstraction provides an extension point for future compatible test
targets.

Conceptually:

```text
                       +------------------+
                       |                  |
                       v                  v
                ECUSimulator       Future Target
                       |                  |
                       +--------+---------+
                                |
                                v
                            ECUTarget
                                ^
                                |
                         SecurityTestRunner
                                |
                                v
                         Evidence Framework
```

This diagram represents an architectural possibility, not a current
implementation.

The repository currently uses the simulated ECU only.

No real ECU adapter, CAN adapter, or UDS adapter is implemented.

Any future target would need to satisfy the defined target interaction
contract without requiring changes to the fundamental security-test execution
model.

---

## Phase Boundaries

Phase 6 includes TC-002 Message Validation in addition to the previously verified TC-001 Diagnostic Authorization test.

Phase 7 adds the TC-003 Regression Workflow verification.

The Phase-7 implementation is limited to the diagnostic authorization
security property represented by TC-001.

It provides:

```text
Controlled vulnerable-state reproduction
        |
        v
Secure retest
        |
        v
Expected-versus-actual evaluation
        |
        v
Regression evidence generation
        |
        v
Evidence validation
        |
        v
Authorized-behavior verification
```

Phase 8 adds finding documentation as a documentation layer on top of the
existing test and evidence architecture.

The Phase-8 finding layer does not change the target, test-runner, adapter, or
evidence architecture.

Phase 9 adds automated pytest verification of established security properties
on top of the existing test and evidence architecture.

The Phase-9 implementation is limited to deterministic local regression
verification. It does not implement a generalized regression-management
platform.

Phase 10 adds the minimal GitHub Actions CI/CD execution layer for the
established security regression suite.

The Phase-10 implementation provides:

```text
Configured push trigger
        |
        v
Configured pull_request trigger
        |
        v
Repository checkout
        |
        v
Python 3.12 setup
        |
        v
Project test dependency installation
        |
        v
Security regression pytest execution
        |
        v
CI evidence generation
        |
        v
Evidence artifact upload
```

The Phase-10 implementation does not provide:

```text
Generalized regression orchestration
Historical result comparison
Automatic finding management
Automatic regression-test generation
Production deployment
Vehicle communication
OEM-system integration
```

The pull-request trigger is configured in the workflow. The documented
verification of the current Phase-10 implementation includes a successful
push-triggered workflow and a controlled failure workflow. A separate
pull-request execution is not represented as an already executed verification
result.

---

## Phase History

### Phase 1 — Repository Foundation

Phase 1 established the project and development foundation.

It introduced:

* Python project configuration
* pytest-based verification
* repository structure
* documentation structure
* project scope
* initial architectural decisions
* deterministic local development environment

### Phase 2 — ECU Simulation

Phase 2 implemented the deterministic simulated ECU.

It introduced:

* secure mode
* vulnerable mode
* authorization state
* protected operation handling
* request validation
* deterministic response statuses
* structured ECU responses

### Phase 3 — Security Test Architecture

Phase 3 separated security-test execution from the simulated ECU.

It introduced:

* `SecurityTestCase`
* `SecurityTestRunner`
* `TestResult`
* `ECUTarget`
* `ECUAdapter`

The resulting architecture established the target boundary used by later
security tests.

### Phase 4 — Evidence Framework

Phase 4 introduced structured evidence generation.

It added:

* the Evidence model
* mandatory evidence fields
* evidence validation
* `PASS` / `FAIL` semantics
* runtime timestamps
* JSON serialization
* evidence generation from `TestResult`

The Evidence Framework was deliberately kept separate from the ECU and Test
Runner.

### Phase 5 — TC-001 Diagnostic Authorization

Phase 5 introduced the first dedicated security test case:

```text
TC-001 — Diagnostic Authorization
```

TC-001 reuses the existing Phase-3 test architecture and Phase-4 Evidence
Framework.

No new communication layer was required.

The test evaluates the authorization behavior of the simulated ECU and
provides the security property used by the subsequent regression workflow.

### Phase 6 — TC-002 Message Validation

Phase 6 introduced the second dedicated security test case:

```text
TC-002 — Message Validation
```

TC-002 reuses the existing security-test architecture and Evidence Framework.

The test validates message/request handling through the existing target
abstraction and does not introduce real automotive communication.

Phase 6 therefore extends the security-test coverage without changing the
fundamental architectural boundaries established in earlier phases.

### Phase 7 — TC-003 Regression Workflow

Phase 7 introduces the controlled regression workflow:

```text
TC-003 — Regression Workflow
```

TC-003 reuses the existing TC-001 security-test definition and verifies the
regression lifecycle for the diagnostic authorization security property.

The workflow includes:

* controlled reproduction of the original vulnerable behavior
* preservation of the original security expectation
* secure retest of the same unauthorized condition
* expected-versus-actual evaluation through `SecurityTestRunner`
* generation of regression evidence from the executed result
* validation of the generated evidence
* verification that authorized behavior remains available

Phase 7 therefore extends the existing test and evidence architecture without
introducing a separate communication or target layer.

The implementation is a controlled local regression workflow. Generalized
finding management, historical regression comparison, regression orchestration,
and CI/CD remain outside the current architecture.

### Phase 8 — Example Findings

Phase 8 introduces structured security finding documentation based on the
existing TC-001, TC-002, and TC-003 test and evidence workflow.

It introduces:

* SEC-001 example finding documentation for the controlled TC-001
  authorization deviation
* SEC-002 example finding documentation for the TC-002 validation assessment
  where no security-relevant deviation was reproduced
* structured security impact documentation
* qualitative exploitability assessment
* root-cause documentation where supported by implementation evidence
* recommendation and fix documentation
* retest documentation
* regression-test relationship documentation

Phase 8 does not introduce a generalized finding-management or vulnerability
tracking system.

The finding documents remain controlled portfolio documentation artifacts
derived from the existing security-test and evidence workflow.

### Phase 9 — Automated Security Regression Suite

Phase 9 introduces the dedicated pytest security regression suite:

```text
04_tests/test_security_regression.py
```

The suite verifies established security properties using the existing
`SecurityTestCase`, `SecurityTestRunner`, `ECUAdapter`, `ECUSimulator`,
`TestResult`, and Evidence Framework components.

The automated regression suite verifies:

* unauthorized protected operation is denied
* authorized protected operation remains allowed
* invalid messages are rejected
* unsupported operations are rejected
* out-of-range boundary input does not bypass validation
* blocked ECU state does not enable protected behavior
* regression evidence correctly represents the secure retest

Each regression scenario uses a fresh secure ECU simulator with explicitly
configured authorization and ECU state.

Phase 9 does not introduce a new execution architecture, target abstraction,
communication layer, generalized regression engine, historical comparison
mechanism, finding-management system, or CI/CD integration.

The vulnerable-state reproduction remains part of the Phase-7 TC-003 workflow.
Phase 9 focuses on automated verification of the established secure behavior.

### Phase 10 — CI/CD Security Regression Pipeline

Phase 10 introduces the minimal GitHub Actions CI/CD pipeline for the
established security regression suite.

The workflow is implemented in:

```text
.github/workflows/security-regression.yml
```

The configured execution path is:

```text
GitHub Event
       |
       v
Checkout Repository
       |
       v
Python 3.12
       |
       v
Install Dependencies
       |
       v
pytest Security Regression Suite
       |
       v
Generate Evidence
       |
       v
Upload Evidence Artifact
```

The Phase-10 CI/CD layer reuses the existing Phase-9 regression suite and
evidence architecture.

The Single Source of Truth remains:

```text
04_tests/test_security_regression.py
```

GitHub Actions executes this existing regression logic and does not implement
a second security-test implementation.

The CI evidence path reuses the existing `EvidenceGenerator` and
`Evidence.to_json()` serialization:

```text
Security Regression Tests
       |
       v
EvidenceGenerator
       |
       v
Evidence
       |
       v
Evidence.to_json()
       |
       v
CI Evidence JSON Files
       |
       v
GitHub Actions Artifact
```

The workflow is configured for both `push` and `pull_request` events.

The implemented CI/CD layer is intentionally limited to automated security
regression execution and evidence artifact collection. It does not implement
deployment, production integration, generalized finding management, historical
comparison, or generalized regression orchestration.

The current Phase-10 verification includes:

* successful push-triggered GitHub Actions execution
* successful execution of the seven security regression tests in CI
* generated CI evidence
* uploaded `security-regression-evidence` artifact
* controlled CI failure behavior
* evidence artifact availability after the controlled failure
* restoration of the secure regression expectation
* successful local re-execution after restoration

A separate pull-request workflow execution has not been documented as an
executed verification result.

---

## Verification

The current repository has been locally verified with:

```text
pytest -v
```

Result:

```text
41 passed in 0.16s
```

The dedicated Phase-9 security regression suite has also been verified with:

```text
pytest .\04_tests\test_security_regression.py -v
```

Result:

```text
7 passed in 0.06s
```

The verified full-suite test distribution is:

```text
ECU Simulation Tests:               6
Evidence Framework Tests:         14
Foundation Tests:                  1
Security Regression Tests:         7
TC-001 Diagnostic Authorization:   4
TC-002 Message Validation:        5
Test Runner Tests:                 4
-------------------------------------
Total:                            41
```

The Phase-9 regression tests reuse the existing test architecture and do not
introduce a second target or execution abstraction.

The dedicated Phase-9 suite currently contains seven regression scenarios and
all seven pass locally.

Phase 10 also verifies the local CI execution sequence:

```text
pytest -v 04_tests/test_security_regression.py
       |
       v
generate_regression_evidence(...)
       |
       v
6 CI evidence JSON files
```

The CI evidence generation produced six JSON files for the established
regression scenarios.

The generated evidence uses the existing `Evidence` model and its JSON
serialization path. The evidence records contain the established fields
including `test_id`, `timestamp`, `target`, `preconditions`, `input`,
`expected`, `actual`, `result`, and `notes`.

The GitHub Actions workflow has been successfully executed through a
push-triggered run on `main`.

The successful CI run produced:

```text
Workflow: Security Regression
Trigger: push
Commit: 78c943f
Status: Success
Artifact: security-regression-evidence
```

The artifact was successfully uploaded by the workflow.

A controlled failure test was also executed on a temporary branch. The
regression expectation was deliberately changed so that the first security
regression assertion failed while the remaining six tests passed locally:

```text
F......
1 failed, 6 passed
```

The corresponding GitHub Actions workflow run failed with exit code `1`, as
expected.

The CI evidence artifact was still produced and uploaded during the failed
workflow because evidence generation and artifact upload use `if: always()`.

The controlled failure state was subsequently restored. The restored
regression suite was executed locally again with:

```text
7 passed
```

The temporary failure branch remains intentionally retained as portfolio
evidence of the controlled CI failure path.

The successful CI run and the controlled failure run verify the implemented
push-triggered CI behavior, failure propagation, and evidence artifact
handling.

The workflow also contains a `pull_request` trigger. Configuration of this
trigger is part of the implemented workflow, but a separate pull-request
execution is not claimed here as an executed verification result.

The GitHub Actions runner reported a Node.js 20 deprecation warning for the
currently used GitHub Actions components. This warning did not prevent the
workflow from completing successfully and is not part of the security-test
result.

---

## Current Architectural Scope

The current implementation provides:

* deterministic ECU simulation
* secure and vulnerable security modes
* authorization handling
* protected operation handling
* request validation
* target abstraction
* security-test execution
* expected-versus-actual evaluation
* structured test results
* structured evidence
* evidence validation
* JSON serialization
* TC-001 Diagnostic Authorization
* TC-002 Message Validation
* TC-003 Regression Workflow
* controlled regression evidence generation
* authorized-behavior verification during the TC-003 regression workflow
* SEC-001 example finding documentation
* SEC-002 example finding documentation
* finding documentation linked to existing test and evidence results
* automated pytest security regression verification
* seven verified Phase-9 regression scenarios
* regression-evidence verification for the secure retest
* minimal GitHub Actions CI/CD execution of the security regression suite
* push-triggered CI execution
* configured pull-request CI triggering
* CI evidence generation
* CI evidence JSON serialization
* GitHub Actions evidence artifact upload
* verified CI failure propagation for a controlled regression assertion failure

The following capabilities are outside the current implementation:

* real CAN communication
* real UDS communication
* physical ECU communication
* vehicle-network communication
* production-system testing
* OEM-system integration
* generalized security-finding management
* automated finding ingestion
* historical finding tracking
* CVSS calculation
* historical regression comparison
* generalized regression orchestration
* automatic regression-test generation
* deployment automation
* production CI/CD integration
* automatic remediation

These capabilities are reserved for later project phases.

---

## Architectural Principles

The current architecture follows several principles.

### 1. Separate the Test from the System Under Test

The security test must not depend directly on the internal implementation of
the ECU simulator.

The target abstraction provides the boundary between test execution and the
system under test.

### 2. Keep Security Behavior in the Target

The simulated ECU is responsible for its security behavior.

The Test Runner must evaluate that behavior rather than implement or replace
it.

### 3. Separate Execution from Evidence

The Test Runner produces a `TestResult`.

The Evidence Framework consumes the completed result and records the
observation.

Evidence generation therefore does not control test execution.

### 4. Keep Expected Security Behavior Independent from the Implementation

The expected result is derived from the security requirement represented by
the test case.

The expected result must not be changed simply to make an insecure
implementation pass.

This principle is also preserved by TC-003. The original TC-001 expectation
remains `ACCESS_DENIED` throughout the vulnerable-state reproduction and the
secure regression retest.

Phase 9 preserves the same principle by defining expected statuses in the
regression test cases independently from the concrete simulator behavior.

Phase 10 preserves the same principle by invoking the existing regression
suite without redefining its expected security behavior inside the CI
workflow.

### 5. Keep the Simulation Deterministic

Equivalent input and target state must produce equivalent target behavior.

This is required for reproducible local security testing.

Phase 9 maintains this property by using deterministic inputs and fresh,
explicitly configured secure simulator instances for individual regression
scenarios.

Phase 10 executes the same deterministic regression scenarios in the
controlled GitHub Actions environment.

### 6. Reuse Existing Architectural Boundaries for Regression Testing

The Phase-7 regression workflow reuses the existing security-test and target
architecture.

It does not introduce a separate communication path, target abstraction, or
test-result mechanism solely for regression testing.

The regression workflow operates on the existing test definition, target
behavior, `TestResult`, and Evidence Framework.

Phase 9 follows the same principle. The automated regression suite reuses the
existing test-case, runner, target, simulator, result, and evidence
components instead of introducing parallel implementations.

Phase 10 extends this principle to CI/CD. GitHub Actions invokes the
established regression suite and existing evidence-generation path rather than
implementing separate CI-specific security-test logic or evidence semantics.

### 7. Add Future Workflow Stages Only When Their Prerequisites Exist

The project is developed incrementally:

```text
ECU Simulation
       |
       v
Security Test Architecture
       |
       v
Evidence Framework
       |
       v
TC-001
       |
       v
TC-002
       |
       v
TC-003 Regression Workflow
       |
       v
Phase-8 Example Findings
       |
       v
Phase-9 Automated Security Regression Suite
       |
       v
Phase-10 CI/CD Security Regression Pipeline
       |
       v
Future Generalized Regression
```

Later workflow stages are not implemented inside earlier architectural layers
just to anticipate future functionality.

---

## Architecture and Project Scope

The architecture is intentionally smaller than a real automotive cybersecurity
test environment.

The purpose of the project is to demonstrate how a security requirement can be
translated into a reproducible security test, how the resulting execution can
be evaluated and recorded as structured evidence, how a defined security
property can be retested through a controlled regression workflow, how
established security properties can be protected by automated regression
tests, and how this regression suite can be executed automatically in a
minimal CI/CD pipeline with machine-readable evidence artifacts.

The project does not attempt to reproduce a complete automotive
communication stack, production ECU, or real vehicle environment.

The current architecture therefore provides the minimum separation required
for the demonstrated workflow while keeping the implementation deterministic,
local, and understandable.

The long-term architecture can build additional security workflow stages on
top of these stable boundaries without changing the basic responsibilities
of the existing components.

The current Phase-7 regression implementation is intentionally limited to the
diagnostic authorization security property established by TC-001. It does
not constitute a generalized security finding or regression management
platform.

Phase 8 adds structured example finding documentation as a documentation layer
on top of the existing test and evidence workflow. The Phase-8 findings are
controlled documentation artifacts and do not constitute a generalized
security finding management or vulnerability tracking platform.

Phase 9 adds automated pytest verification for the established security
properties represented by the current security-test architecture. It is a
deterministic local regression suite and does not constitute a generalized
regression management platform, historical comparison system, or CI/CD
implementation.

Phase 10 adds a minimal GitHub Actions CI/CD execution layer around the
Phase-9 regression suite. It provides automated security regression execution
and evidence artifact collection, but does not constitute a generalized
regression management platform, historical comparison system, deployment
pipeline, or production integration.