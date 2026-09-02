from security_lab.ecu_simulator import ResponseStatus
from security_lab.evidence import EvidenceResult
from security_lab.tc_001_diagnostic_authorization import (
    run_authorized_secure_test,
    run_unauthorized_secure_test,
    run_unauthorized_vulnerable_test,
)


def test_tc001_unauthorized_access_secure_ecu():
    test_case, result, evidence = run_unauthorized_secure_test()

    assert test_case.test_id == "TC-001"
    assert result.passed
    assert result.expected_status is ResponseStatus.ACCESS_DENIED
    assert result.actual_status is ResponseStatus.ACCESS_DENIED
    assert evidence.result is EvidenceResult.PASS


def test_tc001_authorized_access_secure_ecu():
    test_case, result, evidence = run_authorized_secure_test()

    assert test_case.test_id == "TC-001"
    assert result.passed
    assert result.expected_status is ResponseStatus.ACCESS_GRANTED
    assert result.actual_status is ResponseStatus.ACCESS_GRANTED
    assert evidence.result is EvidenceResult.PASS


def test_tc001_vulnerable_behavior_produces_security_observation():
    test_case, result, evidence = run_unauthorized_vulnerable_test()

    assert test_case.test_id == "TC-001"
    assert result.expected_status is ResponseStatus.ACCESS_DENIED
    assert result.actual_status is ResponseStatus.ACCESS_GRANTED
    assert not result.passed

    assert evidence.result is EvidenceResult.FAIL
    assert evidence.expected == "ACCESS_DENIED"
    assert evidence.actual == "ACCESS_GRANTED"


def test_tc001_vulnerable_evidence_is_machine_readable():
    _, _, evidence = run_unauthorized_vulnerable_test()

    evidence_dict = evidence.to_dict()

    assert evidence_dict["test_id"] == "TC-001"
    assert evidence_dict["target"] == "simulated-ecu"
    assert evidence_dict["preconditions"]["authorization"] is False
    assert evidence_dict["expected"] == "ACCESS_DENIED"
    assert evidence_dict["actual"] == "ACCESS_GRANTED"
    assert evidence_dict["result"] == "FAIL"