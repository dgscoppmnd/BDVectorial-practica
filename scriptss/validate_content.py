#!/usr/bin/env python3
"""Valida la estructura del proyecto y, si existen, los artefactos de results/.

Uso: python scriptss/validate_content.py [--quick]
  --quick  solo comprueba rutas obligatorias (no requiere pandas)
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_PATHS = [
    "notebook/Aurum_Market_Practica.ipynb",
    "data",
    "src/aurum/metricas.py",
    "src/aurum/texto.py",
    "docker-compose.yml",
    ".python-version",
    "pyproject.toml",
    ".env.example",
]

missing = [p for p in REQUIRED_PATHS if not (PROJECT_ROOT / p).exists()]
if missing:
    raise SystemExit(
        "Validación fallida. Faltan rutas obligatorias:\n"
        + "\n".join(f" - {p}" for p in missing)
    )
print("Estructura del proyecto: OK")

if "--quick" not in sys.argv:
    import json

    import pandas as pd

    results = PROJECT_ROOT / "results"
    problemas = []

    ruta = results / "resultados_busqueda.csv"
    if ruta.exists():
        df = pd.read_csv(ruta)
        n_eval = len(pd.read_csv(PROJECT_ROOT / "data" / "consultas_evaluacion.csv"))
        if list(df.columns) != ["evaluation_id", "rank", "product_id", "score"]:
            problemas.append("resultados_busqueda.csv: columnas incorrectas")
        if len(df) != n_eval * 10:
            problemas.append(f"resultados_busqueda.csv: {len(df)} filas (esperadas {n_eval * 10})")

    ruta = results / "resultados_duplicados.csv"
    if ruta.exists():
        df = pd.read_csv(ruta, keep_default_na=False, dtype={"predicted_duplicate": str})
        if list(df.columns) != ["incoming_id", "predicted_duplicate", "matched_product_id", "score"]:
            problemas.append("resultados_duplicados.csv: columnas incorrectas")
        if not set(df["predicted_duplicate"].astype(str)) <= {"true", "false"}:
            problemas.append("resultados_duplicados.csv: predicted_duplicate debe ser true/false")

    ruta = results / "metricas_desarrollo.json"
    if ruta.exists():
        metricas = json.loads(ruta.read_text(encoding="utf-8"))
        for clave in ("lexical", "dense", "latency_p50_ms", "latency_p95_ms"):
            if clave not in metricas:
                problemas.append(f"metricas_desarrollo.json: falta la clave {clave!r}")

    if problemas:
        raise SystemExit("Validación de artefactos fallida:\n" + "\n".join(f" - {p}" for p in problemas))
    print("Artefactos de results/: OK")

print("Validación completada correctamente.")
