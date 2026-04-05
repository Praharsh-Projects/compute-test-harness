from pathlib import Path

from harness.runner import _parse_checksum, _parse_elapsed, load_test_cases


def test_parse_stdout_extractors() -> None:
    text = "CHECKSUM=123.456\nELAPSED_MS=78.9\n"
    assert _parse_checksum(text) == 123.456
    assert _parse_elapsed(text, 999.0) == 78.9


def test_load_cases_from_yaml(tmp_path: Path) -> None:
    config = tmp_path / "suite.yaml"
    config.write_text(
        """
suite_name: unit

tests:
  - name: demo
    workload: vector_add
    args: [100]
""",
        encoding="utf-8",
    )

    cases = load_test_cases([config])
    assert len(cases) == 1
    assert cases[0]["suite_name"] == "unit"
    assert cases[0]["name"] == "demo"
