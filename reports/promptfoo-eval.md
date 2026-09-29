# Reporte reproducible de Promptfoo

Fecha de actualización: 2026-09-28 (America/Guatemala)

## Comando

```text
npx --yes promptfoo@latest --version
npx promptfoo@latest eval --no-cache -c promptfooconfig.yaml
```

## Resultado

`npx --yes promptfoo@latest --version` no terminó en 30 segundos y fue
interrumpido por timeout. La evaluación solicitada se ejecutó como
`timeout 30s npx promptfoo@latest eval --no-cache -c promptfooconfig.yaml` y
terminó con código `124`, sin producir evaluación ni reporte JSON nativo. La
causa concreta fue que el DNS devolvió `EAI_AGAIN getaddrinfo
registry.npmjs.org`; la comprobación offline de npm indicó `ENOTCACHED` porque
Promptfoo no estaba disponible en caché. Por tanto, no se ejecutaron las
assertions nativas de Promptfoo, incluida `factuality`.

La comprobación adicional sin red fue:

```text
timeout 15s npx --offline --yes promptfoo@latest --version
```

Resultado: código `1`, `npm error code ENOTCACHED`; no había respuesta de
Promptfoo en la caché local.

La configuración entregada sí declara `factuality` con referencias explícitas
para FAQ y clima. Para ejecutar ese grader se necesita proporcionar un modelo
de evaluación, por ejemplo `--grader openai:gpt-5-mini` con sus credenciales.

Como evidencia local reproducible, se ejecutó `local_eval.py`. Este control no
se presenta como factualidad model-graded: compara las respuestas de fixtures
con referencias exactas y verifica también contains, regex, latencia y tool-use.
Genera `reports/local-eval.json` y `reports/local-eval.md`.

Comando y resultado:

```text
PYTHONPATH=/home/deiv/Universidad/AI-Engineering/AI-HDT5:/home/deiv/Universidad/AI-Engineering/AI-HDT5/.venv/lib/python3.14/site-packages ../AI-HDT5/.venv/bin/python local_eval.py
{"cases": 9, "checks_passed": 45, "checks_total": 45, "failed": 0, "passed": 9}
```

El JSON registra `grader: local-reference-control` y
`promptfoo_factuality_executed: false`.

La suite equivalente del adaptador se ejecutó localmente con pytest y terminó
`9 passed` (verificación sin red). Para reproducirla en este entorno:

```text
PYTHONPATH=/home/deiv/Universidad/AI-Engineering/AI-HDT5:/home/deiv/Universidad/AI-Engineering/AI-HDT5/.venv/lib/python3.14/site-packages ../AI-HDT5/.venv/bin/python -m pytest -q tests
```

Resultado: `9 passed in 0.09s`.

La suite original de HDT-5 también se ejecutó con su entorno existente:
`PYTHONPATH=/home/deiv/Universidad/AI-Engineering/AI-HDT5:/home/deiv/Universidad/AI-Engineering/AI-HDT5/.venv/lib/python3.14/site-packages ../AI-HDT5/.venv/bin/python -m pytest -q -p no:cacheprovider ../AI-HDT5/tests`
Resultado: `12 passed in 0.03s`. Se deshabilitó el plugin de caché para no
intentar escribir en el proyecto vecino de solo lectura.
