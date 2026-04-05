from __future__ import annotations

from typing import Any


def validate_case(result: dict[str, Any], case: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    expected_exit_code = int(case.get("expected_exit_code", 0))
    if int(result.get("exit_code", 1)) != expected_exit_code:
        failures.append(f"exit_code expected {expected_exit_code}, got {result.get('exit_code')}")

    if "expected_checksum" in case:
        expected = float(case["expected_checksum"])
        observed = float(result.get("checksum", 0.0))
        tolerance = float(case.get("checksum_tolerance", 1e-3))
        if abs(observed - expected) > tolerance:
            failures.append(
                f"checksum expected {expected:.4f} +/- {tolerance}, got {observed:.4f}"
            )

    if "max_time_ms" in case:
        max_time = float(case["max_time_ms"])
        elapsed = float(result.get("elapsed_ms", 0.0))
        if elapsed > max_time:
            failures.append(f"elapsed_ms {elapsed:.3f} exceeded max_time_ms {max_time:.3f}")

    return failures
