"""Evidence model for the Automotive Security Regression Lab."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from security_lab.ecu_simulator import ResponseStatus
from security_lab.test_runner import SecurityTestCase, TestResult


@dataclass(frozen=True)
class Evidence:
    """Structured evidence for one security test execution."""

    execution_id: str
    test_id: str
    description: str
    request: Mapping[str, Any]
    expected_status: ResponseStatus
    actual_status: ResponseStatus
    passed: bool
    operation: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible dictionary representation."""
        data = asdict(self)
        data["expected_status"] = self.expected_status.value
        data["actual_status"] = self.actual_status.value
        return data


class EvidenceGenerator:
    """Create structured evidence from a test case and test result."""

    def __init__(self) -> None:
        self._counter = 0

    def generate(
        self,
        test_case: SecurityTestCase,
        result: TestResult,
    ) -> Evidence:
        """Generate evidence for one completed test execution."""
        self._counter += 1
        execution_id = f"EXEC-{self._counter:06d}"

        operation = test_case.request.get("operation")
        if not isinstance(operation, str):
            operation = ""

        return Evidence(
            execution_id=execution_id,
            test_id=test_case.test_id,
            description=test_case.description,
            request=dict(test_case.request),
            expected_status=result.expected_status,
            actual_status=result.actual_status,
            passed=result.passed,
            operation=operation,
        )
