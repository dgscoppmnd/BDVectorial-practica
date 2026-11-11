"""Validación del contrato de los artefactos exportados en results/.

Se omiten (skip) si los artefactos aún no se han generado.
"""

import json
from pathlib import Path

import pandas as pd
import pytest

RESULTS = Path(__file__).resolve().parent.parent / "results"
DATA = Path(__file__).resolve().parent.parent / "data"


def _requiere(ruta):
    if not ruta.exists():
        pytest.skip(f"artefacto no generado todavía: {ruta.name}")
    return ruta


def test_resultados_busqueda():
    df = pd.read_csv(_requiere(RESULTS / "resultados_busqueda.csv"))
    consultas = pd.read_csv(DATA / "consultas_evaluacion.csv")
    assert list(df.columns) == ["evaluation_id", "rank", "product_id", "score"]
    assert len(df) == len(consultas) * 10
    assert set(df["evaluation_id"]) == set(consultas["evaluation_id"])
    for _, grupo in df.groupby("evaluation_id"):
        assert sorted(grupo["rank"]) == list(range(1, 11))
        ordenado = grupo.sort_values("rank")["score"]
        assert (ordenado.diff().dropna() <= 1e-9).all(), "scores descendentes por rank"


def test_resultados_duplicados():
    df = pd.read_csv(_requiere(RESULTS / "resultados_duplicados.csv"),
                     keep_default_na=False, dtype={"predicted_duplicate": str, "matched_product_id": str})
    altas = pd.read_csv(DATA / "altas_evaluacion.csv")
    assert list(df.columns) == ["incoming_id", "predicted_duplicate", "matched_product_id", "score"]
    assert len(df) == len(altas)
    assert set(df["predicted_duplicate"].astype(str)) <= {"true", "false"}
    con_match = df[df["predicted_duplicate"].astype(str) == "true"]
    assert (con_match["matched_product_id"].astype(str).str.len() > 0).all()


def test_metricas_desarrollo():
    with open(_requiere(RESULTS / "metricas_desarrollo.json"), encoding="utf-8") as fh:
        metricas = json.load(fh)
    for sistema in ("lexical", "dense"):
        for clave in ("ndcg_at_10", "recall_at_10", "mrr_at_10"):
            assert 0.0 <= metricas[sistema][clave] <= 1.0
    assert metricas["latency_p95_ms"] >= metricas["latency_p50_ms"]
    assert metricas["latencia_detalle"]["total"]["n_muestras"] > 1, \
        "los percentiles deben calcularse sobre repeticiones, no sobre una media"
    assert metricas["protocolo"]["k"] == 10
