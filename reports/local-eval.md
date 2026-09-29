# HDT-6 control local offline

Este artefacto no es la métrica model-graded `factuality` de Promptfoo.
Es un control reproducible de consistencia contra referencias, además de contains, regex, latencia y tool-use.

- Casos: 9 | aprobados: 9 | fallidos: 0
- Checks: 45/45
- Fecha de evaluación: `2026-09-26` | umbral de latencia: `< 1000 ms`

| Caso | Resultado | Latencia (ms) | Checks |
|---|---:|---:|---:|
| `faq_known` | PASS | 1.541 | factuality_reference_consistency=PASS, contains=PASS, regex=PASS, latency_under_1000ms=PASS, tool_execution=PASS |
| `faq_unknown` | PASS | 0.184 | factuality_reference_consistency=PASS, contains=PASS, regex=PASS, latency_under_1000ms=PASS, tool_execution=PASS |
| `weather_favorable` | PASS | 0.395 | factuality_reference_consistency=PASS, contains=PASS, regex=PASS, latency_under_1000ms=PASS, tool_execution=PASS |
| `weather_marginal` | PASS | 0.365 | factuality_reference_consistency=PASS, contains=PASS, regex=PASS, latency_under_1000ms=PASS, tool_execution=PASS |
| `reject_wind_speed` | PASS | 0.253 | factuality_reference_consistency=PASS, contains=PASS, regex=PASS, latency_under_1000ms=PASS, tool_execution=PASS |
| `reject_wind_gust` | PASS | 0.194 | factuality_reference_consistency=PASS, contains=PASS, regex=PASS, latency_under_1000ms=PASS, tool_execution=PASS |
| `reject_precipitation` | PASS | 0.222 | factuality_reference_consistency=PASS, contains=PASS, regex=PASS, latency_under_1000ms=PASS, tool_execution=PASS |
| `reject_cloud_cover` | PASS | 0.349 | factuality_reference_consistency=PASS, contains=PASS, regex=PASS, latency_under_1000ms=PASS, tool_execution=PASS |
| `weather_outside_window` | PASS | 0.083 | factuality_reference_consistency=PASS, contains=PASS, regex=PASS, latency_under_1000ms=PASS, tool_execution=PASS |
