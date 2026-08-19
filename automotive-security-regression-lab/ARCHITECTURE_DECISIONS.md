# Architecture Decisions

This document records the initial architecture decisions for the Automotive Security Regression Lab.

## ADR-001 — The ECU is fully simulated

**Status:** Accepted  
**Phase:** 1  
**Source:** [MASTER]

The project uses a simulated ECU rather than a real vehicle ECU or productive automotive system.

**Rationale:** The project is explicitly defined as a controlled, fully simulated automotive security-testing laboratory. This keeps the environment reproducible and avoids interaction with real vehicles or productive systems.

## ADR-002 — Security tests are intended to be reproducible and automatable

**Status:** Accepted  
**Phase:** 1  
**Source:** [MASTER]

The later security-testing workflow is designed around repeatable automated execution and evidence-oriented verification.

**Rationale:** Reproducibility and automation are explicit project objectives and are required for the later regression-testing workflow.

## ADR-003 — No interaction with real vehicles or productive systems

**Status:** Accepted  
**Phase:** 1  
**Source:** [MASTER]

The project does not interact with real vehicles, ECUs, OEM systems, customer data, or productive systems.

**Rationale:** This is an explicit project scope constraint.

## ADR-004 — Test logic is separated from the ECU implementation

**Status:** Accepted  
**Phase:** 1  
**Source:** [MASTER]

The planned architecture separates the security test case and test runner from the simulated ECU through an ECU adapter boundary.

**Rationale:** The separation is part of the target architecture and supports the later distinction between test logic and ECU behavior.

## ADR-005 — Phase 1 uses a minimal Python/pytest foundation

**Status:** Accepted  
**Phase:** 1  
**Source:** [MASTER] + [SOURCE]

Phase 1 defines Python project metadata and pytest configuration without adding security-specific runtime dependencies.

**Rationale:** The masterprompt requires Python and pytest as the primary test stack and explicitly calls for a simple configuration with no unnecessary dependencies. pytest officially supports project configuration in `pyproject.toml`.

## ADR-006 — ECU security behavior is deterministic and mode-controlled

**Status:** Accepted  
**Phase:** 2  
**Source:** [MASTER]

The simulated ECU provides two explicit security modes: `secure` and `vulnerable`.

In `secure` mode, the protected operation requires explicit authorization. In `vulnerable` mode, the protected operation is intentionally granted without authorization.

**Rationale:** The project requires a deterministic security target that can represent both the intended secure behavior and a controlled vulnerable behavior for reproducible security testing. Explicit modes make the security behavior predictable and suitable for automated regression testing.

## ADR-007 — ECU responses use a structured deterministic response model

**Status:** Accepted  
**Phase:** 2  
**Source:** [MASTER]

The simulated ECU returns a structured `ECUResponse` containing a deterministic response status and the corresponding operation.

The response can be converted into a simple dictionary representation using `to_dict()`.

**Rationale:** A structured response model provides a stable interface between the simulated ECU and the later test, evidence, and regression layers. Deterministic response values make test results reproducible and easy to compare.

## ADR-008 — Requests are validated before security processing

**Status:** Accepted  
**Phase:** 2  
**Source:** [MASTER]

The simulated ECU validates the request structure before applying the security policy.

Requests must provide a valid operation string. Only the defined `PROTECTED_OPERATION` is accepted. If optional `parameters` are provided, they must be represented as a mapping.

Invalid request structures and unknown operations result in a deterministic `INVALID_REQUEST` response.

**Rationale:** Request validation provides a clear boundary between malformed input and security-policy decisions. This keeps the simulator deterministic and prevents invalid requests from being interpreted as valid protected operations.

## Change policy

Architecture changes must be documented in this file before they are treated as accepted project decisions. Later phases may add decisions, but they must not silently contradict the decisions above.
