"""Promptfoo adapter for the deterministic HDT-5 interface.

The adapter deliberately uses HDT-5's public architecture contract and an
injected HTTP transport backed by JSON fixtures. It never calls Open-Meteo.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import date
from pathlib import Path
from typing import Any


PROJECT_DIR = Path(__file__).resolve().parent
HDT5_DIR = Path(__file__).resolve().parent.parent / "AI-HDT5"
if str(HDT5_DIR) not in sys.path:
    sys.path.insert(0, str(HDT5_DIR))

from hdt5.centralized import CentralizedArchitecture  # noqa: E402
from hdt5.faq import load_faq_json  # noqa: E402
from hdt5.weather import OpenMeteoClient, WeatherService  # noqa: E402


class FixtureHttp:
    def __init__(self, fixture_dir: Path, fixture: str):
        self.path = fixture_dir / f"{fixture}.json"

    def get_json(self, _url: str, _params: dict[str, str]) -> dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))


class Hdt5Adapter:
    def __init__(
        self,
        fixture_dir: str | Path = PROJECT_DIR / "fixtures",
        hdt5_dir: str | Path = HDT5_DIR,
        today: date | None = None,
    ):
        self.fixture_dir = Path(fixture_dir)
        self.hdt5_dir = Path(hdt5_dir)
        # Keep Promptfoo runs reproducible while allowing CI/users to choose a
        # different forecast reference date explicitly.
        configured_today = os.environ.get("HDT5_EVAL_TODAY")
        self.today = today or date.fromisoformat(configured_today or "2026-09-26")

    def _architecture(self, fixture: str) -> CentralizedArchitecture:
        faq = load_faq_json(self.hdt5_dir / "data" / "faqs.json")
        http = FixtureHttp(self.fixture_dir, fixture)
        weather = WeatherService(OpenMeteoClient(http), today=self.today)
        return CentralizedArchitecture(faq, weather)

    def run(self, request: dict[str, Any]) -> dict[str, Any]:
        started = time.perf_counter()
        question = str(request.get("question", ""))
        requested_date = request.get("requested_date")
        fixture = str(request.get("fixture", "favorable"))
        selected_tool = "weather" if requested_date or any(
            word in question.lower() for word in ("clima", "tiempo", "viento", "lluvia", "saltar")
        ) else "faq"
        metadata: dict[str, Any] = {
            "architecture": "centralized",
            "tool_selected": selected_tool,
            "fixture": fixture,
            "evaluation_today": self.today.isoformat(),
            "offline": True,
        }
        try:
            parsed_date = date.fromisoformat(requested_date) if requested_date else None
            architecture = self._architecture(fixture)
            result = architecture.query(question, parsed_date)
            metadata.update(
                tool_executed=True,
                citations=result.citations,
                found=result.found,
            )
            if selected_tool == "weather" and parsed_date is not None:
                assessment = architecture.weather.assess(parsed_date)
                metadata.update(status=assessment.status, reasons=assessment.reasons)
            answer = result.answer
        except ValueError as exc:
            metadata.update(tool_executed=False, citations=[], found=False, error=str(exc))
            answer = str(exc)
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as exc:
            metadata.update(tool_executed=False, citations=[], found=False, error=str(exc))
            answer = f"Error de fixture local: {exc}"
        metadata["latency_ms"] = round((time.perf_counter() - started) * 1000, 3)
        return {"answer": answer, "metadata": metadata}


def main() -> None:
    request = json.loads(sys.argv[1]) if len(sys.argv) > 1 else json.load(sys.stdin)
    print(json.dumps(Hdt5Adapter().run(request), ensure_ascii=False))


if __name__ == "__main__":
    main()
