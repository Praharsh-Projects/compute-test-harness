from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Template


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <title>Compute Test Harness Report</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
    th, td { border: 1px solid #ddd; padding: 8px; }
    th { background: #f4f4f4; }
    .pass { color: #1a7f37; font-weight: 600; }
    .fail { color: #b42318; font-weight: 600; }
  </style>
</head>
<body>
  <h1>Compute Test Harness Report</h1>
  <h2>Results</h2>
  <table>
    <thead>
      <tr>
        <th>Test</th><th>Workload</th><th>Status</th><th>Elapsed (ms)</th><th>Checksum</th><th>Failures</th>
      </tr>
    </thead>
    <tbody>
      {% for r in results %}
      <tr>
        <td>{{ r.test_name }}</td>
        <td>{{ r.workload }}</td>
        <td class="{{ 'pass' if r.status == 'PASS' else 'fail' }}">{{ r.status }}</td>
        <td>{{ '%.3f'|format(r.elapsed_ms) }}</td>
        <td>{{ '%.4f'|format(r.checksum) }}</td>
        <td>{{ '; '.join(r.failures) }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <h2>Regression Findings</h2>
  {% if regressions %}
    <ul>
    {% for reg in regressions %}
      <li>{{ reg.test_name }}: {{ reg.metric }} regressed by {{ '%.2f'|format(reg.delta_pct) }}%</li>
    {% endfor %}
    </ul>
  {% else %}
    <p>No regressions detected.</p>
  {% endif %}
</body>
</html>
"""


def generate_reports(results: list[dict], regressions: list[dict], output_dir: str | Path) -> dict[str, Path]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    json_path = out / "results.json"
    md_path = out / "summary.md"
    html_path = out / "report.html"

    payload = {"results": results, "regressions": regressions}
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = ["# Compute Test Harness Summary", "", "## Results"]
    for r in results:
        lines.append(
            f"- **{r['test_name']}** ({r['workload']}): {r['status']} | elapsed={r['elapsed_ms']:.3f} ms"
        )
        if r["failures"]:
            lines.append(f"  - failures: {'; '.join(r['failures'])}")

    lines.append("")
    lines.append("## Regressions")
    if regressions:
        for reg in regressions:
            lines.append(
                f"- {reg['test_name']}: {reg['metric']} regressed by {reg['delta_pct']:.2f}% "
                f"(baseline={reg['baseline']:.3f}, current={reg['current']:.3f})"
            )
    else:
        lines.append("- No regressions detected.")

    md_path.write_text("\n".join(lines), encoding="utf-8")

    html = Template(HTML_TEMPLATE).render(results=results, regressions=regressions)
    html_path.write_text(html, encoding="utf-8")

    return {"json": json_path, "md": md_path, "html": html_path}
