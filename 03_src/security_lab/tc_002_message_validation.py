"""TC-002 — Message Validation security tests."""

from __future__ import annotations

from typing import Any

from security_lab.ecu_adapter import ECUAdapter
from security_lab.ecu_simulator import (
    ECUState,
    ECUSimulator,
    ResponseStatus,
    SecurityMode,
)
from security_lab.evidence import Evidence, EvidenceGenerator
from security_lab.test_runner import (
    SecurityTestCase,
    SecurityTestRunner,
)

TEST_ID_PREFIX = "TC-002"
TARGET = "simulated-ecu"
PROTECTED_OPERATION = "PROTECTED_OPERATION"


def _run_test(
    test_id: str,
    request: Any,
    expected_status: ResponseStatus,
    *,
    preconditions: dict[str, Any] | None = None,
    notes: str = "",
) -> tuple[SecurityTestCase, Any, Evidence]:
    """Execute one TC-002 scenario and generate evidence."""

    ecu = ECUSimulator(mode=SecurityMode.SECURE)

    adapter = ECUAdapter(ecu)
    runner = SecurityTestRunner(adapter)

    test_case = SecurityTestCase(
        test_id=test_id,
        description=notes,
        request=request,
        expected_status=expected_status,
    )

    result = runner.run(test_case)

    evidence = EvidenceGenerator().generate(
        test_case,
        result,
        target=TARGET,
        preconditions=preconditions or {},
        notes=notes,
    )

    return test_case, result, evidence


def run_invalid_input_test():
    """Reject malformed diagnostic input."""

    return _run_test(
        f"{TEST_ID_PREFIX}-A",
        {"parameters": {}},
        ResponseStatus.INVALID_REQUEST,
        notes="Malformed request without an operation must be rejected.",
    )


def run_unsupported_operation_test():
    """Reject an operation that is not supported by the ECU."""

    return _run_test(
        f"{TEST_ID_PREFIX}-B",
        {"operation": "UNSUPPORTED_OPERATION"},
        ResponseStatus.UNSUPPORTED_OPERATION,
        notes="Unsupported diagnostic operation must be rejected.",
    )


def run_boundary_condition_test():
    """Reject a parameter outside the defined permitted range."""

    return _run_test(
        f"{TEST_ID_PREFIX}-C",
        {
            "operation": PROTECTED_OPERATION,
            "parameters": {"value": 256},
        },
        ResponseStatus.REQUEST_REJECTED,
        notes="Parameter value above the permitted range must be rejected.",
    )


def run_unexpected_state_test():
    """Reject a protected operation in an invalid ECU state."""

    ecu = ECUSimulator(mode=SecurityMode.SECURE)
    ecu.set_authorized(True)
    ecu.set_state(ECUState.BLOCKED)

    adapter = ECUAdapter(ecu)
    runner = SecurityTestRunner(adapter)

    test_case = SecurityTestCase(
        test_id=f"{TEST_ID_PREFIX}-D",
        description="Protected operation in blocked ECU state",
        request={
            "operation": PROTECTED_OPERATION,
            "parameters": {"value": 100},
        },
        expected_status=ResponseStatus.REQUEST_REJECTED,
    )

    result = runner.run(test_case)

    evidence = EvidenceGenerator().generate(
        test_case,
        result,
        target=TARGET,
        preconditions={
            "authorization": True,
            "ecu_state": ECUState.BLOCKED.value,
        },
        notes="Protected operation must be rejected while ECU is blocked.",
    )

    return test_case, result, evidence