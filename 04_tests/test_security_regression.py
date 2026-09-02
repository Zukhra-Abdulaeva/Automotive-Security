"""TC-003 — Security regression tests for diagnostic authorization.

These tests verify that the security property established by TC-001
remains enforced after a security-relevant change:
protected operations require authorization.
"""

from security_lab.ecu_adapter import ECUAdapter
from security_lab.ecu_simulator import ECUSimulator, ResponseStatus, SecurityMode
from security_lab.evidence import EvidenceGenerator, EvidenceResult
from security_lab.test_runner import SecurityTestCase, SecurityTestRunner


TEST_ID = "TC-001"
TARGET = "simulated-ecu"
PROTECTED_OPERATION = "PROTECTED_OPERATION"


def _create_unauthorized_case() -> SecurityTestCase:
    """Create the regression case for the authorization security property."""
    return SecurityTestCase(
        test_id=TEST_ID,
        description="Unauthorized protected operation must be denied",
        request={"operation": PROTECTED_OPERATION},
        expected_status=ResponseStatus.ACCESS_DENIED,
    )


def _create_authorized_case() -> SecurityTestCase:
    """Create the regression case for authorized functional behavior."""
    return SecurityTestCase(
        test_id=TEST_ID,
        description="Authorized protected operation must remain available",
        request={"operation": PROTECTED_OPERATION},
        expected_status=ResponseStatus.ACCESS_GRANTED,
    )


def test_tc003_reproduces_original_vulnerable_behavior():
    """Reproduce the controlled pre-fix behavior of the security finding."""
    ecu = ECUSimulator(mode=SecurityMode.VULNERABLE)
    ecu.set_authorized(False)

    runner = SecurityTestRunner(ECUAdapter(ecu))
    test_case = _create_unauthorized_case()

    result = runner.run(test_case)

    assert result.expected_status is ResponseStatus.ACCESS_DENIED
    assert result.actual_status is ResponseStatus.ACCESS_GRANTED
    assert not result.passed


def test_tc003_retest_confirms_secure_behavior():
    """Re-execute the same regression condition against the secure ECU."""
    ecu = ECUSimulator(mode=SecurityMode.SECURE)
    ecu.set_authorized(False)

    runner = SecurityTestRunner(ECUAdapter(ecu))
    test_case = _create_unauthorized_case()

    result = runner.run(test_case)

    assert result.expected_status is ResponseStatus.ACCESS_DENIED
    assert result.actual_status is ResponseStatus.ACCESS_DENIED
    assert result.passed


def test_tc003_regression_evidence_matches_retest_result():
    """Verify that regression evidence represents the executed retest."""
    ecu = ECUSimulator(mode=SecurityMode.SECURE)
    ecu.set_authorized(False)

    runner = SecurityTestRunner(ECUAdapter(ecu))
    test_case = _create_unauthorized_case()
    result = runner.run(test_case)

    evidence = EvidenceGenerator().generate(
        test_case,
        result,
        target=TARGET,
        preconditions={"authorization": False},
        notes="Retest confirms that unauthorized protected operation is denied.",
    )

    assert evidence.test_id == TEST_ID
    assert evidence.target == TARGET
    assert evidence.preconditions["authorization"] is False
    assert evidence.expected == "ACCESS_DENIED"
    assert evidence.actual == "ACCESS_DENIED"
    assert evidence.result is EvidenceResult.PASS

    evidence.validate()


def test_tc003_regression_preserves_authorized_behavior():
    """Verify that authorization remains functional after the security fix."""
    ecu = ECUSimulator(mode=SecurityMode.SECURE)
    ecu.set_authorized(True)

    runner = SecurityTestRunner(ECUAdapter(ecu))
    test_case = _create_authorized_case()

    result = runner.run(test_case)

    assert result.expected_status is ResponseStatus.ACCESS_GRANTED
    assert result.actual_status is ResponseStatus.ACCESS_GRANTED
    assert result.passed
