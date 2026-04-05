from __future__ import annotations

import argparse
import re
import subprocess
import time
from pathlib import Path

import yaml

from harness.regression import detect_regressions, load_baseline, save_baseline
from harness.reporter import generate_reports
from harness.validator import validate_case


def _parse_checksum(stdout: str) -> float:
    match = re.search(r"CHECKSUM=([-+]?\d*\.?\d+)", stdout)
    if not match:
        return 0.0
    return float(match.group(1))


def _parse_elapsed(stdout: str, wall_ms: float) -> float:
    match = re.search(r"ELAPSED_MS=([-+]?\d*\.?\d+)", stdout)
    if not match:
        return wall_ms
    return float(match.group(1))


def load_test_cases(config_paths: list[Path]) -> list[dict]:
    cases: list[dict] = []
    for config_path in config_paths:
        payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        suite_name = payload.get("suite_name", config_path.stem)
        for case in payload.get("tests", []):
            merged = dict(case)
            merged["suite_name"] = suite_name
            cases.append(merged)
    return cases


def run_test_case(case: dict, bin_dir: Path) -> dict:
    workload = case["workload"]
    binary = bin_dir / workload
    args = [str(arg) for arg in case.get("args", [])]

    if not binary.exists():
        return {
            "test_name": case["name"],
            "workload": workload,
            "status": "FAIL",
            "exit_code": 127,
            "elapsed_ms": 0.0,
            "checksum": 0.0,
            "stdout": "",
            "stderr": f"binary not found: {binary}",
            "failures": [f"binary not found: {binary}"],
        }

    command = [str(binary)] + args
    start = time.perf_counter()
    completed = subprocess.run(command, capture_output=True, text=True)
    wall_ms = (time.perf_counter() - start) * 1000.0

    checksum = _parse_checksum(completed.stdout)
    elapsed_ms = _parse_elapsed(completed.stdout, wall_ms)

    result = {
        "test_name": case["name"],
        "suite_name": case["suite_name"],
        "workload": workload,
        "exit_code": int(completed.returncode),
        "elapsed_ms": float(elapsed_ms),
        "checksum": float(checksum),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }

    failures = validate_case(result, case)
    result["failures"] = failures
    result["status"] = "PASS" if not failures else "FAIL"
    return result


def discover_configs(config: str | None, config_dir: str) -> list[Path]:
    if config:
        return [Path(config)]
    return sorted(Path(config_dir).glob("*.yaml"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run parameterized compute workload test suites")
    parser.add_argument("--config", default=None, help="Single YAML config file")
    parser.add_argument("--config-dir", default="configs", help="Directory containing YAML test suites")
    parser.add_argument("--bin-dir", default="workloads/bin", help="Directory containing compiled workload binaries")
    parser.add_argument("--baseline", default="baselines/baseline.json", help="Baseline JSON for regression detection")
    parser.add_argument("--regression-threshold", type=float, default=0.15)
    parser.add_argument("--report-dir", default="reports/latest")
    parser.add_argument("--update-baseline", action="store_true")
    args = parser.parse_args()

    config_paths = discover_configs(args.config, args.config_dir)
    if not config_paths:
        raise SystemExit("No config files found.")

    cases = load_test_cases(config_paths)
    results = [run_test_case(case, Path(args.bin_dir)) for case in cases]

    baseline = load_baseline(args.baseline)
    regressions = detect_regressions(results, baseline, threshold=args.regression_threshold)
    generate_reports(results, regressions, args.report_dir)

    if args.update_baseline:
        save_baseline(results, args.baseline)

    has_failures = any(r["status"] == "FAIL" for r in results)
    has_regressions = len(regressions) > 0

    print(f"Executed {len(results)} tests")
    print(f"Failures: {sum(1 for r in results if r['status'] == 'FAIL')}")
    print(f"Regressions: {len(regressions)}")

    return 1 if has_failures or has_regressions else 0


if __name__ == "__main__":
    raise SystemExit(main())
