"""Structured evidence model for the Automotive Security Regression Lab."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import json
from typing import Any, Mapping

from security_lab.test_runner import SecurityTestCase, TestResult


class EvidenceResult(str, Enum):
    """Allowed result values for a security test evidence record."""

    PASS = "PASS"
    FAIL = "FAIL"


class EvidenceValidationError(ValueError):
    """Raised when an evidence record is incomplete or inconsistent."""


@dataclass(frozen=True)
class Evidence:
    """Structured, machine-readable evidence for one test execution."""

    test_id: str
    timestamp: str
    target: str
    preconditions: Mapping[str, Any]
    input: Any
    expected: Any
    actual: Any
    result: EvidenceResult
    notes: str

    def validate(self) -> None:
        """Validate required fields and result semantics."""
        required_fields = {
            "test_id": self.test_id,
            "timestamp": self.timestamp,
            "target": self.target,
            "expected": self.expected,
            "actual": self.actual,
            "result": self.result,
        }

        missing_fields = [
            field
            for field, value in required_fields.items()
            if value is None or (isinstance(value, str) and not value.strip())
        ]

        if missing_fields:
            raise EvidenceValidationError(
                f"Missing required evidence fields: {', '.join(missing_fields)}"
            )

        if not isinstance(self.preconditions, Mapping):
            raise EvidenceValidationError(
                "preconditions must be a mapping"
            )

        if not isinstance(self.result, EvidenceResult):
            raise EvidenceValidationError(
                "result must be PASS or FAIL"
            )

        expected_result = (
            EvidenceResult.PASS
            if self.expected == self.actual
            else EvidenceResult.FAIL
        )

        if self.result is not expected_result:
            raise EvidenceValidationError(
                "result does not match expected/actual behavior"
            )

    def to_dict(self) -> dict[str, Any]:
        """Return the evidence as a JSON-compatible dictionary."""
        self.validate()

        return {
            "test_id": self.test_id,
            "timestamp": self.timestamp,
            "target": self.target,
            "preconditions": dict(self.preconditions),
            "input": self.input,
            "expected": self.expected,
            "actual": self.actual,
            "result": self.result.value,
            "notes": self.notes,
        }

    def to_json(self) -> str:
        """Serialize the evidence as formatted JSON."""
        return json.dumps(
            self.to_dict(),
            indent=2,
            sort_keys=True,
        )

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Evidence:
        """Create and validate evidence from a mapping."""
        required_fields = {
            "test_id",
            "timestamp",
            "target",
            "preconditions",
            "input",
            "expected",
            "actual",
            "result",
            "notes",
        }

        missing_fields = sorted(required_fields - set(data))
        if missing_fields:
            raise EvidenceValidationError(
                f"Missing required evidence fields: {', '.join(missing_fields)}"
            )

        try:
            result = EvidenceResult(data["result"])
        except (TypeError, ValueError) as exc:
            raise EvidenceValidationError(
                "result must be PASS or FAIL"
            ) from exc

        evidence = cls(
            test_id=data["test_id"],
            timestamp=data["timestamp"],
            target=data["target"],
            preconditions=data["preconditions"],
            input=data["input"],
            expected=data["expected"],
            actual=data["actual"],
            result=result,
            notes=data["notes"],
        )
        evidence.validate()
        return evidence


class EvidenceGenerator:
    """Create structured evidence from a Phase-3 test execution."""

    def generate(
        self,
        test_case: SecurityTestCase,
        result: TestResult,
        *,
        target: str = "simulated-ecu",
        preconditions: Mapping[str, Any] | None = None,
        notes: str = "",
    ) -> Evidence:
        """Generate evidence for one completed security test execution."""
        actual = result.actual_status.value
        expected = result.expected_status.value

        evidence = Evidence(
            test_id=test_case.test_id,
            timestamp=datetime.now(timezone.utc).isoformat().replace(
                "+00:00", "Z"
            ),
            target=target,
            preconditions=dict(preconditions or {}),
            input=dict(test_case.request),
            expected=expected,
            actual=actual,
            result=(
                EvidenceResult.PASS
                if expected == actual
                else EvidenceResult.FAIL
            ),
            notes=notes,
        )

        evidence.validate()
        return evidence