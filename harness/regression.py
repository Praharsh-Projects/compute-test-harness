from __future__ import annotations

import json
from pathlib import Path


def load_baseline(path: str | Path) -> dict:
    baseline_path = Path(path)
    if not baseline_path.exists():
        return {"tests": {}}
    return json.loads(baseline_path.read_text(encoding="utf-8"))


def save_baseline(results: list[dict], path: str | Path) -> None:
    tests = {}
    for result in results:
        tests[result["test_name"]] = {
            "elapsed_ms": float(result.get("elapsed_ms", 0.0)),
            "checksum": float(result.get("checksum", 0.0)),
        }

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"tests": tests}, indent=2), encoding="utf-8")


def detect_regressions(results: list[dict], baseline: dict, threshold: float = 0.15) -> list[dict]:
    findings: list[dict] = []

    for result in results:
        name = result["test_name"]
        base = baseline.get("tests", {}).get(name)
        if not base:
            continue

        base_time = float(base.get("elapsed_ms", 0.0))
        current_time = float(result.get("elapsed_ms", 0.0))
        # Ignore ultra-short timings where scheduler jitter dominates signal.
        if base_time >= 20.0:
            delta = (current_time - base_time) / base_time
            if delta > threshold:
                findings.append(
                    {
                        "test_name": name,
                        "metric": "elapsed_ms",
                        "baseline": base_time,
                        "current": current_time,
                        "delta_pct": delta * 100.0,
                    }
                )

    return findings
