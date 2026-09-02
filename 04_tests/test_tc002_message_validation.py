from security_lab.ecu_simulator import ResponseStatus
from security_lab.evidence import EvidenceResult
from security_lab.tc_002_message_validation import (
    run_boundary_condition_test,
    run_invalid_input_test,
    run_unexpected_state_test,
    run_unsupported_operation_test,
)


def test_tc002_invalid_input():
    test_case, result, evidence = run_invalid_input_test()

    assert test_case.test_id == "TC-002-A"
    assert result.passed
    assert result.expected_status is ResponseStatus.INVALID_REQUEST
    assert result.actual_status is ResponseStatus.INVALID_REQUEST
    assert evidence.result is EvidenceResult.PASS


def test_tc002_unsupported_operation():
    test_case, result, evidence = run_unsupported_operation_test()

    assert test_case.test_id == "TC-002-B"
    assert result.passed
    assert result.expected_status is ResponseStatus.UNSUPPORTED_OPERATION
    assert result.actual_status is ResponseStatus.UNSUPPORTED_OPERATION
    assert evidence.result is EvidenceResult.PASS


def test_tc002_boundary_condition():
    test_case, result, evidence = run_boundary_condition_test()

    assert test_case.test_id == "TC-002-C"
    assert result.passed
    assert result.expected_status is ResponseStatus.REQUEST_REJECTED
    assert result.actual_status is ResponseStatus.REQUEST_REJECTED
    assert evidence.result is EvidenceResult.PASS


def test_tc002_unexpected_state():
    test_case, result, evidence = run_unexpected_state_test()

    assert test_case.test_id == "TC-002-D"
    assert result.passed
    assert result.expected_status is ResponseStatus.REQUEST_REJECTED
    assert result.actual_status is ResponseStatus.REQUEST_REJECTED
    assert evidence.result is EvidenceResult.PASS

def test_valid_boundary_values_are_accepted():
    from security_lab.ecu_simulator import ECUSimulator

    ecu = ECUSimulator()
    ecu.set_authorized(True)

    for value in (0, 255):
        response = ecu.handle_request(
            {
                "operation": "PROTECTED_OPERATION",
                "parameters": {"value": value},
            }
        )

        assert response.status is ResponseStatus.ACCESS_GRANTED