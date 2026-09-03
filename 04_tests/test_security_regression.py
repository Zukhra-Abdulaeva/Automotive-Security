"""Phase 9 — Security regression tests for established security properties."""

from security_lab.ecu_adapter import ECUAdapter
from security_lab.ecu_simulator import (
    ECUState,
    ECUSimulator,
    ResponseStatus,
    SecurityMode,
)
from security_lab.evidence import EvidenceGenerator, EvidenceResult
from security_lab.test_runner import SecurityTestCase, SecurityTestRunner


TEST_ID = "TC-003"
TARGET = "simulated-ecu"
PROTECTED_OPERATION = "PROTECTED_OPERATION"


def _run_case(
    request: object,
    expected_status: ResponseStatus,
    *,
    authorized: bool = False,
    state: ECUState = ECUState.READY,
) -> tuple[SecurityTestCase, object]:
    """Execute one deterministic regression scenario against a fresh secure ECU."""
    ecu = ECUSimulator(mode=SecurityMode.SECURE, state=state)
    ecu.set_authorized(authorized)

    runner = SecurityTestRunner(ECUAdapter(ecu))
    test_case = SecurityTestCase(
        test_id=TEST_ID,
        description="Phase 9 security regression scenario",
        request=request,
        expected_status=expected_status,
    )

    result = runner.run(test_case)
    return test_case, result


def test_unauthorized_protected_operation_is_denied():
    """Unauthorized protected operations must remain denied."""
    test_case, result = _run_case(
        {"operation": PROTECTED_OPERATION},
        ResponseStatus.ACCESS_DENIED,
        authorized=False,
    )

    assert test_case.expected_status is ResponseStatus.ACCESS_DENIED
    assert result.actual_status is ResponseStatus.ACCESS_DENIED
    assert result.passed


def test_authorized_protected_operation_is_allowed():
    """Authorization must continue to permit the protected operation."""
    test_case, result = _run_case(
        {"operation": PROTECTED_OPERATION},
        ResponseStatus.ACCESS_GRANTED,
        authorized=True,
    )

    assert test_case.expected_status is ResponseStatus.ACCESS_GRANTED
    assert result.actual_status is ResponseStatus.ACCESS_GRANTED
    assert result.passed


def test_invalid_message_is_rejected():
    """Malformed requests must not reach protected-operation execution."""
    test_case, result = _run_case(
        {"parameters": {}},
        ResponseStatus.INVALID_REQUEST,
    )

    assert test_case.expected_status is ResponseStatus.INVALID_REQUEST
    assert result.actual_status is ResponseStatus.INVALID_REQUEST
    assert result.passed


def test_unsupported_operation_is_rejected():
    """Unsupported operations must be rejected safely."""
    test_case, result = _run_case(
        {"operation": "UNSUPPORTED_OPERATION"},
        ResponseStatus.UNSUPPORTED_OPERATION,
    )

    assert test_case.expected_status is ResponseStatus.UNSUPPORTED_OPERATION
    assert result.actual_status is ResponseStatus.UNSUPPORTED_OPERATION
    assert result.passed


def test_boundary_input_does_not_bypass_validation():
    """An out-of-range parameter must not bypass validation or authorization."""
    test_case, result = _run_case(
        {
            "operation": PROTECTED_OPERATION,
            "parameters": {"value": 256},
        },
        ResponseStatus.REQUEST_REJECTED,
        authorized=True,
    )

    assert test_case.expected_status is ResponseStatus.REQUEST_REJECTED
    assert result.actual_status is ResponseStatus.REQUEST_REJECTED
    assert result.passed


def test_unexpected_state_does_not_enable_protected_behavior():
    """A blocked ECU must reject protected operations even when authorized."""
    test_case, result = _run_case(
        {
            "operation": PROTECTED_OPERATION,
            "parameters": {"value": 100},
        },
        ResponseStatus.REQUEST_REJECTED,
        authorized=True,
        state=ECUState.BLOCKED,
    )

    assert test_case.expected_status is ResponseStatus.REQUEST_REJECTED
    assert result.actual_status is ResponseStatus.REQUEST_REJECTED
    assert result.passed


def test_regression_evidence_matches_secure_retest():
    """Regression evidence must represent the executed secure retest."""
    test_case, result = _run_case(
        {"operation": PROTECTED_OPERATION},
        ResponseStatus.ACCESS_DENIED,
        authorized=False,
    )

    evidence = EvidenceGenerator().generate(
        test_case,
        result,
        target=TARGET,
        preconditions={
            "authorization": False,
            "ecu_state": ECUState.READY.value,
            "security_mode": SecurityMode.SECURE.value,
        },
        notes="Secure regression retest confirms unauthorized protected operation is denied.",
    )

    assert evidence.test_id == TEST_ID
    assert evidence.target == TARGET
    assert evidence.preconditions["authorization"] is False
    assert evidence.preconditions["ecu_state"] == ECUState.READY.value
    assert evidence.preconditions["security_mode"] == SecurityMode.SECURE.value
    assert evidence.expected == "ACCESS_DENIED"
    assert evidence.actual == "ACCESS_DENIED"
    assert evidence.result is EvidenceResult.PASS

    evidence.validate()