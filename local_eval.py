"""Reproducible offline control for the HDT-6 Promptfoo cases.

This is not Promptfoo's model-graded ``factuality`` metric. It is an explicit
local reference-consistency control used when no Promptfoo grader is available.
"""

from __future__ import annotations

import json
import re
import time
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from hdt5_adapter import Hdt5Adapter


ROOT = Path(__file__).resolve().parent
TODAY = date(2026, 9, 26)
LATENCY_LIMIT_MS = 1000


CASES: list[dict[str, Any]] = [
    {
        "id": "faq_known",
        "request": {"question": "¿Qué es HDT-5?"},
        "reference": "Es una demostración educativa de agentes.",
        "contains": ["Es una demostración educativa de agentes."],
        "regex": [r"faq-001"],
        "tool": "faq",
        "executed": True,
    },
    {
        "id": "faq_unknown",
        "request": {"question": "¿Cuál es el color del cielo?"},
        "reference": "No tengo una respuesta sustentada en el FAQ para esa pregunta.",
        "contains": ["No tengo una respuesta sustentada"],
        "regex": [r"^No tengo"],
        "tool": "faq",
        "executed": True,
    },
    {
        "id": "weather_favorable",
        "request": {"question": "¿Puedo saltar?", "requested_date": "2026-09-27", "fixture": "favorable"},
        "reference": "Estado meteorológico: favorable.",
        "contains": ["Estado meteorológico: favorable."],
        "regex": [r"Open-Meteo: https://api\.open-meteo\.com/"],
        "tool": "weather",
        "executed": True,
    },
    {
        "id": "weather_marginal",
        "request": {"question": "¿Puedo saltar?", "requested_date": "2026-09-27", "fixture": "marginal"},
        "reference": "Estado meteorológico: marginal.",
        "contains": [],
        "regex": [r"Estado meteorológico: marginal\."],
        "tool": "weather",
        "executed": True,
    },
]

for fixture in ("reject_wind_speed", "reject_wind_gust", "reject_precipitation", "reject_cloud_cover"):
    CASES.append(
        {
            "id": fixture,
            "request": {"question": "¿Puedo saltar?", "requested_date": "2026-09-27", "fixture": fixture},
            "reference": "Estado meteorológico: rejected.",
            "contains": ["Estado meteorológico: rejected."],
            "regex": [],
            "tool": "weather",
            "executed": True,
        }
    )

CASES.append(
    {
        "id": "weather_outside_window",
        "request": {"question": "¿Puedo saltar?", "requested_date": "2026-10-13"},
        "reference": "La fecha debe estar dentro de los próximos 16 días",
        "contains": ["La fecha debe estar dentro de los próximos 16 días"],
        "regex": [r"16 días"],
        "tool": "weather",
        "executed": False,
    }
)


def evaluate_case(adapter: Hdt5Adapter, case: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    result = adapter.run(case["request"])
    elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
    answer = result["answer"]
    metadata = result["metadata"]
    citations = metadata.get("citations", [])
    provider_output = f"{answer}\nCitas: {', '.join(citations)}" if citations else answer
    checks = {
        "factuality_reference_consistency": answer == case["reference"],
        "contains": all(value in provider_output for value in case["contains"]),
        "regex": all(re.search(pattern, provider_output) for pattern in case["regex"]),
        "latency_under_1000ms": elapsed_ms < LATENCY_LIMIT_MS,
        "tool_execution": metadata.get("tool_selected") == case["tool"]
        and metadata.get("tool_executed") is case["executed"],
    }
    return {
        "id": case["id"],
        "request": case["request"],
        "answer": answer,
        "provider_output": provider_output,
        "metadata": metadata,
        "latency_ms": elapsed_ms,
        "checks": checks,
        "passed": all(checks.values()),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# HDT-6 control local offline",
        "",
        "Este artefacto no es la métrica model-graded `factuality` de Promptfoo.",
        "Es un control reproducible de consistencia contra referencias, además de contains, regex, latencia y tool-use.",
        "",
        f"- Casos: {payload['summary']['cases']} | aprobados: {payload['summary']['passed']} | fallidos: {payload['summary']['failed']}",
        f"- Checks: {payload['summary']['checks_passed']}/{payload['summary']['checks_total']}",
        f"- Fecha de evaluación: `{TODAY.isoformat()}` | umbral de latencia: `< {LATENCY_LIMIT_MS} ms`",
        "",
        "| Caso | Resultado | Latencia (ms) | Checks |\n|---|---:|---:|---:|",
    ]
    for case in payload["cases"]:
        checks = ", ".join(f"{name}={'PASS' if value else 'FAIL'}" for name, value in case["checks"].items())
        lines.append(f"| `{case['id']}` | {'PASS' if case['passed'] else 'FAIL'} | {case['latency_ms']} | {checks} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    adapter = Hdt5Adapter(today=TODAY)
    cases = [evaluate_case(adapter, case) for case in CASES]
    checks = [value for case in cases for value in case["checks"].values()]
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evaluation_today": TODAY.isoformat(),
        "grader": "local-reference-control",
        "promptfoo_factuality_executed": False,
        "cases": cases,
        "summary": {
            "cases": len(cases),
            "passed": sum(case["passed"] for case in cases),
            "failed": sum(not case["passed"] for case in cases),
            "checks_total": len(checks),
            "checks_passed": sum(checks),
        },
    }
    json_path = ROOT / "reports" / "local-eval.json"
    markdown_path = ROOT / "reports" / "local-eval.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False, sort_keys=True))
    return 0 if payload["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
