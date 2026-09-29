import json
from datetime import date

from hdt5_adapter import Hdt5Adapter


FIXTURES = "fixtures"


def test_known_faq_uses_hdt5_and_reports_faq_tool():
    result = Hdt5Adapter(fixture_dir=FIXTURES, today=date(2026, 9, 26)).run(
        {"question": "¿Qué es HDT-5?"}
    )

    assert result["answer"] == "Es una demostración educativa de agentes."
    assert result["metadata"]["tool_selected"] == "faq"
    assert result["metadata"]["tool_executed"] is True
    assert result["metadata"]["citations"] == ["faq-001"]


def test_unknown_faq_is_a_grounded_refusal_without_citation():
    result = Hdt5Adapter(fixture_dir=FIXTURES).run(
        {"question": "¿Cuál es el color del cielo?"}
    )

    assert "no tengo" in result["answer"].lower()
    assert result["metadata"]["tool_selected"] == "faq"
    assert result["metadata"]["citations"] == []


def test_weather_uses_selected_fixture_without_network_and_cites_open_meteo():
    result = Hdt5Adapter(fixture_dir=FIXTURES, today=date(2026, 9, 26)).run(
        {
            "question": "¿Puedo saltar?",
            "requested_date": "2026-09-27",
            "fixture": "favorable",
        }
    )

    assert result["answer"] == "Estado meteorológico: favorable."
    assert result["metadata"]["tool_selected"] == "weather"
    assert result["metadata"]["tool_executed"] is True
    assert result["metadata"]["citations"][0].startswith("Open-Meteo: https://api.open-meteo.com/")


def test_weather_marks_marginal_fixture():
    result = Hdt5Adapter(fixture_dir=FIXTURES, today=date(2026, 9, 26)).run(
        {"question": "¿Puedo saltar?", "requested_date": "2026-09-27", "fixture": "marginal"}
    )

    assert result["metadata"]["status"] == "marginal"
    assert "wind_speed entre 20 y 28 km/h" in result["metadata"]["reasons"]


def test_each_weather_rejection_rule_is_exposed_in_metadata():
    expected = {
        "reject_wind_speed": "wind_speed > 28 km/h",
        "reject_wind_gust": "wind_gust > 35 km/h",
        "reject_precipitation": "precipitation > 0.0 mm",
        "reject_cloud_cover": "cloud_cover > 75%",
    }
    for fixture, reason in expected.items():
        result = Hdt5Adapter(fixture_dir=FIXTURES, today=date(2026, 9, 26)).run(
            {"question": "¿Puedo saltar?", "requested_date": "2026-09-27", "fixture": fixture}
        )
        assert result["metadata"]["status"] == "rejected"
        assert reason in result["metadata"]["reasons"]


def test_date_beyond_forecast_window_is_rejected_before_tool_execution():
    result = Hdt5Adapter(fixture_dir=FIXTURES, today=date(2026, 9, 26)).run(
        {"question": "¿Puedo saltar?", "requested_date": "2026-10-13"}
    )

    assert "16 días" in result["answer"]
    assert result["metadata"]["tool_selected"] == "weather"
    assert result["metadata"]["tool_executed"] is False


def test_cli_returns_json_for_promptfoo():
    import subprocess
    import sys

    completed = subprocess.run(
        [sys.executable, "hdt5_adapter.py"],
        input=json.dumps({"question": "¿Qué es HDT-5?"}),
        text=True,
        capture_output=True,
        check=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["metadata"]["tool_selected"] == "faq"


def test_default_evaluation_date_is_reproducible(monkeypatch):
    monkeypatch.delenv("HDT5_EVAL_TODAY", raising=False)
    result = Hdt5Adapter(fixture_dir=FIXTURES).run(
        {"question": "¿Puedo saltar?", "requested_date": "2026-09-27"}
    )
    assert result["metadata"]["evaluation_today"] == "2026-09-26"
    assert result["metadata"]["tool_executed"] is True


def test_evaluation_date_can_be_overridden(monkeypatch):
    monkeypatch.setenv("HDT5_EVAL_TODAY", "2026-09-28")
    result = Hdt5Adapter(fixture_dir=FIXTURES).run(
        {"question": "¿Puedo saltar?", "requested_date": "2026-09-29"}
    )
    assert result["metadata"]["evaluation_today"] == "2026-09-28"
    assert result["metadata"]["tool_executed"] is True
